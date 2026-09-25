# Infinitesimal Plane-Based Pose Estimation (IPPE) — ghi chú đọc

| | |
|---|---|
| bibkey | `collins2014ippe` |
| Venue, năm | International Journal of Computer Vision 109(3), 2014 (theo `refs.bib`; bản thảo tác giả không in số tập/trang) |
| Bản đã đọc | `papers/collins2014ippe.pdf` — bản thảo tác giả ("Noname manuscript No.", mẫu Springer), 36 trang; mã gốc được tác giả trỏ tới tobycollins.net/research/IPPE [tr. 1] |
| Mức đọc | lượt 2 toàn bài; lượt 3 cho §3 (Jacobian eq. (14), lời giải eq. (20)–(24), Theorem 3–6, Lemma 3–4) |
| Người đọc | Claude (agent), 2026-09-25 — **Huy chưa đọc lại để ký** |
| Mức tin | giữ A (IJCV, cài trong OpenCV; lõi toán học tôi dựng lại và kiểm số được), nhưng bản thảo có **ba lỗi in trong công thức** (mục 8) — đừng chép eq. (14), (22) và chứng minh Theorem 5 nguyên văn |
| Kiểm chứng | eq. (14) ở u0 = 0, eq. (21)–(24), (27)–(28), (36), Theorem 3–6, Lemma 4: cửa (b), script `code/collins2014ippe_check.py`, 14/14 PASS (hai PASS trong đó xác nhận lỗi in). Quan hệ phản xạ và góc 2α: thêm cửa (a), tôi tự dẫn được (mục 3). Đối chiếu mã OpenCV `ippe.cpp` (cùng tác giả, nên KHÔNG tính là cửa (c)) |

## 1. Bài toán gốc và bối cảnh

Bài toán là ước lượng pose của một mặt phẳng đã biết mô hình từ một ảnh, khi camera đã hiệu chỉnh: cho n ≥ 4 tương ứng điểm trên mặt phẳng mô hình ↔ điểm ảnh, tìm R, t [§1, tr. 1]. Trước bài này có hai họ lời giải. Họ thứ nhất là phân rã homography (PHD, Zhang/Sturm): ước lượng H rồi lấy hai cột đầu chuẩn hoá làm r1, r2. Cách này nhanh nhưng cực tiểu hoá một sai số đại số trên 8 hệ số H với giả thiết nhiễu IID trên H, điều tác giả cho là không đúng [§1, tr. 2]. Nó cũng chỉ trả **một** nghiệm, nên hỏng khi homography gần affine, tức khi target nhỏ hoặc ở xa [§1, tr. 2; §2.1.3, tr. 5]. Họ thứ hai là PnP tổng quát coi mặt phẳng như trường hợp riêng (RPP-SP `schweighofer2006planar`, EPnP `lepetit2009epnp`, RPnP `li2012rpnp`). Các bộ giải này chính xác hơn nhưng chậm hơn, và vì dựa vào tìm nghiệm đa thức nên không nói trước được số nghiệm hay quan hệ hình học giữa các nghiệm [§1, tr. 3; §2.2, tr. 5–6]. Chỗ khó mà bài nhắm vào là làm sao tận dụng phần dư thừa (8 hệ số H so với 6 bậc tự do của pose) mà không phải cực tiểu hoá sai số lặp.

## 2. Giả thiết — kể cả giả thiết ngầm; bỏ đi thì hỏng ở đâu

- **Camera đã hiệu chỉnh, méo đã khử** [§1 "Background and notation", tr. 3]. Nếu K sai thì v và J (tính trong toạ độ chuẩn hoá) sai theo, và γ không còn là nghịch đảo độ sâu (tôi suy ra).
- **Mô hình phẳng, đặt trên z = 0, trọng tâm các u_i ở gốc** [tr. 4]. Mã OpenCV xử lý mặt phẳng bất kỳ bằng cách đưa điểm về dạng chính tắc trước (`makeCanonicalObjectPoints` trong `ippe.cpp`), điều này nằm ngoài bài.
- **Đã có homography Ĥ, và Ĥ không hạng 1 (J ≠ 0)** [Theorem 5, tr. 9]. Toàn bộ lời giải đi qua Ĥ, nên chất lượng IPPE bị chặn bởi bộ ước lượng homography. Bài chọn Harker–O'Leary (HO, không có trong `refs.bib`) sau khi so năm bộ ước lượng [§4.4, tr. 15].
- **Nhiễu ảnh Gauss IID đẳng hướng** trong phân tích chọn u0 [§3.2, tr. 7]. Theorem 1 còn dùng thêm xấp xỉ bậc nhất của Ĥ bằng một phép affine [tr. 8]. Theorem 2 cần giả thiết mạnh hơn nữa: các số hạng phối cảnh H'31, H'32 của homography đã chuẩn hoá phải "không đáng kể" [tr. 8]. Khi target lớn và nghiêng mạnh thì trọng tâm không còn được chứng minh là điểm tối ưu; bài nói nó vẫn "rất gần" nhưng không đưa số đo nào [tr. 8].
- **Giả thiết ngầm: chọn nghiệm bằng sai số tái chiếu là đủ.** Lemma 3 bảo đảm hai nghiệm cho hình chiếu khác nhau khi không có nhiễu [tr. 10], nhưng quy tắc quyết định khi có nhiễu thì bị bỏ ngỏ và đẩy cho ứng dụng [§3.4, tr. 11].

## 3. Cơ chế — năm câu, rồi chi tiết có định vị

