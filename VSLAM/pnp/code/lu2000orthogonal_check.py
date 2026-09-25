"""Kiểm chứng số (cửa (b)) cho lu2000orthogonal — orthogonal iteration (OI / LHM).

Chạy:  python3 VSLAM/pnp/code/lu2000orthogonal_check.py
Các kiểm:
  C0  công thức cục bộ: t(R) eq.(20) so với lstsq; I - mean(V) xác định dương (21);
      eq.(16) "R* = V U^t" theo đúng quy ước (13) của bài -> ra chuyển vị.
  C1  E(R^k) giảm đơn điệu (eq.(33)); bất đẳng thức trung gian (31) có đúng từng bước không;
      hàm majorant g(q) = sum ||q - V q^(k)||^2 >= E (tôi suy ra: OI là thuật toán MM).
  C2  hội tụ từ nhiều R^(0) ngẫu nhiên: bao nhiêu lần tới cực tiểu toàn cục của E,
      bao nhiêu lần kẹt ở điểm bất động khác; target không phẳng và target phẳng.
      SQPnP (cv2) dùng làm tham chiếu độc lập cho cực tiểu toàn cục của cùng hàm E.
  C3  tốc độ hội tụ cục bộ: tuyến tính hay "quadratic-like" (bài chỉ phỏng đoán, [tr. 11]).
  C4  độ chính xác theo nhiễu pixel đẳng hướng: OI vs cv2 ITERATIVE vs SQPNP, và khác biệt
      giữa nghiệm tối ưu không gian vật (OI) và nghiệm tối ưu không gian ảnh (LM refine).
  C5  thiên lệch theo độ sâu (§3.5, thí nghiệm D1 kiểu hộp 8 đỉnh [-5,5]^3).
Tất cả seed cố định. Tọa độ ảnh chuẩn hoá v = K^-1 [u;1] (thành phần thứ ba = 1), như bài.
"""
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from common import K_DEFAULT, make_scene, random_rotation, rot_err_deg, trans_err_rel, reproj_rmse  # noqa: E402

import cv2  # noqa: E402

Kinv = np.linalg.inv(K_DEFAULT)
I3 = np.eye(3)


# ---------------------------------------------------------------- OI (LHM) theo §3
def los_proj(v):
    """V_i = v v^t / v^t v  (eq. (6)/(18)); v (n,3)."""
    return np.einsum('ni,nj->nij', v, v) / np.einsum('ni,ni->n', v, v)[:, None, None]


class OI:
    def __init__(self, P, v):
        self.P = np.asarray(P, float)                      # p_i (n,3) — điểm vật
        self.V = los_proj(v)                               # \hat V_i
        n = len(P)
        self.n = n
        self.Pc = self.P - self.P.mean(0)                  # p'_i (12)
        # eq. (20): t(R) = (1/n) (I - (1/n) sum V_j)^-1 sum (V_j - I) R p_j
        self.Tfac = np.linalg.inv(I3 - self.V.mean(0)) / n
        self.VmI = self.V - I3

    def t_of_R(self, R):
        RP = self.P @ R.T
        return self.Tfac @ np.einsum('nij,nj->i', self.VmI, RP)

    def E(self, R, t):
        """eq. (19)."""
        q = self.P @ R.T + t
        e = q - np.einsum('nij,nj->ni', self.V, q)
        return float(np.sum(e * e))

    @staticmethod
    def abs_orient(P, Q):
        """R cực tiểu (10): M = sum q'_i p'^t_i (13); R = U diag(1,1,det) V^t với M = U S V^t
        (quy ước numpy). Đây là CHUYỂN VỊ của biểu thức (16) nếu đọc (16) theo nghĩa đen."""
        Pc = P - P.mean(0)
        Qc = Q - Q.mean(0)
        M = Qc.T @ Pc
        U, S, Vt = np.linalg.svd(M)
        d = np.sign(np.linalg.det(U @ Vt))
        return U @ np.diag([1, 1, d]) @ Vt

    def step(self, R):
        t = self.t_of_R(R)
        q = self.P @ R.T + t
        Vq = np.einsum('nij,nj->ni', self.V, q)            # \hat V_i q_i^(k)
        Rn = self.abs_orient(self.P, Vq)                   # (25)/(26)
        return Rn, Vq

    def init_weak_persp(self, v):
        """§3.4: dùng chính v_i làm điểm cảnh giả thuyết cho lần AO đầu tiên."""
        return self.abs_orient(self.P, v)

    def run(self, R0, tol=1e-11, max_iter=3000, trace=False):
        R = R0
        Es = [self.E(R, self.t_of_R(R))]
        Rs = [R]
        for k in range(max_iter):
            Rn, _ = self.step(R)
            Es.append(self.E(Rn, self.t_of_R(Rn)))
            if trace:
                Rs.append(Rn)
            if np.linalg.norm(Rn - R) < tol:
                R = Rn
                break
            R = Rn
        out = dict(R=R, t=self.t_of_R(R), E=Es[-1], iters=k + 1, Es=np.array(Es),
                   converged=k + 1 < max_iter)
        if trace:
            out['Rs'] = Rs
        return out


