# deep_learning — cây tri thức Học AI cho Computer Vision

Dựng từ lộ trình tự soạn (`roadmap_dl.md`, v5), theo `../learning-rules.md`.
Bắt đầu đọc từ `00-map.tex` (bản đồ gốc: vì sao chia thế, thứ tự đọc, các nguyên lý xuyên suốt).

## Dựng PDF

```bash
./build.sh                    # deep_learning.pdf — bản gộp toàn cây
./build.sh all                # thêm PDF riêng cho từng phần, chương, mục
./build.sh B-tu-duy-he-thong/07-chia-du-lieu-va-danh-gia/chia-du-lieu-va-danh-gia.tex   # một file
```

Yêu cầu: XeLaTeX + biber; font TeX Gyre Pagella/Heros, Noto Sans Mono; package `subfiles`, `babel-vietnamese`,
`tcolorbox`, `pgfplots`, `listings`.

## Cấu trúc

```
deep_learning.tex     master, gộp toàn cây
00-map.tex            bản đồ gốc — đọc đầu tiên
preamble/common.tex   toàn bộ style, macro, ba loại hộp
refs.bib              thư mục dùng chung
A-nen-tang-co-gioi-han/   Phần A — nền tảng có giới hạn        (chương 1–2)
B-tu-duy-he-thong/        Phần B — tư duy hệ thống             (chương 3–11)
C-thuat-toan-va-mo-hinh/  Phần C — thuật toán và mô hình       (chương 12–18)
D-ky-thuat-va-trien-khai/ Phần D — kỹ thuật, tối ưu, triển khai (chương 19–22)
E-danh-gia-va-du-an/      Phần E — đánh giá, độ tin cậy, dự án  (chương 23–26)
```

Mỗi thư mục có `00-map.tex` (bản đồ nhánh) và đúng một tệp `.tex` cùng tên với thư mục (bản văn chính).
Mục con là thư mục con, không phải tệp ngang cấp. Nhờ `subfiles`, mỗi tệp vừa dựng riêng ra PDF được,
vừa được master gộp lại thành một PDF liền mạch.

## Quy ước thuật ngữ

`TERMS.md` là từ điển chuẩn của cây: **một khái niệm, một cách gọi**. Mọi file phải theo bảng đó.
Nó chốt các chỗ từng mâu thuẫn (ví dụ *backpropagation* luôn là **lan truyền ngược**, còn *backward pass*
là **lượt ngược** — hai khái niệm khác nhau), liệt kê các cặp dễ nhầm phải phân biệt, và danh sách thuật ngữ
giữ nguyên tiếng Anh. Đọc nó trước khi viết thêm bất cứ chương nào.

## Bảng tra thuật ngữ (sinh tự động)

`98-thuat-ngu.tex` là bảng tra Việt--Anh của cả cây, kèm chương định nghĩa mỗi thuật ngữ lần đầu.
Nó được **sinh tự động** từ mọi `\vn{}{}` và `\kn{}{}` trong cây — đừng sửa tay. Sinh lại bằng:

```bash
python3 <scratchpad>/gen_glossary.py   # ghi đè 98-thuat-ngu.tex
./build.sh 98-thuat-ngu.tex
```

Chạy lại mỗi khi thêm chương mới hoặc thêm thuật ngữ.

## Quy ước trong tài liệu

- Ba loại hộp, không hơn: **Trực giác** (mô hình tư duy), **Cạm bẫy** (lỗi thường gặp), **Cần nhớ** (điều phải nhớ nếu quên hết).
- Nhãn `[T1]`–`[T4]` là tầng bán rã của tri thức; `[T2]` và `[T3]` là trọng tâm.
- Mỗi tài liệu mở bằng dòng *Phụ thuộc*, rồi khối **Tóm tắt**, rồi khối **Kiến thức cần có trước**
  (định nghĩa thật tại chỗ cho mọi khái niệm sơ cấp mà thân bài dùng — không giả sử người đọc đã biết).
- Đóng bằng mục *Kết nối* và 3–7 câu hỏi tự kiểm; mọi câu hỏi kết thúc bằng dấu `?`.
- Thuật ngữ dùng `\vn{tiếng Việt}{English}` ở lần đầu trong mỗi file, hoặc `\en{...}` khi không nên dịch.
- Mỗi chương có một khối *Thực hành*: repo, câu hỏi, mini project, và project cho chương đáng đầu tư.

## Cần biết trước khi tin

- `refs.bib` soạn từ trí nhớ về công trình gốc — đối chiếu bản gốc trước khi trích dẫn ra ngoài cây.
- Mọi con số định lượng cần kiểm lại tại nguồn trước khi dùng để ra quyết định thật.
- Mục *Repo và SOTA* chốt tại **9/2026**, hết hạn nhanh nhất; rà lại mỗi sáu tháng.
