# EPnP: An Accurate O(n) Solution to the PnP Problem — ghi chú đọc

| | |
|---|---|
| bibkey | `lepetit2009epnp` |
| Venue, năm | *International Journal of Computer Vision* 81(2), 2009 (nhận bài 15/4/2008, chấp nhận 25/6/2008, DOI 10.1007/s11263-008-0152-6 in trên trang đầu) [tr. 1]. Bản mở rộng của bài ICCV 2007 cùng nhóm, thêm bước Gauss–Newton [§1, tr. 3] |
| Bản đã đọc | `papers/lepetit2009epnp.pdf` — nguồn: https://www.tugraz.at/fileadmin/user_upload/Institute/ICG/Images/team_lepetit/publications/lepetit_ijcv08.pdf, 12 trang (bản tác giả, dàn trang Springer nhưng không có số trang tạp chí) |
| Mức đọc | lượt 3 (Keshav): dựng lại toàn bộ thuật toán thành code và chạy |
| Người đọc | Claude (agent), 2026-09-25 — **Huy chưa đọc lại để ký** |
| Mức tin | giữ A — venue đầu ngành, thuật toán tôi cài lại từ mô tả trong bài khôi phục pose chính xác trên dữ liệu không nhiễu; nhưng bài có lỗi in (eq. (15)), mâu thuẫn nội bộ (Fig. 7 vs văn bản) và mô tả mơ hồ ở trường hợp phẳng — xem mục 8 |
| Kiểm chứng | eq. (1)–(8) và ca N = 1, 2, 4: cửa (a) + (b); ca phẳng N = 3 (§3.4): cửa (b) cho thấy mô tả của bài **không đủ** — xem mục 7 [2]; eq. (15): cửa (a) phát hiện thiếu bình phương, (b) chạy với bản đã sửa; tuyên bố O(n): cửa (b); đường cong Fig. 5: cửa (b) định tính, lệch định lượng — mục 7 |

## 1. Bài toán gốc và bối cảnh

PnP ở đây là bài toán có nội tham số: biết `K`, biết n cặp (điểm 3D trong hệ thế giới, pixel), tìm `R, t` [§1, tr. 1]. Cái khó mà bài nhắm tới không phải là số nghiệm hay tính tối ưu, mà là **độ phức tạp theo n khi n lớn và có nhiễu**: ứng dụng tracking theo điểm đặc trưng cần xử lý hàng trăm tương ứng nhiễu trong thời gian thực [§1, tr. 1].

[T] Theo phần tổng quan của tác giả, trước đó có ba nhóm [§1–2, tr. 1–4]. Nhóm bộ giải cho n cố định nhỏ (P3P, P4P) không dùng được độ dư của nhiều điểm. Nhóm bộ giải không lặp cho n tuỳ ý đều khử bằng cách giải độ sâu của từng điểm rồi căn chỉnh 3D–3D; cái rẻ nhất là Fiore (2001) với O(n²) nhưng bỏ qua ràng buộc phi tuyến nên nhạy nhiễu, còn các cách giữ ràng buộc khoảng cách giữa các điểm thì phải tuyến tính hoá các tích độ sâu, sinh ra O(n²) ẩn và độ phức tạp O(n⁵) (Quan–Lan, `quan1999linear`) hay O(n⁸) (Ansar–Daniilidis 2003, không có trong `refs.bib`) [§2, tr. 3]. Nhóm lặp (đại diện là LHM của `lu2000orthogonal`) chính xác nhưng chậm hơn và cần khởi tạo; LHM khởi tạo bằng giả thiết weak-perspective nên hỏng khi vật chiếu lên một vùng nhỏ lệch về một bên ảnh [§1, tr. 2].

[M] Nút thắt thật sự mà EPnP gỡ là: mọi cách "giải độ sâu" đều có số ẩn tăng theo n, và nếu muốn giữ ràng buộc khoảng cách thì số ẩn sau tuyến tính hoá tăng theo n². EPnP thay n ẩn độ sâu bằng **12 ẩn cố định**, nên ràng buộc khoảng cách chỉ còn 6 phương trình không phụ thuộc n.

## 2. Giả thiết — kể cả giả thiết ngầm; bỏ đi thì hỏng ở đâu

Giả thiết nói ra:

- Camera đã hiệu chuẩn, mô hình pinhole không méo, `K` đã biết đầy đủ (f_u, f_v, điểm chính) [eq. (4), tr. 5]. Bỏ đi thì eq. (5)–(6) không còn tuyến tính theo toạ độ điểm điều khiển; đây là chỗ các biến thể về sau (ví dụ `penate2013exhaustive`, tôi chưa đọc) phải thêm ẩn.
- n ≥ 4 [tr. 1]; điểm không đồng phẳng thì dùng 4 điểm điều khiển, đồng phẳng thì dùng 3 [§3, tr. 4; §3.4, tr. 7].
- Tương ứng đúng; ngoại lai do RANSAC bên ngoài xử lý [§5.2, tr. 11].

Giả thiết ngầm tôi tìm ra (tất cả là [M]):

- **Hàm mục tiêu của bước tuyến tính là sai số đại số, có trọng số độ sâu.** Mỗi hàng của M là `f_u·x_c − (u_i − u_c)·z_c` = `z_i · f_u · (x_c/z_c − ū_i)`, tức là sai số pixel nhân với độ sâu z_i của điểm (tôi suy ra từ eq. (5)–(6)). Vector riêng nhỏ nhất của MᵀM vì vậy cực tiểu tổng bình phương sai số pixel **có trọng số z_i²**: điểm xa được coi nặng hơn điểm gần, ngược với lượng thông tin nó mang. Bài nói eq. (5)–(6) "không cần chuẩn hoá toạ độ 2D như DLT" [§3.2, tr. 5] — đúng về điều kiện số, nhưng không nói gì về trọng số này. Dải độ sâu càng rộng thì ảnh hưởng càng lớn; với dải [4, 8] của bài thì trọng số chênh tối đa 4 lần.
- **Tỉ lệ của các điểm điều khiển.** Bài chỉ nói lấy trọng tâm và "một cơ sở dóng theo các hướng chính của dữ liệu" [§3.1, tr. 4–5], không nói độ dài mỗi trục. Tôi chọn độ dài = căn bậc hai trị riêng của ma trận hiệp phương sai (tức là trắng hoá dữ liệu); mã OpenCV cũng làm đúng như vậy (xem mục 7). Lựa chọn này quyết định α_ij có cỡ O(1) hay không, và — như mục 7 [8] cho thấy — nó là lý do cách 4 điểm điều khiển vẫn chạy tốt với dữ liệu gần phẳng.
- **Ngưỡng "phẳng".** §3.4 nói "khi ma trận mômen có một trị riêng rất nhỏ" [tr. 7] nhưng không cho ngưỡng. Với dữ liệu phẳng tuyệt đối, cách 4 điểm điều khiển suy biến hẳn (ma trận đổi sang toạ độ trọng tâm không khả nghịch); với dữ liệu gần phẳng thì — trái với dự đoán ban đầu của tôi — không có vấn đề gì (mục 7 [8]).
- **Số chiều nhân N ∈ {1..4} là đủ.** Với dữ liệu hoàn hảo từ ≥ 6 điểm và camera phối cảnh, nhân có đúng 1 chiều [§3.3, tr. 6]; tôi kiểm lại được: n = 4 cho 4 chiều, n = 5 cho 2 chiều, n ≥ 6 cho 1 chiều (mục 7 [1]). Nhưng khi camera tiến gần trực giao (tiêu cự dài, vật xa) thì 4 trị riêng nhỏ nhất cùng tiến về 0 [Fig. 3, tr. 5] — với n = 4 hay trường hợp trực giao, mọi thông tin độ sâu nằm trong 6 ràng buộc khoảng cách, và kết quả nhạy nhiễu (mục 7 [4], n = 5 "uncentered").
- **Bước Gauss–Newton không nhìn ảnh.** eq. (15) chỉ phạt sai lệch khoảng cách giữa các điểm điều khiển; ảnh chỉ đi vào qua việc chọn không gian con (4 vector riêng nhỏ nhất). Vì vậy EPnP+GN không phải ước lượng hợp lý cực đại theo sai số tái chiếu. Ở trường hợp phẳng, 3 ẩn β và 3 ràng buộc khiến GN ép khớp khoảng cách tuyệt đối và có thể kéo nghiệm ra xa ảnh (mục 7 [7]).