**Năm câu.** Hàm biến điểm mặt phẳng thành điểm ảnh, w(u) = π(H[u;1]), phải bằng π∘s với s(u) = R[u;0] + t. Nếu cân bằng giá trị và đạo hàm bậc nhất của hai hàm tại **một** điểm u0 thì được đúng sáu ràng buộc cho sáu ẩn [eq. (7)–(11)]. Sau khi khử độ sâu, sáu ràng buộc này thu về việc tách một ma trận 2×2 A thành một hệ số dương γ nhân một khối 2×2 trích từ ma trận xoay; γ bằng giá trị kỳ dị lớn nhất của A và là nghịch đảo độ sâu của u0 [eq. (16), (21), (22)]. Khối 2×2 xác định hai cột đầu của R chỉ sai khác một dấu ±b ở hàng thứ ba, nên luôn có đúng một hoặc hai nghiệm xoay. Hai nghiệm này là ảnh phản xạ của nhau qua mặt phẳng đi qua điểm s(u0) và vuông góc với tia nhìn [v;1] [Theorem 4, eq. (24), (27)]. Điểm u0 được đặt ở trọng tâm các điểm mô hình, vì theo lan truyền sai số bậc nhất đó là nơi v và J ít nhiễu nhất [Theorem 1–2].

**Chi tiết.**
- *Jacobian của homography tại u0* [eq. (14), tr. 7]: J = (1 + u_x Ĥ31 + u_y Ĥ32)^(−2) [J11 J12; J21 J22]. Tại u0 = 0 (dạng mà Algorithm 2 thực sự dùng [tr. 13]), công thức rút gọn thành J11 = Ĥ11 − Ĥ31Ĥ13, J12 = Ĥ12 − Ĥ32Ĥ13, J21 = Ĥ21 − Ĥ31Ĥ23, J22 = Ĥ22 − Ĥ32Ĥ23, và v = [Ĥ13, Ĥ23] khi Ĥ33 = 1. Dạng này tôi kiểm đúng (C1a). Ở số hạng bậc nhất theo u0, bản in đặt u_x và u_y **sai chỗ**: J11, J21 phải nhân u_y, còn J12, J22 phải nhân u_x (tôi tự lấy đạo hàm, rồi kiểm C1b: sai số tương đối 5,6·10⁻² và 8,1·10⁻² với bản in, 10⁻⁸ với bản đã sửa).
- *Khử độ sâu* [eq. (15)–(16), tr. 7]: từ π(x) = v suy ra J_π(x) = x3⁻¹[I2 | −v]. Bài toán trở thành: tìm γ > 0 và R32 (hai cột đầu của R) sao cho γ[I2|−v]R32 = J và R32ᵀR32 = I2.
- *Xoay về tia nhìn* [eq. (20)–(21), (23), tr. 9]: R_v là phép xoay nhỏ nhất đưa trục z về [v;1] (công thức Rodrigues ở eq. (23)). Khi đó [I2|−v]R_v = [B|0], và bài toán còn lại là γ·R̃22 = A với A = B⁻¹J.
- *Lời giải* [eq. (22), (24), tr. 9]: γ = σ1(A), vì giá trị kỳ dị lớn nhất của một khối 2×2 lấy từ ma trận xoay là 1 [eq. (25)–(26), tr. 10]. Biểu thức đóng in trong eq. (22), ½(a_u + a_w + √((a_u − a_w)² + 4a_v²)) với [a_u a_v; a_v a_w] = AAᵀ, thật ra là trị riêng lớn nhất của AAᵀ, tức σ1², nên **phải lấy căn** (C2b; mã OpenCV cũng lấy căn: `gamma = sqrt(gamma2)`). Tiếp theo, R̃22 = A/γ và b = ±√(hạng-1 của I2 − R̃22ᵀR̃22). Cột thứ ba bằng tích có hướng của hai cột đầu, nên R̃1 = [R̃22 +c; +bᵀ a] và R̃2 = [R̃22 −c; −bᵀ a], và cuối cùng R_j = R_v R̃_j.
- *Translation* [eq. (28), tr. 10]: t_j = γ⁻¹[v;1] − R_j[u0;0]. Với u0 là trọng tâm, **hai nghiệm có cùng vị trí trọng tâm trong hệ camera**. Algorithm 2 lại tính t bằng bình phương tối thiểu tuyến tính trên sai số trong không gian camera [eq. (36), tr. 12–13], vì tác giả thấy cách này "slightly more accurately" [tr. 12]. Với cách này hai t không còn trùng nhau.
- *Quan hệ hình học* [eq. (27), tr. 10]: R̃2 = D R̃1 D với D = diag(1, 1, −1). Suy ra R2 = M R1 D, trong đó M = I − 2llᵀ và l = [v;1]/‖[v;1]‖ (tôi suy ra từ eq. (24), (27)). Trên mặt phẳng z = 0 thì D không tác dụng, nên X2 − x0 = M(X1 − x0) với mọi điểm mô hình: đây là phép phản xạ gương thật sự qua mặt phẳng đi qua x0 và vuông góc với l. Pháp tuyến n2 = −M n1 là ảnh phản xạ của n1 qua đường thẳng l. Nếu α là góc giữa n1 và l thì tr(R1ᵀR2) = 1 + 2cos 2α, nghĩa là **hai xoay cách nhau đúng 2α** (tôi tự dẫn, qua cửa (a); C3 kiểm đến 10⁻¹² độ).
- *Duy nhất* [chứng minh Theorem 4, tr. 10]: R1 = R2 ⇔ b = 0 ⇔ a = 1, tức mặt phẳng vuông góc với **tia nhìn tới u0**. Mặt phẳng song song mặt ảnh nhưng nằm lệch khỏi trục quang vẫn có hai nghiệm (C4b: 33,9° tại pixel (520, 100)).
- *Front-facing* [§3.5, Lemma 4, eq. (31), tr. 11]: ràng buộc "nhìn thấy mặt trước" tương đương với det(J) ≥ 0. Vì vậy hoặc cả hai nghiệm đều hợp lệ, hoặc không nghiệm nào hợp lệ, và ràng buộc này không phân xử được giữa hai nghiệm.
- *Liên hệ P3P* [§3.6, Theorem 6, eq. (32)–(35), tr. 11–12]: tuyến tính hoá P3P quanh u0 = 0 cho J = QU⁻¹ + O². Vậy IPPE là giới hạn của P3P khi ba điểm (ảo, dự đoán từ Ĥ) co về một điểm. Trong giới hạn đó translation duy nhất và xoay có hai nghiệm.

