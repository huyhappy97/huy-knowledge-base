# Pose Estimation for Augmented Reality: A Hands-On Survey — ghi chú đọc

| | |
|---|---|
| bibkey | `marchand2016arsurvey` |
| Venue, năm | *IEEE Transactions on Visualization and Computer Graphics* 22(12), tr. 2633–2651, 2016; DOI 10.1109/TVCG.2015.2513408 (theo `refs.bib`; bản tôi đọc là bản tác giả, đầu trang ghi "TO APPEAR 2016", nên tôi không tự đối chiếu được số tập/trang) |
| Bản đã đọc | `papers/marchand2016arsurvey.pdf` — nguồn: http://rainbow-doc.irisa.fr/pdf/2016_ieeetvcg_marchand.pdf, 18 trang (bản tác giả; tr. 15–18 là tài liệu tham khảo). Lưu ý: văn bản trích xuất ở tr. 6, 11, 12 lẫn chữ của các bài khác (ảnh chụp nhúng trong Fig. 5, 15, 21) — không trích dẫn từ các đoạn đó |
| Mức đọc | lượt 2 (Keshav) toàn bài; đọc kỹ tới mức cài lại §3.1 (tr. 3–6) và §4.1 (tr. 9–10) |
| Người đọc | Claude (agent), 2026-09-25 — **Huy chưa đọc lại để ký** |
| Mức tin | **giữ A** cho vai trò *bản đồ từ vựng/tổng quan*, kèm cảnh báo: các công thức lõi đúng nhưng **thiếu bước** (khử thang của DLT, chiều cập nhật exp, chuẩn hoá thang của H) — không dùng bài này làm nguồn công thức duy nhất |
| Kiểm chứng | DLT eq. (4)–(5): (a)+(b). Jacobian eq. (11) + cập nhật: (b) — **cập nhật đọc theo chữ thì phân kỳ**. IRLS eq. (13): (b). Số vòng RANSAC 5/72: (a)+(b). Pose từ homography eq. (23), (26)–(27): (b). Tuyên bố "DLT kém chính xác": (b), định tính khớp. Tuyên bố "hình học ≡ đại số cho H": (b) **không khớp hoàn toàn**. Xem mục 7 |

## 1. Bài toán gốc và bối cảnh

Bài không đề xuất phương pháp mới; đây là một bài tổng quan có tính "giáo trình", viết cho sinh viên và kỹ sư đang dùng OpenCV/ViSP/Vuforia như hộp đen [tr. 1, mục "Rationale"]. Luận điểm tổ chức là: trong AR, ẩn số duy nhất là pose camera cTw, vì camera đồ hoạ chỉ cần đặt trùng với camera thật rồi ghép ảnh [§2, tr. 2, Fig. 1] [T]. Vì vậy mọi thứ quy về ước lượng pose, và bài chia theo *dữ liệu có sẵn*: có mô hình 3D (PnP §3.1, tracking theo mô hình §3.2, SLAM §3.3, đăng ký 3D–3D §3.4), cảnh phẳng (homography, template §4), rồi đặc trưng và ghép cặp (§5) [§2, tr. 2]. Bài chủ động bỏ lọc Bayes (EKF) vì cho rằng chúng đang bị thay bởi các cách tất định, trừ khi hợp nhất cảm biến [tr. 2, "Choices have to be made"] [T]. Mỗi phương pháp chính có kèm mã ví dụ (OpenCV và ViSP) làm tài liệu bổ sung [tr. 1; chú thích 1, 3, 8, 9] — tôi không mở được mã đó từ bản PDF (liên kết "here" không mang URL trong văn bản trích xuất).

Phần có ích cho khảo sát PnP là §3.1 (tr. 3–6): P3P, DLT, POSIT, EPnP, cực tiểu hoá sai số tái chiếu bằng Gauss–Newton theo kiểu *virtual visual servoing*, và RANSAC/M-estimator; cùng §4.1.3 (tr. 10) về pose từ homography cho target phẳng.

## 2. Giả thiết — kể cả giả thiết ngầm; bỏ đi thì hỏng ở đâu

Giả thiết bài nêu rõ:

- Camera đã hiệu chỉnh, mọi toạ độ ảnh dùng ở dạng chuẩn hoá x = K⁻¹x̄; bài nói méo ống kính "có thể xử lý dễ dàng" nhưng không trình bày [§3, tr. 3] [T].
- Tương ứng 2D–3D là điểm–điểm và đã có sẵn; việc tìm tương ứng để sang §5 [§3, tr. 3].
- Nhiễu đo là Gauss trên toạ độ ảnh — đây là lý do bài gọi cực tiểu sai số tái chiếu là "gold standard" và là ước lượng hợp lý cực đại [§3.1.2, tr. 4] [T]. Giả thiết này ngầm là đẳng hướng và đồng nhất giữa các điểm, vì eq. (6) không có trọng số (tôi suy ra).
- Gauss–Newton cần khởi tạo đủ gần, nếu không sẽ rơi vào cực tiểu địa phương [§3.1.2, tr. 5, Fig. 3] [T].

