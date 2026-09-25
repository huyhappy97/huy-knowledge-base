"""Kiểm chứng số (cửa (b)) cho ding2023p3p — "Revisiting the P3P Problem", CVPR 2023.

Cài lại bộ giải TỪ BÀI BÁO (không chép mã nguồn gốc): eq. (3)-(6) -> hai conic (7)-(8),
cubic det(C1 + sigma C2) = 0 (eq. 11), bậc ba khuyết (29)-(32), adjoint -C* = v v^T (eq. 20),
D = C + [v]_x = 2 p q^T (eq. 22), giao đường-conic (23)+(5), d3 theo (24), Gauss-Newton trên (3),
R = B A^{-1} (eq. 28), rồi t theo (1). Logic nhánh theo Algorithm 1 [tr. 6].

Các lựa chọn của người ghi chú mà bài KHÔNG quy định (ghi rõ trong ghi chú mục 7):
  * giao đường-conic: khử biến có hệ số lớn hơn trong (23) thay vì luôn khử y (bài: "quadratic in x");
  * Gauss-Newton: tối đa 5 bước Newton trên 3 phương trình (3), dừng khi tổng |r| < 1e-12 * scale;
  * lấy cột/hàng của D theo phần tử |D_ij| lớn nhất ("one row and the corresponding column");
  * nhánh Delta == 0 so sánh đúng bằng 0 như Algorithm 1 (thực tế gần như không bao giờ xảy ra).

Chạy:  python3 VSLAM/pnp/code/ding2023p3p_check.py        (~1-2 phút)
"""
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from common import random_rotation  # noqa: E402

import cv2  # noqa: E402

N_MAIN = 100_000
N_SIDE = 3_000
N_DEG = 600


# ----------------------------------------------------------------------------------------------
# Bộ giải theo bài báo
# ----------------------------------------------------------------------------------------------
def skew(v):
    return np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])


def adjugate_sym(C):
    """adj(C) cho ma trận đối xứng 3x3 (ma trận phụ hợp = cofactor^T)."""
    a, b, c = C[0, 0], C[0, 1], C[0, 2]
    d, e, f = C[1, 1], C[1, 2], C[2, 2]
    return np.array([[d * f - e * e, c * e - b * f, b * e - c * d],
                     [c * e - b * f, a * f - c * c, b * c - a * e],
                     [b * e - c * d, b * c - a * e, a * d - b * b]])


def conics(m, X):
    """C1, C2 của eq. (7)-(8) trên cơ sở [1, x, y], x = d1/d3, y = d2/d3 (eq. (4)-(6))."""
    AB2 = np.sum((X[0] - X[1]) ** 2)
    AC2 = np.sum((X[0] - X[2]) ** 2)
    BC2 = np.sum((X[1] - X[2]) ** 2)
    a, b = AB2 / BC2, AC2 / BC2
    m12, m13, m23 = m[0] @ m[1], m[0] @ m[2], m[1] @ m[2]
    # (4): x^2 + (1-a) y^2 - 2 m12 x y + 2 a m23 y - a = 0
    C1 = np.array([[-a, 0.0, a * m23], [0.0, 1.0, -m12], [a * m23, -m12, 1.0 - a]])
    # (5): x^2 - b y^2 - 2 m13 x + 2 b m23 y + 1 - b = 0
    C2 = np.array([[1.0 - b, -m13, b * m23], [-m13, 1.0, 0.0], [b * m23, 0.0, -b]])
    return C1, C2, a, b, m12, m13, m23, AB2, AC2, BC2


def cubic_coeffs(A, B):
    """det(A + s B) = k3 s^3 + k2 s^2 + k1 s + k0 (khai triển chuẩn)."""
    adjA, adjB = adjugate_sym(A), adjugate_sym(B)
    k0 = A[0] @ adjA[:, 0]  # det(A) = hàng 0 . cột 0 của adj(A)
    k1 = np.sum(adjA * B)   # tr(adj(A) B), B đối xứng
    k2 = np.sum(A * adjB)
    k3 = B[0] @ adjB[:, 0]
    return k3, k2, k1, k0


