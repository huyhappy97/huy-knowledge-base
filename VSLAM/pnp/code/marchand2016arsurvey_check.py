"""Kiểm chứng số (cửa (b)) cho marchand2016arsurvey — Marchand, Uchiyama, Spindler, TVCG 2016.

Cài đặt ĐÚNG như bài viết (đối chiếu trang PDF 4-6, 10):
  - DLT cho pose: eq. (4)-(5), toạ độ chuẩn hoá x = K^-1 u, h = (r1, tx, r2, ty, r3, tz),
    nghiệm = vector kỳ dị phải nhỏ nhất của A, rồi "trực chuẩn hoá" R (chú thích tr. 4).
  - Gauss-Newton / virtual visual servoing: eq. (6)-(11), dq = -J^+ e, J là ma trận tương tác
    điểm của eq. (11), cập nhật "q_{k+1} = q_k (+) dq = exp^{dq} q" (tr. 5).
  - IRLS với M-estimator: eq. (12)-(13), dq = -(W J)^+ W e, trọng số Tukey.
  - RANSAC: số vòng N = log(1-p) / log(1-(1-eta)^n) (tr. 5-6) và hai con số 5 / 72 (tr. 6).
  - Target phẳng: DLT homography eq. (23), pose từ H theo eq. (26)-(27): (c1, c2, t) = H, c3 = c1 x c2.
So với cv2.solvePnP (SOLVEPNP_ITERATIVE, SOLVEPNP_EPNP). Seed cố định. Chạy: python marchand2016arsurvey_check.py
"""
import os
import sys
import time

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")   # ma trận nhỏ: đa luồng BLAS chỉ làm chậm

import numpy as np
import cv2
from scipy.optimize import least_squares

sys.path.insert(0, os.path.dirname(__file__))
from common import (K_DEFAULT, make_scene, rot_err_deg, trans_err_rel, proj_to_so3,  # noqa: E402
                    rodrigues)

K = K_DEFAULT
Kinv = np.linalg.inv(K)
RESULTS = []


def verdict(name, ok, detail=""):
    RESULTS.append((name, ok))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


def to_norm(u):
    x = (Kinv @ np.c_[u, np.ones(len(u))].T).T
    return x[:, :2]


# ---------------------------------------------------------------- DLT, eq. (4)-(5)
def dlt_A(X, x):
    rows = []
    for (Xw, Yw, Zw), (xi, yi) in zip(X, x):
        rows.append([Xw, Yw, Zw, 1, 0, 0, 0, 0, -xi*Xw, -xi*Yw, -xi*Zw, -xi])
        rows.append([0, 0, 0, 0, Xw, Yw, Zw, 1, -yi*Xw, -yi*Yw, -yi*Zw, -yi])
    return np.array(rows)


def dlt_pose(X, x, literal=False):
    """literal=True: đúng những gì bài viết nói (chỉ trực chuẩn hoá R, t giữ nguyên thang của h).
    literal=False: thêm bước bài viết KHÔNG nói — khử thang và dấu của h."""
    A = dlt_A(X, x)
    _, S, Vt = np.linalg.svd(A)
    h = Vt[-1]
    P = h.reshape(3, 4)          # hàng: (r1 tx), (r2 ty), (r3 tz)
    M, tt = P[:, :3], P[:, 3]
    if literal:
        return proj_to_so3(M), tt, S
    s = np.sign(np.linalg.det(M)) / np.cbrt(abs(np.linalg.det(M)))   # khử thang + dấu
    return proj_to_so3(s * M), s * tt, S


# ---------------------------------------------------------------- GN / VVS, eq. (6)-(11)
def hat(w):
    return np.array([[0, -w[2], w[1]], [w[2], 0, -w[0]], [-w[1], w[0], 0]])


def exp_se3(xi):
    """xi = (v, w) — thứ tự như q = (t, theta u) của bài viết. Trả về ma trận 4x4."""
    v, w = xi[:3], xi[3:]
    th = np.linalg.norm(w)
    R = rodrigues(w)
    if th < 1e-12:
        V = np.eye(3)
    else:
        W = hat(w)
        V = np.eye(3) + (1 - np.cos(th)) / th**2 * W + (th - np.sin(th)) / th**3 * W @ W
    T = np.eye(4); T[:3, :3] = R; T[:3, 3] = V @ v
    return T


