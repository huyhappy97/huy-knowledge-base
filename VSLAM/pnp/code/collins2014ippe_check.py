"""Kiểm chứng số (cửa (b)) cho collins2014ippe — Infinitesimal Plane-based Pose Estimation.

Chạy:  python3 VSLAM/pnp/code/collins2014ippe_check.py
Cần: numpy, opencv (cv2). Thời gian < 1 phút. Seed cố định.

Các kiểm tra:
  C1  Jacobian của homography tại u0 (eq. (14)) — so công thức in trong bài với sai phân hữu hạn.
  C2  Algorithm 1+2 (eq. (22)-(24), (28), (36)) không nhiễu: một trong hai nghiệm trùng pose thật.
  C3  Quan hệ hình học giữa hai nghiệm (Theorem 4, eq. (27)-(28)): R2 = M R1 D, M = phản xạ qua mặt
      phẳng vuông góc tia nhìn [v;1]; t1 = t2 theo eq. (28); góc giữa R1,R2 = 2*alpha.
  C4  Nghiệm duy nhất khi mặt phẳng vuông góc tia nhìn (Theorem 4) ; Lemma 4 (det J > 0 => cả hai front-facing);
      Theorem 5 (J = 0 <=> H hạng 1).
  C5  Đối chiếu với cv2.solvePnPGeneric(..., SOLVEPNP_IPPE) trên dữ liệu có nhiễu.
  C6  Theorem 6: P3P trên 3 điểm ảo tách nhau eps quanh tâm -> nghiệm hội tụ về hai nghiệm IPPE.
  C7  Quét: tỉ số sai số tái chiếu rho = e2/e1 và tỉ lệ chọn nhầm theo kích thước ảnh, khoảng cách,
      góc nghiêng, vị trí trong ảnh và số điểm n.
  C8  Mô phỏng gần thiết lập §4.1 của bài (f=800, 640x480, d~U(f/2,2f)), quét w như E3/E24.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
import cv2
from common import rodrigues, rot_err_deg, proj_to_so3  # noqa: F401

np.set_printoptions(precision=4, suppress=True)
F = 800.0
K = np.array([[F, 0, 320.0], [0, F, 240.0], [0, 0, 1]])
Kinv = np.linalg.inv(K)
D = np.diag([1.0, 1.0, -1.0])
ALL_OK = []


def report(name, ok, msg=""):
    ALL_OK.append(ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name} {msg}")


# ---------------------------------------------------------------- IPPE (theo bài)
def pi(x):
    return x[:2] / x[2]


def dlt_homography(U, Q):
    """Normalised DLT: U (n,2) mặt phẳng mô hình -> Q (n,2) toạ độ chuẩn hoá. Trả H với H33=1."""
    def norm_T(P):
        c = P.mean(0)
        s = np.sqrt(2) / np.mean(np.linalg.norm(P - c, axis=1))
        return np.array([[s, 0, -s * c[0]], [0, s, -s * c[1]], [0, 0, 1]])
    Tu, Tq = norm_T(U), norm_T(Q)
    Uh = (Tu @ np.c_[U, np.ones(len(U))].T).T
    Qh = (Tq @ np.c_[Q, np.ones(len(Q))].T).T
    A = []
    for (x, y, _), (u, v, _) in zip(Uh, Qh):
        A.append([-x, -y, -1, 0, 0, 0, u * x, u * y, u])
        A.append([0, 0, 0, -x, -y, -1, v * x, v * y, v])
    _, _, Vt = np.linalg.svd(np.asarray(A))
    Hn = Vt[-1].reshape(3, 3)
    H = np.linalg.inv(Tq) @ Hn @ Tu
    return H / H[2, 2]


def ho_homography(U, Q):
    """Harker & O'Leary (tham chiếu [16] của bài) — chép lại từ HomographyHO::homographyHO trong
    opencv/modules/calib3d/src/ippe.cpp (nhánh 4.x) để so sánh cùng bộ ước lượng homography với cv2."""
    def norm_iso(P):
        m = P.mean(0); Pc = P - m
        beta = np.sqrt(2 * len(P) / np.sum(Pc ** 2))
        T = np.array([[1 / beta, 0, m[0]], [0, 1 / beta, m[1]], [0, 0, 1]])
        Ti = np.array([[beta, 0, -beta * m[0]], [0, beta, -beta * m[1]], [0, 0, 1]])
        return (Pc * beta).T, T, Ti
    A, TA, TAi = norm_iso(U)
    Bd, TB, TBi = norm_iso(Q)
    C1, C2 = -Bd[0] * A[0], -Bd[0] * A[1]
    C3, C4 = -Bd[1] * A[0], -Bd[1] * A[1]
    mC = [C1.mean(), C2.mean(), C3.mean(), C4.mean()]
    Mx = np.c_[C1 - mC[0], C2 - mC[1], -Bd[0]]
    My = np.c_[C3 - mC[2], C4 - mC[3], -Bd[1]]
    Pp = np.linalg.inv(A @ A.T) @ A
    Bx, By = Pp @ Mx, Pp @ My
    Dm = np.r_[Mx - A.T @ Bx, My - A.T @ By]
    w_, V = np.linalg.eigh(Dm.T @ Dm)
    h789 = V[:, 0]
    h12, h45 = -Bx @ h789, -By @ h789
    h3 = -(mC[0] * h789[0] + mC[1] * h789[1]); h6 = -(mC[2] * h789[0] + mC[3] * h789[1])
    H = np.array([[h12[0], h12[1], h3], [h45[0], h45[1], h6], h789])
    H = TB @ H @ TAi
    return H / H[2, 2]


def J_paper_eq14(H, u0):
    """Eq. (14) chép nguyên văn như in trong bài (J11 có u_x, J12 có u_y, ...)."""
    ux, uy = u0
    J11 = H[0, 0] - H[2, 0] * H[0, 2] + ux * (H[0, 0] * H[2, 1] - H[2, 0] * H[0, 1])
    J12 = H[0, 1] - H[2, 1] * H[0, 2] + uy * (H[0, 1] * H[2, 0] - H[2, 1] * H[0, 0])
    J21 = H[1, 0] - H[2, 0] * H[1, 2] + ux * (H[1, 0] * H[2, 1] - H[2, 0] * H[1, 1])
    J22 = H[1, 1] - H[2, 1] * H[1, 2] + uy * (H[1, 1] * H[2, 0] - H[2, 1] * H[1, 0])
    return np.array([[J11, J12], [J21, J22]]) / (1 + ux * H[2, 0] + uy * H[2, 1]) ** 2


def J_swapped(H, u0):
    """Đạo hàm tay của pi(H[u;1]): số hạng bậc nhất của J11,J21 đi với u_y, của J12,J22 đi với u_x
    (tức eq. (14) với u_x <-> u_y đổi chỗ trong các số hạng bậc nhất)."""
    ux, uy = u0
    J11 = H[0, 0] - H[2, 0] * H[0, 2] + uy * (H[0, 0] * H[2, 1] - H[2, 0] * H[0, 1])
    J12 = H[0, 1] - H[2, 1] * H[0, 2] + ux * (H[0, 1] * H[2, 0] - H[2, 1] * H[0, 0])
    J21 = H[1, 0] - H[2, 0] * H[1, 2] + uy * (H[1, 0] * H[2, 1] - H[2, 0] * H[1, 1])
    J22 = H[1, 1] - H[2, 1] * H[1, 2] + ux * (H[1, 1] * H[2, 0] - H[2, 1] * H[1, 0])
    return np.array([[J11, J12], [J21, J22]]) / (1 + ux * H[2, 0] + uy * H[2, 1]) ** 2


def J_fd(H, u0, h=1e-6):
    f = lambda u: pi(H @ np.r_[u, 1.0])
    J = np.zeros((2, 2))
    for k in range(2):
        e = np.zeros(2); e[k] = h
        J[:, k] = (f(u0 + e) - f(u0 - e)) / (2 * h)
    return J


def ippe_alg1(v, J, literal22=False):
    """Algorithm 1 (eq. (20)-(24))."""
    t = np.linalg.norm(v)
    if t < 1e-14:
        Rv = np.eye(3)
    else:
        s = np.linalg.norm(np.r_[v, 1.0])
        c, sn = 1 / s, np.sqrt(1 - 1 / s ** 2)
        Kx = np.zeros((3, 3)); Kx[:2, 2] = v / t; Kx[2, :2] = -v / t
        Rv = np.eye(3) + sn * Kx + (1 - c) * Kx @ Kx          # eq. (23)
    B = (np.c_[np.eye(2), -v] @ Rv)[:, :2]                    # [I|-v] Rv = [B|0]
    A = np.linalg.solve(B, J)                                 # eq. (21)
    AAt = A @ A.T
    au, av, aw = AAt[0, 0], AAt[0, 1], AAt[1, 1]
    gamma = 0.5 * (au + aw + np.sqrt((au - aw) ** 2 + 4 * av ** 2))  # eq. (22) — xem ghi chú dưới
    if not literal22:
        gamma = np.sqrt(gamma)  # (22) viết gamma = sigma_1^A; biểu thức trong ngoặc là sigma_1^2 (trị riêng lớn của AA^T)
    R22 = A / gamma
    Bm = np.eye(2) - R22.T @ R22
    ru, rv_, rw = Bm[0, 0], Bm[0, 1], Bm[1, 1]
    b = np.array([np.sqrt(max(ru, 0)), np.sign(rv_) * np.sqrt(max(rw, 0))])  # eq. (24)
    c1 = np.r_[R22[:, 0], b[0]]
    c2 = np.r_[R22[:, 1], b[1]]
    ca = np.cross(c1, c2)                                     # [c; a]
    Rt1 = np.c_[np.r_[R22, b[None]], ca]
    Rt2 = np.c_[np.r_[R22, -b[None]], np.r_[-ca[:2], ca[2]]]
    return gamma, Rv @ Rt1, Rv @ Rt2, Rv


def t_eq36(R, U, Qn):
    """Eq. (36): LS cho t với R cố định, sai số trong không gian camera."""
    W, bvec = [], []
    for u, q in zip(U, Qn):
        X = R @ np.r_[u, 0.0]
        # [X1 + t1 - (X3 + t3) q1 ; X2 + t2 - (X3 + t3) q2] = 0
        W.append([1, 0, -q[0]]); bvec.append(-(X[0] - X[2] * q[0]))
        W.append([0, 1, -q[1]]); bvec.append(-(X[1] - X[2] * q[1]))
    W, bvec = np.asarray(W), np.asarray(bvec)
    return np.linalg.solve(W.T @ W, W.T @ bvec)


def ippe_alg2(U, q_px, t_mode="eq36", hom="dlt"):
    """Algorithm 2. U (n,2) trên mặt phẳng z=0 (sẽ được trừ trọng tâm), q_px (n,2) pixel.
    Trả [(R1,t1),(R2,t2)] trong hệ mô hình GỐC (chưa trừ trọng tâm), cùng (v, J, gamma)."""
    c = U.mean(0)
    Uc = U - c
    Qn = (Kinv @ np.c_[q_px, np.ones(len(q_px))].T).T[:, :2]
    H = dlt_homography(Uc, Qn) if hom == "dlt" else ho_homography(Uc, Qn)
    J = np.array([[H[0, 0] - H[2, 0] * H[0, 2], H[0, 1] - H[2, 1] * H[0, 2]],
                  [H[1, 0] - H[2, 0] * H[1, 2], H[1, 1] - H[2, 1] * H[1, 2]]])
    v = H[:2, 2].copy()
    gamma, R1, R2, Rv = ippe_alg1(v, J)
    out = []
    for R in (R1, R2):
        t = np.r_[v, 1.0] / gamma if t_mode == "eq28" else t_eq36(R, Uc, Qn)   # eq. (28), u0=0
        out.append((R, t - R @ np.r_[c, 0.0]))   # đổi về hệ mô hình gốc
    return out, dict(v=v, J=J, gamma=gamma, Rv=Rv, H=H)


def reproj_rmse(U, q_px, R, t):
    X = (R @ np.c_[U, np.zeros(len(U))].T).T + t
    p = (K @ X.T).T
    return float(np.sqrt(np.mean(np.sum((p[:, :2] / p[:, 2:3] - q_px) ** 2, axis=1))))


def project(U, R, t):
    X = (R @ np.c_[U, np.zeros(len(U))].T).T + t
    p = (K @ X.T).T
    return p[:, :2] / p[:, 2:3]


def cv_ippe(U, q_px):
    obj = np.c_[U, np.zeros(len(U))].astype(np.float64)
    n, rvecs, tvecs, errs = cv2.solvePnPGeneric(obj, q_px.astype(np.float64), K, None,
                                                flags=cv2.SOLVEPNP_IPPE)
    sols = [(cv2.Rodrigues(r)[0], tv.ravel()) for r, tv in zip(rvecs, tvecs)]
    return sols, np.asarray(errs).ravel()


# ---------------------------------------------------------------- sinh cảnh có điều khiển
def rot_axis_angle(axis, ang):
    axis = axis / np.linalg.norm(axis)
    return rodrigues(axis * ang)


def make_pose(rng, Z, tilt_deg, px=None):
    """Tâm mặt phẳng ở độ sâu Z trên tia qua pixel px; pháp tuyến nghiêng tilt_deg so với tia nhìn."""
    if px is None:
        px = np.array([320.0, 240.0])
    l = Kinv @ np.r_[px, 1.0]
    t = Z * l                              # l có z = 1
    ln = l / np.linalg.norm(l)
    # Rv0: e3 -> ln (trục z mô hình hướng ra xa camera: front-facing theo §3.5)
    _, _, _, Rv0 = ippe_alg1(l[:2], np.eye(2))
    th = rng.uniform(0, 2 * np.pi)
    Rz = rodrigues([0, 0, th])
    a = rng.normal(size=3); a -= a.dot(ln) * ln
    R = rot_axis_angle(a, np.radians(tilt_deg)) @ Rv0 @ Rz
    return R, t


def model_points(rng, n, w, corners=True):
    pts = []
    if corners:
        pts = [[w / 2, w / 2], [w / 2, -w / 2], [-w / 2, -w / 2], [-w / 2, w / 2]]
    k = n - len(pts)
    if k > 0:
        pts += list(rng.uniform(-w / 2, w / 2, size=(k, 2)))
    return np.asarray(pts, float)


def ambiguity_stats(rng, trials, n, w, Z, tilt, sigma, px=None, want_lr=False):
    rhos, wrong, lrs = [], 0, []
    for _ in range(trials):
        R, t = make_pose(rng, Z, tilt, px)
        U = model_points(rng, n, w)
        q = project(U, R, t) + rng.normal(scale=sigma, size=(n, 2))
        sols, errs = cv_ippe(U, q)
        e = [reproj_rmse(U, q, *s) for s in sols]
        i_best = int(np.argmin(e))
        rho = max(e) / max(min(e), 1e-12)
        rhos.append(rho)
        lrs.append(n * (max(e) ** 2 - min(e) ** 2) / sigma ** 2)   # 2*log-likelihood ratio (Gauss IID)
        rerr = [rot_err_deg(s[0], R) for s in sols]
        if rerr[i_best] > rerr[1 - i_best]:
            wrong += 1
    if want_lr:
        return np.median(rhos), np.percentile(rhos, 10), wrong / trials, np.median(lrs)
    return np.median(rhos), np.percentile(rhos, 10), wrong / trials


# ================================================================ C1
def check_C1(rng):
    print("\n== C1: Jacobian eq. (14) tại u0 != 0 ==")
    R, t = make_pose(rng, 1000.0, 40.0, np.array([400.0, 300.0]))
    H = np.c_[R[:, 0], R[:, 1], t]; H = H / H[2, 2]
    for u0 in [np.array([0.0, 0.0]), np.array([60.0, -25.0]), np.array([-80.0, 50.0])]:
        Jf = J_fd(H, u0)
        ep = np.abs(J_paper_eq14(H, u0) - Jf).max() / np.abs(Jf).max()
        es = np.abs(J_swapped(H, u0) - Jf).max() / np.abs(Jf).max()
        print(f"  u0={u0}: sai số tương đối  eq.(14) như in = {ep:.2e} | đổi ux<->uy = {es:.2e}")
    report("C1a eq.(14) đúng tại u0=0 (dạng Algorithm 2 dùng)", np.abs(J_paper_eq14(H, np.zeros(2)) - J_fd(H, np.zeros(2))).max() < 1e-8)
    u0 = np.array([60.0, -25.0])
    report("C1b eq.(14) như in SAI tại u0!=0; bản đổi ux<->uy mới khớp sai phân",
           np.abs(J_paper_eq14(H, u0) - J_fd(H, u0)).max() / np.abs(J_fd(H, u0)).max() > 1e-2
           and np.abs(J_swapped(H, u0) - J_fd(H, u0)).max() / np.abs(J_fd(H, u0)).max() < 1e-6)


# ================================================================ C2 + C3
def check_C2_C3(rng):
    print("\n== C2: Algorithm 1+2, không nhiễu ==")
    worst_R, worst_t, worst_g = 0, 0, 0
    for _ in range(200):
        R, t = make_pose(rng, rng.uniform(400, 1600), rng.uniform(0, 70), rng.uniform([50, 50], [590, 430]))
        U = model_points(rng, 8, rng.uniform(50, 300))
        q = project(U, R, t)
        for mode in ("eq28", "eq36"):
            sols, info = ippe_alg2(U, q, mode)
            e = [rot_err_deg(s[0], R) for s in sols]
            i = int(np.argmin(e))
            worst_R = max(worst_R, e[i])
            worst_t = max(worst_t, np.linalg.norm(sols[i][1] - t) / np.linalg.norm(t))
        c = U.mean(0)
        depth_c = (R @ np.r_[c, 0] + t)[2]
        worst_g = max(worst_g, abs(info["gamma"] * depth_c - 1))
    print(f"  200 cảnh: max sai số xoay nghiệm đúng = {worst_R:.2e} deg, max sai số t tương đối = {worst_t:.2e}, "
          f"max |gamma*Z_centroid - 1| = {worst_g:.2e}")
    report("C2 một nghiệm IPPE trùng pose thật; gamma = 1/độ sâu trọng tâm", worst_R < 1e-5 and worst_t < 1e-9 and worst_g < 1e-9)
    # eq. (22) đọc nguyên văn: gamma = 1/2(au+aw+sqrt(...)) — biểu thức đó là sigma_1^2, không phải sigma_1
    R, t = make_pose(rng, 1000.0, 30.0, np.array([300.0, 200.0]))
    U = model_points(rng, 8, 150); U -= U.mean(0)
    _, info = ippe_alg2(U, project(U, R, t), "eq28")
    g_lit, R1l, R2l, _ = ippe_alg1(info["v"], info["J"], literal22=True)
    A = np.linalg.solve((np.c_[np.eye(2), -info["v"]] @ info["Rv"])[:, :2], info["J"])
    s1 = np.linalg.svd(A, compute_uv=False)[0]
    print(f"  sigma_1(A) = {s1:.6e};  biểu thức eq.(22) = {g_lit:.6e} = sigma_1^2 ? {abs(g_lit - s1**2)/s1**2:.1e};"
          f"  1/Z_centroid = {1/(t[2]):.6e}")
    report("C2b biểu thức đóng trong eq.(22) cho sigma_1^2 (phải lấy căn) — lỗi in", abs(g_lit - s1 ** 2) / s1 ** 2 < 1e-12 and abs(s1 * t[2] - 1) < 1e-9)

    print("\n== C3: quan hệ giữa hai nghiệm (Theorem 4, eq. (27)-(28)), dữ liệu CÓ nhiễu sigma=1px ==")
    res_refl, res_t28, res_ang, res_pts = 0, 0, 0, 0
    for _ in range(200):
        R, t = make_pose(rng, rng.uniform(400, 1600), rng.uniform(0, 70), rng.uniform([50, 50], [590, 430]))
        U = model_points(rng, 10, rng.uniform(50, 300))
        q = project(U, R, t) + rng.normal(size=(10, 2))
        sols, info = ippe_alg2(U, q, "eq28")
        (R1, t1), (R2, t2) = sols
        l = np.r_[info["v"], 1.0]; l /= np.linalg.norm(l)
        M = np.eye(3) - 2 * np.outer(l, l)        # phản xạ qua mặt phẳng vuông góc tia nhìn
        res_refl = max(res_refl, np.abs(R2 - M @ R1 @ D).max())
        c = U.mean(0)
        x1 = R1 @ np.r_[c, 0] + t1; x2 = R2 @ np.r_[c, 0] + t2
        res_t28 = max(res_t28, np.linalg.norm(x1 - x2) / np.linalg.norm(x1))
        alpha = np.degrees(np.arccos(np.clip(abs(l @ R1[:, 2]), -1, 1)))
        res_ang = max(res_ang, abs(rot_err_deg(R1, R2) - 2 * alpha))
        # mọi điểm mô hình: X2 = x0 + M (X1 - x0)
        X1 = (R1 @ np.c_[U, np.zeros(10)].T).T + t1
        X2 = (R2 @ np.c_[U, np.zeros(10)].T).T + t2
        res_pts = max(res_pts, np.abs(X2 - (x1 + (M @ (X1 - x1).T).T)).max() / np.linalg.norm(x1))
    print(f"  max|R2 - M R1 diag(1,1,-1)| = {res_refl:.2e};  max ||x0_1 - x0_2||/||x0|| (eq.28) = {res_t28:.2e}")
    print(f"  max |angle(R1,R2) - 2*alpha| = {res_ang:.2e} deg;  max lệch điểm 3D so với phản xạ = {res_pts:.2e}")
    report("C3 hai nghiệm = phản xạ qua mặt phẳng qua x0, pháp tuyến dọc tia nhìn; góc giữa hai xoay = 2*alpha",
           res_refl < 1e-9 and res_t28 < 1e-12 and res_ang < 1e-6 and res_pts < 1e-9)


# ================================================================ C4
def check_C4(rng):
    print("\n== C4: nghiệm duy nhất / front-facing / suy biến ==")
    # mặt phẳng vuông góc tia nhìn qua trọng tâm (tilt = 0), tâm lệch khỏi trục quang
    R, t = make_pose(rng, 800.0, 0.0, np.array([520.0, 100.0]))
    U = model_points(rng, 6, 200)
    U -= U.mean(0)
    sols, info = ippe_alg2(U, project(U, R, t), "eq28")
    d = rot_err_deg(sols[0][0], sols[1][0])
    print(f"  tilt=0 so với tia nhìn tại pixel (520,100): angle(R1,R2) = {d:.2e} deg")
    report("C4a tilt=0 so với tia nhìn (không phải so với trục quang) => R1 = R2", d < 1e-5)
    R, t = make_pose(rng, 800.0, 0.0, np.array([520.0, 100.0]))
    Rfp = np.eye(3)  # fronto-parallel theo TRỤC QUANG, nhưng tâm lệch khỏi trục
    sols, info = ippe_alg2(U, project(U, Rfp, t), "eq28")
    d2 = rot_err_deg(sols[0][0], sols[1][0])
    print(f"  mặt phẳng song song mặt ảnh (vuông góc TRỤC QUANG), tâm ở pixel (520,100): angle(R1,R2) = {d2:.2f} deg")
    report("C4b fronto-parallel theo trục quang nhưng lệch tâm => vẫn có 2 nghiệm khác nhau", d2 > 1.0)
    # Lemma 4 / front-facing
    ok = True; nneg = 0
    for _ in range(300):
        R, t = make_pose(rng, 800.0, rng.uniform(0, 85), rng.uniform([50, 50], [590, 430]))
        U = model_points(rng, 8, 200)
        q = project(U, R, t) + rng.normal(scale=0.5, size=(8, 2))
        sols, info = ippe_alg2(U, q, "eq28")
        l = np.r_[info["v"], 1.0]
        ff = [l @ s[0][:, 2] >= 0 for s in sols]
        if np.linalg.det(info["J"]) > 0:
            ok &= all(ff)
        else:
            nneg += 1
            ok &= not any(ff)
    print(f"  300 cảnh front-facing: số ca det(J)<0 = {nneg}; mọi ca det(J)>0 đều có cả hai nghiệm front-facing = {ok}")
    report("C4c Lemma 4: det(J)>0 => cả hai nghiệm front-facing (không dùng để phân xử được)", ok)
    a = np.r_[rng.normal(size=2), 1.0]; b = np.r_[rng.normal(size=2), 1.0]
    H1 = np.outer(a, b)
    J0 = np.array([[H1[0, 0] - H1[2, 0] * H1[0, 2], H1[0, 1] - H1[2, 1] * H1[0, 2]],
                   [H1[1, 0] - H1[2, 0] * H1[1, 2], H1[1, 1] - H1[2, 1] * H1[1, 2]]])
    print(f"  H = [H13 H23 1]^T [H31 H32 1] (không đối xứng): |J(0)| = {np.abs(J0).max():.1e}")
    report("C4d Theorem 5: H hạng 1 dạng a b^T (a3=b3=1) cho J=0 — không cần dạng đối xứng như in", np.abs(J0).max() < 1e-12)


# ================================================================ C5
def check_C5(rng):
    print("\n== C5: đối chiếu cv2.solvePnPGeneric(SOLVEPNP_IPPE) (cv2 %s) ==" % cv2.__version__)
    dR_dlt, dR_ho, dt28, dt36, derr, asym, dnrm = [], [], [], [], [], [], []
    for _ in range(300):
        R, t = make_pose(rng, rng.uniform(400, 1600), rng.uniform(0, 70), rng.uniform([50, 50], [590, 430]))
        n = int(rng.integers(4, 30))
        U = model_points(rng, n, rng.uniform(50, 300), corners=bool(rng.integers(0, 2)))
        q = project(U, R, t) + rng.normal(scale=1.0, size=(n, 2))
        cvs, cverr = cv_ippe(U, q)
        mine_dlt, _ = ippe_alg2(U, q, "eq36", "dlt")
        mine28, info = ippe_alg2(U, q, "eq28", "ho")
        mine36, _ = ippe_alg2(U, q, "eq36", "ho")
        for (Rc, tc) in cvs:
            j = int(np.argmin([rot_err_deg(Rc, m[0]) for m in mine36]))
            dR_ho.append(rot_err_deg(Rc, mine36[j][0]))
            dR_dlt.append(min(rot_err_deg(Rc, m[0]) for m in mine_dlt))
            dt28.append(np.linalg.norm(tc - mine28[j][1]) / np.linalg.norm(tc))
            dt36.append(np.linalg.norm(tc - mine36[j][1]) / np.linalg.norm(tc))
        derr.append(abs(cverr[0] - reproj_rmse(U, q, *cvs[0]) / np.sqrt(2)))
        # quan hệ phản xạ trên chính đầu ra OpenCV
        (R1, _), (R2, _) = cvs
        Mc = R2 @ D @ R1.T
        asym.append(np.abs(Mc - Mc.T).max())
        l = np.r_[info["v"], 1.0]; l /= np.linalg.norm(l)
        dnrm.append(np.abs(Mc - (np.eye(3) - 2 * np.outer(l, l))).max())
    print(f"  300 bài (n=4..29, sigma=1px, u0 = trọng tâm):")
    print(f"   góc lệch xoay cv2 vs Algorithm 1 + DLT chuẩn hoá : median {np.median(dR_dlt):.2e}, max {np.max(dR_dlt):.2e} deg")
    print(f"   góc lệch xoay cv2 vs Algorithm 1 + Harker-O'Leary: median {np.median(dR_ho):.2e}, max {np.max(dR_ho):.2e} deg")
    print(f"   lệch t tương đối (HO): vs t eq.(28) median {np.median(dt28):.2e} max {np.max(dt28):.2e} | "
          f"vs t eq.(36) median {np.median(dt36):.2e} max {np.max(dt36):.2e}")
    print(f"   cv2 reprojectionError = RMSE_pixel/sqrt(2) (RMS mỗi toạ độ)? max chênh = {np.max(derr):.2e}")
    print(f"   trên đầu ra cv2: max|R2 D R1^T - (R2 D R1^T)^T| = {np.max(asym):.2e}; "
          f"max|R2 D R1^T - (I - 2 l l^T)| với l = [v;1] từ H của HO = {np.max(dnrm):.2e}")
    report("C5a xoay cv2 = Algorithm 1 khi dùng cùng homography HO (khác DLT chỉ do bộ ước lượng H)", np.max(dR_ho) < 1e-5)  # ~1e-6 deg là giới hạn phân giải của arccos gần 0
    report("C5b t của cv2 = eq.(36), không phải eq.(28)", np.max(dt36) < 1e-9 and np.median(dt28) > 1e-4)
    report("C5c quan hệ phản xạ đúng trên chính đầu ra cv2", np.max(asym) < 1e-9 and np.max(dnrm) < 1e-6)
    report("C5d cv2 reprojectionError = RMSE/sqrt(2)", np.max(derr) < 1e-5)


# ================================================================ C6
def check_C6(rng):
    print("\n== C6: Theorem 6 — P3P trên 3 điểm ảo tách nhau eps quanh trọng tâm ==")
    R, t = make_pose(rng, 900.0, 35.0, np.array([380.0, 200.0]))
    U = model_points(rng, 12, 200)
    U -= U.mean(0)
    q = project(U, R, t) + rng.normal(scale=1.5, size=(12, 2))
    sols, info = ippe_alg2(U, q, "eq28")
    H = info["H"]
    rows = []
    for eps in [100.0, 30.0, 10.0, 1.0, 0.1]:
        Uv = np.array([[0, 0], [eps, 0], [0, eps]], float)
        qv = np.array([K[:2, :2] @ pi(H @ np.r_[u, 1]) + K[:2, 2] for u in Uv])
        nsol, rv, tv = cv2.solveP3P(np.c_[Uv, np.zeros(3)], qv, K, None, flags=cv2.SOLVEPNP_P3P)
        Rs = [cv2.Rodrigues(r)[0] for r in rv]
        dmin = [min(rot_err_deg(Rp, s[0]) for Rp in Rs) if Rs else np.nan for s in sols]
        rows.append((eps, nsol, dmin))
        print(f"  eps={eps:6.1f}: P3P trả {nsol} nghiệm; khoảng cách tới R1_IPPE = {dmin[0]:.3e} deg, tới R2_IPPE = {dmin[1]:.3e} deg")
    report("C6 khi eps->0, P3P có nghiệm hội tụ về CẢ HAI nghiệm IPPE", max(rows[-1][2]) < 1e-2 and max(rows[0][2]) > max(rows[-1][2]))


# ================================================================ C7
def check_C7(rng):
    print("\n== C7: tỉ số rho = e_sai/e_đúng (RMSE px, cv2 IPPE) — median, p10, tỉ lệ chọn nhầm ==")
    T = 300
    sig = 1.0
    print(f"  (sigma={sig}px, n=4 góc vuông, mặc định: Z=1000, tilt=20deg, tâm ảnh, {T} lần/ô; cạnh ảnh ~ f*w/Z)")
    print("  -- theo kích thước w (Z=1000):")
    for w in [400, 200, 100, 50, 25]:
        m, p10, wr = ambiguity_stats(rng, T, 4, w, 1000.0, 20.0, sig)
        print(f"     w={w:4d} (~{F*w/1000:5.0f}px): rho median {m:8.2f}  p10 {p10:7.2f}  chọn nhầm {wr*100:5.1f}%")
    print("  -- theo khoảng cách Z (w=100):")
    for Z in [400, 800, 1600, 3200]:
        m, p10, wr = ambiguity_stats(rng, T, 4, 100, Z, 20.0, sig)
        print(f"     Z={Z:5d} (~{F*100/Z:5.0f}px): rho median {m:8.2f}  p10 {p10:7.2f}  chọn nhầm {wr*100:5.1f}%")
    print("  -- theo góc nghiêng so với tia nhìn (w=100, Z=1000):")
    for tilt in [60, 40, 20, 10, 5, 2]:
        m, p10, wr = ambiguity_stats(rng, T, 4, 100, 1000.0, tilt, sig)
        print(f"     tilt={tilt:3d}deg: rho median {m:8.2f}  p10 {p10:7.2f}  chọn nhầm {wr*100:5.1f}%")
    print("  -- theo vị trí tâm trong ảnh (w=100, Z=1000, tilt=20):")
    for px in [(320, 240), (520, 240), (620, 460)]:
        m, p10, wr = ambiguity_stats(rng, T, 4, 100, 1000.0, 20.0, sig, np.array(px, float))
        print(f"     pixel {px}: rho median {m:8.2f}  p10 {p10:7.2f}  chọn nhầm {wr*100:5.1f}%")
    print("  -- theo số điểm n đồng phẳng (w=100, Z=1000, tilt=20; 4 góc + điểm đều):")
    res_n = []
    for n in [4, 8, 16, 64]:
        m, p10, wr, lr = ambiguity_stats(rng, T, n, 100, 1000.0, 20.0, sig, want_lr=True)
        res_n.append((n, m, wr))
        print(f"     n={n:3d}: rho median {m:8.2f}  p10 {p10:7.2f}  chọn nhầm {wr*100:5.1f}%  "
              f"median n(e2^2-e1^2)/sigma^2 = {lr:7.1f}")
    return res_n


# ================================================================ C8
def paper_pose(rng, w, n):
    """Theo §4.1: pixel đều trên ảnh, d ~ U(f/2, 2f), t = d*[p~;1], R = R(psi,q) R(theta), tilt < 80 deg."""
    while True:
        p = rng.uniform([0, 0], [640, 480])
        l = Kinv @ np.r_[p, 1.0]
        d = rng.uniform(F / 2, 2 * F)
        t = d * l
        th = rng.uniform(0, 2 * np.pi)
        qx, qy = rng.uniform(-1, 1, 2)
        psi = rng.uniform(0, np.radians(80))
        R = rodrigues(np.array([qx, qy, 0]) / np.hypot(qx, qy) * psi) @ rodrigues([0, 0, th])
        ln = l / np.linalg.norm(l)
        if np.degrees(np.arccos(abs(ln @ R[:, 2]))) >= 80:
            continue
        U = model_points(rng, n, w, corners=True)
        X = (R @ np.c_[U, np.zeros(n)].T).T + t
        if np.any(X[:, 2] <= 0):
            continue
        qq = project(U, R, t)
        if np.any(qq < 0) or np.any(qq[:, 0] > 640) or np.any(qq[:, 1] > 480):
            continue
        return R, t, U, qq


def check_C8(rng):
    print("\n== C8: mô phỏng theo §4.1 của bài (4 góc + điểm đều, sigma_I=1px, n=6, Mode 2 kiểu 'lấy nghiệm gần GT') ==")
    T = 400
    for w in [400, 200, 100, 50]:
        rhos, wrong, e_best, e_ml = [], 0, [], []
        for _ in range(T):
            R, t, U, q0 = paper_pose(rng, w, 6)
            q = q0 + rng.normal(size=q0.shape)
            sols, _ = cv_ippe(U, q)
            e = [reproj_rmse(U, q, *s) for s in sols]
            rerr = [rot_err_deg(s[0], R) for s in sols]
            i = int(np.argmin(e))
            rhos.append(max(e) / min(e))
            wrong += rerr[i] > rerr[1 - i]
            e_best.append(min(rerr)); e_ml.append(rerr[i])
        print(f"  w={w:3d}: rho median {np.median(rhos):7.2f} | chọn nhầm {100*wrong/T:5.1f}% | "
              f"RE nghiệm gần GT (Mode 2) median {np.median(e_best):5.2f} deg | RE nghiệm e nhỏ nhất (Mode 1 không lọc) median {np.median(e_ml):5.2f}, mean {np.mean(e_ml):5.2f} deg")


if __name__ == "__main__":
    rng = np.random.default_rng(20140725)
    check_C1(rng)
    check_C2_C3(rng)
    check_C4(rng)
    check_C5(rng)
    check_C6(rng)
    res_n = check_C7(rng)
    check_C8(rng)
    print(f"\nTổng: {sum(ALL_OK)}/{len(ALL_OK)} PASS")