def depressed(k3, k2, k1, k0):
    """eq. (29)-(32): chuẩn hoá monic, đổi biến sigma = gamma - kappa2/3."""
    K2, K1, K0 = k2 / k3, k1 / k3, k0 / k3
    alpha = (3 * K1 - K2 ** 2) / 3
    beta = (2 * K2 ** 3 - 9 * K2 * K1 + 27 * K0) / 27
    Delta = -(4 * alpha ** 3 + 27 * beta ** 2)
    return K2, alpha, beta, Delta


def all_gamma_roots(alpha, beta, Delta):
    if Delta > 0:
        c = np.clip((3 * beta / (2 * alpha)) * np.sqrt(-3 / alpha), -1, 1)
        th = np.arccos(c) / 3
        return [2 * np.sqrt(-alpha / 3) * np.cos(th - 2 * np.pi * k / 3) for k in range(3)]
    return [one_gamma_root(alpha, beta, Delta)]


def one_gamma_root(alpha, beta, Delta, k=0):
    if Delta > 0:  # lượng giác [28]
        return all_gamma_roots(alpha, beta, Delta)[k]
    if Delta < 0:  # Cardano [3]
        s = np.sqrt(beta ** 2 / 4 + alpha ** 3 / 27)
        return np.cbrt(-beta / 2 + s) + np.cbrt(-beta / 2 - s)
    if alpha != 0:  # Delta == 0, nghiệm đơn gamma1 = 3 beta / alpha (Algorithm 1 dòng 24)
        return 3 * beta / alpha
    return 0.0


def lines_from_degenerate(C):
    """Method 2 [§3.2]: -C* = v v^T (20), D = C + [v]_x = 2 p q^T (22). Trả về list đường thẳng."""
    M = -adjugate_sym(C)
    i = int(np.argmax(np.diag(M)))
    scale = np.max(np.abs(C))
    if M[i, i] <= 1e-14 * scale ** 2:
        # hạng 1 (đường lặp) hoặc cặp đường ảo (M[i,i] < 0)
        if np.max(np.abs(M)) <= 1e-12 * scale ** 2:
            j = int(np.argmax(np.abs(np.diag(C))))
            return [C[:, j] / np.sqrt(abs(C[j, j]) + 1e-300)]
        return []  # cặp đường ảo: không có giao thực
    v = M[:, i] / np.sqrt(M[i, i])
    D = C + skew(v)
    r, c = np.unravel_index(np.argmax(np.abs(D)), D.shape)
    return [D[:, c].copy(), D[r, :].copy()]


def intersect_line_conic5(l, b, m13, m23, tang_tol=0.0):
    """Giao đường l0 + l1 x + l2 y = 0 (23) với conic (5). Trả về list (x, y) thực."""
    l0, l1, l2 = l
    out = []
    if abs(l2) >= abs(l1):  # y = w0 + w1 x
        w0, w1 = -l0 / l2, -l1 / l2
        # x^2 - b (w0 + w1 x)^2 - 2 m13 x + 2 b m23 (w0 + w1 x) + 1 - b = 0
        A = 1 - b * w1 * w1
        B = -2 * b * w0 * w1 - 2 * m13 + 2 * b * m23 * w1
        Cc = -b * w0 * w0 + 2 * b * m23 * w0 + 1 - b
        for x in quad_roots(A, B, Cc, tang_tol):
            out.append((x, w0 + w1 * x))
    else:  # x = w0 + w1 y
        w0, w1 = -l0 / l1, -l2 / l1
        A = w1 * w1 - b
        B = 2 * w0 * w1 - 2 * m13 * w1 + 2 * b * m23
        Cc = w0 * w0 - 2 * m13 * w0 + 1 - b
        for y in quad_roots(A, B, Cc, tang_tol):
            out.append((w0 + w1 * y, y))
    return out


