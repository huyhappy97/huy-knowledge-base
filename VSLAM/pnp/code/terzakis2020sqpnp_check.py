"""Kiểm chứng số cho terzakis2020sqpnp (SQPnP, ECCV 2020) — cửa (b), learning-rules.md mục 5.

Chạy:  python3 VSLAM/pnp/code/terzakis2020sqpnp_check.py      (< 3 phút, seed cố định)

Nội dung:
  [1] Dựng A_i, Q_i, P, Omega theo eq. (3)-(7); kiểm E^2(R, t=P r) = r^T Omega r, t=P r là nghiệm
      bình phương tối thiểu theo t, và đồng nhất thức (tôi suy ra) E^2 = sum z_i^2 ||m_i - pi(X_c,i)||^2.
  [2] Hạng của Omega: 2n-3 (n nhỏ), null 3 chiều cho điểm đồng phẳng.
  [3] Mệnh đề 3 (lồi trong vùng 90 độ) và Mệnh đề 4 (góc < 71 độ) — kiểm bằng số.
  [4] Cài SQPnP (Alg. 1 + Alg. 2) bằng numpy, ba biến thể:
        'fixed'   : bắt đầu từ e9 (vector riêng trị riêng nhỏ nhất), dừng khi min E^2 < 3*s_next (như §2.1 viết)
        'literal' : chỉ số nu của eq. (14)/Alg. 1 chép nguyên văn, điều kiện while so với s (không nhân 3)
        'e9only'  : chỉ hai lần SQP từ +-sqrt(3) e9 (hoặc từ không gian null), không vòng while
      So với cv2.solvePnP(flags=SOLVEPNP_SQPNP).
  [5] Tối ưu toàn cục thực nghiệm: so E^2 của SQPnP với cực tiểu của cùng hàm r^T Omega r trên SO(3)
      tìm bằng LM đa khởi tạo dày (256 điểm khởi tạo ngẫu nhiên đều trên SO(3)).
  [6] Hàm (2) khác hàm (1): sai số tái chiếu của nghiệm SQPnP so với sau khi tinh chỉnh LM theo (1).
  [7] Thời gian theo n.
"""
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from common import K_DEFAULT, make_scene, random_rotation, rot_err_deg, proj_to_so3  # noqa: E402

try:
    import cv2
except ImportError:  # pragma: no cover
    cv2 = None

SQ3 = np.sqrt(3.0)


# ---------------------------------------------------------------- [1] Omega, P theo eq. (3)-(7)
def build_omega(M, m):
    """M (n,3) điểm thế giới; m (n,2) toạ độ chuẩn hoá trên mặt Z=1. Trả về Omega (9x9), P (3x9)."""
    n = len(M)
    A = np.zeros((n, 3, 9))
    for k in range(3):
        A[:, k, 3 * k:3 * k + 3] = M                      # eq. (3): R M_i = A_i r, r = hàng của R xếp chồng
    mh = np.c_[m, np.ones(n)]
    B = mh[:, :, None] * np.array([0, 0, 1.0])[None, None, :] - np.eye(3)[None]   # m_i 1_z^T - I_3
    Q = np.einsum('nki,nkj->nij', B, B)                   # Q_i = B^T B  (PSD)
    sumQ = Q.sum(0)
    QA = np.einsum('nij,njk->nik', Q, A).sum(0)
    P = -np.linalg.solve(sumQ, QA)                        # eq. (6)
    AP = A + P[None]
    Om = np.einsum('nji,njk,nkl->il', AP, Q, AP)          # eq. (7)
    return 0.5 * (Om + Om.T), P


def cost_eq2(M, m, R, t):
    Xc = M @ R.T + t
    mh = np.c_[m, np.ones(len(m))]
    return float(np.sum((Xc[:, 2:3] * mh - Xc) ** 2))     # eq. (2)


def normalized(u, K=K_DEFAULT):
    return (np.c_[u, np.ones(len(u))] @ np.linalg.inv(K).T)[:, :2]