def jac_eq11(X, R, t):
    Xc = (R @ X.T).T + t
    x, y, Z = Xc[:, 0] / Xc[:, 2], Xc[:, 1] / Xc[:, 2], Xc[:, 2]
    J = np.zeros((2 * len(X), 6))
    J[0::2] = np.c_[-1/Z, 0*Z, x/Z, x*y, -(1 + x**2), y]
    J[1::2] = np.c_[0*Z, -1/Z, y/Z, 1 + y**2, -x*y, -x]
    return J, np.c_[x, y]


def gn_pose(X, x, R0, t0, update="visp", iters=30, tukey=False, centered_mad=False):
    """update='literal': cTw <- exp(dq) cTw (đọc chữ theo 'exp^{dq} q', tr. 5)
       update='visp'   : cTw <- exp(dq)^-1 cTw (quy ước ViSP / visual servoing: dq là vận tốc camera)"""
    T = np.eye(4); T[:3, :3] = R0; T[:3, 3] = t0
    w = np.ones(len(X))
    for _ in range(iters):
        with np.errstate(all="ignore"):
            J, xp = jac_eq11(X, T[:3, :3], T[:3, 3])
        e = (xp - x).ravel()
        if not (np.all(np.isfinite(J)) and np.all(np.isfinite(e))) or np.abs(T).max() > 1e8:
            T[:] = np.nan                           # phân kỳ
            break                                   # e(q) = x(q) - x, eq. (7)
        if tukey:
            r = np.linalg.norm((xp - x), axis=1)
            # thang: 1.4826 * median|r| (giả định phần dư inlier quanh 0). centered_mad=True dùng MAD quanh
            # trung vị — khi pose khởi tạo lệch, mọi phần dư cùng lớn, MAD nhỏ -> mọi trọng số = 0, kẹt.
            med_r = np.median(r) if centered_mad else 0.0
            sig = 1.4826 * np.median(np.abs(r - med_r)) + 1e-12
            c = 4.6851 * sig
            w = np.where(r < c, (1 - (r / c) ** 2) ** 2, 0.0)
        Wd = np.repeat(w, 2)
        dq = -np.linalg.pinv(Wd[:, None] * J) @ (Wd * e)   # eq. (13); W = I -> eq. (10)
        E = exp_se3(dq)
        T = (E if update == "literal" else np.linalg.inv(E)) @ T
        if np.linalg.norm(dq) < 1e-12:
            break
    return T[:3, :3], T[:3, 3], w


def cv_pnp(X, u, flag):
    ok, rv, tv = cv2.solvePnP(X, u, K, None, flags=flag)
    return cv2.Rodrigues(rv)[0], tv.ravel()


def med(a):
    return float(np.median(a))


