"""Kiểm chứng số (cửa (b)) cho lepetit2009epnp — EPnP, IJCV 81(2) 2009.

Cài lại EPnP từ mô tả trong bài (không chép mã OpenCV/EPFL):
  - điểm điều khiển: trọng tâm + 3 trục PCA, độ dài sqrt(trị riêng hiệp phương sai) [§3.1, tr. 4-5]
    (độ dài trục là lựa chọn của tôi; bài chỉ nói "basis aligned with the principal directions")
  - ma trận M 2n x 12 theo eq. (5)-(6), nghiệm = tổ hợp vector riêng nhỏ nhất của M^T M, eq. (8)
  - N = 1 (eq. 11), N = 2 (tuyến tính hoá 6x3, eq. 13), N = 3 (6x6), N = 4 (tái tuyến tính hoá, eq. 14)
  - chọn N theo sai số tái chiếu nhỏ nhất, eq. (9)
  - trường hợp phẳng: 3 điểm điều khiển, M 2n x 9, 3 ràng buộc khoảng cách [§3.4]
  - Gauss-Newton trên beta, eq. (15) (tôi bình phương số hạng trong ngoặc — xem ghi chú mục 8)
So sánh với cv2.solvePnP(flags=SOLVEPNP_EPNP) và LM trên sai số tái chiếu (cv2.solvePnPRefineLM).
Chạy:  python3 VSLAM/pnp/code/lepetit2009epnp_check.py      (< 3 phút, seed cố định)
"""
import os
import sys
import time
import itertools

sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
import cv2
from common import random_rotation, project, rot_err_deg, proj_to_so3  # noqa: F401

FU = FV = 800.0
UC, VC = 320.0, 240.0
K = np.array([[FU, 0, UC], [0, FV, VC], [0, 0, 1.0]])
PAIRS4 = list(itertools.combinations(range(4), 2))   # 6 cặp điểm điều khiển
PAIRS3 = list(itertools.combinations(range(3), 2))   # 3 cặp (phẳng)


# ----------------------------------------------------------------------------- EPnP
def _sym_index(N):
    """Danh sách (k,l), k<=l, thứ tự của các beta_kl."""
    return [(k, l) for k in range(N) for l in range(k, N)]


def _build_L(V, pairs, cw):
    """L: hàng = cặp (a,b); cột = beta_kl (k<=l). rho = ||cw_a - cw_b||^2.  eq. (12)-(13)."""
    N = V.shape[1]
    nc = V.shape[0] // 3
    idx = _sym_index(N)
    Vr = V.reshape(nc, 3, N)
    L = np.zeros((len(pairs), len(idx)))
    rho = np.zeros(len(pairs))
    for r, (a, b) in enumerate(pairs):
        dv = Vr[a] - Vr[b]                      # 3 x N
        G = dv.T @ dv                           # N x N, G_kl = dv_k . dv_l
        for c, (k, l) in enumerate(idx):
            L[r, c] = G[k, k] if k == l else 2 * G[k, l]
        rho[r] = np.sum((cw[a] - cw[b]) ** 2)
    return L, rho


def _beta_from_B(bvec, N):
    """Từ các beta_kl lấy beta_k: đối xứng hoá thành ma trận B rồi xấp xỉ hạng 1."""
    B = np.zeros((N, N))
    for c, (k, l) in enumerate(_sym_index(N)):
        B[k, l] = B[l, k] = bvec[c]
    w, E = np.linalg.eigh(B)
    return np.sqrt(max(w[-1], 0.0)) * E[:, -1]


def _beta_sqrt_sign(bvec, N):
    """Cách của bài cho N=2,3: beta_1 = sqrt|beta_11|, beta_k = sign(beta_1k) sqrt|beta_kk|."""
    idx = _sym_index(N)
    d = {kl: bvec[c] for c, kl in enumerate(idx)}
    b = np.zeros(N)
    b[0] = np.sqrt(abs(d[(0, 0)]))
    for k in range(1, N):
        b[k] = np.sign(d[(0, k)]) * np.sqrt(abs(d[(k, k)]))
    return b


