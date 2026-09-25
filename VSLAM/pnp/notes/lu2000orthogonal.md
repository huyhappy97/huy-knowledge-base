# Fast and Globally Convergent Pose Estimation from Video Images (orthogonal iteration, LHM) — ghi chú đọc

| | |
|---|---|
| bibkey | `lu2000orthogonal` |
| Venue, năm | IEEE T-PAMI 22(6), tr. 610–622, 06/2000 (khớp `refs.bib`; bản PDF in số trang tạp chí 610–622) |
| Bản đã đọc | `papers/lu2000orthogonal.pdf` — nguồn: http://computableplant.ics.uci.edu/papers/2000/LuHagerMjolsness.pdf (theo `papers/fetch.sh`), 13 trang. Đây là bản dàn trang của IEEE (metadata "IEEE Copyright"), không phải bản thảo tác giả. `tr. N` = trang PDF, tức trang tạp chí 609 + N |
| Mức đọc | lượt 3 cho §2.1, §3.1–3.4 (dựng lại (17)–(33) và Phụ lục A–B); lượt 2 cho §3.5, §4, §5 |
| Người đọc | Claude (agent), 2026-09-25 — **Huy chưa đọc lại để ký** |
| Mức tin | giữ A cho thuật toán và định lý đơn điệu, nhưng có bốn chỗ **không được chép nguyên văn**: eq. (16) (ra chuyển vị), bước (31) (không suy ra được như viết), Phụ lục A (thiếu trường hợp hạng thiếu, đúng là trường hợp target phẳng), và các số trong Fig. 3–8 và 15–16 (không khớp với Fig. 11–12 của chính bài) — xem mục 8 |
| Kiểm chứng | (20), (21), (29)→(33) và tính đơn điệu: cửa (a) và (b). (16): cửa (b), xác nhận lỗi quy ước. "Hội tụ toàn cục" nghĩa là gì: cửa (a), đối chiếu với định lý Zangwill mà bài dẫn từ [39] Luenberger (chưa mở Luenberger nên chưa tính là cửa (c)). Thí nghiệm C1 (Fig. 11–12): cửa (b), dựng lại khớp. Script `code/lu2000orthogonal_check.py`, kết quả ở mục 7 |

## 1. Bài toán gốc và bối cảnh

Bài giải PnP có hiệu chỉnh với n ≥ 3 điểm không thẳng hàng [§2.1, tr. 2]. Năm 2000 có hai lối chính, và tác giả chê cả hai. Lối thứ nhất là tối ưu phi tuyến trên sai số tái chiếu, eq. (8), bằng Gauss–Newton hoặc Levenberg–Marquardt với xoay tham số hoá bằng góc Euler [§2.2, tr. 3]. Lối này chính xác nhưng cần khởi tạo tốt: bài dẫn [29] (Haralick–Shapiro) rằng Gauss–Newton chỉ chạy được khi khởi tạo lệch không quá 10% về tỉ lệ translation và 15° mỗi góc xoay [tr. 3], và nói rằng không có bảo đảm hội tụ [§1, tr. 1]. Lối thứ hai là các phương pháp xấp xỉ: nới ràng buộc trực giao, hoặc lặp trên mô hình camera đơn giản hoá (POSIT `dementhon1995posit`, Horaud và cộng sự [26], không có trong `refs.bib`). Các phương pháp này tính xoay theo hai bước, "giải tuyến tính rồi chiếu về ma trận trực giao gần nhất", và tác giả dẫn [27] (Horn–Hilden–Negahdaripour) để nói rằng làm vậy không cho ma trận trực giao tốt nhất [§1, tr. 1].

Động lực trực tiếp là thuật toán của Haralick và cộng sự [28] (`haralick1989pose`). Thuật toán này ước lượng đồng thời pose và độ sâu từng điểm, nên khử được phi tuyến phối cảnh và "có vẻ" hội tụ toàn cục, nhưng cần hàng trăm vòng lặp [§1, tr. 1]. Chỗ khó mà bài nhắm vào là giữ ưu điểm "biến phụ khử phối cảnh" của [28] nhưng làm mỗi vòng lặp là một bài toán có nghiệm đóng và tối ưu trên SO(3).

## 2. Giả thiết — kể cả giả thiết ngầm; bỏ đi thì hỏng ở đâu

- **Nội tham số và méo đã biết**; mọi thứ làm trên mặt ảnh chuẩn hoá z = 1 [chú thích 1, tr. 2]. Nếu K sai thì V̂_i sai theo và bài không nói gì thêm.
- **n ≥ 3 điểm không thẳng hàng** [§2.1, tr. 2]. Để (20) xác định, I − (1/n)ΣV̂_i phải xác định dương; điều này đúng trừ khi mọi v_i song song, tức mọi điểm chiếu về một điểm ảnh [eq. (21), tr. 5]. Tôi kiểm được (C0).
- **Nhiễu ảnh đẳng hướng, đồng nhất**, nhưng hàm mục tiêu lại đo trong không gian vật. Bài thừa nhận hàm (19) ngầm cho điểm xa camera trọng số lớn hơn, vì sai số không gian vật tỉ lệ với độ sâu [§3.5, tr. 7]. Như vậy OI **không** là ước lượng hợp lý cực đại dưới nhiễu pixel Gauss. Tác giả đề xuất trọng số 1/d_i² [eq. (45)–(46), tr. 7] nhưng không chứng minh hội tụ cho phiên bản có trọng số, và không đo nó.
- **Nghiệm AO duy nhất.** Chứng minh giảm ngặt (33) dựa trên việc nghiệm của (25) là duy nhất [tr. 6], và Phụ lục A chứng minh điều đó [tr. 12]. Chứng minh này bỏ sót trường hợp M có giá trị kỳ dị bằng 0; khi đó cột tương ứng của U và V chọn độc lập được, nên VUᵗ không duy nhất (tôi suy ra). Với target phẳng thì p'_i nằm trong một mặt phẳng, M luôn có hạng ≤ 2, nên trường hợp bị bỏ sót lại chính là trường hợp phẳng. Muốn có nghiệm duy nhất trong SO(3) thì phải thêm hệ số sửa det = ±1 (kiểu Umeyama), mà (16) không có.
- **Giả thiết ngầm: "SO(3)" trong chứng minh thực ra là O(3).** Bài định nghĩa SO(3) là "the set of 3 × 3 orthogonal matrices" [tr. 5], và công thức (16) không chặn det = −1. Tính compact vẫn đúng với O(3), nhưng không có sửa det thì OI có thể trả về một phép phản xạ (tôi suy ra).
- **Giả thiết ngầm về cheirality.** Hàm E trong (19) không biết điểm ở trước hay sau camera, vì (I − V̂_i)q và (I − V̂_i)(−q) có cùng chuẩn. Với target phẳng z = 0, mỗi nghiệm (R, t) có một "song sinh" (−RS, −t), với S = diag(1, 1, −1), là một phép xoay thật (det = +1) cho E **bằng hệt** nhưng đặt vật sau camera (tôi suy ra, C0 kiểm). Bài chỉ nói ràng buộc duy nhất cần cho R^(0) là không đặt vật sau camera [tr. 6]. Kiểm chứng của tôi cho thấy ràng buộc đó không đủ (mục 7, C2).

