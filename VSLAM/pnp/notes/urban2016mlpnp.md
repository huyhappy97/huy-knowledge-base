# MLPnP — A Real-Time Maximum Likelihood Solution to the Perspective-n-Point Problem — ghi chú đọc

| | |
|---|---|
| bibkey | `urban2016mlpnp` |
| Venue, năm | *ISPRS Annals of the Photogrammetry, Remote Sensing and Spatial Information Sciences* III-3, tr. 131–138, 2016 (XXIII ISPRS Congress, Prague); phản biện kín hai chiều trên toàn văn [tr. 1, chân trang] |
| Bản đã đọc | `papers/urban2016mlpnp.pdf` — bản xuất bản của ISPRS Annals (Copernicus), 8 trang; DOI 10.5194/isprs-annals-III-3-131-2016 (Crossref khớp tên, tập, trang 131–138, kiểm ngày 2026-09-25) |
| Mức đọc | lượt 2 toàn bài; lượt 3 cho §3.1–§3.4 và §4.3–§4.4 (lan truyền covariance, không gian tiếp tuyến, nghiệm tuyến tính, Gauss–Newton, covariance của pose) |
| Người đọc | Claude (agent), 2026-09-25 — **Huy chưa đọc lại để ký** |
| Mức tin | giữ B: công thức lõi đúng và tôi tái hiện được bằng số; nhưng venue không phải đầu ngành thị giác máy, thực nghiệm chỉ ở dạng đồ thị, và hai tuyên bố ("tối ưu thống kê", MLPnP+Σ) không được bằng chứng của chính bài đỡ |
| Kiểm chứng | eq. (6), (9): cửa (a) + (b) [C1]; eq. (11)–(19): cửa (b) [C2]; GN §3.4 ≈ ML pixel: cửa (b) [C3, C4]; eq. (23), (26): cửa (b) [C5]. Eq. (24)–(25) (MLPnP+Σ): **chưa kiểm**, chỉ phê phán lý thuyết ở mục 8 |

## 1. Bài toán gốc và bối cảnh

Bài nhắm vào PnP với camera đã hiệu chỉnh, nhưng muốn hai thứ mà phần lớn bộ giải PnP n điểm thời đó không cho: đưa độ bất định của từng quan sát ảnh vào ước lượng, và trả về độ chính xác bên trong (covariance) của pose [tr. 1, §1]. [T] Tác giả nhận định các bộ giải trước (LHM, EPnP+GN, DLS, RPnP, OPnP, ASPnP, UPnP…) đều giả định mọi quan sát chính xác như nhau, tức "tối ưu hình học nhưng không tối ưu thống kê" [tr. 1–2, §2, Tab. 1]. [T] Theo họ, công trình duy nhất trước đó dùng covariance quan sát là CEPPnP của Ferraz và cộng sự (`ferraz2014cepnp`), vốn đưa covariance vào không gian điểm điều khiển của EPnP rồi xấp xỉ ML bằng sai số Sampson [tr. 2, §2].

Cái khó mà bài giải quyết là chuyện kỹ thuật chứ không phải khái niệm: nếu làm việc với tia chiếu đơn vị 3D `v` (để phục vụ camera trung tâm bất kỳ, kể cả fisheye > 180°) thì covariance 3×3 của `v` luôn suy biến hạng 2, nên không thể nghịch đảo để làm ma trận trọng số [tr. 3, eq. (6) và câu ngay sau]. Lời giải là mượn biểu diễn tối giản của Förstner (ACCV 2010, không có trong `refs.bib`): chiếu mọi thứ xuống mặt phẳng tiếp tuyến 2D của `v` [tr. 3, §3.2].

## 2. Giả thiết — kể cả giả thiết ngầm; bỏ đi thì hỏng ở đâu

- **Camera trung tâm đã hiệu chỉnh**, có hàm chiếu ngược π khả vi [tr. 3, eq. (3)]. Bỏ đi thì không có `v`; đây là giả thiết tường minh.
- **Nhiễu Gauss ở điểm ảnh 2D với covariance Σ_x'x' đã biết, không suy biến**, độc lập giữa các điểm [tr. 3, eq. (2); tr. 3–4, "Assuming uncorrelated observations", eq. (13)]. [M] Nếu Σ chỉ biết sai một hằng số nhân thì nghiệm không đổi và σ0² ở eq. (26) sửa thang đo; nếu Σ sai về *hình dạng* thì nghiệm vẫn nhất quán nhưng không còn hiệu quả và covariance eq. (23) sai (mục 7, C5c cho thấy một dạng của hiện tượng này).
- **Điểm 3D `p_i` không có sai số** (tôi suy ra: không có số hạng nào cho Σ của `p_i` trong eq. (10)–(14)). Trong thí nghiệm thật, điểm 3D đo bằng laser tracker ≈ 0,1 mm [tr. 5, §4.2], nên giả thiết này gần đúng ở đó; với bản đồ SLAM thì không.
- **Tuyến tính hoá bậc nhất**: covariance của `v` lan truyền qua Jacobian eq. (6), và mặt phẳng tiếp tuyến được dựng tại `v` **quan sát** (có nhiễu), không tại `v` thật [tr. 3, eq. (7)–(9)]. [M] Khi nhiễu lớn so với độ cong, cả hai xấp xỉ vỡ; mục 7 (C5, nhiễu ×20) cho thấy điểm vỡ.
- **Không có ngoại lai.** [M] Hàm mục tiêu là bình phương có trọng số, không bền vững; bài không nói gì về ngoại lai ngoài việc nhắc REPPnP ở §2.
- **Ngầm: dấu của nghiệm tuyến tính.** [M] Vectơ `u` trong eq. (12) chỉ xác định tới dấu; eq. (17) lấy căn bậc ba của tích chuẩn (luôn dương) nên không sửa dấu. Bài không nói cách chọn dấu; tôi phải thêm điều kiện det(R̂) > 0 khi cài lại.
- **Ngầm: n ≥ 6 cho bước tuyến tính** — bài nói "I > 5" [tr. 3, sau eq. (12)] vì 12 ẩn đồng nhất, 2 phương trình/điểm. Với 4–5 điểm phải dùng bộ giải khác để khởi tạo (tôi suy ra).
- **Trường hợp phẳng** dùng ngưỡng cố định 1e-10 trên trị riêng nhỏ nhất của S = MMᵀ [tr. 4, §3.5]. [M] Ngưỡng tuyệt đối này phụ thuộc đơn vị toạ độ thế giới và sẽ bỏ sót cảnh *gần* phẳng.

