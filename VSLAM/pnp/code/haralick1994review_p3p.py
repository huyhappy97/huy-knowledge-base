"""Cài lại các lời giải P3P đúng như chúng được IN trong haralick1994review (IJCV 13(3), 1994).

Chỉ phục vụ kiểm chứng số (cửa (b)); không tối ưu tốc độ. Mọi phép tính giữ nguyên kiểu dữ liệu
`dt` (np.float32 hoặc np.float64) để mô phỏng thí nghiệm "single / double precision" của bài.

Ký hiệu của bài -> khảo sát:
  j_i (tia đơn vị)  = f_i (bearing);  s_i = khoảng cách tâm chiếu -> điểm i = độ dài của X_c,i
  p_i (điểm trong hệ camera) = X_c,i;  p'_i (điểm trong hệ thế giới) = X_w,i
  p_i = R p'_i + T  [eq. (54), (a.1)]  <=>  X_c = R X_w + t
  a = |p2-p3|, b = |p1-p3|, c = |p1-p2|;  cos(alpha)=j2.j3, cos(beta)=j1.j3, cos(gamma)=j1.j2
"""
import numpy as np


def _roots(coeffs, dt):
    """Nghiệm đa thức (hệ số bậc cao trước) bằng trị riêng ma trận đồng hành, tính trong kiểu dt.
    (Bài dùng phương pháp Laguerre [A.2.3]; ở đây dùng eigvals — khác bộ tìm nghiệm, xem ghi chú.)"""
    c = np.asarray(coeffs, dtype=dt)
    # bỏ hệ số dẫn đầu bằng 0 đúng
    k = 0
    while k < len(c) - 1 and c[k] == 0:
        k += 1
    c = c[k:]
    n = len(c) - 1
    if n < 1:
        return np.array([], dtype=np.complex64 if dt == np.float32 else np.complex128)
    M = np.zeros((n, n), dtype=dt)
    M[0, :] = -c[1:] / c[0]
    if n > 1:
        M[1:, :-1] = np.eye(n - 1, dtype=dt)
    return np.linalg.eigvals(M)


def _real(r, dt, tol=None):
    if tol is None:
        tol = 1e-3 if dt == np.float32 else 1e-7
    out = [z.real for z in r if abs(z.imag) <= tol * max(1.0, abs(z))]
    return [dt(x) for x in out]


def triangle_data(Xw, f, dt=np.float64):
    """a,b,c từ tam giác 3D; cos alpha, beta, gamma từ ba tia đơn vị (bài: §2, tr. 3)."""
    Xw = np.asarray(Xw, dtype=dt)
    f = np.asarray(f, dtype=dt)
    f = f / np.linalg.norm(f, axis=1, keepdims=True)
    a = np.linalg.norm(Xw[1] - Xw[2])
    b = np.linalg.norm(Xw[0] - Xw[2])
    c = np.linalg.norm(Xw[0] - Xw[1])
    ca = f[1] @ f[2]
    cb = f[0] @ f[2]
    cg = f[0] @ f[1]
    return a, b, c, ca, cb, cg, f


# ---------------------------------------------------------------- Grunert  [tr. 3-4, eq. (1)-(9)]
def grunert_coeffs(a, b, c, ca, cb, cg):
    """A4..A0 của eq. (9), chép đúng dạng in ở tr. 4."""
    a2, b2, c2 = a * a, b * b, c * c
    K1 = (a2 - c2) / b2          # (a^2-c^2)/b^2
    K2 = (a2 + c2) / b2          # (a^2+c^2)/b^2
    two, four = a2 * 0 + 2, a2 * 0 + 4
    A4 = (K1 - 1) ** 2 - four * c2 / b2 * ca ** 2
    A3 = four * (K1 * (1 - K1) * cb - (1 - K2) * ca * cg + two * c2 / b2 * ca ** 2 * cb)
    A2 = two * (K1 ** 2 - 1 + two * K1 ** 2 * cb ** 2 + two * (b2 - c2) / b2 * ca ** 2
                - four * K2 * ca * cb * cg + two * (b2 - a2) / b2 * cg ** 2)
    A1 = four * (-K1 * (1 + K1) * cb + two * a2 / b2 * cg ** 2 * cb - (1 - K2) * ca * cg)
    A0 = (1 + K1) ** 2 - four * a2 / b2 * cg ** 2
    return np.array([A4, A3, A2, A1, A0])


