"""Kiểm chứng số cho fischler1981ransac (Fischler & Bolles 1981, CACM 24(6)).

Chạy:  python3 VSLAM/pnp/code/fischler1981ransac_check.py
Ba phần:
  [1] Thống kê số lần thử của RANSAC (§II-B, tr. 4): E(k)=w^-n, E(k^2)=(2-b)/b^2,
      SD(k)=sqrt(1-w^n)/w^n, bảng E(k), k=log(1-z)/log(1-b); Monte-Carlo có/không hoàn lại.
      Cộng: ví dụ đường thẳng Fig. 1 (tr. 2) và ngưỡng t-n=5 (§II-C).
  [2] Đường ống RANSAC + P3P (cv2.solveP3P) trên dữ liệu tổng hợp, ngoại lai 10–70 %.
  [3] Các khẳng định về số nghiệm của LDP (§III-A, tr. 6–9, Phụ lục A):
      Fig. 5 (P3P 4 nghiệm), hệ số quartic (A18)–(A23), Fig. 6 (P4P 2 nghiệm),
      Fig. 7 (P5P 2 nghiệm), 4 điểm đồng phẳng -> duy nhất, P6P/DLT.
Seed cố định; chạy < 3 phút.
"""
import os
import sys
import time
from math import comb, log, sqrt

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from common import K_DEFAULT, make_scene, project, rot_err_deg  # noqa: E402

import cv2  # noqa: E402

T0 = time.time()
RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok)))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


# =============================================================================
# [1] Thống kê số lần thử
# =============================================================================
print("=" * 78)
print("[1] Số lần thử của RANSAC (§II-B, tr. 4)")
print("=" * 78)

# (1a) chuỗi số: E(k)=sum i b a^{i-1}, E(k^2)=sum i^2 b a^{i-1}
for w, n in [(0.5, 4), (0.8, 3), (0.3, 3)]:
    b = w ** n
    a = 1 - b
    i = np.arange(1, 200000, dtype=float)
    Ek = np.sum(i * b * a ** (i - 1))
    Ek2 = np.sum(i ** 2 * b * a ** (i - 1))
    sd = sqrt(Ek2 - Ek ** 2)
    ok = abs(Ek - 1 / b) < 1e-6 * Ek and abs(Ek2 - (2 - b) / b ** 2) < 1e-6 * Ek2 \
        and abs(sd - sqrt(1 - b) / b) < 1e-6 * sd
    check(f"chuỗi số w={w}, n={n}: E(k)={Ek:.4f} (1/b={1/b:.4f}), "
          f"SD={sd:.4f} (sqrt(1-b)/b={sqrt(1-b)/b:.4f})", ok)

# (1b) ví dụ số trong bài: w=0.5,n=4 -> E=16, SD=15.5, k(z=.9)=35.7
b = 0.5 ** 4
check("ví dụ w=0.5,n=4: E(k)=16, SD(k)≈15.5, k=log(0.1)/log(15/16)≈35.7",
      abs(1 / b - 16) < 1e-12 and abs(sqrt(1 - b) / b - 15.5) < 0.01
      and abs(log(0.1) / log(15 / 16) - 35.7) < 0.05,
      f"SD={sqrt(1-b)/b:.3f}, k={log(0.1)/log(15/16):.3f}")

# (1c) bảng E(k) ở tr. 4 (chép tay từ bản PDF; '--' bỏ trống)
paper_tab = {
    0.9: [1.1, 1.2, 1.4, 1.5, 1.7, 1.9], 0.8: [1.3, 1.6, 2.0, 2.4, 3.0, 3.8],
    0.7: [1.4, 2.0, 2.9, 4.2, 5.9, 8.5], 0.6: [1.7, 2.8, 4.6, 7.7, 13, 21],
    0.5: [2.0, 4.0, 8.0, 16, 32, 64], 0.4: [2.5, 6.3, 16, 39, 98, 244],
    0.3: [3.3, 11, 37, 123, 412, None], 0.2: [5.0, 25, 125, 625, None, None]}
bad, worst = [], 0.0
for w, row in paper_tab.items():
    for n, v in enumerate(row, 1):
        if v is None:
            continue
        exact = w ** -n
        unit = 0.1 if exact < 10 else 1.0          # chữ số cuối được in
        worst = max(worst, abs(exact - v) / unit)
        if abs(exact - v) > 0.5 * unit + 1e-9:   # không khớp phép làm tròn thông thường
            bad.append((w, n, v, round(exact, 4)))
check("bảng E(k)=w^-n ở tr. 4: mọi ô lệch <= 1 đơn vị chữ số cuối", worst <= 1.0,
      f"ô không khớp làm tròn thông thường: {bad}")