def quad_roots(A, B, C, tang_tol=0.0):
    """tang_tol > 0: coi biệt thức âm nhẹ (|disc| <= tang_tol * (B^2 + |4AC|)) là nghiệm kép — biến thể
    của người ghi chú, KHÔNG có trong bài (mã OpenCV/PoseLib có ngưỡng tuyệt đối -1e-12 tương tự)."""
    if abs(A) < 1e-300:
        return [] if B == 0 else [-C / B]
    disc = B * B - 4 * A * C
    if disc < 0 and tang_tol > 0 and -disc <= tang_tol * (B * B + abs(4 * A * C)):
        return [-B / (2 * A)]
    if disc < 0:
        return []
    s = np.sqrt(disc)
    q = -0.5 * (B + np.copysign(s, B))  # công thức ổn định số
    r1 = q / A
    r2 = C / q if q != 0 else r1
    return [r1, r2] if disc > 0 else [r1]


def gauss_newton(d, m12, m13, m23, AB2, AC2, BC2, iters=5):
    d = np.array(d, float)
    sc = AB2 + AC2 + BC2
    for _ in range(iters):
        d1, d2, d3 = d
        r = np.array([d1 * d1 + d2 * d2 - 2 * d1 * d2 * m12 - AB2,
                      d1 * d1 + d3 * d3 - 2 * d1 * d3 * m13 - AC2,
                      d2 * d2 + d3 * d3 - 2 * d2 * d3 * m23 - BC2])
        if np.sum(np.abs(r)) < 1e-15 * sc:
            break
        J = 2 * np.array([[d1 - d2 * m12, d2 - d1 * m12, 0],
                          [d1 - d3 * m13, 0, d3 - d1 * m13],
                          [0, d2 - d3 * m23, d3 - d2 * m23]])
        try:
            d = d - np.linalg.solve(J, r)
        except np.linalg.LinAlgError:
            break
    return d


def pose_from_depths(d, m, X):
    """eq. (25)-(28): R = B A^{-1}; t từ (1)."""
    d1, d2, d3 = d
    b1, b2 = d1 * m[0] - d2 * m[1], d3 * m[2] - d1 * m[0]
    a1, a2 = X[0] - X[1], X[2] - X[0]
    Bm = np.c_[b1, b2, np.cross(b1, b2)]
    Am = np.c_[a1, a2, np.cross(a1, a2)]
    R = Bm @ np.linalg.inv(Am)
    t = d1 * m[0] - R @ X[0]
    return R, t


def pose_kabsch(d, m, X):
    """Biến thể của người ghi chú: khớp 3D-3D (Kabsch) giữa d_i m_i và X_i thay cho eq. (28)."""
    P = d[:, None] * m
    Pc, Xc = P - P.mean(0), X - X.mean(0)
    U, _, Vt = np.linalg.svd(Pc.T @ Xc)
    R = U @ np.diag([1, 1, np.sign(np.linalg.det(U @ Vt))]) @ Vt
    return R, P.mean(0) - R @ X.mean(0)


def ding_p3p(X, m, root_k=0, skip_logic=True, refine=True, info=None, tang_tol=0.0, kabsch=False):
    """X: (3,3) điểm thế giới; m: (3,3) tia chiếu đơn vị. Trả về list (R, t)."""
    C1, C2, a, b, m12, m13, m23, AB2, AC2, BC2 = conics(m, X)
    k3, k2, k1, k0 = cubic_coeffs(C1, C2)
    K2, alpha, beta, Delta = depressed(k3, k2, k1, k0)
    if info is not None:
        info["Delta_n"] = Delta / (4 * abs(alpha) ** 3 + 27 * beta ** 2 + 1e-300)
        info["Delta"] = Delta
    gamma = one_gamma_root(alpha, beta, Delta, root_k)
    sigma = gamma - K2 / 3
    C = C1 + sigma * C2
    lines = lines_from_degenerate(C)
    xy_all = []
    for li, l in enumerate(lines):
        xy = intersect_line_conic5(l, b, m13, m23, tang_tol)
        xy_all += xy
        if skip_logic and li == 0:
            has_real = len(xy) > 0
            # Algorithm 1: Delta>0 -> không có nghiệm ở đường 1 thì bỏ đường 2 (dòng 11-14);
            #              Delta<0 -> có nghiệm ở đường 1 thì bỏ đường 2 (dòng 19-22)
            if Delta > 0 and not has_real:
                break
            if Delta < 0 and has_real:
                break
    sols = []
    for x, y in xy_all:
        if not (x > 0 and y > 0):
            continue
        den = x * x - 2 * m13 * x + 1  # eq. (24)
        if den <= 0:
            continue
        d3 = np.sqrt(AC2 / den)
        d = np.array([x * d3, y * d3, d3])
        if refine:
            d = gauss_newton(d, m12, m13, m23, AB2, AC2, BC2)
        if np.any(~np.isfinite(d)) or np.any(d <= 0):
            continue
        sols.append(pose_kabsch(d, m, X) if kabsch else pose_from_depths(d, m, X))
        if info is not None:
            info.setdefault("depths", []).append(d)
    return sols


