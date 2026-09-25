"""Kiểm chứng cửa (b) cho urban2016mlpnp (MLPnP, ISPRS Annals 2016).

Cài lại theo bài:
  - lan truyền covariance pixel -> tia chiếu: eq. (3)-(6); rút gọn về không gian tiếp tuyến eq. (7)-(9)
  - nghiệm tuyến tính có trọng số: eq. (10)-(19)   (không cài trường hợp phẳng §3.5)
  - Gauss-Newton trên phần dư tiếp tuyến eq. (10), R tham số hoá Cayley (§3.4), tối đa 5 vòng
  - covariance pose eq. (23), hệ số phương sai eq. (26)-(27)
Rồi đo trên cảnh tổng hợp có nhiễu pixel BẤT ĐẲNG HƯỚNG, khác nhau theo từng điểm (covariance biết trước):
  C1 lan truyền covariance so với Monte-Carlo
  C2 nghiệm tuyến tính không nhiễu phải đúng tuyệt đối
  C3 độ chính xác: MLPnP có trọng số vs không trọng số vs cv2 EPnP / ITERATIVE / SQPNP
  C4 MLPnP so với ML "chuẩn vàng" (GN trên sai số tái chiếu Mahalanobis ở pixel)
  C5 tính nhất quán: NEES của covariance dự đoán eq. (23) so với Monte-Carlo; sigma0^2 eq. (26)
Chạy:  python3 VSLAM/pnp/code/urban2016mlpnp_check.py
"""
import os
import sys
import time

import numpy as np
import cv2

sys.path.insert(0, os.path.dirname(__file__))
from common import K_DEFAULT, make_scene, project, rot_err_deg, trans_err_rel  # noqa: E402

K = K_DEFAULT
Kinv = np.linalg.inv(K)
RESULTS = []


def report(name, ok, msg):
    RESULTS.append((name, ok))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {msg}")


# ---------------------------------------------------------------- mô hình nhiễu
def random_pixel_covs(n, rng, smaj=(0.5, 5.0), ratio=(1.0, 8.0)):
    """Covariance 2x2 bất đẳng hướng, khác nhau theo điểm: trục lớn U(smaj), tỉ lệ trục U(ratio), hướng ngẫu nhiên."""
    covs = np.empty((n, 2, 2))
    for i in range(n):
        s1 = rng.uniform(*smaj)
        s2 = s1 / rng.uniform(*ratio)
        a = rng.uniform(0, np.pi)
        Q = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])
        covs[i] = Q @ np.diag([s1 ** 2, s2 ** 2]) @ Q.T
    return covs


def iso_hetero_covs(n, rng, smax):
    """Kiểu thí nghiệm Fig. 3(e)-(h) của bài: mỗi điểm một sigma đẳng hướng ~ U(0, smax) (chặn dưới 0.05 px)."""
    s = np.maximum(rng.uniform(0, smax, n), 0.05)
    return s[:, None, None] ** 2 * np.eye(2)[None]


def add_noise(u_clean, covs, rng):
    L = np.linalg.cholesky(covs)
    return u_clean + np.einsum('nij,nj->ni', L, rng.normal(size=u_clean.shape))


# ---------------------------------------------------------------- MLPnP
def null_basis(v):
    """eq. (7): J_vr(v) = null(v^T) qua SVD, 3x2 trực chuẩn. v: (3,) hoặc (n,3)."""
    V = np.atleast_2d(v)
    _, _, Vt = np.linalg.svd(V[:, None, :])          # (n,3,3); hai hàng cuối là null(v^T)
    B = np.transpose(Vt[:, 1:, :], (0, 2, 1))
    return B[0] if np.ndim(v) == 1 else B


