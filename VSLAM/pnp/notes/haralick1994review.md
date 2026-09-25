# Review and Analysis of Solutions of the Three Point Perspective Pose Estimation Problem — ghi chú đọc

| | |
|---|---|
| bibkey | `haralick1994review` |
| Venue, năm | International Journal of Computer Vision 13(3), tr. 331–356, 1994 (nhận bài 10/1990, sửa 3/1992 và 10/1993 [tr. 1]) |
| Bản đã đọc | `papers/haralick1994review.pdf` — bản tác giả lấy từ haralick.org; 26 trang, là bản quét của bản in IJCV (có số trang tạp chí 331–356, có lớp chữ OCR) |
| Mức đọc | lượt 3 (Keshav) cho §2, lời giải Grunert, "Singularity of Solutions", §4–§6 và Phụ lục II; lượt 2 cho năm lời giải còn lại và Phụ lục I |
| Người đọc | Claude (agent), 2026-09-25 — **Huy chưa đọc lại để ký** |
| Mức tin | giữ **A**. Lý do: bài có phản biện ở IJCV, và các đa thức của Grunert, Merritt, Fischler–Bolles, Finsterwalder, Grafarend mà tôi kiểm số đều đúng. Kèm cảnh báo: có ít nhất bốn lỗi in trong công thức (xem mục 8), nên đừng chép công thức từ bài mà không kiểm |
| Kiểm chứng | cửa (b) cho eq. (9), (8), (5), (13)–(17), (22), (27), (31), (52), Phụ lục I, hai ví dụ suy biến ở tr. 13 và thí nghiệm Tab. II–V. Cửa (a) cho eq. (10), (16), (51)–(52) (tôi tự suy dẫn lại). Chi tiết ở mục 7 |

## 1. Bài toán gốc và bối cảnh

P3P (ở đây gọi là *three point space resection*, theo tên bên trắc địa ảnh) hỏi: biết hình dạng một tam giác trong không gian và ba tia chiếu tới ba đỉnh của nó, hãy tìm vị trí ba đỉnh trong hệ camera [§1, tr. 1]. Theo các tác giả, bài toán có tối đa bốn nghiệm nằm trước tâm chiếu, cộng bốn nghiệm đối xứng nằm sau [§1, tr. 1] [T]. Nó cũng là lượng thông tin tối thiểu để bài toán có lời giải [§1, tr. 1] [T].

Bài kể lại lịch sử để giải thích vì sao bài toán bị giải lại nhiều lần mà không ai biết ai. Grunert giải trực tiếp lần đầu năm 1841, giới trắc địa ảnh Đức làm gọn lại vào các năm 1904 và 1925, rồi Merritt giải độc lập ở Mỹ năm 1949 [§1, tr. 1–2] [T]. Sau đó, trắc địa ảnh chuyển sang phương pháp lặp (Church 1945, 1948), vì trong nghề đó người ta thường đã biết thang đo và khoảng cách với sai số khoảng 10 % và góc với sai số khoảng 15°, đủ làm điểm khởi đầu cho lặp [§1, tr. 2] [T]. Thị giác máy thì ngược lại: thường không có nghiệm xấp xỉ nào để bắt đầu, nên lời giải trực tiếp quay lại quan trọng. Fischler và Bolles 1981 (`fischler1981ransac`) đã tự suy dẫn lại lời giải trực tiếp mà không biết các lời giải cũ [§1, tr. 2] [T].

Bài có hai mục tiêu [§1, tr. 2] [T]. Thứ nhất, trình bày lại sáu lời giải trong cùng một khung ký hiệu. Thứ hai, và mới hơn, là đo xem sai số làm tròn phụ thuộc thế nào vào cách tính: dùng lời giải nào, thứ tự đưa ba điểm vào ra sao, và tính bằng single hay double precision. Đi kèm là một phương pháp phân tích độ nhạy để chọn thứ tự tốt.

## 2. Giả thiết — kể cả giả thiết ngầm; bỏ đi thì hỏng ở đâu

- **Camera lỗ kim đã hiệu chỉnh**: ảnh ở khoảng cách `f` trước tâm chiếu, và tia đơn vị là `j_i = (u_i, v_i, f)/√(u_i²+v_i²+f²)` [§2, tr. 3] [T]. Nếu không biết `f`, ta không tính được `cos α, cos β, cos γ` và bài toán đổi thành P4Pf (`bujnak2008p4pf`) (tôi suy ra).
- **Đo không nhiễu**. Cả sáu lời giải là lời giải *chính xác* cho đúng ba điểm. Bài chỉ nghiên cứu sai số làm tròn, không đưa nhiễu đo nào vào thí nghiệm [§4, tr. 14–15] [T]. Vì vậy mọi kết luận về độ chính xác trong bài là kết luận về số học dấu phẩy động, không phải về độ bền với nhiễu pixel (tôi suy ra).
- **Ba điểm không thẳng hàng, tâm chiếu không đồng phẳng với chúng**. Khi có đồng phẳng, ma trận `A` trong eq. (53) suy biến [tr. 13] [T]. Phụ lục I cũng cần ba điểm không thẳng hàng để hệ 9×9 khả nghịch [tr. 22] [T].
- **Giả thiết ngầm ở Phụ lục I**: bài viết "we can assume z'_i = 0" [tr. 22], nghĩa là hệ toạ độ thế giới phải được xoay trước sao cho tam giác nằm trong mặt z' = 0. Bài không viết bước đổi hệ này ra (tôi suy ra; script của tôi phải tự thêm bước đó). Phụ lục I cũng *không* ép `R` trực chuẩn. Cột 3 được tính bằng tích có hướng (a.2), còn hai cột đầu lấy thẳng từ nghiệm tuyến tính. Khi dữ liệu có sai số, kết quả không còn là ma trận quay (mục 7 [2]).
- **Chọn nghiệm đúng**. Trong thí nghiệm, bài biết nghiệm thật nên chọn được nghiệm gần nó nhất (tôi suy ra từ cách định nghĩa ADE ở Step 4.1 [tr. 15]). Trong ứng dụng thật phải có điểm thứ tư hoặc RANSAC để phân biệt tới bốn nghiệm; bài không bàn chuyện này.
- **Phân bố dữ liệu thử**: x, y ~ U[−25, 25], z ~ U[f+a, b] với f = 1 [§4.1, tr. 14; Step 1, tr. 15] [T]. Với f = 1, phân bố này cho góc nhìn rất rộng: điểm có thể lệch trục quang tới khoảng 87° khi z = 1 (tôi suy ra). Mọi con số ở Tab. II–VII chỉ đúng với phân bố này.

