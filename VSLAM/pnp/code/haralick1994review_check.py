"""Kiểm chứng số (cửa (b)) cho haralick1994review — Haralick, Lee, Ottenberg, Nölle, IJCV 1994.

Chạy:  python3 VSLAM/pnp/code/haralick1994review_check.py            (mặc định, < 3 phút)
       python3 VSLAM/pnp/code/haralick1994review_check.py --trials 10000  (đúng N1 của bài, lâu hơn)

Các phần:
 [1] chép công thức: phần dư của đa thức của cả sáu lời giải tại nghiệm thật
 [2] Grunert đầu-cuối: khôi phục R,t (Phụ lục I) + phân bố số nghiệm thực dương
 [3] Finsterwalder đầu-cuối, bản sửa và bản in ở tr. 7
 [4] hai trường hợp suy biến bài nêu ở tr. 13
 [5] thí nghiệm ổn định số: 6 hoán vị, single/double, so với Tab. II, IV, V
"""
import os
import sys
import time
import itertools
import argparse
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import common  # noqa: E402
import haralick1994review_p3p as H  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--trials", type=int, default=1500, help="số lần thử cho phần [5] (bài dùng 10000)")
ap.add_argument("--count-trials", type=int, default=10000, help="số cấu hình cho thống kê số nghiệm")
args = ap.parse_args()

T0 = time.time()
NFAIL = 0


def verdict(ok, msg):
    global NFAIL
    if not ok:
        NFAIL += 1
    print(("  PASS  " if ok else "  FAIL  ") + msg)


def relres(coeffs, x):
    """|P(x)| / sum |a_k x^k| — phần dư tương đối, không phụ thuộc thang đo của hệ số."""
    n = len(coeffs) - 1
    terms = np.array([coeffs[k] * x ** (n - k) for k in range(n + 1)])
    return abs(terms.sum()) / max(np.abs(terms).sum(), 1e-300)


def paper_scene(rng, zr):
    """Tam giác như §4.1 [tr. 14]: x,y ~ U[-25,25], z ~ U[f+a, b], f = 1, pose = đơn vị."""
    P = np.c_[rng.uniform(-25, 25, 3), rng.uniform(-25, 25, 3), rng.uniform(zr[0], zr[1], 3)]
    return P


# ============================================================================ [1]
print("[1] Chép công thức: phần dư tương đối của từng đa thức tại nghiệm thật (200 cảnh common.make_scene)")
rng = np.random.default_rng(1)
res = {k: [] for k in ["grunert9", "merritt22", "fb27", "linn52_printed", "linn52_fixed", "graf31",
                       "graf_det", "fin10_at_lam0", "fin_det13", "merritt_eq_grunert_swapped", "fb_eq_minus_merritt"]}