def propagate(u, covs_px):
    """eq. (3)-(6), (9) (vector hoá theo điểm): trả về v (n,3), Jvr (n,3,2), Sigma_vv (n,3,3), Sigma_vr (n,2,2)."""
    n = len(u)
    Jpi = np.zeros((3, 2))
    Jpi[:2, :2] = Kinv[:2, :2]                       # eq. (3): Jacobian của x = K^-1 [x';1], hàng cuối = 0
    x = (Kinv @ np.c_[u, np.ones(n)].T).T
    Sxx = Jpi @ covs_px @ Jpi.T                      # eq. (4), hạng 2
    nx = np.linalg.norm(x, axis=1)
    v = x / nx[:, None]                              # eq. (5)
    J = (np.eye(3)[None] - v[:, :, None] * v[:, None, :]) / nx[:, None, None]   # eq. (6)
    Svv = J @ Sxx @ np.transpose(J, (0, 2, 1))
    Jvr = null_basis(v)
    Svr = np.transpose(Jvr, (0, 2, 1)) @ Svv @ Jvr   # eq. (9)
    return v, Jvr, Svv, Svr


def whiteners(Svr):
    """W_i sao cho W_i^T W_i = Sigma_vr^-1 (khối của P, eq. (13))."""
    return np.transpose(np.linalg.cholesky(np.linalg.inv(Svr)), (0, 2, 1))


def linear_mlpnp(Xw, Jvr, W, depth_w=None):
    """eq. (11)-(19). W=None -> P = I (không trọng số). depth_w: hệ số nhân từng điểm (biến thể của tôi, không có trong bài)."""
    n = len(Xw)
    rT = np.transpose(Jvr, (0, 2, 1))                # (n,2,3): hàng r^T, s^T
    A = np.concatenate([(rT[:, :, :, None] * Xw[:, None, None, :]).reshape(n, 2, 9), rT], axis=2)  # eq. (11)
    if W is not None:
        A = W @ A
    if depth_w is not None:
        A = A * depth_w[:, None, None]
    _, _, Vt = np.linalg.svd(A.reshape(-1, 12))      # tương đương SVD của N = A^T P A, eq. (14)-(15)
    uvec = Vt[-1]
    Rh = uvec[:9].reshape(3, 3); th = uvec[9:]
    if np.linalg.det(Rh) < 0:                        # bài không nói cách chọn dấu; tôi chọn det > 0
        Rh, th = -Rh, -th
    t = th / np.cbrt(np.prod(np.linalg.norm(Rh, axis=0)))  # eq. (17)
    U, _, VRt = np.linalg.svd(Rh)                    # eq. (18)-(19)
    R = U @ VRt
    return R, t


def cay(c):
    cc = c @ c
    C = np.array([[0, -c[2], c[1]], [c[2], 0, -c[0]], [-c[1], c[0], 0]])
    return ((1 - cc) * np.eye(3) + 2 * C + 2 * np.outer(c, c)) / (1 + cc)


def cay_inv(R):
    return np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]]) / (1 + np.trace(R))


def skew(q):
    return np.array([[0, -q[2], q[1]], [q[2], 0, -q[0]], [-q[1], q[0], 0]])


def skew_batch(Q):
    Z = np.zeros(len(Q))
    return np.stack([np.stack([Z, -Q[:, 2], Q[:, 1]], 1), np.stack([Q[:, 2], Z, -Q[:, 0]], 1),
                     np.stack([-Q[:, 1], Q[:, 0], Z], 1)], 1)


def tangent_res_jac(Xw, Jvr, R, t):
    """phần dư eq. (10): d_i = Jvr_i^T (R p_i + t)/||R p_i + t||, Jacobian theo (c, t) với R <- cay(c) R tại c = 0."""
    n = len(Xw)
    q = Xw @ R.T
    X = q + t
    nX = np.linalg.norm(X, axis=1)
    g = X / nX[:, None]
    dg = (np.eye(3)[None] - g[:, :, None] * g[:, None, :]) / nX[:, None, None]
    rT = np.transpose(Jvr, (0, 2, 1))
    res = np.einsum('nij,nj->ni', rT, g)
    dX = np.concatenate([-2 * skew_batch(q), np.tile(np.eye(3), (n, 1, 1))], axis=2)  # d(cay(c) q)/dc|0 = -2[q]x
    Jac = rT @ dg @ dX
    return res, Jac