def normalized(u):
    return (Kinv @ np.c_[u, np.ones(len(u))].T).T


def cv_pose(X, u, flag, rvec=None, tvec=None):
    if rvec is None:
        ok, rv, tv = cv2.solvePnP(X, u, K_DEFAULT, None, flags=flag)
    else:
        ok, rv, tv = cv2.solvePnP(X, u, K_DEFAULT, None, rvec.copy(), tvec.copy(), True, flags=flag)
    return cv2.Rodrigues(rv)[0], tv.ravel()


def lm_refine(X, u, R, t):
    rv = cv2.Rodrigues(R)[0]
    rv, tv = cv2.solvePnPRefineLM(X, u, K_DEFAULT, None, rv, t.reshape(3, 1).copy(),
                                  (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_COUNT, 200, 1e-14))
    return cv2.Rodrigues(rv)[0], tv.ravel()


def front(R, t, X):
    return bool(np.all((X @ R.T + t)[:, 2] > 0))


def verdict(ok):
    return "PASS" if ok else "FAIL"


# ---------------------------------------------------------------- C0
def check0():
    print("== C0: công thức cục bộ (20), (21), (16)")
    rng = np.random.default_rng(0)
    X, u, _, R, t = make_scene(10, rng, sigma_px=1.0)
    oi = OI(X, normalized(u))
    Rr = random_rotation(rng)
    # t(R) theo (20) so với nghiệm lstsq của sum ||(I-V_i)(R p_i + t)||^2 theo t
    A = np.concatenate([I3 - Vi for Vi in oi.V])
    b = -np.concatenate([(I3 - Vi) @ (Rr @ p) for Vi, p in zip(oi.V, X)])
    t_ls = np.linalg.lstsq(A, b, rcond=None)[0]
    d = np.linalg.norm(oi.t_of_R(Rr) - t_ls) / np.linalg.norm(t_ls)
    print(f"  t(R) eq.(20) vs lstsq: sai khác tương đối = {d:.2e}  -> {verdict(d < 1e-10)}")
    ev = np.linalg.eigvalsh(I3 - oi.V.mean(0))
    print(f"  trị riêng của I - mean(V): {ev.round(5)}  -> xác định dương {verdict(ev.min() > 0)}")
    # eq. (16) theo nghĩa đen: U^t M V = Sigma, R* = V U^t, với M = sum q' p'^t (13)
    Q = X @ R.T + t
    M = (Q - Q.mean(0)).T @ (X - X.mean(0))
    U, S, Vt = np.linalg.svd(M)
    R_lit = Vt.T @ U.T
    R_fix = OI.abs_orient(X, Q)
    print(f"  AO không nhiễu: sai số R theo (16) nghĩa đen = {rot_err_deg(R_lit, R):.2f} deg; "
          f"sai số R^t theo (16) = {rot_err_deg(R_lit.T, R):.2e} deg; U V^t (có sửa det) = "
          f"{rot_err_deg(R_fix, R):.2e} deg")
    print(f"  -> (16) đúng như in chỉ khi M định nghĩa là sum p' q'^t (ngược với (13)): "
          f"{verdict(rot_err_deg(R_lit.T, R) < 1e-8 and rot_err_deg(R_lit, R) > 1)} (lỗi quy ước trong bài)")
    # target phẳng z=0: (R, t) và (-R S, -t), S = diag(1,1,-1), cho q -> -q, nên E bằng nhau (tôi suy ra)
    Pp, up, Rp, tp = planar_scene(rng, 8, 3.0, 40, 1.0)
    oip = OI(Pp, normalized(up))
    Rq = random_rotation(rng); tq = rng.normal(size=3)
    S = np.diag([1.0, 1.0, -1.0])
    e1, e2 = oip.E(Rq, tq), oip.E(-Rq @ S, -tq)
    print(f"  target phẳng: E(R,t)={e1:.6e}, E(-RS,-t)={e2:.6e}, det(-RS)={np.linalg.det(-Rq @ S):+.0f} "
          f"-> song sinh sau camera cùng E {verdict(abs(e1 - e2) < 1e-12 * max(1, e1))}")