# ================================================================================
def check_dlt_min_points():
    print("\n[1] DLT eq.(4)-(5): số điểm tối thiểu, suy biến phẳng, thang của h (không nhiễu)")
    rng = np.random.default_rng(1)
    for n in (4, 5, 6, 7):
        errs, nulls = [], []
        for _ in range(50):
            X, u, _, R, t = make_scene(n, rng)
            Rh, th, S = dlt_pose(X, to_norm(u))
            errs.append(rot_err_deg(Rh, R)); nulls.append(int(np.sum(S < 1e-9 * S[0])) + (12 - len(S)))
        print(f"    n={n}: số chiều nhân (null space) của A = {sorted(set(nulls))}, "
              f"sai số quay trung vị = {med(errs):.3g} deg")
        if n == 5:
            verdict("DLT với n=5 KHÔNG xác định pose (nhân >= 2 chiều)", med(errs) > 1 and min(nulls) >= 2)
        if n == 6:
            verdict("DLT với n=6 điểm tổng quát, không nhiễu, cho pose đúng", med(errs) < 1e-6)
    # phẳng
    X, u, _, R, t = make_scene(20, rng, planar=True)
    Rh, th, S = dlt_pose(X, to_norm(u))
    k = int(np.sum(S < 1e-9 * S[0]))
    print(f"    20 điểm đồng phẳng: nhân của A có {k} chiều, sai số quay = {rot_err_deg(Rh, R):.3g} deg")
    verdict("DLT suy biến với điểm đồng phẳng (nhân 4 chiều) — bài không cảnh báo ở §3.1.2", k == 4)
    # literal: chỉ trực chuẩn hoá R, không khử thang của t
    X, u, _, R, t = make_scene(10, rng)
    Rl, tl, _ = dlt_pose(X, to_norm(u), literal=True)
    Rc, tc, _ = dlt_pose(X, to_norm(u))
    print(f"    đọc chữ (chỉ trực chuẩn hoá R): rot err {rot_err_deg(Rl, R):.3g} deg, "
          f"trans err rel {trans_err_rel(tl, t):.3g};  thêm khử thang+dấu: rot {rot_err_deg(Rc, R):.2g}, "
          f"trans {trans_err_rel(tc, t):.2g}")
    verdict("Công thức DLT đúng nếu thêm bước khử thang/dấu (bài không nêu)", trans_err_rel(tc, t) < 1e-8)
    verdict("Đọc chữ (chỉ trực chuẩn hoá R) KHÔNG cho t đúng", trans_err_rel(tl, t) > 0.1)


def check_jacobian_and_update():
    print("\n[2] Jacobian eq.(11) và chiều cập nhật 'exp^{dq} q'")
    rng = np.random.default_rng(2)
    X, u, _, R, t = make_scene(8, rng)
    J, xp = jac_eq11(X, R, t)
    T = np.eye(4); T[:3, :3] = R; T[:3, 3] = t
    for name, side in (("cTw <- exp(xi) cTw", 1), ("cTw <- exp(xi)^-1 cTw", -1)):
        Jn = np.zeros_like(J)
        for k in range(6):
            d = np.zeros(6); d[k] = 1e-6
            E = exp_se3(d) if side == 1 else np.linalg.inv(exp_se3(d))
            T2 = E @ T
            Xc = (T2[:3, :3] @ X.T).T + T2[:3, 3]
            Jn[:, k] = ((Xc[:, :2] / Xc[:, 2:3]) - xp).ravel() / 1e-6
        rel = np.linalg.norm(Jn - J) / np.linalg.norm(J)
        print(f"    J số (sai phân) với nhiễu loạn {name}: ||J_num - J_eq11||/||J|| = {rel:.2e}")
        if side == -1:
            verdict("J eq.(11) là đạo hàm theo dịch chuyển camera: cTw <- exp(xi)^-1 cTw", rel < 1e-4)
    # hội tụ của hai cách đọc cập nhật, khởi tạo lệch nhỏ quanh nghiệm đúng
    conv = {"literal": 0, "visp": 0}
    for trial in range(50):
        X, u, _, R, t = make_scene(10, rng, sigma_px=0.0)
        R0 = rodrigues(rng.normal(scale=0.05, size=3)) @ R; t0 = t + rng.normal(scale=0.05, size=3)
        for up in conv:
            Rh, th, _ = gn_pose(X, to_norm(u), R0, t0, update=up)
            conv[up] += rot_err_deg(Rh, R) < 1e-4  # sàn số của arccos ~1e-6 deg
    print(f"    hội tụ về nghiệm đúng (50 lần, lệch ~3 deg / 5 cm): literal {conv['literal']}/50, visp {conv['visp']}/50")
    verdict("Đọc chữ 'exp^{dq} q' (nhân trái exp(dq)) PHÂN KỲ; phải dùng exp(dq)^-1", conv["literal"] == 0 and conv["visp"] == 50)


NTRIAL = 200


