# marker — cây tri thức định vị bằng fiducial marker cho docking chính xác

Dựng từ lộ trình tự soạn (Tầng 1 nguyên lý, Tầng 2 giải thuật, Tầng 4 framework,
cộng phần ngân sách sai số cho mục tiêu 5 mm / 0,5°), theo `../learning-rules.md`.
Bắt đầu đọc từ `00-map.tex` (bản đồ gốc: luận điểm trung tâm, vì sao chia thế,
thứ tự đọc).

## Luận điểm trung tâm

**Mục tiêu 5 mm / 0,5° không bị giới hạn bởi thuật toán mà bởi ngân sách sai
số** — chủ yếu là hình học constellation, độ chính xác cơ khí của tấm marker, và
calibration. Cả cây được dựng để làm rõ câu đó và để chỉ ra khi nào nó hỏng.

Bốn hệ quả kéo theo, gặp lại ở gần như mọi chương:

1. **Translation dễ, rotation khó.** Sai số tịnh tiến gần như luôn đạt; sai số
   xoay từ một tag phẳng nhìn vuông góc dễ vượt 1°.
2. **Hình học thắng thuật toán.** δθ ≈ Zσ/(fB) — cải thiện tuyến tính theo
   baseline, một đại lượng mua được bằng nhôm và vít.
3. **Cơ khí là sàn sai số.** Đừng tin CAD; đo lại constellation bằng bundle
   adjustment.
4. **Docking cần repeatability, không cần accuracy.** Teach-by-showing triệt
   tiêu mọi sai số hệ thống — trong ví dụ của cây, hệ số 3,6 lần.

## Dựng PDF

```bash
./build.sh                    # marker.pdf — bản gộp toàn cây (258 trang)
./build.sh all                # thêm PDF riêng cho từng phần, từng chương
./build.sh A-nguyen-ly-va-toan-hoc/05-lan-truyen-sai-so-pixel-sang-pose/lan-truyen-sai-so-pixel-sang-pose.tex
```

Yêu cầu: XeLaTeX + biber; font TeX Gyre Pagella / Lato / Noto Sans Mono; package
`subfiles`, `babel-vietnamese`, `tcolorbox`, `pgfplots`, `listings`.

## Cấu trúc

```
marker.tex              master, gộp toàn cây
00-map.tex              bản đồ gốc — đọc đầu tiên
99-chua-biet.md         sổ những điều chưa biết (Feynman)
preamble/common.tex     toàn bộ style, macro, ba loại hộp
refs.bib                thư mục dùng chung
A-nguyen-ly-va-toan-hoc/      Phần A — nguyên lý và toán học   (chương 1–6)
B-giai-thuat-va-phuong-phap/  Phần B — giải thuật và phương pháp (chương 7–14)
C-ngan-sach-sai-so/           Phần C — ngân sách sai số        (chương 15–16)
D-framework-va-cong-cu/       Phần D — framework và công cụ    (chương 17–18)
E-lo-trinh/                   Phần E — lộ trình                (chương 19)
```

Mỗi thư mục có `00-map.tex` (bản đồ nhánh) và đúng một tệp `.tex` cùng tên với
thư mục. Mục con là thư mục con, không phải tệp ngang cấp.

## Bảy chương xương sống

Nếu chỉ có thời gian cho phần ★★★:

| Ch. | Chương | Vì sao |
|---|---|---|
| 4 | Pose ambiguity | Nguồn lỗi xoay số một, và ít người gọi đúng tên nó. |
| 5 | Lan truyền sai số | Chương định giá. Bốn quan hệ tỉ lệ, đủ ngắn để thuộc. |
| 9 | Constellation | Đòn bẩy lớn nhất của cả cây — và nó là bản vẽ cơ khí. |
| 10 | Xử lý ambiguity | Ngắn, nhưng nó là điều kiện để mọi con số có nghĩa. |
| 12 | Calibration | Ba bước, đúng thứ tự, kiểm sau mỗi bước. |
| 13 | Docking control | Chứa mẹo lớn nhất: biến accuracy thành repeatability. |
| 15 | Ngân sách sai số | Chương hội tụ. **Đọc sớm, ngay sau chương 5.** |

Đáng chú ý: chỉ hai trong bảy chương ấy nói về thuật toán xử lý ảnh. Đó không
phải ngẫu nhiên mà là hệ quả trực tiếp của luận điểm trung tâm.

Chương 19 là lộ trình tám bước, và **ba bước đầu không có dòng code nào**.

## Mã nguồn chạy được