## 4. Ký hiệu của bài ↔ ký hiệu của khảo sát

| Bài | Khảo sát (`code/common.py`) | Ghi chú |
|---|---|---|
| u ∈ ℝ² (điểm trên mặt phẳng mô hình), [uᵀ 0]ᵀ | X_w (với X_w,z = 0) | bài giả sử Σu_i = 0 [tr. 4] |
| q_i (pixel) | u | **trùng chữ u, khác nghĩa**: u của bài là điểm mô hình |
| q̃_i = K⁻¹(q − c) [eq. (2)] | K⁻¹[u;1] (chưa chuẩn hoá về độ dài 1) | f của khảo sát là q̃ đã chuẩn hoá đơn vị |
| R, t với s(u) = R[u;0] + t | R, t với X_c = R X_w + t | cùng chiều thế giới → camera |
| K [eq. (1)] | K | bài cho phép có skew s |
| H, Ĥ (mô hình → toạ độ ảnh chuẩn hoá), Ĥ33 = 1 | — | không phải homography pixel |
| v = π(Ĥ[u0;1]), J = J_w(u0) | — | ảnh của u0 và Jacobian 2×2 tại đó |
| x = s(u0), γ = 1/x3 | X_c của trọng tâm; 1/độ sâu | |
| R32, R22 | hai cột đầu của R; khối 2×2 trên trái | SS2×2 = khối 2×2 của ma trận xoay [tr. 3] |
| R_v, B, A, R̃, b, c, a | — | eq. (20)–(24) |
| σ_I, σ_M | nhiễu ảnh (px), nhiễu mô hình | [Tab. 1] |
| RE (độ), TE (%) | `rot_err_deg`, `trans_err_rel` | [§4.3, tr. 14] |

## 5. Bằng chứng — dữ liệu, phần cứng, baseline, con số kèm điều kiện, số lần lặp

**Mô phỏng** [§4.1, tr. 13–14]. Ảnh 640×480, f = 800 px, điểm chính (320, 240). Tâm target nằm trên tia qua một pixel ngẫu nhiên, độ sâu d ~ U(f/2, 2f), xoay trong mặt phẳng ngẫu nhiên, nghiêng ngoài mặt phẳng tới mức góc so với tia nhìn dưới 80°. Target là hình vuông cạnh w, điểm đều trong đó. Nhiễu Gauss σ_I trên ảnh và σ_M trên mô hình. Chỉ giữ các mẫu mà mọi điểm nằm trong ảnh. Có hai chế độ đo [§4.2, tr. 14]. Mode 1 loại mẫu "mơ hồ" bằng tỉ số log-likelihood giữa homography phối cảnh và affine, D < τ_a = 5, rồi bắt mỗi thuật toán trả một nghiệm có sai số tái chiếu nhỏ nhất. Mode 2 giữ mọi mẫu và chấm nghiệm **gần ground truth nhất**.

- [Đ] IPPE so với PHD, qua năm thí nghiệm E1–E5, "5,000 simulated poses" mỗi thí nghiệm [§4.4, tr. 15; Tab. 2–7]. Ví dụ E1 (n = 10, w = 200, homography HO, Mode 1) ở hàng σ_I = 3,79: RE của IPPE là 4,07 ± 8,73°, của HDSt 14,9 ± 12,2°, của HDZh 15,2 ± 12,4° (trung bình ± độ lệch chuẩn) [Tab. 3, tr. 17]. IPPE thắng PHD ở mọi bộ ước lượng homography. HO tốt nhất cho IPPE, còn DLT tốt nhất cho PHD [tr. 15].
- [Đ] So với PnP (E6–E17, w = 300, n = 4→10 và 8→50): IPPE+HO là bộ giải không lặp tốt nhất về xoay khi n ≥ 6. Khi n = 4 với điểm ngẫu nhiên, IPPE+HO **thua** RPnP và RPP-SP [§4.5.2, tr. 18]. Khi n > 15, việc tinh chỉnh bằng GEOMREF gần như không thêm gì [§4.5.1, tr. 18]. Các kết quả này chỉ có ở dạng đồ thị [Fig. 2–3], bài không in bảng số.
- [Đ] Khi đặt bốn điểm ở góc hình vuông, như với marker AR (E18–E23, w = 100), IPPE+HO vượt RPnP ở mọi n [tr. 19; Fig. 4]. Trong Mode 2 với w = 50 (E24–E29, nhiều ca mơ hồ), IPPE+HO tốt nhất về xoay, sát GEOMREF [§4.5.3, tr. 19; Fig. 5].
- [Đ] IPPE thắng P3P đặt trên ba điểm ảo lấy từ Ĥ (đặt ngẫu nhiên hoặc ở góc hộp bao) [§4.6; Fig. 6]. P3P-Random không trả nghiệm nào ở 3–4% số ca [tr. 23].
- [Đ] Dữ liệu thật: (i) "Game cover", 28 ảnh 2304×1536 chụp bằng Nikon D3100, 250–400 tương ứng SIFT mỗi ảnh; ground truth là GEOMREF dùng mọi điểm. IPPE+HO chính xác nhất [Tab. 11]. Khi chỉ dùng điểm trong cửa sổ bán kính r, IPPE+HO thua nhẹ RPP-SP ở r = 5,22 mm (n̄ = 4,64) và bám sát GEOMREF từ r ≥ 10,4 mm [§5.1, tr. 25–26; Fig. 8]. (ii) Bàn cờ: 20 ảnh 720p với 628 góc mỗi ảnh, cộng 20 ảnh của Matlab Calibration Toolbox. IPPE+HO và RPP-SP gần như trùng GEOMREF [§5.2; Fig. 10–11]. (iii) 300 marker ArUco, 30 khung ở cự ly trung bình 52,1 cm và 30 khung ở 102,2 cm, bốn góc mỗi marker. IPPE, RPnP, RPP-SP gần như nhau, còn HDZh và EPnP kém hẳn, nhất là ở cự ly vừa [§5.3, tr. 26–27; Fig. 13].
- [Đ] Thời gian, đo bằng Matlab 2012a trên Intel i7-3820, 500 cấu hình mỗi n, cài đặt IPPE do tác giả tự viết [§5.4, tr. 27; Tab. 12]. Ở n = 4: IPPE+HO 0,150 ms, HDZh+DLT 0,261 ms, RPnP 0,940 ms, EPnP 1,012 ms, RPP-SP 11,101 ms. Ở n = 500, IPPE chậm hơn khoảng 1,5 lần so với ở n = 6.
- [T] Ở điều kiện weak-perspective, nghiệm PHD duy nhất "far from the true solution about 50% of the time" [tr. 2]. Bài không có thí nghiệm riêng đo con số này.

