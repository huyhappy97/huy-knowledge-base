"""Kiểm chứng số (cửa (b)) cho chen2022epropnp — EPro-PnP, CVPR 2022.

Kiểm các công thức lõi trên cảnh tổng hợp nhỏ, chỉ CPU, seed cố định:
  C1  log-normalizer log Z = log ∫ exp(-1/2 Σ||f_i(y)||^2) dy  [eq. (3)/(5)]:
      importance sampling vanilla [eq. (6)] và AMIS [Alg. 1] hội tụ khi số mẫu tăng,
      và khớp xấp xỉ Laplace dùng Hessian Gauss-Newton J^T J khi hậu nghiệm gần Gauss;
      lệch khỏi Laplace khi hậu nghiệm không Gauss (ít điểm, nhiễu lớn, xa).
  C2  gradient theo trọng số từng điểm [eq. (8)]: công thức giải tích (ước lượng MC)
      khớp sai phân hữu hạn của chính ước lượng MC (mẫu cố định).
  C3  diễn giải của eq. (8): điểm không nhất quán với pose GT (ngoại lai) nhận gradient
      làm giảm trọng số; tối ưu trọng số theo L_KL đẩy trọng số ngoại lai xuống.
  C4  vai trò số hạng log Z (Fig. 2, §3.1): chỉ L_tgt thì thu trọng số về 0 (suy biến);
      L_KL có cực tiểu hữu hạn theo thang trọng số; loss kiểu điểm ||y*-y_gt||^2
      (cách BPnP / implicit diff.) bất biến theo thang trọng số -> không có tín hiệu.
  C5  lưỡng nghĩa (§1, §3.1): với target phẳng xa, nghiệm cực tiểu toàn cục y* nhảy
      giữa hai nhánh khi dữ liệu đổi liên tục, còn L_KL (MC, đề xuất trộn hai mode) liên tục.

Tham số hoá pose: y = (omega, delta) quanh pose tham chiếu (R0, t0):
  R = exp(omega) R0, t = t0 + delta; dy = độ đo Lebesgue trên (omega, delta) (tôi chọn;
  bài không nói rõ độ đo dy trên SE(3)).
Chạy:  python3 VSLAM/pnp/code/chen2022epropnp_check.py
"""
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from common import K_DEFAULT, make_scene, project, rodrigues, rot_err_deg  # noqa: E402

import cv2  # noqa: E402

K = K_DEFAULT
LOG2PI = np.log(2 * np.pi)
RESULTS = []


def report(name, ok, msg):
    RESULTS.append((name, ok))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {msg}")


# ---------------------------------------------------------------- mô hình
def batch_rodrigues(W):
    th = np.linalg.norm(W, axis=1)
    k = W / np.maximum(th, 1e-300)[:, None]
    Kx = np.zeros((len(W), 3, 3))
    Kx[:, 0, 1], Kx[:, 0, 2] = -k[:, 2], k[:, 1]
    Kx[:, 1, 0], Kx[:, 1, 2] = k[:, 2], -k[:, 0]
    Kx[:, 2, 0], Kx[:, 2, 1] = -k[:, 1], k[:, 0]
    s, c = np.sin(th)[:, None, None], (1 - np.cos(th))[:, None, None]
    return np.eye(3)[None] + s * Kx + c * Kx @ Kx


def residuals_batch(Y, R0, t0, X, u):
    """Y (M,6) -> r (M,N,2): r_i(y) = pi(R X_i + t) - u_i (chưa nhân trọng số)."""
    Rs = batch_rodrigues(Y[:, :3]) @ R0[None]
    ts = t0[None] + Y[:, 3:]
    Xc = np.einsum('mab,nb->mna', Rs, X) + ts[:, None, :]
    p = np.einsum('ab,mnb->mna', K, Xc)
    return p[..., :2] / p[..., 2:3] - u[None]