## 3. Cơ chế — năm câu, rồi chi tiết có định vị

(1) Viết mọi điểm 3D thành tổ hợp affine (toạ độ trọng tâm α_ij, tổng bằng 1) của 4 điểm điều khiển ảo; vì phép biến đổi rời thế giới→camera là affine nên **cùng các α_ij đó** biểu diễn điểm trong hệ camera [eq. (1)–(2)]. (2) Phương trình chiếu của mỗi điểm khi khử độ sâu cho 2 phương trình **tuyến tính** theo 12 toạ độ camera của 4 điểm điều khiển, nên toàn bộ dữ liệu gom thành Mx = 0 với M cỡ 2n × 12 [eq. (5)–(7)]. (3) Nghiệm nằm trong nhân của M, tính bằng vector riêng của MᵀM cỡ 12 × 12 — việc duy nhất tốn O(n) là lập MᵀM [eq. (8)]. (4) Hệ số tổ hợp β được chọn sao cho khoảng cách giữa các điểm điều khiển trong hệ camera bằng khoảng cách trong hệ thế giới (6 phương trình bậc hai), giải bằng tuyến tính hoá hoặc tái tuyến tính hoá tuỳ số chiều nhân N, và chọn N theo sai số tái chiếu [eq. (9)–(14)]. (5) Có toạ độ camera của các điểm thì R, t là bài toán căn chỉnh 3D–3D chuẩn; tuỳ chọn tinh chỉnh 4 hệ số β bằng Gauss–Newton với chi phí không phụ thuộc n [eq. (15)–(16)].

Chi tiết, theo thứ tự tôi dựng lại:

**Tham số hoá [§3.1, tr. 4–5].** eq. (1): p_i^w = Σ_j α_ij c_j^w, Σ_j α_ij = 1; eq. (2): cùng α cho p_i^c. [M] Lý do eq. (2) đúng: p^c = R p^w + t và Σα_ij = 1 nên R Σα c^w + t = Σα (R c^w + t). Tính α: với c_1 là trọng tâm, [c_2−c_1, c_3−c_1, c_4−c_1] là ma trận 3×3 khả nghịch khi dữ liệu không phẳng, giải ra 3 hệ số còn lại, hệ số đầu là 1 trừ tổng (tôi suy ra; bài chỉ nói α "được xác định duy nhất và dễ tính" [tr. 4]). Điểm điều khiển: trọng tâm + các trục chính, với lập luận rằng đây là một dạng chuẩn hoá điều kiện giống cách khuyến cáo cho DLT [tr. 5].

**Ma trận M [§3.2, tr. 5].** eq. (3): w_i [u_i; 1] = A Σ_j α_ij c_j^c; eq. (4) viết rõ A với f_u, f_v, (u_c, v_c). Hàng thứ ba cho w_i = Σ α_ij z_j^c, thế vào hai hàng đầu được eq. (5): Σ_j α_ij f_u x_j^c + α_ij (u_c − u_i) z_j^c = 0 và eq. (6) tương tự với v. Ghép 2n phương trình: eq. (7) Mx = 0, x = [c_1^cᵀ, …, c_4^cᵀ]ᵀ ∈ ℝ¹². eq. (8): x = Σ_{i=1..N} β_i v_i với v_i là vector kỳ dị phải ứng với N giá trị kỳ dị bằng 0, tính như vector riêng của MᵀM.

**Vì sao nhân có số chiều như vậy [§3.3, tr. 6].** [T] Với dữ liệu hoàn hảo, ≥ 6 điểm, camera phối cảnh: N = 1 (chỉ còn mơ hồ tỉ lệ). Camera trực giao: N = 4, vì dịch độ sâu của 4 điểm điều khiển không đổi ảnh [tr. 6]. [M] Với n = 4 và 5, M chỉ có 8 và 10 hàng nên nhân có ít nhất 4 và 2 chiều — bài nhắc điều này ở đầu trang 6 như ví dụ hệ thiếu ràng buộc. Cả ba điều này tôi đã kiểm bằng số (mục 7 [1], [6]).

**Chọn N và β [§3.3, tr. 6–7].** Thay vì đoán N từ phổ trị riêng, bài giải cả 4 trường hợp rồi giữ nghiệm có sai số tái chiếu nhỏ nhất, eq. (9). Ký hiệu v^[i] là 3 thành phần của v ứng với điểm điều khiển i.
- N = 1: x = βv, ràng buộc eq. (10) ‖βv^[i] − βv^[j]‖² = ‖c_i^w − c_j^w‖², nghiệm bình phương tối thiểu theo chuẩn (không bình phương) eq. (11): β = Σ‖v^[i]−v^[j]‖·‖c_i^w−c_j^w‖ / Σ‖v^[i]−v^[j]‖².
- N = 2: eq. (12), tuyến tính hoá (kỹ thuật mượn từ mật mã học, như Ansar–Daniilidis dùng): coi β11 = β1², β12 = β1β2, β22 = β2² là ẩn độc lập, được Lβ = ρ với L cỡ 6 × 3, eq. (13), giải bằng giả nghịch đảo; chọn dấu để mọi điểm có z > 0, rồi tinh lại tỉ lệ chung bằng eq. (11) [tr. 7].
- N = 3: như trên, L vuông 6 × 6, dùng nghịch đảo [tr. 7].
- N = 4: 10 tích β_ab mà chỉ 6 phương trình, nên dùng **tái tuyến tính hoá** (Kipnis–Shamir 1999, không có trong `refs.bib`): nghiệm β_ab nằm trong nhân của một hệ tuyến tính thuần nhất, rồi thêm các phương trình bậc hai mới từ tính giao hoán β_ab β_cd = β_a'b' β_c'd' với {a',b',c',d'} là hoán vị của {a,b,c,d}, eq. (14), và giải chúng lại bằng tuyến tính hoá [tr. 7]. [M] Đếm: nhân của [L | −ρ] (6 × 11) có 5 chiều, hệ mới có 15 đơn thức λ_kλ_l; cần hạng 14 — kiểm bằng số: đúng hạng 14 (mục 7 [2]).