for _ in range(200):
    Xw, u, _, R, t = common.make_scene(3, rng)
    Xc = (R @ Xw.T).T + t
    f = common.bearings(u)
    a, b, c, ca, cb, cg, _ = H.triangle_data(Xw, f)
    s = np.linalg.norm(Xc, axis=1)
    uu, vv = s[1] / s[0], s[2] / s[0]
    A = H.grunert_coeffs(a, b, c, ca, cb, cg)
    res["grunert9"].append(relres(A, vv))
    Bm = H.merritt_coeffs(a, b, c, ca, cb, cg)
    res["merritt22"].append(relres(Bm, uu))
    D = H.fischler_bolles_coeffs(a, b, c, ca, cb, cg)
    res["fb27"].append(relres(D, uu))
    Tp, _ = H.linnainmaa_coeffs(a, b, c, ca, cb, cg, r2_as_printed=True)
    Tf, _ = H.linnainmaa_coeffs(a, b, c, ca, cb, cg, r2_as_printed=False)
    res["linn52_printed"].append(relres(Tp, s[0] ** 2))
    res["linn52_fixed"].append(relres(Tf, s[0] ** 2))
    lam = rng.normal()
    val = H.grafarend_31(uu, vv, lam, a, b, c, ca, cb, cg)
    scale = a * a + b * b + c * c
    res["graf31"].append(abs(val) / scale)
    # Finsterwalder: lambda0 là nghiệm của (14) => định thức (13) = 0 và (10) đúng tại (u,v) thật
    lams = np.roots(H.finsterwalder_cubic(a, b, c, ca, cb, cg))
    lam0 = lams[np.argmin(np.abs(lams.imag))].real
    Af, Bf, Cf, Df, Ef, Ff = H.finsterwalder_ABCDEF(lam0, a, b, c, ca, cb, cg)
    M = np.array([[Af, Bf, Df], [Bf, Cf, Ef], [Df, Ef, Ff]])
    res["fin_det13"].append(abs(np.linalg.det(M)) / np.prod(np.linalg.norm(M, axis=1)))
    conic = Af * uu ** 2 + 2 * Bf * uu * vv + Cf * vv ** 2 + 2 * Df * uu + 2 * Ef * vv + Ff
    res["fin10_at_lam0"].append(abs(conic) / (abs(Af) * uu ** 2 + abs(Cf) * vv ** 2 + abs(Ff) + 1e-300))
    # Grafarend: det(A(lambda)) là bậc ba; nghiệm của nó làm A suy biến (tr. 10)
    dets = [np.linalg.det(H.grafarend_A(x, a, b, c, ca, cb, cg)) for x in (-1.0, 0.0, 1.0, 2.0)]
    cub = np.polyfit([-1.0, 0.0, 1.0, 2.0], dets, 3)
    lg = np.roots(cub); lg = lg[np.argmin(np.abs(lg.imag))].real
    Ag = H.grafarend_A(lg, a, b, c, ca, cb, cg)
    sv = np.linalg.svd(Ag, compute_uv=False)
    res["graf_det"].append(sv[-1] / sv[0])
    # Nhận xét tr. 12: đổi b<->c, beta<->gamma trong (9) cho ra (22)
    Asw = H.grunert_coeffs(a, c, b, ca, cg, cb) * c ** 4
    res["merritt_eq_grunert_swapped"].append(np.max(np.abs(Asw - Bm)) / np.max(np.abs(Bm)))
    res["fb_eq_minus_merritt"].append(np.max(np.abs(D + Bm)) / np.max(np.abs(Bm)))

tol = 1e-9
for k, lab in [("grunert9", "Grunert eq.(9) tại v=s3/s1"),
               ("merritt22", "Merritt eq.(22) tại u=s2/s1"),
               ("fb27", "Fischler-Bolles eq.(27) tại u=s2/s1"),
               ("graf31", "Grafarend eq.(31) tại (p,q)=(s2/s1,s3/s1), lambda ngẫu nhiên"),
               ("graf_det", "Grafarend: det A(lambda) có nghiệm thực làm A hạng 2 (sigma_min/sigma_max)"),
               ("fin_det13", "Finsterwalder: nghiệm của cubic (14) làm định thức (13) = 0"),
               ("fin10_at_lam0", "Finsterwalder: conic (10) tại (u,v) thật với lambda0"),
               ("merritt_eq_grunert_swapped", "tr.12: (9) với b<->c, beta<->gamma, nhân c^4 == (22)"),
               ("fb_eq_minus_merritt", "(27) == -(22) (tôi suy ra: D_i = -B_i)"),
               ("linn52_printed", "Linnainmaa eq.(52), r2 CHÉP ĐÚNG BẢN IN (-c^2 q5 - b^2 q6)"),
               ("linn52_fixed", "Linnainmaa eq.(52), r2 tôi sửa (-c^2 q5^2 - b^2 q6^2)")]:
    mx = float(np.max(res[k]))
    verdict(mx < tol, f"{lab:74s} max={mx:.1e}")
print("  (FAIL ở dòng 'r2 CHÉP ĐÚNG BẢN IN' là kết quả mong đợi nếu bản in có lỗi — xem ghi chú mục 8)")