def energy_batch(Y, R0, t0, X, u, w):
    """E(y) = 1/2 Σ_i ||w_i ∘ r_i(y)||^2 (eq. (1)/(2)), w (N,2)."""
    r = residuals_batch(Y, R0, t0, X, u)
    return 0.5 * np.sum((w[None] * r) ** 2, axis=(1, 2)), r


def jacobian(R0, t0, X, u, w):
    """F = vec(w∘r) và J = dF/dy tại y=0 (giải tích, nhiễu trái trên SO(3))."""
    RX = X @ R0.T
    Xc = RX + t0
    x, y, z = Xc.T
    fx, fy = K[0, 0], K[1, 1]
    dpi = np.zeros((len(X), 2, 3))
    dpi[:, 0, 0] = fx / z
    dpi[:, 0, 2] = -fx * x / z ** 2
    dpi[:, 1, 1] = fy / z
    dpi[:, 1, 2] = -fy * y / z ** 2
    dXc = np.zeros((len(X), 3, 6))
    for i in range(len(X)):
        a = RX[i]
        dXc[i, :, :3] = -np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])
        dXc[i, :, 3:] = np.eye(3)
    J = (w[:, :, None] * (dpi @ dXc)).reshape(-1, 6)
    r = project(X, R0, t0, K) - u
    return (w * r).reshape(-1), J


def weighted_lm(R, t, X, u, w, iters=100):
    """LM cho eq. (1) có trọng số, khởi tạo (R, t). Trả về R*, t*, E*, H=J^T J."""
    lam = 1e-3
    F, J = jacobian(R, t, X, u, w)
    E = 0.5 * F @ F
    for _ in range(iters):
        H = J.T @ J
        dy = -np.linalg.solve(H + lam * np.diag(np.diag(H)), J.T @ F)
        Rn, tn = rodrigues(dy[:3]) @ R, t + dy[3:]
        Fn, Jn = jacobian(Rn, tn, X, u, w)
        En = 0.5 * Fn @ Fn
        if En < E:
            R, t, F, J, lam = Rn, tn, Fn, Jn, lam * 0.3
            conv = E - En < 1e-12 * max(E, 1e-30)
            E = En
            if conv:
                break
        else:
            lam *= 10
            if lam > 1e12:
                break
    return R, t, E, J.T @ J


def pnp_init(X, u):
    ok, rv, tv = cv2.solvePnP(X, u, K, None, flags=cv2.SOLVEPNP_EPNP)
    R, _ = cv2.Rodrigues(rv)
    return R, tv.ravel()


def laplace_logZ(E_star, H):
    """log Z ≈ -E* + d/2 log 2π - 1/2 log det H  (Laplace, Hessian GN)."""
    return -E_star + 0.5 * 6 * LOG2PI - 0.5 * np.linalg.slogdet(H)[1]


# ------------------------------------------------------------ đề xuất (proposal)
def mvt_logpdf(Y, mu, S, nu):
    d = Y.shape[1]
    L = np.linalg.cholesky(S)
    z = np.linalg.solve(L, (Y - mu).T)
    m = np.sum(z * z, axis=0)
    from scipy.special import gammaln
    return (gammaln((nu + d) / 2) - gammaln(nu / 2) - 0.5 * d * np.log(nu * np.pi)
            - np.sum(np.log(np.diag(L))) - 0.5 * (nu + d) * np.log1p(m / nu))


def mvt_sample(rng, mu, S, nu, n):
    L = np.linalg.cholesky(S)
    z = rng.standard_normal((n, len(mu))) @ L.T
    g = rng.chisquare(nu, n) / nu
    return mu + z / np.sqrt(g)[:, None]


def logsumexp(a, axis=None):
    m = np.max(a, axis=axis, keepdims=True)
    return np.squeeze(m + np.log(np.sum(np.exp(a - m), axis=axis, keepdims=True)), axis=axis)


def vanilla_is(rng, M, R0, t0, X, u, w, mu, S, nu=5.0):
    """eq. (6): log (1/M) Σ exp(-E(y_j)) / q(y_j)."""
    Y = mvt_sample(rng, mu, S, nu, M)
    E, _ = energy_batch(Y, R0, t0, X, u, w)
    lv = -E - mvt_logpdf(Y, mu, S, nu)
    return logsumexp(lv) - np.log(M)