def _relinearize(L, rho, N, return_rank=False):
    """Tái tuyến tính hoá (Kipnis-Shamir) như eq. (14): [L | -rho][beta;1] = 0 -> không gian nhân,
    rồi các ràng buộc beta_ab beta_cd = beta_ac beta_bd tuyến tính theo các tích lambda_k lambda_l."""
    A = np.c_[L, -rho]
    _, s, Vt = np.linalg.svd(A)
    rank = int(np.sum(s > 1e-12 * s[0]))
    Nul = Vt[rank:].T                            # (m+1) x d, d = dim nhân
    d = Nul.shape[1]
    B = np.zeros((N, N, d))                      # B[a,b,:] = hệ số của beta_ab theo lambda
    for c, (k, l) in enumerate(_sym_index(N)):
        B[k, l] = B[l, k] = Nul[c]
    lam_idx = _sym_index(d)
    # beta_ab beta_ce - beta_ac beta_be = 0 cho mọi (a,b,c,e)  (hoán vị b <-> c)
    P = np.einsum('abk,cel->abcekl', B, B) - np.einsum('ack,bel->abcekl', B, B)
    P = (P + np.swapaxes(P, -1, -2)).reshape(-1, d, d)
    ku, lu = np.triu_indices(d)
    W = np.where(ku == lu, 0.5, 1.0)
    R = P[:, ku, lu] * W                         # hàng = phương trình, cột = đơn thức lambda_k lambda_l
    R = R[np.linalg.norm(R, axis=1) > 1e-14]
    _, s2, Vt2 = np.linalg.svd(R, full_matrices=False)
    rank2 = int(np.sum(s2 > 1e-10 * s2[0]))
    if return_rank:
        return rank2, len(lam_idx)
    Lam = np.zeros((d, d))
    for c, (k, l) in enumerate(lam_idx):
        Lam[k, l] = Lam[l, k] = Vt2[-1, c]
    w, E = np.linalg.eigh(Lam)
    j = np.argmax(np.abs(w))
    lam = np.sqrt(abs(w[j])) * E[:, j]
    btil = Nul @ lam
    btil = btil / btil[-1]                       # thành phần cuối = 1
    return _beta_from_B(btil[:-1], N)


def _pose_from_ctrl(Cc, alphas, Pw):
    """p_i^c = sum_j alpha_ij c_j^c, rồi căn chỉnh Procrustes (Arun/Horn/Umeyama không tỉ lệ)."""
    Pc = alphas @ Cc
    if np.mean(Pc[:, 2]) < 0:                    # chọn dấu để điểm nằm trước camera
        Pc = -Pc
    mw, mc = Pw.mean(0), Pc.mean(0)
    H = (Pc - mc).T @ (Pw - mw)
    R = proj_to_so3(H)
    t = mc - R @ mw
    return R, t


def _reproj_res(Pw, u, R, t):
    return float(np.sum((project(Pw, R, t, K) - u) ** 2))   # eq. (9)


def _gauss_newton(beta, V, pairs, cw, iters=10):
    """eq. (15)-(16): cực tiểu sum_(a<b) (||c_a^c - c_b^c||^2 - ||c_a^w - c_b^w||^2)^2 theo beta."""
    nc = V.shape[0] // 3
    Vr = V.reshape(nc, 3, V.shape[1])
    D = np.array([Vr[a] - Vr[b] for a, b in pairs])          # P x 3 x N
    rho = np.array([np.sum((cw[a] - cw[b]) ** 2) for a, b in pairs])
    beta = beta.copy()
    for _ in range(iters):
        dc = D @ beta                                           # P x 3
        r = np.sum(dc ** 2, 1) - rho
        J = 2 * np.einsum('pi,pik->pk', dc, D)
        step, *_ = np.linalg.lstsq(J, -r, rcond=None)
        beta += step
        if np.linalg.norm(step) < 1e-12 * (1 + np.linalg.norm(beta)):
            break
    return beta