# ----------------------------------------------------------------------------------------------
# Sinh dữ liệu và đo sai số
# ----------------------------------------------------------------------------------------------
def scene_persson(rng):
    """Giao thức [§4, tr. 6-7] (theo Lambda Twist): quaternion ~ N(0,I) -> R_gt, t_gt ~ N(0,I),
    toạ độ ảnh chuẩn hoá đều trong [-1,1]^2, độ sâu đều trong [0.1, 10], X_i = R^T (d_i m_i - t).
    Ở đây m_i = [u, v, 1] và d là độ sâu z (bài không nói rõ d nhân với tia đơn vị hay [u,v,1])."""
    R = random_rotation(rng)
    t = rng.normal(size=3)
    uv = rng.uniform(-1, 1, (3, 2))
    z = rng.uniform(0.1, 10, 3)
    Xc = np.c_[uv, np.ones(3)] * z[:, None]
    X = (R.T @ (Xc - t).T).T
    return X, uv, R, t


def bearings_from_uv(uv):
    m = np.c_[uv, np.ones(len(uv))]
    return m / np.linalg.norm(m, axis=1, keepdims=True)


def xi(R, t, Rg, tg):
    """xi_R + xi_t như [§4, tr. 6]: chuẩn L1 (tổng |phần tử|) của hiệu."""
    return np.sum(np.abs(R - Rg)) + np.sum(np.abs(t - tg))


def run_cv(X, uv, flag):
    try:
        n, rv, tv = cv2.solveP3P(X.astype(np.float64), uv.astype(np.float64), np.eye(3), None, flag)
    except cv2.error:
        return []
    out = []
    for r, tt in zip(rv, tv):
        R, _ = cv2.Rodrigues(r)
        out.append((R, tt.ravel()))
    return out


def stats_for(sols_per_trial, gts, X_all, uv_all, name, gt_thr=1e-6, dup_thr=1e-5):
    n = len(gts)
    valid = 0; dup = 0; nosol = 0; gt_ok = 0; incorrect = 0
    best = np.full(n, np.inf)
    counts = np.zeros(5, int)
    for k, sols in enumerate(sols_per_trial):
        Rg, tg = gts[k]
        valid += len(sols)
        counts[min(len(sols), 4)] += 1
        if not sols:
            nosol += 1
            continue
        for i in range(len(sols)):
            for j in range(i):
                if xi(*sols[i], *sols[j]) < dup_thr:
                    dup += 1
                    break
        errs = [xi(R, t, Rg, tg) for R, t in sols]
        best[k] = min(errs)
        gt_ok += best[k] < gt_thr
        # "incorrect": nghiệm trả về không thoả hình học (định nghĩa của người ghi chú):
        # |det R - 1| > 1e-6 hoặc sai số góc tái chiếu lớn nhất > 1e-6 rad
        m = bearings_from_uv(uv_all[k])
        for R, t in sols:
            Xc = (R @ X_all[k].T).T + t
            ang = np.arccos(np.clip(np.sum(Xc / np.linalg.norm(Xc, axis=1, keepdims=True) * m, 1), -1, 1))
            if abs(np.linalg.det(R) - 1) > 1e-6 or ang.max() > 1e-6 or np.any(Xc[:, 2] <= 0):
                incorrect += 1
    fin = best[np.isfinite(best)]
    lg = np.log10(np.maximum(fin, 1e-17))
    q = np.percentile(lg, [50, 90, 99, 99.9, 100])
    print(f"  {name:<14s} nghiệm={valid:7d} TB/lượt={valid/n:.4f} trùng={dup:4d} không-nghiệm={nosol:4d} "
          f"có-GT(xi<1e-6)={gt_ok}/{n} ({100*(n-gt_ok)/n:.3f}% hỏng) sai-hình-học={incorrect}")
    print(f"  {'':<14s} xi của nghiệm tốt nhất: mean={fin.mean():.1e} median={np.median(fin):.1e} "
          f"max={fin.max():.1e} | log10 p50/p90/p99/p99.9/max = "
          + " / ".join(f"{v:.1f}" for v in q)
          + f" | số nghiệm 0..4: {counts.tolist()}")
    return best