def amis(rng, R0, t0, X, u, w, mu, S, T=4, Kp=128, nu=5.0, return_samples=False):
    """Alg. 1 (AMIS, Cornuet et al.) với đề xuất t đa biến 6D (bài dùng t 3D cho vị trí +
    ACG cho quaternion; ở đây gộp làm một cho gọn — (tôi chọn))."""
    props, Ys, logP = [], [], []
    for it in range(T):
        props.append((mu.copy(), S.copy()))
        Y = mvt_sample(rng, mu, S, nu, Kp)
        E, _ = energy_batch(Y, R0, t0, X, u, w)
        Ys.append(Y)
        logP.append(-E)
        Yall = np.concatenate(Ys)
        lP = np.concatenate(logP)
        # Q = (1/t) Σ_m q_m(y) — mọi mẫu cũ được tính lại trọng số (dòng 7–9 của Alg. 1)
        lq = np.stack([mvt_logpdf(Yall, m_, S_, nu) for m_, S_ in props])
        lQ = logsumexp(lq, axis=0) - np.log(len(props))
        lv = lP - lQ
        if it < T - 1:
            a = np.exp(lv - lv.max())
            a /= a.sum()
            mu = a @ Yall
            D = Yall - mu
            S = (a[:, None] * D).T @ D * (nu - 2) / nu + 1e-12 * np.eye(6)
    L = logsumexp(lv) - np.log(len(lv))
    if return_samples:
        return L, Yall, lv
    return L


def setup(n, sigma, seed, depth=(4.0, 8.0), n_out=0, out_px=0.0):
    rng = np.random.default_rng(seed)
    X, u, uc, Rg, tg = make_scene(n, rng, depth=depth, sigma_px=sigma)
    if n_out:
        idx = np.arange(n_out)
        ang = rng.uniform(0, 2 * np.pi, n_out)
        u[idx] += out_px * np.c_[np.cos(ang), np.sin(ang)]
    return X, u, Rg, tg