**Trường hợp phẳng [§3.4, tr. 7].** 3 điểm điều khiển, M cỡ 2n × 9, số ràng buộc khoảng cách giảm từ 6 còn 3, và "cần tái tuyến tính hoá khi N ≥ 3". [M] Đếm tương tự: nhân của [L | −ρ] (3 × 7) có 4 chiều, 10 đơn thức, cần hạng 9 nhưng các quan hệ giao hoán chỉ cho hạng 6 — **một vòng tái tuyến tính hoá không đủ** cho N = 3 phẳng (mục 7 [2]). Bài không nói gì thêm.

**Từ điểm điều khiển ra pose.** p_i^c = Σα_ij c_j^c, rồi căn chỉnh 3D–3D (Horn 1988, Arun 1987, Umeyama 1991) [§3, tr. 4]. Bài không viết công thức bước này.

**Gauss–Newton [§4, tr. 7].** Tinh chỉnh β = [β1..β4] để cực tiểu eq. (15) Error(β) = Σ_{i<j} (‖c_i^c − c_j^c‖² − ‖c_i^w − c_j^w‖²) với c_i^c = Σ_j β_j v_j^[i], eq. (16). [M] Như in, eq. (15) thiếu bình phương ngoài ngoặc (tổng có dấu của hiệu không bị chặn dưới, không thể là hàm để cực tiểu); tôi cài bản có bình phương. [T] Dưới 10 vòng lặp, chi phí độc lập với n [tr. 7].

## 4. Ký hiệu của bài ↔ ký hiệu của khảo sát

| Bài (EPnP) | Ý nghĩa | Khảo sát (`code/common.py`) |
|---|---|---|
| p_i^w, "reference points" | điểm 3D trong hệ thế giới | `X_w` (hàng i) |
| p_i^c | cùng điểm trong hệ camera | `X_c = R X_w + t` |
| c_j^w, c_j^c (j = 1..4, phẳng 1..3) | điểm điều khiển ảo | không có ký hiệu chung — giữ `c_j` |
| α_ij | toạ độ trọng tâm thuần nhất | giữ `α_ij` |
| A (f_u, f_v, u_c, v_c) | ma trận nội tham số | `K` |
| u_i = [u_i, v_i]ᵀ | toạ độ pixel | `u` (hàng i) — bài làm việc trực tiếp trên pixel, không dùng tia chiếu `f` |
| w_i | tham số chiếu (= độ sâu z của p_i^c) | thành phần z của `X_c` |
| [R \| t] trong eq. (9) | pose thế giới → camera | `R, t` — cùng quy ước (tôi suy ra từ eq. (9): A[R\|t][p^w; 1]) |
| M (2n × 12 / 2n × 9), x ∈ ℝ¹² | hệ tuyến tính, vector toạ độ camera của điểm điều khiển | giữ |
| v_i, β_i, N | vector riêng nhân, hệ số, số chiều nhân hiệu dụng | giữ; **lưu ý**: chỉ số i ở v_i, β_i *không* phải chỉ số điểm |
| β_ab, L, ρ | tích tuyến tính hoá, ma trận 6 × (3, 6, 10), khoảng cách bình phương | giữ |
| E_rot (%), E_trans (%) | ‖q_true − q‖/‖q‖, ‖t_true − t‖/‖t‖ [§5.1, tr. 9] | khảo sát dùng `rot_err_deg`, `trans_err_rel`; script của tôi tính cả thước đo % của bài |

## 5. Bằng chứng — dữ liệu, phần cứng, baseline, con số kèm điều kiện, số lần lặp

**Thiết lập tổng hợp [§5.1, tr. 8–9]**, đúng như bài ghi: ảnh 640 × 480, f_u = f_v = 800, điểm chính (320, 240). Dữ liệu "centered": điểm phân bố đều trong hộp x, y, z ∈ [−2, 2] × [−2, 2] × [4, 8]; "uncentered": [1, 2] × [1, 2] × [4, 8]. Nhiễu Gauss trên toạ độ 2D; ngoại lai = toạ độ 2D lấy ngẫu nhiên trên toàn ảnh. Mỗi đồ thị là 300 mô phỏng MATLAB độc lập; thời gian là trung bình 100 lần chạy mỗi ví dụ. Phần cứng: "một PC chuẩn" [Fig. 2, tr. 3], không nêu cấu hình. Pose thật và hệ thế giới được sinh thế nào: **bài không nói** (hộp điểm cho trong hệ camera). [M] Ở z = 4, x = ±2 chiếu ra u = 320 ± 400, tức là nằm ngoài ảnh 640 px — bài không nói có loại các điểm này hay không.

Baseline: AD (Ansar–Daniilidis 2003), Clamped DLT, LHM (`lu2000orthogonal`, khởi tạo weak-perspective), EPnP+LHM, EPnP+GN; phẳng thêm SP+LHM (`schweighofer2006planar` + LHM) [§5.1.1–5.1.2, tr. 9–10].