## 3. Cơ chế — năm câu, rồi chi tiết có định vị

**Năm câu.** Định lý cos cho ba cạnh của tứ diện tạo bởi tâm chiếu và ba đỉnh cho ra ba phương trình bậc hai theo ba khoảng cách `s1, s2, s3`. Cả sáu lời giải đều làm cùng một việc: bỏ bớt ẩn bằng cách chia cho `s1` (hoặc dời gốc), rút về một ẩn, giải đa thức bậc bốn, hoặc bậc ba cộng các bậc hai, rồi thế ngược lại. Các lời giải chỉ khác nhau ở ba chỗ: cách đổi biến, cặp phương trình được dùng, và cách khử ẩn thứ hai (thế, khử trực tiếp, hay đưa vào tham số λ để biến một conic thành cặp đường thẳng). Khác biệt đó không đổi tập nghiệm nhưng đổi sai số làm tròn, và thứ tự đưa ba điểm vào cũng đổi sai số làm tròn. Chọn thứ tự theo độ nhạy chuẩn hoá của nghiệm đa thức (S_wn) cho kết quả gần với thứ tự tốt nhất.

**Chi tiết.**

- *Thiết lập* [§2, tr. 3; Fig. 1]: `a = ‖p2−p3‖, b = ‖p1−p3‖, c = ‖p1−p2‖`; `cos α = j2·j3, cos β = j1·j3, cos γ = j1·j2`; `p_i = s_i j_i`. Ba phương trình định lý cos là eq. (1)–(3) [tr. 3–4].
- *Grunert* [tr. 4]: đặt `s2 = u s1, s3 = v s1` (eq. (4)), rút ra ba biểu thức của `s1²` (eq. (5)), rồi hai phương trình (6), (7) theo u, v. Từ (6) ta có `u²`, thế vào (7) để ra u là hàm hữu tỉ của v (eq. (8), mẫu là `2(cos γ − v cos α)`). Thế tiếp vào (6) cho đa thức bậc bốn theo v (eq. (9)), với hệ số `A4..A0` in ở tr. 4. Mỗi nghiệm v cho một u qua (8), rồi `s1` qua (5) và `s2, s3` qua (4) [tr. 4] [T]. Bài không nói nên dùng biểu thức nào trong ba biểu thức của (5); tôi dùng dạng `b²/(1+v²−2v cos β)` vì dạng này chỉ cần v.
- *Khung so sánh* [tr. 4–6, Fig. 2]: Linnainmaa dùng phép đổi biến `s2 = u + cos γ s1`, `s3 = v + cos β s1`, còn các lời giải khác chia cho `s1`. Grunert dùng cặp phương trình (1,2) và (2,3); Merritt dùng (1,2) và (1,3). Grunert và Merritt khử ẩn bằng phép thế; Fischler–Bolles và Linnainmaa khử trực tiếp; Finsterwalder và Grafarend đưa vào λ [tr. 5] [T]. Tab. I [tr. 14] tóm tắt: lời giải của Fischler–Bolles và của Linnainmaa được đánh dấu "không có suy biến đại số", bốn lời giải còn lại thì có.
- *Finsterwalder* (lượt 2) [tr. 5–7]: lấy λ·(7) + (6) được một conic theo (u, v) (eq. (10)). Sau đó chọn λ sao cho biệt thức theo v là một bình phương hoàn hảo; khi đó conic suy biến thành cặp đường thẳng `v = um + n`. Điều kiện này chính là định thức 3×3 bằng 0 (eq. (13)) và cho một phương trình bậc ba theo λ (eq. (14)). Chỉ cần một nghiệm thực λ0 [tr. 7]. Mỗi đường thẳng thế vào (7) cho một phương trình bậc hai theo u (eq. (16)–(17)), tổng cộng bốn nghiệm. Bài nhấn mạnh cách tính ổn định cho phương trình bậc hai: tính nghiệm lớn trước, rồi suy nghiệm nhỏ từ tích hai nghiệm [tr. 5, tr. 7] [T].
- *Merritt* (lượt 2) [tr. 7–8]: đa thức bậc bốn theo u (eq. (22)) với hệ số `B4..B0` và K. Theo bài, đa thức này là eq. (9) sau khi hoán đổi b↔c và β↔γ [tr. 12] [T]. Merritt giải đa thức bậc bốn theo kiểu Ferrari, qua một phương trình bậc ba phụ [tr. 8].
- *Fischler–Bolles* (lượt 2) [tr. 9]: khử v bằng cách nhân chéo (23), (24) rồi trừ, ra đa thức bậc bốn theo u (eq. (27)) với hệ số `D4..D0`.
- *Grafarend–Lohse–Schaffrin* (lượt 2) [tr. 9–11]: đưa về dạng toàn phương thuần nhất `s^T A(λ) s = 0` (eq. (30)), chọn λ để `det A = 0` (một phương trình bậc ba). Khi đó quadric thành cặp mặt phẳng; xoay toạ độ để bỏ số hạng chéo (eq. (33)–(37)). Bài nhắc thêm một biến thể đơn giản hơn của Lohse 1989 [tr. 11].
- *Linnainmaa–Harwood–Davis* (lượt 2) [tr. 11–12]: dời gốc theo (42)–(43), bình phương hai lần để khử uv, ra đa thức bậc tám theo `s1` nhưng chỉ chứa luỹ thừa chẵn, tức bậc bốn theo `s1²` (eq. (52)).
- *Suy biến* [tr. 12–13]: bài chia làm hai loại. Loại hình học gồm hình trụ nguy hiểm (*danger cylinder*: tâm chiếu nằm trên mặt trụ qua ba đỉnh có trục vuông góc với mặt tam giác). Ở đó ma trận B của eq. (53) suy biến, nghiệm không ổn định [Fig. 3a]. Trường hợp đồng viên (tâm chiếu nằm trên đường tròn ngoại tiếp tam giác) thì mọi hệ số của (9) bằng 0 và bài toán không xác định [Fig. 3b]. Loại đại số xuất hiện khi mẫu số của phép thế bằng 0, ví dụ `cos γ − v cos α` trong (8). Loại này xảy ra với Grunert, Finsterwalder, Merritt và Grafarend, ngay cả ở cấu hình tứ diện đều vốn không có vấn đề gì về hình học [tr. 13] [T].
- *Tư thế tuyệt đối* [tr. 13–14; Phụ lục I, tr. 21–22]: `p_i = R p'_i + T` (eq. (54) = (a.1)). Bài giải tuyến tính 9 ẩn `r11, r12, r21, r22, r31, r32, tx, ty, tz` (hệ `AX = B`, 9×9), rồi lấy cột 3 của R bằng tích có hướng (a.2).
- *Phân tích số* [Phụ lục II, tr. 22–25]: độ nhạy của nghiệm `x = z_j` theo hệ số `a_i` được tính bằng `S_i = −(∂P/∂a_i)/(∂P/∂x)`. Độ nhạy chuẩn hoá là `S^x_{a_i} = (a_i/x) ∂x/∂a_i`. Từ đó bài định nghĩa `S_w = Σ|S_i|`, `S_wn = Σ|S^x_{a_i}|` [A.2.3, A.2.5], và các cận sai số làm tròn xấu nhất ε_ware, ε_wrre theo mô hình của Wilkinson [A.2.4]. Tích của độ nhạy với cận sai số cho "độ trôi nghiệm" ε_sware, ε_swrre [A.2.5]. Mỗi đại lượng này được dùng làm tiêu chí chọn một trong sáu hoán vị [Step 5.5, tr. 16].

