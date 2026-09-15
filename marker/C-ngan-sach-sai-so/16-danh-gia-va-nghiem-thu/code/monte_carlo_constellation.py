#!/usr/bin/env python3
"""
monte_carlo_constellation.py — kiểm bằng số các công thức của A/05 và A/04.

Đây là hiện thân của CỬA KIỂM CHỨNG (b) trong `learning-rules.md` mục 5, cho
toàn bộ Phần C. Cho tới khi script này được chạy và kết quả khớp với dự đoán
giải tích, các công thức ở A/05 mới chỉ qua cửa (a) — tự dẫn — chứ chưa qua (b).

Script làm bốn việc:
  1. Kiểm bốn quan hệ tỉ lệ của A/05 bằng cách quét Z, W, sigma, B.
  2. Kiểm luận điểm của A/04: target phẳng có hai nghiệm, và tỉ số rho
     tiến về 1 khi góc nghiêng tiến về 0.
  3. So PnP hợp nhất với trung bình pose (luận điểm A/03 mục 5, B/09 mục 2).
  4. So bốn phương án bố trí constellation (mini project B/09).

Yêu cầu: numpy, opencv-python. Không cần phần cứng.

Chạy:
    python3 monte_carlo_constellation.py            # chạy cả bốn phần
    python3 monte_carlo_constellation.py --part 1   # chỉ phần 1

Ghi chú trung thực: mọi con số MẶC ĐỊNH trong script là ví dụ số học lấy từ
cấu hình chuẩn của cây (A/05 mục 4, C/15 mục 3). Chúng KHÔNG phải số đo của
một hệ thống nào. Thay chúng bằng số đo của hệ bạn trước khi dùng kết quả
để ra quyết định.
"""

import argparse
import math

import numpy as np

try:
    import cv2
except ImportError:  # pragma: no cover
    raise SystemExit("Cần opencv-python: pip install opencv-python")


# ---------------------------------------------------------------------------
# Cấu hình chuẩn của cây — xem A/05 mục 4 và C/15 mục 3.
# ĐỔI CÁC SỐ NÀY THÀNH SỐ ĐO CỦA HỆ BẠN.
# ---------------------------------------------------------------------------
F_PX = 600.0        # tiêu cự tính bằng pixel
IMG_W, IMG_H = 1280, 960
SIGMA_PX = 0.2      # nhiễu định vị góc, bậc độ lớn kinh nghiệm — hãy tự đo
N_TRIALS = 2000     # số lần Monte Carlo mỗi cấu hình

K = np.array([[F_PX, 0.0, IMG_W / 2.0],
              [0.0, F_PX, IMG_H / 2.0],
              [0.0, 0.0, 1.0]])
DIST = np.zeros(5)  # giả định đã khử méo sạch — xem A/01 về việc này không hiển nhiên

RNG = np.random.default_rng(20260913)


# ---------------------------------------------------------------------------
# Dựng hình học
# ---------------------------------------------------------------------------
def tag_corners(size_m, center=(0.0, 0.0, 0.0), rx=0.0, ry=0.0):
    """Bốn góc của một tag vuông cạnh `size_m`, tâm tại `center`, trong hệ DOCK.

    `rx`, `ry` là góc nghiêng CỦA TAG SO VỚI TẤM DOCK (radian) — tức cái nêm
    cơ khí ở B/09 mục 4. Chúng là một phần của MÔ HÌNH 3D, không phải tư thế
    của camera.

    QUY ƯỚC QUAN TRỌNG: góc nhìn của camera so với constellation được đặt ở
    `R_true` khi gọi `run_config`, KHÔNG phải ở đây. Trộn hai thứ này là một
    lỗi dễ mắc: nếu nghiêng cả mô hình lẫn pose thì `rot_angle_deg(R_true, R)`
    so hai thứ khác nhau và mọi con số sai số góc trở nên vô nghĩa.

    Thứ tự góc theo quy ước OpenCV cho SOLVEPNP_IPPE_SQUARE:
    trái-trên, phải-trên, phải-dưới, trái-dưới.
    """
    h = size_m / 2.0
    local = np.array([[-h, +h, 0.0],
                      [+h, +h, 0.0],
                      [+h, -h, 0.0],
                      [-h, -h, 0.0]])
    cx, sx = math.cos(rx), math.sin(rx)
    cy, sy = math.cos(ry), math.sin(ry)
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    return (local @ (Ry @ Rx).T) + np.asarray(center)