def grunert(Xw, f, dt=np.float64, return_coeffs=False):
    """Trả về danh sách (s1,s2,s3) (có thể có dấu âm — lọc sau) theo Grunert [eq. (4),(5),(8),(9)]."""
    a, b, c, ca, cb, cg, _ = triangle_data(Xw, f, dt)
    A = grunert_coeffs(a, b, c, ca, cb, cg)
    K1 = (a * a - c * c) / (b * b)
    sols = []
    for v in _real(_roots(A, dt), dt):
        den = 2 * (cg - v * ca)                               # mẫu của eq. (8)
        if den == 0:
            continue
        u = ((-1 + K1) * v * v - 2 * K1 * cb * v + 1 + K1) / den   # eq. (8)
        s1sq = b * b / (1 + v * v - 2 * v * cb)               # eq. (5), dạng b^2 (tôi chọn)
        if not (s1sq > 0):
            continue
        s1 = np.sqrt(s1sq)
        sols.append(np.array([s1, u * s1, v * s1], dtype=dt))  # eq. (4)
    return (sols, A) if return_coeffs else sols


# ---------------------------------------------------------------- Finsterwalder  [tr. 5-7, eq. (10)-(17)]
def finsterwalder_cubic(a, b, c, ca, cb, cg):
    """G,H,I,J của eq. (14)."""
    a2, b2, c2 = a * a, b * b, c * c
    sa2, sb2, sg2 = 1 - ca * ca, 1 - cb * cb, 1 - cg * cg
    G = c2 * (c2 * sb2 - b2 * sg2)
    H = b2 * (b2 - a2) * sg2 + c2 * (c2 + 2 * a2) * sb2 + 2 * b2 * c2 * (-1 + ca * cb * cg)
    I = b2 * (b2 - c2) * sa2 + a2 * (a2 + 2 * c2) * sb2 + 2 * a2 * b2 * (-1 + ca * cb * cg)
    J = a2 * (a2 * sb2 - b2 * sa2)
    return np.array([G, H, I, J])


def finsterwalder_ABCDEF(lam, a, b, c, ca, cb, cg):
    """Hệ số của conic (10) theo lambda [tr. 5]."""
    a2, b2, c2 = a * a, b * b, c * c
    A = 1 + lam
    B = -ca
    C = (b2 - a2) / b2 - lam * c2 / b2
    D = -lam * cg
    E = (a2 / b2 + lam * c2 / b2) * cb
    F = -a2 / b2 + lam * (b2 - c2) / b2
    return A, B, C, D, E, F


def finsterwalder(Xw, f, dt=np.float64, as_printed_p7=False):
    """as_printed_p7=True dùng đúng hệ số A = b^2 - m c^2, C = -c n^2 in ở tr. 7 (khối "numerically
    stable way"); False dùng hệ số của chính eq. (16): b^2 - m^2 c^2, -c^2 n^2."""
    a, b, c, ca, cb, cg, _ = triangle_data(Xw, f, dt)
    lams = _real(_roots(finsterwalder_cubic(a, b, c, ca, cb, cg), dt), dt, tol=1e-2 if dt == np.float32 else 1e-6)
    # Bài chỉ nói "Solve this equation for any root lambda0" [tr. 7]. Chọn của tôi: nghiệm thực
    # làm cho cả B^2-AC và E^2-CF không âm, ưu tiên min(...) lớn nhất.
    best, score = None, -np.inf
    for lam in lams:
        A, B, C, D, E, F = finsterwalder_ABCDEF(lam, a, b, c, ca, cb, cg)
        sc = min(B * B - A * C, E * E - C * F)
        if sc > score:
            best, score = lam, sc
    if best is None:
        return []
    lam = best
    A, B, C, D, E, F = finsterwalder_ABCDEF(lam, a, b, c, ca, cb, cg)
    p = np.sqrt(max(B * B - A * C, dt(0)))                                   # eq. (15)
    q = np.sign(B * E - C * D) * np.sqrt(max(E * E - C * F, dt(0)))          # eq. (15)
    sols = []
    a2, b2, c2 = a * a, b * b, c * c
    for sgn in (dt(1), dt(-1)):
        m = (-B + sgn * p) / C
        n = (-E + sgn * q) / C                                               # v = u m + n
        Aq = (b2 - m * c2) if as_printed_p7 else (b2 - m * m * c2)          # eq. (16)
        Bq = c2 * (cb - n) * m - b2 * cg
        Cq = ((-c * n * n) if as_printed_p7 else (-c2 * n * n)) + 2 * c2 * n * cb + b2 - c2
        disc = Bq * Bq - Aq * Cq
        if disc < 0 or Aq == 0:
            continue
        ul = -np.sign(Bq) / Aq * (abs(Bq) + np.sqrt(disc))                   # u_large [tr. 7]
        us = Cq / (Aq * ul) if ul != 0 else ul                               # u_small
        for u in (ul, us):
            v = u * m + n
            s1sq = b2 / (1 + v * v - 2 * v * cb)                             # eq. (5)
            if s1sq > 0:
                s1 = np.sqrt(s1sq)
                sols.append(np.array([s1, u * s1, v * s1], dtype=dt))
    return sols