# ---------------------------------------------------------------- C1
def check1():
    print("== C1: E giảm đơn điệu (33); bất đẳng thức (31); majorant")
    rng = np.random.default_rng(1)
    n_runs = viol_E = viol_31 = viol_maj = viol_chain = 0
    worst31 = 0.0
    steps = 0
    for s in range(40):
        planar = s % 2 == 1
        X, u, _, _, _ = make_scene(8, rng, planar=planar, sigma_px=2.0)
        oi = OI(X, normalized(u))
        for _ in range(10):
            R = random_rotation(rng)
            n_runs += 1
            for k in range(60):
                t = oi.t_of_R(R)
                Ek = oi.E(R, t)
                Rn, Vq = oi.step(R)
                tn = oi.t_of_R(Rn)
                qn = X @ Rn.T + tn
                En = oi.E(Rn, tn)
                lhs31 = float(np.sum((qn - Vq) ** 2))        # vế trái (31) với t^(k+1)=t(R^(k+1))
                # chuỗi sửa lại (tôi suy ra): t_AO = mean(Vq) - R^(k+1) p_bar là t tối ưu của (25);
                # E(R^(k+1)) <= E(R^(k+1), t_AO) <= sum||R^(k+1)p+t_AO - Vq^(k)||^2 <= E(R^k)
                tAO = Vq.mean(0) - Rn @ X.mean(0)
                qa = X @ Rn.T + tAO
                c1, c2 = oi.E(Rn, tAO), float(np.sum((qa - Vq) ** 2))
                if not (En <= c1 * (1 + 1e-12) + 1e-15 and c1 <= c2 * (1 + 1e-12) + 1e-15
                        and c2 <= Ek * (1 + 1e-12) + 1e-15):
                    viol_chain += 1
                steps += 1
                if En > Ek * (1 + 1e-12) + 1e-15:
                    viol_E += 1
                if lhs31 > Ek * (1 + 1e-12) + 1e-15:
                    viol_31 += 1
                    worst31 = max(worst31, lhs31 / Ek - 1)
                # majorant: sum ||q - V q^(k)||^2 >= E(q) với q bất kỳ, bằng nhau tại q^(k)
                qr = X @ random_rotation(rng).T + rng.normal(size=3) * 3
                g = float(np.sum((qr - Vq) ** 2))
                Eq = float(np.sum((qr - np.einsum('nij,nj->ni', oi.V, qr)) ** 2))
                if g < Eq - 1e-9 * max(1, Eq):
                    viol_maj += 1
                R = Rn
    print(f"  {n_runs} lượt chạy (20 cảnh không phẳng + 20 phẳng, n=8, sigma=2px, R0 ngẫu nhiên), {steps} bước")
    print(f"  số bước E tăng: {viol_E}  -> đơn điệu {verdict(viol_E == 0)}")
    print(f"  số bước (31) sai khi t^(k+1)=t(R^(k+1)) như (27): {viol_31}"
          f" (vượt tối đa {worst31:.2%} so với E(R^k))")
    print(f"  chuỗi thay thế E(R^k+1) <= E(R^k+1,t_AO) <= g <= E(R^k) vi phạm: {viol_chain}  -> {verdict(viol_chain == 0)}")
    print(f"  majorant g >= E vi phạm: {viol_maj}  -> {verdict(viol_maj == 0)}")