def rotation(rx=0.0, ry=0.0, rz=0.0):
    cx, sx = math.cos(rx), math.sin(rx)
    cy, sy = math.cos(ry), math.sin(ry)
    cz, sz = math.cos(rz), math.sin(rz)
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return Rz @ Ry @ Rx


def project(pts3d, R, t):
    rvec, _ = cv2.Rodrigues(R)
    uv, _ = cv2.projectPoints(pts3d.astype(np.float64), rvec,
                              t.astype(np.float64), K, DIST)
    return uv.reshape(-1, 2)


def rot_angle_deg(R1, R2):
    """Góc của phép quay đưa R1 về R2, tính bằng độ."""
    dR = R1.T @ R2
    c = (np.trace(dR) - 1.0) / 2.0
    return math.degrees(math.acos(max(-1.0, min(1.0, c))))


# ---------------------------------------------------------------------------
# Chạy một cấu hình Monte Carlo
# ---------------------------------------------------------------------------
def run_config(pts3d, R_true, t_true, sigma=SIGMA_PX, n=N_TRIALS,
               flags=cv2.SOLVEPNP_ITERATIVE, refine=True):
    """Trả về (std vị trí theo 3 trục tính bằng mm, std góc tính bằng độ,
    rho trung vị)."""
    uv_clean = project(pts3d, R_true, t_true)
    ts, Rs, rhos = [], [], []

    use_ippe = (len(pts3d) == 4)

    for _ in range(n):
        uv = uv_clean + RNG.normal(0.0, sigma, uv_clean.shape)

        if use_ippe:
            ok, rvecs, tvecs, errs = cv2.solvePnPGeneric(
                pts3d.astype(np.float64), uv.astype(np.float64), K, DIST,
                flags=cv2.SOLVEPNP_IPPE_SQUARE)
            if not ok or len(rvecs) == 0:
                continue
            e = np.asarray(errs).ravel()
            order = np.argsort(e)
            if len(e) >= 2 and e[order[0]] > 1e-12:
                rhos.append(float(e[order[1]] / e[order[0]]))
            rvec, tvec = rvecs[order[0]], tvecs[order[0]]
        else:
            ok, rvec, tvec = cv2.solvePnP(
                pts3d.astype(np.float64), uv.astype(np.float64), K, DIST,
                flags=flags)
            if not ok:
                continue

        if refine:
            rvec, tvec = cv2.solvePnPRefineLM(
                pts3d.astype(np.float64), uv.astype(np.float64), K, DIST,
                rvec, tvec)

        R, _ = cv2.Rodrigues(rvec)
        ts.append(tvec.ravel())
        Rs.append(R)

    ts = np.asarray(ts)
    std_mm = ts.std(axis=0) * 1000.0
    ang = np.array([rot_angle_deg(R_true, R) for R in Rs])
    # Độ tản mát góc TỔNG: RMS quanh chân trị (gồm cả thiên lệch nếu có).
    std_deg = float(np.sqrt(np.mean(ang ** 2)))
    # Độ tản mát góc THEO TỪNG TRỤC — cần thiết vì baseline CÓ HƯỚNG
    # (B/09 mục 3): trải rộng theo x cải thiện yaw và roll, KHÔNG cải thiện
    # pitch. Một con số góc vô hướng bị trục tệ nhất chi phối và che mất
    # điều đó, nên luôn nhìn cả ba trục.
    axis = np.array([np.degrees(cv2.Rodrigues(R_true.T @ R)[0].ravel())
                     for R in Rs])
    std_axis = axis.std(axis=0)          # [rx (pitch), ry (yaw), rz (roll)]
    rho_med = float(np.median(rhos)) if rhos else float("nan")
    return std_mm, std_deg, rho_med, std_axis