## 6. Đóng góp thật sự (thường nhỏ hơn abstract)

Theo tôi, đóng góp có giá trị lâu dài là **phần phân tích**: sáu câu hỏi Q1–Q6 [tr. 3] được trả lời bằng định lý có chứng minh. Pose phẳng suy từ thông tin bậc nhất tại một điểm có đúng một translation và một hoặc hai xoay. Hai xoay này liên hệ với nhau bằng phép phản xạ qua mặt phẳng vuông góc tia nhìn, và chỉ trùng nhau khi target vuông góc tia nhìn. Nhờ vậy "tính hai nghiệm" của target phẳng trở thành một mệnh đề đóng, dạng giới hạn của P3P (tôi suy ra, đánh giá). Về mặt thuật toán, IPPE là một bước phân rã homography tốt hơn Zhang/Sturm: không trả thêm chi phí (chỉ một SVD 2×2) và không hỏng khi homography gần affine. Tuyên bố "vượt PnP trong đa số trường hợp" có điều kiện rõ ràng: n ≥ 6 với điểm ngẫu nhiên, hoặc có bốn góc, và so với các cài đặt Matlab năm 2012 [§4.5]. Câu kết "không có lý do tốt để dùng phương pháp khác" [tr. 32] mạnh hơn bằng chứng mà bài đưa ra.

## 7. Kiểm chứng của người ghi chú — script trong `code/`, lệnh chạy, kết quả thật

Lệnh, chạy từ gốc repo, mất khoảng 9 s:

```
python3 VSLAM/pnp/code/collins2014ippe_check.py
```

Script cài lại Algorithm 1 và 2 từ các eq. (14), (22)–(24), (28), (36). Homography có hai lựa chọn: DLT chuẩn hoá, hoặc Harker–O'Leary chép lại từ `HomographyHO::homographyHO` trong `opencv/modules/calib3d/src/ippe.cpp` (nhánh 4.x). Script so với `cv2.solvePnPGeneric(..., flags=cv2.SOLVEPNP_IPPE)` của cv2 5.0.0. Kết quả thật, đã cắt bớt:

```
== C1: Jacobian eq. (14) tại u0 != 0 ==
  u0=[0. 0.]: sai số tương đối  eq.(14) như in = 7.53e-09 | đổi ux<->uy = 7.53e-09
  u0=[ 60. -25.]: sai số tương đối  eq.(14) như in = 5.58e-02 | đổi ux<->uy = 1.28e-08
  u0=[-80.  50.]: sai số tương đối  eq.(14) như in = 8.13e-02 | đổi ux<->uy = 1.74e-09
[PASS] C1a eq.(14) đúng tại u0=0 (dạng Algorithm 2 dùng)
[PASS] C1b eq.(14) như in SAI tại u0!=0; bản đổi ux<->uy mới khớp sai phân
== C2: Algorithm 1+2, không nhiễu ==
  200 cảnh: max sai số xoay nghiệm đúng = 1.71e-06 deg, max sai số t tương đối = 4.38e-14, max |gamma*Z_centroid - 1| = 2.00e-15
  sigma_1(A) = 1.000000e-03;  biểu thức eq.(22) = 1.000000e-06 = sigma_1^2 ? 2.1e-16;  1/Z_centroid = 1.000000e-03
[PASS] C2b biểu thức đóng trong eq.(22) cho sigma_1^2 (phải lấy căn) — lỗi in
== C3: quan hệ giữa hai nghiệm (Theorem 4, eq. (27)-(28)), dữ liệu CÓ nhiễu sigma=1px ==
  max|R2 - M R1 diag(1,1,-1)| = 2.07e-14;  max ||x0_1 - x0_2||/||x0|| (eq.28) = 1.32e-16
  max |angle(R1,R2) - 2*alpha| = 1.46e-12 deg;  max lệch điểm 3D so với phản xạ = 3.98e-15
== C4 ==
  tilt=0 so với tia nhìn tại pixel (520,100): angle(R1,R2) = 4.83e-06 deg
  mặt phẳng song song mặt ảnh (vuông góc TRỤC QUANG), tâm ở pixel (520,100): angle(R1,R2) = 33.94 deg
  300 cảnh front-facing: số ca det(J)<0 = 0; mọi ca det(J)>0 đều có cả hai nghiệm front-facing = True
  H = [H13 H23 1]^T [H31 H32 1] (không đối xứng): |J(0)| = 0.0e+00
== C5: đối chiếu cv2.solvePnPGeneric(SOLVEPNP_IPPE) (cv2 5.0.0) ==
  300 bài (n=4..29, sigma=1px, u0 = trọng tâm):
   góc lệch xoay cv2 vs Algorithm 1 + DLT chuẩn hoá : median 1.22e-02, max 1.37e+00 deg
   góc lệch xoay cv2 vs Algorithm 1 + Harker-O'Leary: median 0.00e+00, max 1.71e-06 deg
   lệch t tương đối (HO): vs t eq.(28) median 3.27e-03 max 3.10e-01 | vs t eq.(36) median 1.54e-15 max 1.66e-13
   cv2 reprojectionError = RMSE_pixel/sqrt(2) (RMS mỗi toạ độ)? max chênh = 3.11e-14
   trên đầu ra cv2: max|R2 D R1^T - (R2 D R1^T)^T| = 4.00e-10; max|R2 D R1^T - (I - 2 l l^T)| ... = 2.16e-10
== C6: Theorem 6 — P3P trên 3 điểm ảo tách nhau eps quanh trọng tâm ==
  eps= 100.0: P3P trả 2 nghiệm; khoảng cách tới R1_IPPE = 5.450e+00 deg, tới R2_IPPE = 2.513e+00 deg
  eps=  10.0: P3P trả 2 nghiệm; khoảng cách tới R1_IPPE = 5.787e-01 deg, tới R2_IPPE = 2.096e-01 deg
  eps=   0.1: P3P trả 2 nghiệm; khoảng cách tới R1_IPPE = 5.818e-03 deg, tới R2_IPPE = 2.056e-03 deg
== C7: tỉ số rho = e_sai/e_đúng (RMSE px, cv2 IPPE) — median, p10, tỉ lệ chọn nhầm ==
  (sigma=1.0px, n=4 góc vuông, mặc định: Z=1000, tilt=20deg, tâm ảnh, 300 lần/ô; cạnh ảnh ~ f*w/Z)
     w= 400 (~  320px): rho median    27.91  p10   16.53  chọn nhầm   0.0%
     w= 200 (~  160px): rho median     8.04  p10    4.73  chọn nhầm   0.0%
     w= 100 (~   80px): rho median     2.40  p10    1.33  chọn nhầm  11.0%
     w=  50 (~   40px): rho median     1.40  p10    1.09  chọn nhầm  42.0%
     w=  25 (~   20px): rho median     1.13  p10    1.03  chọn nhầm  51.0%
     Z=  400 (~  200px): rho median    13.70  p10    6.99  chọn nhầm   0.0%
     Z= 1600 (~   50px): rho median     1.65  p10    1.12  chọn nhầm  29.3%
     Z= 3200 (~   25px): rho median     1.16  p10    1.03  chọn nhầm  50.7%
     tilt= 60deg: rho median     4.49  p10    2.46  chọn nhầm   1.0%
     tilt= 20deg: rho median     2.51  p10    1.30  chọn nhầm   9.7%
     tilt= 10deg: rho median     1.78  p10    1.12  chọn nhầm  29.3%
     tilt=  2deg: rho median     1.75  p10    1.13  chọn nhầm  42.0%
     pixel (320, 240): rho median     2.43  p10    1.23  chọn nhầm  11.0%
     pixel (520, 240): rho median     2.44  p10    1.22  chọn nhầm   9.3%
     pixel (620, 460): rho median     2.45  p10    1.37  chọn nhầm   8.7%
     n=  4: rho median     2.53  p10    1.35  chọn nhầm  10.3%  median n(e2^2-e1^2)/sigma^2 =     6.7
     n=  8: rho median     1.41  p10    1.11  chọn nhầm   3.3%  median n(e2^2-e1^2)/sigma^2 =     9.5
     n= 16: rho median     1.24  p10    1.07  chọn nhầm   4.0%  median n(e2^2-e1^2)/sigma^2 =    13.6
     n= 64: rho median     1.12  p10    1.06  chọn nhầm   0.3%  median n(e2^2-e1^2)/sigma^2 =    31.0
== C8: mô phỏng theo §4.1 của bài (4 góc + điểm đều, sigma_I=1px, n=6, ...) ==
  w=400: rho median   18.96 | chọn nhầm   0.0% | RE Mode 2 median  0.52 deg | RE e-nhỏ-nhất median  0.52, mean  0.82 deg
  w=200: rho median    5.47 | chọn nhầm   1.2% | RE Mode 2 median  1.07 deg | RE e-nhỏ-nhất median  1.08, mean  1.67 deg
  w=100: rho median    1.93 | chọn nhầm   9.8% | RE Mode 2 median  1.93 deg | RE e-nhỏ-nhất median  2.03, mean  7.00 deg
  w= 50: rho median    1.16 | chọn nhầm  26.5% | RE Mode 2 median  3.24 deg | RE e-nhỏ-nhất median  4.32, mean 22.76 deg
Tổng: 14/14 PASS
```