# ---------------------------------------------------------------- C2
def planar_scene(rng, n, dist, tilt_deg, sigma_px):
    P = np.c_[rng.uniform(-0.5, 0.5, (n, 2)), np.zeros(n)]
    ax = rng.normal(size=2); ax /= np.linalg.norm(ax)
    w = np.radians(tilt_deg) * np.array([ax[0], ax[1], 0.0])
    Rt = cv2.Rodrigues(w)[0] @ cv2.Rodrigues(np.array([0, 0, rng.uniform(0, 2 * np.pi)]))[0]
    t = np.array([rng.uniform(-0.2, 0.2), rng.uniform(-0.2, 0.2), dist])
    Xc = P @ Rt.T + t
    uc = (K_DEFAULT @ (Xc / Xc[:, 2:3]).T).T[:, :2]
    return P, uc + rng.normal(scale=sigma_px, size=uc.shape), Rt, t


def converge_stats(name, scenes, n_init, rng):
    cnt = dict(G=0, L=0, B=0, N=0)          # G: cực tiểu toàn cục trong các nghiệm trước camera; L: điểm bất
    cnt_good = dict(G=0, L=0, B=0, N=0)     # động khác, vật trước camera; B: vật sau camera; N: chưa hội tụ
    multi_front = behind_lower = gt_is_best = wp_best = sq_best = 0
    sq_excess, iters_wp, iters_rand, it01_wp = [], [], [], []
    for (X, u, Rt, tt) in scenes:
        v = normalized(u)
        oi = OI(X, v)
        runs = []
        for _ in range(n_init):
            R0 = random_rotation(rng)
            r = oi.run(R0, max_iter=3000)
            r['init_front'] = front(R0, oi.t_of_R(R0), X)  # mọi điểm trước camera tại (R0, t(R0))
            r['front'] = front(r['R'], r['t'], X)
            runs.append(r)
            iters_rand.append(r['iters'])
        wp = oi.run(oi.init_weak_persp(v), trace=True)
        wp['front'] = front(wp['R'], wp['t'], X)
        iters_wp.append(wp['iters'])
        it01_wp.append(next(k for k, Rk in enumerate(wp['Rs']) if rot_err_deg(Rk, wp['R']) < 0.01))
        allr = [r for r in runs + [wp] if r['converged']]
        fr = [r for r in allr if r['front']]
        best = min(fr, key=lambda r: r['E'])
        Ef, Rf = best['E'], best['R']
        if min(r['E'] for r in allr) < Ef * (1 - 1e-9):
            behind_lower += 1
        fps = []
        for r in fr:
            if all(rot_err_deg(r['R'], f) > 0.5 for f in fps):
                fps.append(r['R'])
        multi_front += len(fps) >= 2
        gt_is_best += rot_err_deg(Rf, Rt) <= min(rot_err_deg(f, Rt) for f in fps) + 1e-9
        wp_best += rot_err_deg(wp['R'], Rf) < 0.05
        Rs, ts = cv_pose(X, u, cv2.SOLVEPNP_SQPNP)
        if rot_err_deg(Rs, Rf) < 0.05:
            sq_best += 1
            sq_excess.append(oi.E(Rs, oi.t_of_R(Rs)) / Ef - 1)
        for r in runs:
            if not r['converged']:
                c = 'N'
            elif not r['front']:
                c = 'B'
            elif rot_err_deg(r['R'], Rf) < 0.05:
                c = 'G'
            else:
                c = 'L'
            cnt[c] += 1
            if r['init_front']:
                cnt_good[c] += 1
    ns, tot, tg = len(scenes), sum(cnt.values()), sum(cnt_good.values())
    print(f"  [{name}] {ns} cảnh x {n_init} R0 ngẫu nhiên = {tot} lượt")
    print(f"    tới cực tiểu tốt nhất (trong các nghiệm vật-trước-camera): {cnt['G']} ({cnt['G']/tot:.1%}); "
          f"điểm bất động khác vật trước camera: {cnt['L']}; vật sau camera: {cnt['B']}; chưa hội tụ (3000 bước): {cnt['N']}")
    print(f"    chỉ R0 mà (R0, t(R0)) đặt mọi điểm trước camera (điều kiện của bài [tr. 6]): {tg} lượt -> tốt nhất {cnt_good['G']} "
          f"({cnt_good['G']/max(tg,1):.1%}), khác-trước-camera {cnt_good['L']}, sau camera {cnt_good['B']}")
    print(f"    cảnh có >=2 điểm bất động khác nhau vật trước camera: {multi_front}/{ns}; "
          f"cảnh có điểm bất động sau camera với E NHỎ HƠN hẳn nghiệm tốt nhất trước camera: {behind_lower}/{ns}")
    print(f"    cảnh mà nghiệm tốt nhất (trước camera) cũng gần R thật nhất: {gt_is_best}/{ns}; "
          f"khởi tạo weak-persp tới nghiệm tốt nhất: {wp_best}/{ns}")
    print(f"    SQPnP (cv2) cùng lưu vực (<0.05deg) với nghiệm tốt nhất: {sq_best}/{ns}; "
          f"E(SQPnP)/E_min - 1 trung vị {np.median(sq_excess) if sq_excess else float('nan'):.1e}")
    print(f"    số bước (dừng khi ||dR||_F<1e-11): weak-persp trung vị {int(np.median(iters_wp))}, "
          f"R0 ngẫu nhiên trung vị {int(np.median(iters_rand))} (p90 {int(np.percentile(iters_rand, 90))}); "
          f"weak-persp tới trong 0.01deg của điểm bất động: trung vị {int(np.median(it01_wp))} bước")