# (1d) xấp xỉ k ≈ -ln(1-z) E(k) khi w^n << 1 (bài in 'log(1-z)E(k)', thiếu dấu trừ)
print("  xấp xỉ k/E(k) khi w^n<<1 (bài: z=.90 -> 2.3, z=.95 -> 3.0):")
for z in (0.90, 0.95):
    bb = 0.2 ** 6
    ratio = (log(1 - z) / log(1 - bb)) * bb
    print(f"    z={z}: k/E(k) = {ratio:.3f}; ln(1-z) = {log(1-z):+.3f} (âm) ; log10(1-z) = {np.log10(1-z):+.3f}")
check("hệ số 2.3 / 3.0 = -ln(1-z) (log tự nhiên, cần dấu trừ; bản in thiếu dấu)",
      abs(-log(0.1) - 2.3) < 0.01 and abs(-log(0.05) - 3.0) < 0.01)

# (1e) Monte-Carlo: lấy mẫu có hoàn lại (đúng giả thiết của bài) và không hoàn lại (RANSAC thực)
print("  Monte-Carlo 20000 lần chạy mỗi cấu hình (mô phỏng từng lần rút điểm):")
rng = np.random.default_rng(1)


def mc_first_success(N, w, n, reps, replace, rng, kmax=20000):
    Nin = int(round(w * N))
    first = np.full(reps, -1)
    alive = np.arange(reps)
    k = 0
    while alive.size and k < kmax:
        k += 1
        u = rng.random((alive.size, n))
        if replace:
            good = np.all(u < Nin / N, axis=1)
        else:  # rút tuần tự từ bình: xác suất lần j là inlier = (Nin-j)/(N-j)
            thr = np.array([(Nin - j) / (N - j) for j in range(n)])
            good = np.all(u < thr, axis=1)
        first[alive[good]] = k
        alive = alive[~good]
    return first


for N, w, n in [(1000, 0.5, 4), (100, 0.5, 3), (20, 0.5, 4), (30, 0.6, 3)]:
    b = w ** n
    bh = comb(int(round(w * N)), n) / comb(N, n)
    fr = mc_first_success(N, w, n, 20000, True, rng)
    fn = mc_first_success(N, w, n, 20000, False, rng)
    print(f"    N={N:4d} w={w} n={n}: w^-n={1/b:6.2f} SD={sqrt(1-b)/b:6.2f} | có hoàn lại: "
          f"mean={fr.mean():6.2f} sd={fr.std():6.2f} | không hoàn lại: mean={fn.mean():6.2f} "
          f"sd={fn.std():6.2f} (1/p_hypergeo={1/bh:6.2f})")
    se = sqrt(1 - b) / b / sqrt(20000)
    check(f"N={N},w={w},n={n}: MC có hoàn lại khớp E(k)=w^-n trong 4 SE", abs(fr.mean() - 1 / b) < 4 * se)
    seh = sqrt(1 - bh) / bh / sqrt(20000)
    check(f"N={N},w={w},n={n}: MC không hoàn lại khớp 1/p_hypergeo, lệch w^-n {100*(1/bh*b-1):+.1f}%",
          abs(fn.mean() - 1 / bh) < 4 * seh)

# (1f) k = log(1-z)/log(1-w^n): tỉ lệ lần chạy thành công trong ceil(k) lần thử
print("  tỉ lệ lần chạy có ít nhất một mẫu sạch trong k=ceil(log(1-z)/log(1-w^n)) lần thử:")
for N, w, n in [(1000, 0.5, 4), (20, 0.5, 4)]:
    for z in (0.9, 0.95, 0.99):
        k = int(np.ceil(log(1 - z) / log(1 - w ** n)))
        fr = mc_first_success(N, w, n, 20000, True, rng)
        fn = mc_first_success(N, w, n, 20000, False, rng)
        pr, pn = np.mean(fr <= k), np.mean(fn <= k)
        print(f"    N={N:4d} w={w} n={n} z={z}: k={k:3d}  có hoàn lại {pr:.4f} | không hoàn lại {pn:.4f}")
        if N == 1000:
            check(f"z={z}: tỉ lệ đạt >= z - 0.01 (N lớn)", pr >= z - 0.01)
        if N == 20 and z == 0.99:
            check("N=20 không hoàn lại: công thức k ĐÁNH GIÁ THẤP số lần cần (tỉ lệ < z)", pn < z,
                  f"{pn:.3f} < {z}")

# (1g) §II-C: y^(t-n) với y<0.5, t-n=5
check("§II-C: y=0.5, t-n=5 -> y^5 = 0.031 < 0.05", 0.5 ** 5 < 0.05, f"0.5^5={0.5**5:.4f}")

