# Cây tri thức: Giải thuật và tư duy giải bài

Sách LaTeX 28 chương về thuật toán, viết theo `learning-rules.md`: văn xuôi mạch lạc,
mỗi chương có gốc rễ lịch sử, liên hệ sang ngành khác, câu hỏi có đáp án và ngân hàng bài tập.

## Build

```bash
./build.sh          # algorithm.pdf — bản gộp toàn cây
./build.sh all      # thêm PDF riêng cho từng phần và từng chương
./build.sh <path.tex>   # dựng riêng một file
```

Yêu cầu: XeLaTeX + biber (`latexmk -xelatex`), font TeX Gyre Pagella / Lato / Noto Sans Mono.

## Cấu trúc

| Phần | Nội dung | Chương |
|------|----------|--------|
| A | Tư duy và nền tảng | 1–5 |
| B | Cấu trúc dữ liệu | 6–12 |
| C | Chiến lược thiết kế | 13–20 |
| D | Giới hạn và miền chuyên | 21–24 |
| E | Hành nghề và luyện tập | 25–28 |

`00-map.tex` ở mỗi cấp là bản đồ nhánh: có gì, vì sao chia như vậy, đọc theo thứ tự nào.
`preamble/common.tex` giữ toàn bộ style và macro. `refs.bib` là thư mục nguồn dùng chung.

## Khuôn của một chương

Tóm tắt → kiến thức cần có trước → câu hỏi mở đầu → thân bài → **Gốc rễ** (bài toán lịch sử
đẻ ra ý tưởng) → **Liên hệ ngang** (đối chiếu với ngành khác) → trả lời câu hỏi mở đầu →
nói lại thật đơn giản → active recall → câu hỏi ôn tập có đáp án → bài tập → kết chương.

Khi mở rộng: thêm thư mục mới (không thêm file ngang cấp), giữ nguyên khuôn, cập nhật
`00-map.tex` của nhánh, và ghi ngày ôn gần nhất ở đầu file.

## Review và bổ sung trực quan — 2026-09-07

Đã rà soát cấu trúc và hệ thống hình của 28 chương; đợt bổ sung nội dung tập trung
vào 10 chương dưới đây. Giữ hình vector TikZ/PGFPlots ngay trong nguồn LaTeX để
chữ, công thức và đường nét vẫn rõ khi phóng to hoặc in. Có thêm **7 hình, 6 bảng**;
các hình đã có cũng được sửa khi số liệu hoặc mô hình không khớp lời giải.

| Chương | Phần mới nên đọc |
|--------|-----------------|
| B/06 | Vết chạy cửa sổ trượt, phản ví dụ số âm; bảng chọn tiền tố, mảng hiệu, cửa sổ và băm |
| B/10 | Hình phân rã tiền tố 13 theo lowbit; kiểm thứ tự gán/cộng lazy và trạng thái thiếu thông tin |
| C/15 | Hình đổi cuộc họp trong chứng minh tham lam; vì sao thêm trọng số làm chứng minh hỏng |
| C/16 | Hình hai chiều duyệt ba lô; bảng 0/1, không giới hạn và có số lượng |
| C/17 | Phản ví dụ BFS/Dijkstra; bảng lựa chọn bổ sung DAG và 0–1 BFS |
| C/18 | Đường tăng xen kẽ minh hoạ vai trò cạnh ngược và cách kiểm luồng sau khi chạy |
| C/19 | Bảng chạy từng bước bài chia mảng, đáp án 18; kiểm cả 17 và 18 ở ranh giới |
| D/22 | Hình các ca suy biến của giao đoạn; kinh nghiệm ép kiểu và tránh nhân hai định thức |
| E/25 | Bảng ba lớp kiểm thử; lưu và thu nhỏ phản ví dụ; kiểm hồi quy sau khi sửa |
| E/26 | Phiếu benchmark, giới hạn tăng tốc toàn pipeline và lưu ý khi đo hệ thống robot |

### Những điểm đã sửa sau review

- Hình segment tree: truy vấn `[4,8]` dùng `[4,4]` và `[5,8]`, tổng `3 + 18 = 21`;
  sửa nút tô màu và thêm cạnh nối xuống lá.
- Hình đong nước: thay các cạnh không hợp lệ bằng một đường đi sáu thao tác có
  nhãn rõ; phân biệt đường đi minh hoạ với toàn bộ đồ thị trạng thái.