def epnp(Pw, u, planar=None, gn=False, info=None):
    """EPnP theo bài. planar=None: tự quyết định theo trị riêng nhỏ nhất của ma trận mômen."""
    n = len(Pw)
    c0 = Pw.mean(0)
    Q = Pw - c0
    lam, E = np.linalg.eigh(Q.T @ Q / n)                        # tăng dần
    if planar is None:
        planar = lam[0] < 1e-10 * lam[2]                        # ngưỡng: lựa chọn của tôi
    if planar:
        axes = [E[:, 2], E[:, 1]]
        sc = [np.sqrt(lam[2]), np.sqrt(lam[1])]
        cw = np.array([c0] + [c0 + s * a for s, a in zip(sc, axes)])
        B2 = (Q @ np.array(axes).T) / np.array(sc)             # toạ độ trong mặt phẳng
        alphas = np.c_[1 - B2.sum(1), B2]
        pairs, nc = PAIRS3, 3
    else:
        axes = [E[:, 2], E[:, 1], E[:, 0]]
        sc = [np.sqrt(lam[2]), np.sqrt(lam[1]), np.sqrt(lam[0])]
        cw = np.array([c0] + [c0 + s * a for s, a in zip(sc, axes)])
        C = (cw[1:] - cw[0]).T
        B3 = np.linalg.solve(C, Q.T).T
        alphas = np.c_[1 - B3.sum(1), B3]                      # eq. (1)
        pairs, nc = PAIRS4, 4
    # M: eq. (5)-(6)
    M = np.zeros((2 * n, 3 * nc))
    M[0::2, 0::3] = alphas * FU
    M[0::2, 2::3] = alphas * (UC - u[:, [0]])
    M[1::2, 1::3] = alphas * FV
    M[1::2, 2::3] = alphas * (VC - u[:, [1]])
    w, Vall = np.linalg.eigh(M.T @ M)                           # 12x12 (hoặc 9x9)
    Nmax = 4 if not planar else 3
    cands = []
    for N in range(1, Nmax + 1):
        V = Vall[:, :N]
        L, rho = _build_L(V, pairs, cw)
        try:
            if N == 1:
                v = V[:, 0].reshape(nc, 3)
                dv = np.array([np.linalg.norm(v[a] - v[b]) for a, b in pairs])
                dw = np.array([np.linalg.norm(cw[a] - cw[b]) for a, b in pairs])
                beta = np.array([dv @ dw / (dv @ dv)])          # eq. (11)
            elif L.shape[1] <= L.shape[0]:                     # N=2 (6x3 / 3x3), N=3 (6x6)
                bvec = np.linalg.lstsq(L, rho, rcond=None)[0]
                beta = _beta_sqrt_sign(bvec, N)
                # tinh lại tỉ lệ chung theo eq. (11)
                v = (V @ beta).reshape(nc, 3)
                dv = np.array([np.linalg.norm(v[a] - v[b]) for a, b in pairs])
                dw = np.array([np.linalg.norm(cw[a] - cw[b]) for a, b in pairs])
                beta = beta * (dv @ dw / (dv @ dv))
            else:                                               # N=4 (hoặc N=3 phẳng)
                beta = _relinearize(L, rho, N)
        except np.linalg.LinAlgError:
            continue
        bfull = np.zeros(Nmax)
        bfull[:N] = beta
        if gn:
            bfull = _gauss_newton(bfull, Vall[:, :Nmax], pairs, cw)
        Cc = (Vall[:, :Nmax] @ bfull).reshape(nc, 3)
        R, t = _pose_from_ctrl(Cc, alphas, Pw)
        cands.append((_reproj_res(Pw, u, R, t), N, R, t))
    rmin = min(c[0] for c in cands)
    # khi hoà (dữ liệu không nhiễu, mọi N đều khớp) ưu tiên N nhỏ — lựa chọn của tôi, bài không nói
    res, N, R, t = min((c for c in cands if c[0] <= rmin * (1 + 1e-6) + 1e-12), key=lambda c: c[1])
    if info is not None:
        info['N'] = N
        info['eig'] = w
        info['planar'] = planar
    return R, t