Giả thiết ngầm tôi thấy khi cài lại [M]:

- **DLT eq. (4)–(5) cần ít nhất 6 điểm không đồng phẳng.** Bài không nói con số 6 ở đâu cả; ngược lại, bước 2 của RANSAC liệt kê DLT cạnh P3P, POSIT, EPnP như bộ giải cho mẫu tối thiểu "3 cho P3P, 4 cho P4P" [§3.1.3, tr. 5]. Với 4 hay 5 điểm, nhân của A có 4 hay 2 chiều và DLT trả về pose rác; với điểm đồng phẳng nhân có 4 chiều dù có 20 điểm (mục 7, [1]).
- **Nghiệm h của DLT chỉ xác định tới một hệ số thang và dấu.** Bài chỉ nói "cần trực chuẩn hoá ma trận quay thu được" [tr. 4]; nếu chỉ làm đúng như thế thì R đúng nhưng t sai thang (sai số tương đối 0,49 trong thí nghiệm không nhiễu, mục 7 [1]). Phải chia h cho thang của khối 3×3 và chọn dấu để det > 0.
- **Công thức cập nhật "q_{k+1} = q_k ⊕ δq = exp^{δq} q" [tr. 5] chỉ đúng với một quy ước ngầm.** Jacobian eq. (11) là ma trận tương tác điểm của visual servoing, tức đạo hàm theo *vận tốc camera*; nó khớp với nhiễu loạn cTw ← exp(ξ)⁻¹·cTw chứ không phải exp(ξ)·cTw. Đọc chữ "exp^{δq} q" là nhân trái exp(δq) thì Gauss–Newton phân kỳ 50/50 lần (mục 7 [2]).
- **Pose từ homography cần chuẩn hoá thang của H.** Bài viết "(c1, c2, 0tw) = Π⁻¹ 0Hw" [§4.1.3, tr. 10], trong khi Π là ma trận 3×4 không khả nghịch và H từ DLT có thang tuỳ ý; cần chia cho ‖c1‖ và chọn dấu để tz > 0. Và c3 = c1 × c2 chỉ cho R trực giao khi không nhiễu.

## 3. Cơ chế — năm câu, rồi chi tiết có định vị

Năm câu. (1) PnP là bài toán ngược của phép chiếu xi = Π cTw wXi [eq. (3)]; mọi phương pháp chỉ khác nhau ở chỗ cực tiểu hoá sai số gì và có cần khởi tạo hay không. (2) Các bộ giải không cần khởi tạo — P3P, DLT, POSIT, EPnP — dùng để sinh giả thuyết trong RANSAC hoặc để khởi động bước lặp [§3.1.1–3.1.2]. (3) Lời giải "chuẩn vàng" theo tác giả là Gauss–Newton/Levenberg–Marquardt trên 6 tham số pose, cực tiểu tổng bình phương sai số tái chiếu eq. (6), với Jacobian lấy từ visual servoing eq. (11) [tr. 4–5]. (4) Ngoại lai được xử lý bằng RANSAC (từ mẫu tối thiểu, gom tập nhất quán) hoặc IRLS với M-estimator (dùng mọi điểm, giảm trọng số dần) — thay eq. (10) bằng eq. (13) [§3.1.3]. (5) Với target phẳng, pose tách ra được trực tiếp từ homography mặt phẳng–ảnh, tính bằng DLT eq. (23) rồi đọc cột [§4.1.3, eq. (26)–(27)].

Chi tiết:

