# Tiếng Anh cho đọc và viết chuyên ngành

Cây tri thức LaTeX theo `my_study/learning-rules.md`. Mục tiêu: hiểu sâu về ngôn từ để
đọc đúng ý người viết và viết cho người khác đọc đúng ý mình. Trọng tâm reading + writing;
ngữ pháp chỉ ở mức tối thiểu.

## Build

```bash
./build.sh                 # build master → english.pdf
./build.sh all             # build master + mọi phần + mọi chương (PDF riêng từng file)
./build.sh C-viet-ro/11-cau-ro/cau-ro.tex   # build một file
```

Yêu cầu: `latexmk`, `xelatex`, `biber`. Mỗi chương build được độc lập nhờ `subfiles`,
và mỗi PDF con cũng in phần **Nguồn** của riêng nó.

## Cấu trúc

```
english.tex            # master
preamble/common.tex    # toàn bộ style và macro
refs.bib               # ~58 nguồn
00-map.tex             # bản đồ toàn cây

A-nen-tang-nghia/      # 01 nghĩa nằm ở đâu · 02 biết một từ · 03 ngữ pháp tối thiểu · 04 từ nguyên
B-doc-sau/             # 05 ba tầng đọc · 06 cấu trúc lập luận · 07 đọc bài báo · 08 đọc giữa các dòng
                       # 09 nghe giảng · 10 từ vựng chuyên ngành
C-viet-ro/             # 11 câu rõ · 12 mạch văn · 13 đoạn/bài/tóm tắt · 14 nói đúng mức · 15 sửa bài
D-sac-thai/            # 16 gần nghĩa và văn vực · 17 kết hợp từ · 18 ẩn dụ và khung tư duy
E-luyen-hang-ngay/     # 19 bốn nhánh luyện · 20 công cụ · 21 lộ trình 12 tuần

97-doc-them.tex        # tài liệu tham khảo có chú giải, nhóm theo mục đích
98-thuat-ngu.tex       # bảng thuật ngữ Việt–Anh
99-ket-luan.tex
```

Mỗi phần có `00-map.tex` với bảng tra ngược "bạn đang gặp gì → đọc chương nào".

## Cách dùng

- **Lần đầu:** đọc `00-map.tex` rồi theo một trong ba lộ trình trong đó.
- **Khi gặp vấn đề thật:** dùng bảng tra ngược ở đầu mỗi phần, nhảy thẳng tới chương.
- **Ôn:** dùng khối *Ôn nhanh* cuối mỗi chương (che đáp án, tự trả lời), không đọc lại thân chương.
  Lịch giãn: sau 1 tuần → 3 tuần → 2 tháng. Ghi ngày vào dòng `Ôn gần nhất` ở đầu file chương.
- **Bắt đầu luyện:** chương 21 có tuần mẫu 5 giờ, lộ trình 12 tuần và 4 chỉ số đo được.

## Quy ước trong file

Mỗi chương mở đầu bằng header metadata (Ngày tạo / Sửa gần nhất / Ôn gần nhất / Dependency / Mức độ),
rồi `tomtat` → `nentang` → `khoigoi` → thân chương → `gocre` → `lienhe` → `traloi` → `dongian`
→ `onbai` → `hoidap` → `baitap`. Liên kết chéo bằng `\ptrtarget{A/01}` và `\ptr{A/01}`.