| Hình | Điều kiện | Điều bài báo cáo |
|---|---|---|
| Fig. 1 [tr. 2] | centered, n = 6, σ = 0..15 px, 300 lần, boxplot E_rot | [Đ] EPnP có hộp tứ phân vị thấp hơn AD và Clamped DLT; EPnP+GN, LHM, EPnP+LHM thấp hơn nữa |
| Fig. 5a [tr. 8] | như trên, mean/median E_rot, E_trans | [Đ] đọc bằng mắt ở σ = 5: EPnP median E_rot ≈ 4 %, mean ≈ 6 %; EPnP+GN, LHM ≈ 2 % |
| Fig. 5b | uncentered, n = 6 | [Đ] LHM có median nhảy vọt (> 100 % ở σ ≈ 9) — không hội tụ; EPnP+GN ổn định hơn |
| Fig. 5c | centered, n = 5..20, σ = 5 | [Đ] EPnP gần LHM, tốt hơn AD, Clamped DLT |
| Fig. 5d–e | uncentered, n = 5..50, σ = 5, ngoại lai 0 % và 25 % | [Đ] EPnP+GN ≈ EPnP+LHM, LHM một mình kém ổn định; AD bị bỏ vì không chuẩn hoá toạ độ 2D [tr. 9] |
| Fig. 4 [tr. 6] | trái: σ = 10, n = 5..20; phải: n = 6, σ = 0..15; 300 lần | [Đ] phân bố N được chọn; ở n = 6, σ = 0 gần như toàn N = 1; nhiễu tăng thì N = 2, 3 tăng |
| Fig. 3 [tr. 5] | 100 lần mỗi f, f = 100..10000 | [Đ] f càng lớn, 4 trị riêng nhỏ nhất của MᵀM càng tiến về 0 (cách đổi cảnh theo f không nêu) |
| Fig. 2 [tr. 3] | MATLAB, n tới 150 | [Đ] thời gian EPnP gần phẳng theo n và thấp nhất; EPnP+GN chồng lên EPnP |
| Fig. 6 [tr. 9] | median sai số vs thời gian | [Đ] EPnP+GN cần khoảng 1/20 thời gian của LHM để đạt cùng độ chính xác |
| văn bản [tr. 10] | n = 6 | [Đ] EPnP nhanh hơn LHM khoảng 10 lần, nhanh hơn AD khoảng 200 lần (MATLAB, LHM "chưa tối ưu") |
| Fig. 7 [tr. 10] | phẳng, nghiêng 0° và 30°, σ = 0..15; **n = 6 theo chú thích hình nhưng n = 10 theo văn bản** | [Đ] nghiêng 0°: mọi phương pháp như nhau, không ngoại lai; nghiêng 30°: EPnP ≈ 20–25 % nghiệm "ngoại lai", LHM < 10 %, SP+LHM ≈ 0 %, AD tới gần 100 %; sai số chỉ lấy trung bình trên nghiệm *không* bị lưỡng nghĩa |
| văn bản [tr. 11] | phẳng, n = 10, nghiêng 30° | [Đ] EPnP nhanh hơn AD ~200 lần, LHM ~30 lần |
| Fig. 8 [tr. 11] | hai video thật, ~200 tương ứng/ảnh, RANSAC trên tập con 7 điểm rồi tinh chỉnh lặp với mọi inlier | chỉ minh hoạ định tính, **không có con số nào** |

Không có bộ dữ liệu thật có ground truth; không có sai số tái chiếu; không có thống kê lặp lại ngoài 300 lần mô phỏng.

## 6. Đóng góp thật sự (thường nhỏ hơn abstract)

[M] Đóng góp bền là **một phép đổi biến**: thay n ẩn độ sâu bằng 12 toạ độ của 4 điểm điều khiển, nhờ tính bất biến của toạ độ trọng tâm dưới phép biến đổi affine. Nhờ đó ràng buộc khoảng cách chỉ còn 6 phương trình cố định và toàn bộ phụ thuộc vào n dồn vào một phép nhân MᵀM. Ý này tổng quát hơn PnP — chính tác giả nói nó áp dụng được cho khôi phục bề mặt biến dạng [§6, tr. 11], và cùng phòng thí nghiệm dùng lại công thức nhân của M cho loại ngoại lai và bất định (`ferraz2014reppnp`, `ferraz2014cepnp`, theo ghi chú `refs.bib`, tôi chưa đọc).

Những gì nhỏ hơn abstract: (i) "chính xác" nghĩa là chính xác hơn các bộ giải không lặp *năm 2008* (AD, Clamped DLT), không phải tối ưu theo bất kỳ hàm mục tiêu thống kê nào; (ii) bước GN không cực tiểu sai số tái chiếu, và trong đo của tôi vẫn kém LM trên sai số tái chiếu 10–25 % (median E_rot, mục 7 [3]–[4]); (iii) trường hợp phẳng chỉ được mô tả trong một đoạn văn và không đủ để cài lại cho N = 3 (mục 7 [2]); (iv) cơ chế chọn N theo sai số tái chiếu là heuristic.

## 7. Kiểm chứng của người ghi chú — script trong `code/`, lệnh chạy, kết quả thật

Script: `code/lepetit2009epnp_check.py`. Cài EPnP từ mô tả trong bài (điểm điều khiển PCA, M theo eq. (5)–(6), N = 1..4 theo eq. (10)–(14), chọn N theo eq. (9), trường hợp phẳng 3 điểm điều khiển, GN theo eq. (15) có bình phương). Tôi không chép mã OpenCV; sau khi cài xong tôi mới đọc `modules/calib3d/src/epnp.cpp` nhánh 4.x trên GitHub (tải ngày 2026-09-25) để hiểu vì sao `cv2` cho kết quả khác. Các lựa chọn của tôi mà bài không quy định: độ dài trục điểm điều khiển = √(trị riêng hiệp phương sai); ở N = 2, 3 lấy β_1 = √|β_11|, β_k = sign(β_1k)√|β_kk|; ở N = 4 lấy β từ xấp xỉ hạng 1 của ma trận β_ab; khi các N hoà nhau (không nhiễu) chọn N nhỏ nhất; GN chạy từ nghiệm của từng N rồi mới chọn theo eq. (9); hệ thế giới = xoay ngẫu nhiên quanh tâm hộp, t = tâm hộp; cảnh phẳng = hình vuông [−2, 2]² ở độ sâu 6, nghiêng quanh trục x camera.

Lệnh (từ gốc repo; ~60 s trên CPU của container; numpy 2.4.6, OpenCV 5.0.0):

```
python3 VSLAM/pnp/code/lepetit2009epnp_check.py
```

Kết quả thật (cắt bớt dòng trùng lặp, không sửa số):