## 3. Cơ chế — năm câu, rồi chi tiết có định vị

Năm câu: (1) lan truyền covariance pixel qua π và qua chuẩn hoá cầu để có covariance 3×3 (suy biến) của tia chiếu `v`; (2) lấy cơ sở trực chuẩn `[r s]` của không gian rỗng của `vᵀ`, chiếu covariance xuống đó thành ma trận 2×2 khả nghịch; (3) phần dư của một điểm là toạ độ của `R p + t` (chuẩn hoá) trên mặt phẳng tiếp tuyến ấy — bằng 0 khi pose đúng; (4) bỏ hệ số độ sâu thì phần dư tuyến tính theo 12 phần tử của [R | t], giải bằng SVD của hệ chuẩn tắc có trọng số rồi ép về SO(3); (5) tinh chỉnh bằng Gauss–Newton trên chính phần dư tiếp tuyến có trọng số (R tham số hoá Cayley), và nghịch đảo ma trận chuẩn tắc cho covariance của pose.

**Lan truyền** [tr. 3, §3.1]. Pixel x' có Σ_x'x' [eq. (2)]; x = π(x') với Jacobian J_π có hàng cuối bằng 0 [eq. (3)], nên Σ_xx = J_π Σ_x'x' J_πᵀ có hạng 2 [eq. (4)]. Chuẩn hoá cầu v = x/‖x‖ [eq. (5)], Jacobian J = (I₃ − v vᵀ)/‖x‖ và Σ_vv = J Σ_xx Jᵀ [eq. (6)]. Σ_vv vẫn suy biến (vectơ `v` nằm trong không gian rỗng của nó).

**Không gian tiếp tuyến** [tr. 3, §3.2]. J_vr(v) = null(vᵀ) = [r s] (3×2, trực chuẩn) tính bằng SVD [eq. (7)]; v_r = J_vrᵀ v = 0 [eq. (8)]; Σ_vrvr = J_vrᵀ Σ_vv J_vr là 2×2 khả nghịch [eq. (9)]. [T] Tác giả gọi v_r là "phần dư trong không gian tiếp tuyến" [tr. 3, dưới eq. (9)].

**Nghiệm tuyến tính** [tr. 3–4, §3.3]. Từ λ_i v_i = R p_i + t [eq. (1)], phần dư [d_r, d_s]ᵀ = [rᵀ; sᵀ] λ_i⁻¹ (R p_i + t) = 0 [eq. (10)]. Khai triển với λ_i⁻¹ bị bỏ đi [eq. (11)] cho hai phương trình tuyến tính trong u = [r̂11…r̂33, t̂1, t̂2, t̂3]ᵀ, xếp thành A u = 0 [eq. (12)]. Trọng số P = blockdiag(Σ_vrvr⁻¹) [eq. (13)], hệ chuẩn tắc AᵀPA u = N u = 0 [eq. (14)], nghiệm là vectơ kỳ dị nhỏ nhất của N [eq. (15)–(16)]. Thang đo: t = t̂ / ∛(‖r̂1‖‖r̂2‖‖r̂3‖) [eq. (17)]; ép R̂ về SO(3) bằng SVD, R = U_R V_Rᵀ [eq. (18)–(19)].

**Gauss–Newton** [tr. 4, §3.4]. Cực tiểu hoá phần dư tiếp tuyến eq. (10) có trọng số P, R biểu diễn bằng tham số Cayley; [T] "tối đa năm vòng là đủ". Bài không viết Jacobian ra.

**Trường hợp phẳng** [tr. 4, §3.5]. Khi các điểm đồng phẳng, N có tới bốn giá trị kỳ dị nhỏ; bài xoay điểm theo các vectơ riêng của S = MMᵀ [eq. (20)], bỏ cột ứng với toạ độ hằng khỏi A, rồi xoay R trở lại [eq. (21)].

**Covariance của pose** [tr. 5–6, §4.3–4.4]. Σ_r̂t̂ = (AᵀPA)⁻¹ với A là Jacobian của phần dư eq. (10) [eq. (23)]; hệ số phương sai σ0² = rᵀPr / b với độ dư b = 2I − 6 [eq. (26)]; độ lệch chuẩn σ_r̂,t̂ = σ0 √diag(Σ_r̂t̂) [eq. (27)]. Ngoài ra "MLPnP+Σ" dùng Q_vrvr = A Σ_r̂t̂ Aᵀ [eq. (24)], chiếu ngược về Σ_vivi = J_vr Q J_vrᵀ [eq. (25)] làm covariance quan sát cho khung hình sau [tr. 5, §4.3].