## 3. Cơ chế — năm câu, rồi chi tiết có định vị

**Năm câu.** Thay vì đo độ lệch trên ảnh, bài đo khoảng cách từ điểm camera q_i = Rp_i + t tới tia nhìn qua điểm ảnh quan sát được. Khoảng cách đó bằng ‖(I − V̂_i)q_i‖, với V̂_i = v̂v̂ᵗ/(v̂ᵗv̂) là phép chiếu trực giao lên tia [eq. (17)–(19)]. Hàm này bậc hai theo t, nên t tối ưu có dạng đóng t(R) [eq. (20)]. Còn lại một bài toán theo R, và bài giải nó bằng cách lặp: chiếu các điểm dự đoán hiện tại lên tia nhìn để được "điểm cảnh giả thuyết" V̂_i q_i^(k), rồi giải bài toán absolute orientation 3D–3D giữa p_i và các điểm đó bằng SVD [eq. (25)–(27)]. Mỗi vòng làm E giảm ngặt cho tới khi gặp một điểm bất động, và định lý hội tụ toàn cục Zangwill (Luenberger [39, ch. 6]) cho kết luận: từ **mọi** R^(0), mọi điểm tụ của dãy lặp là điểm bất động [§3.3]. Kết luận đó **không** nói điểm bất động là cực tiểu toàn cục; chính bài viết rằng nó không bảo đảm tìm được pose thật [tr. 5, tr. 6].

**Chi tiết.**
- *Hai dạng thẳng hàng* [eq. (4)–(6), tr. 3]: dạng không gian ảnh v_i = (Rp_i + t)/(r₃ᵗp_i + t_z), eq. (4), và dạng không gian vật Rp_i + t = V_i(Rp_i + t), eq. (5), với V_i = v_iv_iᵗ/(v_iᵗv_i), eq. (6). V_i đối xứng và lũy đẳng [eq. (7a)–(7c)].
- *AO* [eq. (10)–(16), tr. 4]: M = Σq'_ip'_iᵗ (13); R* = argmax tr(RᵗM) (14); t* = q̄ − R*p̄ (15); với UᵗMV = Σ thì R* = VUᵗ (16). **Công thức (16) sai quy ước so với (13).** Với M = Σq'p'ᵗ = UΣVᵗ thì tr(RᵗM) cực đại tại R = UVᵗ; VUᵗ là chuyển vị (tôi suy ra; C0 cho sai số 123° khi dùng (16) nguyên văn và 0° khi dùng chuyển vị).
- *Hàm mục tiêu* [eq. (19), tr. 4]: E(R, t) = Σ‖(I − V̂_i)(Rp_i + t)‖².
- *Translation tối ưu* [eq. (20), tr. 4]: t(R) = (1/n)(I − (1/n)ΣV̂_j)⁻¹ Σ(V̂_j − I)Rp_j. Tôi tự dẫn lại: đạo hàm theo t cho Σ(I − V̂_i)(Rp_i + t) = 0, vì (I − V̂)ᵗ(I − V̂) = I − V̂. C0 so với lstsq, sai khác 4·10⁻¹⁶.
- *Viết lại dạng AO* [eq. (22)–(24), tr. 5]: với q_i(R) = V̂_i(Rp_i + t(R)) thì E(R) = Σ‖Rp_i + t(R) − q_i(R)‖², giống (10), chỉ khác là M(R) phụ thuộc R. Đây là lý do phải lặp.
- *Vòng lặp* [eq. (25)–(27), tr. 5]: R^(k+1) = argmin_R Σ‖Rp_i + t − V̂_iq_i^(k)‖² (25), tương đương argmax tr(RᵗM(R^(k))) (26); sau đó t^(k+1) = t(R^(k+1)) (27). Nghiệm của OI được định nghĩa là điểm bất động của (25) [eq. (28)].
- *Khởi tạo* [§3.4, tr. 6–7]: lần AO đầu dùng chính v_i (các điểm ảnh coi như điểm 3D đồng phẳng) làm điểm cảnh giả thuyết. Xoay thu được trùng với xoay của weak perspective tối ưu (37)–(39); translation thì tính bằng (20). Các điều kiện (42)–(43) để hai translation gần nhau ứng đúng với điều kiện weak perspective đúng.
- *Hội tụ* [§3.3, tr. 5–6]: ba điều kiện của định lý Zangwill là (1) ánh xạ OI đóng, (2) dãy nằm trong một tập compact, và (3) E giảm ngặt ngoài tập nghiệm. Điều kiện (1): OI = G∘SVD∘F, trong đó F và G liên tục, còn SVD là ánh xạ điểm–tập đóng [Phụ lục B]. Điều kiện (2): SO(3) compact. Điều kiện (3): dẫn qua (29)–(33).

**Dựng lại bước (29)–(33) — chỗ bài viết hụt, và cách vá (tôi suy ra, cửa (a) + (b)).** Đẳng thức (29)–(30) đúng và thực chất là định lý Pythagoras: với q bất kỳ, q − V̂q^(k) = (I − V̂)q + V̂(q − q^(k)), và hai thành phần này trực giao. Do đó

  g_k(q) := Σ‖q_i − V̂_iq_i^(k)‖² = E(q) + Σ‖V̂_i(q_i − q_i^(k))‖² ≥ E(q),