# ----------------------------------------------------------------------------- tiện ích
def quat(R):
    q = np.empty(4)
    tr = np.trace(R)
    if tr > 0:
        s = np.sqrt(tr + 1) * 2
        q[:] = [s / 4, (R[2, 1] - R[1, 2]) / s, (R[0, 2] - R[2, 0]) / s, (R[1, 0] - R[0, 1]) / s]
    else:
        i = np.argmax(np.diag(R))
        j, k = (i + 1) % 3, (i + 2) % 3
        s = np.sqrt(1 + R[i, i] - R[j, j] - R[k, k]) * 2
        q[0] = (R[k, j] - R[j, k]) / s
        q[1 + i] = s / 4
        q[1 + j] = (R[j, i] + R[i, j]) / s
        q[1 + k] = (R[k, i] + R[i, k]) / s
    return q / np.linalg.norm(q)


def erot_pct(R, Rt):
    """Thước đo của bài [§5.1, tr. 9]: ||q_true - q|| / ||q|| (%), có xử lý dấu q ~ -q."""
    q, qt = quat(R), quat(Rt)
    return 100 * min(np.linalg.norm(qt - q), np.linalg.norm(qt + q))


def etrans_pct(t, tt):
    return 100 * np.linalg.norm(tt - t) / np.linalg.norm(t)   # đúng như bài: chia cho ||t|| ước lượng