**ML theo nghĩa nào.** [M] Ghép lại: "maximum likelihood" ở đây là ML dưới mô hình nhiễu Gauss cộng tính trên pixel với covariance biết trước, độc lập giữa các điểm, điểm 3D chính xác — **sau khi** tuyến tính hoá bậc nhất phép chiếu ngược và dựng mặt phẳng tiếp tuyến tại tia quan sát. Hàm mục tiêu của GN, Σᵢ dᵢᵀ Σ_vr,i⁻¹ dᵢ, là xấp xỉ bậc nhất của sai số tái chiếu Mahalanobis ở pixel. Bước tuyến tính eq. (14) **không** phải ML: nó là sai số đại số có trọng số, trong đó mỗi phần dư đã bị nhân với độ sâu λᵢ (do bỏ λᵢ⁻¹ ở eq. (11)) và 12 ẩn được nới lỏng khỏi ràng buộc SO(3). Dù vậy bài gọi nó là "linear ML estimation" [tr. 4, dưới eq. (19)]. Mục 7 đo khoảng cách giữa hai bước.

## 4. Ký hiệu của bài ↔ ký hiệu của khảo sát

| Bài | Khảo sát | Ghi chú |
|---|---|---|
| p_i (I điểm, i = 1..I) | X_w (n điểm) | điểm 3D hệ thế giới |
| R, t với λ_i v_i = R p_i + t [eq. (1)] | R, t với X_c = R X_w + t | cùng chiều thế giới → camera |
| x' = [x', y']ᵀ | u | pixel |
| π (ví dụ K⁻¹), J_π [eq. (3)] | K⁻¹ | bài cho phép π tổng quát (fisheye) |
| x = π x' | K⁻¹[u; 1] | điểm trên mặt phẳng ảnh chuẩn hoá |
| v = x/‖x‖ [eq. (5)] | f | tia chiếu đơn vị |
| λ_i | ‖X_c‖ | "độ sâu" của bài là **khoảng cách** dọc tia, không phải toạ độ z (vì ‖v‖ = 1) |
| J_vr(v) = [r s] [eq. (7)] | — | cơ sở mặt phẳng tiếp tuyến, khảo sát chưa đặt tên |
| Σ_x'x', Σ_vv, Σ_vrvr | Σ_u (pixel) | |
| u (12×1) [eq. (12)] | — | **trùng chữ với pixel `u` của khảo sát** — đừng nhầm |
| A, P, N [eq. (12)–(14)] | — | A dùng hai lần: ma trận thiết kế tuyến tính (eq. 12) và Jacobian GN (eq. 23) |
| Σ_r̂t̂ [eq. (23)] | Σ_pose | tham số: 3 Cayley + 3 tịnh tiến |
| σ0², b = 2I − 6 [eq. (26)] | — | hệ số phương sai, độ dư |

## 5. Bằng chứng — dữ liệu, phần cứng, baseline, con số kèm điều kiện, số lần lặp

**Phần cứng và cài đặt** [tr. 4, §4]: laptop Intel Core i7-3630QM 2,4 GHz. MLPnP, UPnP, EPnP+GN chạy C++ qua mex; OPnP, EPPnP, CEPPnP, DLS, LHM, ASPnP, SDP, RPnP, PPnP chạy Matlab. [T] Tác giả tự lưu ý không rõ bản C++ của các thuật toán Matlab nhanh hơn bao nhiêu. [T] MLPnP bản C++ được tích hợp vào OpenGV (`kneip2014opengv`); tôi chưa kiểm được điều này trong mã OpenGV (không truy cập được kho).

**Tổng hợp** [tr. 4–5, §4.1; Fig. 3, tr. 7]: dùng toolbox Matlab của Ferraz/Li/Zheng; f = 800 px; điểm lấy đều trong hộp [−2,2]×[−2,2]×[4,8] hệ camera; t_gt là trọng tâm các điểm, R_gt ngẫu nhiên; T = 250 lần lặp, báo **trung bình** sai số. Sai số quay = max theo ba cột của góc giữa cột thật và cột ước lượng (độ); sai số tịnh tiến "tính theo %" ‖t_gt − t‖/‖t‖×100 [tr. 5] — nhưng trục tung Fig. 3 ghi "[m]" (mâu thuẫn, xem mục 8). Hai kịch bản: (a)–(d) số điểm I = 10..200, nhiễu σ = 1..10 px, mỗi mức nhiễu áp cho 10% số điểm; (e)–(h) I = 50, mỗi điểm một σ ngẫu nhiên trong [0, σ_max], σ_max = 1..10. Cột trái là cảnh 3D thường, cột phải là cảnh phẳng (Z = 0). **Nhiễu đẳng hướng ở mọi thí nghiệm tổng hợp** (tôi suy ra: bài chỉ nói "Gaussian noise with different standard deviations σ" [tr. 5]; không có covariance xiên).