- Fenwick, sparse table và chia khối: làm rõ phạm vi của điều kiện nghịch đảo,
  luỹ đẳng và chi phí gộp; sửa số ô sparse table bị ảnh hưởng bởi một cập nhật điểm.
- Dinic: không đồng nhất mạng ghép đôi hai phía với mọi mạng có sức chứa bằng 1.
- Tìm kiếm đáp án: bỏ khẳng định 100 vòng luôn đủ trên số thực; nêu điều kiện
  không âm khi kiểm tra chia mảng bằng tham lam.
- Hình học: sửa vị trí giao với đường quét, quy ước tia đi qua đỉnh; phép quay
  không loại tính thẳng hàng. Đồng bộ cả phần active recall.
- Gỡ lỗi: phân biệt tìm ranh giới đơn điệu và thu nhỏ dữ liệu; không hứa phản ví dụ
  nhỏ nhất toàn cục hoặc hai cách cài chắc chắn không cùng sai.
- Biểu đồ độ trễ: dùng mật độ log-normal và vị trí trung bình/p99 tương ứng,
  ghi rõ đây là minh hoạ toán học, không phải benchmark đã đo.
- Chỉnh chiều cao header, bảng thuật ngữ tràn lề và neo trang bìa trùng trang 1;
  sửa tham chiếu hình sang chương khác khi build riêng chương A/02.
- `build.sh all` nay dựng thêm ba tài liệu cuối sách, ngoài các phần/chương.

### Nguồn cho các hiệu chỉnh chuyên biệt