# ----------------------------------------------------------------------------------------------
def check_identities(rng):
    print("[1] Đồng nhất thức đại số của §3.2 trên 1000 cặp p, q ngẫu nhiên")
    e20 = e19 = e22a = e22b = 0.0
    for _ in range(1000):
        p, q = rng.normal(size=3), rng.normal(size=3)
        C = np.outer(p, q) + np.outer(q, p)
        v = np.cross(p, q)
        e20 = max(e20, np.abs(-adjugate_sym(C) - np.outer(v, v)).max() / (v @ v))
        c = C
        n19 = c[0, 1]**2 + c[0, 2]**2 + c[1, 2]**2 - c[0, 0]*c[1, 1] - c[0, 0]*c[2, 2] - c[1, 1]*c[2, 2]
        e19 = max(e19, abs(n19 - v @ v) / (v @ v))
        # eq. (21) viết [v]_x = p q^T - q p^T ; kiểm cả hai dấu
        e22a = max(e22a, np.abs(skew(v) - (np.outer(p, q) - np.outer(q, p))).max())
        e22b = max(e22b, np.abs(skew(v) + (np.outer(p, q) - np.outer(q, p))).max())
    print(f"  (20) -C* = v v^T           : sai số tương đối max {e20:.1e}  -> {'PASS' if e20 < 1e-12 else 'FAIL'}")
    print(f"  (19) ||v||^2 theo c_ij     : sai số tương đối max {e19:.1e}  -> {'PASS' if e19 < 1e-12 else 'FAIL'}")
    print(f"  (21) [v]x = pq^T - qp^T    : sai số max {e22a:.1e}  -> {'PASS' if e22a < 1e-12 else 'SAI DẤU'}")
    print(f"       [v]x = qp^T - pq^T    : sai số max {e22b:.1e}  -> {'PASS' if e22b < 1e-12 else 'FAIL'}")
    print("       (dấu của v từ (20) tuỳ ý nên (22) vẫn cho 2pq^T hoặc 2qp^T — cả hai đều ra cặp đường {p, q})")


def check_conics_at_gt(rng):
    print("[2] Nghiệm thật (x, y) = (d1/d3, d2/d3) nằm trên cả hai conic (4), (5); và trên conic suy biến C")
    worst = 0.0; worst_c = 0.0
    for _ in range(2000):
        X, uv, R, t = scene_persson(rng)
        m = bearings_from_uv(uv)
        d = np.linalg.norm((R @ X.T).T + t, axis=1)
        C1, C2, *_ = conics(m, X)
        h = np.array([1, d[0] / d[2], d[1] / d[2]])
        s = max(1, np.abs(C1).max(), np.abs(C2).max()) * (h @ h)
        worst = max(worst, abs(h @ C1 @ h) / s, abs(h @ C2 @ h) / s)
        k3, k2, k1, k0 = cubic_coeffs(C1, C2)
        K2, al, be, De = depressed(k3, k2, k1, k0)
        for g in all_gamma_roots(al, be, De):
            C = C1 + (g - K2 / 3) * C2
            worst_c = max(worst_c, abs(np.linalg.det(C)) / np.abs(C).max() ** 3, abs(h @ C @ h) / (np.abs(C).max() * (h @ h)))
    print(f"  max |h^T C_i h| (chuẩn hoá) = {worst:.1e}; det(C)/|C|^3 và h^T C h trên mọi nghiệm cubic: {worst_c:.1e}"
          f"  -> {'PASS' if worst < 1e-12 and worst_c < 1e-9 else 'FAIL'}")