[Đ] Đọc xấp xỉ từ đồ thị Fig. 3(a), cảnh 3D, I = 50: MLPnP+Σ ≈ 0,27°, CEPPnP ≈ 0,31°, còn MLPnP *không* Σ ≈ 0,45°, nằm lẫn trong nhóm các bộ giải không dùng Σ. [Đ] Fig. 3(e), I = 50, σ_max = 10: MLPnP+Σ ≈ 0,15°, CEPPnP ≈ 0,18°, các phương pháp không Σ ≈ 0,42–0,5°. [Đ] Ở cảnh phẳng (Fig. 3(b),(f)) MLPnP+Σ và CEPPnP gần như trùng nhau. (Đây là số tôi đọc bằng mắt từ đồ thị, sai số đọc cỡ ±0,02°; bài không có bảng số.)

**Thời gian** [Fig. 2, tr. 6]: [Đ] đọc từ Fig. 2(b), ở 2000 điểm MLPnP ≈ 6 ms, MLPnP+Σ ≈ 9 ms, EPnP+GN ≈ 1 ms, CEPPnP > 20 ms. [T] "Với ít hơn 20 điểm, thuật toán còn nhanh hơn EPnP" [tr. 5, §4.1] — không có số cụ thể đi kèm.

**Dữ liệu thật** [tr. 5, §4.2; Fig. 4, Fig. 5, Tab. 2]: quỹ đạo T = 200 pose của một camera fisheye gắn mũ (754×480 px, trường nhìn 185°, mô hình Scaramuzza), mỗi khung nhìn thấy 6–13 điểm mốc phẳng hình tròn; pose thật từ Leica T-Probe + laser tracker (σ_pos ≈ 0,1 mm, σ_angle ≈ 0,05 mrad), toạ độ điểm mốc đo cũng bằng tracker. Chỉ số: độ lệch chuẩn trung bình σ̄_R, σ̄_t của phép biến đổi tương đối camera↔T-Probe M_rel = M_gt⁻¹ M_t [eq. (22)] — phép biến đổi này lẽ ra hằng số, nên độ tản của nó đo sai số pose. [Đ] Đọc từ Fig. 5(a),(b): MLPnP ≈ 0,23° / 1,25 cm; MLPnP+Σ ≈ 0,19° / 1,0 cm; CEPPnP ≈ 0,21° / 1,0 cm; DLS ≈ 0,22° / 1,13 cm; UPnP ≈ 0,22° / 1,1 cm. [Đ] Fig. 5(c): thời gian trung bình MLPnP ≈ 0,3 ms mỗi khung. [Đ] Tab. 2 [tr. 6]: σ_angle "ground truth" 0,19° so với "estimated" 0,18°; σ_pos 1,03 cm so với 0,92 cm. Bài không nói Tab. 2 là của MLPnP hay MLPnP+Σ; [M] con số 0,19° và ≈ 1,0 cm khớp với cột MLPnP+Σ ở Fig. 5 hơn là cột MLPnP.

Không có khoảng tin cậy, không có số lần chạy lại cho dữ liệu thật (một quỹ đạo), không có thí nghiệm với covariance bất đẳng hướng hay ngoại lai.

## 6. Đóng góp thật sự (thường nhỏ hơn abstract)

[M] Đóng góp thực là một **cách viết phần dư** gọn cho PnP trên tia chiếu: phần dư 2D trong mặt phẳng tiếp tuyến của tia quan sát, cùng với covariance 2×2 khả nghịch tương ứng (lấy từ Förstner 2010). Nhờ đó (i) một bộ giải tuyến tính có trọng số và một GN có trọng số dùng được cho mọi camera trung tâm, kể cả tia có z ≤ 0 của fisheye 185°, và (ii) covariance pose rơi ra tự nhiên từ ma trận chuẩn tắc. Bản thân GN có trọng số và (JᵀPJ)⁻¹ là bình sai trắc địa ảnh kinh điển; điểm mới là đóng gói nó cho bearing vector và làm nhanh.

[M] Những gì abstract nói nhiều hơn thế: "statistically optimal" chỉ đúng theo nghĩa xấp xỉ bậc nhất, và bằng chứng "tối ưu" duy nhất của bài (Tab. 2) thực ra là bằng chứng về **tính nhất quán của covariance** trên một quỹ đạo, không phải về hiệu quả. "Outperforms the state-of-the-art" [tr. 6, §5] dựa vào biến thể MLPnP+Σ; MLPnP không Σ ngang hàng các bộ giải khác ở Fig. 3 và kém DLS/UPnP ở Fig. 5 (đọc từ đồ thị).

## 7. Kiểm chứng của người ghi chú — script trong `code/`, lệnh chạy, kết quả thật

Script: `code/urban2016mlpnp_check.py` (numpy + cv2 5.0.0, seed cố định, ~20 s). Tôi cài lại eq. (3)–(9), (11)–(19) (không cài §3.5 phẳng), GN §3.4 với phần dư eq. (10) **có** chia cho ‖R p + t‖, R cập nhật nhân trái bằng Cayley, tối đa 5 vòng; Σ pose theo eq. (23), σ0² theo eq. (26). Cảnh sinh bằng `common.make_scene` (K: f = 800 px, ảnh 640×480, độ sâu 4–8, pose ngẫu nhiên). Mô hình nhiễu chính (A): mỗi điểm một covariance 2×2 riêng, trục lớn σ_maj ~ U(0,5; 5) px, tỉ lệ trục ~ U(1; 8), hướng ngẫu nhiên; covariance đúng được đưa cho MLPnP. (B) mô phỏng Fig. 3(e): σ_i ~ U(0; 5) đẳng hướng; (C) đối chứng σ = 2 px đồng nhất. "Mahal-pixel GN" là GN trên sai số tái chiếu Mahalanobis ở pixel (ML chuẩn vàng dưới cùng mô hình nhiễu), khởi tạo từ MLPnP, 20 vòng. "MLPnP P=I" là cùng thuật toán với trọng số đơn vị. "lin eq.14 + 1/lam" là biến thể **của tôi**, không có trong bài: chạy lại bước tuyến tính với mỗi hàng chia cho λ̂ᵢ lấy từ lần giải đầu.

