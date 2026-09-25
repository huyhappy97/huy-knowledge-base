"""Kiểm chứng cửa (b) cho vakhitov2021uncertainty (CVPR 2021) — phần ĐIỂM.

Phần 1: kiểm công thức.
  C1  eq. (4): covariance của residual đại số r = x̂(1:2) - u x̂(3) (Monte Carlo, bậc một).
  C2  eq. (13) là trường hợp riêng của eq. (4) khi Σx = σ²I, x̂(3) = d̄.
  C3  eq. (21): covariance của residual tái chiếu u - π(Rx+t) (Monte Carlo, bậc một).
  C4  §3.6: σ² = trace(Σx)/3 cực tiểu ||Σx - σ²I||_F.
Phần 2: thí nghiệm — nhiễu 3D đáng kể, không đẳng hướng.
  Bộ giải tuyến tính kiểu EPnP (vector null N=1 + Procrustes có tỉ lệ), 4 cách đặt trọng số:
    L0    không trọng số
    L2D   chỉ 2D: Σr = d̄² Σu              (kiểu CEPPnP)
    LU    eq. (13): σx² I + d̄² Σu + σx² u uᵀ (EPnPU: d̄, Σx đẳng hướng)
    LUz*  như LU nhưng độ sâu từng điểm lấy từ pose giả thuyết (= nghiệm L0), Σx vẫn đẳng hướng
          (đúng mô tả EPnPU* ở §3.3)
    LU*   eq. (4) với pose giả thuyết = nghiệm L0, Σx đầy đủ (theo mô tả §3.2)
  Tinh chỉnh Gauss-Newton trên sai số tái chiếu, cùng khởi tạo L0, 10 vòng:
    G0    không trọng số
    G2D   Σ = Σu                       ("standard refinement")
    GUiso eq. (21) với Σx ≈ trace/3 I, cập nhật mỗi vòng (IRLS)
    GU    eq. (21) Σx đầy đủ, cập nhật mỗi vòng (IRLS) ("uncertain refinement")
    GUgt  eq. (21) Σx đầy đủ, đánh giá cố định tại pose thật (oracle — nơi đánh giá covariance)
Chạy:  python3 VSLAM/pnp/code/vakhitov2021uncertainty_check.py
Mọi toạ độ ảnh trong bộ giải là toạ độ chuẩn hoá (K = I như bài, §3.1); nhiễu pixel chia cho f.
"""
import os
import sys
import time

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")  # tránh tranh chấp luồng BLAS với ma trận nhỏ

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from common import K_DEFAULT, make_scene, random_rotation, rodrigues, rot_err_deg  # noqa: E402

F = K_DEFAULT[0, 0]
C = K_DEFAULT[:2, 2]


def skew(v):
    return np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])


def aniso_cov(sig, rng):
    """Như bài §4.1: bộ ba {σ, σ1, σ2}, σ1,σ2 ~ U(0, σ], xoay ngẫu nhiên."""
    s = np.array([sig, rng.uniform(1e-6, sig), rng.uniform(1e-6, sig)])
    Q = random_rotation(rng)
    return Q @ np.diag(s ** 2) @ Q.T


def eq4(Sx_cam, u, z):
    """eq. (4): Σr = S + γ u uᵀ + z² Σu - (u wᵀ + w uᵀ); trả phần 3D, phần 2D nhân riêng."""
    S = Sx_cam[:2, :2]; w = Sx_cam[:2, 2]; g = Sx_cam[2, 2]
    return S + g * np.outer(u, u) - (np.outer(u, w) + np.outer(w, u)), z ** 2


def jpi(xh):
    x, y, z = xh
    return np.array([[1 / z, 0, -x / z ** 2], [0, 1 / z, -y / z ** 2]])