# (1h) Fig. 1: ví dụ bình phương tối thiểu + loại điểm dư lớn nhất
pts = np.array([[0, 0], [1, 1], [2, 2], [3, 2], [3, 3], [4, 4], [10, 2]], float)
print("  Fig. 1 (tr. 2): bình phương tối thiểu lặp, loại điểm dư lớn nhất:")
idx = list(range(7))
fits = []
for it in range(4):
    A = np.c_[np.ones(len(idx)), pts[idx, 0]]
    c0, c1 = np.linalg.lstsq(A, pts[idx, 1], rcond=None)[0]
    res = pts[idx, 1] - (c0 + c1 * pts[idx, 0])
    fits.append((c0, c1))
    print(f"    lần {it+1}: điểm {[i+1 for i in idx]} -> y = {c0:.2f} + {c1:.2f}x ; dư lớn nhất ở điểm {idx[np.argmax(abs(res))]+1}")
    idx.pop(int(np.argmax(abs(res))))
paper_fits = [(1.48, .16), (1.25, .13), (0.96, .14), (1.51, .06)]
check("Fig. 1: 4 đường LS in trong bảng khớp tính lại (±0.01)",
      all(abs(a - c) < 0.011 and abs(b_ - d) < 0.011 for (a, b_), (c, d) in zip(fits, paper_fits)),
      str([(round(float(a), 3), round(float(b_), 3)) for a, b_ in fits]))
best = 0
for i in range(7):
    for j in range(i + 1, 7):
        p, q = pts[i], pts[j]
        if p[0] == q[0]:
            continue
        s = (q[1] - p[1]) / (q[0] - p[0]); c = p[1] - s * p[0]
        d = np.abs(pts[:, 1] - s * pts[:, 0] - c) / sqrt(1 + s * s)
        best = max(best, int(np.sum(d <= 0.8)))
check("Fig. 1: duyệt 21 cặp, tập đồng thuận lớn nhất (dung sai 0.8) = 6 điểm đúng", best == 6, f"max={best}")

# =============================================================================
# [2] RANSAC + P3P trên dữ liệu tổng hợp
# =============================================================================
print("=" * 78)
print("[2] RANSAC + cv2.solveP3P, N=100 tương ứng, nhiễu inlier sigma=1 px, ngoại lai >=10 px")
print("=" * 78)
K = K_DEFAULT
rng = np.random.default_rng(2)


def make_data(N, eps, rng):
    X, u, uc, R, t = make_scene(N, rng, sigma_px=1.0)
    n_out = int(round(eps * N))
    out = rng.choice(N, n_out, replace=False)
    for i in out:
        while True:
            cand = rng.uniform([0, 0], [640, 480])
            if np.linalg.norm(cand - uc[i]) >= 10:
                break
        u[i] = cand
    inl = np.ones(N, bool); inl[out] = False
    return X, u, R, t, inl


def p3p(Xs, us):
    try:
        nsol, rv, tv = cv2.solveP3P(Xs, us, K, None, cv2.SOLVEPNP_P3P)
    except cv2.error:
        return []
    return [(cv2.Rodrigues(rv[i])[0], tv[i].ravel()) for i in range(nsol)]


def reproj_err(X, u, R, t):
    Xc = X @ R.T + t
    e = np.full(len(X), 1e9)
    front = Xc[:, 2] > 1e-9
    p = Xc[front] @ K.T
    e[front] = np.linalg.norm(p[:, :2] / p[:, 2:3] - u[front], axis=1)
    return e


# (2a) chọn dung sai theo §II-A: nhiễu hoá dữ liệu, đo sai số suy ra, lấy trung bình + 2 SD
errs = []
for _ in range(300):
    X, u, R, t, inl = make_data(100, 0.0, rng)
    s = rng.choice(100, 3, replace=False)
    for Rh, th in p3p(X[s], u[s]):
        if rot_err_deg(Rh, R) < 5:
            m = np.ones(100, bool); m[s] = False
            errs.append(reproj_err(X[m], u[m], Rh, th))
errs = np.concatenate(errs)
errs = errs[errs < 1e3]
tau = float(errs.mean() + 2 * errs.std())
print(f"  dung sai theo §II-A: mean={errs.mean():.2f}px, sd={errs.std():.2f}px -> tau = mean+2sd = {tau:.2f} px")
print(f"  tỉ lệ inlier (của mô hình dựng từ mẫu sạch) rơi trong tau: {np.mean(errs < tau):.3f}"
      f"  (w hiệu dụng < w danh nghĩa)")

print(f"  {'eps':>4} {'w':>4} {'1/w^3':>7} {'1/p_hyp':>7} {'T_sạch':>14} {'T_đồng thuận>=.8wN':>18} "
      f"{'k99':>4} {'P(T_s<=k99)':>11} {'P(T_c<=k99)':>11} {'y_hat':>6} {'maxC_sai':>8} {'P(C>=8|bẩn)':>11} {'sai@t=8':>7}")