# ============================================================================ [2]
print("\n[2] Grunert đầu-cuối (eq. (4),(5),(8),(9) + Phụ lục I), cảnh common.make_scene, nhiễu 0")


def valid_solutions(sols, a, b, c, ca, cb, cg, tol=1e-6):
    """nghiệm thực, cả ba s_i > 0, thoả (1)-(3) với sai số tương đối < tol, đã khử trùng."""
    out = []
    for s in sols:
        s1, s2, s3 = s
        if min(s) <= 0:
            continue
        e = max(abs(s2 * s2 + s3 * s3 - 2 * s2 * s3 * ca - a * a) / a ** 2,
                abs(s1 * s1 + s3 * s3 - 2 * s1 * s3 * cb - b * b) / b ** 2,
                abs(s1 * s1 + s2 * s2 - 2 * s1 * s2 * cg - c * c) / c ** 2)
        if e < tol and all(np.linalg.norm(s - o) > 1e-7 * np.linalg.norm(s) for o in out):
            out.append(s)
    return out


rng = np.random.default_rng(2)
N2 = 2000
serr, rerr, terr, orth, max_nsol = [], [], [], [], 0
for _ in range(N2):
    Xw, u, _, R, t = common.make_scene(3, rng)
    f = common.bearings(u)
    a, b, c, ca, cb, cg, fn = H.triangle_data(Xw, f)
    s_true = np.linalg.norm((R @ Xw.T).T + t, axis=1)
    sols = valid_solutions(H.grunert(Xw, f), a, b, c, ca, cb, cg)
    max_nsol = max(max_nsol, len(sols))
    if not sols:
        serr.append(np.inf); rerr.append(np.inf); terr.append(np.inf); continue
    s = min(sols, key=lambda s: np.linalg.norm(s - s_true))
    serr.append(np.linalg.norm(s - s_true) / np.linalg.norm(s_true))
    Re, te, _ = H.absolute_orientation_appendixI(s[:, None] * fn, Xw)
    rerr.append(np.linalg.norm(Re - R))          # Frobenius: rot_err_deg bị đánh lừa khi Re không trực chuẩn
    terr.append(common.trans_err_rel(te, t))
    orth.append(np.linalg.norm(Re.T @ Re - np.eye(3)))
serr, rerr, terr, orth = map(np.array, (serr, rerr, terr, orth))
pc = lambda x: "trung vị {:.1e}, p99 {:.1e}, max {:.1e}".format(*np.percentile(x, [50, 99, 100]))
verdict(np.isfinite(serr).all() and serr.max() < 1e-5, f"|s - s_thật|/|s_thật|        : {pc(serr)}")
verdict(rerr.max() < 1e-4, f"||R_PhụlụcI - R||_F         : {pc(rerr)}")
verdict(terr.max() < 1e-4, f"|t - t_thật|/|t_thật|        : {pc(terr)}")
print(f"    ||R^T R - I|| của R Phụ lục I (không ép trực chuẩn): {pc(orth)}")
print("    (đuôi dài của sai số s tương quan với |P'(v)| nhỏ — gần nghiệm kép — và mẫu (8) nhỏ; xem mục 7)")
verdict(max_nsol <= 4, f"số nghiệm thực dương tối đa gặp = {max_nsol} (<= 4)")