def paper_scene(rng, N, snr_db):
    """Kiểu §4.2 của bài [tr. 10]: N điểm đều trong hộp [-5,5]^3, R đều, tx,ty ~ U[5,15], tz ~ U[20,50];
    nhiễu trên toạ độ chuẩn hoá theo SNR = -20 log10(sigma tz / 10) [tr. 8]; quy ra pixel với f=800."""
    P = rng.uniform(-5, 5, (N, 3))
    R = random_rotation(rng)
    t = np.array([rng.uniform(5, 15), rng.uniform(5, 15), rng.uniform(20, 50)])
    Xc = P @ R.T + t
    uc = (K_DEFAULT @ (Xc / Xc[:, 2:3]).T).T[:, :2]
    sig_n = 10 ** (-snr_db / 20) * 10 / t[2]
    return P, uc + rng.normal(scale=800 * sig_n, size=uc.shape), R, t


def check2():
    print("== C2: hội tụ từ R0 ngẫu nhiên đều trên SO(3)")
    rng = np.random.default_rng(2)
    NI = 30
    sc = [paper_scene(rng, 20, 60.0) for _ in range(20)]
    converge_stats("kiểu bài §4.2: N=20 trong hộp [-5,5]^3, tz 20-50, SNR 60dB", sc, NI, rng)
    sc = [paper_scene(rng, 6, 50.0) for _ in range(20)]
    converge_stats("kiểu bài §4.2 nhưng N=6, SNR 50dB", sc, NI, rng)
    sc = []
    for _ in range(20):
        X, u, _, R, t = make_scene(10, rng, sigma_px=1.0)
        sc.append((X, u, R, t))
    converge_stats("common.make_scene n=10, sâu 4-8, gốc vật xa trọng tâm, sigma=1px", sc, NI, rng)
    sc = [planar_scene(rng, 8, 3.0, 40, 1.0) for _ in range(20)]
    converge_stats("phẳng n=8, vuông 1m, cách 3m, nghiêng 40deg, sigma=1px", sc, NI, rng)
    sc = [planar_scene(rng, 8, 8.0, 40, 1.0) for _ in range(20)]
    converge_stats("phẳng n=8, vuông 1m, cách 8m, nghiêng 40deg, sigma=1px", sc, NI, rng)