RUNS = 150
summary = []
for eps in (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7):
    w = 1 - eps
    N = 100
    Nin = int(round(w * N))
    k99 = int(np.ceil(log(0.01) / log(1 - w ** 3)))
    T_s, T_c, ys, maxc_wrong, wrong_at8, c8 = [], [], [], [], 0, []
    for r in range(RUNS):
        X, u, R, t, inl = make_data(N, eps, rng)
        t_acc = int(0.8 * Nin)
        ts = tc = None
        first8_wrong = None
        k = 0
        while (ts is None or tc is None) and k < 5000:
            k += 1
            s = rng.choice(N, 3, replace=False)
            clean = bool(np.all(inl[s]))
            if clean and ts is None:
                ts = k
            for Rh, th in p3p(X[s], u[s]):
                e = reproj_err(X, u, Rh, th)
                c = int(np.sum(e < tau))
                correct = rot_err_deg(Rh, R) < 2.0
                if not clean:
                    m = np.ones(N, bool); m[s] = False
                    ys.append(np.mean(e[m] < tau))
                    maxc_wrong.append(c)
                    c8.append(c >= 8)
                if first8_wrong is None and c >= 8:
                    first8_wrong = (not clean) and (not correct)
                if tc is None and c >= t_acc:
                    tc = k
        T_s.append(ts); T_c.append(tc)
        wrong_at8 += bool(first8_wrong)
    T_s = np.array(T_s, float); T_c = np.array(T_c, float)
    ph = comb(Nin, 3) / comb(N, 3)
    ys = np.array(ys)
    summary.append((eps, T_s.mean(), 1 / ph, T_c.mean(), np.mean(T_s <= k99), np.mean(T_c <= k99)))
    print(f"  {eps:4.1f} {w:4.1f} {w**-3:7.2f} {1/ph:7.2f} {T_s.mean():6.2f}±{T_s.std():5.2f} "
          f"{T_c.mean():9.2f}±{T_c.std():6.2f} {k99:6d} {np.mean(T_s<=k99):11.3f} {np.mean(T_c<=k99):11.3f} "
          f"{ys.mean():6.3f} {max(maxc_wrong):8d} {np.mean(c8):11.4f} {wrong_at8:4d}/{RUNS}")
    se = sqrt(1 - ph) / ph / sqrt(RUNS)
    check(f"eps={eps}: số lần tới mẫu sạch đầu tiên khớp 1/p_hyp trong 4 SE", abs(T_s.mean() - 1 / ph) < 4 * se)

check("eps=0.7: số lần tới đồng thuận >= 0.8 w N lớn hơn số lần tới mẫu sạch (nhiễu làm w hiệu dụng nhỏ đi)",
      summary[-1][3] > summary[-1][1], f"{summary[-1][3]:.1f} vs {summary[-1][1]:.1f}")

# (2b) cv2.solvePnPRansac (P3P) với confidence 0.99: tỉ lệ thành công
print("  cv2.solvePnPRansac(flags=P3P, reprojectionError=tau, confidence=0.99, iterationsCount=10000):")
for eps in (0.1, 0.3, 0.5, 0.7):
    succ = 0
    for r in range(100):
        X, u, R, t, inl = make_data(100, eps, rng)
        cv2.setRNGSeed(r)
        ok, rv, tv, inliers = cv2.solvePnPRansac(X, u, K, None, iterationsCount=10000,
                                                 reprojectionError=tau, confidence=0.99,
                                                 flags=cv2.SOLVEPNP_P3P)
        if ok and rot_err_deg(cv2.Rodrigues(rv)[0], R) < 1.0:
            succ += 1
    print(f"    eps={eps}: thành công (sai số quay < 1°) {succ}/100")
    check(f"solvePnPRansac eps={eps}: thành công >= 95/100", succ >= 95)

# =============================================================================
# [3] Số nghiệm của LDP
# =============================================================================
print("=" * 78)
print("[3] Số nghiệm của bài toán định vị (§III-A, Phụ lục A)")
print("=" * 78)