print(f"\n    Phân bố số nghiệm thực dương (Grunert, đối chiếu cv2.solveP3P), {args.count_trials} cấu hình mỗi loại:")
import cv2  # noqa: E402
for name, gen in [("common.make_scene (FOV ~44 deg, z 4-8)", "common"),
                  ("như §4.1 bài: x,y~U[-25,25], z~U[1,5], f=1", "paper15"),
                  ("như §4.1 bài: z~U[5,20]", "paper520")]:
    rng = np.random.default_rng(3)
    hist = np.zeros(6, int)
    agree = 0
    for _ in range(args.count_trials):
        if gen == "common":
            Xw, u, _, R, t = common.make_scene(3, rng)
            f = common.bearings(u)
            Kc = common.K_DEFAULT
            uimg = u
        else:
            P = paper_scene(rng, (1, 5) if gen == "paper15" else (5, 20))
            Xw = P
            f = P / np.linalg.norm(P, axis=1, keepdims=True)
            Kc = np.eye(3)
            uimg = P[:, :2] / P[:, 2:3]
        a, b, c, ca, cb, cg, _ = H.triangle_data(Xw, f)
        n = len(valid_solutions(H.grunert(Xw, f), a, b, c, ca, cb, cg))
        hist[min(n, 5)] += 1
        try:
            nc, _, _ = cv2.solveP3P(Xw.astype(np.float64), uimg.astype(np.float64), Kc, None, flags=cv2.SOLVEPNP_P3P)
        except cv2.error:
            nc = -1
        agree += (nc == n)
    frac = hist / hist.sum()
    print(f"    {name:44s} 0:{frac[0]:.3f} 1:{frac[1]:.3f} 2:{frac[2]:.3f} 3:{frac[3]:.3f} 4:{frac[4]:.3f} >4:{frac[5]:.3f}"
          f" | trùng số nghiệm với cv2 {agree / args.count_trials:.3f}")
    verdict(hist[5] == 0, f"{name}: số cấu hình >4 nghiệm = {hist[5]}; (0 nghiệm hợp lệ: {hist[0]} cấu hình"
            f" — bộ lọc thực/dư của tôi loại mất nghiệm gần kép, không phải khẳng định của bài)")

# ============================================================================ [3]
print("\n[3] Finsterwalder đầu-cuối (eq. (10)-(17)), 2000 cảnh common.make_scene, nhiễu 0")
for printed in (False, True):
    rng = np.random.default_rng(2)
    ok = 0
    errs = []
    for _ in range(2000):
        Xw, u, _, R, t = common.make_scene(3, rng)
        f = common.bearings(u)
        a, b, c, ca, cb, cg, fn = H.triangle_data(Xw, f)
        s_true = np.linalg.norm((R @ Xw.T).T + t, axis=1)
        sols = H.finsterwalder(Xw, f, as_printed_p7=printed)
        err = min([np.linalg.norm(s - s_true) / np.linalg.norm(s_true) for s in sols] + [np.inf])
        ok += err < 1e-6
        errs.append(err)
    lab = "hệ số A,C CHÉP ĐÚNG BẢN IN tr.7 (b^2-mc^2, -cn^2)" if printed else "hệ số A,C lấy từ eq.(16) (b^2-m^2c^2, -c^2n^2)"
    verdict(ok == 2000, f"{lab}: tìm lại s thật (sai số tương đối < 1e-6) trong {ok}/2000 cảnh;"
            f" trung vị sai số {np.median(errs):.1e}")
print("  (FAIL ở dòng 'CHÉP ĐÚNG BẢN IN' là mong đợi nếu tr.7 in sai — xem ghi chú mục 8)")
# công thức v_small ở tr. 5
rng = np.random.default_rng(5)
bad = nreal = 0
for _ in range(200):
    Xw, u, _, R, t = common.make_scene(3, rng)
    f = common.bearings(u)
    a, b, c, ca, cb, cg, _ = H.triangle_data(Xw, f)
    lam = rng.normal()
    A_, B_, C_, D_, E_, F_ = H.finsterwalder_ABCDEF(lam, a, b, c, ca, cb, cg)
    uu = rng.uniform(0.5, 2)
    r = np.roots([C_, 2 * (B_ * uu + E_), A_ * uu ** 2 + 2 * D_ * uu + F_])
    if np.any(np.abs(r.imag) > 1e-12):
        continue
    nreal += 1
    vl = r[np.argmax(np.abs(r))].real
    vs_printed = C_ / (A_ * vl)
    vs_true = r[np.argmin(np.abs(r))].real
    bad += abs(vs_printed - vs_true) > 1e-6 * abs(vs_true)