**Đọc kết quả.**
- [M] Lõi toán học của bài đúng: không nhiễu thì một nghiệm trùng pose thật (C2), và γ đúng là nghịch đảo độ sâu của trọng tâm. Quan hệ "phản xạ qua mặt phẳng vuông góc tia nhìn" đúng **chính xác đến sai số làm tròn, cả khi có nhiễu và dưới chiếu phối cảnh đầy đủ** (C3). Lý do là nó được xây sẵn vào lời giải, chứ không phải một xấp xỉ. Góc giữa hai xoay đúng bằng 2α.
- [M] OpenCV `SOLVEPNP_IPPE` là đúng Algorithm 1 cộng homography HO cộng translation theo eq. (36) (C5a, C5b), không phải eq. (28). Vì vậy **hai translation của OpenCV khác nhau một chút** (trung vị 0,33%, tối đa 31% so với eq. (28) trên 300 bài). Mọi mô tả kiểu "hai nghiệm có cùng vị trí tâm" chỉ đúng với eq. (28). Chọn DLT thay cho HO làm xoay lệch trung vị 0,012°, tối đa 1,37°. `reprojectionError` mà cv2 trả về là RMS trên mỗi toạ độ, tức RMSE điểm chia √2 (C5d).
- [M] Theorem 6 đứng vững trên số (C6): P3P trên ba điểm ảo tách nhau ε cho **hai** nghiệm, và cả hai hội tụ tuyến tính theo ε về hai nghiệm IPPE. Khoảng cách giảm 10 lần mỗi khi ε giảm 10 lần.
- [M] Tỉ số ρ = e_sai/e_đúng co về 1 khi target nhỏ đi trên ảnh, dù do kích thước thật hay do khoảng cách. Hai trục này cho cùng đường cong theo số pixel: khoảng 80–100 px thì chọn nhầm 2–11%, khoảng 20–25 px thì chọn nhầm 51% (C7). Như vậy ở 20 px việc chọn nghiệm là tung đồng xu, khớp với câu "khoảng 50%" của bài [tr. 2] (bài nói câu đó cho PHD, còn đây là IPPE chọn theo sai số nhỏ nhất). Khi góc nghiêng so với tia nhìn giảm, tỉ lệ chọn nhầm tăng từ 1% (60°) lên 42% (2°). Nhưng ở góc nhỏ thì hai nghiệm cũng chỉ cách nhau 2α, nên chọn nhầm ít hại hơn. **Vị trí của target trong ảnh gần như không có ảnh hưởng khi góc nghiêng được đo so với tia nhìn** (11,0 / 9,3 / 8,7% nằm trong dao động thống kê của 300 lần thử).
- [M] Số điểm đồng phẳng: ρ **giảm** khi n tăng (trung vị 2,53 → 1,12). Lý do: với n = 4, homography khớp gần hết, nên e_đúng bị nhỏ giả tạo. Ngược lại, tỉ lệ chọn nhầm giảm mạnh (10,3% → 0,3%), và thống kê tỉ số likelihood n(e2² − e1²)/σ² tăng (6,7 → 31). Vậy ρ là **chỉ báo tồi và phụ thuộc n**. Đại lượng nên dùng là tỉ số likelihood, đúng như bài gợi ý [§3.4, tr. 11].
- [M] So với thiết lập của bài (C8): tôi theo §4.1 (f = 800, 640×480, d ~ U(400, 1600), nghiêng < 80°, 4 góc + 2 điểm đều, σ_I = 1 px, 400 mẫu mỗi w). Có ba khác biệt: không lọc Mode 1 bằng τ_a, n = 6 cố định, và dùng HO của OpenCV. Mức lỗi Mode 2 tăng từ 0,52° (w = 400) lên 3,24° (w = 50). Nếu chọn theo sai số nhỏ nhất mà không lọc mẫu mơ hồ, trung bình ở w = 50 vọt lên 22,8° vì 26,5% ca chọn nhầm. Điều này giải thích vì sao bài buộc phải tách Mode 1 và Mode 2. Bài không in bảng số cho E24–E29 [Fig. 5], nên tôi không so được con số cụ thể, chỉ so được xu hướng.

## 8. Chỗ tôi không tin

- **Ba lỗi in trong công thức lõi**, cả ba kiểm bằng số. (1) Eq. (14): u_x và u_y bị đổi chỗ ở số hạng bậc nhất của J (C1b). Lỗi này vô hại cho Algorithm 2 (u0 = 0) nhưng sai với ai muốn đặt u0 ở chỗ khác, mà §3.2 lại khuyến khích chuyện đó khi phối cảnh mạnh. (2) Eq. (22): biểu thức đóng cho σ1², không phải σ1 (C2b). (3) Chứng minh Theorem 5 [tr. 9] viết J = 0 ⇔ Ĥ = [Ĥ13 Ĥ23 1]ᵀ[Ĥ13 Ĥ23 1], tức một ma trận đối xứng. Điều kiện đúng là Ĥ = [Ĥ13 Ĥ23 1]ᵀ[Ĥ31 Ĥ32 1] (C4d). Kết luận "Ĥ hạng 1" vẫn đúng.
- **Điều kiện nghiệm duy nhất được phát biểu ba kiểu khác nhau.** Q5 nói mặt cầu tâm tại tâm chiếu [tr. 3]. Theorem 4 nói mặt cầu "centred at the optical axis" [tr. 9]. §3.6 nói mặt cầu "passing through the line-of-sight" [tr. 12]. Chỉ cách thứ nhất đúng: điều kiện là mặt phẳng vuông góc với tia nhìn tới u0 (C4a, C4b).
- **Mâu thuẫn trong mô tả thí nghiệm.** Tab. 8 xếp E6–E11 là n = 8→50 và E12–E17 là n = 4→10. Văn bản §4.5 [tr. 18] lại viết ngược ("6 for n = 4 → 10 (E6-E11)"). Chú thích Fig. 2–3 trộn cả hai: E8–E11 ghi n = 4→10 trong khi E6–E7 ghi 8→50. Tab. 3 ghi hàng σ_I từ 0 đến 3,79, còn Tab. 2 nói E1 quét 0→6. Tab. 4 (E2 quét n) có cột tên "σ_I" với các giá trị không nguyên 5; 8,68; 14,2. Người đọc không thể biết chắc mỗi đồ thị ứng với điều kiện nào.
- **"In §3.4 we have shown that pose is ambiguous iff an affine homography can model the transformation"** [tr. 14]. §3.4 không chứng minh điều đó. Nó chỉ chứng minh (Lemma 3) rằng khi không nhiễu thì luôn phân xử được. Tiêu chí τ_a = 5 là heuristic và còn dùng H_p dựng từ ground truth. Bài cũng không báo bao nhiêu mẫu bị loại, nên con số Mode 1 thiên về các ca dễ.
- **Mode 2 chấm nghiệm gần ground truth nhất** [§4.1, tr. 13]. Cách chấm này thưởng cho việc trả nhiều nghiệm, và không đo được điều người dùng thật sự cần là chọn đúng nghiệm. C8 cho thấy khoảng cách giữa hai cách chấm ở w = 50 rất lớn (trung bình 3,24° so với 22,8°).
- **Tốc độ đo bằng Matlab**, và cài đặt IPPE là của chính tác giả, còn các baseline dùng mã của tác giả gốc [§5.4, tr. 27]. Các tỉ lệ 6,7× và 75× vì vậy phụ thuộc chất lượng cài đặt. Ngay trong bài cũng có hai con số khác nhau: "50 and 70 times faster than RPP-SP" [tr. 26] và "approximately 75 times" [tr. 27].
- **"99.6% of samples have a rotation error less than 10%"** [tr. 26]: sai số xoay tính bằng độ ở mọi chỗ khác, nên đơn vị "%" ở đây vô nghĩa hoặc là lỗi.
- **"IPPE does not involve any linearisation"** [tr. 2] đúng theo nghĩa hẹp. Nhưng việc chỉ dùng thông tin bậc 0 và 1 tại một điểm là một lựa chọn bỏ thông tin. Nghiệm thứ hai của IPPE là nghiệm thứ hai của bài toán cục bộ, **không phải** cực tiểu địa phương thứ hai của sai số tái chiếu, và bài không nói hai thứ này gần nhau đến đâu (tôi suy ra).