def fb_quartic(Rab, Rac, Rbc, cab, cac, cbc):
    """Hệ số G4..G0 đúng như in ở (A19)–(A23), tr. 11–12."""
    K1 = Rbc ** 2 / Rac ** 2
    K2 = Rbc ** 2 / Rab ** 2
    G4 = (K1 * K2 - K1 - K2) ** 2 - 4 * K1 * K2 * cbc ** 2
    G3 = (4 * (K1 * K2 - K1 - K2) * K2 * (1 - K1) * cab
          + 4 * K1 * cbc * ((K1 * K2 + K2 - K1) * cac + 2 * K2 * cab * cbc))
    G2 = ((2 * K2 * (1 - K1) * cab) ** 2
          + 2 * (K1 * K2 + K1 - K2) * (K1 * K2 - K1 - K2)
          + 4 * K1 * ((K1 - K2) * cbc ** 2 + (1 - K2) * K1 * cac ** 2
                      - 2 * K2 * (1 + K1) * cab * cac * cbc))
    G1 = (4 * (K1 * K2 + K1 - K2) * K2 * (1 - K1) * cab
          + 4 * K1 * ((K1 * K2 - K1 + K2) * cac * cbc + 2 * K1 * K2 * cab * cac ** 2))
    G0 = (K1 * K2 + K1 - K2) ** 2 - 4 * K1 ** 2 * K2 * cac ** 2
    return np.array([G4, G3, G2, G1, G0]), K1, K2


def fb_p3p_legs(Rab, Rac, Rbc, cab, cac, cbc, tol=1e-10):
    """Giải hệ A* theo (A18)–(A28); trả về các bộ (a,b,c) dương thoả cả ba phương trình."""
    G, K1, K2 = fb_quartic(Rab, Rac, Rbc, cab, cac, cbc)
    sols = []
    for x in np.roots(G):
        if abs(x.imag) > 1e-5 * max(1, abs(x)) or x.real <= 0:
            continue
        x = x.real
        a = Rab / sqrt(max(x * x - 2 * x * cab + 1, 1e-300))
        b = a * x
        m, p, q = 1 - K1, 2 * (K1 * cac - x * cbc), x * x - K1
        m2, p2, q2 = 1.0, -2 * x * cbc, x * x * (1 - K2) + 2 * x * K2 * cab - K2
        den = m * q2 - m2 * q
        ys = []
        if abs(den) > 1e-12 * (abs(m * q2) + abs(m2 * q) + 1e-300):
            ys.append((p2 * q - p * q2) / den)                              # (A26)
        # (A27): nhánh dự phòng khi m'q ~ m q' (nghiệm kép) — mọi ứng viên đều được kiểm bằng (A1)–(A3)
        ys += [cac + sg * sqrt(max(cac ** 2 + (Rac ** 2 - a * a) / (a * a), 0)) for sg in (1, -1)]
        for y in ys:
            if y <= 0:
                continue
            v = np.array([a, b, y * a])
            for _ in range(8):   # Newton đánh bóng trên (A1)–(A3), chỉ để khử sai số làm tròn của nghiệm kép
                A_, B_, C_ = v
                F = np.array([A_*A_ + B_*B_ - 2*A_*B_*cab - Rab**2, A_*A_ + C_*C_ - 2*A_*C_*cac - Rac**2,
                              B_*B_ + C_*C_ - 2*B_*C_*cbc - Rbc**2])
                J = np.array([[2*A_ - 2*B_*cab, 2*B_ - 2*A_*cab, 0], [2*A_ - 2*C_*cac, 0, 2*C_ - 2*A_*cac],
                              [0, 2*B_ - 2*C_*cbc, 2*C_ - 2*B_*cbc]])
                try:
                    v = v - np.linalg.lstsq(J, F, rcond=None)[0]
                except np.linalg.LinAlgError:
                    break
            A_, B_, C_ = v
            r = [A_*A_ + B_*B_ - 2*A_*B_*cab - Rab**2, A_*A_ + C_*C_ - 2*A_*C_*cac - Rac**2,
                 B_*B_ + C_*C_ - 2*B_*C_*cbc - Rbc**2]
            if min(v) > 0 and max(abs(q_) for q_ in r) < tol * max(Rab, Rac, Rbc) ** 2 \
                    and np.linalg.norm(v - [a, b, y * a]) < 1e-3 * np.linalg.norm(v):
                if not any(np.allclose(v, s_, rtol=1e-6) for s_ in sols):
                    sols.append(tuple(v))
    return sols


def legs_problem(Lc, A, B, C):
    fa, fb, fc = [(P - Lc) / np.linalg.norm(P - Lc) for P in (A, B, C)]
    return (np.linalg.norm(A - B), np.linalg.norm(A - C), np.linalg.norm(B - C),
            fa @ fb, fa @ fc, fb @ fc)


def align(Pw, Pc):
    """Kabsch: Pc = R Pw + t."""
    mw, mc = Pw.mean(0), Pc.mean(0)
    U, _, Vt = np.linalg.svd((Pc - mc).T @ (Pw - mw))
    D = np.diag([1, 1, np.sign(np.linalg.det(U @ Vt))])
    R = U @ D @ Vt
    return R, mc - R @ mw