# ---------------------------------------------------------------------------
# Phần 1 — bốn quan hệ tỉ lệ của A/05
# ---------------------------------------------------------------------------
def part1():
    print("\n=== PHẦN 1: bốn quan hệ tỉ lệ của A/05 ===")
    print("Dự đoán: dx ~ Z.sigma/f ; dZ ~ Z.sigma/w ; dtheta ~ Z.sigma/(f.B)")

    W = 0.10
    print("\n-- quét Z (một tag %.0f mm, camera nhìn chếch 20 độ) --" % (W * 1000))
    print("   Công thức A/05 KHÔNG có hệ số 1/sqrt(N) (xem A/05 mục 3A: cố ý bỏ")
    print("   cho thận trọng). Với 4 góc độc lập, mô phỏng cho dx nhỏ hơn dự đoán")
    print("   khoảng sqrt(4) = 2 lần — nên cột cuối là dự đoán ĐÃ chia cho 2.")
    print(f"\n{'Z (m)':>7} {'dx (mm)':>9} {'dZ (mm)':>9} {'dZ/dx':>7} {'Z/W':>7} "
          f"{'dx dự đoán/2':>13} {'dZ dự đoán':>11}")
    for Z in (0.3, 0.5, 1.0, 2.0):
        pts = tag_corners(W)                       # mô hình PHẲNG
        R = rotation(ry=math.radians(20))          # góc nhìn nằm ở POSE
        t = np.array([0.0, 0.0, Z])
        std_mm, _, _, _ = run_config(pts, R, t)
        dx = float(np.mean(std_mm[:2]))
        dz = float(std_mm[2])
        w_px = F_PX * W / Z
        pred_x = Z * SIGMA_PX / F_PX * 1000.0 / 2.0
        pred_z = Z * SIGMA_PX / w_px * 1000.0
        print(f"{Z:7.2f} {dx:9.3f} {dz:9.3f} {dz/dx:7.2f} {Z/W:7.2f} "
              f"{pred_x:13.3f} {pred_z:11.3f}")
    print("  Kiểm 1: cột dx phải xấp xỉ cột 'dx dự đoán/2'  -> dx ~ Z.sigma/f.")
    print("  Kiểm 2: cột dZ phải xấp xỉ cột 'dZ dự đoán'    -> dZ ~ Z.sigma/w.")
    print("  Kiểm 3: cột dZ/dx phải TĂNG TUYẾN TÍNH theo Z (cùng dốc với Z/W).")

    print("\n-- quét baseline B NGANG (hai tag %.0f mm, Z = 0,5 m) --" % (W * 1000))
    print("   Baseline CÓ HƯỚNG (B/09 mục 3): trải rộng theo x cải thiện YAW,")
    print("   không cải thiện PITCH. Vì vậy phải nhìn từng trục, không nhìn")
    print("   một con số góc vô hướng — nó bị trục tệ nhất chi phối.")
    print(f"\n{'B (m)':>7} {'pitch':>9} {'yaw':>9} {'roll':>9} {'yaw dự đoán':>12} {'tỉ số':>7}")
    Z = 0.5
    for B in (0.10, 0.20, 0.40, 0.80):
        # hai tag nghiêng ngược chiều: nêm cơ khí, thuộc MÔ HÌNH
        pts = np.vstack([
            tag_corners(W, center=(-B / 2, 0, 0), ry=math.radians(+20)),
            tag_corners(W, center=(+B / 2, 0, 0), ry=math.radians(-20)),
        ])
        R = rotation()                              # camera nhìn thẳng trục
        t = np.array([0.0, 0.0, Z])
        _, _, _, std_axis = run_config(pts, R, t)
        pred = math.degrees(Z * SIGMA_PX / (F_PX * B))
        print(f"{B:7.2f} {std_axis[0]:9.4f} {std_axis[1]:9.4f} {std_axis[2]:9.4f} "
              f"{pred:12.4f} {std_axis[1]/pred:7.2f}")
    print("  Kiểm 1: cột YAW phải giảm gần TUYẾN TÍNH theo B (A/05 mục 6),")
    print("          nên cột 'tỉ số' phải gần như KHÔNG ĐỔI theo B.")
    print("  Kiểm 2: cột PITCH giảm CHẬM hơn nhiều — vì baseline đứng không đổi.")
    print("          Đây chính là luận điểm 'baseline có hướng' của B/09 mục 3,")
    print("          và nó là lý do không nên bỏ hẳn baseline theo chiều đứng.")