## 9. Chỗ tôi chưa hiểu (→ `99-chua-biet.md`)

- Lemma 2 nói khi phối cảnh nhỏ thì việc tìm u0 là bài toán bậc hai lồi [tr. 8; App. C, eq. (45)–(46)]. Nhưng Algorithm 2 luôn dùng trọng tâm. Khi phối cảnh lớn (target to, nghiêng mạnh), u0 tối ưu lệch khỏi trọng tâm bao nhiêu, và dời u0 có cải thiện đo được không? Bài không đo.
- Vì sao HO tốt hơn DLT cho IPPE mà DLT lại tốt nhất cho PHD [§4.4, tr. 15]? Bài chỉ báo kết quả, không giải thích.
- Nghiệm thứ hai của IPPE (phản xạ chính xác) liên hệ thế nào với cực tiểu thứ hai của RPP-SP `schweighofer2006planar`? Sau tinh chỉnh LM, nghiệm thứ hai của IPPE có hội tụ về cực tiểu đó không, và nó dịch đi bao xa khi target lớn trên ảnh?
- Lemma 4 cho phép trường hợp det(J) < 0, khi đó không nghiệm nào front-facing. Với dữ liệu có nhiễu thì trường hợp này xảy ra khi nào? Trong 300 cảnh của tôi (σ = 0,5 px, nghiêng tới 85°) nó không xảy ra lần nào. Nếu nó xảy ra, OpenCV trả gì?

## 10. Quan hệ với các bài khác trong `refs.bib`