# ---------------------------------------------------------------- các đa thức khác, chỉ để kiểm phần dư
def merritt_coeffs(a, b, c, ca, cb, cg):
    """B4..B0 của eq. (22) [tr. 8], ẩn u = s2/s1."""
    a2, b2, c2 = a * a, b * b, c * c
    B4 = (b2 + c2 - a2) ** 2 - 4 * b2 * c2 * ca ** 2
    B0 = (a2 + c2 - b2) ** 2 - 4 * a2 * c2 * cb ** 2
    K = 2 * (b2 + c2 - a2) * (a2 + c2 - b2) * cg + 4 * c2 * (a2 + b2 - c2) * ca * cb
    B3 = K - 2 * B4 * cg
    B2 = B4 + B0 - 2 * K * cg + 4 * c2 * c2 * (ca ** 2 + cb ** 2 + cg ** 2 - 2 * ca * cb * cg - 1)
    B1 = K - 2 * B0 * cg
    return np.array([B4, B3, B2, B1, B0])


def fischler_bolles_coeffs(a, b, c, ca, cb, cg):
    """D4..D0 của eq. (27) [tr. 9], ẩn u = s2/s1."""
    a2, b2, c2 = a * a, b * b, c * c
    D4 = 4 * b2 * c2 * ca ** 2 - (a2 - b2 - c2) ** 2
    D3 = (-4 * c2 * (a2 + b2 - c2) * ca * cb - 8 * b2 * c2 * ca ** 2 * cg
          + 4 * (a2 - b2 - c2) * (a2 - b2) * cg)
    D2 = (4 * c2 * (a2 - c2) * cb ** 2 + 8 * c2 * (a2 + b2) * ca * cb * cg + 4 * c2 * (b2 - c2) * ca ** 2
          - 2 * (a2 - b2 - c2) * (a2 - b2 + c2) - 4 * (a2 - b2) ** 2 * cg ** 2)
    D1 = (-8 * a2 * c2 * cb ** 2 * cg - 4 * c2 * (b2 - c2) * ca * cb - 4 * a2 * c2 * ca * cb
          + 4 * (a2 - b2) * (a2 - b2 + c2) * cg)
    D0 = 4 * a2 * c2 * cb ** 2 - (a2 - b2 + c2) ** 2
    return np.array([D4, D3, D2, D1, D0])


def grafarend_31(p, q, lam, a, b, c, ca, cb, cg):
    """Vế trái eq. (31) [tr. 10], p = s2/s1, q = s3/s1."""
    a2, b2, c2 = a * a, b * b, c * c
    return ((a2 - c2 - lam * b2) * p * p + 2 * c2 * ca * p * q + c2 * (-1 + lam) * q * q
            + 2 * (-a2 + lam * b2) * cg * p - 2 * lam * c2 * cb * q + a2 - lam * (b2 - c2))


def grafarend_A(lam, a, b, c, ca, cb, cg):
    """Ma trận A của eq. (30) [tr. 10]."""
    a2, b2, c2 = a * a, b * b, c * c
    return np.array([
        [(a2 - lam * (b2 - c2)) / c2, (lam * b2 - a2) * cg / c2, -lam * cb],
        [(lam * b2 - a2) * cg / c2, (a2 - c2 - lam * b2) / c2, ca],
        [-lam * cb, ca, -1 + lam]])