# ---------------------------------------------------------------- C3
def check3():
    print("== C3: tốc độ hội tụ cục bộ (bài: 'quadratic-like' [tr. 11], chỉ là phỏng đoán)")
    rng = np.random.default_rng(3)
    rates = []
    for kind in ["không phẳng", "phẳng"]:
        rates = []
        for _ in range(20):
            if kind == "phẳng":
                X, u, R, t = planar_scene(rng, 8, 3.0, 40, 1.0)
            else:
                X, u, _, R, t = make_scene(10, rng, sigma_px=1.0)
            oi = OI(X, normalized(u))
            ref = oi.run(oi.init_weak_persp(normalized(u)), tol=1e-14, max_iter=20000)
            tr = oi.run(oi.init_weak_persp(normalized(u)), tol=0, max_iter=60, trace=True)
            err = np.array([np.linalg.norm(Rk - ref['R']) for Rk in tr['Rs']])
            ok = (err > 1e-12) & (err < 1e-3)
            idx = np.where(ok[1:] & ok[:-1])[0]
            if len(idx) >= 3:
                rates.append(np.median(err[idx + 1] / err[idx]))
        rates = np.array(rates)
        print(f"  [{kind}] tỉ số ||R_(k+1)-R*|| / ||R_k-R*|| gần nghiệm: trung vị {np.median(rates):.3f}, "
              f"khoảng [{rates.min():.3f}, {rates.max():.3f}] trên {len(rates)} cảnh "
              f"-> hội tụ {'TUYẾN TÍNH' if np.median(rates) > 0.02 else 'siêu tuyến tính'}")


# ---------------------------------------------------------------- C4
def check4():
    print("== C4: độ chính xác theo nhiễu pixel đẳng hướng (n=10, không phẳng, sâu 4-8, f=800, 200 lần/mức)")
    rng = np.random.default_rng(4)
    print("  sigma | trung vị sai số R (deg): OI  ITER  SQPNP  LM* | trung vị sai số t tương đối: OI  ITER  SQPNP  LM*"
          " | OI vs LM*: dR(deg) dt(rel)  RMSE_OI/RMSE_LM*")
    for sig in [0.5, 1.0, 2.0, 5.0]:
        er = {k: [] for k in ["OI", "IT", "SQ", "LM"]}
        et = {k: [] for k in er}
        dR, dt, rr = [], [], []
        for _ in range(200):
            X, u, _, R, t = make_scene(10, rng, sigma_px=sig)
            v = normalized(u)
            oi = OI(X, v)
            r = oi.run(oi.init_weak_persp(v))
            sol = {"OI": (r['R'], r['t']),
                   "IT": cv_pose(X, u, cv2.SOLVEPNP_ITERATIVE),
                   "SQ": cv_pose(X, u, cv2.SOLVEPNP_SQPNP)}
            # nghiệm tối ưu không gian ảnh: LM tinh chỉnh từ OI, giữ nghiệm reprojection nhỏ nhất
            cands = [lm_refine(X, u, *sol[k]) for k in sol]
            sol["LM"] = min(cands, key=lambda p: reproj_rmse(X, u, *p))
            for k, (Re, te) in sol.items():
                er[k].append(rot_err_deg(Re, R))
                et[k].append(trans_err_rel(te, t))
            dR.append(rot_err_deg(sol["OI"][0], sol["LM"][0]))
            dt.append(trans_err_rel(sol["OI"][1], sol["LM"][1]))
            rr.append(reproj_rmse(X, u, *sol["OI"]) / reproj_rmse(X, u, *sol["LM"]))
        med = lambda a: float(np.median(a))  # noqa: E731
        print(f"  {sig:4.1f}  |  {med(er['OI']):.4f} {med(er['IT']):.4f} {med(er['SQ']):.4f} {med(er['LM']):.4f}"
              f" | {med(et['OI']):.5f} {med(et['IT']):.5f} {med(et['SQ']):.5f} {med(et['LM']):.5f}"
              f" | {med(dR):.4f} {med(dt):.5f} {med(rr):.4f}")
    print("  (LM* = cực tiểu sai số tái chiếu, tinh chỉnh LM từ nghiệm tốt nhất trong OI/ITER/SQPNP)")