với dấu bằng tại q = q^(k). Vậy g_k là một **hàm chặn trên (majorant)** của E, tiếp xúc E tại điểm lặp hiện tại, và OI chính là một thuật toán majorize–minimize (MM). Bước (31) của bài lại viết Σ‖q_i^(k+1) − V̂_iq_i^(k)‖² ≤ E(R^(k)) "theo (25) và (27)", với q^(k+1) dùng t^(k+1) = t(R^(k+1)). Suy luận này không đi được: (25) cực tiểu theo **cả** R và t, nên đạt cực tiểu tại t_AO = mean(V̂q^(k)) − R^(k+1)p̄, chứ không tại t(R^(k+1)). C1 cho thấy bất đẳng thức (31) như viết **sai ở 10519/24000 bước**, có bước vượt E(R^(k)) tới 1252%. Kết luận (33) vẫn đúng nhờ chuỗi E(R^(k+1), t(R^(k+1))) ≤ E(R^(k+1), t_AO) ≤ g_k(R^(k+1), t_AO) ≤ g_k(R^(k), t^(k)) = E(R^(k)). Bất đẳng thức đầu đúng vì t(R) tối ưu E theo t, bất đẳng thức thứ hai là tính majorant, bất đẳng thức thứ ba là (25). C1 kiểm chuỗi này: 0 vi phạm.

**"Globally convergent" nghĩa là gì, chính xác.** Theo chính §3.3, đó là tính chất *hội tụ từ mọi điểm đầu* của Zangwill: với mọi R^(0) ∈ SO(3), mọi dãy con hội tụ của {R^(k)} hội tụ về một điểm bất động của OI, và E(R^(k)) giảm đơn điệu [tr. 5–6]. Tôi rút ra ba điều (tôi suy ra). (i) Đây **không** phải tối ưu toàn cục. Bài tự nói "a solution does not necessarily correspond to the correct true pose" [tr. 5] và "global convergence does not guarantee that the true pose will always be recovered" [tr. 6]. (ii) Định lý Zangwill chỉ cho điểm tụ của dãy con, không cho cả dãy hội tụ. Câu của bài "a solution, or a fixed point, will eventually be reached" [tr. 6] vì vậy mạnh hơn điều đã chứng minh, dù trong thực nghiệm của tôi mọi lượt đều hội tụ (0 lượt chưa hội tụ trên 3000 lượt ở C2). (iii) Vì OI là MM với majorant tiếp xúc bậc nhất, mỗi điểm bất động là một điểm dừng (bậc nhất) của E trên SO(3) × R³. Tập "nghiệm" vì thế gồm mọi cực tiểu địa phương, và về lý thuyết cả điểm yên ngựa.

## 4. Ký hiệu của bài ↔ ký hiệu của khảo sát

| Bài | Khảo sát | Ghi chú |
|---|---|---|
| p_i = (x_i, y_i, z_i)ᵗ, hệ vật | X_w | "object-centered reference frame" [tr. 2] |
| q_i = Rp_i + t, eq. (1) | X_c = R X_w + t | cùng chiều biến đổi thế giới → camera; không cần đổi dấu |
| R (hàng r₁ᵗ, r₂ᵗ, r₃ᵗ), t = (t_x, t_y, t_z)ᵗ, eq. (2) | R, t | |
| v_i = (u_i, v_i, 1)ᵗ trên mặt ảnh chuẩn hoá z' = 1 | K⁻¹[u; 1] | bài dùng u_i, v_i cho toạ độ **chuẩn hoá**, không phải pixel; đừng nhầm với `u` (pixel) của khảo sát |
| v̂_i, û_i | quan sát có nhiễu | dấu mũ = quan sát |
| V_i = v_iv_iᵗ/(v_iᵗv_i), eq. (6) | f fᵗ, với f = tia chiếu đơn vị | V̂_i = f_if_iᵗ |
| M = Σq'_ip'_iᵗ, eq. (13) | — | quy ước này cho R = UVᵗ, **không** phải VUᵗ như (16) |
| E(R, t), eq. (19) | Σ‖(I − f_if_iᵗ)(R X_w,i + t)‖² | sai số không gian vật (object-space) |
| s (principal depth), eq. (34)–(40) | — | chỉ dùng cho khởi tạo weak perspective |
| SNR = −20 log(σ t_z/10) dB [tr. 8] | — | σ là độ lệch chuẩn nhiễu trên toạ độ **chuẩn hoá**; 10 là cạnh hộp vật |
| Xᵗ | Xᵀ | bài dùng mũ t cho chuyển vị |

## 5. Bằng chứng — dữ liệu, phần cứng, baseline, con số kèm điều kiện, số lần lặp

Mọi thí nghiệm đều là mô phỏng; bài nói có thử trên dữ liệu thật nhưng không báo số nào [§4, tr. 7]. Có hai bộ thí nghiệm.

**§4.1, phụ thuộc vị trí và khởi tạo** [tr. 8–10]. Vật là tám đỉnh hộp [−5, 5]³, với 1000 xoay đều cho mỗi translation và nhiễu SNR = 70 dB trên cả hai toạ độ ảnh [tr. 8]. D1 cố định t_x = t_y = 5 và cho t_z/10 chạy từ 1,5 đến 50; D2 cố định t_x = 5, t_z = 200 và cho t_y/10 chạy từ 1,5 đến 50 [tr. 8].
- [Đ] Số vòng lặp: khởi tạo weak perspective giảm từ khoảng 7 xuống khoảng 3 khi vật ra xa; khởi tạo xoay ngẫu nhiên nằm quanh 10 [Fig. 3, tr. 8]. Theo trục quang, khởi tạo weak perspective tăng từ khoảng 6 lên khoảng 11 [Fig. 6, tr. 9]. Các số này tôi đọc từ đồ thị, và bài không nêu tiêu chí dừng.
- [Đ] Sai số xoay khoảng 3° và gần như phẳng theo khoảng cách, cho cả hai kiểu khởi tạo [Fig. 4, 7]. Sai số translation tương đối khoảng 3% khi xa, tăng lên khoảng 15% ở t_z/10 = 1,5 [Fig. 5, tr. 9].
- [T] Tác giả diễn giải rằng thiên lệch do độ sâu chỉ đáng kể khi tỉ số khoảng cách / kích thước vật theo z < 3,5, và rằng xoay "gần như không bị ảnh hưởng" [§4.1.1, tr. 8]. Với khởi tạo ngẫu nhiên, sai số translation lệch trong khoảng 2% so với khởi tạo weak perspective [tr. 9]. Chỉ cần R^(0) không đặt vật sau camera thì OI "seems to be able to reach the true pose" [tr. 9–10].