def paper_scene(n, rng, sigma=0.0, centered=True):
    """Cảnh của bài [§5.1, tr. 9]: điểm đều trong hộp [-2,2]x[-2,2]x[4,8] (centered) hoặc
    [1,2]x[1,2]x[4,8] (uncentered) *trong hệ camera*. Hệ thế giới: quay ngẫu nhiên quanh trọng tâm
    hộp (bài không nói — lựa chọn của tôi; EPnP bất biến với hệ thế giới)."""
    lo, hi = ([-2, -2, 4], [2, 2, 8]) if centered else ([1, 1, 4], [2, 2, 8])
    Xc = rng.uniform(lo, hi, size=(n, 3))
    R = random_rotation(rng)
    t = np.array([(lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, 6.0])
    Xw = (R.T @ (Xc - t).T).T
    uc = project(Xw, R, t, K)
    return Xw, uc + rng.normal(scale=sigma, size=uc.shape), R, t


def planar_scene(n, rng, sigma=0.0, tilt_deg=30.0, thick=0.0):
    """Mặt phẳng hình vuông [-2,2]^2 ở độ sâu 6, nghiêng tilt quanh trục x camera (bài không cho
    kích thước/độ sâu của cảnh phẳng — lựa chọn của tôi). thick>0: 'gần phẳng'."""
    P = np.c_[rng.uniform(-2, 2, (n, 2)), rng.uniform(-thick, thick, n) if thick > 0 else np.zeros(n)]
    a = np.radians(tilt_deg)
    Rt = np.array([[1, 0, 0], [0, np.cos(a), -np.sin(a)], [0, np.sin(a), np.cos(a)]])
    Rw = random_rotation(rng)                  # hệ thế giới xoay tuỳ ý
    R = Rt @ Rw
    t = np.array([0, 0, 6.0])
    Xw = (Rw.T @ P.T).T
    uc = project(Xw, R, t, K)
    return Xw, uc + rng.normal(scale=sigma, size=uc.shape), R, t


def cv_epnp(Xw, u):
    ok, rv, tv = cv2.solvePnP(Xw.astype(np.float64), u.astype(np.float64), K, None,
                              flags=cv2.SOLVEPNP_EPNP)
    return cv2.Rodrigues(rv)[0], tv.ravel()


def lm_refine(Xw, u, R, t):
    rv = cv2.Rodrigues(R)[0]
    tv = t.reshape(3, 1).copy()
    rv, tv = cv2.solvePnPRefineLM(Xw, u, K, None, rv, tv)
    return cv2.Rodrigues(rv)[0], tv.ravel()


def line(s):
    print(s, flush=True)


# ----------------------------------------------------------------------------- các kiểm
def check_exact():
    line("\n[1] Không nhiễu: khôi phục chính xác, n = 4..50 (20 cảnh / n)")
    rng = np.random.default_rng(1)
    ns = [4, 5, 6, 7, 8, 10, 15, 20, 30, 50]
    for kind in ["khong-phang", "phang"]:
        worst_me, worst_cv, Ns, cvbad = 0.0, 0.0, {}, {}
        per_n, nulldim = [], {}
        for n in ns:
            wm = 0.0
            for _ in range(20):
                if kind == "khong-phang":
                    Xw, u, Rt, tt = paper_scene(n, rng)
                else:
                    Xw, u, Rt, tt = planar_scene(n, rng)
                info = {}
                R, t = epnp(Xw, u, info=info)
                e = max(np.linalg.norm(R - Rt), np.linalg.norm(t - tt) / np.linalg.norm(tt))
                wm = max(wm, e)
                ev = info['eig']
                nulldim.setdefault(n, set()).add(int(np.sum(ev < 1e-12 * ev[-1])))
                Ns[info['N']] = Ns.get(info['N'], 0) + 1
                Rc, tc = cv_epnp(Xw, u)
                ec = np.linalg.norm(Rc - Rt)
                worst_cv = max(worst_cv, ec)
                cvbad[n] = cvbad.get(n, 0) + int(ec > 1e-6)
            per_n.append((n, wm))
            worst_me = max(worst_me, wm)
        ok = worst_me < 1e-8
        line(f"  {kind:12s} EPnP của tôi: max(||R-R*||_F, ||t-t*||/||t*||) = {worst_me:.1e}  "
             f"-> {'PASS' if ok else 'FAIL'};  N được chọn: {dict(sorted(Ns.items()))}")
        line(f"      số chiều nhân của M^T M (trị riêng < 1e-12 max) theo n: "
             + ", ".join(f"{n}:{sorted(v)}" for n, v in nulldim.items()))
        bad = [(n, f"{e:.1e}") for n, e in per_n if e >= 1e-8]
        if bad:
            line(f"      các n hỏng: {bad}")
        line(f"  {kind:12s} cv2 SOLVEPNP_EPNP: max ||R-R*||_F = {worst_cv:.1e}; "
             f"số cảnh sai (>1e-6) theo n: {cvbad}")


def check_relin_counting():
    line("\n[2] Đếm ẩn/phương trình của tái tuyến tính hoá (eq. 14)")
    rng = np.random.default_rng(2)
    for N, pairs, nc, name in [(4, PAIRS4, 4, "không phẳng N=4"), (3, PAIRS3, 3, "phẳng N=3")]:
        V = np.linalg.qr(rng.normal(size=(3 * nc, N)))[0]
        cw = (V @ rng.normal(size=N)).reshape(nc, 3)     # dữ liệu nhất quán: có beta đúng
        L, rho = _build_L(V, pairs, cw)
        rank2, nmono = _relinearize(L, rho, N, return_rank=True)
        need = nmono - 1
        line(f"  {name}: {L.shape[0]} ràng buộc, {L.shape[1]} ẩn beta_ab -> nhân dim {L.shape[1]+1-L.shape[0]}; "
             f"hệ tái tuyến tính hoá có hạng {rank2} trên {nmono} đơn thức "
             f"(cần hạng {need} để nghiệm duy nhất) -> {'ĐỦ' if rank2 >= need else 'THIẾU'}")


def check_noise():
    line("\n[3] Sai số theo nhiễu, n = 6, dữ liệu 'centered' của bài, 300 lần/mức "
         "(E_rot, E_trans theo % của bài; median | mean)")
    rng = np.random.default_rng(3)
    meths = ["EPnP(tôi)", "EPnP+GN(tôi)", "cv2 EPNP", "+LM tái chiếu"]
    line("  sigma | " + " | ".join(f"{m:>22s}" for m in meths))
    for sigma in [0, 1, 3, 5, 10, 15]:
        E = {m: [] for m in meths}
        for _ in range(300):
            Xw, u, Rt, tt = paper_scene(6, rng, sigma)
            outs = {}
            outs["EPnP(tôi)"] = epnp(Xw, u)
            outs["EPnP+GN(tôi)"] = epnp(Xw, u, gn=True)
            outs["cv2 EPNP"] = cv_epnp(Xw, u)
            outs["+LM tái chiếu"] = lm_refine(Xw, u, *outs["EPnP+GN(tôi)"])
            for m in meths:
                R, t = outs[m]
                E[m].append((erot_pct(R, Rt), etrans_pct(t, tt)))
        cells = []
        for m in meths:
            a = np.array(E[m])
            cells.append(f"R {np.median(a[:,0]):4.1f}|{np.mean(a[:,0]):5.1f} t {np.median(a[:,1]):4.1f}|{np.mean(a[:,1]):5.1f}")
        line(f"  {sigma:5d} | " + " | ".join(f"{c:>22s}" for c in cells))


def check_npts():
    line("\n[4] Sai số theo số điểm, sigma = 5 px, 'centered' (Fig. 5c) và 'uncentered' (Fig. 5d), "
         "300 lần; median E_rot % [mean]")
    rng = np.random.default_rng(4)
    for centered in [True, False]:
        line(f"  {'centered' if centered else 'uncentered'}:")
        for n in [5, 6, 8, 10, 15, 20, 50]:
            E = {k: [] for k in ["me", "gn", "cv", "lm"]}
            for _ in range(300):
                Xw, u, Rt, tt = paper_scene(n, rng, 5.0, centered)
                Rm, tm = epnp(Xw, u)
                Rg, tg = epnp(Xw, u, gn=True)
                Rc, tc = cv_epnp(Xw, u)
                Rl, tl = lm_refine(Xw, u, Rg, tg)
                for k, R in zip(E, [Rm, Rg, Rc, Rl]):
                    E[k].append(erot_pct(R, Rt))
            s = "  ".join(f"{k}={np.median(v):5.2f} [{np.mean(v):5.1f}]" for k, v in E.items())
            line(f"    n={n:3d}: {s}")


def check_fig4():
    line("\n[5] Phân bố N được chọn theo eq. (9) (so với Fig. 4), 300 lần")
    rng = np.random.default_rng(5)
    for n, sigma in [(6, 0), (6, 5), (6, 15), (5, 10), (10, 10), (20, 10)]:
        cnt = np.zeros(5, int)
        for _ in range(300):
            Xw, u, Rt, tt = paper_scene(n, rng, sigma)
            info = {}
            epnp(Xw, u, info=info)
            cnt[info['N']] += 1
        line(f"  n={n:2d} sigma={sigma:2d}: tỉ lệ N=1..4 -> " + " ".join(f"{x:.2f}" for x in cnt[1:] / 300))


def check_fig3():
    line("\n[6] Trị riêng nhỏ nhất của M^T M khi camera tiến tới trực giao (Fig. 3), không nhiễu, n = 20")
    global FU, FV, K
    rng = np.random.default_rng(6)
    f0 = FU
    for f in [800.0, 10000.0, 100000.0]:
        FU = FV = f
        K = np.array([[f, 0, UC], [0, f, VC], [0, 0, 1.0]])
        acc = []
        for _ in range(50):
            Xc = rng.uniform([-2, -2, -2], [2, 2, 2], size=(20, 3)) + [0, 0, 6.0 * f / f0]
            R = random_rotation(rng)
            t = np.array([0, 0, 6.0 * f / f0])
            Xw = (R.T @ (Xc - t).T).T
            info = {}
            epnp(Xw, project(Xw, R, t, K), info=info)
            acc.append(info['eig'][:5] / info['eig'][-1])
        line(f"  f={f:8.0f} (độ sâu x{f/f0:5.1f}): 5 trị riêng nhỏ nhất / lớn nhất = "
             + " ".join(f"{x:.1e}" for x in np.median(acc, 0)))
    FU = FV = f0
    K = np.array([[f0, 0, UC], [0, f0, VC], [0, 0, 1.0]])


def check_planar():
    line("\n[7] Phẳng, n = 10, 300 lần: median E_rot % và tỉ lệ 'hỏng' (E_rot > 20%, ngưỡng của tôi)")
    rng = np.random.default_rng(7)
    for tilt in [0.0, 30.0]:
        for sigma in [1, 5, 10]:
            E = {k: [] for k in ["me", "gn", "cv"]}
            for _ in range(300):
                Xw, u, Rt, tt = planar_scene(10, rng, sigma, tilt)
                outs = [epnp(Xw, u), epnp(Xw, u, gn=True), cv_epnp(Xw, u)]
                for k, (R, t) in zip(E, outs):
                    E[k].append(erot_pct(R, Rt))
            s = "  ".join(f"{k}: med {np.median(v):5.2f} hỏng {np.mean(np.array(v) > 20):4.0%}" for k, v in E.items())
            line(f"  tilt={tilt:4.0f} sigma={sigma:2d}: {s}")


def check_near_planar():
    line("\n[8] Gần phẳng: bề dày +-eps quanh mặt phẳng [-2,2]^2, tilt 30, n = 20, 200 lần; median E_rot %")
    rng = np.random.default_rng(8)
    for sigma in [0.0, 1.0]:
        for eps in [0.5, 1e-1, 1e-2, 1e-3, 1e-5]:
            E = {k: [] for k in ["4 đ.đ.khiển", "3 đ.đ.khiển", "cv2"]}
            for _ in range(200):
                Xw, u, Rt, tt = planar_scene(20, rng, sigma, 30.0, thick=eps)
                outs = [epnp(Xw, u, planar=False, gn=True), epnp(Xw, u, planar=True, gn=True), cv_epnp(Xw, u)]
                for k, (R, t) in zip(E, outs):
                    E[k].append(erot_pct(R, Rt))
            s = "  ".join(f"{k}={np.median(v):8.1e}" for k, v in E.items())
            line(f"  sigma={sigma:.0f} eps={eps:6.0e}: {s}")


def check_timing():
    line("\n[9] Thời gian (CPU của container, numpy/Python; median 25 lần) — kiểm O(n)")
    rng = np.random.default_rng(9)
    ns = [10, 30, 100, 300, 1000, 3000, 5000]
    T = {"EPnP(tôi)": [], "EPnP+GN(tôi)": [], "cv2 EPNP": []}
    for n in ns:
        Xw, u, Rt, tt = paper_scene(n, rng, 2.0)
        epnp(Xw, u); cv_epnp(Xw, u)                              # làm nóng
        for name, fn in [("EPnP(tôi)", lambda: epnp(Xw, u)), ("EPnP+GN(tôi)", lambda: epnp(Xw, u, gn=True)),
                         ("cv2 EPNP", lambda: cv_epnp(Xw, u))]:
            ts = []
            for _ in range(25):
                t0 = time.perf_counter()
                fn()
                ts.append(time.perf_counter() - t0)
            T[name].append(np.median(ts))
    line("  n     : " + " ".join(f"{n:>8d}" for n in ns))
    for name, v in T.items():
        v = np.array(v)
        sl = np.polyfit(np.log(ns[3:]), np.log(v[3:]), 1)[0]
        line(f"  {name:13s}: " + " ".join(f"{x*1e3:7.2f}ms" for x in v) + f"   độ dốc log-log (n>=300) = {sl:.2f}")
        # chi phí biên mỗi điểm: nếu O(n) thì hai ước lượng dưới đây phải xấp xỉ nhau (O(n^2) -> gấp ~2)
        m1 = (v[5] - v[4]) / (ns[5] - ns[4])
        m2 = (v[6] - v[5]) / (ns[6] - ns[5])
        line(f"  {'':13s}  chi phí biên/điểm: 1000->3000: {m1*1e6:.3f} us, 3000->5000: {m2*1e6:.3f} us")
    d = [T["EPnP+GN(tôi)"][i] - T["EPnP(tôi)"][i] for i in range(len(ns))]
    line("  chênh lệch GN - không GN theo n: " + " ".join(f"{x*1e3:.2f}" for x in d) + " ms")


if __name__ == "__main__":
    t0 = time.time()
    check_exact()
    check_relin_counting()
    check_noise()
    check_npts()
    check_fig4()
    check_fig3()
    check_planar()
    check_near_planar()
    check_timing()
    line(f"\nTổng thời gian: {time.time() - t0:.0f} s")