# ---------------------------------------------------------------- C5
def check5():
    corners = np.array([[x, y, z] for x in (-5, 5) for y in (-5, 5) for z in (-5, 5)], float)
    for sig in [1.0, 5.0]:
        print(f"== C5: thiên lệch theo độ sâu (§3.5, kiểu D1: 8 đỉnh hộp [-5,5]^3, tx=ty=5, "
              f"sigma={sig}px @ f=800, 200 lần/mức)")
        rng = np.random.default_rng(5)
        print("  tz/10 | SNR(dB) theo định nghĩa của bài | TB sai số t tương đối (%): OI  LM* | TB sai số R (deg): OI  LM*"
              " | TB sai lệch t_z có dấu (%): OI  LM*")
        for d in [1.5, 2.0, 3.5, 5.0, 10.0, 20.0]:
            tz = 10 * d
            eo, el, ro, rl, bo, bl = [], [], [], [], [], []
            for _ in range(200):
                R = random_rotation(rng)
                t = np.array([5.0, 5.0, tz])
                Xc = corners @ R.T + t
                uc = (K_DEFAULT @ (Xc / Xc[:, 2:3]).T).T[:, :2]
                u = uc + rng.normal(scale=sig, size=uc.shape)
                v = normalized(u)
                oi = OI(corners, v)
                r = oi.run(oi.init_weak_persp(v))
                Rl, tl = lm_refine(corners, u, r['R'], r['t'])
                eo.append(trans_err_rel(r['t'], t)); el.append(trans_err_rel(tl, t))
                ro.append(rot_err_deg(r['R'], R)); rl.append(rot_err_deg(Rl, R))
                bo.append((r['t'][2] - tz) / tz); bl.append((tl[2] - tz) / tz)
            snr = -20 * np.log10(sig / 800 * tz / 10)
            print(f"  {d:5.1f} | {snr:5.1f} | {100*np.mean(eo):6.3f} {100*np.mean(el):6.3f} | "
                  f"{np.mean(ro):.4f} {np.mean(rl):.4f} | {100*np.mean(bo):+6.3f} {100*np.mean(bl):+6.3f}")


# ---------------------------------------------------------------- C6
def check6():
    print("== C6: dựng lại thí nghiệm C1 của bài [tr. 10-11] (N=20, PO=0, SNR 30-70dB), 200 lần/mức; so với Fig. 11-12")
    rng = np.random.default_rng(6)
    print("  SNR | TB sai số R (deg): OI  LM* | TB sai số t tương đối: OI  LM* | TB ||dt|| tuyệt đối (đơn vị hộp): OI  LM*")
    for snr in [30, 40, 50, 60, 70]:
        ro, rl, to, tl, ao, al = [], [], [], [], [], []
        for _ in range(200):
            P, u, R, t = paper_scene(rng, 20, snr)
            v = normalized(u)
            oi = OI(P, v)
            r = oi.run(oi.init_weak_persp(v))
            Rl, tl_ = lm_refine(P, u, r['R'], r['t'])
            ro.append(rot_err_deg(r['R'], R)); rl.append(rot_err_deg(Rl, R))
            to.append(trans_err_rel(r['t'], t)); tl.append(trans_err_rel(tl_, t))
            ao.append(np.linalg.norm(r['t'] - t)); al.append(np.linalg.norm(tl_ - t))
        print(f"  {snr:3d} | {np.mean(ro):.4f} {np.mean(rl):.4f} | {np.mean(to):.5f} {np.mean(tl):.5f}"
              f" | {np.mean(ao):.4f} {np.mean(al):.4f}")


if __name__ == "__main__":
    t0 = time.time()
    check0()
    check1()
    check2()
    check3()
    check4()
    check5()
    check6()
    print(f"Tổng thời gian: {time.time()-t0:.1f} s")