def main_benchmark(rng):
    print(f"[3] {N_MAIN} lượt không nhiễu theo giao thức của bài (Lambda Twist): ours vs cv2 P3P vs cv2 AP3P")
    data = [scene_persson(rng) for _ in range(N_MAIN)]
    gts = [(R, t) for _, _, R, t in data]
    Xs = [d[0] for d in data]; uvs = [d[1] for d in data]
    res = {}
    t0 = time.time()
    ours, deltas = [], []
    for X, uv, _, _ in data:
        info = {}
        ours.append(ding_p3p(X, bearings_from_uv(uv), info=info))
        deltas.append(info["Delta_n"])
    t_ours = time.time() - t0
    t0 = time.time(); cvp3p = [run_cv(X, uv, cv2.SOLVEPNP_P3P) for X, uv, _, _ in data]; t_p3p = time.time() - t0
    t0 = time.time(); cvap3p = [run_cv(X, uv, cv2.SOLVEPNP_AP3P) for X, uv, _, _ in data]; t_ap3p = time.time() - t0
    deltas = np.array(deltas)
    print(f"  Delta>0: {np.mean(deltas>0)*100:.1f}%  Delta<0: {np.mean(deltas<0)*100:.1f}%  Delta==0: {np.sum(deltas==0)}"
          f"   (thời gian Python, chỉ để tham khảo: ours {t_ours:.0f}s, cv2 P3P {t_p3p:.1f}s, AP3P {t_ap3p:.1f}s)")
    res["ours"] = stats_for(ours, gts, Xs, uvs, "ours(numpy)")
    res["p3p"] = stats_for(cvp3p, gts, Xs, uvs, "cv2 P3P")
    res["ap3p"] = stats_for(cvap3p, gts, Xs, uvs, "cv2 AP3P")
    # So khớp số nghiệm dương giữa bản cài của tôi và cv2 P3P (cv2 5.0.0 có đúng là Ding?)
    same_n = np.mean([len(a) == len(b) for a, b in zip(ours, cvp3p)])
    same_n_ap = np.mean([len(a) == len(b) for a, b in zip(ours, cvap3p)])
    match = []
    for a, b in zip(ours, cvp3p):
        if len(a) == len(b) and a:
            match.append(max(min(xi(*sa, *sb) for sb in b) for sa in a))
    match = np.array(match)
    print(f"  số nghiệm trùng khớp ours vs cv2 P3P: {same_n*100:.3f}% lượt; ours vs cv2 AP3P: {same_n_ap*100:.3f}% lượt")
    print(f"  khi cùng số nghiệm, xi lớn nhất giữa nghiệm ghép cặp ours<->cv2 P3P: median {np.median(match):.1e}, "
          f"p99.9 {np.percentile(match, 99.9):.1e}")
    return data, deltas, ours, res


def check_algorithm_logic(data):
    print(f"[4] Algorithm 1: (a) bỏ đường thứ hai có làm mất nghiệm không; (b) Delta>0: chọn nghiệm cubic nào cũng như nhau?")
    lost = 0; diff_root = 0; n_pos = 0
    for X, uv, R, t in data[:N_SIDE]:
        m = bearings_from_uv(uv)
        info = {}
        s_skip = ding_p3p(X, m, skip_logic=True, info=info)
        s_all = ding_p3p(X, m, skip_logic=False)
        lost += len(s_all) != len(s_skip)
        if info["Delta"] > 0:
            n_pos += 1
            cnt = [len(ding_p3p(X, m, root_k=k, skip_logic=False)) for k in range(3)]
            diff_root += len(set(cnt)) > 1
    print(f"  (a) số lượt mà skip-logic đổi số nghiệm: {lost}/{N_SIDE}  -> {'PASS' if lost == 0 else 'FAIL'}")
    print(f"  (b) Delta>0: {n_pos} lượt; số lượt mà 3 nghiệm cubic cho số nghiệm khác nhau: {diff_root}"
          f"  -> {'PASS' if diff_root == 0 else 'CÓ KHÁC BIỆT'}")