Lệnh: `python3 VSLAM/pnp/code/urban2016mlpnp_check.py` (chạy từ gốc repo). Kết quả thật, cắt bớt:

```
cv2 5.0.0, numpy 2.4.6
[PASS] C1a Jacobian eq.(6): max|J_num - J_eq6| = 1.3e-09
[PASS] C1b Sigma_vv hạng 2 (eq.6): max s3/s1 = 2.6e-17
[PASS] C1c Sigma_vv, Sigma_vr so với Monte-Carlo (N=2e5): sai lệch Frobenius tương đối lớn nhất: vv 0.381%, vr 0.381%
[PASS] C2 nghiệm tuyến tính không nhiễu (n=6..50, 80 cảnh): max ||R0 - R||_F 2.3e-13 (...), max trans rel err 7.1e-13

  -- A bất đẳng hướng, sigma_maj U(0.5,5), tỉ lệ U(1,8): n=10, 300 cảnh --
  phương pháp          rot mean  rot med  t% mean   t% med
  cv2 EPNP               0.4628   0.4115   6.4214   4.6865
  cv2 ITERATIVE          0.4164   0.3746   5.3612   4.1891
  cv2 SQPNP              0.4275   0.3762   5.5803   4.2043
  MLPnP lin P=I          1.5027   1.0638  34.8174  17.5657
  MLPnP lin (eq.14)      0.9378   0.6791  17.5070   9.5406
  lin eq.14 + 1/lam      0.8941   0.6409  17.0469   9.5540
  MLPnP P=I (+GN)        0.4166   0.3719   5.3823   4.3217
  MLPnP (+GN)            0.1876   0.1546   2.4169   1.8411
  Mahal-pixel GN         0.1876   0.1544   2.4169   1.8437

  -- A bất đẳng hướng, sigma_maj U(0.5,5), tỉ lệ U(1,8): n=50, 300 cảnh --
  cv2 EPNP               0.1898   0.1780   2.3740   2.0190
  cv2 ITERATIVE          0.1573   0.1466   1.8130   1.6059
  cv2 SQPNP              0.1694   0.1541   1.9597   1.7009
  MLPnP lin P=I          0.3201   0.2995   6.2462   4.8592
  MLPnP lin (eq.14)      0.0947   0.0831   1.4905   1.2220
  lin eq.14 + 1/lam      0.0906   0.0762   1.3894   1.1262
  MLPnP P=I (+GN)        0.1568   0.1466   1.8132   1.5505
  MLPnP (+GN)            0.0390   0.0372   0.4466   0.3900
  Mahal-pixel GN         0.0390   0.0373   0.4466   0.3902

  -- B đẳng hướng dị phương sai kiểu Fig.3(e), sigma U(0,5): n=50, 300 cảnh --
  cv2 ITERATIVE          0.2139   0.2090   2.7187   2.1658
  MLPnP lin (eq.14)      0.1740   0.1475   3.1111   2.1497
  MLPnP P=I (+GN)        0.2141   0.2073   2.7213   2.1743
  MLPnP (+GN)            0.0582   0.0515   0.7604   0.5658
  Mahal-pixel GN         0.0581   0.0514   0.7602   0.5665

  -- C đẳng hướng đồng nhất sigma=2 (đối chứng): n=50, 300 cảnh --
  cv2 ITERATIVE          0.1424   0.1327   1.8002   1.4620
  MLPnP lin (eq.14)      0.2911   0.2744   4.9899   4.0480
  MLPnP (+GN)            0.1424   0.1326   1.7996   1.4668

[PASS] C3A n=10: MLPnP có trọng số < 0.9x cv2 ITERATIVE (median): rot ratio 0.413, trans ratio 0.440, MLPnP thắng 90% cảnh (rot)
[PASS] C4A n=10: MLPnP ~ ML pixel Mahalanobis: median |Δrot| / median rot = 0.070%
[PASS] C3A n=50: ... rot ratio 0.254, trans ratio 0.243, MLPnP thắng 98% cảnh (rot)
[PASS] C4A n=50: ... = 0.067%
      (chỉ thông tin) bước tuyến tính: median rot có trọng số / không trọng số = 0.277; lin(eq.14) / ML cuối = 2.23
[PASS] C3B n=50: ... rot ratio 0.246, trans ratio 0.261, MLPnP thắng 96% cảnh (rot)
[PASS] C3C n=50 đồng nhất: trọng số không được lợi/hại: median rot MLPnP/ITER = 0.999, trans = 1.003
[PASS] C5a NEES nhất quán ở nhiễu thật (Sigma biết, không nhân sigma0^2): noise x1: mean NEES 5.92, median 5.29 (chi2_6: 5.35) (kỳ vọng 6, ±0.15 2σ), phủ 95% = 0.952, mean sigma0^2 = 0.998, SD dự đoán/thực nghiệm = [1.02, 1.01, 1.01, 1.01, 1.02, 0.99], max|bias z| = 1.4
[PASS] C5b E[sigma0^2] ~ 1 (eq. 26): mean sigma0^2 = 0.998
      (chỉ thông tin) noise x5: mean NEES 5.92, median 5.31 (...), phủ 95% = 0.953, ...
      (chỉ thông tin) noise x20: mean NEES 2238675.54, median 5.90 (...), phủ 95% = 0.791, mean sigma0^2 = 149.579, SD dự đoán/thực nghiệm = [48.29, 51.53, 10.27, 1424.79, 4533.72, 4675.67], max|bias z| = 3.9
[PASS] C5c đối chứng: GN không trọng số + covariance đẳng hướng eq.(27) sai ở từng thành phần: mean NEES 6.05, phủ 95% = 0.944, SD dự đoán/thực nghiệm = [0.91, 1.22, 0.99, 1.14, 0.91, 1.08]

Tổng: 15/15 PASS, 20 s
```