# ------------------------------------------------------------------ phần 1
def formula_checks(rng):
    print("== Phần 1: kiểm công thức ==")
    R = random_rotation(rng); t = np.array([0.2, -0.1, 0.3])
    X = np.array([0.7, -0.4, 5.5])
    xb = R @ X + t
    ub = xb[:2] / xb[2]
    ok_all = True
    for label, s3, spx in [("nhiễu nhỏ (σ3D=0.02, σ2D=2px)", 0.02, 2.0),
                           ("nhiễu lớn (σ3D=0.5, σ2D=10px)", 0.5, 10.0)]:
        Sx = aniso_cov(s3, rng)
        Su = (spx / F) ** 2 * np.diag([1.0, 0.6])
        N = 400_000
        xi = rng.multivariate_normal(np.zeros(3), Sx, N)
        ze = rng.multivariate_normal(np.zeros(2), Su, N)
        xh = (R @ (X + xi).T).T + t
        um = ub + ze
        r = xh[:, :2] - um * xh[:, 2:3]
        emp = np.cov(r.T)
        A, z2 = eq4(R @ Sx @ R.T, ub, xb[2])
        pred = A + z2 * Su
        g = (R @ Sx @ R.T)[2, 2]
        pred2 = pred + g * Su  # thêm số hạng bậc hai ξ3·ζ mà eq. (4) bỏ
        e1 = np.linalg.norm(emp - pred) / np.linalg.norm(emp)
        e2 = np.linalg.norm(emp - pred2) / np.linalg.norm(emp)
        # MC sai số thống kê ~ sqrt(2/N) ≈ 0.2%
        ok = e1 < 0.02
        ok_all &= ok
        print(f"C1 eq.(4) {label}: sai lệch tương đối |emp-pred|/|emp| = {e1:.4f}; "
              f"thêm γΣu -> {e2:.4f}  [{'PASS' if ok else 'FAIL'} ngưỡng 2%]")
        # eq. (21)
        e = um - xh[:, :2] / xh[:, 2:3]
        emp21 = np.cov(e.T)
        J = jpi(xb)
        pred21 = Su + J @ R @ Sx @ R.T @ J.T
        e21 = np.linalg.norm(emp21 - pred21) / np.linalg.norm(emp21)
        ok = e21 < 0.02 if s3 < 0.1 else True
        ok_all &= ok
        print(f"C3 eq.(21) {label}: sai lệch tương đối = {e21:.4f}  "
              f"[{'PASS' if ok else 'FAIL'}{' (chỉ báo, bậc một không kỳ vọng đúng)' if s3 >= 0.1 else ' ngưỡng 2%'}]")
    # C2
    s2 = 0.03 ** 2; dbar = 6.0; Su = (3 / F) ** 2 * np.eye(2); u = np.array([0.1, -0.2])
    A, _ = eq4(R @ (s2 * np.eye(3)) @ R.T, u, dbar)
    p4 = A + dbar ** 2 * Su
    p13 = s2 * np.eye(2) + dbar ** 2 * Su + s2 * np.outer(u, u)
    ok = np.allclose(p4, p13, rtol=1e-12, atol=1e-18)
    ok_all &= ok
    print(f"C2 eq.(13) == eq.(4) với Σx=σ²I, z=d̄: max|diff| = {np.abs(p4 - p13).max():.2e}  [{'PASS' if ok else 'FAIL'}]")
    # C4
    Sx = aniso_cov(0.3, rng)
    s_opt = np.trace(Sx) / 3
    grid = np.linspace(0, 2 * s_opt, 20001)
    fro = [np.linalg.norm(Sx - s * np.eye(3)) for s in grid]
    s_num = grid[int(np.argmin(fro))]
    ok = abs(s_num - s_opt) < 2 * (grid[1] - grid[0])
    ok_all &= ok
    print(f"C4 §3.6 σ²=tr/3: giải tích {s_opt:.6f}, lưới {s_num:.6f}  [{'PASS' if ok else 'FAIL'}]")
    return ok_all