## 4. Ký hiệu của bài ↔ ký hiệu của khảo sát

| Bài | Khảo sát (`code/common.py`) | Ghi chú |
|---|---|---|
| `p'_i` (hệ thế giới) | `X_w,i` | [tr. 13, eq. (54)] |
| `p_i = (x_i, y_i, z_i)` (hệ camera) | `X_c,i = R X_w,i + t` | |
| `R`, `T` trong `p_i = R p'_i + T` | `R`, `t` | cùng chiều thế giới → camera, không phải đảo ngược |
| `j_i` (tia đơn vị) | `f_i` (bearing) | bài dùng `f` cho **tiêu cự**, khảo sát dùng `f` cho tia: dễ nhầm |
| `f` (tiêu cự) | `K[0,0] = K[1,1]` (tính theo pixel) | bài giả định điểm chính ở gốc, pixel vuông |
| `(u_i, v_i)` (toạ độ ảnh) | `u` (pixel) sau khi bỏ `K` | **lưu ý**: `u, v` trong bài còn là *tỉ số* `s2/s1, s3/s1` (Grunert) hoặc hiệu dời (Linnainmaa), trùng tên với toạ độ ảnh |
| `s_i` | `‖X_c,i‖` | khoảng cách tới tâm chiếu, không phải độ sâu z |
| `a, b, c` | `‖X_w,2−X_w,3‖, ‖X_w,1−X_w,3‖, ‖X_w,1−X_w,2‖` | cạnh đối diện đỉnh 1, 2, 3 |
| `α, β, γ` | `∠(f_2,f_3), ∠(f_1,f_3), ∠(f_1,f_2)` | |
| `K` (Merritt, tr. 8), `K` (eq. (36)) | — | hai đại lượng khác nhau, không liên quan tới ma trận nội tham số |

## 5. Bằng chứng — dữ liệu, phần cứng, baseline, con số kèm điều kiện, số lần lặp

**Điều kiện** [§4, §4.1, §4.2, §5, tr. 14–16]: tam giác ngẫu nhiên với x, y ~ U[−25, 25], z ~ U[1, 5] hoặc U[5, 20] (và U[25, 75] ở Tab. VI, VII), f = 1, không nhiễu. Mỗi tam giác được thử với cả sáu hoán vị đỉnh. N1 = 10 000 lần thử cho Tab. II–V và N2 = 100 000 cho Tab. VI–VII. Mã viết bằng C, chạy trên Sun 3/280 và VAX 8500 (VMS). Tab. VI–VII lấy từ VAX; các bảng khác mặc định lấy từ Sun [tr. 16, tr. 20] [Đ]. Bộ tìm nghiệm là phương pháp Laguerre [tr. 16; A.2.3]. Chỉ số đo là ADE: tổng ba khoảng cách giữa đỉnh tính được và đỉnh thật; MADE là trung bình của ADE [Step 4.1, tr. 15].