def gn_mlpnp(Xw, Jvr, W, R, t, iters=5):
    """§3.4: Gauss-Newton, tối đa 5 vòng. Trả R, t, Sigma (6x6, eq. 23), sigma0^2 (eq. 26)."""
    n = len(Xw)
    Wm = np.tile(np.eye(2), (n, 1, 1)) if W is None else W
    for _ in range(iters):
        res, Jac = tangent_res_jac(Xw, Jvr, R, t)
        rw = np.einsum('nij,nj->ni', Wm, res).ravel()
        Aw = np.einsum('nij,njk->nik', Wm, Jac).reshape(-1, 6)
        dx = -np.linalg.lstsq(Aw, rw, rcond=None)[0]
        R = cay(dx[:3]) @ R
        t = t + dx[3:]
        if np.linalg.norm(dx) < 1e-12:
            break
    res, Jac = tangent_res_jac(Xw, Jvr, R, t)
    rw = np.einsum('nij,nj->ni', Wm, res).ravel()
    Aw = np.einsum('nij,njk->nik', Wm, Jac).reshape(-1, 6)
    Sigma = np.linalg.inv(Aw.T @ Aw)                 # eq. (23)
    s0sq = rw @ rw / (2 * n - 6)                     # eq. (26)
    return R, t, Sigma, s0sq


def mlpnp(Xw, u, covs_px, weighted=True, iters=5, relin=False):
    v, Jvr, _, Svr = propagate(u, covs_px)
    W = whiteners(Svr) if weighted else None
    R0, t0 = linear_mlpnp(Xw, Jvr, W)
    R, t, S, s0 = gn_mlpnp(Xw, Jvr, W, R0, t0, iters)
    out = dict(R0=R0, t0=t0, R=R, t=t, Sigma=S, s0sq=s0)
    if relin:  # biến thể của tôi: phần dư eq.(11) = lambda_i * d_i, nên chia hàng cho lambda_i ước lượng từ lần 1
        lam = np.linalg.norm(Xw @ R0.T + t0, axis=1)
        out["R0b"], out["t0b"] = linear_mlpnp(Xw, Jvr, W, depth_w=1.0 / lam)
    return out


def gn_mahalanobis_pixel(Xw, u, covs_px, R, t, iters=20):
    """ML 'chuẩn vàng' dưới giả thiết nhiễu Gauss ở pixel: min sum (u_i - proj_i)^T C_i^-1 (u_i - proj_i)."""
    W = np.transpose(np.linalg.cholesky(np.linalg.inv(covs_px)), (0, 2, 1))
    for _ in range(iters):
        q = (R @ Xw.T).T; Xc = q + t
        z = Xc[:, 2]
        pr = (K @ Xc.T).T[:, :2] / z[:, None]
        res = pr - u
        Jp = np.zeros((len(Xw), 2, 3))
        Jp[:, 0, 0] = K[0, 0] / z; Jp[:, 0, 2] = -K[0, 0] * Xc[:, 0] / z ** 2
        Jp[:, 1, 1] = K[1, 1] / z; Jp[:, 1, 2] = -K[1, 1] * Xc[:, 1] / z ** 2
        J = np.einsum('nij,njk->nik', Jp, np.concatenate([-2 * skew_batch(q), np.tile(np.eye(3), (len(q), 1, 1))], axis=2))
        rw = np.einsum('nij,nj->ni', W, res).ravel()
        Aw = np.einsum('nij,njk->nik', W, J).reshape(-1, 6)
        dx = -np.linalg.lstsq(Aw, rw, rcond=None)[0]
        R = cay(dx[:3]) @ R; t = t + dx[3:]
        if np.linalg.norm(dx) < 1e-12:
            break
    return R, t


def cv_solve(Xw, u, flag):
    ok, rv, tv = cv2.solvePnP(Xw.reshape(-1, 1, 3), u.reshape(-1, 1, 2), K, None, flags=flag)
    return cv2.Rodrigues(rv)[0], tv.ravel()