**§4.2, so sánh** [tr. 10–11]. N điểm đều trong hộp [−5, 5]³, t_x, t_y ~ U[5, 15], t_z ~ U[20, 50]. Ngoại lai được tạo bằng cách thay điểm 3D bằng một điểm ngẫu nhiên trong hộp [tr. 10]. Có ba bài test, C1 (N = 20, SNR 30–70 dB), C2 (N = 20, SNR 60 dB, 5–25% ngoại lai) và C3 (SNR 50 dB, N = 10–50), mỗi mức 1000 lần [tr. 10–11]. Bài viết "four standard tests" nhưng chỉ liệt kê ba [tr. 10]. Baseline gồm một phương pháp tuyến tính [18] (DLT của Abdel-Aziz–Karara) và LM (LMDIF của MINPACK) khởi tạo từ **cùng** nghiệm đầu của OI [tr. 11].
- [Đ] C1: sai số xoay trung bình của OI khoảng 2,5° ở 30 dB, khoảng 1° ở 40 dB, khoảng 0,3° ở 50 dB, khoảng 0,05° ở 60 dB, khoảng 0,02° ở 70 dB; LM gần như trùng [Fig. 11]. Sai số translation của OI khoảng 0,55 → 0,19 → 0,06 → 0,02 → 0,008 [Fig. 12]. Bài không ghi đơn vị; kiểm chứng C6 của tôi cho thấy đây là ‖Δt‖ **tuyệt đối** theo đơn vị hộp.
- [Đ] C2: có ngoại lai thì OI tốt hơn LM ở cả xoay (đo bằng "quaternion error") lẫn translation [Fig. 13–14]. Chú giải của Fig. 13–14 đổi kiểu nét so với các hình khác (OI là nét đứt, LM là chấm gạch), nên đọc phải cẩn thận.
- [Đ] Thời gian trên SGI IRIS Indigo, MIPS R4400, SNR 60 dB, không ngoại lai: OI khoảng 0,02–0,05 s, LM khoảng 0,4–0,9 s cho N = 10–50 [Fig. 9]. Số vòng lặp: OI khoảng 15 → 10, LM khoảng 55 → 15 [Fig. 10, tr. 10].
- [T] Vì OI nhanh ngang LM khi cả hai được khởi tạo tốt, tác giả "tin rằng" OI có hội tụ cục bộ "quadratic-like" [tr. 11]. Đây chỉ là phỏng đoán, không có đo tốc độ hội tụ nào.

## 6. Đóng góp thật sự (thường nhỏ hơn abstract)

Đóng góp thật gồm ba phần. Thứ nhất là cách đặt PnP thành sai số không gian vật (19) cùng với t(R) dạng đóng (20), để bài toán chỉ còn theo R. Thứ hai là nhận xét rằng khi cố định các "điểm cảnh giả thuyết" V̂_iq_i^(k) thì bài toán theo R là AO có nghiệm SVD, nên mỗi vòng lặp cho xoay trực giao đúng mà không cần tham số hoá. Thứ ba là chứng minh E giảm đơn điệu. Tôi thấy phần thứ ba là một thuật toán MM trá hình, và chứng minh trong bài có một bước (31) phải vá (mục 3). "Globally convergent" trong nhan đề chỉ là hội tụ về *một* điểm dừng từ mọi điểm đầu, không phải về nghiệm tối ưu. Tuyên bố trong abstract rằng OI chống ngoại lai tốt hơn mọi phương pháp đã thử chỉ dựa trên C2 [Fig. 13–14], với chỉ một baseline không bền vững là LM. Cả OI lẫn LM đều là bình phương tối thiểu, nên lợi thế này, nếu có, đến từ cách đo sai số chứ không từ một cơ chế chống ngoại lai nào (tôi suy ra). Về độ chính xác, dựng lại C1 cho thấy OI khớp LM trong khoảng vài phần trăm (mục 7, C6), đúng như Fig. 11–12.

## 7. Kiểm chứng của người ghi chú — script trong `code/`, lệnh chạy, kết quả thật

Script: `code/lu2000orthogonal_check.py`. Nó dùng `common.py`, numpy và cv2 5.0.0, với seed cố định, và chạy hết 71 s. Tôi tự cài OI theo đúng (17)–(27), với hai điểm khác bài: xoay AO tính bằng R = U diag(1, 1, det) Vᵗ (tức (16) đã sửa chuyển vị và sửa det), và khởi tạo weak perspective theo §3.4. Lệnh chạy:

```
python3 VSLAM/pnp/code/lu2000orthogonal_check.py
```

Kết quả thật (cắt bớt dòng):