def linnainmaa_coeffs(a, b, c, ca, cb, cg, r2_as_printed=True):
    """t8,t6,t4,t2,t0 của eq. (52) [tr. 11], ẩn s1^2, qua q1..q6 (47) và r1..r5 (51).
    r2_as_printed=True: r2 chép đúng bản in (-c^2 q5 - b^2 q6); False: bản tôi tự suy dẫn
    (-c^2 q5^2 - b^2 q6^2)."""
    a2, b2, c2 = a * a, b * b, c * c
    q1 = 1 - cg ** 2
    q2 = 1 - cb ** 2
    q3 = 2 * (cg ** 2 - ca * cb * cg + cb ** 2 - 1)
    q4 = c2 + b2 - a2
    q5 = 2 * (ca * cb - cg)
    q6 = 2 * (ca * cg - cb)
    r1 = q3 ** 2 + 4 * q1 * q2 * ca ** 2 + q1 * q5 ** 2 + q2 * q6 ** 2
    if r2_as_printed:
        r2 = 2 * q3 * q4 - 4 * (c2 * q2 + b2 * q1) * ca ** 2 - c2 * q5 - b2 * q6
    else:
        r2 = 2 * q3 * q4 - 4 * (c2 * q2 + b2 * q1) * ca ** 2 - c2 * q5 ** 2 - b2 * q6 ** 2
    r3 = q4 ** 2 + 4 * ca ** 2 * b2 * c2
    r4 = 4 * ca * q3 + 2 * q5 * q6
    r5 = 4 * ca * q4
    t8 = r1 ** 2 - r4 ** 2 * q1 * q2
    t6 = (b2 * q1 + c2 * q2) * r4 ** 2 - 2 * r4 * r5 * q1 * q2 + 2 * r1 * r2
    t4 = r2 ** 2 - b2 * c2 * r4 ** 2 - r5 ** 2 * q1 * q2 + 2 * r4 * r5 * b2 * q1 + 2 * r4 * r5 * c2 * q2 + 2 * r1 * r3
    t2 = (b2 * q1 + c2 * q2) * r5 ** 2 + 2 * r2 * r3 - 2 * b2 * c2 * r4 * r5
    t0 = r3 ** 2 - r5 ** 2 * b2 * c2
    return np.array([t8, t6, t4, t2, t0]), dict(q=(q1, q2, q3, q4, q5, q6), r=(r1, r2, r3, r4, r5))


# ---------------------------------------------------------------- Appendix I: tư thế tuyệt đối tuyến tính
def absolute_orientation_appendixI(Pc, Pw):
    """Tìm R, T với Pc_i = R Pw_i + T [eq. (a.1)] theo Phụ lục I [tr. 22]:
    đưa tam giác thế giới về mặt phẳng z'=0, giải hệ 9x9 AX=B, rồi cột 3 của R bằng (a.2)."""
    Pc = np.asarray(Pc, float)
    Pw = np.asarray(Pw, float)
    # hệ phụ (bài chỉ viết "we can assume z'_i = 0"): gốc tại Pw0, trục z' pháp tuyến tam giác
    e1 = Pw[1] - Pw[0]; e1 /= np.linalg.norm(e1)
    e3 = np.cross(Pw[1] - Pw[0], Pw[2] - Pw[0]); e3 /= np.linalg.norm(e3)
    e2 = np.cross(e3, e1)
    Q = np.vstack([e1, e2, e3])                 # x' = Q (Pw - Pw0)
    Pl = (Q @ (Pw - Pw[0]).T).T                 # z' ~ 0
    A = np.zeros((9, 9))
    Bv = np.zeros(9)
    for i in range(3):
        x, y = Pl[i, 0], Pl[i, 1]
        for r in range(3):
            A[3 * i + r, 2 * r] = x
            A[3 * i + r, 2 * r + 1] = y
            A[3 * i + r, 6 + r] = 1
            Bv[3 * i + r] = Pc[i, r]
    X = np.linalg.solve(A, Bv)
    r11, r12, r21, r22, r31, r32, tx, ty, tz = X
    r13 = r21 * r32 - r22 * r31                 # (a.2)
    r23 = r12 * r31 - r11 * r32
    r33 = r11 * r22 - r12 * r21
    Rl = np.array([[r11, r12, r13], [r21, r22, r23], [r31, r32, r33]])
    Tl = np.array([tx, ty, tz])
    # Pc = Rl Q (Pw - Pw0) + Tl  =>  R = Rl Q, T = Tl - Rl Q Pw0
    R = Rl @ Q
    T = Tl - R @ Pw[0]
    return R, T, np.linalg.cond(A)