def check_accuracy_vs_noise():
    print(f"\n[3] Sai số vs nhiễu ({NTRIAL} cảnh/ô, trung vị; GN = eq.(10)-(11) thuần, không damping, 30 vòng)")
    print("    cột: sai số quay [deg] / sai số tịnh tiến tương đối [%]; 'phân kỳ' = GN cho NaN hoặc |T| > 1e8")
    rng = np.random.default_rng(3)
    methods = ("DLT", "DLT+GN", "EPnP", "EPnP+GN", "ITER")
    table, div = {}, {}
    agree, better = [], []
    for n in (6, 10, 50):
        for s in (0.5, 1.0, 2.0, 5.0):
            acc = {m: ([], [], []) for m in methods}
            ndiv = 0; nsame = 0
            for _ in range(NTRIAL):
                X, u, _, R, t = make_scene(n, rng, sigma_px=s)
                x = to_norm(u)
                Rd, td, _ = dlt_pose(X, x)
                Rg, tg, _ = gn_pose(X, x, Rd, td)
                ndiv += not np.all(np.isfinite(Rg))
                Re, te = cv_pnp(X, u, cv2.SOLVEPNP_EPNP)
                Reg, teg, _ = gn_pose(X, x, Re, te)
                Ri, ti = cv_pnp(X, u, cv2.SOLVEPNP_ITERATIVE)
                for m, (Rm, tm) in zip(methods, ((Rd, td), (Rg, tg), (Re, te), (Reg, teg), (Ri, ti))):
                    if not np.all(np.isfinite(Rm)):
                        acc[m][0].append(180.0); acc[m][1].append(np.inf); acc[m][2].append(np.inf); continue
                    acc[m][0].append(rot_err_deg(Rm, R)); acc[m][1].append(trans_err_rel(tm, t))
                    Xc = (Rm @ X.T).T + tm; p = (K @ Xc.T).T; p = p[:, :2] / p[:, 2:3]
                    acc[m][2].append(np.sqrt(np.mean(np.sum((p - u) ** 2, 1))))
                a_, b_ = acc["EPnP+GN"][2][-1], acc["ITER"][2][-1]
                nsame += abs(a_ - b_) <= 1e-6 * b_
                agree.append(abs(a_ - b_) <= 1e-6 * b_)
                better.append(a_ < b_ * (1 - 1e-6))
            table[(n, s)] = {m: (med(a[0]), med(a[1]), med(a[2])) for m, a in acc.items()}
            div[(n, s)] = ndiv
            row = " ".join(f"{m}:{v[0]:6.3f}/{100*v[1]:6.2f}" for m, v in table[(n, s)].items())
            print(f"    n={n:2d} s={s:3.1f}px | {row} | DLT+GN phân kỳ {ndiv}/{NTRIAL}")
    worse = sum(table[k]["DLT"][0] > table[k]["EPnP+GN"][0] for k in table)
    verdict(f"DLT kém hơn tinh chỉnh phi tuyến (EPnP+GN) ở {worse}/{len(table)} ô", worse == len(table))
    ratio = [table[k]["DLT"][0] / table[k]["EPnP+GN"][0] for k in table]
    print(f"    tỉ số sai số quay trung vị DLT / EPnP+GN: min {min(ratio):.2f}, max {max(ratio):.2f}")
    ok = [k for k in table if div[k] == 0]
    fa, fb = np.mean(agree), np.mean(better)
    verdict("EPnP+GN và cv2 ITERATIVE về cùng cực tiểu ở >= 90% số cảnh (RMSE tái chiếu trùng tới 1e-6)", fa >= 0.9,
            f"trùng {fa:.1%}, EPnP+GN thấp hơn hẳn {fb:.1%}")
    tot = sum(div.values())
    verdict("GN thuần khởi tạo bằng DLT có lúc phân kỳ (bài: 'cần khởi tạo tốt')", tot > 0,
            f"tổng {tot}/{NTRIAL*len(div)} lần; ô không phân kỳ: {len(ok)}/{len(div)}")
    return table