```
== C0: công thức cục bộ (20), (21), (16)
  t(R) eq.(20) vs lstsq: sai khác tương đối = 3.73e-16  -> PASS
  trị riêng của I - mean(V): [0.08848 0.94221 0.96932]  -> xác định dương PASS
  AO không nhiễu: sai số R theo (16) nghĩa đen = 123.12 deg; sai số R^t theo (16) = 0.00e+00 deg; U V^t (có sửa det) = 0.00e+00 deg
  target phẳng: E(R,t)=1.058143e+01, E(-RS,-t)=1.058143e+01, det(-RS)=+1 -> song sinh sau camera cùng E PASS
== C1: E giảm đơn điệu (33); bất đẳng thức (31); majorant
  400 lượt chạy (20 cảnh không phẳng + 20 phẳng, n=8, sigma=2px, R0 ngẫu nhiên), 24000 bước
  số bước E tăng: 0  -> đơn điệu PASS
  số bước (31) sai khi t^(k+1)=t(R^(k+1)) như (27): 10519 (vượt tối đa 1252.28% so với E(R^k))
  chuỗi thay thế E(R^k+1) <= E(R^k+1,t_AO) <= g <= E(R^k) vi phạm: 0  -> PASS
  majorant g >= E vi phạm: 0  -> PASS
== C2: hội tụ từ R0 ngẫu nhiên đều trên SO(3)
  [kiểu bài §4.2: N=20 trong hộp [-5,5]^3, tz 20-50, SNR 60dB] 20 cảnh x 30 R0 ngẫu nhiên = 600 lượt
    tới cực tiểu tốt nhất (trong các nghiệm vật-trước-camera): 301 (50.2%); điểm bất động khác vật trước camera: 18; vật sau camera: 281; chưa hội tụ (3000 bước): 0
    chỉ R0 mà (R0, t(R0)) đặt mọi điểm trước camera (điều kiện của bài [tr. 6]): 226 lượt -> tốt nhất 217 (96.0%), khác-trước-camera 8, sau camera 1
    cảnh có >=2 điểm bất động khác nhau vật trước camera: 3/20; ...
    SQPnP (cv2) cùng lưu vực (<0.05deg) với nghiệm tốt nhất: 20/20; E(SQPnP)/E_min - 1 trung vị 3.6e-04
    số bước (dừng khi ||dR||_F<1e-11): weak-persp trung vị 44, ...; weak-persp tới trong 0.01deg của điểm bất động: trung vị 13 bước
  [kiểu bài §4.2 nhưng N=6, SNR 50dB] 20 cảnh x 30 R0 ngẫu nhiên = 600 lượt
    tới cực tiểu tốt nhất (...): 227 (37.8%); điểm bất động khác vật trước camera: 68; vật sau camera: 305; ...
    chỉ R0 mà (R0, t(R0)) đặt mọi điểm trước camera (...): 242 lượt -> tốt nhất 192 (79.3%), khác-trước-camera 49, sau camera 1
    cảnh có >=2 điểm bất động khác nhau vật trước camera: 11/20; ...
    cảnh mà nghiệm tốt nhất (trước camera) cũng gần R thật nhất: 18/20; khởi tạo weak-persp tới nghiệm tốt nhất: 19/20
  [common.make_scene n=10, sâu 4-8, gốc vật xa trọng tâm, sigma=1px] 20 cảnh x 30 R0 ngẫu nhiên = 600 lượt
    chỉ R0 mà (...): 157 lượt -> tốt nhất 147 (93.6%), khác-trước-camera 1, sau camera 9
  [phẳng n=8, vuông 1m, cách 3m, nghiêng 40deg, sigma=1px] 20 cảnh x 30 R0 ngẫu nhiên = 600 lượt
    tới cực tiểu tốt nhất (...): 174 (29.0%); điểm bất động khác vật trước camera: 118; vật sau camera: 308; ...
    chỉ R0 mà (...): 246 lượt -> tốt nhất 152 (61.8%), khác-trước-camera 94, sau camera 0
    cảnh có >=2 điểm bất động khác nhau vật trước camera: 20/20; cảnh có điểm bất động sau camera với E NHỎ HƠN hẳn ...: 0/20
    cảnh mà nghiệm tốt nhất (trước camera) cũng gần R thật nhất: 17/20; khởi tạo weak-persp tới nghiệm tốt nhất: 17/20
    số bước (...): weak-persp trung vị 168, ...; weak-persp tới trong 0.01deg của điểm bất động: trung vị 65 bước
  [phẳng n=8, vuông 1m, cách 8m, nghiêng 40deg, sigma=1px] 20 cảnh x 30 R0 ngẫu nhiên = 600 lượt
    chỉ R0 mà (...): 280 lượt -> tốt nhất 152 (54.3%), khác-trước-camera 128, sau camera 0
    cảnh có >=2 điểm bất động khác nhau vật trước camera: 20/20; ...
    cảnh mà nghiệm tốt nhất (trước camera) cũng gần R thật nhất: 18/20; khởi tạo weak-persp tới nghiệm tốt nhất: 12/20
== C3: tốc độ hội tụ cục bộ (bài: 'quadratic-like' [tr. 11], chỉ là phỏng đoán)
  [không phẳng] tỉ số ||R_(k+1)-R*|| / ||R_k-R*|| gần nghiệm: trung vị 0.619, khoảng [0.447, 0.797] trên 20 cảnh -> hội tụ TUYẾN TÍNH
  [phẳng] tỉ số ||R_(k+1)-R*|| / ||R_k-R*|| gần nghiệm: trung vị 0.846, khoảng [0.782, 0.866] trên 9 cảnh -> hội tụ TUYẾN TÍNH
== C4: độ chính xác theo nhiễu pixel đẳng hướng (n=10, không phẳng, sâu 4-8, f=800, 200 lần/mức)
  sigma | trung vị sai số R (deg): OI  ITER  SQPNP  LM* | trung vị sai số t tương đối: OI  ITER  SQPNP  LM* | OI vs LM*: dR(deg) dt(rel)  RMSE_OI/RMSE_LM*
   0.5  |  0.0853 0.0835 0.0866 0.0835 | 0.00952 0.00930 0.00969 0.00930 | 0.0234 0.00270 1.0128
   1.0  |  0.1675 0.1655 0.1683 0.1655 | 0.01757 0.01656 0.01752 0.01656 | 0.0443 0.00494 1.0117
   2.0  |  0.3621 0.3609 0.3608 0.3609 | 0.03710 0.03629 0.03699 0.03629 | 0.1011 0.01039 1.0135
   5.0  |  0.8770 0.8468 0.8696 0.8114 | 0.09412 0.08914 0.09438 0.08728 | 0.2609 0.02972 1.0125
== C5: thiên lệch theo độ sâu (§3.5, kiểu D1: 8 đỉnh hộp [-5,5]^3, tx=ty=5, sigma=1.0px @ f=800, 200 lần/mức)
  tz/10 | SNR(dB) | TB sai số t tương đối (%): OI  LM* | TB sai số R (deg): OI  LM* | TB sai lệch t_z có dấu (%): OI  LM*
    1.5 |  54.5 |  0.090  0.076 | 0.1043 0.0863 | +0.005 +0.003
    3.5 |  47.2 |  0.184  0.182 | 0.2605 0.2502 | -0.002 -0.002
   20.0 |  32.0 |  0.987  0.990 | 1.4054 1.4083 | -0.016 +0.130
== C5: (như trên, sigma=5.0px)
    1.5 |  40.6 |  0.451  0.379 | 0.5217 0.4314 | +0.013 +0.013
    3.5 |  33.2 |  0.926  0.913 | 1.3024 1.2499 | -0.109 -0.013
   10.0 |  24.1 |  2.686  2.642 | 3.7404 3.7162 | -0.726 +0.228
   20.0 |  18.1 |  5.548  4.922 | 7.1342 7.1458 | -3.125 +0.516
== C6: dựng lại thí nghiệm C1 của bài [tr. 10-11] (N=20, PO=0, SNR 30-70dB), 200 lần/mức; so với Fig. 11-12
  SNR | TB sai số R (deg): OI  LM* | TB sai số t tương đối: OI  LM* | TB ||dt|| tuyệt đối (đơn vị hộp): OI  LM*
   30 | 2.2616 2.2078 | 0.01613 0.01390 | 0.6082 0.5343
   40 | 0.6728 0.6651 | 0.00438 0.00420 | 0.1659 0.1597
   50 | 0.2058 0.1999 | 0.00156 0.00154 | 0.0593 0.0587
   60 | 0.0656 0.0640 | 0.00043 0.00043 | 0.0167 0.0165
   70 | 0.0210 0.0205 | 0.00014 0.00014 | 0.0053 0.0052
Tổng thời gian: 71.3 s
```