**Con số chính** (1 < z < 5, 10 000 lần thử, Sun 3/280):

- Trong Tab. II (thứ tự điểm ngẫu nhiên), MADE ở double / single là: Grunert 0.19e−8 / 0.31e−1, Finsterwalder 0.22e−10 / 0.89e−2, Merritt 0.11e−5 / 0.28e−1, Fischler 0.62e−8 / 0.14e−1, Linnainmaa 0.74e−7 / 0.32e−1, Grafarend 0.46e−8 / 0.20e−1 [Tab. II, tr. 16] [Đ]. Độ lệch chuẩn lớn hơn trung bình khoảng 100 lần; ví dụ Grunert double có SD = 0.16e−6 [Tab. II] [Đ]. Như vậy phân bố sai số có đuôi rất dài.
- Tab. IV (double, MADE thứ tự tốt nhất / xấu nhất trong sáu hoán vị): Grunert 0.41e−12 / 0.60e−8, Finsterwalder 0.34e−12 / 0.20e−9, Merritt 0.26e−10 / 0.18e−4 [Tab. IV, tr. 18] [Đ]. Tab. III (single): Grunert 0.10e−3 / 0.81e−1, Finsterwalder 0.74e−4 / 0.59e−1 [Tab. III, tr. 17] [Đ].
- Theo bài, kết quả double tốt hơn single khoảng 10^7 lần, và thứ tự tốt nhất tốt hơn thứ tự xấu nhất khoảng 10^4 lần [tr. 17, tr. 18] [T] (đây là tỉ số giữa các trung bình trong bảng).
- Chọn hoán vị theo S_wn cho MADE 0.89e−12; chọn theo ε_sware cho 0.93e−12 và theo ε_swrre cho 0.90e−12. Để so sánh: thứ tự tốt nhất cho 0.41e−12 và thứ tự ngẫu nhiên cho 0.19e−8 [Tab. V, tr. 18] [Đ]. Ngược lại, chọn theo S_w (không chuẩn hoá) cho 0.15e−8, gần như không hơn ngẫu nhiên, và chọn theo ε_wrre cho 0.40e−8 [Tab. V] [Đ].
- Với 100 000 lần thử (Tab. VI, VAX), S_wn cho 9.18e−12 so với 2.22e−07 của thứ tự ngẫu nhiên, ở 1 < z < 5 [Tab. VI, tr. 21] [Đ]. Các ca "lỗi lớn" (ADE > 10^−7) chiếm khoảng 69, 96 và 495 trên 100 000 lần thử ở ba khoảng độ sâu [tr. 20; Tab. VII] [Đ].
- Bài giải thích Merritt kém vì bước chuyển bậc bốn sang bậc ba tự nó kém ổn định. Khi giải thẳng đa thức bậc bốn của Merritt bằng Laguerre, kết quả "tương tự Grunert" [tr. 16] [Đ, không có số].

**Không có**: không có nhiễu đo, không đo thời gian chạy, không có dữ liệu thật, và không có cấu hình gần hình trụ nguy hiểm được dựng có chủ đích. Phần ổn định chỉ phân tích chi tiết cho Grunert [Step 5, tr. 15].

## 6. Đóng góp thật sự (thường nhỏ hơn abstract)

- [M] Đóng góp lâu bền nhất là **bản tổng hợp có ký hiệu thống nhất** của sáu lời giải, kèm khung so sánh ở Fig. 2. Ngày nay nó là cửa vào chuẩn cho lịch sử P3P. Về mặt thuật toán, bài không đưa ra lời giải P3P mới nào.
- [M] Thông điệp "cách tính quan trọng không kém phương trình" đúng và có ích. Các bộ giải P3P về sau, như `persson2018lambdatwist`, xem độ ổn định số là tiêu chí thiết kế chính. Tuy vậy, con số "một nghìn lần" ở abstract là tỉ số giữa các *trung bình* của một phân bố có đuôi dài. Ở trung vị, khác biệt chỉ khoảng 20 lần (mục 7 [5]).
- [M] Phần về số nghiệm ("tối đa bốn nghiệm", "thường là hai") chỉ được tuyên bố, không được chứng minh hay đo trong bài. Câu "thường là hai" được dẫn lại từ `wolfe1991perspective` [tr. 4]. Vì vậy mô tả trong `danh-muc.md` ("vì sao có tới bốn nghiệm") hơi quá so với nội dung bài.
- [M] Tiêu chí S_wn cần biết nghiệm nào của đa thức là nghiệm đúng, trong khi ở ứng dụng thật ta chưa biết điều đó (mục 9). Vì vậy giá trị thực dụng của phần "analysis method" chưa được chứng minh.

## 7. Kiểm chứng của người ghi chú — script trong `code/`, lệnh chạy, kết quả thật

Script gồm `code/haralick1994review_p3p.py`, cài lại các công thức *đúng như bản in*, có cờ để bật bản in sai hoặc bản đã sửa, và `code/haralick1994review_check.py`. Numpy 2.4.6, OpenCV 5.0.0. Nghiệm đa thức được tìm bằng trị riêng của ma trận đồng hành, tính trong đúng kiểu `float32`/`float64`; bài dùng Laguerre, và đây là khác biệt chính giữa hai thí nghiệm.