def check_ransac_numbers():
    print("\n[4] Số vòng RANSAC N = log(1-p)/log(1-(1-eta)^n), p=0.99, n=4 (tr. 5-6)")
    for eta, claim in ((0.1, 5), (0.5, 72)):
        N = np.log(1 - 0.99) / np.log(1 - (1 - eta) ** 4)
        print(f"    eta={eta}: N = {N:.2f} -> ceil {int(np.ceil(N))} (bài ghi {claim})")
        verdict(f"N(eta={eta}) = {claim}", int(np.ceil(N)) == claim)
    N6 = np.log(0.01) / np.log(1 - 0.5 ** 6)
    print(f"    (ghi chú) nếu bộ giải mẫu là DLT (cần 6 điểm) thì với eta=0.5: N = {int(np.ceil(N6))}")


def ransac(X, x, u, frac, rng, solver):
    """RANSAC theo 4 bước ở tr. 5; solver: 'dlt6' (DLT trên mẫu 6 điểm) hoặc 'p3p' (cv2.solveP3P, mẫu 3 điểm,
    thử mọi nghiệm). Ngưỡng 3 px. Số vòng theo công thức của bài với p = 0.99, tối thiểu 20."""
    n = len(X); m = 6 if solver == "dlt6" else 3
    Nit = max(20, int(np.ceil(np.log(0.01) / np.log(1 - (1 - frac) ** m))))
    best = np.zeros(n, bool)
    for _ in range(Nit):
        s = rng.choice(n, m, replace=False)
        if solver == "dlt6":
            hyps = [dlt_pose(X[s], x[s])[:2]]
        else:
            _, rvs, tvs = cv2.solveP3P(X[s], u[s], K, None, cv2.SOLVEPNP_P3P)
            hyps = [(cv2.Rodrigues(rv)[0], tv.ravel()) for rv, tv in zip(rvs, tvs)]
        for Rs, ts in hyps:
            Xc = (Rs @ X.T).T + ts
            with np.errstate(all="ignore"):
                r = np.linalg.norm(Xc[:, :2] / Xc[:, 2:3] - x, axis=1) * K[0, 0]
            inl = (r < 3.0) & (Xc[:, 2] > 0)
            if inl.sum() > best.sum():
                best = inl
    if best.sum() < 6:
        return np.full((3, 3), np.nan), None, best
    Rr, tr_, _ = dlt_pose(X[best], x[best])      # "một PnP chính xác hơn trên toàn bộ inlier"
    Rr, tr_, _ = gn_pose(X[best], x[best], Rr, tr_)
    return Rr, tr_, best