`C-ngan-sach-sai-so/16-danh-gia-va-nghiem-thu/code/monte_carlo_constellation.py`

Đây là **cửa kiểm chứng (b)** theo `learning-rules.md` mục 5 cho toàn bộ cây.
Nó đã được chạy ngày 2026-09-14 (log: `ket-qua-chay-2026-09-14.txt`), và kết quả
được báo cáo ở chương 16 mục 3 — **gồm cả một chỗ đi ngược dự đoán của tôi**.

```bash
cd C-ngan-sach-sai-so/16-danh-gia-va-nghiem-thu/code
python3 monte_carlo_constellation.py --trials 3000
```

Cần `numpy` và `opencv-python`. Không cần phần cứng. Đổi các hằng số ở đầu tệp
thành số đo của hệ bạn trước khi dùng kết quả.

## Trạng thái kiểm chứng

**Đã qua cửa (b)** — kiểm bằng số thật, không phải ví dụ tính tay:

- `δZ ≈ Zσ/w` — khớp, sai lệch dưới 15% ở mọi Z, dưới 3% ở Z ≥ 1 m.
- `δx ≈ Zσ/f` — khớp sau khi tính tới hệ số √N mà A/05 **cố ý** bỏ ra.
- Ambiguity của target phẳng — ρ tăng từ 1,33 (fronto-parallel) lên 66,6 (40°).
- Bốn phương án bố trí — từ A tới D cải thiện 6,7 lần, hoàn toàn bằng hình học.

**Chưa kiểm, và ghi rõ trong bài** — xem `99-chua-biet.md`:

- Mức cải thiện của việc phá tính đồng phẳng (đo được 1,24 lần, thấp hơn dự
  đoán — có thể tôi đã đo nhầm đại lượng).
- Vì sao tag nhô ra theo chiều sâu mạnh hơn nêm nghiêng hai lần.
- Tính tuyến tính chính xác của quan hệ δθ ∝ 1/B.

## Cần biết trước khi tin

- **`refs.bib` soạn từ trí nhớ về công trình gốc, chưa đối chiếu trang nhà xuất
  bản.** Theo `learning-rules.md` mục 5, như vậy là chưa qua cửa kiểm chứng nào.
  Phải mở bản gốc trước khi trích ra ngoài cây.
- **Toàn cây chưa có một phép đo phần cứng nào.** Mọi con số đã kiểm đến từ mô
  phỏng, và mô phỏng không kiểm được hai thứ: các nguồn sai số bị bỏ sót, và
  tính đúng của mô hình nhiễu (chương 16 mục 6).
- **Các con số σ (0,1–0,3 px cho AprilTag, v.v.) là bậc độ lớn kinh nghiệm**,
  không phải số đo có điều kiện xác định. Chúng đủ để lập ngân sách sơ bộ và so
  sánh tương đối; **không** đủ để nghiệm thu.
- **Mọi con số trong bảng ngân sách ở chương 15 là ví dụ số học tự đặt.** Mục
  đích của chúng là cho thấy bậc độ lớn và tỉ lệ giữa các dòng, không phải để
  chép vào báo cáo.
- **Phần D (framework) chốt tại tháng 9/2026**, hết hạn nhanh nhất; rà lại mỗi
  sáu tháng, và rà bằng cách **chạy** chứ không bằng đọc tài liệu.

## Liên kết ngang ra ngoài cây

- `../IMU_Fusion/` — chương 11 của cây này (ước lượng theo thời gian) chồng lấn
  với Phần B của cây đó. Câu hỏi chưa trả lời về quan hệ giữa hai bên nằm ở
  `99-chua-biet.md`. Không chép nội dung qua lại, chỉ trỏ.

## Quy ước trong tài liệu

- Ba loại hộp, không hơn: **Trực giác**, **Cạm bẫy**, **Cần nhớ**.
- Mức ưu tiên `\muc{3}` xương sống / `\muc{2}` quan trọng / `\muc{1}` bổ trợ.
- Mỗi tài liệu mở bằng dòng *Phụ thuộc*, rồi **Tóm tắt**, **Kiến thức cần có
  trước**, **Câu hỏi mở đầu**; đóng bằng *Giới hạn và chế độ hỏng*, *Thực hành*,
  **Active recall**, **Mini project**, **Trả lời câu hỏi mở đầu**, **Nói lại
  thật đơn giản**, *Điều gì chứng minh cách hiểu này sai*, *Kết nối*, và câu hỏi
  tự kiểm.
- Đường dẫn chéo bấm được: `\ptr{A/05-lan-truyen-sai-so-pixel-sang-pose}`.
