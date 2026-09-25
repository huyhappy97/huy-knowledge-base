"""Tiện ích dùng chung cho các script kiểm chứng trong khảo sát PnP (cửa (b), learning-rules.md mục 5).

Quy ước ký hiệu của cả khảo sát (dùng thống nhất trong mọi notes/*.md):
  X_w  : điểm 3D trong hệ thế giới, mảng (n, 3)
  R, t : phép biến đổi thế giới -> camera, X_c = R @ X_w + t
  K    : ma trận nội tham số 3x3
  u    : toạ độ pixel (n, 2);  f = K^-1 [u; 1] chuẩn hoá thành tia chiếu (bearing) đơn vị
Chỉ phụ thuộc numpy (và tuỳ chọn cv2 để đối chiếu).
"""
import numpy as np

K_DEFAULT = np.array([[800.0, 0, 320], [0, 800.0, 240], [0, 0, 1]])


def rodrigues(w):
    """so(3) -> SO(3)."""
    w = np.asarray(w, float)
    th = np.linalg.norm(w)
    if th < 1e-12:
        return np.eye(3)
    k = w / th
    Kx = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + np.sin(th) * Kx + (1 - np.cos(th)) * Kx @ Kx


def random_rotation(rng):
    q = rng.normal(size=4)
    q /= np.linalg.norm(q)
    a, b, c, d = q
    return np.array([
        [a*a+b*b-c*c-d*d, 2*(b*c-a*d), 2*(b*d+a*c)],
        [2*(b*c+a*d), a*a-b*b+c*c-d*d, 2*(c*d-a*b)],
        [2*(b*d-a*c), 2*(c*d+a*b), a*a-b*b-c*c+d*d]])


def make_scene(n, rng, K=K_DEFAULT, depth=(4.0, 8.0), planar=False, sigma_px=0.0, img=(640, 480)):
    """Sinh cảnh kiểu thí nghiệm của EPnP: điểm nằm trong hộp trước camera, pose ngẫu nhiên.
    Trả về X_w (n,3), u (n,2) có nhiễu, u_clean, R, t."""
    w, h = img
    # điểm trong hệ camera: pixel đều trên ảnh, độ sâu đều trong khoảng
    uu = np.c_[rng.uniform(0, w, n), rng.uniform(0, h, n)]
    z = rng.uniform(*depth, n)
    if planar:
        # mặt phẳng nghiêng qua tâm vùng độ sâu
        nrm = rng.normal(size=3); nrm[2] = abs(nrm[2]) + 1.0; nrm /= np.linalg.norm(nrm)
        d0 = np.mean(depth)
        rays = (np.linalg.inv(K) @ np.c_[uu, np.ones(n)].T).T
        z = d0 * nrm[2] / (rays @ nrm)  # giao tia với mặt phẳng nrm·X = d0*nrm_z
    X_c = (np.linalg.inv(K) @ np.c_[uu, np.ones(n)].T).T * z[:, None]
    R = random_rotation(rng)
    t = rng.uniform(-1, 1, 3)
    X_w = (R.T @ (X_c - t).T).T
    u_clean = project(X_w, R, t, K)
    u = u_clean + rng.normal(scale=sigma_px, size=u_clean.shape) if sigma_px > 0 else u_clean.copy()
    return X_w, u, u_clean, R, t


def project(X_w, R, t, K=K_DEFAULT):
    X_c = (R @ X_w.T).T + t
    p = (K @ X_c.T).T
    return p[:, :2] / p[:, 2:3]


def bearings(u, K=K_DEFAULT):
    f = (np.linalg.inv(K) @ np.c_[u, np.ones(len(u))].T).T
    return f / np.linalg.norm(f, axis=1, keepdims=True)


def reproj_rmse(X_w, u, R, t, K=K_DEFAULT):
    return float(np.sqrt(np.mean(np.sum((project(X_w, R, t, K) - u) ** 2, axis=1))))


def rot_err_deg(R_est, R_true):
    c = (np.trace(R_est.T @ R_true) - 1) / 2
    return float(np.degrees(np.arccos(np.clip(c, -1, 1))))


def trans_err_rel(t_est, t_true):
    return float(np.linalg.norm(t_est - t_true) / np.linalg.norm(t_true))


def proj_to_so3(M):
    U, _, Vt = np.linalg.svd(M)
    D = np.diag([1, 1, np.sign(np.linalg.det(U @ Vt))])
    return U @ D @ Vt


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    X, u, uc, R, t = make_scene(10, rng)
    assert reproj_rmse(X, uc, R, t) < 1e-9
    assert abs(np.linalg.det(R) - 1) < 1e-12
    Xp, _, ucp, Rp, tp = make_scene(10, rng, planar=True)
    Xc = (Rp @ Xp.T).T + tp
    # kiểm đồng phẳng: hạng của điểm đã trừ trọng tâm là 2
    s = np.linalg.svd(Xc - Xc.mean(0), compute_uv=False)
    assert s[2] < 1e-9 * s[0], s
    print("common.py: tự kiểm ok")