# ---------------------------------------------------------------- [4] SQPnP (Alg. 1, 2)
def h_and_H(x):
    r1, r2, r3 = x[0:3], x[3:6], x[6:9]
    h = np.array([r1 @ r1 - 1, r2 @ r2 - 1, r1 @ r2, r1 @ r3, r2 @ r3,
                  np.linalg.det(np.vstack([r1, r2, r3])) - 1])
    H = np.zeros((6, 9))
    H[0, 0:3] = 2 * r1
    H[1, 3:6] = 2 * r2
    H[2, 0:3], H[2, 3:6] = r2, r1
    H[3, 0:3], H[3, 6:9] = r3, r1
    H[4, 3:6], H[4, 6:9] = r3, r2
    H[5, 0:3], H[5, 3:6], H[5, 6:9] = np.cross(r2, r3), np.cross(r3, r1), np.cross(r1, r2)
    return h, H


def solve_sqp(r, Om, eps=1e-8, T=15):
    """Alg. 2: lặp  [Om H^T; H 0][d; l] = [-Om r; -h(r)]  cho tới ||d|| < eps hoặc quá T bước."""
    r = r.copy()
    for step in range(1, T + 1):
        h, H = h_and_H(r)
        KKT = np.zeros((15, 15))
        KKT[:9, :9], KKT[:9, 9:], KKT[9:, :9] = Om, H.T, H
        d = np.linalg.solve(KKT, np.r_[-Om @ r, -h])[:9]
        r = r + d
        if np.linalg.norm(d) < eps:
            return r, step, True
    return r, T, False


def nearest_rot_vec(x):
    """argmin_{mat(r) in SO(3)} ||r - x||  (NOMP; bài dùng FOAM, ở đây dùng SVD — cùng nghiệm)."""
    return proj_to_so3(x.reshape(3, 3)).ravel()


def cheiral_fn(M, P):
    """Kiểm độ sâu dương kiểu OpenCV: trọng tâm có z>0, hoặc đa số điểm có z>0."""
    Mbar = M.mean(0)
    def ok(r):
        t = P @ r
        z = M @ r[6:9] + t[2]
        return (r[6:9] @ Mbar + t[2] > 0) or (np.sum(z > 0) >= np.sum(z <= 0))
    return ok