- **P3P** [§3.1.1, tr. 3]: cách cổ điển là tìm độ sâu ba điểm qua định lý cos, giải đa thức bậc bốn, rồi đăng ký 3D–3D; tối đa bốn nghiệm, cần điểm thứ tư để chọn [tr. 3] [T]. Cách của Kneip (`kneip2011p3p`) tính thẳng cTw qua hai hệ trung gian, tránh bước tìm độ sâu và đăng ký 3D–3D, nên nhanh hơn [tr. 3] [T]. Tác giả khuyên dùng P3P nhanh trong RANSAC và để khởi động bước lặp [tr. 3–4] [T].
- **DLT** [§3.1.2, eq. (4)–(5), tr. 4]: mỗi điểm cho hai hàng Ai của hệ thuần nhất Ah = 0 với h = (r1, tx, r2, ty, r3, tz) gồm 12 ẩn; nghiệm là vector ứng với giá trị kỳ dị nhỏ nhất của A, rồi trực chuẩn hoá R. Bài đánh giá: vì tham số hoá thừa nên "rất nhạy với nhiễu" [tr. 4] [T]. Bài viết "eigenvector của A ứng với trị riêng nhỏ nhất" — A là 2N×12 không vuông, chính xác là vector kỳ dị phải (tức vector riêng của AᵀA) (tôi suy ra).
- **POSIT** [tr. 4]: tuyến tính dưới mô hình chiếu trực giao có tỉ lệ, lặp để quay về phối cảnh; không cần khởi tạo, rẻ, nhưng không hợp với điểm đồng phẳng (có bản mở rộng `oberkampf1996coplanar`) [T].
- **EPnP và họ O(N)** [tr. 4–5]: biểu diễn điểm qua bốn điểm điều khiển ảo, độ phức tạp tuyến tính theo N (`lepetit2009epnp`); OPnP (`zheng2013opnp`), GPnP (`kneip2013npnp`), UPnP (`kneip2014upnp`) được nhắc như O(N) về sau [T].
- **Gauss–Newton / VVS** [eq. (6)–(11), tr. 4–5]: e(q) = x(q) − x [eq. (7)], tuyến tính hoá e(q + δq) ≈ e(q) + J δq [eq. (8)], δq = −J⁺ e [eq. (10)], J là ma trận 2N×6 với hai hàng mỗi điểm (−1/Z, 0, x/Z, xy, −(1+x²), y) và (0, −1/Z, y/Z, 1+y², −xy, −x) [eq. (11)], q = (t, θu) [tr. 4]. Cực tiểu toàn cục thì cần branch-and-bound (`olsson2009bnb`), đắt [tr. 5] [T]; phương pháp sai số đại số của Lu et al. (`lu2000orthogonal`) hội tụ nhanh hơn nhưng vẫn có cực tiểu địa phương [tr. 5] [T].
- **RANSAC** [§3.1.3, tr. 5–6]: bốn bước (rút mẫu tối thiểu → giải pose → đếm điểm có d² ≤ ε → lặp), cuối cùng giải lại bằng PnP chính xác hơn trên toàn bộ inlier; số vòng N = log(1−p)/log(1−(1−η)ⁿ) (không đánh số); với P4P, p = 0,99: 5 vòng ở 10 % ngoại lai, 72 vòng ở 50 % [tr. 6].
- **M-estimator / IRLS** [eq. (12)–(13), tr. 6]: thay d² bằng ρ(d) tăng chậm hơn bậc hai; IRLS dùng ma trận trọng số W chéo, δq = −(WJ)⁺ W e, trọng số tính lại mỗi vòng; Tukey cho trọng số 0 với ngoại lai [T].
- **Homography và pose phẳng** [§4.1, tr. 9–10]: x2 = 2H1 x1 với 2H1 = 2R1 + 2t1 1nᵀ/1d [eq. (19)–(20)]; DLT từ x2 × Hx1 = 0 [eq. (22)–(23)]; hoặc cực tiểu sai số hình học [eq. (24)] hay trực tiếp trên tham số dịch chuyển [eq. (25)]. Với các điểm trên mặt phẳng wZ = 0, 0Hw = (c1 c2 0tw) [eq. (26)–(27)], c3 = c1 × c2 [tr. 10].

Các phần còn lại, tóm tắt ngắn:

- **§3.2 tracking theo mô hình (tr. 6–7)**: cùng khung Gauss–Newton nhưng sai số là khoảng cách điểm-tới-đường viền chiếu d⊥ [eq. (14)], tìm điểm tương ứng dọc pháp tuyến cạnh; bền nhờ Tukey; yếu khi nhầm cạnh hình học với cạnh vân [T]; mô hình phức tạp thì render bằng GPU [Fig. 8].
- **§3.3 SLAM (tr. 7–8)**: lọc (EKF, particle) nhường chỗ cho bundle adjustment theo keyframe [eq. (15)], PTAM tách tracking (một bài PnP như §3.1.2) và mapping [Fig. 10]; phương pháp trực tiếp (DTAM, LSD-SLAM) cần giả thiết quang học nhất quán và baseline nhỏ [T]. Một kiến trúc thực dụng là lập bản đồ offline rồi chỉ chạy PnP online [tr. 8, Fig. 11].
- **§3.4 đăng ký 3D–3D (tr. 8–9)**: eq. (16), giải đóng (Horn) hoặc ICP; KinectFusion dùng ICP điểm–mặt với ghép dữ liệu chiếu.
- **§4.2 căn chỉnh ảnh trực tiếp (tr. 11–12)**: cực tiểu SSD trên warp homography [eq. (28)–(29)], các biến thể forward/inverse compositional, ESM; thay SSD bằng ZNCC, SCV, mutual information để chịu đổi sáng [T].
- **§4.3 (tr. 12)**: pose từng khung (§3) bị rung (jitter), còn tích luỹ chuyển động (§4) bị trôi (drift); nên trộn hai loại [T].
- **§5 (tr. 12–15)**: marker, detector (Harris, FAST, SIFT, SURF, KAZE), descriptor (HOG, nhị phân BRIEF/ORB/BRISK/FREAK), ghép láng giềng gần nhất; kết luận không có phương pháp tốt nhất, FAST hay dùng trong thư viện AR [§5.4] [T].

## 4. Ký hiệu của bài ↔ ký hiệu của khảo sát