def scene_cylinder(rng, eps):
    """Tâm quang học O ở khoảng cách r(1+eps) tới trục của danger cylinder qua A, B, C (eps=0: nằm trên mặt trụ)."""
    while True:
        n = rng.normal(size=3); n[2] = abs(n[2]) + 1.0; n /= np.linalg.norm(n)
        e1 = np.cross(n, rng.normal(size=3)); e1 /= np.linalg.norm(e1); e2 = np.cross(n, e1)
        r = rng.uniform(0.5, 2.0); k = rng.uniform(3.0, 8.0)
        c = r * (1 + eps) * e1 + k * n  # tâm đường tròn; trục đi qua c, song song n
        th = rng.uniform(0, 2 * np.pi, 3)
        Xc = np.array([c + r * (np.cos(a) * e1 + np.sin(a) * e2) for a in th])
        if np.all(Xc[:, 2] > 0.5):
            # tránh gần thẳng hàng (ba góc quá gần nhau)
            dth = np.sort(np.mod(th, 2 * np.pi)); gaps = np.diff(np.r_[dth, dth[0] + 2 * np.pi])
            if gaps.min() > 0.3:
                break
    R = random_rotation(rng)
    t_true = rng.normal(size=3)  # X_c = R X_w + t
    X = (R.T @ (Xc - t_true).T).T
    uv = Xc[:, :2] / Xc[:, 2:3]
    return X, uv, R, t_true


def scene_collinear(rng, eps):
    """A, B, C: C lệch khỏi đường thẳng AB một khoảng eps * |AB|."""
    while True:
        A = np.r_[rng.uniform(-1, 1, 2), 0] + np.r_[0, 0, rng.uniform(3, 8)]
        B = np.r_[rng.uniform(-1, 1, 2), 0] + np.r_[0, 0, rng.uniform(3, 8)]
        L = np.linalg.norm(B - A)
        if L < 0.5:
            continue
        u = (B - A) / L
        w = np.cross(u, rng.normal(size=3)); w /= np.linalg.norm(w)
        C = A + rng.uniform(0.2, 0.8) * (B - A) + eps * L * w
        Xc = np.array([A, B, C])
        if np.all(Xc[:, 2] > 0.5):
            break
    R = random_rotation(rng); t = rng.normal(size=3)
    X = (R.T @ (Xc - t).T).T
    uv = Xc[:, :2] / Xc[:, 2:3]
    return X, uv, R, t


def ding_robust(X, m):
    """Biến thể của người ghi chú (KHÔNG phải của bài): không bỏ đường thứ hai, chấp nhận tiếp xúc
    (tang_tol), và khi Delta>0 thử cả ba nghiệm cubic (tránh chọn nhầm nghiệm kép cho cặp đường ảo)."""
    info = {}
    sols = ding_p3p(X, m, skip_logic=False, tang_tol=1e-8, info=info)
    if info["Delta"] > 0:
        for k in (1, 2):
            sols += ding_p3p(X, m, root_k=k, skip_logic=False, tang_tol=1e-8)
    return sols


METHODS = {
    "ours": lambda X, uv, m: ding_p3p(X, m),
    "ours+tol": lambda X, uv, m: ding_p3p(X, m, tang_tol=1e-8),
    "ours robust": lambda X, uv, m: ding_robust(X, m),
    "ours+Kabsch": lambda X, uv, m: ding_p3p(X, m, kabsch=True),
    "cv2 P3P": lambda X, uv, m: run_cv(X, uv, cv2.SOLVEPNP_P3P),
    "cv2 AP3P": lambda X, uv, m: run_cv(X, uv, cv2.SOLVEPNP_AP3P),
}