```
[1] Không nhiễu: khôi phục chính xác, n = 4..50 (20 cảnh / n)
  khong-phang  EPnP của tôi: max(||R-R*||_F, ||t-t*||/||t*||) = 2.4e-11  -> PASS;  N được chọn: {1: 160, 2: 20, 4: 20}
      số chiều nhân của M^T M (trị riêng < 1e-12 max) theo n: 4:[4], 5:[2], 6:[1], 7:[1], 8:[1], 10:[1], 15:[1], 20:[1], 30:[1], 50:[1]
  khong-phang  cv2 SOLVEPNP_EPNP: max ||R-R*||_F = 7.7e-01; số cảnh sai (>1e-6) theo n: {4: 13, 5: 0, 6: 0, 7: 0, 8: 0, 10: 0, 15: 0, 20: 0, 30: 0, 50: 0}
  phang        EPnP của tôi: max(||R-R*||_F, ||t-t*||/||t*||) = 1.3e-10  -> PASS;  N được chọn: {1: 200}
      số chiều nhân của M^T M (trị riêng < 1e-12 max) theo n: 4:[1], 5:[1], 6:[1], 7:[1], 8:[1], 10:[1], 15:[1], 20:[1], 30:[1], 50:[1]
  phang        cv2 SOLVEPNP_EPNP: max ||R-R*||_F = 2.0e+00; số cảnh sai (>1e-6) theo n: {4: 20, 5: 17, 6: 7, 7: 3, 8: 5, 10: 0, 15: 3, 20: 0, 30: 5, 50: 4}

[2] Đếm ẩn/phương trình của tái tuyến tính hoá (eq. 14)
  không phẳng N=4: 6 ràng buộc, 10 ẩn beta_ab -> nhân dim 5; hệ tái tuyến tính hoá có hạng 14 trên 15 đơn thức (cần hạng 14 để nghiệm duy nhất) -> ĐỦ
  phẳng N=3: 3 ràng buộc, 6 ẩn beta_ab -> nhân dim 4; hệ tái tuyến tính hoá có hạng 6 trên 10 đơn thức (cần hạng 9 để nghiệm duy nhất) -> THIẾU

[3] Sai số theo nhiễu, n = 6, dữ liệu 'centered' của bài, 300 lần/mức (E_rot, E_trans theo % của bài; median | mean)
  sigma |              EPnP(tôi) |           EPnP+GN(tôi) |               cv2 EPNP |          +LM tái chiếu
      0 | R  0.0|  0.0 t  0.0|  0.0 | R  0.0|  0.0 t  0.0|  0.0 | R  0.0|  0.0 t  0.0|  0.0 | R  0.0|  0.0 t  0.0|  0.0
      1 | R  0.5|  0.7 t  0.5|  0.8 | R  0.3|  0.3 t  0.2|  0.3 | R  0.3|  0.3 t  0.2|  0.3 | R  0.2|  0.3 t  0.2|  0.2
      5 | R  2.5|  3.7 t  2.0|  3.5 | R  1.3|  1.6 t  1.0|  1.3 | R  1.3|  1.6 t  1.1|  1.4 | R  1.2|  1.4 t  0.8|  1.1
     10 | R  4.1|  5.5 t  3.6|  5.2 | R  2.6|  3.1 t  1.9|  2.5 | R  2.5|  3.1 t  2.0|  2.6 | R  2.3|  2.6 t  1.5|  2.0
     15 | R  6.6|  9.2 t  4.9|  7.8 | R  3.8|  4.6 t  3.2|  3.9 | R  3.9|  4.9 t  2.7|  4.0 | R  3.4|  3.8 t  2.6|  3.1

[4] Sai số theo số điểm, sigma = 5 px, 'centered' (Fig. 5c) và 'uncentered' (Fig. 5d), 300 lần; median E_rot % [mean]
  centered:
    n=  5: me= 2.84 [  4.6]  gn= 1.47 [  1.8]  cv= 1.46 [  2.7]  lm= 1.31 [  1.6]
    n= 10: me= 1.36 [  1.6]  gn= 0.86 [  1.0]  cv= 0.91 [  1.0]  lm= 0.77 [  0.9]
    n= 20: me= 0.82 [  0.9]  gn= 0.59 [  0.6]  cv= 0.60 [  0.7]  lm= 0.51 [  0.6]
    n= 50: me= 0.52 [  0.5]  gn= 0.38 [  0.4]  cv= 0.37 [  0.4]  lm= 0.31 [  0.3]
  uncentered:
    n=  5: me= 8.13 [ 20.3]  gn= 2.59 [  4.6]  cv= 2.77 [  7.9]  lm= 2.46 [  4.4]
    n= 10: me= 3.88 [  4.9]  gn= 1.54 [  1.7]  cv= 1.52 [  1.7]  lm= 1.40 [  1.6]
    n= 20: me= 2.30 [  2.7]  gn= 1.09 [  1.2]  cv= 1.08 [  1.2]  lm= 0.98 [  1.1]
    n= 50: me= 1.51 [  1.7]  gn= 0.66 [  0.7]  cv= 0.68 [  0.7]  lm= 0.60 [  0.6]

[5] Phân bố N được chọn theo eq. (9) (so với Fig. 4), 300 lần
  n= 6 sigma= 0: tỉ lệ N=1..4 -> 1.00 0.00 0.00 0.00
  n= 6 sigma= 5: tỉ lệ N=1..4 -> 0.21 0.26 0.15 0.38
  n= 6 sigma=15: tỉ lệ N=1..4 -> 0.14 0.35 0.25 0.25
  n= 5 sigma=10: tỉ lệ N=1..4 -> 0.00 0.29 0.38 0.33
  n=10 sigma=10: tỉ lệ N=1..4 -> 0.49 0.16 0.06 0.29
  n=20 sigma=10: tỉ lệ N=1..4 -> 0.61 0.10 0.02 0.26

[6] Trị riêng nhỏ nhất của M^T M khi camera tiến tới trực giao (Fig. 3), không nhiễu, n = 20
  f=     800 (độ sâu x  1.0): 5 trị riêng nhỏ nhất / lớn nhất = -2.2e-18 7.6e-03 1.2e-02 2.7e-02 4.9e-02
  f=   10000 (độ sâu x 12.5): 5 trị riêng nhỏ nhất / lớn nhất = 4.3e-18 5.4e-05 8.3e-05 2.9e-04 4.4e-02
  f=  100000 (độ sâu x125.0): 5 trị riêng nhỏ nhất / lớn nhất = -8.6e-18 5.4e-07 7.8e-07 2.9e-06 4.4e-02

[7] Phẳng, n = 10, 300 lần: median E_rot % và tỉ lệ 'hỏng' (E_rot > 20%, ngưỡng của tôi)
  tilt=   0 sigma= 1: me: med  0.68 hỏng   0%  gn: med  1.63 hỏng   0%  cv: med  0.82 hỏng   3%
  tilt=   0 sigma=10: me: med  6.48 hỏng   3%  gn: med 14.30 hỏng  24%  cv: med  8.58 hỏng  18%
  tilt=  30 sigma= 1: me: med  0.65 hỏng   0%  gn: med  0.40 hỏng   0%  cv: med 22.98 hỏng  51%
  tilt=  30 sigma=10: me: med  6.13 hỏng   2%  gn: med  4.24 hỏng   1%  cv: med 31.30 hỏng  57%

[8] Gần phẳng: bề dày +-eps quanh mặt phẳng [-2,2]^2, tilt 30, n = 20, 200 lần; median E_rot %
  sigma=0 eps= 5e-01: 4 đ.đ.khiển= 2.5e-13  3 đ.đ.khiển= 1.7e+00  cv2= 2.4e-13
  sigma=0 eps= 1e-05: 4 đ.đ.khiển= 3.0e-13  3 đ.đ.khiển= 3.3e-05  cv2= 2.1e-13
  sigma=1 eps= 5e-01: 4 đ.đ.khiển= 2.5e-01  3 đ.đ.khiển= 2.0e+00  cv2= 2.7e-01
  sigma=1 eps= 1e-03: 4 đ.đ.khiển= 3.0e-01  3 đ.đ.khiển= 3.0e-01  cv2= 4.8e-01
  sigma=1 eps= 1e-05: 4 đ.đ.khiển= 2.8e-01  3 đ.đ.khiển= 2.7e-01  cv2= 5.2e+01

[9] Thời gian (CPU của container, numpy/Python; median 25 lần) — kiểm O(n)
  n     :       10       30      100      300     1000     3000     5000
  EPnP(tôi)    :    1.70ms    1.65ms    1.69ms    1.89ms    2.12ms    3.27ms    3.98ms   độ dốc log-log (n>=300) = 0.27
                 chi phí biên/điểm: 1000->3000: 0.572 us, 3000->5000: 0.356 us
  EPnP+GN(tôi) :    2.83ms    2.88ms    4.11ms    3.02ms    3.21ms    4.36ms    5.29ms   độ dốc log-log (n>=300) = 0.20
  cv2 EPNP     :    0.11ms    0.05ms    0.14ms    0.10ms    0.22ms    0.62ms    1.03ms   độ dốc log-log (n>=300) = 0.83
                 chi phí biên/điểm: 1000->3000: 0.199 us, 3000->5000: 0.206 us
  chênh lệch GN - không GN theo n: 1.13 1.22 2.42 1.13 1.08 1.09 1.31 ms

Tổng thời gian: 59 s
```