| Bài (Marchand et al.) | Khảo sát (`code/common.py`) | Ghi chú |
|---|---|---|
| wX = (wX, wY, wZ, 1)ᵀ | X_w (thêm 1 khi cần dạng thuần nhất) | [eq. (2)] |
| cTw, cRw, ctw | [R \| t] với X_c = R X_w + t | cùng chiều: thế giới → camera [eq. (1)] |
| K (px, py, u0, v0) | K | px = f/lx là tiêu cự theo pixel [tr. 3] |
| x̄ = (u, v, 1)ᵀ | u (pixel) | [eq. (2)] |
| x = K⁻¹x̄ = (x, y, 1)ᵀ | toạ độ chuẩn hoá = f · (1/f_z) | bài dùng mặt phẳng z = 1, không phải tia đơn vị f |
| Π (3×4) | [I \| 0] | eq. (2) viết "=" nhưng thực ra là bằng nhau tới hệ số thang (tôi suy ra) |
| q = (ctw, θu) ∈ se(3) | ξ = (v, ω), cập nhật cTw ← exp(ξ)⁻¹ cTw | chiều cập nhật phải suy ra, xem mục 2 và 7 |
| J [eq. (11)] | ∂x/∂ξ với nhiễu loạn cTw ← exp(ξ)⁻¹ cTw | = ma trận tương tác điểm L_x của visual servoing |
| Zi | độ sâu (X_c)_z | |
| h = (r1, tx, r2, ty, r3, tz) | các hàng của [R \| t] | [eq. (4)–(5)] |
| η, n (RANSAC) | tỉ lệ ngoại lai, cỡ mẫu | bài lẫn ký hiệu: công thức dùng n, câu giải thích gọi là s [tr. 5] |
| 0Hw = (c1 c2 0tw) | H ~ [r1 r2 t] | [eq. (27)]; bài viết "Π⁻¹ 0Hw" |

## 5. Bằng chứng — dữ liệu, phần cứng, baseline, con số kèm điều kiện, số lần lặp

Bài **không có thí nghiệm định lượng nào của riêng nó**. Bằng chứng là các hình minh hoạ định tính: POSIT phẳng rồi tinh chỉnh phi tuyến trên marker bốn điểm [Fig. 4, tr. 6], EPnP trên hộp với tương ứng keypoint [Fig. 5, tr. 6], các ứng dụng AR (bảo tàng, sách, hệ thống thương mại) [Fig. 9–26]. Không có bảng sai số, không có thời gian chạy; bài trỏ sang `zheng2013opnp` và `kneip2014upnp` cho so sánh thời gian theo N [tr. 6] [T].

Con số duy nhất kiểm được là số vòng RANSAC: 5 vòng (10 % ngoại lai) và 72 vòng (50 % ngoại lai) cho P4P với p = 0,99 [tr. 6] — đây là phép tính từ công thức, không phải phép đo; tôi tính lại được đúng (mục 7 [4]).

Các khẳng định so sánh — "DLT không chính xác lắm", "rất nhạy với nhiễu" [tr. 4], "P3P nhanh là lựa chọn trong RANSAC" [tr. 4], "người dùng thường chọn EPnP + RANSAC rồi tinh chỉnh phi tuyến" [tr. 6] — đều là [T], không kèm số.

## 6. Đóng góp thật sự (thường nhỏ hơn abstract)

Đóng góp thật là một **bản đồ từ vựng thống nhất** nối PnP, tracking theo mô hình, SLAM và homography qua cùng một khung tối ưu (sai số hình học + Gauss–Newton + M-estimator), kèm mã ví dụ. Với khảo sát PnP, giá trị chính là (a) cách viết Gauss–Newton pose qua ma trận tương tác của visual servoing [eq. (11)], vốn là cách ViSP cài; (b) một câu trả lời thực dụng cho "dùng gì": bộ giải không cần khởi tạo + RANSAC, rồi tinh chỉnh phi tuyến [tr. 6]. Bài không đưa ra kết quả mới, không phân tích chỗ suy biến của từng bộ giải, và gần như không nói khi nào mỗi phương pháp hỏng ngoài ba câu: DLT nhạy nhiễu, POSIT không hợp điểm đồng phẳng, Gauss–Newton cần khởi tạo tốt [tr. 4–5].

## 7. Kiểm chứng của người ghi chú — script trong `code/`, lệnh chạy, kết quả thật

Script: `code/marchand2016arsurvey_check.py` (seed cố định, ~60 s). Dữ liệu từ `common.make_scene`: điểm đều trên ảnh 640×480, độ sâu 4–8 m, pose ngẫu nhiên, K mặc định (f = 800 px); nhiễu Gauss trên pixel. DLT và Gauss–Newton cài đúng eq. (4)–(5) và (10)–(11) trong toạ độ chuẩn hoá; so với `cv2.solvePnP` (OpenCV 5.0.0) cờ `SOLVEPNP_EPNP` và `SOLVEPNP_ITERATIVE`.

Lệnh: `cd VSLAM/pnp/code && python marchand2016arsurvey_check.py` — kết quả thật (cắt bớt):