def poses_from_legs(Pw3, F3, legs):
    return [align(Pw3, F3 * np.array(l)[:, None]) for l in legs]


# (3a) Fig. 5: đáy đều cạnh 2√3, ba chân dài 4
A = np.array([2.0, 0, 0]); B = np.array([-1.0, sqrt(3), 0]); C = np.array([-1.0, -sqrt(3), 0])
L = np.array([0, 0, sqrt(12.0)])
prob = legs_problem(L, A, B, C)
G, K1, K2 = fb_quartic(*prob)
print(f"  Fig. 5: cos(alpha)={prob[3]:.6f} (bài: 5/8); hệ số (A18) = {np.round(G, 6)}")
check("Fig. 5: hệ số quartic = [-0.5625, 3.515625, -5.90625, 3.515625, -0.5625]",
      np.allclose(G, [-0.5625, 3.515625, -5.90625, 3.515625, -0.5625]))
print(f"    nghiệm quartic: {np.round(np.sort(np.roots(G).real), 6)}")
legs = fb_p3p_legs(*prob)
print(f"    bộ chân (a,b,c) tìm được: {[tuple(round(float(v), 6) for v in s_) for s_ in legs]}")
check("Fig. 5: đúng 4 nghiệm {(4,4,4),(1,4,4),(4,1,4),(4,4,1)}",
      sorted(np.round(legs, 6).tolist()) == sorted([[4, 4, 4], [1, 4, 4], [4, 1, 4], [4, 4, 1]]))
# thử cùng cấu hình qua OpenCV (điểm ảnh từ camera ở L nhìn xuống)
Rl = np.diag([1.0, -1.0, -1.0])            # trục z camera hướng xuống -z thế giới
tl = -Rl @ L
Pw = np.array([A, B, C])
uu = project(Pw, Rl, tl, K)
for flag, nm in [(cv2.SOLVEPNP_P3P, "P3P"), (cv2.SOLVEPNP_AP3P, "AP3P")]:
    nsol, rv, tv = cv2.solveP3P(Pw, uu, K, None, flag)
    valid = []
    for r_, t_ in zip(rv, tv):
        Rr = cv2.Rodrigues(r_)[0]
        if np.all(np.isfinite(Rr)) and np.max(np.abs(project(Pw, Rr, t_.ravel(), K) - uu)) < 1e-6:
            valid.append(tuple(round(float(v), 4) for v in np.linalg.norm(Pw @ Rr.T + t_.ravel(), axis=1)))
    print(f"    cv2.solveP3P[{nm}] trên cấu hình Fig. 5: trả {nsol} nghiệm, hợp lệ (tái chiếu < 1e-6 px) "
          f"{len(set(valid))}: {sorted(set(valid))}")

# (3b) hệ số in (A19)–(A23) với cấu hình ngẫu nhiên: x_thật = b/a có phải nghiệm?
rng = np.random.default_rng(3)
resid, counts, cv_counts, hist_ok = [], [], [], True
for _ in range(3000):
    X, u, uc, R, t = make_scene(3, rng)
    Xc = X @ R.T + t
    Lw = -R.T @ t
    prob = legs_problem(Lw, *X)
    a_, b_, c_ = np.linalg.norm(Xc, axis=1)
    G, *_ = fb_quartic(*prob)
    x = b_ / a_
    resid.append(abs(np.polyval(G, x)) / np.sum(np.abs(G) * np.abs(x) ** np.arange(4, -1, -1)))
    legs = fb_p3p_legs(*prob)
    counts.append(len(legs))
    if not any(np.allclose(l, (a_, b_, c_), rtol=1e-5) for l in legs):
        hist_ok = False
    cv_counts.append(cv2.solveP3P(X, uc, K, None, cv2.SOLVEPNP_P3P)[0])
resid = np.array(resid)
print(f"  (A19)–(A23) trên 3000 cấu hình ngẫu nhiên: |G(x_thật)| tương đối: trung vị {np.median(resid):.1e}, max {resid.max():.1e}")
check("hệ số (A19)–(A23) như bản in: x=b/a thật là nghiệm (sai số tương đối < 1e-8)", resid.max() < 1e-8)
check("bộ giải (A18)–(A28) luôn chứa nghiệm thật", hist_ok)
hc = np.bincount(counts, minlength=5); hv = np.bincount(cv_counts, minlength=5)
print(f"    histogram số nghiệm thực dương (0..4) — theo (A18)–(A28): {hc.tolist()} ; cv2 P3P: {hv.tolist()}")
check("không cấu hình nào có > 4 nghiệm", len(hc) <= 5 and len(hv) <= 5)