Đọc kết quả:

- **[1] Công thức lõi đúng.** Cài từ mô tả của bài, EPnP khôi phục pose tới sai số 10⁻¹⁰–10⁻¹¹ với n = 4..50 cả không phẳng lẫn phẳng; số chiều nhân khớp đúng lập luận ở §3.3 (n = 4 → 4, n = 5 → 2, n ≥ 6 → 1; phẳng 2n × 9 → 1 với mọi n ≥ 4). Ca n = 4 chỉ đúng được nhờ tái tuyến tính hoá (N = 4 được chọn 20 lần = đúng 20 cảnh n = 4). **PASS.**
- **[1] `cv2.SOLVEPNP_EPNP` không phải thuật toán trong bài.** Trên dữ liệu *không nhiễu* nó sai ở 13/20 cảnh n = 4 không phẳng và ở nhiều cảnh phẳng với mọi n (kể cả n = 30, 50). Kiểm riêng (không nằm trong script): các cảnh phẳng hỏng cho sai số quay đúng 60° = 2 × độ nghiêng 30° với RMSE tái chiếu ~45 px, tức là nghiệm "lật" không phải nghiệm thật. Đọc `epnp.cpp` (nhánh 4.x; tôi chưa kiểm được mã của bản 5.0.0 đã cài có giống không) thì thấy: không có tái tuyến tính hoá, N = 1/2/3 được thay bằng ba xấp xỉ dùng tập con cột của L cỡ 6 × 10, luôn chạy 5 vòng Gauss–Newton trên 4 β, và **không có nhánh phẳng 3 điểm điều khiển** — điểm điều khiển thứ tư có độ dài √(trị riêng) ≈ 0 và ma trận 3 × 3 được nghịch đảo giả bằng SVD. Như vậy "EPnP" trong OpenCV thực chất là "EPnP+GN, bản xấp xỉ".
- **[2] §3.4 không đủ để cài.** Với N = 4 không phẳng, hệ tái tuyến tính hoá có đúng hạng cần thiết; với N = 3 phẳng thì thiếu 3 hạng — một vòng tái tuyến tính hoá không xác định được nghiệm. Trong script tôi vẫn sinh ứng viên N = 3 phẳng (vector kỳ dị nhỏ nhất, tuỳ ý) và để eq. (9) loại nó; trong [7] không lần nào nó được chọn khi không GN. **Mâu thuẫn với tuyên bố của bài** (hoặc bài dùng thêm quan hệ mà không nói).
- **[3]–[4] so với Fig. 5 — khớp định tính, lệch định lượng.** Thứ tự EPnP > EPnP+GN ≈ cv2 > LM tái chiếu và dáng đường cong theo σ và theo n đúng như Fig. 5a, 5c, 5d; uncentered tệ hơn centered, và ở uncentered n = 5 EPnP thuần có mean gấp ~2,5 lần median (đuôi nặng, như bài nói "mean − median lớn = kém ổn định" [tr. 9]). Nhưng EPnP (không GN) của tôi ở n = 6, σ = 5 có median E_rot 2,5 % / mean 3,7 %, trong khi đọc bằng mắt Fig. 5a được ~4 % / ~6 % — thấp hơn chừng 1,5 lần. Các phương pháp lặp thì gần hơn (LM của tôi ở n = 10, 20 centered: mean 0,9 % và 0,6 %; LHM trong Fig. 5c đọc được ~1 % và ~0,7 %). Tôi không xác định được nguyên nhân: pose thật / hệ thế giới không được nêu, và cách chọn dấu/β của tôi có thể khác. **Điều kiện của tôi khớp bài ở:** ảnh 640 × 480, f = 800, điểm chính (320, 240), hai hộp điểm, nhiễu Gauss, 300 lần, thước đo E_rot/E_trans %. **Không khớp / không kiểm được:** pose thật, việc có loại điểm ngoài ảnh không (tôi không loại), không có LHM/AD/Clamped DLT (tôi thay LHM bằng LM trên sai số tái chiếu của OpenCV — hai thứ cực tiểu hai hàm khác nhau), không chạy thí nghiệm ngoại lai 25 % (Fig. 5e) và không kiểm Fig. 6.
- **[3]–[4] Tuyên bố "EPnP+GN chính xác như LHM".** Trong đo của tôi EPnP+GN kém LM tái chiếu 10–25 % ở median E_rot (ví dụ n = 20 centered: 0,59 vs 0,51); ở n = 6 thì gần như bằng. Không mâu thuẫn trực tiếp với bài (LHM ≠ LM tái chiếu), nhưng cho thấy GN trên β không đạt tối ưu theo pixel.
- **[5] so với Fig. 4.** σ = 0 cho 100 % N = 1 (với quy tắc hoà của tôi), khớp. Có nhiễu thì tôi chọn N = 4 nhiều hơn hẳn (n = 6, σ = 5: 38 % so với đọc bằng mắt ~5 % trong Fig. 4 phải; n = 20, σ = 10: 26 % so với ~0–2 %). Tôi đoán cách tái tuyến tính hoá của tôi (xấp xỉ bình phương tối thiểu trên 256 phương trình rồi hạng 1) khớp dữ liệu tốt hơn bản của bài, và đó có thể là một phần lý do EPnP thuần của tôi chính xác hơn Fig. 5a — **chưa kiểm**.
- **[6] Fig. 3 định tính đúng**: khi tiêu cự và độ sâu cùng tăng (ảnh giữ nguyên cỡ), trị riêng thứ 2–4 giảm theo ~1/f² còn trị riêng thứ 5 đứng yên — tiến tới nhân 4 chiều của camera trực giao.
- **[7] Phẳng.** EPnP của tôi (3 điểm điều khiển) không có nghiệm hỏng ở nghiêng 30°, σ ≤ 5, và 2 % ở σ = 10 — tốt hơn con số ~20–25 % "ngoại lai" của EPnP trong Fig. 7 (nhưng ngưỡng "ngoại lai" của bài là sai số vị trí 3D trung bình vượt một ngưỡng không nêu giá trị, còn của tôi là E_rot > 20 %; không so sánh trực tiếp được). **GN làm hỏng trường hợp mặt phẳng song song ảnh**: nghiêng 0°, median E_rot tăng từ 0,68 lên 1,63 % (σ = 1) và từ 6,5 lên 14,3 % (σ = 10), tỉ lệ hỏng 3 % → 24 %. Kiểm riêng ở σ = 5 (không nằm trong script) cho thấy GN làm tăng *sai số tái chiếu* so với nghiệm đóng — đúng như dự đoán vì eq. (15) không nhìn ảnh và 3 ràng buộc = 3 ẩn. Bài bỏ EPnP+GN khỏi thí nghiệm phẳng với lý do khác ("GN không giúp gỡ lưỡng nghĩa") [tr. 10]. `cv2` hỏng 45–57 % ở nghiêng 30°, nhất quán với [1].
- **[8] Gần phẳng — giả thiết của tôi sai.** Tôi dự đoán cách 4 điểm điều khiển sẽ mất ổn định khi dữ liệu gần phẳng; thực tế nó chính xác tới 10⁻¹³ không nhiễu và bằng cách 3 điểm khi có nhiễu, kể cả ε = 10⁻⁵. Lý do (tôi suy ra): trục thứ ba được co theo √λ nên α vẫn cỡ O(1). Ngược lại, dùng cách 3 điểm cho dữ liệu *không* thật phẳng gây sai số mô hình tỉ lệ với ε (1,7 % ở ε = 0,5 không nhiễu). Ngưỡng phẳng vì vậy nên rất chặt. `cv2` thì hỏng ở ε = 10⁻⁵ có nhiễu (median 52 %), khớp với giả thuyết nghịch đảo giả cắt mất trục thứ ba.
- **[9] O(n): khớp.** Chi phí biên mỗi điểm gần như không đổi khi n từ 1000 lên 5000 (bản của tôi ~0,36–0,57 µs/điểm, `cv2` ~0,20 µs/điểm); O(n²) sẽ cho chi phí biên tăng gấp ~2 giữa hai khoảng. Độ dốc log-log < 1 vì chi phí cố định (Python/numpy ~1,7 ms, `cv2` ~0,05–0,1 ms) chiếm phần lớn ở n nhỏ. GN thêm ~1,1–1,3 ms không phụ thuộc n (giá trị 2,42 ở n = 100 là nhiễu đo). Tôi không kiểm được con số "khoảng 15" điểm mà từ đó MᵀM chiếm ưu thế [tr. 5] — nó gắn với cài đặt MATLAB của họ.