# ---------------------------------------------------------------------------
# Phần 2 — ambiguity của target phẳng (A/04)
# ---------------------------------------------------------------------------
def part2():
    print("\n=== PHẦN 2: ambiguity của target phẳng (A/04) ===")
    print("Dự đoán: rho -> 1 khi góc nghiêng -> 0, và sai số góc nổ tung ở đó.")
    W, Z = 0.10, 0.5
    print(f"\n{'nghiêng (deg)':>14} {'rho trung vị':>13} {'sai số góc (deg)':>17}")
    for deg in (0, 2, 5, 10, 20, 40):
        pts = tag_corners(W)                        # mô hình PHẲNG
        R = rotation(ry=math.radians(deg))          # góc nghiêng nằm ở POSE
        t = np.array([0.0, 0.0, Z])
        _, std_deg, rho, _ = run_config(pts, R, t)
        print(f"{deg:14d} {rho:13.3f} {std_deg:17.3f}")
    print("  Kiểm: cột rho phải tăng theo góc nghiêng; ở 0 độ nó phải gần 1,")
    print("        và sai số góc ở 0 độ phải lớn hơn hẳn (A/04 mục 4).")

    print("\n-- KHỬ bằng tính không đồng phẳng --")
    print(f"{'cấu hình':>28} {'pitch':>9} {'yaw':>9} {'roll':>9} {'tổng':>9}")
    R, t = rotation(), np.array([0.0, 0.0, Z])
    # bốn tag ĐỒNG PHẲNG, nhìn vuông góc
    flat = np.vstack([tag_corners(0.075, center=(dx, dy, 0.0))
                      for dx, dy in ((-0.11, 0.045), (0.11, 0.045),
                                     (-0.11, -0.045), (0.11, -0.045))])
    _, d_flat, _, ax_flat = run_config(flat, R, t)
    print(f"{'4 tag đồng phẳng':>28} {ax_flat[0]:9.4f} {ax_flat[1]:9.4f} "
          f"{ax_flat[2]:9.4f} {d_flat:9.4f}")
    # bốn tag NGHIÊNG luân phiên — thiết kế mẫu của B/09 mục 8
    tilt = np.vstack([
        tag_corners(0.075, center=(-0.11, 0.045, 0.0), ry=math.radians(+20)),
        tag_corners(0.075, center=(+0.11, 0.045, 0.0), ry=math.radians(-20)),
        tag_corners(0.075, center=(-0.11, -0.045, 0.0), rx=math.radians(+20)),
        tag_corners(0.075, center=(+0.11, -0.045, 0.0), rx=math.radians(-20)),
    ])
    _, d_tilt, _, ax_tilt = run_config(tilt, R, t)
    print(f"{'4 tag nghiêng 20 độ':>28} {ax_tilt[0]:9.4f} {ax_tilt[1]:9.4f} "
          f"{ax_tilt[2]:9.4f} {d_tilt:9.4f}")
    print(f"  Cải thiện: {d_flat / d_tilt:.2f} lần (B/09 mục 4).")


# ---------------------------------------------------------------------------
# Phần 3 — PnP hợp nhất so với trung bình pose (A/03 mục 5)
# ---------------------------------------------------------------------------
def karcher_mean(Rs, iters=20):
    """Trung bình Karcher trên SO(3) — xem B/11 mục 3."""
    M = Rs[0].copy()
    for _ in range(iters):
        w = np.zeros(3)
        for R in Rs:
            r, _ = cv2.Rodrigues(M.T @ R)
            w += r.ravel()
        w /= len(Rs)
        dM, _ = cv2.Rodrigues(w.reshape(3, 1))
        M = M @ dM
        if np.linalg.norm(w) < 1e-12:
            break
    return M