*(LM\* = cực tiểu sai số tái chiếu: tinh chỉnh `solvePnPRefineLM` từ nghiệm của OI, ITERATIVE và SQPNP, rồi giữ nghiệm có RMSE nhỏ nhất; ở C5 và C6 chỉ tinh chỉnh từ OI. "Tốt nhất" ở C2 = điểm bất động có E nhỏ nhất trong số các nghiệm đặt mọi điểm trước camera.)*

Đọc kết quả [M]:
- **(1) Đơn điệu: khớp bài.** E không tăng ở bước nào trong 24000 bước, kể cả target phẳng và khởi tạo tệ. Nhưng bất đẳng thức trung gian (31) như viết thì sai ở 44% số bước; chứng minh đúng phải đi qua t_AO và majorant (mục 3).
- **(2) Hội tụ và tối ưu toàn cục: bài nói quá.** Với R^(0) đều trên SO(3), chỉ 26–50% số lượt tới nghiệm tốt nhất, và phần lớn số còn lại kết thúc ở điểm bất động đặt vật **sau** camera. Lọc theo đúng điều kiện của bài (R^(0), t(R^(0)) đặt vật trước camera), trong cấu hình giống §4.2 với N = 20 thì 96,0% tới nghiệm tốt nhất, gần với tuyên bố của bài [tr. 9–10]. Nhưng với N = 6 thì chỉ 79,3%, vì 11/20 cảnh có hai điểm bất động khác nhau đều đặt vật trước camera. Như vậy cực tiểu địa phương giả tồn tại cả với vật không phẳng khi ít điểm, trái với câu "few, if any, spurious local minima" [tr. 12]. Với target phẳng, 20/20 cảnh có hai điểm bất động trước camera, và OI rơi vào mỗi cái gần như ngẫu nhiên (54–62% tới nghiệm tốt nhất). Khởi tạo weak perspective chỉ chọn đúng nghiệm tốt nhất ở 12/20 cảnh khi target ở 8 m. Ngoài ra, với target phẳng mỗi cực tiểu còn có một song sinh sau camera cùng E (C0), nên "cực tiểu toàn cục của E" tự nó đã không duy nhất; phải thêm cheirality mới nói được "nghiệm tốt nhất". Tôi chưa gặp trường hợp nào điểm bất động sau camera có E nhỏ hẳn hơn nghiệm tốt nhất trước camera (0/20 ở mọi cấu hình).
- **Kiểm chéo bằng SQPnP.** SQPnP (`terzakis2020sqpnp`) rơi vào cùng lưu vực với nghiệm tốt nhất của OI ở 19–20/20 cảnh mỗi cấu hình. Nhưng nó **không** tối ưu đúng hàm (19): hàm của SQPnP là ‖1_zᵀ(RM_i + t)m_i − (RM_i + t)‖² [eq. (2), tr. 5 của `terzakis2020sqpnp`], tức khoảng cách tới điểm cùng độ sâu trên tia, không phải khoảng cách vuông góc tới tia. Vì vậy E(SQPnP) lớn hơn E_min cỡ 10⁻⁴ (tương đối). Đây là kiểm chéo về lưu vực, không phải chứng nhận tối ưu của E.
- **(3) Tốc độ: không khớp phỏng đoán của bài.** Gần nghiệm, OI hội tụ **tuyến tính**, với tỉ số co 0,45–0,80 khi vật không phẳng và 0,78–0,87 khi phẳng. Điều này đúng như dự đoán cho một thuật toán MM, và không phải "quadratic-like" [tr. 11]. Để tới trong 0,01° của điểm bất động từ khởi tạo weak perspective cần trung vị 13–18 vòng khi vật không phẳng và 63–65 vòng khi phẳng. Số này cùng cỡ với khoảng 10–15 vòng ở Fig. 10, nhưng nhiều hơn "five to 10 iterations" [tr. 2]; bài không nêu tiêu chí dừng nên không so chặt được.
- **(4) Object-space so với image-space dưới nhiễu pixel đẳng hướng.** Ở C4, nghiệm OI lệch khỏi nghiệm cực tiểu tái chiếu một góc trung vị khoảng 0,045° mỗi pixel nhiễu (0,023° ở 0,5 px, 0,26° ở 5 px), tức khoảng 1/4 sai số xoay thật; translation lệch khoảng 0,5% mỗi pixel. RMSE tái chiếu của OI lớn hơn cực tiểu khoảng 1,2–1,35% ở mọi mức nhiễu. Sai số so với ground truth của OI xấu hơn LM\* 0–8% (trung vị). OpenCV ITERATIVE trùng LM\* tới σ = 2 px nhưng xấu hơn ở 5 px, và SQPNP gần như trùng OI. Kết luận: OI **không** thay được bước tinh chỉnh tái chiếu nếu muốn ước lượng ML dưới nhiễu pixel, nhưng phần lệch nhỏ hơn nhiều so với sai số do nhiễu.
- **(5) Thiên lệch theo độ sâu (§3.5): không tái hiện được như bài mô tả.** Trong cấu hình kiểu D1 với σ = 1 px, ở t_z/10 = 1,5, sai số translation của OI lớn hơn LM\* khoảng 18% (0,090% so với 0,076%) và sai số **xoay** lớn hơn khoảng 21%. Từ 3,5 trở đi hai bên gần như bằng nhau, nên ngưỡng 3,5 ăn khớp. Nhưng xoay cũng bị ảnh hưởng, trái với [tr. 8], và phần lệch là phương sai chứ không phải thiên lệch có dấu (sai lệch t_z trung bình ±0,01%). Thiên lệch có dấu thật sự chỉ xuất hiện ở SNR thấp và **xa** camera (σ = 5 px, t_z/10 = 20: OI co t_z −3,1% so với +0,5% của LM\*), tức ngược với nơi bài cảnh báo.
- **(6) C1 của bài: tái hiện khớp.** Sai số xoay trung bình của OI là 2,26° / 0,67° / 0,21° / 0,066° / 0,021° ở 30–70 dB, so với khoảng 2,5 / 1 / 0,3 / 0,05 / 0,02° đọc từ Fig. 11. ‖Δt‖ tuyệt đối là 0,61 / 0,17 / 0,059 / 0,017 / 0,005, so với khoảng 0,55 / 0,19 / 0,06 / 0,02 / 0,008 ở Fig. 12. Ngược lại, Fig. 4 (khoảng 3° ở **70 dB**) và Fig. 5 (khoảng 3% translation) lớn hơn C6 của tôi khoảng 100 lần; mục 8 bàn thêm.