Lệnh chạy (mặc định, 61 s):

```
python3 VSLAM/pnp/code/haralick1994review_check.py
```

Kết quả thật (đã cắt bớt):

```
[1] Chép công thức: phần dư tương đối của từng đa thức tại nghiệm thật (200 cảnh common.make_scene)
  PASS  Grunert eq.(9) tại v=s3/s1                                                 max=4.3e-15
  PASS  Merritt eq.(22) tại u=s2/s1                                                max=3.4e-15
  PASS  Fischler-Bolles eq.(27) tại u=s2/s1                                        max=7.5e-15
  PASS  Grafarend eq.(31) tại (p,q)=(s2/s1,s3/s1), lambda ngẫu nhiên               max=1.4e-15
  PASS  Grafarend: det A(lambda) có nghiệm thực làm A hạng 2 (sigma_min/sigma_max) max=3.2e-14
  PASS  Finsterwalder: nghiệm của cubic (14) làm định thức (13) = 0                max=1.5e-15
  PASS  Finsterwalder: conic (10) tại (u,v) thật với lambda0                       max=1.2e-15
  PASS  tr.12: (9) với b<->c, beta<->gamma, nhân c^4 == (22)                       max=2.8e-14
  PASS  (27) == -(22) (tôi suy ra: D_i = -B_i)                                     max=1.9e-14
  FAIL  Linnainmaa eq.(52), r2 CHÉP ĐÚNG BẢN IN (-c^2 q5 - b^2 q6)                 max=1.0e+00
  PASS  Linnainmaa eq.(52), r2 tôi sửa (-c^2 q5^2 - b^2 q6^2)                      max=1.6e-11
[2] Grunert đầu-cuối (eq. (4),(5),(8),(9) + Phụ lục I), cảnh common.make_scene, nhiễu 0
  PASS  |s - s_thật|/|s_thật|        : trung vị 5.6e-14, p99 8.0e-10, max 1.7e-07
  PASS  ||R_PhụlụcI - R||_F         : trung vị 2.1e-13, p99 8.1e-09, max 2.7e-06
  PASS  |t - t_thật|/|t_thật|        : trung vị 6.2e-13, p99 4.6e-08, max 1.4e-05
    ||R^T R - I|| của R Phụ lục I (không ép trực chuẩn): trung vị 2.7e-13, p99 8.2e-09, max 1.1e-06
  PASS  số nghiệm thực dương tối đa gặp = 4 (<= 4)
    Phân bố số nghiệm thực dương (Grunert, đối chiếu cv2.solveP3P), 10000 cấu hình mỗi loại:
    common.make_scene (FOV ~44 deg, z 4-8)       0:0.000 1:0.043 2:0.880 3:0.004 4:0.072 >4:0.000 | trùng số nghiệm với cv2 1.000
    như §4.1 bài: x,y~U[-25,25], z~U[1,5], f=1   0:0.000 1:0.660 2:0.332 3:0.006 4:0.003 >4:0.000 | trùng số nghiệm với cv2 1.000
    như §4.1 bài: z~U[5,20]                      0:0.000 1:0.445 2:0.486 3:0.038 4:0.030 >4:0.000 | trùng số nghiệm với cv2 1.000
[3] Finsterwalder đầu-cuối (eq. (10)-(17)), 2000 cảnh common.make_scene, nhiễu 0
  PASS  hệ số A,C lấy từ eq.(16) (b^2-m^2c^2, -c^2n^2): tìm lại s thật (sai số tương đối < 1e-6) trong 2000/2000 cảnh; trung vị sai số 3.1e-15
  FAIL  hệ số A,C CHÉP ĐÚNG BẢN IN tr.7 (b^2-mc^2, -cn^2): tìm lại s thật (sai số tương đối < 1e-6) trong 0/2000 cảnh; trung vị sai số 7.3e-01
    tr.5: 'v_small = C/(A v_large)' khác nghiệm nhỏ thật trong 163/163 trường hợp có nghiệm thực (đúng phải là (A u^2+2Du+F)/(C v_large) — tôi suy ra)
[4] Trường hợp suy biến bài nêu ở tr. 13
    Grunert A = [-0.  0.  0.  0. -0.]   (Merritt B, F&B D, Linnainmaa t, Finsterwalder G,H,I,J: cũng toàn 0)
  PASS  đồng viên: mọi hệ số của (9), (22), (27) bằng 0 như bài nói
    tứ diện đều: A = [-0.  2. -4.  2. -0.], P(1) = -8.9e-16, mẫu (8) tại v=1: 0.0e+00, tử (8) tại v=1: 0.0e+00
  PASS  tứ diện đều: v=1 là nghiệm của (9) và (8) thành 0/0
Tổng: 2 dòng FAIL
```

Hai dòng FAIL là **kết quả có chủ đích**: chúng xác nhận hai lỗi in (mục 8). Mọi dòng còn lại là PASS.

Phần [5] chạy thêm với đúng N1 = 10 000 của bài (lệnh `... --trials 10000 --count-trials 20000`, 143 s). Điều kiện: 1 < z < 5, f = 1, x, y ~ U[−25, 25]. ADE tính như Step 4.1, chọn nghiệm gần nghiệm thật nhất, và "thất bại" là không trả về nghiệm nào:

```
lời giải  prec thất bại  MADE random   MADE best  MADE worst  rand/best worst/best  trung vị r/b/w          %w/b>1e3 | bài (random, best, worst)
grunert   f64         0     2.05e-09    6.51e-13    4.59e-08     3150.4    70539.4   5.6e-14/1.5e-14/3.4e-13   8.4 | 1.90e-09, 4.10e-13, 6.00e-09
               chọn hoán vị theo S_wn nhỏ nhất (oracle nghiệm): MADE 1.25e-12  (bài Tab. V/VI: 0.89e-12 / 9.18e-12)
grunert   f32        48     2.85e-02    1.90e-04    9.94e-02      150.2      523.1   1.9e-05/7.3e-06/9.6e-05   5.9 | 3.10e-02, 1.00e-04, 8.10e-02
finster   f64         0     1.87e-10    3.17e-13    1.32e-09      591.4     4169.3   8.6e-14/1.7e-14/5.2e-13   5.1 | 2.20e-11, 3.40e-13, 2.00e-10
finster   f32        31     9.09e-03    1.68e-04    3.84e-02       54.2      228.9   3.9e-05/8.2e-06/2.2e-04   4.2 | 8.90e-03, 7.40e-05, 5.90e-02
(5 < z < 20)  grunert f64: random 3.03e-10, best 6.33e-13, worst 9.74e-09, S_wn 1.46e-12; trung vị 9.1e-14/2.1e-14/7.3e-13
```

**Đọc kết quả** [M]:

1. **Công thức.** Các đa thức (9), (22), (27), (31), (13)/(14) và (52) (sau khi sửa r2) đều bằng 0 tại nghiệm thật, sai khác chỉ ở mức làm tròn. Nhận xét ở tr. 12 rằng Merritt = Grunert sau khi hoán đổi (b, β) ↔ (c, γ) là đúng. Ngoài ra (27) = −(22) theo đúng từng hệ số. Như vậy, về mặt đại số, Merritt và Fischler–Bolles giải *cùng một đa thức* (tôi suy ra); bài chỉ nói chúng "khác cách suy dẫn".
2. **Grunert đầu-cuối.** Grunert kết hợp với Phụ lục I khôi phục đúng tư thế trong mọi cảnh không nhiễu. Tuy vậy, sai số có đuôi dài: trung vị 5.6e−14 nhưng lớn nhất 1.7e−7, ngay cả khi dùng double và không nhiễu. Đuôi này đi cùng nghiệm gần kép (|P'(v)| nhỏ) và mẫu số (8) nhỏ; trong một lần chẩn đoán riêng (không nằm trong script, cùng 2000 cảnh), hệ số tương quan log-log lần lượt là −0.84 và −0.78. R của Phụ lục I không trực chuẩn tới 1.1e−6. Nếu đo sai số quay bằng `arccos((tr(RᵀR̂)−1)/2)` thì một R không trực chuẩn cỡ 1e−6 có thể báo sai tới 0.02°, vì vậy script dùng chuẩn Frobenius.
3. **Số nghiệm.** Qua 10 000 cấu hình mỗi loại, không có cấu hình nào có hơn 4 nghiệm dương, và số nghiệm trùng với `cv2.solveP3P` ở 100 % cấu hình (99.9 % trong lần chạy 20 000). Kết quả này khớp với khẳng định "tối đa bốn". Câu "Most of the time it gives two solutions" [tr. 4] chỉ đúng khi góc nhìn hẹp: 88 % cấu hình có hai nghiệm với cảnh FOV khoảng 44°. **Trên đúng phân bố thử của bài**, 66 % cấu hình (1 < z < 5) và 45 % cấu hình (5 < z < 20) chỉ có **một** nghiệm dương.
4. **Ổn định số: khớp về bậc độ lớn.**
   - Grunert, double: MADE với thứ tự ngẫu nhiên là 2.05e−9 (bài 1.9e−9) và với thứ tự tốt nhất là 6.5e−13 (bài 4.1e−13). Thứ tự xấu nhất cho 4.6e−8, gấp 8 lần con số 6.0e−9 của bài.
   - Grunert, single: 2.85e−2 / 1.9e−4 / 9.9e−2 so với 3.1e−2 / 1.0e−4 / 8.1e−2 của bài, rất gần.
   - Finsterwalder, single: 9.1e−3 so với 8.9e−3 của bài. Finsterwalder, double, thứ tự tốt nhất: 3.2e−13 so với 3.4e−13 của bài.
   - Finsterwalder, double, thứ tự ngẫu nhiên: 1.9e−10, **kém 9 lần** con số 2.2e−11 của bài. Nguyên nhân có thể là quy tắc chọn λ0 của tôi (bài không nói cách chọn) và bộ tìm nghiệm.
   - Xếp hạng Finsterwalder tốt hơn Grunert (khi so trung bình) được tái lập.
   - Chọn thứ tự theo S_wn cho 1.25e−12, gần con số 0.89e−12 ở Tab. V. Đây là kết quả tốt nhất và nhất quán nhất với bài.
5. **Nhưng "nghìn lần" là hiện tượng của trung bình.** Tỉ số worst/best của MADE là khoảng 7e4, cùng chiều với khoảng 1e4 của bài. Ở **trung vị**, thứ tự xấu nhất (3.4e−13) chỉ kém thứ tự tốt nhất (1.5e−14) khoảng 23 lần. Chỉ có 8.4 % số lần thử có ADE_worst/ADE_best > 1000. MADE cũng không ổn định theo cỡ mẫu. Với cùng bộ sinh số, N = 1500 cho MADE ngẫu nhiên của Grunert là 1.5e−8, còn N = 10 000 cho 2.05e−9; chính bài cũng có Random = 0.19e−8 ở Tab. V và 2.22e−7 ở Tab. VI. Vì vậy so sánh giữa các lời giải bằng MADE chỉ có ý nghĩa ở mức bậc độ lớn.

## 8. Chỗ tôi không tin

- **Lỗi in trong công thức, đã kiểm bằng số** [M]:
  (i) Trong eq. (51) [tr. 11], `r2` in `−c²q5 − b²q6`. Tôi tự suy dẫn lại thì phải là `−c²q5² − b²q6²`. Bản in cho phần dư tương đối khoảng 1, bản sửa cho 1.6e−11.
  (ii) Khối "numerically stable way to calculate u" [tr. 7] in `A = b² − mc²` và `C = −cn² + …`. Hai hệ số này mâu thuẫn với chính eq. (16) (`b² − m²c²`, `−c²n²`). Dùng bản in, script tìm lại nghiệm trong 0/2000 cảnh.
  (iii) Ở tr. 5, bài in `v_small = C/(A v_large)`. Với phương trình bậc hai theo v là `Cv² + 2(Bu+E)v + (Au²+2Du+F) = 0`, tích hai nghiệm là `(Au²+2Du+F)/C`, nên công thức in sai trong 163/163 lần thử.
  (iv) Trong Fig. 2 [tr. 6], vế phải của (1)–(3) in là "= 0" thay vì a², b², c².
  Không lỗi nào ảnh hưởng tới Grunert, là lời giải bài dùng để phân tích.
- **"Tai nạn" của trung bình** [M]: các kết luận "tốt hơn 10^3–10^4 lần" và "Finsterwalder chính xác nhất" dựa trên MADE, một trung bình bị vài ca gần suy biến chi phối. Bằng chứng nằm ngay trong bài: SD lớn hơn trung bình khoảng 100 lần [Tab. II], và MADE ngẫu nhiên nhảy từ 0.19e−8 (Tab. V) lên 2.22e−7 (Tab. VI) chỉ vì đổi N và máy. Bài không báo trung vị hay phân vị. Histogram ở Fig. 4 có thang log, nhưng không có con số đọc được.
- **Tiêu chí chọn thứ tự cần biết trước nghiệm** [M]: S_wn được định nghĩa tại "zero z_j" [A.2.3, tr. 23]. Bài không nói z_j là nghiệm nào trong tối đa bốn nghiệm; trong thí nghiệm, tác giả biết nghiệm thật. Script của tôi cũng dùng nghiệm thật (oracle). Nếu không có oracle, chưa rõ tiêu chí này còn tốt như vậy không.
- **"Most of the time it gives two solutions"** [tr. 4]: câu này mượn từ Wolfe et al. mà không nêu điều kiện. Trên chính phân bố thử của bài, trường hợp phổ biến nhất lại là một nghiệm (mục 7, điểm 3).
- **Tab. I đánh dấu Fischler–Bolles "không có suy biến đại số"** [tr. 14]: tôi chỉ tin một phần [M]. Theo kiểm của tôi, đa thức của Fischler–Bolles trùng với của Merritt (D = −B). Merritt bị gắn suy biến vì mẫu số `u cos α − cos β` [tr. 13]. Fischler–Bolles vẫn phải lấy v từ (26) hoặc (25) [tr. 9], và (26) chia cho `2c²(cos α u − cos β)`, tức là cùng mẫu số đó. Vậy "không suy biến" chỉ đúng nếu luôn dùng (25). Bài không nói rõ điều này.
- **Không có nhiễu** [M]: bài bàn về độ chính xác trong kỷ nguyên "better sensors and higher image resolution" [tr. 2] nhưng không có một thí nghiệm nào có nhiễu pixel. Với nhiễu 1 px, sai số hình học lớn hơn sai số làm tròn double hàng chục bậc độ lớn. Vì vậy trong thực tế, lựa chọn giữa sáu lời giải chủ yếu quan trọng khi tính bằng single precision hoặc ở vùng gần suy biến.

## 9. Chỗ tôi chưa hiểu (→ `99-chua-biet.md`)

- Khi chạy thật, S_wn được tính tại nghiệm nào của đa thức (9): lớn nhất trên các nghiệm thực, hay tổng, hay chỉ nghiệm đúng? Bài không nói [A.2.3, Step 5.1]. Tôi chưa biết tiêu chí này còn hiệu quả không khi chưa biết nghiệm đúng.
- Với Finsterwalder, khi phương trình bậc ba (14) có ba nghiệm thực, nên chọn λ0 nào [tr. 7: "any root"]? Script của tôi chọn nghiệm làm cả hai biệt thức không âm và lớn nhất. MADE ngẫu nhiên double của tôi kém bài 9 lần, nên có thể tác giả chọn theo một quy tắc khác mà họ không ghi.
- Vì sao đuôi sai số của Grunert ở double (tới 1.7e−7 trên cảnh FOV 44°) gắn với nghiệm gần kép? Nó chỉ là độ nhạy cơ bản `sqrt(eps)` ở nghiệm kép, hay có thêm phần khuếch đại từ mẫu số (8)? Tôi mới thấy tương quan, chưa tách được hai nguyên nhân.
- Liên hệ hình học giữa "hình trụ nguy hiểm" [Fig. 3a] và nghiệm kép của (9): mọi cấu hình có nghiệm kép có nằm trên hình trụ nguy hiểm không? Tôi chưa kiểm được. Bài chỉ lập luận qua ma trận B của eq. (53).
- Bảng VII: số ca lỗi lớn tăng từ khoảng 69 lên khoảng 495 khi độ sâu tăng lên 25–75 [tr. 20]. Bài không giải thích vì sao điểm xa hơn lại gặp suy biến nhiều hơn.

## 10. Quan hệ với các bài khác trong `refs.bib`

- `fischler1981ransac`: là một trong sáu lời giải được tổng hợp. Bài viết rằng Fischler–Bolles "apparently not aware" các lời giải cũ [tr. 9] [T].
- `wolfe1991perspective`: là nguồn của câu "thường hai nghiệm" [tr. 4]. Kiểm của tôi cho thấy câu này phụ thuộc mạnh vào góc nhìn.
- `gao2003p3p`: làm tiếp phần mà bài này bỏ ngỏ, tức phân loại đầy đủ số nghiệm thực. Bài này chỉ nêu cận trên bằng 4 (tôi suy ra, chưa đọc gao2003p3p).
- `kneip2011p3p`, `ke2017p3p`, `persson2018lambdatwist`, `ding2023p3p`, `wu2025conic`: là các bộ giải P3P về sau. Theo mô tả trong `danh-muc.md`, Lambda Twist giải qua chéo hoá và chỉ cần *một* nghiệm của phương trình bậc ba. Về cấu trúc, cách đó gần với ý của Finsterwalder và Grafarend ở bài này: chọn λ để conic hoặc quadric suy biến thành cặp đường thẳng hoặc cặp mặt phẳng (tôi suy ra, chưa đọc persson2018lambdatwist). Nếu đúng vậy, lời giải chính xác nhất trong Tab. II chính là tổ tiên của bộ giải P3P hiện đại được đánh giá cao.
- `haralick1989pose`: cùng nhóm tác giả, được dẫn cho bài toán tư thế tuyệt đối [tr. 2].
- Horn 1988 (tư thế tuyệt đối dạng đóng bằng ma trận trực chuẩn) được bài dẫn [tr. 14] nhưng **không có trong refs.bib**. Nếu bài học cần nhắc cách lấy R trực chuẩn thay cho Phụ lục I, nên thêm Horn 1988 sau khi kiểm nguồn.
- Grunert 1841, Finsterwalder–Scheufele 1937, Merritt 1949, Grafarend–Lohse–Schaffrin 1989 và Linnainmaa–Harwood–Davis 1988 là nguồn gốc của các lời giải nhưng **không có trong refs.bib**. Chỉ Linnainmaa 1988 (IEEE T-PAMI 10(5)) là dễ tìm để đưa vào nếu cần.

## 11. Nó đổi gì trong suy nghĩ

- Trước khi đọc, tôi nghĩ "bộ giải P3P" là một công thức. Sau khi đọc, tôi thấy nó là một *đường tính*: cùng một đa thức (Merritt ≡ −Fischler–Bolles) nhưng thứ tự điểm, cách khử ẩn và công thức nghiệm bậc hai quyết định sai số. Khi đánh giá một bộ giải mới, cần hỏi nó xử lý mẫu số gần 0 và nghiệm gần kép ra sao, chứ không chỉ hỏi đa thức của nó bậc mấy.
- Tôi cũng học được một bài học về đo lường: với sai số có đuôi dài, luôn phải báo trung vị và phân vị bên cạnh trung bình. Nếu chỉ báo trung bình, bài này đã phóng đại khác biệt điển hình (khoảng 20 lần) thành "nghìn lần".
- Câu "P3P thường có hai nghiệm" không phải là hằng số. Nó phụ thuộc vào trường nhìn. Với camera góc rộng hoặc fisheye, trường hợp một nghiệm có thể chiếm đa số (theo kiểm của tôi với f = 1, |x|, |y| ≤ 25 z).

## 12. Câu hỏi tự kiểm (3–5 câu, hỏi *vì sao* / *khi nào hỏng*)

1. Vì sao cấu hình tứ diện đều (a = b = c, α = β = γ = 60°), vốn không có vấn đề gì về hình học, lại làm lời giải Grunert hỏng? Phải đổi gì (thứ tự điểm, cặp phương trình, hay biểu thức lấy u) để tránh?
2. Khi tâm chiếu nằm trên đường tròn ngoại tiếp tam giác, vì sao mọi hệ số của (9) bằng 0? Điều đó nói gì về số nghiệm của bài toán hình học, chứ không chỉ về thuật toán?
3. Vì sao chọn thứ tự theo S_w (không chuẩn hoá) gần như vô dụng (0.15e−8 so với 0.19e−8 của thứ tự ngẫu nhiên, Tab. V), trong khi S_wn (chuẩn hoá) lại tốt?
4. Nếu thêm nhiễu 0.5 px vào ảnh 640×480 với f = 800 px, sai số làm tròn của lời giải xấu nhất còn đáng kể không? Ở chế độ nào (single precision, gần hình trụ nguy hiểm) thì nó vẫn đáng kể?
5. Phụ lục I giải tuyến tính rồi lấy tích có hướng. Khi nào kết quả không còn là ma trận quay, và nên sửa bằng cách nào (chiếu SVD, hay dùng Horn 1988)?

## Trích đoạn nguyên văn làm bằng chứng

- "Three points is the minimal information to solve such a problem." [tr. 1]
- "Depending on the order of the substitutions utilized, the relative error can change over a thousand to one." [tr. 1]
- "This difference is due entirely to the way the calculations are performed and not due to any geometric structural instability of any problem instance." [tr. 1]
- "This fourth order polynomial equation can have as many as four real roots." [tr. 4]
- "Most of the time it gives two solutions (Wolfe et al. 1991)." [tr. 4]
- "Solve this equation for any root" [tr. 7]
- "The accuracy of the best permutation is about a ten thousand times better than the accuracy obtained by the worst case" [tr. 18]
- "Table VII shows that the singular cases do not really happen in these experiments" [tr. 20]
