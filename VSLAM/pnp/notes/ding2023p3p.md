# Revisiting the P3P Problem — ghi chú đọc

| | |
|---|---|
| bibkey | `ding2023p3p` |
| Venue, năm | IEEE/CVF CVPR 2023, tr. 4872–4880 (số trang in ở chân từng trang PDF khớp `refs.bib`) |
| Bản đã đọc | `papers/ding2023p3p.pdf` — bản CVF Open Access (watermark "identical to the accepted version" [tr. 1]), 9 trang kể cả tài liệu tham khảo. **Có tài liệu bổ sung**: openaccess.thecvf.com/content/CVPR2023/supplemental/Ding_Revisiting_the_P3P_CVPR_2023_supplemental.pdf (1 trang, tải về 2026-09-25 chỉ để đọc, không lưu vào `papers/`). Trong ghi chú này, "[supp]" nghĩa là tài liệu bổ sung |
| Mức đọc | lượt 3 (Keshav): dẫn lại eq. (3)–(6), (19)–(22), (24), (28), (30)–(32); cài lại toàn bộ Algorithm 1 bằng numpy |
| Người đọc | Claude (agent), 2026-09-25 — **Huy chưa đọc lại để ký** |
| Mức tin | giữ A (CVPR; bản cài của tôi dựng thuần từ bài báo cho cùng số nghiệm với `cv2.SOLVEPNP_P3P` ở 100% trong 10⁵ lượt). Có ba điểm cần lưu ý: eq. (21) in sai dấu; tuyên bố "bền" chỉ đúng trên phân bố cảnh của bài; khi ba điểm gần thẳng hàng, bộ giải kém AP3P rõ rệt (mục 7, 8) |
| Kiểm chứng | eq. (3)–(6), (24), (25)–(28): cửa (a), tôi tự dẫn lại được. eq. (19), (20), (21), (22), bảng nhánh theo Δ, tuyên bố "danger cylinder ⇒ Δ = 0": cửa (b), script `code/ding2023p3p_check.py`. Mã OpenCV 4.x `calib3d/src/p3p.cpp` do chính Ding đồng tác giả nên **không** tính là cửa (c) |

## 1. Bài toán gốc và bối cảnh

P3P là bài toán tìm pose tuyệt đối của camera đã hiệu chỉnh từ ba tương ứng 2D–3D. Bài toán có tối đa bốn nghiệm thực [§1, tr. 1]. Bộ giải P3P là con đẻ trứng của RANSAC nên phải vừa nhanh vừa không bao giờ đánh rơi nghiệm đúng [§1, tr. 1]. Tác giả chia các lời giải có trước thành hai dòng theo bậc của đa thức một biến cuối cùng [§1, tr. 1–2]. Dòng thứ nhất đưa về một phương trình bậc bốn (quartic): Gao và cs. `gao2003p3p`, Kneip `kneip2011p3p`, Ke–Roumeliotis `ke2017p3p`, Banno và Nakano. Dòng thứ hai đưa về phương trình bậc ba (cubic): Finsterwalder–Scheufele 1937, Grafarend, rồi Lambda Twist `persson2018lambdatwist`. Theo tác giả, Lambda Twist là bộ giải nhanh và chính xác nhất trước bài này [T] [§1, tr. 2]. Chỗ khó mà bài nhắm vào là các cấu hình "cực biên": ở đó hai conic tiếp xúc nhau và bộ giải trả thiếu nghiệm hoặc trả nghiệm trùng. Tác giả nói các bộ giải hiện hành "break down" ở những cấu hình này [T] [Abstract, tr. 1; §4.4, tr. 7]. Bài không đề xuất một công thức mới. Nó phân loại có hệ thống vị trí tương đối của hai conic, rồi dùng phân loại đó để chọn nhánh tính [§3.5, tr. 4–6].

## 2. Giả thiết — kể cả giả thiết ngầm; bỏ đi thì hỏng ở đâu

- **Camera đã hiệu chỉnh, tia chiếu chuẩn hoá |m_i| = 1** [§2, tr. 2]. Nếu bỏ giả thiết này thì cần bộ giải P4Pf, nằm ngoài bài.
- **d_3 ≠ 0**, tức điểm thứ ba không trùng tâm quang học [§2, tr. 2]. Điều kiện này cho phép đổi biến x = d1/d3, y = d2/d3.
- **|BC| > 0**, vì a, b trong eq. (6) chia cho |BC|². Bài không bàn chuyện chọn cạnh nào làm mẫu số. Mã OpenCV/PoseLib thì hoán vị điểm để BC luôn là cạnh dài nhất, một bước không có trong bài (xem mục 8).
- **Ba điểm không thẳng hàng.** Thí nghiệm loại hẳn trường hợp thẳng hàng [§4, tr. 6]. Eq. (28) cũng cần ma trận A = [X1−X2, X3−X1, n_a] khả nghịch, và A suy biến khi ba điểm thẳng hàng. Khi gần thẳng hàng, bộ giải vẫn chạy nhưng mất chính xác nhanh (tôi đo, mục 7).
- **Ngầm: các nhánh Δ = 0 được xét bằng so sánh đúng bằng không** [Algorithm 1, dòng 23 và 25, tr. 6]. Trong số thực dấu phẩy động, Δ gần như không bao giờ bằng đúng 0. Vì vậy các cấu hình tiếp xúc (d)–(h) thực tế rơi vào nhánh Δ > 0 hoặc Δ < 0, và logic "bỏ đường thứ hai" của hai nhánh này làm rơi nghiệm tiếp xúc (tôi đo, mục 7).
- **Ngầm: "không nhiễu là đủ".** Tác giả bỏ thí nghiệm có nhiễu và dữ liệu thật. Lý do họ đưa ra là dữ liệu nhiễu chỉ là dữ liệu không nhiễu với một ground truth khác [§4, tr. 6]. Với bài toán tối thiểu thì lập luận này đúng. Nhưng khi đó tỉ lệ thành công phụ thuộc hoàn toàn vào **phân bố cấu hình** được sinh ra, và phân bố của bài (theo Lambda Twist) không có cảnh gần suy biến nào có chủ đích (tôi suy ra).