```
[1] DLT eq.(4)-(5): số điểm tối thiểu, suy biến phẳng, thang của h (không nhiễu)
    n=4: số chiều nhân (null space) của A = [4], sai số quay trung vị = 172 deg
    n=5: số chiều nhân (null space) của A = [2], sai số quay trung vị = 144 deg
    n=6: số chiều nhân (null space) của A = [1], sai số quay trung vị = 0 deg
    20 điểm đồng phẳng: nhân của A có 4 chiều, sai số quay = 40.2 deg
    đọc chữ (chỉ trực chuẩn hoá R): rot err 0 deg, trans err rel 0.49;  thêm khử thang+dấu: rot 0, trans 3e-15
[2] Jacobian eq.(11) và chiều cập nhật 'exp^{dq} q'
    J số (sai phân) với nhiễu loạn cTw <- exp(xi) cTw: ||J_num - J_eq11||/||J|| = 2.00e+00
    J số (sai phân) với nhiễu loạn cTw <- exp(xi)^-1 cTw: ||J_num - J_eq11||/||J|| = 2.27e-07
    hội tụ về nghiệm đúng (50 lần, lệch ~3 deg / 5 cm): literal 0/50, visp 50/50
[3] Sai số vs nhiễu (200 cảnh/ô, trung vị; GN = eq.(10)-(11) thuần, không damping, 30 vòng)
    cột: sai số quay [deg] / sai số tịnh tiến tương đối [%]
    n= 6 s=1.0px | DLT: 1.848/ 24.15 DLT+GN: 0.265/  2.93 EPnP: 0.292/  3.57 EPnP+GN: 0.262/  2.93 ITER: 0.265/  2.93 | DLT+GN phân kỳ 2/200
    n= 6 s=5.0px | DLT:12.584/267.80 DLT+GN: 1.530/ 16.55 EPnP: 1.407/ 15.73 EPnP+GN: 1.261/ 13.78 ITER: 1.519/ 16.48 | DLT+GN phân kỳ 11/200
    n=10 s=1.0px | DLT: 0.431/  7.35 DLT+GN: 0.169/  1.91 EPnP: 0.187/  2.17 EPnP+GN: 0.169/  1.91 ITER: 0.169/  1.91 | DLT+GN phân kỳ 0/200
    n=10 s=5.0px | DLT: 3.004/ 58.93 DLT+GN: 0.905/  9.53 EPnP: 1.048/ 12.10 EPnP+GN: 0.858/  9.01 ITER: 0.890/  9.39 | DLT+GN phân kỳ 8/200
    n=50 s=1.0px | DLT: 0.147/  1.87 DLT+GN: 0.071/  0.73 EPnP: 0.083/  1.00 EPnP+GN: 0.071/  0.73 ITER: 0.071/  0.73 | DLT+GN phân kỳ 0/200
    n=50 s=5.0px | DLT: 0.687/ 19.72 DLT+GN: 0.345/  3.50 EPnP: 0.385/  4.71 EPnP+GN: 0.345/  3.50 ITER: 0.345/  3.50 | DLT+GN phân kỳ 0/200
  [PASS] DLT kém hơn tinh chỉnh phi tuyến (EPnP+GN) ở 12/12 ô
    tỉ số sai số quay trung vị DLT / EPnP+GN: min 1.74, max 10.39
  [PASS] EPnP+GN và cv2 ITERATIVE về cùng cực tiểu ở >= 90% số cảnh (RMSE tái chiếu trùng tới 1e-6) — trùng 96.0%, EPnP+GN thấp hơn hẳn 4.0%
  [PASS] GN thuần khởi tạo bằng DLT có lúc phân kỳ (bài: 'cần khởi tạo tốt') — tổng 36/2400 lần; ô không phân kỳ: 7/12
[4] Số vòng RANSAC N = log(1-p)/log(1-(1-eta)^n), p=0.99, n=4 (tr. 5-6)
    eta=0.1: N = 4.31 -> ceil 5 (bài ghi 5)
    eta=0.5: N = 71.36 -> ceil 72 (bài ghi 72)
    (ghi chú) nếu bộ giải mẫu là DLT (cần 6 điểm) thì với eta=0.5: N = 293
[5] Ngoại lai (n=60, nhiễu 1 px, ngoại lai = pixel ngẫu nhiên đều trên ảnh; 100 cảnh/ô; sai số quay [deg])
    ngoại lai 10%:
      GN               trung vị  180.000 deg, tỉ lệ > 1 deg: 100%
      IRLS-DLT         trung vị  180.000 deg, tỉ lệ > 1 deg:  95%
      IRLS-track       trung vị    0.072 deg, tỉ lệ > 1 deg:   0%
      IRLS-track-MADc  trung vị    1.468 deg, tỉ lệ > 1 deg:  52%
      RANSAC-DLT6      trung vị  180.000 deg, tỉ lệ > 1 deg:  67%
      RANSAC-P3P       trung vị    0.080 deg, tỉ lệ > 1 deg:   0%
    ngoại lai 50%:
      IRLS-track       trung vị    0.838 deg, tỉ lệ > 1 deg:  42%
      RANSAC-DLT6      trung vị  180.000 deg, tỉ lệ > 1 deg:  91%
      RANSAC-P3P       trung vị    0.128 deg, tỉ lệ > 1 deg:   6%
    DLT trên đúng 6 inlier (nhiễu 1 px): sai số tái chiếu lớn nhất trên chính 6 điểm, trung vị 42.3 px (sau khi trực chuẩn hoá R)
[6] Target phẳng: DLT homography eq.(23) -> pose eq.(26)-(27), 200 cảnh/ô, n=20
    sigma=1.0px: ||R^T R - I|| trung vị 9.62e-03; đọc chữ (không chuẩn thang) trans err 0.86; rot err: H-DLT 0.326, H-hình học eq.(24) 0.309, H-DLT+GN(pose) 0.184, cv2 IPPE 0.235 deg
    sigma=3.0px: ||R^T R - I|| trung vị 2.75e-02; đọc chữ (không chuẩn thang) trans err 0.85; rot err: H-DLT 1.051, H-hình học eq.(24) 1.006, H-DLT+GN(pose) 0.553, cv2 IPPE 0.727 deg
Tổng: 21/21 PASS, thời gian 57.6s
```