def check_robust():
    print("\n[5] Ngoại lai (n=60, nhiễu 1 px, ngoại lai = pixel ngẫu nhiên đều trên ảnh; 100 cảnh/ô; sai số quay [deg])")
    print("    GN: eq.(10) khởi tạo DLT trên mọi điểm | IRLS-DLT: eq.(13) Tukey, khởi tạo DLT trên mọi điểm |")
    print("    IRLS-track: eq.(13) khởi tạo = pose đúng lệch ~3 deg/5 cm (giống tracking theo khung trước) |")
    print("    IRLS-track-MADc: như trên nhưng thang Tukey = MAD quanh trung vị (không quanh 0)")
    print("    RANSAC-DLT6 / RANSAC-P3P: RANSAC rồi DLT+GN trên inlier; 180 = thất bại (consensus < 6 hoặc GN phân kỳ)")
    rng = np.random.default_rng(5)
    out = {}
    for frac in (0.1, 0.3, 0.5):
        keys = ("GN", "IRLS-DLT", "IRLS-track", "IRLS-track-MADc", "RANSAC-DLT6", "RANSAC-P3P")
        res = {k: [] for k in keys}
        for _ in range(100):
            n = 60
            X, u, _, R, t = make_scene(n, rng, sigma_px=1.0)
            mo = int(frac * n)
            idx = rng.choice(n, mo, replace=False)
            u = u.copy(); u[idx] = np.c_[rng.uniform(0, 640, mo), rng.uniform(0, 480, mo)]
            x = to_norm(u)
            Rd, td, _ = dlt_pose(X, x)
            Rg, _, _ = gn_pose(X, x, Rd, td)
            Rw, _, _ = gn_pose(X, x, Rd, td, tukey=True, iters=50)
            R0 = rodrigues(rng.normal(scale=0.03, size=3)) @ R; t0 = t + rng.normal(scale=0.03, size=3)
            Rt, _, _ = gn_pose(X, x, R0, t0, tukey=True, iters=50)
            Rtc, _, _ = gn_pose(X, x, R0, t0, tukey=True, iters=50, centered_mad=True)
            Rr, _, _ = ransac(X, x, u, frac, rng, "dlt6")
            Rp, _, _ = ransac(X, x, u, frac, rng, "p3p")
            for k, Rm in zip(keys, (Rg, Rw, Rt, Rtc, Rr, Rp)):
                res[k].append(rot_err_deg(Rm, R) if np.all(np.isfinite(Rm)) else 180.0)
        out[frac] = res
        print(f"    ngoại lai {frac:.0%}:")
        for k, v in res.items():
            print(f"      {k:16s} trung vị {med(v):8.3f} deg, tỉ lệ > 1 deg: {np.mean(np.array(v) > 1):4.0%}")
    verdict("GN bình phương thường hỏng với 10% ngoại lai (trung vị > 1 deg)", med(out[0.1]["GN"]) > 1)
    verdict("IRLS-Tukey khởi tạo tốt (tracking) khử được 30% ngoại lai (trung vị < 0.2 deg)",
            med(out[0.3]["IRLS-track"]) < 0.2)
    verdict("Chọn thang Tukey = MAD quanh trung vị làm IRLS kẹt thường xuyên hơn (tỉ lệ >1deg ở 10% cao hơn)",
            np.mean(np.array(out[0.1]["IRLS-track-MADc"]) > 1) > np.mean(np.array(out[0.1]["IRLS-track"]) > 1))
    verdict("IRLS-Tukey khởi tạo bằng DLT trên dữ liệu bẩn hỏng ngay ở 10% (trung vị > 1 deg)",
            med(out[0.1]["IRLS-DLT"]) > 1)
    verdict("RANSAC-P3P + GN đúng ở 50% ngoại lai (trung vị < 0.2 deg)", med(out[0.5]["RANSAC-P3P"]) < 0.2)
    verdict("RANSAC dùng DLT mẫu 6 điểm kém hơn RANSAC-P3P ở 50% (tỉ lệ >1deg cao hơn)",
            np.mean(np.array(out[0.5]["RANSAC-DLT6"]) > 1) > np.mean(np.array(out[0.5]["RANSAC-P3P"]) > 1))
    # vì sao DLT-6 là bộ sinh giả thuyết tệ: 6 điểm inlier, nhiễu 1 px -> sai số tái chiếu trên chính 6 điểm mẫu
    r6 = []
    for _ in range(200):
        X, u, _, R, t = make_scene(6, rng, sigma_px=1.0)
        Rs, ts, _ = dlt_pose(X, to_norm(u))
        Xc = (Rs @ X.T).T + ts
        r6.append(np.max(np.linalg.norm(Xc[:, :2] / Xc[:, 2:3] - to_norm(u), axis=1)) * K[0, 0])
    print(f"    DLT trên đúng 6 inlier (nhiễu 1 px): sai số tái chiếu lớn nhất trên chính 6 điểm, trung vị {med(r6):.1f} px"
          f" (sau khi trực chuẩn hoá R)")


def plane_frame(X):
    c = X.mean(0)
    _, _, Vt = np.linalg.svd(X - c)
    Rp = Vt if np.linalg.det(Vt) > 0 else np.diag([1, 1, -1]) @ Vt
    return Rp, c


def homog_dlt(P, x):
    rows = []
    for (X, Y), (x2, y2) in zip(P, x):
        x1 = np.array([X, Y, 1.0]); z = np.zeros(3)
        rows += [np.r_[z, -x1, y2 * x1], np.r_[x1, z, -x2 * x1], np.r_[-y2 * x1, x2 * x1, z]]  # eq. (23)
    _, _, Vt = np.linalg.svd(np.array(rows))
    return Vt[-1].reshape(3, 3)