## 3. Cơ chế — năm câu, rồi chi tiết có định vị

**Năm câu.** Luật cosin khử R, t và để lại ba phương trình bậc hai theo ba độ sâu. Chia cho d3² thì được hai conic theo (x, y) [eq. (3)–(8)]. Mọi giao điểm của hai conic đều nằm trên mọi thành viên của chùm (pencil) C1 + σC2. Chọn σ là **một** nghiệm thực của cubic det(C1 + σC2) = 0 thì được một conic suy biến, tức một cặp đường thẳng [eq. (9)–(11), Prop. 1]. Cặp đường được tách bằng ma trận phụ hợp (adjoint): −C* = v vᵀ cho giao điểm v của hai đường, rồi C + [v]× = 2pqᵀ cho chính hai đường [eq. (20)–(22)]. Cắt từng đường với conic (5) cho các phương trình bậc hai. Dấu của biệt thức Δ của cubic quyết định dùng nghiệm cubic nào và có cần xét đường thứ hai không [eq. (32), Tab. 1, Algorithm 1].

**Chi tiết (dẫn lại từng bước).**

- *Khử pose* [eq. (1)–(3), tr. 2]. Với d_i m_i = R X_i + t [eq. (1)], khoảng cách giữa hai điểm được bảo toàn: |d_i m_i − d_j m_j|² = |X_i − X_j|². Khai triển ra, ví dụ d1² + d2² − 2d1d2 m1ᵀm2 = |AB|² [eq. (3)]. Cửa (a).
- *Hai conic* [eq. (4)–(6), tr. 2]. Lấy phương trình thứ nhất và thứ hai của (3) chia cho phương trình thứ ba (sau khi đã chia cả ba cho d3²) thì d3 biến mất. Kết quả là x² + (1−a)y² − 2m12xy + 2a m23 y − a = 0 [eq. (4)] và x² − by² − 2m13x + 2b m23 y + 1 − b = 0 [eq. (5)], với a = |AB|²/|BC|², b = |AC|²/|BC|² [eq. (6)]. Tôi dẫn lại khớp từng hệ số (cửa (a)). Script kiểm rằng (x, y) thật nằm trên cả hai conic với sai số chuẩn hoá 4·10⁻¹⁶ (mục 7, [2]).
- *Chùm conic và cubic* [eq. (9)–(11), tr. 2–3]. Trong script, tôi viết C1, C2 trên cơ sở [1, x, y] thành C1 = [[−a, 0, a m23], [0, 1, −m12], [a m23, −m12, 1−a]] và C2 = [[1−b, −m13, b m23], [−m13, 1, 0], [b m23, 0, −b]]. Bài không in hai ma trận này, chỉ nói chúng là "3 × 3 matrices" [tr. 2]. det(C1 + σC2) là một cubic theo σ. Bài không bàn trường hợp hệ số σ³ là det(C2) = b(b(1−m23²) + m13² − 1) bằng 0 (tôi tự tính). Khi đó cubic thoái hoá, nhưng việc chia monic ở eq. (29) vẫn ngầm giả định det(C2) ≠ 0 (tôi suy ra).
- *Vì sao không phải giải quartic* (tôi suy ra, khớp với tinh thần [§1, tr. 1–2]). Cubic luôn có ít nhất một nghiệm thực, và một nghiệm đó là đủ. Nghiệm được tính dạng đóng: công thức lượng giác khi Δ > 0, công thức Cardano khi Δ < 0 [§3.5, tr. 5]. Không cần lặp tìm nghiệm. Sau đó chỉ còn hai phương trình bậc hai (hai đường cắt một conic). Tổng cộng là "một cubic + hai quadratic", đúng như Finsterwalder đã chỉ ra năm 1937 [§1, tr. 1].
- *Mẹo conic suy biến* [eq. (10), (13), (18)–(22), tr. 2–3]. Conic suy biến hạng 2 có dạng C = pqᵀ + qpᵀ [eq. (10)], trong đó p, q là toạ độ đường thẳng. Giao điểm của hai đường là v = p × q [eq. (18)]. Bài đưa hai cách lấy v. Method 1 lấy v từ không gian rỗng của C rồi chỉnh tỉ lệ theo ‖v‖² ở eq. (19). Method 2 dùng −C* = v vᵀ [eq. (20)]: lấy cột ứng với phần tử đường chéo lớn nhất của −C*, chia cho căn của phần tử đó [tr. 3]. Tiếp theo, [v]× = pqᵀ − qpᵀ [eq. (21)] và D = C + [v]× = 2pqᵀ [eq. (22)], nên p là một cột của D và q là hàng tương ứng. Tôi kiểm bằng số: (19) và (20) đúng tới 10⁻¹⁴. **Eq. (21) sai dấu**: với v = p × q thì [v]× = qpᵀ − pqᵀ (mục 7, [1]). Lỗi này vô hại cho thuật toán, vì v lấy từ (20) chỉ xác định tới một dấu, và D khi đó bằng 2qpᵀ, vẫn cho cùng cặp đường. Bài còn có "§3.2 Extracting the Lines Directly" [eq. (14)–(17)] (tác giả gọi là "Direct") và một §3.3 hầu như trống [tr. 3]. Tác giả chọn Method 2 vì nó "more stable" [T] [§4, tr. 6]. Theo [supp, Tab. 2], Direct nhanh nhất (211,7 ns) nhưng có 2 lượt không nghiệm trong 10⁷ [Đ].
- *Từ đường về độ sâu* [eq. (23)–(24), tr. 4]. Thế đường p1 + p2x + p3y = 0 [eq. (23)] vào (5) được một phương trình bậc hai. Chỉ giữ nghiệm dương. Sau đó d3 = |AC| / √(x² − 2m13x + 1), từ eq. (24) [tr. 4]; mẫu số luôn dương vì |m13| < 1. Tiếp theo làm Gauss–Newton trên tổng bình phương của (3) [tr. 4]; bài không nói bao nhiêu bước.
- *Từ độ sâu về pose* [eq. (25)–(28), tr. 4]. Hai hiệu vectơ d1m1 − d2m2 = R(X1 − X2) và d3m3 − d1m1 = R(X3 − X1) [eq. (25)], cộng với pháp tuyến n_b = R n_a [eq. (26)–(27)], cho R = B A⁻¹ [eq. (28)]. Sau đó t lấy từ (1). Bài không trực chuẩn hoá R; khi d đã chính xác thì không cần (cửa (a)). Nhưng A⁻¹ khuếch đại sai số của d khi ba điểm gần thẳng hàng (mục 7).
- *Phân tích nghiệm thực* [§3.5, Fig. 2, Tab. 1, eq. (29)–(32), tr. 4–6]. Đổi biến σ = γ − κ2/3 cho cubic khuyết γ³ + αγ + β = 0 [eq. (30)], với biệt thức Δ = −(4α³ + 27β²) [eq. (32)]. Tab. 1 ghép mỗi kiểu nghiệm của cubic với số cặp đường thực và số giao điểm thực. Δ > 0 ứng với ca (a) (0 giao điểm) và (b) (4 giao điểm). Trong hai ca này, nghiệm cubic nào cũng dùng được; nếu đường thứ nhất không có giao thực thì bỏ đường thứ hai. Δ < 0 ứng với ca (c) (2 giao điểm, cả hai nằm trên cùng một đường); nếu đường thứ nhất đã có giao thực thì bỏ đường thứ hai. Δ = 0 ứng với các ca tiếp xúc (d)–(h); khi đó phải tránh nghiệm kép γ = −3β/(2α), vì ở ca (d) nó cho cặp đường ảo [tr. 5–6]. Tôi kiểm lại công thức nghiệm đơn γ1 = 3β/α và nghiệm kép γ2,3 = −3β/(2α) (cửa (a): tổng các nghiệm bằng 0, tích bằng −β khi 4α³ = −27β²). Lưu ý: Fig. 2 và Tab. 1 được lập **giả định conic (4) là ellipse** ("Without loss of generality" [tr. 5]), trong khi (4) có thể là hyperbola (mục 9).
- *Danger cylinder* [§4.5, Fig. 5, tr. 8; supp §3]. Tác giả báo rằng khi tâm quang học nằm trên mặt trụ đi qua A, B, C (trục vuông góc với mặt phẳng ABC) thì Δ = 0. Họ tìm ra điều này bằng thực nghiệm chứ không chứng minh [T] [tr. 8]; [supp] viết "the discriminant of the cubic equation is always zero". Kiểm số của tôi xác nhận: |Δ|/(4|α|³ + 27β²) ≈ 3·10⁻¹² trên mặt trụ, so với ≈ 0,99 ở cảnh ngẫu nhiên, và tăng xấp xỉ theo ε² khi đẩy O ra khỏi mặt trụ một khoảng tương đối ε (mục 7, [5]).