("180 deg" là quy ước của script cho lần chạy thất bại: GN phân kỳ ra NaN, hoặc RANSAC không có consensus ≥ 6 điểm. "PASS" nghĩa là *dự đoán của tôi* về hành vi đúng/sai được xác nhận, kể cả khi dự đoán là "công thức đọc theo chữ thì hỏng".)

Đọc kết quả:

- **Công thức lõi đúng sau khi bổ sung** [M]. Ma trận Ai eq. (5) đúng: với 6 điểm không nhiễu, DLT (đã khử thang/dấu) cho pose chính xác tới 1e-15. Jacobian eq. (11) khớp sai phân số tới 2e-7 — nhưng **chỉ** với nhiễu loạn cTw ← exp(ξ)⁻¹ cTw; với exp(ξ)·cTw sai lệch 200 %, và cập nhật theo chữ "exp^{δq} q" không hội tụ lần nào (0/50). Số vòng RANSAC 5 và 72 đúng.
- **Tuyên bố "DLT kém chính xác, nhạy nhiễu" [tr. 4]: khớp định tính** [M]. Trong 12 cấu hình (n ∈ {6, 10, 50}, σ ∈ {0,5; 1; 2; 5} px), sai số quay trung vị của DLT gấp 1,74–10,4 lần EPnP+GN; nặng nhất ở n = 6 (σ = 5 px: 12,6° và sai số tịnh tiến 268 %). Bài không đưa con số nào để so.
- **Tuyên bố "Gauss–Newton cần khởi tạo tốt" [tr. 5]: khớp** [M]. GN thuần (không damping) khởi tạo bằng DLT phân kỳ 36/2400 lần, toàn ở n = 6 hoặc σ = 5 px — đúng nơi DLT tệ nhất. Khởi tạo bằng EPnP thì EPnP+GN trùng cực tiểu với cv2 ITERATIVE ở 96 % cảnh, 4 % còn lại EPnP+GN có RMSE thấp hơn — tôi đoán vì cv2 ITERATIVE khởi tạo bằng DLT với điểm không phẳng (tôi suy ra từ việc cột ITER gần như trùng cột DLT+GN ở n = 6; chưa đối chiếu mã OpenCV).
- **DLT trong RANSAC là lựa chọn tệ** [M]. Bài liệt kê DLT như bộ giải cho mẫu tối thiểu [tr. 5]. Thực tế DLT cần mẫu 6 điểm (293 vòng thay vì 72 ở 50 % ngoại lai), và vì ma trận 3×3 từ 6 điểm nhiễu cách xa SO(3), sau khi trực chuẩn hoá thì chính 6 điểm mẫu có sai số tái chiếu trung vị 42 px (σ = 1 px). Với ngưỡng 3 px, RANSAC-DLT6 thất bại 67–91 % số lần, còn RANSAC-P3P (cv2.solveP3P) + GN chỉ 0–6 %. Điều này ủng hộ lời khuyên dùng P3P trong RANSAC của chính bài [tr. 4].
- **IRLS chỉ tốt khi khởi tạo tốt** [M]. Eq. (13) với Tukey khởi tạo từ pose đúng lệch khoảng 3°/5 cm (giống tracking theo khung trước) khử sạch 10–30 % ngoại lai; khởi tạo bằng DLT trên dữ liệu bẩn thì hỏng ngay từ 10 %. Kết quả phụ thuộc cách ước lượng thang: dùng MAD quanh trung vị (thay vì quanh 0) thì mọi trọng số về 0 ở vòng đầu khi pose khởi tạo lệch, và IRLS kẹt (52 % số lần > 1° ở 10 % ngoại lai). Bài không nói gì về chọn thang, chỉ trỏ sang [126], [24] [tr. 6].
- **Target phẳng** [M]. Pose từ H đúng khi không nhiễu (sau khi chuẩn thang); không chuẩn thang thì t sai 85–115 %. Với nhiễu, c3 = c1 × c2 cho ‖RᵀR − I‖ ≈ 1e-2 (σ = 1 px), nên phải chiếu về SO(3); tinh chỉnh eq. (6) giảm sai số quay khoảng một nửa (0,326° → 0,184° ở σ = 1 px). Tuyên bố "sai số hình học eq. (24) và đại số của DLT ở đây là tương đương [48]" [tr. 10] **không đúng theo nghĩa đen** trong thí nghiệm này: H từ eq. (24) cho sai số quay trung vị thấp hơn khoảng 5 % (0,309 so với 0,326° ở σ = 1 px; 1,006 so với 1,051° ở σ = 3 px). Tôi chưa kiểm ý nghĩa thống kê của khác biệt, và DLT ở đây chưa chuẩn hoá kiểu Hartley.