def pose_from_H(H, normalize=True):
    Hn = H.copy()
    if normalize:  # bước bài viết không nêu: thang ||c1|| = 1, dấu để tz > 0
        Hn = H / np.linalg.norm(H[:, 0]); Hn *= np.sign(Hn[2, 2])
    c1, c2, tt = Hn[:, 0], Hn[:, 1], Hn[:, 2]
    Rm = np.c_[c1, c2, np.cross(c1, c2)]      # c3 = c1 x c2 (tr. 10)
    return Rm, tt


def check_planar():
    print("\n[6] Target phẳng: DLT homography eq.(23) -> pose eq.(26)-(27), 200 cảnh/ô, n=20")
    rng = np.random.default_rng(6)
    for s in (0.0, 1.0, 3.0):
        ortho, eH, eHn, eGN, eHg, eIPPE = [], [], [], [], [], []
        for _ in range(200):
            X, u, _, R, t = make_scene(20, rng, planar=True, sigma_px=s)
            Rp, c = plane_frame(X)
            P = ((X - c) @ Rp.T)[:, :2]            # toạ độ trên mặt phẳng wZ = 0
            R2, t2 = R @ Rp.T, R @ c + t           # pose đúng trong hệ mặt phẳng
            x = to_norm(u)
            H = homog_dlt(P, x)
            Rm, tm = pose_from_H(H)
            ortho.append(np.linalg.norm(Rm.T @ Rm - np.eye(3)))
            Rq = proj_to_so3(Rm)
            eHn.append(rot_err_deg(Rq, R2))
            Rl, tl = pose_from_H(H, normalize=False)
            eH.append(trans_err_rel(tl, t2))
            P3 = np.c_[P, np.zeros(len(P))]
            Rg, tg, _ = gn_pose(P3, x, Rq, tm)
            eGN.append(rot_err_deg(Rg, R2))
            # eq. (24): cực tiểu sai số hình học trên H (8 tham số, h33 = 1)
            def res(hv):
                Hh = np.r_[hv, 1.0].reshape(3, 3); q = (Hh @ np.c_[P, np.ones(len(P))].T).T
                return (q[:, :2] / q[:, 2:3] - x).ravel()
            hg = least_squares(res, (H / H[2, 2]).ravel()[:8], method="lm").x
            Rhg, thg = pose_from_H(np.r_[hg, 1.0].reshape(3, 3))
            eHg.append(rot_err_deg(proj_to_so3(Rhg), R2))
            Ri, ti = cv_pnp(P3, u, cv2.SOLVEPNP_IPPE)
            eIPPE.append(rot_err_deg(Ri, R2))
        print(f"    sigma={s}px: ||R^T R - I|| trung vị {med(ortho):.2e}; đọc chữ (không chuẩn thang) trans err {med(eH):.2f};"
              f" rot err: H-DLT {med(eHn):.3f}, H-hình học eq.(24) {med(eHg):.3f}, H-DLT+GN(pose) {med(eGN):.3f},"
              f" cv2 IPPE {med(eIPPE):.3f} deg")
        if s == 0.0:
            verdict("Pose từ H đúng khi không nhiễu (sau khi chuẩn thang)", med(eHn) < 1e-6)
        if s == 1.0:
            verdict("c3 = c1 x c2 KHÔNG cho R trực giao khi có nhiễu (||R^T R - I|| > 1e-3)", med(ortho) > 1e-3)
            verdict("Pose từ H-DLT kém hơn pose tinh chỉnh GN (eq.6) ở sigma=1px", med(eHn) > med(eGN))


if __name__ == "__main__":
    t0 = time.time()
    for f in (check_dlt_min_points, check_jacobian_and_update, check_accuracy_vs_noise, check_ransac_numbers,
              check_robust, check_planar):
        t1 = time.time(); f(); print(f"    ({time.time() - t1:.1f}s)")
    print(f"\nTổng: {sum(ok for _, ok in RESULTS)}/{len(RESULTS)} PASS, thời gian {time.time() - t0:.1f}s")