## 4. Ký hiệu của bài ↔ ký hiệu của khảo sát

| Bài | Khảo sát (`code/common.py`) | Ghi chú |
|---|---|---|
| X_i (i = 1..3), A, B, C | X_w (hàng i) | A = X1, B = X2, C = X3 [Fig. 1, eq. (2)] |
| m_i, \|m_i\| = 1 | f_i = K⁻¹[u_i; 1] chuẩn hoá | bài gọi là "normalized image points" [§2] |
| d_i | độ sâu dọc tia, ‖X_c,i‖ | **không** phải toạ độ z |
| R, t với d_i m_i = R X_i + t | R, t với X_c = R X_w + t | cùng chiều thế giới → camera |
| K | K | bài giả định đã khử K; trong script tôi đặt K = I cho cv2 |
| O | tâm quang học, −Rᵀt | |
| a, b, m12, m13, m23 | — | eq. (6) |
| x, y | d1/d3, d2/d3 | |
| C1, C2, C = C1 + σC2 | — | eq. (7)–(9) |
| p, q; v = p × q | hai đường của conic suy biến; giao điểm của chúng | eq. (10), (18) |
| κ2, κ1, κ0; γ; α, β; Δ | hệ số cubic monic; biến khuyết; biệt thức | eq. (29)–(32) |
| ξ_R = ‖R_gt − R_est‖_L1, ξ_t = ‖t_gt − t_est‖_L1 | — | bài không nói L1 của ma trận là tổng \|phần tử\| hay chuẩn cảm sinh; script dùng tổng \|phần tử\| |

## 5. Bằng chứng — dữ liệu, phần cứng, baseline, con số kèm điều kiện, số lần lặp

**Baseline, chính xác theo bài** [§4, tr. 6]. Có đúng năm cột so sánh, không có Grunert, Gao hay Banno:
- Ke và cs. `ke2017p3p` (quartic). Footnote 1 trỏ tới opencv.org, nên bản được dùng là bản cài trong OpenCV (SOLVEPNP_AP3P) [tr. 6];
- Kneip và cs. `kneip2011p3p` (quartic), bản từ trang của Kneip [tr. 6, footnote 2];
- Nakano (BMVC 2019, không có trong `refs.bib`). Chỉ có bản MATLAB nên tác giả **tự cài lại bằng C++/Eigen** [tr. 6];
- Nakano(rp): Nakano cộng root polishing bằng Gauss–Newton [§4.1, tr. 7];
- Persson–Nordberg, tức Lambda Twist `persson2018lambdatwist` (cubic), mã từ github midjji/lambdatwist-p3p [tr. 6, footnote 4].

**Điều kiện chung** [§4, tr. 6]. Mọi bộ giải chạy bằng C++ trên Intel Core i7-9700 3,0 GHz. Chỉ dùng dữ liệu tổng hợp không nhiễu, sinh theo giao thức của Lambda Twist: quaternion ~ N(0, I) cho R_gt, t_gt ~ N(0, I), toạ độ ảnh chuẩn hoá đều trong [−1, 1]², độ sâu đều trong [0,1; 10], X_i = R_gtᵀ(d_i m_i − t_gt). Các bộ ba thẳng hàng bị loại. Kết quả trong bài dùng Method 2 (adjoint).