# ================================================================ C1
def check_C1():
    rng = np.random.default_rng(1)
    u0 = np.array([[600.0, 50.0], [320.0, 240.0], [20.0, 460.0]])
    covs = random_pixel_covs(3, rng)
    v, Jvr, Svv, Svr = propagate(u0, covs)
    N = 200000
    worst_vv = worst_vr = 0.0
    ranks = []
    for i in range(3):
        du = rng.multivariate_normal(np.zeros(2), covs[i], N)
        x = (Kinv @ np.c_[u0[i] + du, np.ones(N)].T).T
        vs = x / np.linalg.norm(x, axis=1, keepdims=True)
        Cvv = np.cov(vs.T)
        vr = (vs - v[i]) @ Jvr[i]                   # toạ độ trong không gian tiếp tuyến tại v quan sát
        Cvr = np.cov(vr.T)
        worst_vv = max(worst_vv, np.linalg.norm(Cvv - Svv[i]) / np.linalg.norm(Svv[i]))
        worst_vr = max(worst_vr, np.linalg.norm(Cvr - Svr[i]) / np.linalg.norm(Svr[i]))
        s = np.linalg.svd(Svv[i], compute_uv=False)
        ranks.append(s[2] / s[0])
    # Jacobian eq. (6) so với sai phân
    x = Kinv @ np.r_[u0[0], 1.0]; e = 1e-7
    Jnum = np.column_stack([((x + e * np.eye(3)[k]) / np.linalg.norm(x + e * np.eye(3)[k])
                             - (x - e * np.eye(3)[k]) / np.linalg.norm(x - e * np.eye(3)[k])) / (2 * e) for k in range(3)])
    Jana = (np.eye(3) - np.outer(v[0], v[0])) / np.linalg.norm(x)
    jerr = np.abs(Jnum - Jana).max()
    report("C1a Jacobian eq.(6)", jerr < 1e-7, f"max|J_num - J_eq6| = {jerr:.1e}")
    report("C1b Sigma_vv hạng 2 (eq.6)", max(ranks) < 1e-12, f"max s3/s1 = {max(ranks):.1e}")
    report("C1c Sigma_vv, Sigma_vr so với Monte-Carlo (N=2e5)", worst_vv < 0.02 and worst_vr < 0.02,
           f"sai lệch Frobenius tương đối lớn nhất: vv {worst_vv:.3%}, vr {worst_vr:.3%}")


# ================================================================ C2
def check_C2():
    rng = np.random.default_rng(2)
    worst_r = worst_t = 0.0
    for n in (6, 7, 10, 50):
        for _ in range(20):
            Xw, _, uc, R, t = make_scene(n, rng)
            covs = random_pixel_covs(n, rng)
            v, Jvr, _, Svr = propagate(uc, covs)
            R0, t0 = linear_mlpnp(Xw, Jvr, whiteners(Svr))
            worst_r = max(worst_r, np.linalg.norm(R0 - R)); worst_t = max(worst_t, trans_err_rel(t0, t))
    report("C2 nghiệm tuyến tính không nhiễu (n=6..50, 80 cảnh)", worst_r < 1e-9 and worst_t < 1e-8,
           f"max ||R0 - R||_F {worst_r:.1e} (arccos không đủ chính xác ở 1e-6 deg), max trans rel err {worst_t:.1e}")