Đọc kết quả [M]:

- **C1, C2 (cửa (a)+(b))**: Jacobian eq. (6) đúng; Σ_vv hạng 2 đúng như bài nói; Σ_vr bậc nhất khớp Monte-Carlo trong 0,4% ở nhiễu tới 5 px (f = 800). Với dữ liệu không nhiễu, eq. (11)–(19) (thêm luật chọn dấu det > 0 của tôi) cho lại pose chính xác tới 1e-13, kể cả n = 6.
- **C3: trọng số có lợi rõ khi nhiễu không đồng nhất.** Với nhiễu bất đẳng hướng theo điểm, MLPnP có trọng số giảm sai số quay trung vị còn 0,41× (n = 10) và 0,25× (n = 50) so với `cv2 SOLVEPNP_ITERATIVE`, thắng 90–98% số cảnh. Kiểu nhiễu của chính bài (B, đẳng hướng nhưng σ khác nhau) cũng cho 0,25×. Với nhiễu đồng nhất (C) trọng số không đổi gì (tỉ lệ 0,999) — đúng kỳ vọng, và cho thấy lợi ích đến **hoàn toàn từ thông tin covariance**, không từ cấu trúc bộ giải: MLPnP với P = I ngang `cv2 ITERATIVE` trong mọi kịch bản. Điều này khớp với Fig. 3 của bài, nơi MLPnP không Σ nằm lẫn trong nhóm.
- **C4: "ML" của MLPnP ≈ ML pixel thật.** Sau 5 vòng GN, nghiệm MLPnP khác nghiệm GN Mahalanobis ở pixel dưới 0,1% sai số — với f = 800 px và nhiễu ≤ 5 px, xấp xỉ mặt phẳng tiếp tuyến không làm mất gì đo được.
- **Bước tuyến tính không phải ML.** Nghiệm eq. (14) kém nghiệm cuối 2–4,4 lần (trung vị); ở n = 10 và ở nhiễu đồng nhất nó còn kém cả EPnP (0,68° so với 0,41° ở n = 10; 0,27° so với 0,15° ở C). Chia hàng cho λ̂ᵢ (biến thể của tôi) chỉ cải thiện 5–8% — phần lớn khoảng cách đến từ việc nới lỏng 12 ẩn khỏi SO(3), không từ hệ số độ sâu. Vậy độ chính xác cuối cùng là công của GN, và bước tuyến tính chỉ cần đủ gần để GN hội tụ.
- **C5: covariance eq. (23) nhất quán** trên một cảnh cố định n = 30, 2000 lần Monte-Carlo: NEES trung bình 5,92 (kỳ vọng 6 ± 0,15), phủ 95,2% ở ngưỡng χ²₆ 95%, SD dự đoán/thực nghiệm từng thành phần 0,99–1,02, σ0² trung bình 0,998. Ở nhiễu ×5 (σ_maj tới 25 px) vẫn nhất quán (lưu ý: ×1 và ×5 dùng cùng các mẫu nhiễu chuẩn hoá, nên chúng chỉ khác nhau qua phi tuyến). Ở ×20 (σ_maj tới 100 px) ước lượng **vỡ**: NEES trung bình bùng nổ do vài lần thất bại thảm hoạ, phủ chỉ 79%, σ0² ≈ 150. Như vậy tuyên bố "covariance nội bộ khớp độ chính xác bên ngoài" của Tab. 2 được tôi tái hiện trong điều kiện tổng hợp lý tưởng (Σ biết đúng, không ngoại lai, nhiễu vừa phải).
- **C5c — một kỳ vọng của tôi bị bác bỏ, ghi lại thẳng.** Phiên bản đầu của C5c kiểm rằng GN không trọng số kèm covariance đẳng hướng σ0²(JᵀJ)⁻¹ (eq. (27) với P = I) sẽ có NEES trung bình lệch khỏi 6; nó **FAIL**: NEES trung bình 6,05, phủ 94,4%. Nhờ σ0² tự co giãn, NEES *trung bình* không phân biệt được covariance sai hình dạng. Tôi đổi tiêu chí sang từng thành phần: SD dự đoán lệch thực nghiệm tới 22% (0,91–1,22). Bài học: NEES trung bình là phép thử yếu; Tab. 2 của bài (chỉ so SD trung bình của hai khối góc/vị trí) còn yếu hơn.

Không kiểm: trường hợp phẳng §3.5, MLPnP+Σ eq. (24)–(25), thời gian chạy, dữ liệu fisheye thật.