- **Độ ổn định số** [§4.1, Fig. 4, Tab. 2, tr. 7], 100 000 lượt, sai số ξ_R + ξ_t [Đ]. Mean / median / max: Ours 3,5e-12 / 1,4e-13 / 2,3e-8; Persson 4,2e-12 / 1,6e-13 / 4,3e-8; Ke 3,5e-7 / 1,1e-13 / 0,011; Kneip 2,5e-6 / 2,5e-13 / 0,070; Nakano 4,4e-7 / 3,0e-13 / 0,002; Nakano(rp) 1,7e-9 / 9,4e-14 / 1,8e-5. Bộ của bài không thắng median; Nakano(rp) thắng [Tab. 2]. Với các bộ quartic, các lượt hỏng "have been removed for this test" [tr. 7], nên mean/max của Ke và Kneip ở đây là **sau khi bỏ lượt hỏng**.
- **Nghiệm** [§4.2, Tab. 3, tr. 7–8], 10⁷ cảnh [Đ]. Ngưỡng: coi là trùng nếu ξ < 10⁻⁵, coi là ground truth nếu ξ < 10⁻⁶. Ours: 16 825 700 nghiệm, 0 trùng, 0 lượt không nghiệm, 9 999 993 lượt tìm được GT, 0 nghiệm sai. Persson: 11 lượt không nghiệm, 9 999 978 lượt có GT. Ke: 163 038 nghiệm trùng, 378 lượt không nghiệm, 375 209 nghiệm sai. Kneip: 7 328 099 nghiệm sai. Nakano: 3 043 lượt không nghiệm. Tác giả giải thích số nghiệm sai lớn của Ke và Kneip là do hai bộ này dùng cả bốn nghiệm quartic và bỏ phần ảo [T] [tr. 7].
- **Thời gian** [§4.3, Tab. 4, tr. 7–8], trung bình trên 10⁷ lượt, mỗi lượt lặp 100 lần [Đ]. Ours 225,8 ns, Persson 260,6, Ke 387,1, Kneip 667,2, Nakano 591,3, Nakano(rp) 702,0; tức nhanh hơn Lambda Twist 1,154 lần. Tác giả thừa nhận bản C++ Nakano của chính họ chậm hơn con số Nakano tự báo bằng MATLAB [T] [tr. 7].
- **Lượt hỏng** [§4.4, tr. 7–8; supp §3]. Trên các lượt Lambda Twist không trả nghiệm nào, biệt thức "rất gần 0" [T]. Phần lớn là ca (d) và (f); các ca (e), (g), (h) "rarely happen" [T]. Bài không đưa số đếm.
- **Không nhất quán giữa bài và [supp].** Cùng phương pháp Adjoint mà [supp, Tab. 1] báo 16 828 556 nghiệm (bài: 16 825 700), và thời gian 224,2 ns đo trên "10⁷ trials with 10 times each" (bài: 225,8 ns, "100 times each"). Vậy hai lần chạy dùng hai tập ngẫu nhiên khác nhau; con số chỉ so được trong cùng một bảng (tôi suy ra).

## 6. Đóng góp thật sự (thường nhỏ hơn abstract)

Công thức hai conic và mẹo conic suy biến đều không mới: tác giả tự nói họ "follow a similar strategy as Persson and Nordberg" [§3, tr. 2], và dạng cubic có từ Finsterwalder 1937 [§1, tr. 1]. Phần mới có ba thứ, mỗi thứ nhỏ. (1) Cách tách cặp đường bằng adjoint, eq. (20)–(22). Cách này rẻ hơn cách của Lambda Twist [T] [§4.3, tr. 7] và là nguồn chính của mức tăng tốc 15% [Đ] [Tab. 4]. (2) Bảng Tab. 1 ghép dấu của Δ với số giao điểm thực, dùng để bỏ bớt việc: chỉ cần một nghiệm cubic, và có khi bỏ được đường thứ hai. (3) Quan sát thực nghiệm rằng cấu hình danger cylinder ứng với Δ = 0. Tuyên bố "correctly solve cases where competing methods might fail" [Abstract] chỉ được đo trên phân bố cảnh ngẫu nhiên của Lambda Twist, nơi cấu hình tiếp xúc rất hiếm. Theo Tab. 3, số lượt Lambda Twist không trả nghiệm là 11/10⁷, còn bộ của bài là 0/10⁷ [Đ]. Đây là khác biệt thật nhưng ở mức 10⁻⁶. Đóng góp có ích nhất trong thực tế có lẽ là bộ giải đã vào OpenCV và PoseLib (xem `refs.bib`), chứ không nằm ở lý thuyết (tôi suy ra).

## 7. Kiểm chứng của người ghi chú — script trong `code/`, lệnh chạy, kết quả thật

Script: `code/ding2023p3p_check.py`. Tôi cài lại Algorithm 1 **từ bài báo** (Method 2 adjoint, Cardano/lượng giác, logic bỏ đường, eq. (24), Gauss–Newton, eq. (28)). Những chỗ bài không quy định, tôi tự chọn như sau: khử biến có hệ số lớn hơn trong (23); tối đa 5 bước Newton trên (3); lấy hàng và cột của D theo phần tử |D_ij| lớn nhất. Hàm sinh cảnh theo §4 của bài, với m_i = [u, v, 1] và d là độ sâu z; bài không nói rõ d nhân với tia đơn vị hay với [u, v, 1]. OpenCV 5.0.0: docstring của `cv2.solveP3P` ghi SOLVEPNP_P3P là Ding và cs. Tôi không lấy được mã nguồn nhánh 5.x (đường dẫn `calib3d/src/p3p.cpp` trả 404 trên nhánh 5.x). Nhánh 4.x có tệp này, với ghi chú "Author: Yaqing Ding, Mark Shachkov" và dẫn nguồn từ PoseLib. Vì vậy tôi kiểm **bằng hành vi** (khối [3] bên dưới).

Lệnh (từ gốc repo, ~140 s trên máy này):

```
python3 VSLAM/pnp/code/ding2023p3p_check.py
```

Kết quả thật (cắt bớt các dòng chú thích):