print(f"    tr.5: 'v_small = C/(A v_large)' khác nghiệm nhỏ thật trong {bad}/{nreal} trường hợp có nghiệm thực "
      f"(đúng phải là (A u^2+2Du+F)/(C v_large) — tôi suy ra)")

# ============================================================================ [4]
print("\n[4] Trường hợp suy biến bài nêu ở tr. 13")
# (a) đồng viên: a=b=c, alpha=gamma=60, beta=120 -> mọi hệ số bằng 0
c60, c120 = np.cos(np.radians(60)), np.cos(np.radians(120))
A = H.grunert_coeffs(1.0, 1.0, 1.0, c60, c120, c60)
Bm = H.merritt_coeffs(1.0, 1.0, 1.0, c60, c120, c60)
D = H.fischler_bolles_coeffs(1.0, 1.0, 1.0, c60, c120, c60)
Tl, _ = H.linnainmaa_coeffs(1.0, 1.0, 1.0, c60, c120, c60, r2_as_printed=False)
Gc = H.finsterwalder_cubic(1.0, 1.0, 1.0, c60, c120, c60)
print(f"    Grunert A = {np.round(A, 12)}\n    Merritt B = {np.round(Bm, 12)}\n    F&B D     = {np.round(D, 12)}"
      f"\n    Linnainmaa t (r2 sửa) = {np.round(Tl, 12)}\n    Finsterwalder G,H,I,J = {np.round(Gc, 12)}")
verdict(max(np.abs(A).max(), np.abs(Bm).max(), np.abs(D).max()) < 1e-12,
        "đồng viên: mọi hệ số của (9), (22), (27) bằng 0 như bài nói")
# (b) tứ diện đều: a=b=c, alpha=beta=gamma=60 -> v=1 là nghiệm và mẫu của (8) bằng 0
A = H.grunert_coeffs(1.0, 1.0, 1.0, c60, c60, c60)
print(f"    tứ diện đều: A = {np.round(A, 12)}, P(1) = {np.polyval(A, 1.0):.1e}, mẫu (8) tại v=1: "
      f"{2 * (c60 - 1.0 * c60):.1e}, tử (8) tại v=1: {(-1) * 1 - 0 + 1:.1e}")
verdict(abs(np.polyval(A, 1.0)) < 1e-12, "tứ diện đều: v=1 là nghiệm của (9) và (8) thành 0/0")

# ============================================================================ [5]
print(f"\n[5] Ổn định số theo thứ tự điểm (6 hoán vị), N = {args.trials} thử mỗi độ sâu, f = 1, "
      f"x,y~U[-25,25] (như §4.1-4.2)")
print("    ADE = tổng 3 khoảng cách |p_tính - p_thật| (tr. 15); chọn nghiệm gần thật nhất; MADE = trung bình")
PERMS = list(itertools.permutations(range(3)))


def run_solver(name, P, dt):
    """P (3,3) điểm trong hệ camera (float64, thật). Trả về ADE (float64) hoặc nan nếu thất bại."""
    uv = (P[:, :2] / P[:, 2:3]).astype(dt)                        # ảnh, f = 1
    jj = np.c_[uv, np.ones(3, dt)]
    jj = jj / np.sqrt((jj * jj).sum(1, keepdims=True))
    Pd = P.astype(dt)
    sols = H.grunert(Pd, jj, dt) if name == "grunert" else H.finsterwalder(Pd, jj, dt)
    if not sols:
        return np.nan
    best = np.inf
    for s in sols:
        pc = (s[:, None] * jj).astype(np.float64)
        best = min(best, np.linalg.norm(pc - P, axis=1).sum())
    return best


def swn_grunert(P):
    """S_wn (A.2.5, tr. 25) của nghiệm v thật cho đa thức (9) — tính bằng double."""
    f = P / np.linalg.norm(P, axis=1, keepdims=True)
    a, b, c, ca, cb, cg, _ = H.triangle_data(P, f)
    A = H.grunert_coeffs(a, b, c, ca, cb, cg)
    s = np.linalg.norm(P, axis=1)
    x = s[2] / s[0]
    dP = np.polyval(np.polyder(A), x)
    pw = np.arange(4, -1, -1)
    return np.sum(np.abs(A * x ** (pw - 1) / dP))