## 8. Chỗ tôi không tin

- **eq. (15) in sai** [tr. 7]: thiếu bình phương ngoài ngoặc. Như in, Error(β) → −∞ khi β → 0, không thể là hàm GN cực tiểu. Chắc chắn là lỗi in, nhưng người cài theo bài sẽ vấp.
- **Fig. 7 mâu thuẫn với văn bản**: chú thích ghi n = 6, văn bản §5.1.2 ghi n = 10 [tr. 10]. Không biết đồ thị là cái nào.
- **Thí nghiệm phẳng thiếu điều kiện và có thiên lệch chọn mẫu**: không có kích thước mặt phẳng, độ sâu, ngưỡng "ngoại lai"; sai số chỉ lấy trung bình trên các nghiệm *không* bị lưỡng nghĩa [Fig. 7, tr. 10], nên đồ thị sai số không phản ánh độ tin cậy thật. Tôi không tái lập được con số ~20–25 % ngoại lai của EPnP ở nghiêng 30° (tôi được 0–2 % với ngưỡng của mình).
- **Mô tả §3.4 không đủ**: với N = 3 phẳng, đếm bậc tự do cho thấy một vòng tái tuyến tính hoá thiếu 3 phương trình (mục 7 [2]). Bài khẳng định dùng được mà không cho chi tiết.
- **"Uncentered" trộn hai yếu tố**: hộp [1, 2] × [1, 2] × [4, 8] vừa lệch trục vừa nhỏ hơn 16 lần theo diện tích mặt cắt so với hộp centered [tr. 9]. Kết luận "EPnP ổn định hơn LHM với dữ liệu lệch" không tách được hai nguyên nhân.
- **"EPnP+GN chính xác như LHM" / "gần như tối ưu"**: không phương pháp nào trong so sánh là ước lượng ML theo pixel; trong đo của tôi EPnP+GN còn kém LM tái chiếu 10–25 % ở n lớn. Tôi tin EPnP+GN ≈ LHM (không kiểm được LHM), không tin nó ≈ tối ưu.
- **Trọng số độ sâu ẩn trong MᵀM** (mục 2) không được nhắc; với cảnh có dải độ sâu lớn (SLAM ngoài trời), EPnP thuần có thể lệch nhiều hơn thí nghiệm [4, 8] m gợi ý. (Tôi suy ra, chưa đo.)
- **Thước đo lỗi**: E_trans chia cho ‖t‖ *ước lượng* chứ không phải ‖t_true‖ [tr. 9]; E_rot dùng quaternion mà không nói cách xử lý q ≡ −q. Nhỏ, nhưng là dấu hiệu cẩu thả.
- **Con số tốc độ** (10×, 200×, 30×, 1/20) [tr. 9–11] là so MATLAB với MATLAB, LHM "chưa tối ưu", phần cứng không nêu — chỉ nên đọc như thứ bậc, không như tỉ lệ.
- **Mã "tham chiếu" khác bài**: `cv2.SOLVEPNP_EPNP` (và theo tôi hiểu, mã EPFL gốc mà nó chép — chưa kiểm trực tiếp) không có tái tuyến tính hoá và nhánh phẳng. Mọi benchmark về sau gọi "EPnP" qua OpenCV đang đo một thuật toán khác thuật toán trong bài; trong đo của tôi nó hỏng ở n = 4 và ở dữ liệu phẳng *không nhiễu*.

## 9. Chỗ tôi chưa hiểu (→ `99-chua-biet.md`)