# (3c) Fig. 6: P4P có 2 nghiệm
L6 = np.array([0, 0, 144 / 5]); A6 = np.array([0, 12.0, 0]); B6 = np.array([10, -12.0, 0])
C6 = np.array([-10, -12.0, 0]); D6 = np.array([0, 0, -5.0]); P6 = np.array([0, -12.0, 0])
A6p = np.array([0, 828 / 169, 2880 / 169]); D6p = np.array([0, 0, 5.0])


def rot_x(th):
    c, s = np.cos(th), np.sin(th)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


va, vap = A6 - P6, A6p - P6
beta = np.arctan2(va[1] * vap[2] - va[2] * vap[1], va @ vap)
Rb = rot_x(beta)
col = lambda P, Q, Rr: np.linalg.norm(np.cross(Q - Rr, P - Rr)) / np.linalg.norm(Q - Rr) / np.linalg.norm(P - Rr)
print(f"  Fig. 6: cos(beta)={np.cos(beta):.6f} (bài: cos(alpha)=119/169={119/169:.6f}); "
      f"|A'P|={np.linalg.norm(vap):.6f}, Rb(A-P)+P-A'={np.linalg.norm(Rb@va+P6-A6p):.1e}, "
      f"Rb(D-P)+P-D'={np.linalg.norm(Rb@(D6-P6)+P6-D6p):.1e}")
check("Fig. 6: A' nằm trên LA, D' trên LD, cùng một phép quay quanh BC đưa A->A', D->D'",
      col(A6p, A6, L6) < 1e-12 and col(D6p, D6, L6) < 1e-12
      and np.linalg.norm(Rb @ va + P6 - A6p) < 1e-9 and np.linalg.norm(Rb @ (D6 - P6) + P6 - D6p) < 1e-9)
L6b = Rb.T @ (L6 - P6) + P6            # tâm chiếu thứ hai, trong hệ của A,B,C,D
Pw4 = np.array([A6, B6, C6, D6])


def angles(Lc, Pts):
    F = (Pts - Lc) / np.linalg.norm(Pts - Lc, axis=1, keepdims=True)
    return F @ F.T


print(f"    tâm thứ hai L''={np.round(L6b, 4)}; max|Δ cos góc| giữa hai tâm = {np.abs(angles(L6, Pw4)-angles(L6b, Pw4)).max():.1e}")
check("Fig. 6: hai tâm chiếu khác nhau nhìn A,B,C,D dưới cùng mọi góc cặp -> P4P 2 nghiệm",
      np.abs(angles(L6, Pw4) - angles(L6b, Pw4)).max() < 1e-12 and np.linalg.norm(L6 - L6b) > 1)


def count_consistent(Lc, Pts, tol=1e-7):
    """Giải P3P trên 3 điểm đầu (A18–A28), đếm các tư thế khớp tia của mọi điểm còn lại."""
    F = (Pts - Lc) / np.linalg.norm(Pts - Lc, axis=1, keepdims=True)
    prob = legs_problem(Lc, *Pts[:3])
    good = []
    for Rr, tt in poses_from_legs(Pts[:3], F[:3], fb_p3p_legs(*prob)):
        Xc = Pts @ Rr.T + tt
        fc = Xc / np.linalg.norm(Xc, axis=1, keepdims=True)
        if np.all(np.linalg.norm(np.cross(fc, F), axis=1) < tol) and np.all(np.sum(fc * F, 1) > 0):
            c_ = -Rr.T @ tt
            if not any(np.linalg.norm(c_ - g_) < 1e-6 for g_ in good):
                good.append(c_)
    return good


c4 = count_consistent(L6, np.array([B6, C6, A6, D6]))
print(f"    đếm lại bằng P3P(B,C,A) + kiểm D: {len(c4)} tư thế, tâm = {[tuple(round(float(v), 3) for v in c) for c in c4]}")
check("Fig. 6: P3P + kiểm điểm thứ 4 cho đúng 2 tư thế", len(c4) == 2)

# (3d) Fig. 7: thêm E = ảnh đối xứng của A' qua đường LP
d = (L6 - P6) / np.linalg.norm(L6 - P6)
mirror = lambda Q: 2 * (P6 + d * ((Q - P6) @ d)) - Q
E6, E6p = mirror(A6p), mirror(A6)
Pw5 = np.array([B6, C6, A6, D6, E6])
c5 = count_consistent(L6, Pw5)
dets = []
from itertools import combinations
for q4 in combinations(range(5), 4):
    Q = Pw5[list(q4)]
    dets.append(abs(np.linalg.det(np.c_[Q[1:] - Q[0]])))
print(f"  Fig. 7: E={np.round(E6, 3)}, E'={np.round(E6p, 3)}; Rb(E-P)+P-E'={np.linalg.norm(Rb@(E6-P6)+P6-E6p):.1e}; "
      f"số tư thế khớp cả 5 điểm = {len(c5)}")