```
OpenCV 5.0.0; numpy 2.4.6
  docstring cv2.solveP3P nhắc 'Ding' cho SOLVEPNP_P3P: True
[1] Đồng nhất thức đại số của §3.2 trên 1000 cặp p, q ngẫu nhiên
  (20) -C* = v v^T           : sai số tương đối max 1.4e-14  -> PASS
  (19) ||v||^2 theo c_ij     : sai số tương đối max 2.3e-14  -> PASS
  (21) [v]x = pq^T - qp^T    : sai số max 1.7e+01  -> SAI DẤU
       [v]x = qp^T - pq^T    : sai số max 0.0e+00  -> PASS
[2] Nghiệm thật (x, y) = (d1/d3, d2/d3) nằm trên cả hai conic (4), (5); và trên conic suy biến C
  max |h^T C_i h| (chuẩn hoá) = 4.0e-16; det(C)/|C|^3 và h^T C h trên mọi nghiệm cubic: 3.7e-11  -> PASS
[3] 100000 lượt không nhiễu theo giao thức của bài (Lambda Twist): ours vs cv2 P3P vs cv2 AP3P
  Delta>0: 17.4%  Delta<0: 82.6%  Delta==0: 0
  ours(numpy)    nghiệm= 168964 TB/lượt=1.6896 trùng=   0 không-nghiệm=   0 có-GT(xi<1e-6)=100000/100000 (0.000% hỏng) sai-hình-học=0
                 xi của nghiệm tốt nhất: mean=3.1e-13 median=1.3e-14 max=2.0e-09 | log10 p50/p90/p99/p99.9/max = -13.9 / -12.9 / -11.7 / -10.5 / -8.7 | số nghiệm 0..4: [0, 44851, 44782, 6919, 3448]
  cv2 P3P        nghiệm= 168964 TB/lượt=1.6896 trùng=   0 không-nghiệm=   0 có-GT(xi<1e-6)=99999/100000 (0.001% hỏng) sai-hình-học=1
                 xi của nghiệm tốt nhất: mean=6.2e-11 median=2.0e-14 max=5.3e-06 | log10 p50/p90/p99/p99.9/max = -13.7 / -12.6 / -11.2 / -10.1 / -5.3 | số nghiệm 0..4: [0, 44851, 44782, 6919, 3448]
  cv2 AP3P       nghiệm= 234882 TB/lượt=2.3488 trùng=   0 không-nghiệm=   0 có-GT(xi<1e-6)=99993/100000 (0.007% hỏng) sai-hình-học=65946
                 xi của nghiệm tốt nhất: mean=5.7e-08 median=1.3e-14 max=3.1e-03 | log10 p50/p90/p99/p99.9/max = -13.9 / -12.8 / -10.7 / -8.5 / -2.5 | số nghiệm 0..4: [0, 0, 82559, 0, 17441]
  số nghiệm trùng khớp ours vs cv2 P3P: 100.000% lượt; ours vs cv2 AP3P: 42.215% lượt
  khi cùng số nghiệm, xi lớn nhất giữa nghiệm ghép cặp ours<->cv2 P3P: median 2.9e-14, p99.9 9.2e-11
[4] Algorithm 1: (a) bỏ đường thứ hai có làm mất nghiệm không; (b) Delta>0: chọn nghiệm cubic nào cũng như nhau?
  (a) số lượt mà skip-logic đổi số nghiệm: 0/3000  -> PASS
  (b) Delta>0: 525 lượt; số lượt mà 3 nghiệm cubic cho số nghiệm khác nhau: 0  -> PASS
  (... cảnh ngẫu nhiên ở [3]: median |Delta_n| = 0.99)
[5 danger cylinder] 600 lượt mỗi mức eps. Ô = % lượt KHÔNG có nghiệm nào với xi < 1e-6 / < 1e-3; [med] = median log10 xi
      eps  med|Dn| |                   ours |               ours+tol |            ours robust |            ours+Kabsch |                cv2 P3P |               cv2 AP3P
    0e+00  3.4e-12 |     71.7/ 48.5 [ -5.1] |     68.2/ 45.0 [ -5.4] |     53.3/ 31.8 [ -5.9] |     71.7/ 48.5 [ -5.1] |     54.8/ 24.3 [ -5.9] |     59.8/ 49.3 [ -5.3]
    1e-06  6.0e-11 |     27.3/ 13.3 [ -6.7] |     27.3/ 13.2 [ -6.7] |     19.0/  8.2 [ -7.0] |     27.3/ 13.3 [ -6.7] |     24.0/  4.3 [ -6.7] |      3.7/  1.5 [ -7.6]
    1e-04  3.9e-07 |      0.2/  0.0 [ -8.7] |      0.2/  0.0 [ -8.7] |      0.0/  0.0 [ -9.1] |      0.2/  0.0 [ -8.7] |      0.3/  0.0 [ -8.7] |      0.3/  0.0 [ -9.6]
    1e-02  3.8e-03 |      0.0/  0.0 [-10.7] |      0.0/  0.0 [-10.7] |      0.0/  0.0 [-11.0] |      0.0/  0.0 [-10.7] |      0.0/  0.0 [-10.7] |      0.0/  0.0 [-11.6]
[6 gần thẳng hàng] 600 lượt mỗi mức eps. (cùng định dạng)
    1e-02  1.4e-01 |      0.0/  0.0 [-10.1] |      0.0/  0.0 [-10.1] |      0.0/  0.0 [-10.1] |      0.0/  0.0 [-10.3] |      2.2/  0.0 [ -9.1] |      0.0/  0.0 [-12.6]
    1e-03  1.5e-03 |      0.8/  0.0 [ -8.1] |      0.8/  0.0 [ -8.1] |      0.8/  0.0 [ -8.1] |      0.8/  0.0 [ -8.4] |     19.8/  0.3 [ -7.1] |      0.0/  0.0 [-11.6]
    1e-04  1.6e-05 |     46.3/  0.8 [ -6.1] |     46.3/  1.0 [ -6.1] |     46.3/  0.7 [ -6.1] |     35.7/  0.8 [ -6.4] |     75.3/  7.8 [ -5.2] |      0.0/  0.0 [-10.6]
    1e-06  1.6e-09 |    100.0/ 87.7 [ -2.0] |    100.0/ 87.7 [ -2.0] |    100.0/ 87.7 [ -2.1] |    100.0/ 74.2 [ -2.2] |    100.0/ 93.5 [ -1.2] |      0.0/  0.0 [ -8.6]
    1e-08  3.8e-10 |    100.0/100.0 [  inf] |    100.0/100.0 [  5.1] |    100.0/100.0 [  2.5] |    100.0/100.0 [  inf] |    100.0/100.0 [  2.7] |     44.0/ 11.3 [ -6.2]
[7] Chẩn đoán gần thẳng hàng: sai số tương đối của độ sâu d_i (trước eq. (28)) so với sai số pose
  eps=1e-02: median log10 |d-d_gt|/d =  -12.0;  median log10 xi =  -10.0
  eps=1e-03: median log10 |d-d_gt|/d =  -11.0;  median log10 xi =   -8.1
  eps=1e-04: median log10 |d-d_gt|/d =  -10.0;  median log10 xi =   -6.1
  eps=1e-05: median log10 |d-d_gt|/d =   -9.0;  median log10 xi =   -4.0
Tổng thời gian: 142s
```