## 8. Chỗ tôi không tin

- **Eq. (16) như in.** Với M định nghĩa ở (13) thì R* = VUᵗ là chuyển vị của nghiệm (C0: sai 123°). Phụ lục A lặp lại cùng quy ước (47). Ai cài lại từ bài mà chép nguyên văn sẽ ra sai. Mã Matlab gốc (trỏ tới www.cs.jhu.edu/~hager [tr. 7]) tôi chưa mở, nên chưa biết mã có đúng không.
- **Bước (31) của chứng minh.** Như viết thì không suy ra được từ (25) và (27), và C1 cho thấy nó sai thật ở gần nửa số bước. Kết luận (33) vẫn đúng, nhưng nhờ một lập luận khác (majorant, mục 3). Chứng minh trong bài vì vậy không hoàn chỉnh, dù định lý đúng.
- **Phụ lục A (nghiệm AO duy nhất).** Lập luận chỉ xét hoán vị, đổi dấu cặp cột và xoay trong không gian riêng của giá trị kỳ dị lặp. Nó bỏ qua giá trị kỳ dị bằng 0, tức M hạng ≤ 2, mà với target phẳng thì điều này **luôn** xảy ra. Khi đó (16) không sửa det cho hai ma trận, một xoay và một phản xạ. Vì vậy giả thiết "nghiệm AO duy nhất" dùng trong (33), và cả tính đóng trong SO(3), đều cần thêm sửa det mà bài không có.
- **"Hội tụ toàn cục" ở nhan đề và abstract.** Người đọc nhanh (và ít nhất một survey, xem mục 10) dễ hiểu thành "tìm được nghiệm toàn cục". Định lý chỉ nói về điểm bất động. Câu "will eventually be reached" [tr. 6] còn mạnh hơn cả kết luận của Zangwill, vốn chỉ nói về dãy con.
- **Tuyên bố thực nghiệm "chỉ cần không đặt vật sau camera".** [tr. 6, tr. 9–10] Với N = 20 trong cấu hình của bài, tôi thấy 96% đạt, gần với tuyên bố. Nhưng với N = 6 chỉ 79%, và target phẳng thì khoảng 50–60% (C2). Bài chỉ thử tám đỉnh hộp và N ≥ 10 điểm trong hộp, nên câu kết "few, if any, spurious local minima" [tr. 12] là khái quát hoá quá phạm vi đã thử.
- **"Quadratic-like local convergence"** [tr. 11]. Đây là suy luận từ thời gian chạy, không phải đo tốc độ; C3 đo được tuyến tính (0,45–0,87). Kết luận "nhanh hơn LM" ở Fig. 9 là so với MINPACK LMDIF, một bản LM dùng **sai phân hữu hạn** cho Jacobian, chạy trên phần cứng năm 2000. Điều này không chuyển sang được một LM có Jacobian giải tích ngày nay (tôi suy ra).
- **Các số của Fig. 3–8 và 15–16.** Fig. 4 và 7 cho sai số xoay khoảng 3° ở SNR 70 dB, trong khi Fig. 11 của chính bài cho khoảng 0,02° ở 70 dB, và C6 của tôi cho 0,021°. Fig. 15–16 (C3, SNR 50 dB, N = 20) cho khoảng 2° và khoảng 0,6, trong khi Fig. 11–12 ở cùng điều kiện (50 dB, N = 20) cho khoảng 0,3° và khoảng 0,06. Hai nhóm hình không thể cùng đúng với định nghĩa SNR đã nêu. Nhóm Fig. 11–12 là nhóm tôi dựng lại được, nên tôi tin nhóm đó và không dùng số của Fig. 3–8 và 15–16.
- **Mâu thuẫn trong ngưỡng 3,5.** §3.5 viết "ratio between the size of the object in the direction of optical axis and distance to camera is smaller than 3.5" [tr. 7], còn §4.1.1 viết ngược lại, "distance to camera and the object size in z direction" [tr. 8]. Chỉ cách viết thứ hai khớp với Fig. 5.
- **Tuyên bố chống ngoại lai.** Chỉ có một thí nghiệm (C2), một baseline (LM không robust), ngoại lai kiểu "thay điểm 3D bằng điểm ngẫu nhiên trong hộp" (ngoại lai nhẹ, vẫn chiếu gần vật), và không có RANSAC. Tôi không coi đây là bằng chứng rằng OI "robust".
- Bài gọi **GL(3) là tập ma trận chéo 3 × 3** [tr. 5], một ký hiệu không chuẩn. Câu cuối của (21) viết "positive definiteness of V̂_i" trong khi ý là của I − (1/n)ΣV̂_i [tr. 5]. Cả hai là lỗi nhỏ nhưng cho thấy bài không được soát kỹ phần toán.

## 9. Chỗ tôi chưa hiểu (→ `99-chua-biet.md`)