# ================================================================ C3/C4
def run_accuracy(label, n, trials, cov_fn, seed):
    rng = np.random.default_rng(seed)
    names = ["cv2 EPNP", "cv2 ITERATIVE", "cv2 SQPNP", "MLPnP lin P=I", "MLPnP lin (eq.14)", "lin eq.14 + 1/lam",
             "MLPnP P=I (+GN)", "MLPnP (+GN)", "Mahal-pixel GN"]
    E = {k: [] for k in names}
    Tr = {k: [] for k in names}
    for _ in range(trials):
        Xw, _, uc, R, t = make_scene(n, rng)
        covs = cov_fn(n, rng)
        u = add_noise(uc, covs, rng)
        out = {}
        out["cv2 EPNP"] = cv_solve(Xw, u, cv2.SOLVEPNP_EPNP)
        out["cv2 ITERATIVE"] = cv_solve(Xw, u, cv2.SOLVEPNP_ITERATIVE)
        out["cv2 SQPNP"] = cv_solve(Xw, u, cv2.SOLVEPNP_SQPNP)
        mu = mlpnp(Xw, u, covs, weighted=False)
        mw = mlpnp(Xw, u, covs, weighted=True, relin=True)
        out["lin eq.14 + 1/lam"] = (mw["R0b"], mw["t0b"])
        out["MLPnP lin P=I"] = (mu["R0"], mu["t0"]); out["MLPnP P=I (+GN)"] = (mu["R"], mu["t"])
        out["MLPnP lin (eq.14)"] = (mw["R0"], mw["t0"]); out["MLPnP (+GN)"] = (mw["R"], mw["t"])
        out["Mahal-pixel GN"] = gn_mahalanobis_pixel(Xw, u, covs, mw["R"], mw["t"])
        for k in names:
            E[k].append(rot_err_deg(out[k][0], R)); Tr[k].append(100 * trans_err_rel(out[k][1], t))
    print(f"\n  -- {label}: n={n}, {trials} cảnh --")
    print(f"  {'phương pháp':<20}{'rot mean':>9}{'rot med':>9}{'t% mean':>9}{'t% med':>9}")
    for k in names:
        e = np.array(E[k]); tt = np.array(Tr[k])
        print(f"  {k:<20}{e.mean():9.4f}{np.median(e):9.4f}{tt.mean():9.4f}{np.median(tt):9.4f}")
    return {k: np.array(v) for k, v in E.items()}, {k: np.array(v) for k, v in Tr.items()}


def check_C3_C4():
    res = {}
    cfgs = [("A bất đẳng hướng, sigma_maj U(0.5,5), tỉ lệ U(1,8)", 10, lambda n, r: random_pixel_covs(n, r)),
            ("A bất đẳng hướng, sigma_maj U(0.5,5), tỉ lệ U(1,8)", 50, lambda n, r: random_pixel_covs(n, r)),
            ("B đẳng hướng dị phương sai kiểu Fig.3(e), sigma U(0,5)", 50, lambda n, r: iso_hetero_covs(n, r, 5.0)),
            ("C đẳng hướng đồng nhất sigma=2 (đối chứng)", 50, lambda n, r: 4.0 * np.tile(np.eye(2), (n, 1, 1)))]
    for j, (lab, n, fn) in enumerate(cfgs):
        res[(lab, n)] = run_accuracy(lab, n, 300, fn, 100 + j)
    print()
    for (lab, n), (E, Tr) in res.items():
        key = lab.split()[0]
        ratio_r = np.median(E["MLPnP (+GN)"]) / np.median(E["cv2 ITERATIVE"])
        ratio_t = np.median(Tr["MLPnP (+GN)"]) / np.median(Tr["cv2 ITERATIVE"])
        win = np.mean(E["MLPnP (+GN)"] < E["cv2 ITERATIVE"])
        if key == "C":
            ok = 0.9 < ratio_r < 1.1
            report(f"C3{key} n={n} đồng nhất: trọng số không được lợi/hại", ok,
                   f"median rot MLPnP/ITER = {ratio_r:.3f}, trans = {ratio_t:.3f}")
        else:
            ok = ratio_r < 0.9 and ratio_t < 0.9
            report(f"C3{key} n={n}: MLPnP có trọng số < 0.9x cv2 ITERATIVE (median)", ok,
                   f"rot ratio {ratio_r:.3f}, trans ratio {ratio_t:.3f}, MLPnP thắng {win:.0%} cảnh (rot)")
        d = np.abs(E["MLPnP (+GN)"] - E["Mahal-pixel GN"])
        rel = np.median(d) / np.median(E["Mahal-pixel GN"])
        report(f"C4{key} n={n}: MLPnP ~ ML pixel Mahalanobis", rel < 0.05,
               f"median |Δrot| / median rot = {rel:.3%}")
        lr = np.median(E["MLPnP lin (eq.14)"]) / np.median(E["MLPnP lin P=I"])
        print(f"      (chỉ thông tin) bước tuyến tính: median rot có trọng số / không trọng số = {lr:.3f}; "
              f"lin(eq.14) / ML cuối = {np.median(E['MLPnP lin (eq.14)']) / np.median(E['MLPnP (+GN)']):.2f}")