# ------------------------------------------------------------------ bộ giải
def umeyama(A, B):
    """Tìm s,R,t: s*A ≈ R B + t  (A: điểm camera ước lượng, B: điểm thế giới)."""
    ma, mb = A.mean(0), B.mean(0)
    Ac, Bc = A - ma, B - mb
    H = Bc.T @ Ac
    U, _, Vt = np.linalg.svd(H)
    D = np.diag([1, 1, np.sign(np.linalg.det(Vt.T @ U.T))])
    R = Vt.T @ D @ U.T                    # R Bc ≈ s Ac
    s = np.sum(Bc * (Ac @ R)) / np.sum(Ac * Ac)
    t = s * ma - R @ mb
    return R, t


def linear_solve(Xw, un, Sr=None):
    """EPnP-like: x̂ = P [X;1] (12 ẩn, tương đương vector null N=1 của EPnP), residual đại số (1),
    trọng số làm trắng Σr^{-1/2}, rồi Procrustes có tỉ lệ để về SO(3)."""
    n = len(Xw)
    mu = Xw.mean(0)
    Xh = np.c_[Xw - mu, np.ones(n)]
    M = np.zeros((2 * n, 12))
    for k in range(2):
        M[k::2, 4 * k:4 * k + 4] = Xh
        M[k::2, 8:12] = -un[:, k:k + 1] * Xh
    if Sr is not None:
        L = np.linalg.cholesky(np.linalg.inv(Sr))  # Σ^{-1} = L Lᵀ ; hàng làm trắng = Lᵀ
        Mb = M.reshape(n, 2, 12)
        M = np.einsum('nji,njk->nik', L, Mb).reshape(2 * n, 12)
    v = np.linalg.svd(M)[2][-1]
    P = v.reshape(3, 4)
    xh = Xh @ P.T
    if np.mean(xh[:, 2]) < 0:
        xh = -xh
    R, t = umeyama(xh, Xw - mu)
    t = t - R @ mu
    return R, t


def gn_refine(Xw, un, R, t, Su, Sx=None, mode="none", Rgt=None, tgt=None, iters=10):
    R = R.copy(); t = t.copy()
    n = len(Xw)
    Wfix = None
    if mode == "gt":
        xg = (Rgt @ Xw.T).T + tgt
        Wfix = np.array([np.linalg.inv(Su[i] + jpi(xg[i]) @ Rgt @ Sx[i] @ Rgt.T @ jpi(xg[i]).T) for i in range(n)])
    for _ in range(iters):
        RX = (R @ Xw.T).T
        xh = RX + t
        e = xh[:, :2] / xh[:, 2:3] - un
        z = xh[:, 2]
        J = np.zeros((n, 2, 3))
        J[:, 0, 0] = 1 / z; J[:, 1, 1] = 1 / z
        J[:, 0, 2] = -xh[:, 0] / z ** 2; J[:, 1, 2] = -xh[:, 1] / z ** 2
        if mode == "none":
            W = np.broadcast_to(np.eye(2), (n, 2, 2))
        elif mode == "2d":
            W = np.linalg.inv(Su)
        elif mode in ("full", "iso"):
            Sxc = np.einsum('ij,njk,lk->nil', R, Sx, R) if mode == "full" else \
                (np.trace(Sx, axis1=1, axis2=2) / 3)[:, None, None] * np.eye(3)
            W = np.linalg.inv(Su + np.einsum('nij,njk,nlk->nil', J, Sxc, J))
        else:
            W = Wfix
        Sk = np.array([skew(v) for v in RX])
        H = np.concatenate([np.einsum('nij,njk->nik', J, -Sk), J], axis=2)  # (n,2,6)
        A = np.einsum('nji,njk,nkl->il', H, W, H)
        b = np.einsum('nji,njk,nk->i', H, W, e)
        d = -np.linalg.solve(A, b)
        R = rodrigues(d[:3]) @ R
        t = t + d[3:]
    return R, t