def part3():
    print("\n=== PHẦN 3: PnP hợp nhất so với trung bình pose (A/03 mục 5) ===")
    print("Dự đoán: hợp nhất thắng rõ về sai số GÓC, và khoảng cách thắng")
    print("         tăng theo baseline (B/09 mục 2).")
    Z, W = 0.5, 0.075
    R_true, t_true = rotation(), np.array([0.0, 0.0, Z])
    print(f"\n{'B (m)':>7} {'hợp nhất (deg)':>16} {'trung bình (deg)':>18} {'tỉ số':>7}")
    for B in (0.10, 0.22, 0.45):
        tags = [tag_corners(W, center=(-B / 2, 0, 0), ry=math.radians(+20)),
                tag_corners(W, center=(+B / 2, 0, 0), ry=math.radians(-20))]
        joint = np.vstack(tags)
        _, d_joint, _, _ = run_config(joint, R_true, t_true)

        # trung bình pose: PnP riêng từng tag rồi Karcher
        angs = []
        for _ in range(N_TRIALS // 4):
            Rs = []
            ok_all = True
            for pts in tags:
                uv = project(pts, R_true, t_true) + RNG.normal(0, SIGMA_PX, (4, 2))
                ok, rv, tv, errs = cv2.solvePnPGeneric(
                    pts.astype(np.float64), uv.astype(np.float64), K, DIST,
                    flags=cv2.SOLVEPNP_IPPE_SQUARE)
                if not ok or len(rv) == 0:
                    ok_all = False
                    break
                i = int(np.argmin(np.asarray(errs).ravel()))
                Rm, _ = cv2.Rodrigues(rv[i])
                Rs.append(Rm)
            if ok_all and len(Rs) == len(tags):
                angs.append(rot_angle_deg(R_true, karcher_mean(Rs)))
        d_avg = float(np.sqrt(np.mean(np.square(angs)))) if angs else float("nan")
        print(f"{B:7.2f} {d_joint:16.4f} {d_avg:18.4f} {d_avg/d_joint:7.2f}")
    print("  Kiểm: cột tỉ số phải LỚN HƠN 1 và tăng theo B.")
    print("        Nếu nó bằng 1 thì mệnh đề A/03 mục 5 bị bác bỏ — hãy ghi lại.")


# ---------------------------------------------------------------------------
# Phần 4 — so bốn phương án bố trí (mini project B/09)
# ---------------------------------------------------------------------------
def part4():
    print("\n=== PHẦN 4: bốn phương án bố trí constellation (B/09) ===")
    Z = 0.5
    R_true, t_true = rotation(), np.array([0.0, 0.0, Z])

    layouts = {
        "A. một tag 150 mm": tag_corners(0.15),
        "B. 4 tag đồng phẳng, B=0,22": np.vstack([
            tag_corners(0.075, center=(dx, dy, 0.0))
            for dx, dy in ((-0.11, 0.045), (0.11, 0.045),
                           (-0.11, -0.045), (0.11, -0.045))]),
        "C. 4 tag nghiêng 20 độ": np.vstack([
            tag_corners(0.075, center=(-0.11, 0.045, 0.0), ry=math.radians(+20)),
            tag_corners(0.075, center=(+0.11, 0.045, 0.0), ry=math.radians(-20)),
            tag_corners(0.075, center=(-0.11, -0.045, 0.0), rx=math.radians(+20)),
            tag_corners(0.075, center=(+0.11, -0.045, 0.0), rx=math.radians(-20))]),
        "D. C + tag nhô ra 60 mm": np.vstack([
            tag_corners(0.075, center=(-0.11, 0.045, 0.0), ry=math.radians(+20)),
            tag_corners(0.075, center=(+0.11, 0.045, 0.0), ry=math.radians(-20)),
            tag_corners(0.075, center=(-0.11, -0.045, 0.0), rx=math.radians(+20)),
            tag_corners(0.075, center=(+0.11, -0.045, 0.0), rx=math.radians(-20)),
            tag_corners(0.050, center=(0.0, 0.0, -0.060))]),
    }

    print(f"\n{'phương án':>30} {'dx (mm)':>8} {'dZ (mm)':>8} "
          f"{'pitch':>8} {'yaw':>8} {'roll':>8}")
    for name, pts in layouts.items():
        std_mm, std_deg, _, std_axis = run_config(pts, R_true, t_true)
        dx = float(np.mean(std_mm[:2]))
        print(f"{name:>30} {dx:8.3f} {std_mm[2]:8.3f} "
              f"{std_axis[0]:8.4f} {std_axis[1]:8.4f} {std_axis[2]:8.4f}")
    print("\n  Ngân sách của cây: 5 mm và 0,5 độ (C/15).")
    print("  Kiểm: phương án B phải tệ hơn C rõ rệt ở cột GÓC dù cùng baseline —")
    print("        đó là toàn bộ luận điểm của A/04 và B/09 mục 4.")


def main():
    global SIGMA_PX, N_TRIALS
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--part", type=int, choices=[1, 2, 3, 4],
                    help="chỉ chạy một phần")
    ap.add_argument("--sigma", type=float, default=SIGMA_PX,
                    help="nhiễu định vị góc (px) — HÃY TỰ ĐO cho hệ của bạn")
    ap.add_argument("--trials", type=int, default=N_TRIALS)
    args = ap.parse_args()

    SIGMA_PX, N_TRIALS = args.sigma, args.trials

    print(f"Cấu hình: f = {F_PX:.0f} px, sigma = {SIGMA_PX} px, "
          f"{N_TRIALS} lần thử mỗi cấu hình")
    print("CẢNH BÁO: mọi số mặc định là VÍ DỤ SỐ HỌC, không phải số đo.")

    parts = [part1, part2, part3, part4]
    if args.part:
        parts[args.part - 1]()
    else:
        for p in parts:
            p()

    print("\nXong. Đối chiếu kết quả với dự đoán giải tích ở A/05, A/04, A/03.")
    print("Chỗ nào lệch thì GHI LẠI — đó là một mục cho 99-chua-biet.md.")


if __name__ == "__main__":
    main()
