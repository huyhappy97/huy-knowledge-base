# VSLAM — cây tri thức Visual SLAM

Dựng từ lộ trình tự soạn (Tầng 1 nguyên lý, Tầng 2 giải thuật, Tầng 4 framework, phần mass
production, tám hướng còn trống, lộ trình năm giai đoạn), theo `../learning-rules.md`.

Bắt đầu đọc từ `00-map.tex` (bản đồ gốc: luận đề trung tâm, vì sao chia thế, thứ tự đọc).
Nếu đọc lần đầu, xem **chương 24 (lộ trình)** trước cả Phần A — nó nói thứ tự nên đi.

## Luận đề trung tâm

**SLAM, SfM, hiệu chuẩn và localization là một bài toán MAP duy nhất; chúng chỉ khác nhau
ở chỗ biến nào được fix, biến nào để tự do, và chuyển động nào làm cho biến đó trở nên
quan sát được.**

Cả cây được dựng để làm rõ câu đó và để chỉ ra khi nào nó hỏng. Chương 4 dựng khung MAP,
chương 5 dựng observability, và **chương 14 là chỗ luận đề được chứng minh bằng tay** —
ta đi từ ô "hiệu chuẩn" sang ô "SLAM" bằng cách thả dần các biến, và không có gì trong bộ
giải phải thay đổi.

## Dựng PDF

```bash
./build.sh                    # vslam.pdf — bản gộp toàn cây
./build.sh all                # thêm PDF riêng cho từng phần, từng chương
./build.sh A-nguyen-ly-va-toan-hoc/03-lie-group-va-toi-uu-tren-da-tap/lie-group-va-toi-uu-tren-da-tap.tex
./check-cites.sh              # kiểm mọi \cite{} đều có trong refs.bib
```

Yêu cầu: XeLaTeX + biber; font TeX Gyre Pagella / Lato / Noto Sans Mono; package `subfiles`,
`babel-vietnamese`, `tcolorbox`, `pgfplots`, `listings`, `xstring`.

## Cấu trúc

```
vslam.tex             master, gộp toàn cây
00-map.tex            bản đồ gốc — đọc đầu tiên
99-chua-biet.md       sổ những điều chưa biết (Feynman) — danh sách công việc học tập
99-chua-biet.tex      ảnh chụp của sổ trên, để gộp vào PDF
preamble/common.tex   toàn bộ style, macro, ba loại hộp
refs.bib              thư mục dùng chung (chưa đối chiếu nguồn — xem 99-chua-biet.md mục 0)
check-cites.sh        kiểm bibkey

A-nguyen-ly-va-toan-hoc/     Phần A — nguyên lý và toán học     (chương 1–6)
B-front-end-va-back-end/     Phần B — front-end và back-end     (chương 7–12)
C-he-thong-slam-day-du/      Phần C — hệ thống SLAM đầy đủ      (chương 13–18)
D-thuc-te-va-san-xuat/       Phần D — thực tế và sản xuất       (chương 19–22)
E-framework-va-lo-trinh/     Phần E — framework và lộ trình     (chương 23–24)
```

Mỗi thư mục có `00-map.tex` (bản đồ nhánh) và đúng một tệp `.tex` cùng tên với thư mục.
Mục con là thư mục con, không phải tệp ngang cấp. Nhờ `subfiles`, mỗi tệp vừa dựng riêng ra
PDF được, vừa được master gộp lại thành một PDF liền mạch.

## Bảy chương xương sống

Nếu chỉ có thời gian cho phần ★★★:

| Ch. | Chương | Vì sao |
|---|---|---|
| 3 | Lie group và tối ưu trên đa tạp | Ngôn ngữ. Không có nó thì mọi Jacobian là hộp đen. |
| 4 | MAP và bundle adjustment | Khung mà cả cây nằm trong. Schur là lý do bài toán giải được. |
| 5 | Observability, gauge và suy biến | Chương giải thích *vì sao* mọi thứ hỏng. |
| 7 | Đặc trưng và data association | Front-end quyết định hệ thống hỏng theo *kiểu* nào. |
| 9 | Paradigm ước lượng back-end | Bộ lọc và tối ưu là cùng một MAP — hiểu điều này thì chuyển qua lại rất tự nhiên. |
| 13 | Quản lý bản đồ | Bị coi nhẹ nhất, ảnh hưởng production lớn nhất. |
| 14 | Hiệu chuẩn như một nhánh của SLAM | Chỗ luận đề trung tâm được chứng minh bằng tay. |

## Ba mini project có tỉ lệ giá trị trên thời gian cao nhất

1. **Kiểm mọi Jacobian bằng sai phân số** (ch 3) — tạo ra bộ unit test dùng suốt về sau.
2. **Phổ giá trị riêng trên bốn quỹ đạo** (ch 5) — làm observability thành thứ nhìn thấy được.
3. **Đi từ hiệu chuẩn tới SLAM bằng cách thả biến** (ch 14) — chứng minh luận đề trung tâm.

## Trạng thái và cảnh báo

Cây này ở trạng thái **bản nháp có kiểm soát**:

- `refs.bib` **chưa được đối chiếu với nguồn gốc** — xem `99-chua-biet.md` mục 0. Phải mở
  bản gốc trước khi trích dẫn ra ngoài cây hoặc dùng để ra quyết định thật.
- Cây **không chứa con số thực nghiệm nào do tôi đo**. Mọi con số hoặc dẫn nguồn, hoặc tính
  tay từ ví dụ tự đặt, hoặc được đánh dấu *(tôi suy ra, chưa đối chiếu nguồn)*.
- Phần **hết hạn nhanh nhất**: ch 16 mục 4 (NeRF, 3DGS), ch 17 (học máy), ch 23 (framework).
  Cả ba chốt 9/2026 — **rà lại 3/2027**.
- Ch 22 (tám hướng còn trống) **chưa đạt chuẩn `research-rules.md`** và nói rõ điều đó ngay
  từ đầu. Mỗi hướng kèm một *phép kiểm* — chạy nó trước khi đầu tư thời gian.

## Quan hệ với các cây khác

- `../IMU_Fusion/` — nhánh quán tính: tiền tích phân, bộ lọc, khởi tạo VI, hiệu chuẩn
  camera–IMU. Cây này **không lặp lại** nội dung đó, chỉ trỏ sang.
- `../marker/` — nhánh fiducial: detection, lưỡng nghĩa tư thế phẳng, constellation, ngân
  sách sai số docking. Là bản thu nhỏ tốt của toàn bộ lộ trình (xem ch 24 mục 7).