# ------------------------------------------------------------------ phần 2
def make_trial(rng, n, cond):
    Xw, _, u_clean, R, t = make_scene(n, rng, depth=(4.0, 8.0))
    Xc = (R @ Xw.T).T + t
    grp = np.arange(n) * 10 // n            # 10 nhóm bằng nhau như §4.1
    if cond["px"] == "groups":
        spx = np.linspace(1, 10, 10)[rng.permutation(grp)]
    else:
        spx = np.full(n, cond["px"])
    Su = np.array([(s / F) ** 2 * np.eye(2) for s in spx])
    kind = cond["x3"]
    if kind == "none":
        Sx = np.zeros((n, 3, 3)) + 1e-12 * np.eye(3)
    elif kind in ("groups", "groups_corr", "mild"):
        lo, hi = (0.05, 0.5) if kind != "mild" else (0.005, 0.05)
        g = grp if kind == "groups_corr" else rng.permutation(grp)
        if kind == "groups_corr":  # cùng chỉ số nhóm với nhiễu 2D
            spx = np.linspace(1, 10, 10)[grp]
            Su = np.array([(s / F) ** 2 * np.eye(2) for s in spx])
        s3 = np.linspace(lo, hi, 10)[g]
        Sx = np.array([aniso_cov(s, rng) for s in s3])
    elif kind == "homog":
        Sx = np.array([cond["s3"] ** 2 * np.eye(3) for _ in range(n)])
    elif kind == "stereo":
        # covariance kéo dài theo tia từ một camera tham chiếu cách 2 m (triangulation kiểu stereo)
        cq = -R.T @ t
        off = rng.normal(size=3); off /= np.linalg.norm(off)
        cref = cq + 2.0 * off
        Sx = []
        for X in Xw:
            d = X - cref; dist = np.linalg.norm(d); d /= dist
            sa = cond["k"] * dist ** 2; sp = 0.005
            Sx.append(sa ** 2 * np.outer(d, d) + sp ** 2 * (np.eye(3) - np.outer(d, d)))
        Sx = np.array(Sx)
    Xn = Xw + np.array([rng.multivariate_normal(np.zeros(3), S) for S in Sx])
    un_clean = (u_clean - C) / F
    un = un_clean + np.array([rng.multivariate_normal(np.zeros(2), S) for S in Su])
    dbar = Xc[:, 2].mean()
    return Xn, un, R, t, Su, Sx, dbar


def run_condition(name, cond, rng, trials=200, n=50):
    methods = ["L0", "L2D", "LU", "LUz*", "LU*", "G0", "G2D", "GUiso", "GU", "GUgt"]
    er = {m: [] for m in methods}; et = {m: [] for m in methods}
    for _ in range(trials):
        Xn, un, Rg, tg, Su, Sx, dbar = make_trial(rng, n, cond)
        out = {}
        out["L0"] = linear_solve(Xn, un)
        out["L2D"] = linear_solve(Xn, un, dbar ** 2 * Su)
        s2 = np.trace(Sx, axis1=1, axis2=2) / 3
        S13 = s2[:, None, None] * np.eye(2) + dbar ** 2 * Su + s2[:, None, None] * np.einsum('ni,nj->nij', un, un)
        out["LU"] = linear_solve(Xn, un, S13)
        Rh, th = out["L0"]
        zh = ((Rh @ Xn.T).T + th)[:, 2]
        S4 = []
        for i in range(n):
            A, z2 = eq4(Rh @ Sx[i] @ Rh.T, un[i], zh[i])
            S4.append(A + z2 * Su[i])
        out["LU*"] = linear_solve(Xn, un, np.array(S4))
        # đúng chữ §3.3: vẫn Σx đẳng hướng, chỉ lấy độ sâu từng điểm từ pose giả thuyết
        Sz = s2[:, None, None] * np.eye(2) + zh[:, None, None] ** 2 * Su + s2[:, None, None] * np.einsum('ni,nj->nij', un, un)
        out["LUz*"] = linear_solve(Xn, un, Sz)
        R0, t0 = out["L0"]
        out["G0"] = gn_refine(Xn, un, R0, t0, Su, Sx, "none")
        out["G2D"] = gn_refine(Xn, un, R0, t0, Su, Sx, "2d")
        out["GUiso"] = gn_refine(Xn, un, R0, t0, Su, Sx, "iso")
        out["GU"] = gn_refine(Xn, un, R0, t0, Su, Sx, "full")
        out["GUgt"] = gn_refine(Xn, un, R0, t0, Su, Sx, "gt", Rg, tg)
        for m in methods:
            er[m].append(rot_err_deg(out[m][0], Rg)); et[m].append(float(np.linalg.norm(out[m][1] - tg)))
    print(f"\n-- {name}  ({trials} lần thử, n={n}) --")
    print(f"{'method':7s} {'medRot°':>8s} {'meanRot°':>9s} {'medT':>7s} {'meanT':>7s}")
    res = {}
    for m in methods:
        r = np.array(er[m]); tt = np.array(et[m])
        res[m] = (np.median(r), np.mean(r), np.median(tt), np.mean(tt))
        print(f"{m:7s} {res[m][0]:8.3f} {res[m][1]:9.3f} {res[m][2]:7.3f} {res[m][3]:7.3f}")
    return res