- Các điểm bất động "giả" mà tôi gặp (C2) là cực tiểu địa phương thật hay có cả điểm yên ngựa? OI là MM nên điểm yên ngựa thường không hút, nhưng tôi chưa kiểm Hessian của E trên SO(3) tại các điểm đó.
- Hệ số co tuyến tính của OI (0,45–0,87) phụ thuộc vào hình học thế nào? Về lý thuyết MM, nó là "tỉ lệ độ cong" giữa majorant và E tại nghiệm, nên hẳn gắn với phần Σ‖V̂(q − q^(k))‖² (thành phần dọc tia, tức độ sâu). Tôi đoán nó tiến về 1 khi vật phẳng hoặc xa, và C3 cho phẳng chậm hơn, nhưng chưa dẫn được.
- Phiên bản có trọng số 1/d_i² [eq. (46)] có còn là MM không? Trọng số đổi theo k, nên majorant ở vòng k không còn chặn trên hàm mục tiêu cố định, và chứng minh (33) không áp dụng nguyên được. Bài cũng không nói t(R) tính thế nào khi có trọng số.
- Số trong Fig. 3–8 được tạo với định nghĩa nhiễu nào? Có thể σ ở §4.1 là trên pixel chứ không phải toạ độ chuẩn hoá, hoặc "rotation error" là một đại lượng khác. Tôi chưa tìm được cách đọc nào làm 3° ở 70 dB hợp lý.
- Mã Matlab gốc (JHU) có sửa det và dùng UVᵗ không? Nếu có thì lỗi (16) chỉ là lỗi in; nếu không thì các thí nghiệm target phẳng dùng mã đó có thể đã trả về phản xạ.

## 10. Quan hệ với các bài khác trong `refs.bib`

- `haralick1989pose` là động lực trực tiếp ([28], [tr. 1]). OI giữ ý "biến phụ khử phối cảnh" và thay vòng lặp chậm (hàng trăm vòng theo [28]) bằng AO có nghiệm đóng.
- `dementhon1995posit` ([23]) là đại diện "iterative reduced perspective". Bài chê cách tính xoay hai bước của nó [tr. 1], và khởi tạo §3.4 của OI chính là một bước weak perspective tối ưu hơn.
- `schweighofer2006planar`: theo ghi chú trong `refs.bib`, bài này chỉ ra hai cực tiểu địa phương với target phẳng. C2 của tôi thấy đúng điều đó với hàm E của OI (20/20 cảnh phẳng có hai điểm bất động trước camera). Tôi chưa đọc bài đó, nên chưa biết họ phân tích trên cùng hàm (19) hay không.
- `terzakis2020sqpnp` xếp OI vào nhóm "heuristic", không xử lý cấu hình nhiều cực tiểu [tr. 3 của bài đó], điều khớp với C2 ở đây. Nó dùng một hàm không gian vật **khác** [eq. (2), tr. 5 của bài đó] và dẫn [34] = OI như tiền lệ của kiểu hàm này.
- `marchand2016arsurvey` (ghi chú `notes/marchand2016arsurvey.md`, mục 10) mô tả OI là lặp trên sai số đại số, nhanh nhưng còn cực tiểu địa phương, và ghi nhận nhan đề "globally convergent" có vẻ trái với điều đó. Đọc kỹ thì hai điều không mâu thuẫn: "globally convergent" là hội tụ từ mọi điểm đầu, không phải tối ưu toàn cục. Chữ "sai số đại số" của survey thì không chính xác, vì (19) là khoảng cách hình học trong không gian vật.
- `collins2014ippe` dùng OI ([28] của họ) làm baseline PnP, theo `notes/collins2014ippe.md`.

## 11. Nó đổi gì trong suy nghĩ

Trước khi đọc, tôi hiểu "globally convergent" là "không phụ thuộc khởi tạo". Giờ tôi thấy đó là một phát biểu hẹp: OI là MM trên một hàm có nhiều điểm dừng, và tính đơn điệu chỉ bảo đảm nó không phân kỳ, không bảo đảm nó đến đúng chỗ. Với câu hỏi dẫn đường số 2 ("tối ưu toàn cục theo hàm nào?"), OI là ví dụ rõ nhất về việc phải tách *hội tụ toàn cục* khỏi *tối ưu toàn cục*. Nó cũng là ví dụ về một hàm mục tiêu không gian vật: đổi được nghiệm đóng cho t và vòng lặp AO, trả giá bằng việc lệch khỏi nghiệm ML dưới nhiễu pixel (khoảng 1,2% RMSE tái chiếu, và khoảng 20% sai số khi vật sâu so với khoảng cách). Với câu hỏi 5, kết quả C4 cho thấy khi đã có tinh chỉnh LM ở cuối thì chọn OI hay SQPnP làm bộ khởi tạo gần như không đổi kết quả với vật không phẳng. Với target phẳng thì khác: bộ khởi tạo quyết định rơi vào cực tiểu nào, nên cần bộ giải trả cả hai nghiệm (IPPE, RPP).

## 12. Câu hỏi tự kiểm (3–5 câu, hỏi *vì sao* / *khi nào hỏng*)

1. Vì sao E(R^(k)) giảm đơn điệu mà OI vẫn có thể dừng ở pose sai? Nêu đúng điều mà định lý Zangwill cho và điều nó không cho.
2. Vì sao với target phẳng, hàm (19) *không thể* có cực tiểu toàn cục duy nhất nếu bỏ qua cheirality? Viết ra phép biến đổi (R, t) ↦ (−RS, −t) và kiểm det.
3. Khi nào nghiệm của OI lệch xa nghiệm cực tiểu tái chiếu nhất, khi vật gần hay xa, nông hay sâu, và vì sao trọng số ngầm tỉ lệ với độ sâu gây ra điều đó?
4. Nếu chép nguyên văn eq. (16) vào code thì hỏng thế nào, và vì sao bỏ sửa det lại nguy hiểm riêng cho target phẳng?
5. Vì sao OI hội tụ tuyến tính chứ không bậc hai, và điều đó nói gì về số vòng lặp khi vật gần phẳng hoặc rất xa?

## Trích đoạn nguyên văn làm bằng chứng

- "Note that a solution does not necessarily correspond to the correct true pose." [tr. 5]
- "meaning that OI decreases E strictly unless a solution is reached." [tr. 6]
- "Although global convergence does not guarantee that the true pose will always be recovered, it does suggest that the true pose can be reached from very a broad range of initial guesses." [tr. 6]
- "The global convergence of the OI algorithm is attained at the expense of being biased when the observed image points are perturbed by homogeneous Gaussian noise." [tr. 7]
- "The pose solution will implicitly more heavily weight reference points that are farther away from the camera." [tr. 7]
- "Although in noisy cases there may be a few spurious fixed points to which OI converges" [tr. 9]
- "This leads us to believe that the proposed method has quadratic-like local convergence similar to that of the Gauss-Newton method." [tr. 11]
- "our results suggest that OI tends to find the correct pose solution, suggesting that there are few, if any, spurious local minima." [tr. 12]