## 8. Chỗ tôi không tin

- **"Empirical proof … statistically optimal" [tr. 6, §4.4].** [M] Tab. 2 so hai con số độ lệch chuẩn trung bình (0,19° với 0,18°; 1,03 cm với 0,92 cm) trên **một** quỹ đạo 200 khung. Covariance khớp với sai số là tính *nhất quán* (consistency) của covariance, không phải *tối ưu* (đạt cận Cramér–Rao, hay có sai số nhỏ nhất). Một ước lượng không tối ưu vẫn có thể có covariance nội bộ khớp. Chính C5c của tôi cho thấy ngay cả covariance sai hình dạng vẫn có thể khớp ở mức trung bình. Hơn nữa σ_pos ước lượng thấp hơn thực tế 11%, bài gọi đó là "marginal" mà không có khoảng tin cậy nào.
- **MLPnP+Σ (eq. (24)–(25)) có cơ sở thống kê đáng ngờ.** [M] Q = AΣ_r̂t̂Aᵀ là cofactor của các quan sát *đã được hiệu chỉnh* (giá trị khớp) ở khung t, không phải covariance nhiễu đo; trong bình sai kinh điển, covariance của phần dư mới là Q_ll − AΣAᵀ. Đem nó làm covariance đo cho khung t+1 — nơi phép đo ảnh mới có nhiễu độc lập với ước lượng khung trước — không suy ra được từ mô hình ML của chính bài. Nó thực chất là một cơ chế trọng số dựa trên đòn bẩy hình học của từng điểm. Thế mà mọi tuyên bố "vượt trội" (Fig. 3, Fig. 5) lại dựa vào biến thể này. Với dữ liệu tổng hợp, bài không nói MLPnP+Σ lấy Σ từ đâu; tôi đoán là dùng thẳng Σ thật của trình sinh nhiễu (tôi suy ra), tức là một thông tin mà các bộ giải khác không có.
- **Mâu thuẫn đơn vị**: văn bản nói sai số tịnh tiến tính theo % [tr. 5], trục Fig. 3(c),(d),(g),(h) ghi "[m]" [tr. 7]. Không biết cái nào đúng; so với sai số quay cỡ 0,1–0,5° thì 0,1–0,5 "m" trên độ sâu 4–8 m là quá lớn, nên % có vẻ hợp lý hơn (tôi suy ra).
- **"Linear ML estimation" [tr. 4].** [M] Bước tuyến tính là sai số đại số có trọng số với phần dư nhân độ sâu và 12 ẩn nới lỏng; theo C3 nó kém nghiệm cuối 2–4 lần và có lúc kém EPnP. Gọi nó là ML dễ gây hiểu nhầm.
- **So sánh thời gian C++ với Matlab** [tr. 4]: tác giả tự thừa nhận điểm yếu; tôi coi Fig. 2(a) là không so sánh được, chỉ Fig. 2(b) giữa các bản C++ (MLPnP, UPnP, EPnP+GN) là có nghĩa.
- **Tuyên bố "only work" [tr. 1]** chỉ có CEPPnP là tiền lệ dùng covariance quan sát trong PnP: [M] bình sai trắc địa ảnh có trọng số (space resection bằng bình phương tối thiểu có trọng số) đã có từ lâu; tuyên bố chỉ đúng nếu hiểu là "bộ giải PnP thời gian thực không cần khởi tạo". Tôi chưa có nguồn cụ thể trong `refs.bib` để đối chiếu.

## 9. Chỗ tôi chưa hiểu (→ `99-chua-biet.md`)

- Trong thí nghiệm tổng hợp, "MLPnP" (không Σ) và "MLPnP+Σ" khác nhau chính xác ở đâu? §4.3 chỉ mô tả MLPnP+Σ cho dữ liệu thật (Σ lấy từ khung trước qua eq. (24)–(25)); với dữ liệu tổng hợp không có "khung trước". Bài không nói.
- Tab. 2 là của MLPnP hay MLPnP+Σ, và "estimated" có nhân σ0 theo eq. (27) không? Nếu có thì với Σ_x'x' = I₂ ở khung 1, σ0 chính là thứ hiệu chỉnh thang đo, và phép so sánh chỉ còn kiểm hình dạng.
- GN của bài có thật sự chia cho λᵢ = ‖R pᵢ + t‖ (eq. (10)) hay dùng dạng đã bỏ λ như eq. (11)? Văn bản nói "tangent space residuals defined in Eq. 10" [tr. 4]; tôi cài có chia. Nếu bỏ λ thì trọng số lệch theo độ sâu và C4 sẽ không còn khớp. Cần đối chiếu mã OpenGV (`kneip2014opengv`), tôi chưa truy cập được.
- Với fisheye 185°, J_π của mô hình Scaramuzza [eq. (3)] được tính thế nào, và xấp xỉ bậc nhất eq. (6) còn đúng tới đâu ở rìa ảnh, nơi độ méo lớn?
- Tỉ lệ phủ 79% ở nhiễu ×20 (C5) đến từ GN rơi vào cực tiểu địa phương, từ nghiệm tuyến tính sai dấu/sai nhánh, hay từ tuyến tính hoá tiếp tuyến vỡ? Tôi chưa tách được.

## 10. Quan hệ với các bài khác trong `refs.bib`