paper = {  # MADE bài báo, Sun 3/280, 10000 thử, 1<z<5 (Tab. II random; Tab. III, IV best/worst)
    ("grunert", "f64"): (0.19e-8, 0.41e-12, 0.60e-8), ("grunert", "f32"): (0.31e-1, 0.10e-3, 0.81e-1),
    ("finster", "f64"): (0.22e-10, 0.34e-12, 0.20e-9), ("finster", "f32"): (0.89e-2, 0.74e-4, 0.59e-1)}
for zr in [(1, 5), (5, 20)]:
    rng = np.random.default_rng(7)
    scenes = [paper_scene(rng, zr) for _ in range(args.trials)]
    pick = rng.integers(0, 6, args.trials)
    print(f"\n    độ sâu {zr[0]} < z < {zr[1]}")
    print(f"    {'lời giải':9s} {'prec':4s} {'thất bại':>8s} {'MADE random':>12s} {'MADE best':>11s} {'MADE worst':>11s}"
          f" {'rand/best':>10s} {'worst/best':>10s} {'trung vị r/b/w':>27s} {'%w/b>1e3':>8s} | bài (random, best, worst){'' if zr == (1, 5) else ' — chỉ có cho 1<z<5'}")
    for name in ("grunert", "finster"):
        for prec, dt in (("f64", np.float64), ("f32", np.float32)):
            E = np.full((args.trials, 6), np.nan)
            for i, P in enumerate(scenes):
                for k, pm in enumerate(PERMS):
                    E[i, k] = run_solver("grunert" if name == "grunert" else "finster", P[list(pm)], dt)
            fail = np.isnan(E).any(1)
            Eg = E[~fail]
            rnd = Eg[np.arange(len(Eg)), pick[~fail]].mean()
            bst, wst = Eg.min(1).mean(), Eg.max(1).mean()
            ref = paper[(name, prec)] if zr == (1, 5) else None
            refs = f"{ref[0]:.2e}, {ref[1]:.2e}, {ref[2]:.2e}" if ref else "-"
            med = (np.median(Eg[np.arange(len(Eg)), pick[~fail]]), np.median(Eg.min(1)), np.median(Eg.max(1)))
            print(f"    {name:9s} {prec:4s} {fail.sum():8d} {rnd:12.2e} {bst:11.2e} {wst:11.2e} {rnd / bst:10.1f}"
                  f" {wst / bst:10.1f} {med[0]:9.1e}/{med[1]:.1e}/{med[2]:.1e} {100 * np.mean(Eg.max(1) > 1e3 * Eg.min(1)):8.1f} | {refs}")
            if name == "grunert" and prec == "f64":
                Sw = np.array([[swn_grunert(P[list(pm)]) for pm in PERMS] for P in scenes])[~fail]
                sel = Eg[np.arange(len(Eg)), Sw.argmin(1)].mean()
                print(f"    {'':9s} {'':4s} chọn hoán vị theo S_wn nhỏ nhất (oracle nghiệm): MADE {sel:.2e}"
                      f"  (bài Tab. V/VI: {'0.89e-12 / 9.18e-12' if zr == (1, 5) else '0.58e-11 / 3.76e-12'})")
                GR = (rnd, bst, wst, sel)
    print(f"    [{time.time() - T0:.0f}s]")
    if zr == (1, 5):
        verdict(GR[2] / GR[1] > 100, f"Grunert f64: worst/best = {GR[2] / GR[1]:.0f} (bài: ~1e4, Tab. IV) — cỡ >=100 lần")
        verdict(GR[3] < GR[0], f"Grunert f64: chọn theo S_wn ({GR[3]:.1e}) tốt hơn chọn ngẫu nhiên ({GR[0]:.1e})")

print(f"\nTổng: {NFAIL} dòng FAIL; thời gian {time.time() - T0:.0f}s")