Đọc kết quả:

- **Cơ chế lõi đúng** [M]. (19), (20), (22) và phép dẫn (4)–(5) đều qua. Riêng (21) sai dấu, như đã nói ở mục 3; lỗi này không ảnh hưởng tới thuật toán.
- **`SOLVEPNP_P3P` trong OpenCV 5.0.0 là Ding** [M]. Bản numpy dựng thuần từ bài báo cho **cùng số nghiệm ở 100% trong 10⁵ lượt**, và các nghiệm ghép cặp lệch nhau với median 3·10⁻¹⁴. Ngược lại, AP3P khớp số nghiệm chỉ ở 42%. Docstring cũng ghi Ding. Tôi không đọc được mã 5.x, nên đây là bằng chứng hành vi chứ không phải bằng chứng mã nguồn.
- **So với con số của bài** [M]. Số nghiệm trung bình mỗi lượt: của tôi 1,690, của bài 16 825 700 / 10⁷ = 1,683 [Tab. 3]; khớp tới 0,4%, và chênh lệch có thể do định nghĩa độ sâu. Tỉ lệ tìm được GT: 100 000/100 000 ở bản của tôi, so với 9 999 993/10⁷ trong bài; hai con số nhất quán (bài dự đoán khoảng 0,07 lượt hỏng trên 10⁵ lượt). cv2 P3P hỏng 1/10⁵ lượt. Con số này cao hơn kỳ vọng từ Tab. 3 nhưng một lượt thì chưa đủ để kết luận. Mean / median / max của ξ ở bản của tôi là 3,1e-13 / 1,3e-14 / 2,0e-9, so với 3,5e-12 / 1,4e-13 / 2,3e-8 của bài [Tab. 2]. Của tôi nhỏ hơn đều khoảng 10 lần ở cả ba thống kê. Tôi **không giải thích được** chênh lệch này; các nghi vấn là cách tính chuẩn L1 của ma trận, định nghĩa d, và số bước Gauss–Newton. **Điều kiện không khớp hoàn toàn**: của tôi là Python double và 10⁵ lượt cho mọi bảng, trong khi bài dùng C++ và 10⁷ lượt cho Tab. 3. Tôi không đo thời gian so sánh được.
- **AP3P trong OpenCV 5.0.0 không phải bản mà bài đo** [M]. Bản 5.0.0 luôn trả 2 hoặc 4 nghiệm (trung bình 2,35 nghiệm/lượt), và 28% số nghiệm sai hình học. Bài báo đo Ke được 1,74 nghiệm/lượt với 2,2% nghiệm sai [Tab. 3]. Vậy các so sánh với Ke trong bài không chuyển được sang OpenCV hiện tại. Kneip, Nakano và Lambda Twist tôi **không** chạy, vì chúng không có trong cv2.
- **Danger cylinder** [M]. Tuyên bố Δ = 0 của bài được xác nhận: |Δ_n| cỡ 10⁻¹², và tăng theo ε² khi rời mặt trụ. Nhưng **không bộ giải nào** tìm lại được GT một cách tin cậy khi O nằm trên mặt trụ. Tỉ lệ lượt không có nghiệm nào có ξ < 10⁻³ là 48,5% với bản dựng đúng theo bài, 24,3% với cv2 P3P và 49,3% với cv2 AP3P. Tôi chẩn đoán thêm bằng một đoạn thử riêng, không nằm trong script: trong các lượt mà số học đẩy Δ sang âm, đường chứa nghiệm tiếp xúc có biệt thức bậc hai cỡ −10⁻¹⁴. Đường còn lại có hai giao thực, nên logic "đã có giao thực thì bỏ đường thứ hai" của nhánh Δ < 0 làm rơi GT. Biến thể "robust" của tôi không bỏ đường nào, có dung sai tiếp xúc, và thử cả ba nghiệm cubic khi Δ > 0. Nó hạ tỉ lệ hỏng xuống 31,8% nhưng không về 0. Điều này hợp lý, vì trên mặt trụ nghiệm thật là nghiệm kép và bài toán tự nó suy biến (tôi suy ra).
- **Gần thẳng hàng** là phát hiện rõ nhất [M]. Bản của tôi và cv2 P3P mất chính xác theo khoảng 1/ε², còn AP3P chỉ theo khoảng 1/ε. Ví dụ ở ε = 10⁻⁴, tỉ lệ lượt không có nghiệm với ξ < 10⁻⁶ là 46% (của tôi) và 75% (cv2 P3P), so với 0% của AP3P. Ở ε = 10⁻⁶, AP3P vẫn đạt median ξ ≈ 10⁻⁸·⁶, còn Ding hỏng hoàn toàn. Khối [7] cho thấy sai số của độ sâu tăng theo 1/ε, và bước độ sâu → R nhân thêm một thừa số 1/ε. Thay eq. (28) bằng Kabsch không cứu được, vì cách nào đi qua độ sâu cũng gặp khuếch đại này. Đồng thời |Δ_n| ∝ ε², tức cấu hình gần thẳng hàng cũng tiến về vùng tiếp xúc. Bài báo không kiểm vùng này vì đã loại cấu hình thẳng hàng [§4, tr. 6].
- Trên dữ liệu ngẫu nhiên, logic của Algorithm 1 đúng: bỏ đường thứ hai không làm mất nghiệm (0/3000 lượt), và với Δ > 0 thì cả ba nghiệm cubic cho cùng số nghiệm (0/525 lượt khác nhau). Tức tuyên bố "any real root" [tr. 6] qua được cửa (b) **khi Δ cách xa 0**.