- `ferraz2014cepnp` (CEPPnP): đối thủ trực tiếp. [T] Theo bài, CEPPnP dùng ML để ước lượng không gian con điểm điều khiển còn MLPnP tối ưu thẳng trên R, t, nên có covariance pose trực tiếp [tr. 2]. [Đ] Trên Fig. 3 hai phương pháp gần như ngang nhau về độ chính xác (đọc từ đồ thị); MLPnP nhanh hơn nhiều ở nhiều điểm [Fig. 2(b)].
- `lepetit2009epnp`, `hesch2011dls`, `li2012rpnp`, `zheng2013opnp`, `zheng2013aspnp`, `kneip2014upnp`, `lu2000orthogonal`, `schweighofer2008sos`, `ferraz2014reppnp`: các baseline không dùng Σ [Tab. 1, tr. 2]. (PPnP của Garro và cộng sự 2012 cũng là baseline nhưng không có trong `refs.bib`.)
- `kneip2014opengv`: nơi bài nói đã đưa bản C++ vào [tr. 4].
- `vakhitov2021uncertainty`: mở rộng hướng này sang bất định cả ở 2D lẫn 3D và sang đường — tức là gỡ đúng giả thiết "điểm 3D chính xác" ở mục 2 (tôi suy ra từ ghi chú danh mục, chưa đọc bài đó).
- `zhan2025gmlpnp`: [M] ước lượng đồng thời pose và covariance bất đẳng hướng — gỡ giả thiết "Σ biết trước" mà MLPnP cần (và mà MLPnP+Σ cố vá bằng eq. (24)–(25)).
- `zeng2023cpnp`: tính nhất quán khi n → ∞ (consistent estimator) là một khái niệm khác với "covariance nhất quán" (NEES) mà §4.4 kiểm; cần phân biệt khi viết ma trận câu hỏi 3 (tôi suy ra).
- `terzakis2020sqpnp`, `opencvsolvepnp`: baseline tôi dùng thêm trong mục 7 (`cv2 SOLVEPNP_SQPNP`, `SOLVEPNP_ITERATIVE`, `SOLVEPNP_EPNP`).

## 11. Nó đổi gì trong suy nghĩ

[M] Trước khi đọc tôi nghĩ MLPnP là một "bộ giải PnP mới"; sau khi đọc và chạy số, tôi thấy nó chủ yếu là **một cách tham số hoá phần dư** (mặt phẳng tiếp tuyến của bearing vector) cộng với GN có trọng số. Hai hệ quả thực hành: (1) độ chính xác cuối cùng gần như hoàn toàn đến từ việc có covariance đúng và từ bước GN — với nhiễu đồng nhất nó không hơn `cv2 ITERATIVE` chút nào; (2) nếu pipeline đã có tinh chỉnh LM trên sai số tái chiếu, chỉ cần thêm trọng số Mahalanobis vào LM là được cùng kết quả (C4 khớp dưới 0,1%), trừ khi camera là fisheye/omni, nơi mặt phẳng tiếp tuyến thực sự giúp. Điều này trả lời một phần câu hỏi dẫn đường 5: bộ giải dạng đóng chỉ cần đủ tốt để khởi tạo. Với câu hỏi 3, MLPnP là mốc rõ ràng cho nhóm "dùng covariance từng điểm", nhưng "ML" của nó mang điều kiện: nhiễu Gauss 2D biết trước, bậc nhất, điểm 3D chính xác.

## 12. Câu hỏi tự kiểm (3–5 câu, hỏi *vì sao* / *khi nào hỏng*)

1. Vì sao không thể dùng thẳng Σ_vv (3×3) làm trọng số, và vì sao chiếu xuống null(vᵀ) lại không làm mất thông tin nào về nhiễu?
2. Vì sao nghiệm eq. (14) không phải ML dù đã dùng đúng P = Σ_vr⁻¹? Chỉ ra hai nguồn sai lệch (gợi ý: λᵢ và ràng buộc SO(3)), và theo mục 7 nguồn nào lớn hơn.
3. Khi nào trọng số của MLPnP không đem lại gì so với `cv2 SOLVEPNP_ITERATIVE`, và khi nào nó còn có thể làm hại (gợi ý: Σ khai báo sai hình dạng; ngoại lai)?
4. NEES trung bình ≈ 6 có chứng minh được ước lượng là tối ưu không? Vì sao ở C5c một covariance sai hình dạng vẫn cho NEES trung bình ≈ 6?
5. Khi nào xấp xỉ mặt phẳng tiếp tuyến tại tia *quan sát* vỡ — nhiễu cỡ bao nhiêu so với tiêu cự, và điều gì xảy ra với σ0² khi đó?

## Trích đoạn nguyên văn làm bằng chứng

- "Thus far, all methods assume, that the observations are equally accurate and free of erroneous correspondences." [tr. 2]
- "Observe, that the covariance matrix Σvv remains singular" [tr. 3]
- "Another way to think about vr is as a residual in the tangent space." [tr. 3]
- "Up to this point, a linear ML estimation of the absolute camera pose is obtained." [tr. 4]
- "In practice we found, that a maximum number of five iterations is sufficient." [tr. 4]
- "For less than 20 points, the algorithm is even faster than EPnP, that is still the fastest PnP solution." [tr. 5]
- "To this point, the only thing we know about the features is, that they are measured with identical accuracy of 1 pixel." [tr. 5]
- "Comparison between the estimated (internal) uncertainty and the uncertainty obtained by the ground truth (external)" [tr. 6]