## 8. Chỗ tôi không tin

- **"Minimal" mà không phải minimal.** Liệt kê DLT (và POSIT) cạnh P3P như bộ giải cho mẫu tối thiểu của RANSAC [§3.1.3, bước 2, tr. 5] dễ gây hiểu lầm: DLT không chạy được với 3 hay 4 điểm, và ngay cả khi có 6 điểm thì là bộ sinh giả thuyết rất kém (mục 7 [5]). Bài không nói con số 6, cũng không cảnh báo DLT suy biến với điểm đồng phẳng — trong khi lại cảnh báo điều đó cho POSIT [tr. 4].
- **Công thức in không tự chạy được.** Ba chỗ nếu cài đúng theo chữ thì sai: DLT thiếu khử thang của t [tr. 4]; cập nhật "exp^{δq} q" sai chiều so với J eq. (11) [tr. 5]; "Π⁻¹ 0Hw" không định nghĩa và thiếu chuẩn hoá thang [tr. 10]. Với một bài tự nhận "hands-on" và "gần như tự đủ" [tr. 1], đây là lỗi đáng kể; có thể mã bổ sung đã làm đúng, nhưng tôi không mở được mã đó.
- **"Tương đương" giữa sai số hình học và đại số cho homography [tr. 10]** có dẫn [48] (Hartley–Zisserman, `hartley2004`) nhưng không nói điều kiện; theo hiểu biết của tôi, trong sách đó hai sai số trùng nhau với biến đổi affine, không phải homography tổng quát (tôi suy ra, chưa mở lại sách để đối chiếu số mục). Thí nghiệm của tôi cho thấy khác biệt nhỏ nhưng khác 0.
- **"Gold standard" và "tối ưu"** [tr. 4]: eq. (6) là ước lượng hợp lý cực đại chỉ khi nhiễu Gauss đẳng hướng và đồng nhất, và "tối ưu" chỉ đúng khi GN tới được cực tiểu toàn cục — bài tự nói ngay sau đó rằng GN có thể kẹt cực tiểu địa phương [tr. 5]. Hai câu này cần đi cùng nhau.
- **Khẳng định xu hướng không có số**: "EKF ngày càng ít được dùng" [tr. 2], "người dùng thường chọn EPnP + RANSAC" [tr. 6], "FAST hay được dùng trong thư viện AR" [§5.4] — đều là nhận định của tác giả, không có khảo sát hay trích dẫn định lượng.
- Các lỗi nhỏ về ký hiệu: E(q) = ‖e(q)‖ rồi ngay đó E(q) = eᵀe [eq. (7), (9)]; công thức RANSAC dùng n nhưng câu giải thích gọi là s [tr. 5]; eq. (24) dùng 1H2 trong khi eq. (19)–(23) dùng 2H1.

## 9. Chỗ tôi chưa hiểu (→ `99-chua-biet.md`)

- Vì sao tác giả gọi J eq. (11) là "Jacobian của e(q) theo q" [tr. 4–5] trong khi q = (t, θu) là tham số hoá tuyệt đối; thật ra J là đạo hàm theo một nhiễu loạn cục bộ trên SE(3). Cách viết này có tương đương với GN trên đa tạp (kiểu "boxplus") không, và nếu tham số hoá q tuyệt đối thì Jacobian đúng khác eq. (11) ra sao?
- Trong ViSP, chiều cập nhật là exp(v)⁻¹ hay exp(−v)? Tôi đã kiểm bằng số rằng exp(δq)⁻¹ hội tụ, nhưng chưa đọc mã ViSP hay [22] (Chaumette–Hutchinson, không có trong `refs.bib`) để xác nhận quy ước dấu của vận tốc.
- Chọn thang cho Tukey trong IRLS pose: ViSP dùng MAD quanh trung vị hay quanh 0, và có ngưỡng dưới cho thang không? Thí nghiệm của tôi cho thấy lựa chọn này quyết định IRLS có kẹt hay không khi khởi tạo lệch.
- Hai sai số (hình học eq. (24) và đại số của DLT) cho homography khác nhau bao nhiêu khi đã chuẩn hoá Hartley, và khác biệt đó có còn ý nghĩa khi pose được tinh chỉnh bằng eq. (6) sau cùng không?
- cv2 `SOLVEPNP_ITERATIVE` khởi tạo bằng gì khi điểm không phẳng và n ≥ 6 — DLT như tôi đoán, hay cách khác?

## 10. Quan hệ với các bài khác trong `refs.bib`