def degenerate_sweep(rng, maker, label, eps_list, thr_list=(1e-6, 1e-3)):
    print(f"[{label}] {N_DEG} lượt mỗi mức eps. Ô = % lượt KHÔNG có nghiệm nào với xi < 1e-6 / < 1e-3; "
          "[med] = median log10 xi của nghiệm tốt nhất (inf nếu >50% lượt mất GT)")
    print(f"  {'eps':>7s} {'med|Dn|':>8s} | " + " | ".join(f"{k:>22s}" for k in METHODS))
    for eps in eps_list:
        fails = {k: np.zeros(len(thr_list)) for k in METHODS}
        best = {k: [] for k in METHODS}
        dn = []
        for _ in range(N_DEG):
            X, uv, R, t = maker(rng, eps)
            m = bearings_from_uv(uv)
            info = {}
            ding_p3p(X, m, info=info)
            dn.append(abs(info["Delta_n"]))
            for k, f in METHODS.items():
                errs = [xi(Ri, ti, R, t) for Ri, ti in f(X, uv, m)]
                errs = [e for e in errs if np.isfinite(e)]
                e = min(errs, default=np.inf)
                best[k].append(e)
                for j, th in enumerate(thr_list):
                    fails[k][j] += not (e < th)
        cells = []
        for k in METHODS:
            med = np.median(np.log10(np.maximum(np.array(best[k]), 1e-17)))
            cells.append(f"{100*fails[k][0]/N_DEG:5.1f}/{100*fails[k][1]/N_DEG:5.1f} [{med:5.1f}]")
        print(f"  {eps:7.0e} {np.median(dn):8.1e} | " + " | ".join(f"{c:>22s}" for c in cells))


def depth_diag(rng):
    print("[7] Chẩn đoán gần thẳng hàng: sai số tương đối của độ sâu d_i (trước eq. (28)) so với sai số pose")
    for eps in (1e-2, 1e-3, 1e-4, 1e-5):
        ed, ep = [], []
        for _ in range(500):
            X, uv, R, t = scene_collinear(rng, eps)
            m = bearings_from_uv(uv)
            info = {}
            sols = ding_p3p(X, m, info=info)
            dtrue = np.linalg.norm((R @ X.T).T + t, axis=1)
            if not sols:
                ed.append(np.inf); ep.append(np.inf); continue
            ed.append(min(np.abs(d - dtrue).max() / dtrue.max() for d in info["depths"]))
            ep.append(min(xi(Ri, ti, R, t) for Ri, ti in sols))
        print(f"  eps={eps:.0e}: median log10 |d-d_gt|/d = {np.median(np.log10(np.maximum(ed,1e-17))):6.1f};"
              f"  median log10 xi = {np.median(np.log10(np.maximum(ep,1e-17))):6.1f}")


if __name__ == "__main__":
    T0 = time.time()
    print(f"OpenCV {cv2.__version__}; numpy {np.__version__}")
    doc = cv2.solveP3P.__doc__ or ""
    print("  docstring cv2.solveP3P nhắc 'Ding' cho SOLVEPNP_P3P:", "Ding" in doc and "Revisiting the P3P" in doc)
    rng = np.random.default_rng(20230625)
    check_identities(rng)
    check_conics_at_gt(rng)
    data, deltas, ours, res = main_benchmark(np.random.default_rng(1))
    check_algorithm_logic(data)
    rng = np.random.default_rng(7)
    print("  (Delta_n = Delta / (4|alpha|^3 + 27 beta^2) ∈ [-1, 1]; cảnh ngẫu nhiên ở [3]: median |Delta_n| = "
          f"{np.median(np.abs(deltas)):.2f})")
    degenerate_sweep(rng, scene_cylinder, "5 danger cylinder", [0, 1e-8, 1e-6, 1e-4, 1e-2, 1e-1])
    degenerate_sweep(rng, scene_collinear, "6 gần thẳng hàng", [1e-1, 1e-2, 1e-3, 1e-4, 1e-6, 1e-8])
    depth_diag(np.random.default_rng(11))
    print(f"Tổng thời gian: {time.time()-T0:.0f}s")