# ---------------------------------------------------------------- C1
def check_C1():
    print("\n== C1: log Z — IS vanilla eq.(6), AMIS Alg.1, Laplace ==")
    for label, n, sigma, depth, tol in [("gần Gauss (N=12, σ=1px, sâu 4–8m)", 12, 1.0, (4, 8), 0.05),
                                         ("không Gauss (N=4, σ=40px, sâu 20–40m)", 4, 40.0, (20, 40), None)]:
        X, u, Rg, tg = setup(n, sigma, seed=1, depth=depth)
        w = np.full((n, 2), 1.0 / sigma)
        R0, t0 = pnp_init(X, u)
        Rs, ts, Es, H = weighted_lm(R0, t0, X, u, w)
        Lap = laplace_logZ(Es, H)
        S0 = np.linalg.inv(H)
        mu0 = np.zeros(6)
        rng = np.random.default_rng(100)
        ref = np.mean([vanilla_is(rng, 2 ** 17, Rs, ts, X, u, w, mu0, 2.0 * S0) for _ in range(8)])
        print(f"  [{label}]  Laplace = {Lap:.4f}   tham chiếu IS 8x2^17 mẫu = {ref:.4f}   "
              f"Laplace - ref = {Lap - ref:+.4f}")
        print(f"    {'M':>6} | {'IS vanilla: TB ± std (20 lần)':>32} | {'AMIS T=4: TB ± std':>24}")
        stds = []
        for M in [128, 512, 2048, 8192]:
            rng = np.random.default_rng(M)
            v = [vanilla_is(rng, M, Rs, ts, X, u, w, mu0, 2.0 * S0) for _ in range(20)]
            a = [amis(rng, Rs, ts, X, u, w, mu0, 2.0 * S0, T=4, Kp=M // 4) for _ in range(20)]
            stds.append(np.std(a))
            print(f"    {M:>6} | {np.mean(v):>14.4f} ± {np.std(v):<15.4f} | {np.mean(a):>10.4f} ± {np.std(a):.4f}")
        if tol is not None:
            report("C1a", abs(Lap - ref) < tol and stds[-1] < stds[0],
                   f"hậu nghiệm gần Gauss: |Laplace - MC| = {abs(Lap - ref):.4f} < {tol}; "
                   f"std AMIS giảm {stds[0]:.4f} -> {stds[-1]:.4f}")
        else:
            report("C1b", abs(Lap - ref) > 0.05 and stds[-1] < stds[0],
                   f"hậu nghiệm không Gauss: Laplace lệch MC {Lap - ref:+.4f} nat; "
                   f"MC vẫn hội tụ (std {stds[0]:.4f} -> {stds[-1]:.4f})")
        if tol is not None:
            # AMIS với đề xuất khởi đầu cố ý tồi: tâm lệch 2σ dọc trục riêng lớn nhất của
            # hậu nghiệm Laplace, covariance co còn 0.3 lần — AMIS có tự sửa được không?
            rng = np.random.default_rng(7)
            ev, V = np.linalg.eigh(S0)
            mu_bad = 2.0 * np.sqrt(ev[-1]) * V[:, -1]
            v = [vanilla_is(rng, 512, Rs, ts, X, u, w, mu_bad, 0.3 * S0) for _ in range(20)]
            a = [amis(rng, Rs, ts, X, u, w, mu_bad, 0.3 * S0, T=4, Kp=128) for _ in range(20)]
            print(f"    đề xuất khởi đầu tồi (lệch 2σ, cov x0.3), 512 mẫu: IS vanilla {np.mean(v):.3f} ± {np.std(v):.3f}"
                  f" | AMIS {np.mean(a):.3f} ± {np.std(a):.3f} | ref {ref:.3f}")
            report("C1c", abs(np.mean(a) - ref) < abs(np.mean(v) - ref),
                   f"AMIS sửa được đề xuất tồi: sai lệch |AMIS-ref| = {abs(np.mean(a) - ref):.3f}"
                   f" < |IS-ref| = {abs(np.mean(v) - ref):.3f}")


# ---------------------------------------------------------------- C2, C3
def kl_loss_and_grad(rng, X, u, w, Rg, tg, T=4, Kp=128):
    """L_KL = L_tgt + L_pred (eq. (5)); gradient theo w bằng eq. (7)/(8) với MC tự chuẩn hoá.
    Trả về L, dL/dw, và thông tin phụ."""
    R0, t0 = pnp_init(X, u)
    Rs, ts, Es, H = weighted_lm(R0, t0, X, u, w)
    Lpred, Y, lv = amis(rng, Rs, ts, X, u, w, np.zeros(6), 2.0 * np.linalg.inv(H), T=T, Kp=Kp,
                        return_samples=True)
    r_gt = project(X, Rg, tg, K) - u
    Ltgt = 0.5 * np.sum((w * r_gt) ** 2)
    _, r = energy_batch(Y, Rs, ts, X, u, w)
    a = np.exp(lv - lv.max())
    a /= a.sum()
    Er2 = np.einsum('m,mna->na', a, r ** 2)          # E_{y~p(y|X)} r_i(y)^{∘2}
    grad = w * r_gt ** 2 - w * Er2                  # eq. (8) với dấu dương: dL/dw
    return Ltgt + Lpred, grad, dict(Rs=Rs, ts=ts, Y=Y, lv=lv, r_gt=r_gt, Er2=Er2, Ltgt=Ltgt, Lpred=Lpred)


def check_C2_C3():
    print("\n== C2: gradient theo trọng số, eq. (8) vs sai phân hữu hạn ==")
    n, sigma = 20, 1.0
    X, u, Rg, tg = setup(n, sigma, seed=3, n_out=4, out_px=8.0)   # điểm 0..3 là ngoại lai 8px
    w = np.full((n, 2), 1.0)
    rng = np.random.default_rng(11)
    L, g, info = kl_loss_and_grad(rng, X, u, w, Rg, tg, T=4, Kp=512)
    # sai phân hữu hạn trên CHÍNH ước lượng MC: giữ cố định mẫu y_j và log q(y_j)
    Rs, ts, Y, lv = info['Rs'], info['ts'], info['Y'], info['lv']
    E0, _ = energy_batch(Y, Rs, ts, X, u, w)
    lq = -E0 - lv

    def L_fixed(wv):
        E, _ = energy_batch(Y, Rs, ts, X, u, wv)
        lt = 0.5 * np.sum((wv * (project(X, Rg, tg, K) - u)) ** 2)
        return lt + logsumexp(-E - lq) - np.log(len(Y))

    h = 1e-6
    fd = np.zeros_like(w)
    for i in range(n):
        for k in range(2):
            wp, wm = w.copy(), w.copy()
            wp[i, k] += h
            wm[i, k] -= h
            fd[i, k] = (L_fixed(wp) - L_fixed(wm)) / (2 * h)
    rel = np.linalg.norm(fd - g) / np.linalg.norm(fd)
    report("C2", rel < 1e-5, f"||eq.(8) - FD|| / ||FD|| = {rel:.2e} (N=20, 512 mẫu AMIS, mẫu cố định)")

    # độ chính xác của E r^2 theo số mẫu: so với tham chiếu 2^16 mẫu IS
    Rs_, ts_ = info['Rs'], info['ts']
    F, J = jacobian(Rs_, ts_, X, u, w)
    S0 = 2.0 * np.linalg.inv(J.T @ J)
    rngr = np.random.default_rng(5)
    Yr = mvt_sample(rngr, np.zeros(6), S0, 5.0, 2 ** 16)
    Er, rr = energy_batch(Yr, Rs_, ts_, X, u, w)
    lvr = -Er - mvt_logpdf(Yr, np.zeros(6), S0, 5.0)
    ar = np.exp(lvr - lvr.max()); ar /= ar.sum()
    g_ref = w * info['r_gt'] ** 2 - w * np.einsum('m,mna->na', ar, rr ** 2)
    print("    sai số tương đối của gradient MC so với tham chiếu 2^16 mẫu:")
    for Kp in [32, 128, 512]:
        errs = []
        for s in range(10):
            _, gk, _ = kl_loss_and_grad(np.random.default_rng(1000 + s), X, u, w, Rg, tg, T=4, Kp=Kp)
            errs.append(np.linalg.norm(gk - g_ref) / np.linalg.norm(g_ref))
        print(f"      T=4, K'={Kp:>4}: {np.mean(errs):.4f} (TB 10 lần)")

    print("\n== C3: diễn giải eq. (8) — ngoại lai (4/20 điểm lệch 8px, σ=1px) ==")
    neg = -g
    per_pt = neg.sum(1)
    print(f"    -dL/dw (tổng 2 trục)  ngoại lai: {np.round(per_pt[:4], 2)}")
    print(f"                          nội điểm : TB {per_pt[4:].mean():+.3f}, min {per_pt[4:].min():+.3f}, max {per_pt[4:].max():+.3f}")
    print(f"    r^2(y_gt) ngoại lai TB {np.mean(info['r_gt'][:4] ** 2):.1f} px^2 ; nội điểm TB {np.mean(info['r_gt'][4:] ** 2):.2f} px^2;"
          f"  E_p r^2 TB (tất cả) {np.mean(info['Er2']):.2f} px^2")
    r2gt, r2star = (info['r_gt'] ** 2).sum(1), ((project(X, info['Rs'], info['ts'], K) - u) ** 2).sum(1)
    print(f"    ngoại lai: r^2(y_gt) {np.round(r2gt[:4], 1)} | r^2(y*) {np.round(r2star[:4], 1)} | "
          f"E_p r^2 {np.round(info['Er2'].sum(1)[:4], 1)}")
    report("C3a", np.all(per_pt[:4] < 0),
           "mọi ngoại lai có -dL/dw < 0 (trọng số bị đẩy xuống), đúng dấu tuyên bố ở §3.3")
    print("[NOTE] C3a' (giả thuyết của tôi, mạnh hơn bài nói) 'mọi ngoại lai bị đẩy mạnh hơn mọi nội điểm': "
          + ("ĐÚNG" if np.all(per_pt[:4] < per_pt[4:].min()) else "SAI") + ": ngoại lai yếu nhất "
           f"{per_pt[:4].max():+.2f} vs nội điểm thấp nhất {per_pt[4:].min():+.2f} — dấu chỉ phụ thuộc "
           f"r^2(y_gt) - E_p r^2 ≈ r^2(y_gt) - r^2(y*), không phải độ lớn r^2(y_gt)")

    # tối ưu trọng số (log w, một vô hướng/điểm) theo L_KL bằng gradient descent
    lw = np.zeros(n)
    Rs0 = info['Rs']
    e0 = rot_err_deg(Rs0, Rg)
    hist = []
    for it in range(150):
        wv = np.repeat(np.exp(lw)[:, None], 2, axis=1)
        Lk, gk, inf = kl_loss_and_grad(np.random.default_rng(2000 + it), X, u, wv, Rg, tg, T=4, Kp=128)
        glw = (gk * wv).sum(1)       # chain rule: dL/dlog w = w * dL/dw
        lw -= 0.05 * glw
        hist.append(Lk)
    wv = np.exp(lw)
    e1 = rot_err_deg(inf['Rs'], Rg)
    t_err0 = np.linalg.norm(info['ts'] - tg)
    t_err1 = np.linalg.norm(inf['ts'] - tg)
    print(f"    sau 150 bước GD trên log w (lr 0.05): L_KL {hist[0]:.2f} -> {np.mean(hist[-10:]):.2f}")
    print(f"      w ngoại lai: {np.round(wv[:4], 3)} ; w nội điểm: TB {wv[4:].mean():.3f} (min {wv[4:].min():.3f})")
    print(f"      sai số y* so với GT: quay {e0:.4f}° -> {e1:.4f}°, tịnh tiến {t_err0 * 100:.2f} cm -> {t_err1 * 100:.2f} cm")
    ratio = wv[:4].mean() / wv[4:].mean()
    stat = np.abs(-inf['r_gt'] ** 2 + inf['Er2']).sum(1)
    print(f"      tỉ số w ngoại lai / nội điểm (TB): 1.000 -> {ratio:.3f}; ở điểm dừng |r^2(y_gt) - E_p r^2| "
          f"ngoại lai {np.round(stat[:4], 2)} (điều kiện dừng của eq. (8) là = 0)")
    report("C3b", ratio < 0.5 and e1 < e0,
           f"tối ưu L_KL hạ tương đối trọng số ngoại lai (tỉ số {ratio:.3f} < 0.5) và y* tốt lên; "
           f"nhưng w ngoại lai KHÔNG về 0 (nhỏ nhất {wv[:4].min():.3f})")


# ---------------------------------------------------------------- C4
def check_C4():
    print("\n== C4: vì sao cần log Z — quét thang trọng số w = s·(1/σ) ==")
    n, sigma = 12, 2.0
    X, u, Rg, tg = setup(n, sigma, seed=4)
    print(f"    {'s':>6} | {'L_tgt':>9} | {'L_pred=logZ':>11} | {'L_KL':>9} | {'||y*-y_gt||^2 (BPnP-kiểu)':>26}")
    rows = []
    for s in [0.05, 0.1, 0.3, 0.6, 1.0, 1.5, 3.0, 10.0]:
        w = np.full((n, 2), s / sigma)
        L, _, inf = kl_loss_and_grad(np.random.default_rng(3), X, u, w, Rg, tg, T=4, Kp=256)
        dy = np.r_[cv2.Rodrigues(inf['Rs'] @ Rg.T)[0].ravel(), inf['ts'] - tg]
        pt = dy @ dy
        rows.append((s, inf['Ltgt'], inf['Lpred'], L, pt))
        print(f"    {s:>6.2f} | {inf['Ltgt']:>9.3f} | {inf['Lpred']:>11.3f} | {L:>9.3f} | {pt:>26.3e}")
    rows = np.array(rows)
    imin = np.argmin(rows[:, 3])
    report("C4a", np.all(np.diff(rows[:, 1]) > 0) and 0 < imin < len(rows) - 1,
           f"L_tgt đơn điệu -> 0 khi s -> 0 (suy biến), L_KL có cực tiểu trong khoảng, tại s = {rows[imin, 0]}")
    report("C4b", np.ptp(rows[:, 4]) < 1e-6 * rows[:, 4].max(),
           f"loss điểm ||y*-y_gt||^2 không đổi theo s (dao động {np.ptp(rows[:, 4]):.1e}) -> không học được thang/độ bất định")
    # Dưới Laplace: L_KL(s) = s^2 (A - E1*) - 6 log s + const, A = L_tgt(s=1), E1* = E(y*)(s=1)
    # -> s_opt^2 (A - E1*) = d/2 = 3: thang tối ưu làm khoảng Mahalanobis ½ của y_gt đúng bằng d/2.
    w1 = np.full((n, 2), 1.0 / sigma)
    R0, t0 = pnp_init(X, u)
    _, _, E1, _ = weighted_lm(R0, t0, X, u, w1)
    A = 0.5 * np.sum((w1 * (project(X, Rg, tg, K) - u)) ** 2)
    s_lap = np.sqrt(3.0 / (A - E1))
    from scipy.optimize import minimize_scalar
    f = lambda ls: kl_loss_and_grad(np.random.default_rng(3), X, u, np.full((n, 2), np.exp(ls) / sigma),
                                    Rg, tg, T=4, Kp=1024)[0]
    s_mc = np.exp(minimize_scalar(f, bounds=(np.log(0.3), np.log(5)), method='bounded',
                                  options={'xatol': 1e-3}).x)
    report("C4c", abs(s_mc / s_lap - 1) < 0.05,
           f"thang tối ưu của L_KL (MC) s = {s_mc:.3f} vs dự đoán Laplace sqrt(3/(L_tgt - E*)) = {s_lap:.3f}")


# ---------------------------------------------------------------- C5
def check_C5():
    print("\n== C5: lưỡng nghĩa — target phẳng xa, y* nhảy nhánh, L_KL liên tục ==")
    # hình vuông 4 điểm cạnh 0.2 m, cách 6 m, nghiêng 20°: hai cực tiểu (IPPE) gần bằng nhau
    s = 0.1
    X = np.array([[-s, -s, 0], [s, -s, 0], [s, s, 0], [-s, s, 0]], float)
    Rg = rodrigues(np.radians([20, 5, 0]))
    tg = np.array([0.0, 0.0, 6.0])
    uc = project(X, Rg, tg, K)
    rng = np.random.default_rng(9)
    base = uc + rng.normal(scale=0.3, size=uc.shape)
    sigma = 1.0
    w = np.full((4, 2), 1.0 / sigma)
    direction = np.array([[1, 0], [-1, 0], [1, 0], [-1, 0]], float)  # kéo liên tục ảnh theo 1 hướng
    alphas = np.linspace(-1.5, 1.5, 31)
    rows = []
    for a in alphas:
        u = base + a * direction
        ok, rvs, tvs, _ = cv2.solvePnPGeneric(X, u, K, None, flags=cv2.SOLVEPNP_IPPE)
        mins = []
        for rv, tv in zip(rvs, tvs):
            R0, _ = cv2.Rodrigues(rv)
            mins.append(weighted_lm(R0, tv.ravel(), X, u, w))
        mins.sort(key=lambda m: m[2])
        Rstar = mins[0][0]
        # log Z: IS với đề xuất trộn hai Laplace của hai cực tiểu (bài: AMIS khởi từ PnP)
        rq = np.random.default_rng(42)
        M = 100000
        comps = []
        for Rm, tm, Em, Hm in mins:
            comps.append((Rm, tm, 2.0 * np.linalg.inv(Hm)))
        # toạ độ tích phân cố định quanh (R_gt, t_gt) cho MỌI α: nếu đổi điểm tham chiếu theo y*
        # thì độ đo Lebesgue trên toạ độ exp (không phải độ đo Haar) tự tạo một chỗ gãy giả
        Rr, tr = Rg, tg
        mus = []
        for Rm, tm, Sm in comps:
            mus.append(np.r_[cv2.Rodrigues(Rm @ Rr.T)[0].ravel(), tm - tr])
        Ys = [mvt_sample(rq, mus[c], comps[c][2], 5.0, M // 2) for c in range(2)]
        Y = np.concatenate(Ys)
        lq = logsumexp(np.stack([mvt_logpdf(Y, mus[c], comps[c][2], 5.0) for c in range(2)]), axis=0) - np.log(2)
        E, _ = energy_batch(Y, Rr, tr, X, u, w)
        logZ = logsumexp(-E - lq) - np.log(len(Y))
        Lap = laplace_logZ(mins[0][2], mins[0][3])
        rows.append((a, rot_err_deg(Rstar, Rg), mins[0][2], mins[1][2], logZ, Lap,
                     rot_err_deg(mins[0][0], mins[1][0])))
    rows = np.array(rows)
    print(f"    {'α(px)':>6} | {'∠(R*,R_gt)°':>11} | {'E nhánh1':>8} | {'E nhánh2':>8} | {'logZ MC':>8} | {'logZ Laplace@y*':>15}")
    for r in rows[::3]:
        print(f"    {r[0]:>6.2f} | {r[1]:>11.2f} | {r[2]:>8.3f} | {r[3]:>8.3f} | {r[4]:>8.3f} | {r[5]:>15.3f}")
    print(f"    góc giữa hai nhánh: {rows[:, 6].min():.1f}°–{rows[:, 6].max():.1f}°")
    jump_rot = np.max(np.abs(np.diff(rows[:, 1])))
    # sai phân bậc hai trừ độ cong nền (trung vị): bắt chỗ gãy/nhảy tại điểm đổi nhánh
    D2m, D2l = np.diff(rows[:, 4], 2), np.diff(rows[:, 5], 2)
    d2_mc = np.max(np.abs(D2m - np.median(D2m)))
    d2_lap = np.max(np.abs(D2l - np.median(D2l)))
    gap = rows[:, 4] - rows[:, 5]
    report("C5a", jump_rot > 10,
           f"y* (cực tiểu toàn cục) nhảy {jump_rot:.1f}° giữa hai bước α cách 0.1 px -> ánh xạ X -> y* không liên tục")
    report("C5b", d2_mc < 0.5 * d2_lap,
           f"log Z (MC, trộn hai mode) trơn: max|Δ² - nền| = {d2_mc:.4f} nat, Laplace@y* gãy tại chỗ đổi nhánh: "
           f"{d2_lap:.4f} nat (độ cong nền {np.median(D2l):.3f})")
    report("C5c", gap.max() > 0.5,
           f"Laplace quanh một nghiệm hụt log Z tới {gap.max():.3f} nat khi hai mode ngang nhau (≈ log 2)")
    print(f"    log Z_MC - log Z_Laplace@y* nằm trong [{gap.min():.3f}, {gap.max():.3f}] nat "
          f"(log 2 = {np.log(2):.3f}: Laplace bỏ sót mode thứ hai)")


if __name__ == "__main__":
    t0 = time.time()
    check_C1()
    check_C2_C3()
    check_C4()
    check_C5()
    print(f"\nTổng: {sum(ok for _, ok in RESULTS)}/{len(RESULTS)} PASS; thời gian {time.time() - t0:.1f} s")