def main():
    t0 = time.time()
    rng = np.random.default_rng(20210619)
    ok = formula_checks(rng)
    print("\n== Phần 2: thí nghiệm (sai số xoay: độ; sai số tịnh tiến: ||t_est - t||, cùng đơn vị với cảnh, độ sâu 4..8) ==")
    conds = [
        ("A. chỉ nhiễu 2D (σpx 1..10 theo nhóm), không nhiễu 3D", dict(px="groups", x3="none")),
        ("B. như bài: 2D 1..10 px + 3D không đẳng hướng 0.05..0.5 (nhóm độc lập)", dict(px="groups", x3="groups")),
        ("B'. như B nhưng nhóm 2D và 3D trùng chỉ số (tương quan)", dict(px="groups", x3="groups_corr")),
        ("C. 3D nhẹ: 2D 1..10 px + 3D 0.005..0.05", dict(px="groups", x3="mild")),
        ("D. kiểu stereo: 2D 1 px, 3D kéo dài theo tia camera tham chiếu, σ∥=0.004·dist²", dict(px=1.0, x3="stereo", k=0.004)),
        ("E. đồng nhất: 2D 2 px mọi điểm, 3D đẳng hướng 0.02 mọi điểm", dict(px=2.0, x3="homog", s3=0.02)),
    ]
    allres = {}
    for name, c in conds:
        allres[name[:2].strip(". ")] = run_condition(name, c, rng)
    print("\n== Tóm tắt: tỉ số sai số trung vị (so với cách không trọng số cùng họ) ==")
    for key, res in allres.items():
        lr = res["LU*"][0] / res["L0"][0]; lt = res["LU*"][2] / res["L0"][2]
        l2 = res["L2D"][2] / res["L0"][2]; lu = res["LU"][2] / res["L0"][2]; lz = res["LUz*"][2] / res["L0"][2]
        gr = res["GU"][2] / res["G0"][2]; g2 = res["G2D"][2] / res["G0"][2]; gi = res["GUiso"][2] / res["G0"][2]
        print(f"[{key:2s}] tuyến tính medT: L2D/L0={l2:.2f} LU/L0={lu:.2f} LUz*/L0={lz:.2f} LU*/L0={lt:.2f} (rot LU*/L0={lr:.2f}) | "
              f"GN medT: G2D/G0={g2:.2f} GUiso/G0={gi:.2f} GU/G0={gr:.2f}")
    print(f"\nPhần 1 tổng: {'PASS' if ok else 'FAIL'}   thời gian {time.time() - t0:.1f} s")


if __name__ == "__main__":
    main()