print(f"    min |det| của mọi bộ 4 điểm (đồng phẳng nếu = 0): {min(dets):.3f}; A, D, E, L, P cùng nằm trên mặt x=0")
check("Fig. 7: P5P có 2 tư thế khớp cả 5 điểm", len(c5) == 2)
check("Fig. 7: không có 4 điểm nào đồng phẳng (tức 'general position' theo nghĩa đó)", min(dets) > 1e-6)

# (3e) 4 điểm đồng phẳng: nghiệm duy nhất? 4 điểm tổng quát ngẫu nhiên?
rng = np.random.default_rng(4)
cnt_pl, cnt_gen = [], []
for _ in range(2000):
    X, u, uc, R, t = make_scene(4, rng, planar=True)
    cnt_pl.append(len(count_consistent(-R.T @ t, X)))
    X, u, uc, R, t = make_scene(4, rng)
    cnt_gen.append(len(count_consistent(-R.T @ t, X)))
print(f"  4 điểm ngẫu nhiên, 2000 lần: số tư thế khớp (0..4) — đồng phẳng {np.bincount(cnt_pl, minlength=5).tolist()} ; "
      f"không đồng phẳng {np.bincount(cnt_gen, minlength=5).tolist()}")
check("4 điểm đồng phẳng: luôn đúng 1 tư thế (Phụ lục B)", set(cnt_pl) == {1})
check("4 điểm không đồng phẳng ngẫu nhiên: hầu như luôn 1 (2 nghiệm chỉ ở cấu hình đặc biệt như Fig. 6)",
      np.mean(np.array(cnt_gen) == 1) > 0.99)

# (3f) P6P: DLT 6 điểm — hạng 11 (duy nhất) khi tổng quát; mặt cắt nguy hiểm: điểm + tâm trên twisted cubic
def dlt_sv(X, uu):
    rows = []
    for (x, y, z), (p, q) in zip(X, uu):
        Xh = [x, y, z, 1]
        rows.append([*Xh, 0, 0, 0, 0, *[-p * v for v in Xh]])
        rows.append([0, 0, 0, 0, *Xh, *[-q * v for v in Xh]])
    return np.linalg.svd(np.array(rows), compute_uv=False)


rng = np.random.default_rng(5)
ranks = []
for _ in range(200):
    X, u, uc, R, t = make_scene(6, rng)
    s = dlt_sv(X, (uc - K[:2, 2]) / 800.0)
    ranks.append(int(np.sum(s > 1e-9 * s[0])))
print(f"  P6P ngẫu nhiên, 200 lần: hạng ma trận DLT 12x12 = {sorted(set(ranks))}")
check("6 điểm tổng quát: DLT hạng 11 -> ma trận chiếu duy nhất", set(ranks) == {11})
# twisted cubic X(s)=(s, s^2, s^3) qua tâm chiếu tại s0
Rt = np.array(cv2.Rodrigues(np.array([0.3, -0.2, 0.1]))[0])
curve = lambda s: np.array([s, s ** 2, s ** 3]) @ Rt.T + np.array([0, 0, 10.0])
Ccam = curve(-1.5)
ss = np.array([0.1, 0.3, 0.5, 0.7, 0.9, 1.1])
Xtc = np.array([curve(s) for s in ss])
# camera nhìn về trọng tâm các điểm
zc = Xtc.mean(0) - Ccam; zc /= np.linalg.norm(zc)
xc = np.cross([0, 1.0, 0], zc); xc /= np.linalg.norm(xc); yc = np.cross(zc, xc)
Rc = np.array([xc, yc, zc]); tc_ = -Rc @ Ccam
Xc_ = Xtc @ Rc.T + tc_
s = dlt_sv(Xtc, Xc_[:, :2] / Xc_[:, 2:3])
print(f"    6 điểm + tâm chiếu trên cùng một twisted cubic: độ sâu > 0: {bool(np.all(Xc_[:,2]>0))}; "
      f"hai giá trị kỳ dị nhỏ nhất / lớn nhất = {s[-2]/s[0]:.1e}, {s[-1]/s[0]:.1e}")
check("cấu hình tới hạn (twisted cubic qua tâm chiếu): DLT mất hạng (<= 10) -> P6P KHÔNG duy nhất",
      s[-2] / s[0] < 1e-9)

# =============================================================================
print("=" * 78)
npass = sum(ok for _, ok in RESULTS)
print(f"TỔNG: {npass}/{len(RESULTS)} PASS; thời gian {time.time()-T0:.1f}s")
for nm, ok in RESULTS:
    if not ok:
        print("  FAIL:", nm)