- **`schweighofer2006planar`** (RPP-SP, [34] của bài): tìm nghiệm thứ hai như một cực tiểu địa phương theo một xoay 1 bậc tự do, qua đa thức bậc 4 [tr. 5]. IPPE thay cách đó bằng lời giải đóng có đặc trưng hình học. Nó thắng về xoay khi n ≥ 6, ngang về translation, và nhanh hơn 50–75 lần theo bài [§4.5; Tab. 12].
- **`lu2000orthogonal`** ([28]), **`lepetit2009epnp`** ([23]; lưu ý §4.5 [tr. 18] trích nhầm EPnP thành "[34]"), **`li2012rpnp`** ([24]), **`hesch2011dls`** ([18]) là các baseline PnP. **`oberkampf1996coplanar`** ([30]) và Horaud và cộng sự ([20], không có trong `refs.bib`) cũng có hai nghiệm ở mỗi vòng lặp. Bài nói IPPE dùng camera weak-perspective hoặc para-perspective cho đúng vòng lặp đầu của hai phương pháp này [§2.2, tr. 5; App. A].
- **`sturm2000plane`** ([35]) và Zhang 2000 ([40], không có trong `refs.bib`) là hai phương pháp PHD mà IPPE thay thế [§2.1.1].
- **`gao2003p3p`**: đây là bộ P3P ([12], trùng lặp với [11] trong danh mục tham khảo của bài) được dùng cho P3P trên điểm ảo [§4.6]. Theorem 6 nối IPPE với lý thuyết P3P.
- **So với cây `marker/A-nguyen-ly-va-toan-hoc/04-pose-ambiguity-target-phang/`** (đọc, không sửa). Bài này **thêm** hoặc **bất đồng** ở các điểm sau:
  1. *Đồng ý và làm chặt hơn.* Chương marker nói pháp tuyến nghiệm thứ hai là ảnh phản xạ của pháp tuyến thật qua đường nhìn tới tâm tag, rằng hai nghiệm cách nhau 2α, và rằng vị trí tâm giống nhau "tới xấp xỉ bậc nhất" (dẫn `schweighofer2006robust` §III, key của cây marker; ở `refs.bib` này là `schweighofer2006planar`). IPPE cho cả ba điều **dưới dạng đẳng thức**: R2 = M R1 D, góc đúng 2α, trọng tâm trùng nhau theo eq. (28). C3 kiểm các đẳng thức này đến 10⁻¹².
  2. *Bất đồng về chữ "xấp xỉ".* Chương marker viết quan hệ gương "đúng chính xác trong giới hạn chiếu trực giao và là xấp xỉ … dưới chiếu phối cảnh" (dòng 237 của `.tex`). Với cặp nghiệm IPPE, quan hệ này đúng chính xác cả dưới phối cảnh. Điều còn là xấp xỉ là việc cặp đó trùng với **hai cực tiểu của sai số tái chiếu**, và cả hai nguồn đều chưa định lượng điều này. Hai mệnh đề đang nói về hai đối tượng khác nhau, và chương marker nên nói rõ mình nói về đối tượng nào.
  3. *Translation.* Nếu dùng OpenCV (eq. (36)), hai nghiệm **không** cùng tâm: lệch trung vị 0,33%, tối đa 31% trong C5. Triệu chứng "vị trí đứng yên, góc nhảy" chỉ gần đúng.
  4. *"Tag ở tâm ảnh làm ambiguity nặng hơn"* (chương marker §4). Theo IPPE, đại lượng quyết định là góc nghiêng **so với tia nhìn**. Khi giữ góc đó cố định, vị trí trong ảnh không có ảnh hưởng (C7: 11,0 / 9,3 / 8,7%). Hiệu ứng mà chương marker mô tả chỉ có thật theo nghĩa: một tag song song mặt ảnh nhưng nằm lệch tâm thì *có* góc nghiêng so với tia nhìn (C4b: hai nghiệm cách nhau 33,9°). Nên viết lại theo tia nhìn.
  5. *Bất đồng rõ nhất: "thêm điểm đồng phẳng không cải thiện; tỉ số ρ gần như không đổi"* (chương marker §3, dòng 132, và câu tự kiểm ở dòng 334). C7 cho kết quả ngược lại ở cả hai vế. ρ **giảm** theo n (2,53 → 1,12), còn tỉ lệ chọn nhầm **giảm** từ 10,3% xuống 0,3% (n = 4 → 64, w ≈ 80 px, nghiêng 20°, σ = 1 px). Thêm điểm không phá được đối xứng, nhưng làm hai nghiệm **phân biệt được về mặt thống kê**, vì log-likelihood ratio tăng xấp xỉ tuyến tính theo n. ρ là thước đo sai cho việc này. IPPE [§3.4, tr. 11] đề xuất likelihood ratio test, không đề xuất ρ.
  6. *Sai định vị.* Chương marker dẫn "collins2014ippe §6" cho việc dùng tỉ số sai số tái chiếu làm chỉ báo tin cậy. §6 là phần kết luận và không bàn chuyện này. Chỗ đúng là §3.4 [tr. 10–11], và ở đó bài chỉ nói trả cả hai sai số, không định nghĩa ρ.

## 11. Nó đổi gì trong suy nghĩ

Trước khi đọc, tôi coi "hai nghiệm của target phẳng" là một hiện tượng số học của hàm mất mát. Sau khi đọc, tôi thấy nó là cấu trúc của bài toán cục bộ: đúng một translation, xoay có hai nhánh ±b, và hai nhánh là ảnh gương chính xác qua tia nhìn. Hai hệ quả thực dụng: (i) tham số hoá góc nghiêng phải đo **so với tia nhìn tới tâm target**, không so với trục quang; (ii) để phân xử hai nghiệm, dùng tỉ số likelihood có tính đến n và σ, đừng dùng tỉ số RMSE. Một bài học phụ: bài IJCV được trích nhiều vẫn có lỗi in trong đúng công thức lõi, nên cần cài lại theo mã (OpenCV `ippe.cpp`) và kiểm, không chép công thức từ PDF.

## 12. Câu hỏi tự kiểm

1. Vì sao γ phải là giá trị kỳ dị **lớn nhất** của A, và cách chọn đó hỏng ở đâu nếu J hạng 1 (mặt phẳng nhìn gần tiếp tuyến)?
2. Vì sao mặt phẳng song song mặt ảnh nhưng nằm ở góc ảnh vẫn có hai nghiệm IPPE, còn mặt phẳng nghiêng 30° so với trục quang lại có thể có một nghiệm duy nhất?
3. Khi nào tỉ số ρ = e2/e1 đánh lừa, tức ρ nhỏ mà vẫn phân xử được, hoặc ρ lớn giả tạo? (Gợi ý: n = 4 với homography khớp đúng.)
4. Vì sao đặt u0 ở trọng tâm lại tốt hơn đặt ba điểm ảo P3P ở góc hộp bao, và lập luận này hỏng khi nào (Theorem 2 cần số hạng phối cảnh nhỏ)?
5. Nếu dùng translation theo eq. (36) thay cho eq. (28), mệnh đề "hai nghiệm cùng vị trí tâm" còn đúng không, và điều đó ảnh hưởng thế nào tới một bộ lọc theo dõi marker?

## Trích đoạn nguyên văn làm bằng chứng

- "the single PHD solution can be far from the true solution about 50% of the time" [tr. 2]
- "a reflection of the plane about a single viewing ray." [tr. 3]
- "When the plane is tangential to a 3D sphere centred at the camera's" [tr. 3]
- "R has a unique solution iff the model plane in camera coordinates is tangential to a sphere centred at the optical axis." [tr. 9]
- "The combined effect is a two-fold solution corresponding to a reflection of the model plane about a plane whose normal (in camera coordinates) points along" [tr. 10]
- "Instead we return both solutions with their reprojection errors, and leave it up to the end application to choose whether to reject the alternative hypothesis." [tr. 11]
- "In §3.4 we have shown that pose is ambiguous iff an affine homography can model the transformation" [tr. 14]
- "there really is no good reason to use another method over IPPE." [tr. 32]