## 8. Chỗ tôi không tin

- **Tuyên bố bền vững bị giới hạn bởi phân bố thử.** Abstract và §5 nói bộ giải "more robust" [tr. 1, 8]. Bằng chứng duy nhất là 10⁷ cảnh ngẫu nhiên, nơi ca tiếp xúc hiếm tới mức Lambda Twist cũng chỉ hỏng 11 lần [Tab. 3]. Bài không có thí nghiệm nào **nhắm vào** danger cylinder hay cấu hình gần thẳng hàng; §4.5 chỉ báo quan hệ với Δ. Trên danger cylinder, bản đúng theo Algorithm 1 của tôi hỏng khoảng 48% (mục 7), không tốt hơn AP3P. Các nhánh Δ = 0 được phân tích kỹ trong §3.5 nhưng không bao giờ được kích hoạt bằng phép so sánh đúng bằng 0 (0/10⁵ lượt, và cả trên mặt trụ Δ vẫn khác 0), nên phần phân tích đẹp nhất của bài không bảo vệ được chính những ca nó mô tả.
- **Mã phát hành khác Algorithm 1.** Tôi đọc tệp OpenCV 4.x `modules/calib3d/src/p3p.cpp`, ghi "Author: Yaqing Ding, Mark Shachkov", chép từ PoseLib. Mã này có năm chỗ khác bài: (i) hoán vị điểm để BC là cạnh dài nhất; (ii) ngưỡng tuyệt đối −1e-12 cho biệt thức bậc hai, coi giá trị âm nhẹ là nghiệm kép; (iii) nhánh Cardano chỉ dừng khi đã có nghiệm **dương**, còn bài nói nghiệm **thực**; (iv) luôn lấy cột 0 và hàng 0 của D, trong khi bài nói "one row and the corresponding column"; (v) 5 bước Newton có điều kiện dừng. Trên danger cylinder, cv2 P3P hỏng 24% so với 48% của bản đúng theo bài. Vậy ít nhất một phần độ bền của bản trong thư viện đến từ các chi tiết **không được viết trong bài** (tôi suy ra; tôi chưa tách riêng từng chi tiết).
- **Eq. (21) sai dấu** (mục 3, mục 7). Lỗi nhỏ và vô hại cho thuật toán, nhưng nó cho thấy phần dẫn trong §3.2 không được kiểm kỹ. Bản in còn có §3.3 gần như trống, và câu "Combining (12), (12) and (18)" [tr. 3] lặp số hiệu công thức.
- **Tab. 2 so sánh không đồng đều.** Các lượt hỏng của bộ quartic bị loại trước khi tính mean/max [tr. 7], trong khi cột "Ours" không bị loại gì. Hai điều kiện khác nhau được đặt cạnh nhau trong một bảng. Tab. 3 thì dùng ngưỡng tuyệt đối 10⁻⁶ trên ξ. Vì t ~ N(0, I) có độ lớn cỡ 1 nên ngưỡng này hợp lý cho giao thức này, nhưng không chuyển được sang cảnh có thang đo khác.
- **Tốc độ.** 15,4% nhanh hơn được đo trên một CPU, và Nakano là bản tác giả tự cài, mà chính tác giả nghi bản cài đó chậm bất thường [tr. 7]. Khi bộ giải nằm trong RANSAC, 35 ns chênh lệch thường bị lấn át bởi khâu chấm điểm hypothesis. Lợi thế thật đáng kể hơn là số nghiệm trả về ít hơn: 1,69 so với 2,35 nghiệm/lượt của AP3P trong OpenCV 5.0.0 (mục 7) (tôi suy ra).
- **"The noisy case can be considered as noise free data with different unknown ground truth"** [tr. 6]. Lập luận này đúng về đại số, nhưng nó bỏ qua việc nhiễu có thể đẩy một cấu hình vào gần vùng suy biến. Bài vì thế không có số liệu nào về tỉ lệ cấu hình gần suy biến trong dữ liệu thật.

## 9. Chỗ tôi chưa hiểu (→ `99-chua-biet.md`)

- **Vì sao Tab. 1 vẫn đúng khi cả hai conic đều là hyperbola?** Bài chỉ vẽ Fig. 2 cho trường hợp ellipse + hyperbola "without loss of generality" [tr. 5], trong khi (4) có định thức dạng toàn phương 1 − a − m12², có thể âm. Lý thuyết chùm conic xạ ảnh gợi ý rằng phân loại theo nghiệm cubic không phụ thuộc loại affine của conic (tôi suy ra). Kiểm [4b] ủng hộ điều này trên 525 lượt, nhưng tôi chưa tự chứng minh.
- **Vì sao danger cylinder cho đúng Δ = 0?** Tôi đoán chuỗi lập luận là: O nằm trên mặt trụ ⇒ Jacobian của hệ (3) suy biến tại nghiệm thật (Thompson 1966, không có trong `refs.bib`) ⇒ nghiệm thật là nghiệm kép ⇒ hai conic tiếp xúc ⇒ cubic của chùm có nghiệm bội ⇒ Δ = 0. Tôi chưa kiểm từng mắt xích, và bài cũng không chứng minh [tr. 8; supp §3].
- **Vì sao cấu hình gần thẳng hàng làm |Δ| ∝ ε², và vì sao sai số độ sâu ∝ 1/ε?** Khi ba điểm thẳng hàng, bài toán P3P vẫn có hữu hạn nghiệm độ sâu, nên tôi không thấy lý do để độ sâu phải nhạy như vậy. Có thể thừa số 1/ε đến từ chính công thức hai conic chứ không phải từ bài toán.
- **Chi tiết nào trong mã OpenCV làm nó bền gấp đôi trên danger cylinder nhưng lại tệ hơn khi gần thẳng hàng?** Ở ε = 10⁻³, tỉ lệ hỏng với ngưỡng 10⁻⁶ là 19,8% của cv2 P3P so với 0,8% bản của tôi. Nghi phạm đầu tiên là bước hoán vị để BC dài nhất.