Các mục tương ứng có trích dẫn trong sách và bản ghi dùng chung ở `refs.bib`:
[AtCoder: Lazy Segtree](https://atcoder.github.io/ac-library/master/document_en/lazysegtree.html),
[Shewchuk: Robust Predicates](https://www.cs.cmu.edu/~quake/robust.html),
[Zeller–Hildebrandt: Delta Debugging](https://www.st.cs.uni-saarland.de/papers/tse2002/),
[KACTL: Dinic](https://github.com/kth-competitive-programming/kactl/blob/main/content/graph/Dinic.h).

Phạm vi review này ưu tiên tính đúng của ví dụ, giả thiết áp dụng và khả năng đọc
hình/bảng; chưa phải kiểm chứng độc lập toàn bộ phát biểu lịch sử và mọi bài tập
trong sách. Các mẹo thực hành mới là hướng dẫn vận dụng, không gán thành lời nói
hay kinh nghiệm cá nhân của một tác giả nổi tiếng.

### Kiểm tra bản cập nhật

Đã biên dịch thành công 43 đầu vào LaTeX (bản tổng 313 trang và toàn bộ bản riêng),
kiểm tra tham chiếu/trích dẫn, ký tự thiếu và tràn khung. Đã xem trực tiếp các trang
chứa hình mới/sửa; đối chiếu các ví dụ số bằng tính toán và vét cạn trên dữ liệu nhỏ.
Các cảnh báo môi trường có sẵn về hyphenation/babel không nằm trong kiểm tra nội dung này.

## Bổ sung chiều sâu từ sách và từ công trình gốc — 2026-09-07

Đợt này không thêm chương mới. Mỗi chương dưới đây được bổ sung **đúng một mục chuyên sâu**
trả lời một câu hỏi mà bản cũ bỏ lửng, cộng một khối **Đọc thêm** ghi rõ tên công trình, tác giả,
nơi công bố và năm, kèm một câu vì sao nên đọc và mức ưu tiên (nền tảng / tra khi cần).
Mỗi chương cũng được thêm một dòng active recall tương ứng.

| Chương | Mục mới | Nguồn chính |
|--------|---------|-------------|
| A/03 | Đo bậc tăng trưởng bằng phép thử tỉ lệ nhân đôi | Sedgewick & Wayne, *Algorithms* 4th ed. §1.4 (2011) |
| A/04 | Máy trạng thái và bất biến bảo toàn | Lehman, Leighton, Meyer, *Mathematics for Computer Science* ch. 6 (MIT, 2018) |
| B/07 | Giảm khoá, Fibonacci heap, và số đo thực nghiệm | Fredman & Tarjan (JACM 1987); Larkin, Sen, Tarjan (ALENEX 2014) |
| B/08 | Bảo đảm mạnh hơn: băm cuckoo và băm bảng tra | Pagh & Rodler (J. Algorithms 2004); Pătraşcu & Thorup (JACM 2012) |
| B/09 | Splay và phỏng đoán tối ưu động | Sleator & Tarjan (JACM 1985); Demaine et al. (SICOMP 2007) |
| B/10 | Biến cấu trúc tĩnh thành động: Bentley–Saxe | Bentley & Saxe (J. Algorithms 1980); Fenwick (SP&E 1994) |
| B/11 | "α là tối ưu" trong mô hình nào | Tarjan (JCSS 1979); Fredman & Saks (STOC 1989) |
| C/14 | Biên giới: nhân số O(n log n), số mũ ω | Harvey & van der Hoeven (Annals of Math. 2021); Alman & Vassilevska Williams (SODA 2021) |
| C/16 | Bất đẳng thức tứ giác, SMAWK, Hirschberg | Yao (SIAM J. Alg. Disc. Meth. 1982); Aggarwal et al. (Algorithmica 1987); Hirschberg (CACM 1975) |
| C/17 | Rào cản sắp xếp và cách vượt | Thorup (JACM 1999); Duan et al. (STOC 2025, Best Paper) |
| C/18 | Từ đường tăng tới tối ưu hoá liên tục | Orlin (STOC 2013); Chen et al. (FOCS 2022, Best Paper) |
| D/21 | "Kiểm tra thì dễ" — dễ từ khi nào | Agrawal, Kayal, Saxena (Annals of Math. 2004) |
| D/22 | Vị từ thích nghi: trả giá chính xác đúng chỗ | Shewchuk (Discrete & Comput. Geometry 1997) |
| D/24 | Độ phức tạp tinh: cận dưới có điều kiện | Backurs & Indyk (SICOMP 2018 / STOC 2015); Gajentaan & Overmars (Comput. Geom. 1995) |

Hai chương nữa chỉ được thêm khối **Đọc thêm** (không thêm mục mới): B/12 (KMP, Aho–Corasick,
mảng hậu tố, skew O(n)) và C/20 (Karger–Stein, Karp–Rabin, Alon–Matias–Szegedy).
12 chương còn lại chưa có khối Đọc thêm — có thể bổ sung dần theo cùng khuôn.

Ngoài ra: `preamble/common.tex` có thêm môi trường `docthem` cho khối Đọc thêm; `refs.bib`
thêm 25 mục đã kiểm chứng từng trường (tác giả, tên, nơi công bố, năm); `97-doc-them.tex`
có thêm mục G về **cách chọn nguồn** (chỉ dùng công trình đã phản biện; tài liệu cộng đồng như
cp-algorithms/KACTL chỉ dùng để đối chiếu cài đặt, không dùng làm nguồn cho phát biểu);
`00-map.tex` ghi quy ước của khối Đọc thêm.

### Nguyên tắc đã theo trong đợt này

- **Chọn lọc**: mỗi chương chỉ thêm một mục, đặt đúng chỗ bản cũ để ngỏ một câu hỏi
  ("điều kiện đơn điệu thường phải kiểm bằng thực nghiệm", "α là tối ưu", "Dijkstra là O(m log n)").
  Không rải kết quả mới khắp chương, không đổi mạch có sẵn.
- **Trung thực về khoảng cách lý thuyết – thực hành**: mọi kết quả thiên hà (nhân số O(n log n),
  luồng m^(1+o(1)), AKS, Tango tree) đều kèm câu nói rõ là không nên cài, và nói rõ giá trị của nó
  nằm ở chỗ khác.
- **Chỉ số liệu kiểm chứng được**: các con số duy nhất được trích là số đo in trong sách của
  Sedgewick & Wayne (ThreeSum: tỉ lệ 8; 51,1 giây tại n = 8000) và các phát biểu định lý.
  Con số ω mới nhất (≈ 2,3712) được ghi rõ là **bản tiền ấn chưa qua phản biện**.
- **Kiểm tra**: mỗi mục trích dẫn được đối chiếu tác giả/nơi công bố/năm với dblp, ACM DL,
  Springer hoặc trang tạp chí trước khi ghi vào `refs.bib`.

Bản gộp sau cập nhật: **331 trang** (trước là 313), biên dịch sạch, không có trích dẫn treo.
