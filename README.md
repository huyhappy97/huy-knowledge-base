# huy-knowledge-base

Kho tri thức cá nhân: mỗi chủ đề là **một cuốn sách LaTeX hoàn chỉnh**, không phải một tập
ghi chú rời. Hiện có 7 cây tri thức, tổng ~1.900 trang và 713 nguồn trích dẫn — về thị giác
máy tính, SLAM, hợp nhất cảm biến, giải thuật, tiếng Anh chuyên ngành và cách học.

Nội dung viết bằng tiếng Việt.

## Vì sao kho này tồn tại

Ghi chú rời rạc tạo ảo giác hiểu, và ảo giác đó chỉ vỡ ra khi đã quá muộn. Nên mỗi tài liệu ở
đây phải đọc được như một chương luận văn — có mở đầu, có mạch phát triển, có kết luận — và
phải còn hiểu được sau nhiều năm.

Hai quy tắc chi phối toàn bộ kho, viết đầy đủ trong [`learning-rules.md`](learning-rules.md):

1. **Mọi khẳng định quan trọng phải truy được về một nguồn thật.** Phần lớn nội dung được
   soạn với sự trợ giúp của mô hình ngôn ngữ, mà mô hình sai một cách rất tự tin; một ý sai
   nằm im trong cây sẽ làm hỏng mọi thứ dựng lên trên nó.
2. **Ghi chú là sản phẩm của việc suy nghĩ, không phải của việc chép lại.**

[`research-rules.md`](research-rules.md) là quy tắc cho việc đi trước một bước: dựng hiểu biết
về một chủ đề từ con số không, khi chưa có sách giáo khoa mà chỉ có vài chục công trình rải rác
mâu thuẫn nhau.

## Các cây tri thức

| Cây | Nội dung | Quy mô |
|-----|----------|--------|
| [`VSLAM/`](VSLAM/) | Visual SLAM — từ Lie group và observability đến hệ SLAM đầy đủ và bài toán sản xuất | 274 tr · 29 chương · 126 nguồn |
| [`deep_learning/`](deep_learning/) | Học sâu cho computer vision — nền tảng, tư duy hệ thống, mô hình, triển khai, đánh giá | 762 tr · 73 file · 201 nguồn |
| [`algorithm/`](algorithm/) | Giải thuật và tư duy giải bài — cấu trúc dữ liệu, chiến lược thiết kế, giới hạn tính toán | 337 tr · 28 chương · 107 nguồn |
| [`marker/`](marker/) | Định vị bằng fiducial marker cho docking chính xác 5 mm / 0,5° | 259 tr · 24 chương · 83 nguồn |
| [`english/`](english/) | Tiếng Anh để đọc đúng ý người viết và viết cho người khác đọc đúng ý mình | 217 tr · 26 chương · 58 nguồn |
| [`gioi_han_con_nguoi/`](gioi_han_con_nguoi/) | Ý chí, nỗi sợ thất bại và việc học — chỉ giữ phần áp dụng được | 39 tr · 17 nhánh · 87 nguồn |
| [`hieu_suat/`](hieu_suat/) | *Khảo sát:* hiệu suất người làm nghiên cứu khoa học máy tính | 51 tr · 51 công trình (1945–2021) |

Vài luận đề trung tâm, để biết mỗi cây thực sự nói gì:

- **VSLAM:** SLAM, SfM, hiệu chuẩn và localization là *một* bài toán MAP duy nhất; chúng chỉ
  khác nhau ở chỗ biến nào được fix và chuyển động nào làm biến đó quan sát được. Chương 14
  chứng minh điều đó bằng tay — đi từ ô "hiệu chuẩn" sang ô "SLAM" mà bộ giải không đổi gì.
- **marker:** mục tiêu 5 mm / 0,5° không bị chặn bởi thuật toán mà bởi ngân sách sai số —
  hình học constellation, cơ khí tấm marker, calibration. Hình học thắng thuật toán:
  δθ ≈ Zσ/(fB), cải thiện tuyến tính theo baseline — thứ mua được bằng nhôm và vít.

## Cấu trúc một cây

Thư mục là bản đồ tư duy được vật chất hoá:

```
<chu-de>/
├── <chu-de>.tex          master — gộp toàn cây thành một PDF liền mạch
├── 00-map.tex            bản đồ: có gì, VÌ SAO chia thế, đọc theo thứ tự nào
├── preamble/common.tex   toàn bộ style và macro
├── refs.bib              bibliography dùng chung
├── A-<phan>/             phần, mỗi phần lại có 00-map.tex riêng
│   └── NN-<chuong>/      chương: một file .tex cùng tên + figures/ + code/
└── build.sh
```

`00-map.tex` là file quan trọng nhất ở mỗi cấp. Không có nó, cây chỉ là thư mục chứ không phải
bản đồ tư duy. Số thứ tự trong tên folder phản ánh **thứ tự nên đọc**, không phải thứ tự tôi học được.

## Dựng PDF

```bash
cd VSLAM
./build.sh                    # vslam.pdf — bản gộp toàn cây
./build.sh all                # thêm PDF riêng cho từng phần, từng chương
./build.sh A-nguyen-ly-va-toan-hoc/03-lie-group-va-toi-uu-tren-da-tap/lie-group-va-toi-uu-tren-da-tap.tex
./check-cites.sh              # kiểm mọi \cite{} đều có trong refs.bib
```

Mỗi chương build được độc lập nhờ `subfiles`, và PDF con cũng in phần **Nguồn** của riêng nó.

**Yêu cầu:** XeLaTeX + biber (`latexmk -xelatex`); font TeX Gyre Pagella / Lato / Noto Sans Mono;
package `subfiles`, `babel-vietnamese`, `tcolorbox`, `pgfplots`, `listings`, `xstring`.

```bash
sudo apt install texlive-full fonts-texgyre fonts-lato fonts-noto
```

## Đọc từ đâu

Mỗi cây bắt đầu từ `00-map.tex` của nó. Riêng VSLAM, nếu đọc lần đầu thì xem **chương 24
(lộ trình)** trước cả Phần A — nó nói thứ tự nên đi.

Nếu muốn hiểu cách kho này được dựng trước khi đọc nội dung: [`learning-rules.md`](learning-rules.md).