## 10. Quan hệ với các bài khác trong `refs.bib`

- `persson2018lambdatwist`: cùng ý tưởng hai conic + conic suy biến + một nghiệm cubic. Ding kế thừa trực tiếp [§3, tr. 2], cải tiến cách tách đường và chọn nhánh, và báo nhanh hơn 1,154 lần [Tab. 4]. Bài dùng lại cả giao thức sinh dữ liệu của Lambda Twist [§4, tr. 6], nên phép so sánh diễn ra trên "sân nhà" của dòng cubic.
- `ke2017p3p`: baseline qua bản cài trong OpenCV [tr. 6, footnote 1]. Bài báo cho rằng Ke trả nhiều nghiệm sai vì dùng phần thực của nghiệm phức [tr. 7]. Kiểm của tôi với OpenCV 5.0.0 cho thấy ý đó vẫn đúng và thậm chí tệ hơn (28% nghiệm sai), **nhưng** AP3P bền hơn Ding rõ rệt khi ba điểm gần thẳng hàng (mục 7). Trên cấu hình đó hai bài mâu thuẫn nhau về tuyên bố "bền hơn".
- `kneip2011p3p`: baseline quartic. Theo Tab. 3, bộ này có 7 328 099 nghiệm sai trong 10⁷ lượt [Đ].
- `gao2003p3p`: được nhắc như lời giải giải tích đầy đủ đầu tiên [§1, tr. 1] nhưng **không** có trong thí nghiệm. Theo `refs.bib`, đây từng là SOLVEPNP_P3P của OpenCV cũ.
- `haralick1994review`: bài trích Haralick và cs. CVPR 1991 [12]. Có vẻ đó là bản hội nghị tiền thân của bài review IJCV 1994 (tôi suy ra, chưa đối chiếu), và bài dùng nó làm nguồn tổng kết các lời giải cubic cổ [§1, tr. 1–2].
- `fischler1981ransac`: bối cảnh RANSAC [§1, tr. 1]. `chen2020bpnp`: được trích như ví dụ PnP trong học sâu end-to-end [§1, tr. 1].
- `poselib`: bài không nhắc, nhưng mã OpenCV ghi rõ lấy từ PoseLib. Nakano 2019 (BMVC), Banno 2018 (IVC), Thompson 1966 (danger cylinder), Finsterwalder–Scheufele 1937 và Grunert 1841 **không có trong `refs.bib`**.

## 11. Nó đổi gì trong suy nghĩ

Trước khi đọc, tôi coi "P3P mặc định của OpenCV/PoseLib" là lời giải đã xong và bền ở mọi nơi. Sau khi đọc và đo, tôi thấy nó tốt nhất trên cảnh ngẫu nhiên kiểu Lambda Twist: ít nghiệm thừa và không có nghiệm sai. Nhưng nó dựa vào dạng hai conic, nên kế thừa đúng các điểm yếu của dạng này ở hai vùng: cấu hình tiếp xúc (danger cylinder) và bộ ba gần thẳng hàng. Ở vùng thứ hai, AP3P tốt hơn nhiều bậc độ lớn. Với bài học về PnP, câu hỏi dẫn đường số 1 cần một bảng "bộ giải × cấu hình suy biến", thay vì một thứ hạng duy nhất. Trong RANSAC, mẫu gần thẳng hàng thường cho hypothesis kém dù bộ giải nào, nên khác biệt này chủ yếu quan trọng khi dùng nghiệm P3P trực tiếp, chẳng hạn khởi tạo từ đúng ba điểm (tôi suy ra).

## 12. Câu hỏi tự kiểm (3–5 câu, hỏi *vì sao* / *khi nào hỏng*)

1. Vì sao chỉ cần **một** nghiệm thực của cubic det(C1 + σC2) = 0 là đủ để tìm mọi giao điểm thực của hai conic? Khi Δ > 0, trong trường hợp nào nghiệm được chọn lại cho cặp đường ảo, và vì sao điều đó không làm mất nghiệm ở ca (a) nhưng có thể làm mất nghiệm khi Δ chỉ dương do sai số làm tròn?
2. Vì sao −C* = v vᵀ chỉ cho v tới một dấu, và vì sao dấu sai trong eq. (21) không làm hỏng thuật toán?
3. Khi ba điểm gần thẳng hàng với độ lệch tương đối ε, vì sao sai số pose của Ding tăng theo 1/ε² còn AP3P chỉ theo 1/ε? Bước nào trong chuỗi (conic → d → R) góp mỗi thừa số 1/ε?
4. Vì sao logic "đã có giao thực trên đường thứ nhất thì bỏ đường thứ hai" (nhánh Δ < 0) đúng với ca (c) nhưng làm rơi nghiệm tiếp xúc ở ca (f) khi số học đẩy Δ sang âm?
5. Khi O nằm đúng trên danger cylinder, vì sao **không** bộ giải P3P nào có thể trả nghiệm đúng tới 10⁻⁶ một cách tin cậy trong số học double, bất kể thuật toán? Gợi ý: nghiệm kép và ε_máy^(1/2).

## Trích đoạn nguyên văn làm bằng chứng

- "In this paper we algebraically formulate the problem as finding the intersection of two conics." [tr. 1]
- "The intersections are found by building a degenerate conic which also intersects the true solutions." [tr. 2]
- "In practice, we find that Method 2 is more stable." [tr. 6]
- "We omit the experiments with noisy data and real data" [tr. 6]
- "The cases where three points are collinear are removed" [tr. 6]
- "Note that, the quartic based solvers contain failure cases which have been removed for this test." [tr. 7]
- "We have found that the discriminant of the no solution cases by Persson and Nordberg [21] is very close to zero." [tr. 7]
- "There might be more constraints on the cubic equation. Unfortunately, we have not found a good way to do this." [tr. 8]