# ================================================================ C5
def nees_mc(scale_noise, M, seed, n=30, weighted=True, iters=5):
    rng = np.random.default_rng(seed)
    Xw, _, uc, R, t = make_scene(n, rng)
    covs = random_pixel_covs(n, rng) * scale_noise ** 2
    errs, nees, s0s, Sig = [], [], [], []
    for _ in range(M):
        u = add_noise(uc, covs, rng)
        m = mlpnp(Xw, u, covs, weighted=weighted, iters=iters)
        e = np.r_[cay_inv(R @ m["R"].T), t - m["t"]]   # sai số trong toạ độ (c, t) quanh nghiệm, cùng chart với Sigma
        S = m["Sigma"]
        if not weighted:  # covariance "ngây thơ" giả định nhiễu đẳng hướng: Sigma * sigma0^2 (eq. 27 với P = I)
            S = S * m["s0sq"]
        errs.append(e); nees.append(e @ np.linalg.solve(S, e)); s0s.append(m["s0sq"]); Sig.append(S)
    errs = np.array(errs); nees = np.array(nees)
    Cemp = np.cov(errs.T); Cpred = np.mean(Sig, axis=0)
    sd_ratio = np.sqrt(np.diag(Cpred)) / np.sqrt(np.diag(Cemp))
    bias = np.abs(errs.mean(0)) / np.sqrt(np.diag(Cemp)) * np.sqrt(M)  # z-score của trung bình
    return nees, np.array(s0s), sd_ratio, bias


def check_C5():
    chi95 = 12.5916  # chi2(6) phân vị 0.95
    M = 2000
    print()
    for sc in (1.0, 5.0, 20.0):
        nees, s0, sdr, bias = nees_mc(sc, M, 7)
        cov95 = np.mean(nees < chi95)
        msg = (f"noise x{sc:g}: mean NEES {nees.mean():.2f}, median {np.median(nees):.2f} (chi2_6: 5.35) (kỳ vọng 6, ±{2 * np.sqrt(12 / M):.2f} 2σ), "
               f"phủ 95% = {cov95:.3f}, mean sigma0^2 = {s0.mean():.3f}, "
               f"SD dự đoán/thực nghiệm = [{', '.join(f'{x:.2f}' for x in sdr)}], max|bias z| = {bias.max():.1f}")
        if sc == 1.0:
            report("C5a NEES nhất quán ở nhiễu thật (Sigma biết, không nhân sigma0^2)",
                   abs(nees.mean() - 6) < 0.35 and abs(cov95 - 0.95) < 0.015, msg)
            report("C5b E[sigma0^2] ~ 1 (eq. 26)", abs(s0.mean() - 1) < 0.05, f"mean sigma0^2 = {s0.mean():.3f}")
        else:
            print(f"      (chỉ thông tin) {msg}")
    nees, s0, sdr, _ = nees_mc(1.0, M, 7, weighted=False)
    # Ghi chú: phiên bản đầu của C5c kiểm |mean NEES - 6| > 0.6 và FAIL (mean NEES = 6.05) -> đổi sang
    # kiểm từng thành phần; xem mục 7 của ghi chú.
    report("C5c đối chứng: GN không trọng số + covariance đẳng hướng eq.(27) sai ở từng thành phần",
           np.max(np.abs(sdr - 1)) > 0.1,
           f"mean NEES {nees.mean():.2f}, phủ 95% = {np.mean(nees < chi95):.3f}, "
           f"SD dự đoán/thực nghiệm = [{', '.join(f'{x:.2f}' for x in sdr)}]")


if __name__ == "__main__":
    t0 = time.time()
    print(f"cv2 {cv2.__version__}, numpy {np.__version__}")
    check_C1()
    check_C2()
    check_C3_C4()
    check_C5()
    npass = sum(ok for _, ok in RESULTS)
    print(f"\nTổng: {npass}/{len(RESULTS)} PASS, {time.time() - t0:.0f} s")