- `lepetit2009epnp`, `zheng2013opnp`, `kneip2014upnp`, `kneip2013npnp`: bài chỉ giới thiệu như các bộ giải O(N), không phân tích [tr. 4–5]. Thí nghiệm của tôi khớp với lời bài: EPnP tốt hơn DLT rõ rệt, và EPnP + GN là cấu hình mặc định hợp lý.
- `kneip2011p3p`: bài khuyên dùng trong RANSAC [tr. 3–4]; khớp mục 7 [5].
- `fischler1981ransac`: nguồn của RANSAC và công thức số vòng [tr. 5]; bài nói RANSAC được đề xuất "để giải P3P" — khớp với ghi chú `notes/fischler1981ransac.md` (bài gốc giới thiệu RANSAC cùng bài toán định vị LDP/PnP).
- `dementhon1995posit`, `oberkampf1996coplanar`: POSIT và bản cho điểm đồng phẳng [tr. 4].
- `lu2000orthogonal`: được nhắc như cách lặp trên sai số đại số, nhanh nhưng còn cực tiểu địa phương [tr. 5]. Nhan đề bài gốc lại là "globally convergent" — hai cách nói này chưa khớp nhau; cần đọc `lu2000orthogonal` để phân xử.
- `olsson2009bnb`: tối ưu toàn cục bằng branch-and-bound, đắt [tr. 5].
- `hartley2004` ([48] trong bài, bản 2001): nguồn của DLT, "gold standard" và tuyên bố tương đương hình học/đại số.
- `collins2014ippe`: không được nhắc (bài ra trước khi IPPE phổ biến trong OpenCV); với target phẳng, bài chỉ trình bày cách đọc cột của H, còn IPPE giải trực tiếp và xử lý lưỡng nghĩa — thứ bài không nhắc tới [M].
- `lepetit2005survey`: tổng quan cùng chủ đề, bài trích như [65] (monograph ngắn về tracking 3D) [tr. 2].
- Không có trong `refs.bib`: [22] Chaumette & Hutchinson 2006 (visual servoing), [24] Comport et al. 2006 (VVS, TVCG), [78] Marchand & Chaumette 2002 (virtual visual servoing), [57] PTAM, [126] Stewart 1999 (robust estimation).

## 11. Nó đổi gì trong suy nghĩ

Trước khi đọc, tôi coi "DLT + Gauss–Newton" là một cặp đơn giản, tự chạy được. Sau khi cài đúng theo chữ, tôi thấy phần lớn công sức nằm ở những bước bài bỏ qua: khử thang và dấu, chiều của nhiễu loạn trên SE(3), chuẩn hoá H. Bài học rút ra cho khảo sát là mỗi công thức lấy từ một tổng quan phải qua cửa (b), vì chính các chi tiết quy ước mới là thứ hỏng. Về nội dung, bài củng cố thứ tự thực dụng: P3P (hoặc EPnP) + RANSAC → tinh chỉnh sai số tái chiếu (có M-estimator nếu đang tracking), và cho thấy DLT chỉ nên dùng làm khởi tạo khi có nhiều điểm không đồng phẳng. Bài không đổi hiểu biết của tôi về hình học của từng bộ giải — thứ đó phải lấy từ các bài gốc.

## 12. Câu hỏi tự kiểm

1. Vì sao DLT eq. (4)–(5) cần ít nhất 6 điểm, và vì sao nó suy biến khi mọi điểm đồng phẳng dù có bao nhiêu điểm đi nữa? Nhân của A khi đó có mấy chiều?
2. Nếu cài cập nhật pose là cTw ← exp(δq)·cTw với J của eq. (11), vì sao Gauss–Newton phân kỳ, và cần đổi gì — J hay chiều cập nhật?
3. Khi nào IRLS eq. (13) có thể thay RANSAC, và khi nào không? Vai trò của khởi tạo và của cách ước lượng thang Tukey là gì?
4. Vì sao cực tiểu eq. (6) là ước lượng hợp lý cực đại, và giả thiết nhiễu nào bị vi phạm thì "gold standard" không còn là tối ưu?
5. Với target phẳng, vì sao c3 = c1 × c2 không cho ma trận quay hợp lệ khi có nhiễu, và vì sao cần chia H cho ‖c1‖ trước khi đọc t?

## Trích đoạn nguyên văn làm bằng chứng

- "Since a fourth order polynomial equation as to be solved, the problem features up to four possible solutions." [tr. 3]
- "Obviously and unfortunately, being over-parameterized, this solution is very sensitive to noise" [tr. 4]
- "A drawback is that POSIT is not directly suited for coplanar points." [tr. 4]
- "Minimizing this reprojection error provides the Maximum Likelihood estimate when a Gaussian noise is assumed on measurements" [tr. 4]
- "However, the algorithm requires a good initial guess cTw in order to converge to the globally optimal solution. If this is not the case only a local minima is attained." [tr. 5]
- "users tend to favor a PnP that does not require any initialization (such as EPnP) along with a RANSAC." [tr. 6]
- "For AR application, rather than computational efficiency (as soon as real-time requirement are met), accuracy is the key criterion in order to avoid jitter effects." [tr. 6]
- "Note that considering the geometric distance as in equation (24) or the algebraic one as for the DLT is, here, equivalent [48]." [tr. 10]