- Bài làm tái tuyến tính hoá ở N = 4 cụ thể thế nào: "hệ tuyến tính thuần nhất đầu tiên" [tr. 7] là [L | −ρ] hay cái gì khác; dùng bao nhiêu trong số các quan hệ β_ab β_cd = β_a'b' β_c'd'; lấy λ từ ma trận hạng 1 bằng cách nào. Cách của tôi là một cách đọc khả dĩ, không chắc trùng.
- Ca N = 3 phẳng giải ra sao nếu một vòng tái tuyến tính hoá không đủ hạng.
- Chọn dấu β ở N = 2, 3: nếu có nhiều (hoặc không có) tổ hợp dấu cho mọi z > 0 thì làm gì?
- GN chạy từ nghiệm của mọi N rồi chọn theo eq. (9), hay chỉ từ nghiệm đã chọn? Bài không nói; OpenCV làm cách thứ nhất.
- Vì sao EPnP thuần của tôi chính xác hơn Fig. 5a khoảng 1,5 lần và chọn N = 4 nhiều hơn Fig. 4 nhiều lần — do cách tái tuyến tính hoá, do pose thật, hay do tôi đọc hình sai?
- Fig. 3: khi đổi f từ 100 lên 10000 thì cảnh được đổi thế nào để ảnh không vỡ ra ngoài khung? Bài không nói.
- `cv2` hỏng ở dữ liệu phẳng tuyệt đối có phải do ngưỡng của `cv::invert(..., DECOMP_SVD)` cắt trục có độ dài ≈ 0 không, và OpenCV có ghi nhận lỗi này không?

## 10. Quan hệ với các bài khác trong `refs.bib`

- `lu2000orthogonal` (LHM) là baseline lặp chính và là "chuẩn độ chính xác" của bài [§2, tr. 4]; EPnP được đề xuất vừa như thay thế nhanh vừa như bộ khởi tạo cho nó (EPnP+LHM) [tr. 2]. Hai bài cực tiểu hai thứ khác nhau: LHM cực tiểu sai số không gian vật, EPnP cực tiểu sai số đại số có trọng số độ sâu rồi khớp khoảng cách (tôi suy ra).
- `quan1999linear` (O(n⁵)) và Ansar–Daniilidis 2003 (O(n⁸), không có trong `refs.bib`) là hai đối thủ không lặp giữ ràng buộc khoảng cách [§2, tr. 3]. Bài còn nhận xét Quan–Lan có thể hạ xuống O(n³) bằng cùng mẹo nhân MᵀM [tr. 3] — tuyên bố [T], không kiểm.
- `schweighofer2006planar` (SP+LHM) là tham chiếu cho trường hợp phẳng và lưỡng nghĩa [§5.1.2, tr. 10]; EPnP không gỡ lưỡng nghĩa mà chỉ tạo ít nghiệm sai hơn AD. Phần lưỡng nghĩa target phẳng nối sang `collins2014ippe` và cây `marker/`.
- `gao2003p3p`, `fischler1981ransac`, `oberkampf1996coplanar`, `dementhon1995posit` được trích như bối cảnh [§1–2]. Bài trích Haralick et al. **1991** (CVPR), không phải `haralick1994review`.
- Hậu duệ trong cùng phòng thí nghiệm (theo ghi chú `refs.bib`, tôi chưa đọc): `ferraz2014reppnp` (loại ngoại lai ngay trong nhân của M), `ferraz2014cepnp` (đưa bất định vào), `penate2013exhaustive` (thêm tiêu cự; là thứ `SOLVEPNP_UPNP` của OpenCV trỏ tới), `morenonoguer2008priors`.
- Các bộ giải O(n) về sau so với EPnP như baseline: `li2012rpnp`, `hesch2011dls`, `zheng2013opnp`, `kneip2014upnp`, `terzakis2020sqpnp`, `urban2016mlpnp`, `zeng2023cpnp` (ước lượng nhất quán — theo ghi chú `refs.bib`). Tôi chưa đọc bài nào trong số này nên chưa ghi họ mâu thuẫn EPnP ở khẳng định nào.
- `opencvsolvepnp`: cờ `SOLVEPNP_EPNP` là cài đặt khác bài — xem mục 7 [1].

## 11. Nó đổi gì trong suy nghĩ

Trước khi đọc tôi coi EPnP là "bộ giải O(n) chính xác". Sau khi dựng lại, tôi coi nó là **một cách tham số hoá** tốt (12 ẩn cố định, nhân của MᵀM) cộng với một bước chọn β khá heuristic, và độ chính xác của nó phụ thuộc đáng kể vào những chi tiết bài không quy định (tỉ lệ điểm điều khiển, cách lấy β, cách tái tuyến tính hoá). Hai hệ quả thực tế: (1) trong pipeline RANSAC + LM, EPnP chỉ nên là bộ khởi tạo — trên dữ liệu của bài, nó (kể cả +GN) luôn kém LM tái chiếu; (2) không được coi `cv2.SOLVEPNP_EPNP` là "EPnP của bài báo", nhất là với n = 4 hoặc target phẳng — cờ đó hỏng ngay trên dữ liệu không nhiễu trong đo của tôi.

## 12. Câu hỏi tự kiểm

1. Vì sao cùng các hệ số α_ij dùng được cả trong hệ thế giới và hệ camera, và điều đó hỏng nếu bỏ ràng buộc Σ_j α_ij = 1?
2. Vì sao nhân của M có 4 chiều khi n = 4, 2 chiều khi n = 5, 1 chiều khi n ≥ 6 — và vì sao nó lại tiến về 4 chiều khi camera gần trực giao dù n lớn?
3. Khi nào tuyến tính hoá (coi β_aβ_b là ẩn độc lập) không còn đủ phương trình, và vì sao tái tuyến tính hoá cứu được ca N = 4 không phẳng nhưng một vòng thì không cứu được ca N = 3 phẳng?
4. Vì sao Gauss–Newton trên β có thể làm *tăng* sai số tái chiếu, và điều đó dễ xảy ra ở trường hợp phẳng hơn không phẳng?
5. Sai số mà bước MᵀM cực tiểu là gì, tính theo pixel — và cảnh nào (dải độ sâu nào) làm nó lệch xa ước lượng hợp lý cực đại nhất?

## Trích đoạn nguyên văn làm bằng chứng

- "Our central idea is to write the coordinates of the n 3D points as a weighted sum of four virtual control points." [tr. 2]
- "given perfect data from at least six reference points imaged by a perspective camera" [tr. 6]
- "instead of trying to pick a value of N among the set {1, 2, 3, 4}, which would be error-prone if several eigenvalues had similar magnitudes, we compute solutions for all four values of N" [tr. 6]
- "the linearization procedure treats all 10 products βab = βaβb as unknowns and there are not enough constraints anymore." [tr. 7]
- "The main difference is that the number of quadratic constraints drops from 6 to 3." [tr. 7]
- "Since the optimization is performed only over the four βi coefficients, its computational complexity is independent of the number of input 3D-to-2D correspondences." [tr. 7]
- "All the plots discussed in this section were created by running 300 independent MATLAB simulations." [tr. 9]
- "when n = 10 and for reference points lying on a plane with tilt of either 0 or 30 degrees" [tr. 10]