def sqpnp(Om, variant='fixed', null_tol=1e-10, eps=1e-8, T=15, cheiral=None, null_rot=None):
    """Alg. 1. variant: 'fixed' | 'literal' | 'e9only'. cheiral: hàm r->bool; nếu có, điều kiện dừng
    và việc chọn nghiệm chỉ xét nghiệm có độ sâu dương (như OpenCV). Trả về (R, E2, danh sách lời gọi)."""
    w, V = np.linalg.eigh(Om)
    order = np.argsort(w)[::-1]
    s = w[order]                     # s[0] = s1 >= ... >= s[8] = s9
    e = V[:, order]                  # e[:, j] = e_{j+1}
    E = lambda j: e[:, j - 1]        # chỉ số 1-based như bài
    S = lambda j: s[j - 1]
    k = max(1, int(np.sum(s < null_tol * max(s[0], 1e-300))))
    if null_rot is not None and k > 1:           # đổi cơ sở (tuỳ ý) của không gian null — bài không cố định cơ sở
        e = e.copy()
        e[:, 9 - k:] = e[:, 9 - k:] @ null_rot(k)
    calls = []                       # (E2, r, số bước, hội tụ?, góc seed->kết quả (độ), hợp lệ độ sâu?)
    ok = cheiral if cheiral is not None else (lambda r: True)

    def run(x0):
        r0 = nearest_rot_vec(x0)
        r, it, conv = solve_sqp(r0, Om, eps, T)
        r = nearest_rot_vec(r)       # làm tròn về SO(3)
        calls.append((float(r @ Om @ r), r, it, conv, rot_err_deg(r.reshape(3, 3), r0.reshape(3, 3)), ok(r)))

    def best():
        c = [z[0] for z in calls if z[5]]
        return min(c) if c else np.inf

    if variant == 'literal':
        for i in range(1, 2 * k + 1):
            mu = (i - 1) // k
            nu = 9 - k + i - (i // k) * k            # đúng như Alg. 1 / eq. (14)
            run((-1) ** mu * SQ3 * E(nu))
        kk = k
        while 9 - kk >= 1 and best() >= S(9 - kk):   # Alg. 1: so với s, không có hệ số 3
            for i in (1, 2):
                run((-1) ** i * SQ3 * E(9 - kk))
            kk += 1
    elif variant == 'onesided':
        # mô phỏng OpenCV: FOAM(e) và FOAM(-e) cùng trả về rotation gần nhất của sign(det e)*e -> 1 seed/vector riêng
        sg = lambda x: x if np.linalg.det(x.reshape(3, 3)) > 0 else -x
        for j in range(10 - k, 10):
            run(sg(SQ3 * E(j)))
        j = 9 - k
        while j >= 1 and best() >= 3 * S(j):
            run(sg(SQ3 * E(j)))
            j -= 1
    else:
        for j in range(10 - k, 10):                  # e_{10-k..9}: không gian cực tiểu của f trên S^8
            run(+SQ3 * E(j))
            run(-SQ3 * E(j))
        if variant == 'fixed':
            j = 9 - k
            while j >= 1 and best() >= 3 * S(j):     # §2.1: so với 3*s_j
                run(+SQ3 * E(j))
                run(-SQ3 * E(j))
                j -= 1
    valid = [z for z in calls if z[5]] or calls
    c, r = min(((z[0], z[1]) for z in valid), key=lambda z: z[0])
    return r.reshape(3, 3), c, calls


# ---------------------------------------------------------------- [5] LM đa khởi tạo trên SO(3)
GEN = np.zeros((3, 3, 3))
for _k in range(3):
    _w = np.zeros(3); _w[_k] = 1
    GEN[_k] = np.array([[0, -_w[2], _w[1]], [_w[2], 0, -_w[0]], [-_w[1], _w[0], 0]])


def batch_expm(W):
    th = np.linalg.norm(W, axis=1)[:, None, None]
    Kx = np.einsum('bk,kij->bij', W, GEN)
    ths = np.where(th < 1e-12, 1.0, th)
    a = np.where(th < 1e-12, 1.0, np.sin(ths) / ths)
    b = np.where(th < 1e-12, 0.5, (1 - np.cos(ths)) / ths ** 2)
    return np.eye(3)[None] + a * Kx + b * Kx @ Kx


def multistart_min(Om, rng, n_starts=256, iters=60, extra=()):
    Rs = np.stack([random_rotation(rng) for _ in range(n_starts)] + [np.asarray(x) for x in extra])
    lam = np.full(len(Rs), 1e-3)
    f = lambda Rb: np.einsum('bi,ij,bj->b', Rb.reshape(-1, 9), Om, Rb.reshape(-1, 9))
    fc = f(Rs)
    for _ in range(iters):
        J = np.einsum('bij,kjl->bkil', Rs, GEN).reshape(len(Rs), 3, 9).transpose(0, 2, 1)  # d vec(R[w]x)/dw
        r = Rs.reshape(-1, 9)
        Hm = np.einsum('bik,ij,bjl->bkl', J, Om, J)
        g = np.einsum('bik,ij,bj->bk', J, Om, r)
        Hd = Hm + lam[:, None, None] * (np.einsum('bii->bi', Hm).mean(1)[:, None, None] + 1e-30) * np.eye(3)
        dw = -np.linalg.solve(Hd, g[..., None])[..., 0]
        Rn = Rs @ batch_expm(dw)
        fn = f(Rn)
        acc = fn < fc
        Rs[acc], fc[acc] = Rn[acc], fn[acc]
        lam = np.where(acc, lam * 0.3, lam * 10)
        lam = np.clip(lam, 1e-12, 1e8)
    # "trim": re-orthonormalise
    Rs = np.stack([proj_to_so3(R) for R in Rs])
    fc = f(Rs)
    i = int(np.argmin(fc))
    return Rs[i], float(fc[i]), Rs, fc


# ---------------------------------------------------------------- cảnh
def paper_scene(n, rng, sigma2_px):
    """Cảnh theo §4.1 eq. (15): M_i ~ N([.75,.75,12], 9 I), b~N(0,.2^2 I), MRP psi~N(0,.05^2 I), f=1400."""
    K = np.array([[1400.0, 0, 900], [0, 1400.0, 900], [0, 0, 1]])
    while True:
        M = rng.normal([0.75, 0.75, 12.0], 3.0, size=(n, 3))
        b = rng.normal(0, 0.2, 3)
        psi = rng.normal(0, 0.05, 3)
        p2 = psi @ psi
        Px = np.array([[0, -psi[2], psi[1]], [psi[2], 0, -psi[0]], [-psi[1], psi[0], 0]])
        Rwc = np.eye(3) + (8 * Px @ Px + 4 * (1 - p2) * Px) / (1 + p2) ** 2   # MRP -> R (camera trong thế giới)
        R = Rwc.T
        t = -R @ b
        Xc = M @ R.T + t
        if np.all(Xc[:, 2] > 0.1):
            break
    u = (Xc @ K.T)[:, :2] / Xc[:, 2:3]
    u = u + rng.normal(0, np.sqrt(sigma2_px), u.shape)
    return M, u, R, t, K


def cv2_sqpnp(M, u, K):
    ok, rv, tv = cv2.solvePnP(M.astype(np.float64), u.astype(np.float64), K, None, flags=cv2.SOLVEPNP_SQPNP)
    R, _ = cv2.Rodrigues(rv)
    return R, tv.ravel()


def main():
    FULL = '--full' in sys.argv
    t_start = time.time()
    rng = np.random.default_rng(20200823)
    print("=" * 78)
    print("[1] eq. (2)-(7): loại bỏ t, E^2 = r^T Omega r")
    worst = [0, 0, 0, 0]
    for trial in range(200):
        n = int(rng.integers(3, 30))
        M, u, _, R0, t0 = make_scene(n, rng, sigma_px=2.0, planar=bool(trial % 2))
        m = normalized(u)
        Om, P = build_omega(M, m)
        R = random_rotation(rng)                        # R bất kỳ, không cần đúng
        r = R.ravel()
        t = P @ r
        e_quad = r @ Om @ r
        e_dir = cost_eq2(M, m, R, t)
        # t tối ưu tìm độc lập bằng lstsq trên eq. (2) (tuyến tính theo t)
        mh = np.c_[m, np.ones(n)]
        Bm = mh[:, :, None] * np.array([0, 0, 1.0])[None, None, :] - np.eye(3)[None]
        y = -np.einsum('nij,nj->ni', Bm, M @ R.T).ravel()
        t_ls = np.linalg.lstsq(Bm.reshape(-1, 3), y, rcond=None)[0]
        # đồng nhất thức (tôi suy ra): E^2 = sum z^2 ||m - pi(Xc)||^2
        Xc = M @ R.T + t
        e_z = np.sum(Xc[:, 2] ** 2 * np.sum((m - Xc[:, :2] / Xc[:, 2:3]) ** 2, 1))
        worst[0] = max(worst[0], abs(e_quad - e_dir) / max(e_dir, 1e-300))
        worst[1] = max(worst[1], np.linalg.norm(t - t_ls) / np.linalg.norm(t_ls))
        worst[2] = max(worst[2], abs(e_z - e_dir) / max(e_dir, 1e-300))
        # nghiệm đúng, không nhiễu: cost = 0, t = P r
        M2, u2, _, R2, t2 = make_scene(n, rng)
        Om2, P2 = build_omega(M2, normalized(u2))
        worst[3] = max(worst[3], abs(R2.ravel() @ Om2 @ R2.ravel()) / np.trace(Om2), np.linalg.norm(P2 @ R2.ravel() - t2))
    print(f"  200 cảnh ngẫu nhiên (n=3..29, nửa phẳng, 2px):")
    print(f"  max |r'Om r - E2(eq2)|/E2           = {worst[0]:.1e}  {'PASS' if worst[0] < 1e-9 else 'FAIL'}")
    print(f"  max ||P r - t_lstsq|| / ||t_lstsq||   = {worst[1]:.1e}  {'PASS' if worst[1] < 1e-9 else 'FAIL'}")
    print(f"  max |E2 - sum z^2 ||m-pi||^2| / E2    = {worst[2]:.1e}  {'PASS' if worst[2] < 1e-9 else 'FAIL'}  (E2 = reproj. error có trọng số z^2)")
    print(f"  không nhiễu, pose đúng: max(cost/tr, ||Pr - t||) = {worst[3]:.1e}  {'PASS' if worst[3] < 1e-9 else 'FAIL'}")

    print("=" * 78)
    print("[2] Hạng của Omega (nhiễu 1px) — số trị riêng > 1e-10 * s1")
    for planar in (False, True):
        row = []
        for n in (3, 4, 5, 6, 8, 20):
            if planar and n < 4:
                row.append(f"n={n}:-")
                continue
            M, u, *_ = make_scene(n, rng, sigma_px=1.0, planar=planar)
            Om, _ = build_omega(M, normalized(u))
            s = np.linalg.eigvalsh(Om)
            row.append(f"n={n}:{int(np.sum(s > 1e-10 * s.max()))}")
        print(f"  {'phẳng    ' if planar else 'tổng quát'} " + "  ".join(row))

    print("=" * 78)
    print("[3] Mệnh đề 3 và 4")
    M, u, *_ = make_scene(10, rng, sigma_px=1.0)
    Om, _ = build_omega(M, normalized(u))
    w, V = np.linalg.eigh(Om)
    e9, e1 = V[:, 0], V[:, -1]
    th = np.radians(np.linspace(0, 90, 91))
    fth = np.array([3 * (np.cos(a) * e9 + np.sin(a) * e1) @ Om @ (np.cos(a) * e9 + np.sin(a) * e1) for a in th])
    d2 = np.gradient(np.gradient(fth, th), th)
    first_neg = np.degrees(th[np.argmax(d2 < 0)])
    print(f"  f dọc cung trắc địa e9 -> e1: f''<0 từ góc ~{first_neg:.0f} độ (giải tích: 45 độ)"
          f" -> 'lồi trong vùng 90 độ' của Mđ 3 {'KHÔNG đúng theo nghĩa lồi trắc địa' if first_neg < 80 else 'đúng'}")
    mx = 0
    for _ in range(20000):
        x = rng.normal(size=9); x /= np.linalg.norm(x)
        r = nearest_rot_vec(SQ3 * x)
        mx = max(mx, np.degrees(np.arccos(np.clip(x @ r / SQ3, -1, 1))))
    x = np.diag([1.0, 1, -1]).ravel() / SQ3
    r = nearest_rot_vec(SQ3 * x)
    adv = np.degrees(np.arccos(x @ r / SQ3))
    print(f"  Mđ 4: góc(e, NOMP(sqrt3 e)) lớn nhất trên 20000 e ngẫu nhiên = {mx:.1f} độ; "
          f"e = diag(1,1,-1)/sqrt3 cho {adv:.2f} độ (= arccos(1/3)); cận 71 độ: {'PASS' if max(mx, adv) < 71 else 'FAIL'}")

    print("=" * 78)
    print("[4]+[5] SQPnP (numpy) và cv2 SQPNP so với LM đa khởi tạo (96 điểm; --full: 128) trên SO(3), cùng hàm r'Om r")
    print("  cột A = so với min toàn cục KHÔNG ràng buộc độ sâu; cột C = so với min trong các nghiệm có độ sâu dương")
    print("  mỗi ô: tổng lỗi/(lỗi lớn: gap tương đối > 1e-3). fixed=Alg.1 sửa chỉ số, eps=1e-8, T=15;")
    print("  conv = fixed với eps=1e-12, T=200; literal = chỉ số eq.(14) nguyên văn; e9only = không vòng while;")
    print("  one = 1 seed/vector riêng (mô phỏng FOAM của OpenCV), eps=1e-5, T=15")
    configs = []
    for n in (3, 4, 5, 6, 8, 10, 20):
        for sg in (0.0, 1.0, 5.0, 20.0):
            configs.append(('tổng quát', n, sg, False))
    for n in (4, 5, 6, 8, 20):
        for sg in (0.0, 1.0, 5.0, 20.0):
            configs.append(('phẳng', n, sg, True))
    configs += [('bài §4.1', n, s2, 'paper') for n in (4, 6, 10) for s2 in (2.0, 17.0)]
    configs += [('nhiễu 50px', n, 50.0, 'wide') for n in (3, 4, 5, 6)]
    N_PER = 40 if FULL else 8
    N_START = 128 if FULL else 96
    tol_rel, tol_abs = 1e-6, 1e-12
    VARS = ('fixed', 'conv', 'literal', 'e9only')
    COLS = [v + '/A' for v in VARS] + ['fixed/C', 'conv/C', 'one/C', 'cv2/C']
    tot = {c: [0, 0] for c in COLS}
    ntot = 0
    call_steps, call_conv, seed_ang, ncalls = [], [], [], []
    examples = []
    behind_glob = 0
    cv_vs_mine = []
    hdr = "".join(f"{c:>10}" for c in COLS)
    print(f"  {'cảnh':<11}{'n':>3}{'sigma':>6}{'N':>4} |{hdr} | twin")
    for (name, n, sg, kind) in configs:
        cnt = {c: [0, 0] for c in COLS}
        twin = 0
        for _ in range(N_PER):
            if kind == 'paper':
                M, u, R0, t0, K = paper_scene(n, rng, sg)
            elif kind == 'wide':
                M, u, _, R0, t0 = make_scene(n, rng, depth=(0.5, 20.0), sigma_px=sg); K = K_DEFAULT
            else:
                M, u, _, R0, t0 = make_scene(n, rng, planar=kind, sigma_px=sg); K = K_DEFAULT
            m = normalized(u, K)
            Om, P = build_omega(M, m)
            ch = cheiral_fn(M, P)
            res = {'fixed': sqpnp(Om, 'fixed'), 'conv': sqpnp(Om, 'fixed', eps=1e-12, T=200),
                   'literal': sqpnp(Om, 'literal'), 'e9only': sqpnp(Om, 'e9only')}
            resC = {'fixed': sqpnp(Om, 'fixed', cheiral=ch), 'conv': sqpnp(Om, 'fixed', eps=1e-12, T=200, cheiral=ch),
                    'one': sqpnp(Om, 'onesided', eps=1e-5, T=15, cheiral=ch)}
            for z in res['fixed'][2]:
                call_steps.append(z[2]); call_conv.append(z[3]); seed_ang.append(z[4])
            ncalls.append(len(res['fixed'][2]))
            Rcv, tcv = cv2_sqpnp(M, u, K)
            c_cv = float(Rcv.ravel() @ Om @ Rcv.ravel())
            cv_vs_mine.append(rot_err_deg(Rcv, resC['conv'][0]))
            extra = [res[v][0] for v in res] + [resC[v][0] for v in resC] + [Rcv]
            Rg, cg, Rall, fall = multistart_min(Om, rng, n_starts=N_START, iters=50, extra=extra)
            okm = np.array([ch(R.ravel()) for R in Rall])
            cgC = float(fall[okm].min()) if okm.any() else np.inf
            if not ch(Rg.ravel()):
                behind_glob += 1
            near = Rall[fall - cg <= tol_rel * cg + tol_abs * np.trace(Om)]
            if any(rot_err_deg(Rx, Rg) > 1.0 for Rx in near):
                twin += 1
            vals = {v + '/A': (res[v][1], cg) for v in VARS}
            vals.update({'fixed/C': (resC['fixed'][1], cgC), 'conv/C': (resC['conv'][1], cgC),
                         'one/C': (resC['one'][1], cgC), 'cv2/C': (c_cv, cgC)})
            for c, (val, g) in vals.items():
                gap = val - g
                if gap > tol_rel * max(g, 0) + tol_abs * np.trace(Om):
                    cnt[c][0] += 1
                    big = gap > 1e-3 * max(g, tol_abs * np.trace(Om))
                    cnt[c][1] += int(big)
                    if big and c in ('conv/A', 'conv/C', 'cv2/C') and len(examples) < 6:
                        examples.append((c, name, n, sg, f"{val:.4g}", f"{g:.4g}"))
        ntot += N_PER
        for c in COLS:
            tot[c][0] += cnt[c][0]; tot[c][1] += cnt[c][1]
        row = "".join(f"{str(cnt[c][0]) + '/' + str(cnt[c][1]):>10}" for c in COLS)
        print(f"  {name:<11}{n:>3}{sg:>6.1f}{N_PER:>4} |{row} | {twin:>4}")
    row = "".join(f"{str(tot[c][0]) + '/' + str(tot[c][1]):>10}" for c in COLS)
    print(f"  {'TỔNG':<11}{'':>3}{'':>6}{ntot:>4} |{row}")
    print(f"  (tol: gap > {tol_rel:g}*E2_glob + {tol_abs:g}*tr(Om)). 'twin' = số cảnh có >=2 cực tiểu toàn cục cách nhau > 1 độ")
    print(f"  cảnh mà cực tiểu toàn cục không ràng buộc có độ sâu âm: {behind_glob}/{ntot}")
    print(f"  ví dụ lỗi lớn (cột, cảnh, n, sigma, E2_solver, E2_glob): {examples if examples else 'không có'}")
    cs = np.array(call_steps); cc = np.array(call_conv); sa = np.array(seed_ang)
    print(f"  Alg.2 (eps=1e-8, T=15), {len(cs)} lời gọi: số bước median {int(np.median(cs))}, 90% {int(np.percentile(cs, 90))},"
          f" tỉ lệ chạm T mà chưa hội tụ {100 * np.mean(~cc):.1f}%")
    print(f"  góc giữa điểm khởi tạo NOMP và nghiệm SQP: median {np.median(sa):.1f} độ, 90% {np.percentile(sa, 90):.1f}, max {sa.max():.1f}")
    print(f"  số lời gọi SQP / cảnh (fixed): min {min(ncalls)}  median {int(np.median(ncalls))}  max {max(ncalls)}")
    cvd = np.array(cv_vs_mine)
    print(f"  góc R(cv2) vs R(numpy conv, có kiểm độ sâu): median {np.median(cvd):.1e} độ; > 1 độ ở {np.sum(cvd > 1)}/{len(cvd)} cảnh")

    print("=" * 78)
    print("[5b] Hai seed (eq. 13) so với một seed/vector riêng (như OpenCV), với 6 phép quay ngẫu nhiên của cơ sở")
    print("     null(Omega) mỗi cảnh (có kiểm độ sâu). Đếm: cảnh bị ảnh hưởng / lần chạy sai lớn (gap > 1e-3) / cv2 sai")
    NB = 150 if FULL else 50
    rq = np.random.default_rng(7)
    def rand_orth(k):
        Q, _ = np.linalg.qr(rq.normal(size=(k, k)))
        return Q
    for (name, n, sg, planar) in (('tổng quát', 4, 0.0, False), ('tổng quát', 4, 1.0, False),
                                  ('tổng quát', 5, 1.0, False), ('phẳng', 6, 1.0, True), ('phẳng', 20, 1.0, True)):
        stat = {'fixed': [0, 0, 0], 'onesided': [0, 0, 0]}
        cvbad = 0
        for _ in range(NB):
            M, u, _, R0, t0 = make_scene(n, rng, planar=planar, sigma_px=sg)
            Om, P = build_omega(M, normalized(u))
            ch = cheiral_fn(M, P)
            outs = {'fixed': [sqpnp(Om, 'fixed', eps=1e-12, T=200, cheiral=ch, null_rot=rand_orth)[1] for _ in range(6)],
                    'onesided': [sqpnp(Om, 'onesided', eps=1e-5, T=15, cheiral=ch, null_rot=rand_orth)[1] for _ in range(6)]}
            Rcv, _ = cv2_sqpnp(M, u, K_DEFAULT)
            c_cv = float(Rcv.ravel() @ Om @ Rcv.ravel())
            _, cg, Rall, fall = multistart_min(Om, rng, n_starts=64, iters=50)
            okm = np.array([ch(R.ravel()) for R in Rall])
            g = min(float(fall[okm].min()) if okm.any() else np.inf, *outs['fixed'], *outs['onesided'], c_cv)
            thr = lambda o: o - g > 1e-3 * max(g, 1e-12 * np.trace(Om))
            for v in outs:
                nb = sum(thr(o) for o in outs[v])
                stat[v][0] += int(nb > 0); stat[v][1] += nb; stat[v][2] += len(outs[v])
            cvbad += int(thr(c_cv))
        print(f"  {name:<10} n={n:>2} sigma={sg}: 2 seed: {stat['fixed'][0]}/{NB} cảnh, {stat['fixed'][1]}/{stat['fixed'][2]} lần | "
              f"1 seed: {stat['onesided'][0]}/{NB} cảnh, {stat['onesided'][1]}/{stat['onesided'][2]} lần | cv2: {cvbad}/{NB}")

    print("=" * 78)
    print("[6] Hàm (2) không phải hàm (1): RMSE tái chiếu (px) của SQPnP trước/sau LM theo (1)")
    for n, sg in ((6, 1.0), (6, 20.0), (20, 5.0), (4, 20.0)):
        before, after, dang = [], [], []
        for _ in range(40):
            M, u, _, R0, t0 = make_scene(n, rng, sigma_px=sg)
            Rcv, tcv = cv2_sqpnp(M, u, K_DEFAULT)
            rv = cv2.Rodrigues(Rcv)[0]
            pr = cv2.projectPoints(M, rv, tcv, K_DEFAULT, None)[0].reshape(-1, 2)
            before.append(np.sqrt(np.mean(np.sum((pr - u) ** 2, 1))))
            rv2, tv2 = cv2.solvePnPRefineLM(M, u, K_DEFAULT, None, rv.copy(), tcv.reshape(3, 1).copy())
            pr2 = cv2.projectPoints(M, rv2, tv2, K_DEFAULT, None)[0].reshape(-1, 2)
            after.append(np.sqrt(np.mean(np.sum((pr2 - u) ** 2, 1))))
            dang.append(rot_err_deg(cv2.Rodrigues(rv2)[0], Rcv))
        b, a = np.array(before), np.array(after)
        print(f"  n={n:>2} sigma={sg:>4}px: RMSE SQPnP median {np.median(b):.3f}, sau LM {np.median(a):.3f}; "
              f"max tăng tương đối {np.max((b - a) / a) * 100:.1f}%; góc lệch R max {max(dang):.3f} độ")

    print("=" * 78)
    print("[7] Thời gian (ms, median 10 lần, 1 luồng CPU của container) theo n — cảnh tổng quát, 2px")
    cv2.setNumThreads(1)
    for n in (4, 10, 100, 1000, 10000):
        M, u, *_ = make_scene(n, rng, sigma_px=2.0)
        m = normalized(u)
        tb, ts, tc = [], [], []
        for _ in range(10):
            t0_ = time.perf_counter(); Om, P = build_omega(M, m); t1_ = time.perf_counter()
            sqpnp(Om, 'fixed'); t2_ = time.perf_counter()
            cv2_sqpnp(M, u, K_DEFAULT); t3_ = time.perf_counter()
            tb.append(t1_ - t0_); ts.append(t2_ - t1_); tc.append(t3_ - t2_)
        print(f"  n={n:>5}: numpy dựng Omega {1e3*np.median(tb):7.3f}  numpy SQP {1e3*np.median(ts):6.3f}  "
              f"cv2 SQPNP (toàn bộ) {1e3*np.median(tc):7.3f}")
    print(f"tổng thời gian chạy: {time.time() - t_start:.0f} s")


if __name__ == '__main__':
    main()
