# Uncertainty-Aware Camera Pose Estimation from Points and Lines — ghi chú đọc

| | |
|---|---|
| bibkey | `vakhitov2021uncertainty` |
| Venue, năm | IEEE/CVF CVPR 2021 (CORE A\*) |
| Bản đã đọc | `papers/vakhitov2021uncertainty.pdf`. Nguồn: bản CVF open access (chân trang đánh số 4659–4668), 10 trang gồm 8 trang nội dung và 2 trang tài liệu tham khảo. **Không có** tài liệu bổ sung (supp. mat.), dù bài dẫn nó nhiều lần. Mã: https://alexandervakhitov.github.io/uncertain-pnp/ (theo [tr. 1]; tôi chưa mở). |
| Mức đọc | lượt 2 cho toàn bài, lượt 3 cho §3.2–§3.5 (lan truyền bất định vào covariance của residual) |
| Người đọc | Claude (agent), 2026-09-25 — **Huy chưa đọc lại để ký** |
| Mức tin | giữ **B**. Venue đầu ngành, nhưng chưa thấy người ngoài nhóm tái lập. Bài có vài chỗ chữ và bảng không khớp nhau (mục 8). Nguyên lý cho điểm thì tôi tái lập được bằng mô phỏng (mục 7), còn bộ giải của chính họ thì chưa. |
| Kiểm chứng | eq. (4), (13), (21) và mệnh đề đẳng hướng hoá ở §3.6: qua cửa **(b)** (Monte Carlo, `code/vakhitov2021uncertainty_check.py`, phần 1). Eq. (4) cũng qua cửa **(a)**: tôi tự suy lại được và thấy nó bỏ một số hạng bậc hai (mục 3). Eq. (8), (14), (22) cho đường: **chưa kiểm**. Eq. (17) cho DLSU: **chưa kiểm**. |

## 1. Bài toán gốc và bối cảnh

Trong định vị theo bản đồ thưa (VO/SLAM, SfM), toạ độ 3D của đặc trưng đến từ phép tam giác hoá nên có sai số. Sai số độ sâu của stereo tăng theo bình phương khoảng cách, nên độ chính xác của các điểm trong cùng một bản đồ có thể chênh nhau vài bậc [T] [§1, tr. 1]. Các bộ giải PnP phổ biến (EPnP, DLS, OPnP, UPnP) coi 3D và 2D đều chính xác [T] [§1, tr. 1]. Nhóm "biết covariance" (CEPPnP `ferraz2014cepnp`, MLPnP `urban2016mlpnp`) mới chỉ đưa bất định của phát hiện 2D vào, và chỉ làm cho điểm [T] [§2, tr. 2]. Với đường thì các bộ giải PnPL trước đó (EPnPL, OPnPL của `vakhitov2016pnpl`) không dùng bất định nào [T] [tr. 1].

Cái khó nằm ở chỗ này (tôi suy ra): khi điểm 3D có nhiễu, covariance của residual **phụ thuộc pose** vì nó chứa R Σx Rᵀ và độ sâu. Bộ giải dạng đóng lại cần covariance đó *trước khi* biết pose. Bài giải quyết bằng xấp xỉ: độ sâu trung bình cộng với Σx đẳng hướng, hoặc một pose giả thuyết lấy từ RANSAC. Ở bước tinh chỉnh thì bài dùng IRLS.

## 2. Giả thiết — kể cả giả thiết ngầm; bỏ đi thì hỏng ở đâu

Các giả thiết tác giả nói ra:

- Điểm 3D, các đầu mút đoạn thẳng 3D và hình chiếu 2D đều mang nhiễu Gauss trung bình 0, với covariance Σx, Σp, Σq, Σu **đã biết** [§3.1, tr. 2]. Nhiễu của đường 2D được mô hình hoá là nhiễu Gauss cộng vào khoảng cách điểm–đường, phương sai σl² [§3.1, tr. 2–3].
- Camera đã hiệu chỉnh và toạ độ được chuẩn hoá (K = I) [§3.1, tr. 3].
- Biết trước độ sâu trung bình của cảnh d̄. Có thể có thêm một pose giả thuyết thô (R̂, t̂) [§3.1, tr. 3].
- Nhiễu của p, q và nhiễu phát hiện đường độc lập với nhau. Tác giả tự nhận đây là một đơn giản hoá [T] [§3.2, tr. 3].

Các giả thiết ngầm (tôi suy ra):

- **Nhiễu 3D độc lập giữa các điểm.** Trong SfM/SLAM thật, các điểm được tam giác hoá từ cùng các pose keyframe nên có tương quan. Sai số pose của keyframe tham chiếu dịch cả cụm điểm theo cùng một hướng. Mô hình của bài sẽ đếm cùng một sai số nhiều lần như thể mỗi điểm là một phép đo độc lập, nên đánh giá quá cao thông tin.
- **Bậc một là đủ.** Eq. (4) bỏ số hạng tích ξ(3)ζ. Eq. (21) tuyến tính hoá π. Phần 1 của mục 7 cho thấy cả hai vẫn đúng tới khoảng 1,5% ngay cả khi σ3D = 0,5 ở độ sâu khoảng 5,5.
- **Σx là covariance của điểm trong hệ thế giới, và hệ thế giới coi như không có sai số.** Nếu bản đồ trôi (drift), bất định tuyệt đối không còn tách rời giữa các điểm (liên quan ý trên).
- **Các bộ giải "không có giả thuyết" (EPnPU, DLSU) chỉ dùng một độ sâu d̄ cho mọi điểm** [eq. (13)]. Khi cảnh có dải độ sâu rộng, trọng số tương đối giữa điểm gần và điểm xa bị sai (tôi suy ra). Trong mô phỏng của tôi (độ sâu 4..8), việc lấy độ sâu từng điểm từ pose giả thuyết (LUz\*) gần như không đổi gì so với dùng d̄ (LU) (mục 7).
- **Bỏ số hạng log det Σ(θ).** Khi covariance phụ thuộc pose, cực tiểu tổng Mahalanobis không còn là cực đại likelihood thật. Bài không nói gì về điều này (tôi suy ra).

## 3. Cơ chế — năm câu, rồi chi tiết có định vị

**Năm câu.** (1) Viết residual đại số của điểm, r = x̂(1:2) − u·x̂(3) với x̂ = R x + t, rồi lan truyền nhiễu của x (qua R) và nhiễu của u để được covariance 2×2 cho residual [eq. (1)–(4)]. (2) Với đường, residual là tích vô hướng của hệ số đường 2D l với hai đầu mút 3D trong hệ camera, và covariance là đường chéo 2×2 [eq. (5)–(8)]. (3) Để khỏi phụ thuộc R, họ thay Σx bằng σ²I với σ² = trace(Σx)/3 và thay độ sâu bằng d̄. Covariance khi đó chỉ còn phụ thuộc số liệu đo [eq. (13)–(14)]. Bản "\*" lấy độ sâu (và theo §3.2 là cả Σx) từ pose của RANSAC. (4) Covariance này làm trắng hệ tuyến tính của EPnP/EPnPL (ma trận M_U) và làm trọng số cho hàm mục tiêu kiểu DLS/OPnP giải bằng Groebner basis với tham số hoá Cayley [eq. (12), (17)]. (5) Bước tinh chỉnh là motion-only BA trên sai số tái chiếu, dùng covariance Σu + J R Σx Rᵀ Jᵀ tính lại sau mỗi vòng Gauss-Newton, theo kiểu IRLS [eq. (21), §3.5].

**Chi tiết residual điểm [§3.2, tr. 3].** Hàm residual là eq. (1). Covariance của điểm trong hệ camera là Σx̂ = R Σx Rᵀ, được chia khối thành [S w; wᵀ γ] [eq. (2)]. Thay x̂ = E x̂ + ξ và u = E u + ζ vào (1) ta được (3), rồi lấy kỳ vọng thì ra
Σr = S + γ u uᵀ + (x̂(3))² Σu − (u wᵀ + w uᵀ) [eq. (4)].
Tôi tự suy lại (cửa (a)). Nếu u và x̂(3) là giá trị kỳ vọng thì covariance **đúng** bằng (4) cộng thêm γ Σu, là phần đến từ số hạng tích ξ(3)ζ trong (3). Bài không nêu rằng đã bỏ số hạng này. Nó là bậc hai: γ/(x̂(3))² ≈ σ3D²/z². Kiểm Monte Carlo cho thấy nó không đáng kể, vì thêm hay không thêm thì sai lệch vẫn là 0,22% và 0,52% (mục 7, C1) [M]. Còn một điểm nữa: (4) thực ra được đánh giá tại u **đo được** và tại x̂(3) **xấp xỉ** (d̄ hoặc độ sâu tính từ pose giả thuyết), chứ không tại giá trị kỳ vọng [§3.2, tr. 3].

**Chi tiết residual đường [§3.2, tr. 3].** Ta có r_ln = [lᵀ p̂; lᵀ q̂] [eq. (5)]. Nhiễu phát hiện đường có phương sai σl² khi đo trên mặt phẳng ảnh chuẩn hoá. Đổi sang residual đại số của một điểm ở độ sâu λ thì phương sai phải nhân λ² [eq. (6)–(7)]. Kết quả là Σ_rln = σl² diag(λp², λq²) + diag(lᵀΣp̂ l, lᵀΣq̂ l) [eq. (8)]. Với EPnPLU và DLSLU, λ được thay bằng d̄ và Σ được đẳng hướng hoá [tr. 3]. Phần đường tôi **chưa kiểm số**.

**EPnPU / EPnPLU [§3.3, tr. 3–4].** Hai thay đổi so với EPnP (`lepetit2009epnp`):
(i) Chọn điểm điều khiển bằng PCA có trọng số σx,i⁻² [eq. (10)→(11)], vì PCA thường bị giảm độ chính xác khi có nhiễu 3D ("thí nghiệm sơ bộ", không kèm số) [T] [tr. 4].
(ii) Hệ ‖M vec(Ĉ)‖² [eq. (12)] được thay bằng ma trận "uncertainty-augmented" M_U, dùng covariance đẳng hướng hoá
Σ_rpt^EPnP = σx² I + d̄² Σu + σx² u uᵀ [eq. (13)] và Σ_rln^EPnP = σl² d̄² I + ‖l‖² diag(σp², σq²) [eq. (14)].
Tôi kiểm được rằng (13) đúng là (4) với S = σ²I, w = 0, γ = σ², x̂(3) = d̄ (mục 7, C2). Bài **không viết ra** M_U được dựng thế nào (làm trắng từng khối 2 hàng bằng Σ^{-1/2}, hay cách khác). Bài cũng không nói có giữ phần N = 2..4 và bước tinh chỉnh β của EPnP hay không. Bản EPnPU\* "vẫn dùng xấp xỉ đẳng hướng, chỉ dùng pose để ước lượng độ sâu" [tr. 4]. Câu này mâu thuẫn một phần với §3.2, nơi bản "\*" "tính ước lượng covariance điểm 3D" từ pose [tr. 3].

**DLSU / DLSLU [§3.4, tr. 4].** Giữ tham số hoá Cayley R(s) [eq. (15)] nhưng bỏ sai số không gian vật (object-space error) của DLS gốc (`hesch2011dls`), thay bằng residual đại số (1)/(5) có trọng số: ½ Σ r_kᵀ Σ_rk⁻¹ r_k [eq. (16)–(17)]. Trong đó covariance "lấy như trường hợp EPnP", tức eq. (13)–(14) [tr. 4]. Đặt ∂/∂t = 0 để khử t, nhân hàm mục tiêu với (1+‖s‖²)², rồi đặt gradient theo s bằng 0 thì được hệ đa thức bậc ba, 3 ẩn. Họ giải hệ này bằng solver sinh tự động theo `larsson2017syzygy`, với ma trận khử kích thước 27×27 như DLS [tr. 4]. Có thêm tuỳ chọn tinh chỉnh chính (17) bằng Newton với Hessian giải tích [tr. 4]. Tác giả nói chọn residual đại số vì nhanh hơn mà độ chính xác "tương tự", nhưng bằng chứng nằm trong supp. mat. mà tôi không có [T] [tr. 4].

**Tinh chỉnh có bất định [§3.5, tr. 5].** Hàm mục tiêu là motion-only BA [eq. (18)], dùng residual chuẩn vàng của điểm [eq. (19)] và của đường [eq. (20)].
- "Standard refinement": Σ = Σu cho điểm và σl² I cho đường [tr. 5].
- "Uncertain refinement": Σ_r̄pt = Σu + J(x̂) R Σx Rᵀ Jᵀ(x̂) [eq. (21)] và Σ_r̄ln = σl² I + diag(lᵀΣπ_p̂ l, lᵀΣπ_q̂ l) [eq. (22)], trong đó J là Jacobian của π.
Vì các covariance này phụ thuộc pose nên họ phân biệt hai cách. Cách "full uncertain" là tối ưu phi tuyến tổng quát. Cách "(iterative) uncertain" giống IRLS: mỗi vòng Gauss-Newton tính lại (21)–(22) tại pose hiện tại [tr. 5]. Như vậy **câu trả lời cho câu hỏi "covariance phụ thuộc pose được đánh giá ở đâu"** gồm ba mức. Solver không có giả thuyết dùng d̄ cộng Σ đẳng hướng. Solver "\*" dùng pose của RANSAC. Tinh chỉnh IRLS dùng pose của vòng lặp trước. Mục 7 cho thấy khác biệt giữa đánh giá tại pose IRLS và tại pose thật là không đáng kể (GU so với GUgt).

**Lấy bất định [§3.6, tr. 5].** Với 2D, dùng Σu = σo² I với σo = κ^{o−1} ε, trong đó o là tầng pyramid của đặc trưng. Với điểm 3D, lan truyền sai số sau tam giác hoá (dẫn `hartley2004`, ch. 5). Với đoạn thẳng, họ tái dựng hai đầu mút bằng residual điểm ở camera đầu và residual đường ở các camera còn lại (chi tiết trong supp. mat.). Họ cũng chứng minh σ² = trace(Σx)/3 là xấp xỉ đẳng hướng tốt nhất theo chuẩn Frobenius [tr. 5]; tôi kiểm lại ở C4.

## 4. Ký hiệu của bài ↔ ký hiệu của khảo sát

| Bài | Khảo sát | Ghi chú |
|---|---|---|
| x (điểm 3D), p, q (đầu mút đoạn thẳng) | X_w | hệ thế giới |
| x̂ = R x + t | X_c = R X_w + t | cùng quy ước thế giới → camera |
| R, t | R, t | |
| K = I (giả định) [tr. 3] | K | bài làm trên toạ độ chuẩn hoá; u của bài ≈ K⁻¹[u;1] (2 thành phần đầu) của khảo sát |
| u (điểm 2D) | u sau khi chuẩn hoá bằng K⁻¹ | **không** phải tia đơn vị f; u của bài có thành phần thứ ba bằng 1 |
| x̂(3), λp, λq | độ sâu (X_c)_z | |
| l, ‖l(1:2)‖ = 1 | (chưa có ký hiệu chung) | hệ số đường 2D chuẩn hoá |
| Σx, Σu, σl² | covariance 3D, 2D, phương sai khoảng cách điểm–đường | |
| d̄ | độ sâu trung bình của cảnh | |
| C, α, Ĉ | điểm điều khiển, toạ độ barycentric (như EPnP) | |
| s (Cayley) | — | R(s) theo eq. (15) |
| π(x̂) = x̂(1:2)/x̂(3) | phép chiếu chuẩn hoá | |

## 5. Bằng chứng — dữ liệu, phần cứng, baseline, con số kèm điều kiện, số lần lặp

**Phần cứng và cài đặt.** Mọi phương pháp chạy bằng MATLAB trên laptop Core i7 1,3 GHz, RAM 16 GB [§4, tr. 6]. Baseline gồm EPnP, DLS, OPnP (`zheng2013opnp`), CEPPnP, MLPnP, cộng P3P (`kneip2011p3p`) trong RANSAC (`fischler1981ransac`). Với điểm + đường thì baseline là EPnPL và OPnPL [§4, tr. 5].

**Mô phỏng [§4.1, tr. 6–7].** Camera 640×480, f = 800. Điểm và đầu mút đoạn thẳng nằm trong hộp [−2,2]×[−2,2]×[4,8] tính trong hệ camera. Các điểm được chia thành 10 nhóm đều nhau. Nhiễu 3D tăng từ σ = 0,05 đến 0,5 và là nhiễu không đẳng hướng: bộ ba {σ, σ1, σ2} với σ1, σ2 ∈ (0, σ], xoay ngẫu nhiên. Nhiễu 2D tăng từ σ = 1 đến 10 px. Mỗi cấu hình chạy 400 lần thử, n_pt = 10..110, n_l = n_pt [tr. 6–7]. Bản "\*" được cấp pose giả thuyết từ P3P trên 3 điểm ngẫu nhiên [tr. 7]. Kết quả chỉ được trình bày dạng đồ thị [Fig. 3], không có bảng số:
- [Đ] Khi chỉ có nhiễu 2D, các phương pháp mới ngang CEPPnP/MLPnP. Với n_pt < 30 thì MLPnP nhỉnh hơn một chút [tr. 7, Fig. 3 hàng trên].
- [Đ] Khi có nhiễu 2D + 3D, phương pháp mới chính xác nhất, sau đó đến PnP cổ điển, và **nhóm chỉ-2D đứng cuối** [tr. 7, Fig. 3 hàng giữa].
- [Đ] Với điểm + đường, phương pháp mới vượt EPnPL/OPnPL [Fig. 3 hàng dưới].
- [Đ] "Có pose giả thuyết không làm chính xác hơn" [Fig. 3 chú thích, tr. 6].
- [Đ] Uncertain refinement tốt hơn standard refinement cho EPnP, MLPnP, EPnPU\* và P3P, với ngưỡng lọc inlier τ² = 6² [Fig. 5, tr. 7].
Tôi không đọc được số cụ thể từ Fig. 3 và Fig. 5 ngoài thang trục: sai số xoay trung bình khoảng 0–3°, tịnh tiến khoảng 0–1,5%.

**Dữ liệu thật [§4.2, tr. 7–8].** Dùng KITTI chuỗi 00–02 (monocular, cửa sổ hai khung trái) và TUM-RGBD 3 chuỗi 'freiburg1' đầu. Điểm dùng FAST + ORB, đường dùng EDLines + LBD, pyramid 8 tầng, κ = 1,2, ε = 1 px. **Tam giác hoá bằng pose ground-truth** rồi tinh chỉnh bằng Ceres, bước này cho luôn covariance 3D. Frame kế tiếp dùng để đánh giá. Ngưỡng RANSAC trên residual có trọng số covariance là τ = 5,991. Nếu solver hỏng hoặc có < 3 inlier thì dùng kết quả RANSAC thay [tr. 8]. Bài **không cho số frame** và **không cho độ lệch hay khoảng tin cậy**. Median nằm trong supp. mat.

Bảng 1 (điểm) báo sai số trung bình: xoay tính bằng 0,1°, tịnh tiến tính bằng cm. N = solver đứng một mình, S = standard refinement, U = uncertain refinement [Tab. 1, tr. 7]. Tôi chép lại phần KITTI:

| KITTI 00–02 | P3P | EPnP | DLS | OPnP | CEPPnP | MLPnP | EPnPU\* | EPnPU | DLSU\* | DLSU |
|---|---|---|---|---|---|---|---|---|---|---|
| N e_rot / e_t | 8.6/35.2 | 4.5/24.0 | 5.5/18.1 | 7.8/277.6 | 8.2/49.5 | 5.8/27.2 | 4.2/22.2 | 5.1/23.9 | 5.6/32.2 | 6.0/14.9 |
| S | 5.1/14.4 | 4.0/12.8 | 5.0/12.2 | 7.2/242.2 | 5.3/20.6 | 5.3/14.4 | 3.7/12.6 | 3.9/13.1 | 5.1/25.5 | 5.1/12.1 |
| U | 5.0/14.0 | 3.5/13.2 | 5.0/12.9 | 7.6/325.5 | 5.1/17.4 | 6.3/35.3 | 3.3/10.6 | 3.5/13.4 | 5.0/12.6 | 5.0/10.9 |

- [Đ] DLSU (N) đạt e_t 14,9 cm, so với 18,1 cm của DLS (N). Đây là con số "18%" trong abstract; tôi tính ra 17,7% [Tab. 1].
- [Đ] EPnPU\* giảm từ 12,6 cm (S) xuống 10,6 cm (U), tức 15,9%, và 10,6 cm là kết quả tốt nhất cả bảng cho KITTI [Tab. 1].
- [Đ] Trên TUM, mọi phương pháp sau refinement có e_t trong khoảng 1,1–1,3 cm và e_rot trong khoảng 0,90–1,03°. Riêng MLPnP+U là 2,0 cm. Chênh lệch giữa các phương pháp chỉ khoảng 0,1 cm, cỡ bằng bước làm tròn của bảng [Tab. 1].
- [Đ] Uncertain refinement **làm xấu** e_t của EPnP (12,8 → 13,2), DLS (12,2 → 12,9), OPnP, MLPnP (14,4 → 35,3) và EPnPU (13,1 → 13,4) trên KITTI [Tab. 1].

Bảng 2 (điểm + đường, KITTI) cho e_rot/e_t [Tab. 2, tr. 8]:
- EPnPL: N 2.5/37.1, S 1.8/20.4, U 1.4/12.1.
- OPnPL: N 10.2/650.1, S 6.8/267.4, U 9.0/497.7.
- DLSLU\*: N 6.3/18.2, S 5.2/12.2, U 5.2/12.0.
- EPnPLU\*: N 3.4/25.2, S 1.8/9.8, U 1.4/9.3.
[T] Tác giả nói khi đứng một mình thì tịnh tiến cải thiện "gần 50%", và sau standard refinement là 24% [tr. 8]. Đối chiếu với bảng thì xem mục 8.

Bảng 3 (thời gian trung bình, ms, KITTI, đã gồm RANSAC) [Tab. 3, tr. 8]:
- N: P3P 3.1, EPnP 4.6, DLS 16.5, OPnP 10.7, CEPPnP 5.0, MLPnP 7.6, EPnPU 6.1, DLSU 8.0.
- S: 12.1 / 13.2 / 25.1 / 19.5 / 13.7 / 16.0 / 14.7 / 16.7 (cùng thứ tự).
- U: 11.3 / 12.7 / 24.5 / 18.8 / 13.1 / 15.2 / 13.9 / 16.0.

## 6. Đóng góp thật sự (thường nhỏ hơn abstract)

- **Công thức covariance của residual đại số của điểm khi có nhiễu 3D** [eq. (4)], cùng dạng đẳng hướng không phụ thuộc R [eq. (13)]. Đây là đóng góp gọn và đúng: tôi suy lại được và Monte Carlo khớp. Nó cho phép đưa nhiễu 3D vào bất kỳ solver dạng đóng nào dựa trên residual (1), tức toàn bộ họ EPnP/DLS/OPnP (tôi suy ra).
- Mở rộng cùng ý tưởng sang đường [eq. (8), (14)]. Đây là phần thật sự mới so với CEPPnP/MLPnP.
- DLSU: một solver kiểu DLS dùng residual đại số có trọng số thay cho sai số không gian vật. Đây là cải biên kỹ thuật (sinh lại solver Groebner).
- Tinh chỉnh IRLS với covariance Σu + J R Σx Rᵀ Jᵀ [eq. (21)]. Về bản chất đây là "marginalise điểm 3D ở bậc một", một kỹ thuật chuẩn (tôi suy ra: nó chính là covariance của residual tái chiếu khi lan truyền bậc một). Cái mới là đưa nó vào pipeline PnP và đo.
- Thực nghiệm cho thấy lợi ích rõ trên KITTI, nơi nhiễu 3D do stereo và độ sâu lớn là đáng kể. Trên TUM thì lợi ích nằm trong sai số làm tròn [Tab. 1].
Nhỏ hơn abstract ở chỗ: con số "EPnP giảm 16% nhờ uncertain refinement" trong abstract **không khớp** Bảng 1 (mục 8). Lợi ích của refinement mới cũng không đồng đều: nó làm xấu khoảng nửa số solver trên KITTI.

## 7. Kiểm chứng của người ghi chú — script trong `code/`, lệnh chạy, kết quả thật

Lệnh (chạy từ gốc repo, khoảng 70 s, seed cố định 20210619):

```
python3 VSLAM/pnp/code/vakhitov2021uncertainty_check.py
```

**Phần 1: công thức.** Monte Carlo với 400 000 mẫu, pose và điểm cố định ở độ sâu khoảng 5,5, Σx không đẳng hướng.

```
C1 eq.(4) nhiễu nhỏ (σ3D=0.02, σ2D=2px): sai lệch tương đối |emp-pred|/|emp| = 0.0022; thêm γΣu -> 0.0022  [PASS ngưỡng 2%]
C3 eq.(21) nhiễu nhỏ (σ3D=0.02, σ2D=2px): sai lệch tương đối = 0.0022  [PASS ngưỡng 2%]
C1 eq.(4) nhiễu lớn (σ3D=0.5, σ2D=10px): sai lệch tương đối |emp-pred|/|emp| = 0.0052; thêm γΣu -> 0.0052  [PASS ngưỡng 2%]
C3 eq.(21) nhiễu lớn (σ3D=0.5, σ2D=10px): sai lệch tương đối = 0.0149  [PASS (chỉ báo, bậc một không kỳ vọng đúng)]
C2 eq.(13) == eq.(4) với Σx=σ²I, z=d̄: max|diff| = 2.17e-19  [PASS]
C4 §3.6 σ²=tr/3: giải tích 0.070383, lưới 0.070383  [PASS]
```

Diễn giải [M]:
- Eq. (4) khớp covariance thực nghiệm với sai lệch dưới 0,6%, kể cả ở mức nhiễu lớn nhất trong thí nghiệm của bài. Số hạng γΣu bị bỏ (tôi suy ra, xem mục 3) không thấy được ở 4 chữ số.
- Eq. (21) là tuyến tính hoá của π nên lệch lên 1,5% ở nhiễu lớn: vẫn tốt.

**Phần 2: có đáng đưa nhiễu 3D vào không?** Tôi cài hai họ solver.

Họ tuyến tính "kiểu EPnP": x̂ = P[X;1] với 12 ẩn. Cách này tương đương vector null N = 1 của EPnP, vì Ĉ = RC + t chỉ là tham số hoá lại một ánh xạ affine. Làm trắng từng cặp hàng bằng Σr^{-1/2}, rồi Procrustes có tỉ lệ để về SO(3). Bốn cách đặt trọng số:
- L0: không trọng số.
- L2D: d̄²Σu, kiểu CEPPnP.
- LU: eq. (13).
- LUz\*: eq. (13) nhưng lấy độ sâu từng điểm từ pose giả thuyết, đúng như chữ §3.3.
- LU\*: eq. (4) với Σx đầy đủ và pose giả thuyết, theo §3.2.
Pose giả thuyết là nghiệm L0, không phải P3P như trong bài.

Họ Gauss-Newton: 10 vòng trên sai số tái chiếu, mọi phương pháp cùng khởi tạo từ L0.
- G0: không trọng số.
- G2D: Σu, tức "standard refinement".
- GUiso: (21) với Σx đẳng hướng hoá.
- GU: (21) với Σx đầy đủ, IRLS, tức "uncertain refinement".
- GUgt: (21) đánh giá cố định tại pose thật (oracle).

Cảnh sinh bằng `common.make_scene`: n = 50, độ sâu 4..8, f = 800, 200 lần thử mỗi điều kiện. Sai số tịnh tiến là ‖t̂ − t‖ tuyệt đối, vì ‖t‖ trong `make_scene` nhỏ (≤ √3), làm sai số tương đối phồng lên và không so được với % của bài. Trích kết quả thật, gồm sai số xoay trung vị (°) và sai số tịnh tiến trung vị:

```
-- B. như bài: 2D 1..10 px + 3D không đẳng hướng 0.05..0.5 (nhóm độc lập)  (200 lần thử, n=50) --
method   medRot°  meanRot°    medT   meanT
L0         4.224     4.664   0.528   0.586
L2D        8.179     9.076   1.005   1.087
LU         2.537     2.845   0.318   0.346
LUz*       2.479     2.812   0.314   0.342
LU*        1.919     2.222   0.239   0.270
G0         2.248     2.529   0.365   0.387
G2D        4.721     5.154   0.531   0.588
GUiso      1.198     1.301   0.153   0.157
GU         0.975     1.026   0.119   0.118
GUgt       0.967     1.010   0.119   0.117
-- D. kiểu stereo: 2D 1 px, 3D kéo dài theo tia camera tham chiếu, σ∥=0.004·dist²  (200 lần thử, n=50) --
L0         0.561     0.627   0.067   0.073
LU         0.569     0.635   0.068   0.074
LUz*       0.571     0.637   0.068   0.074
LU*        0.342     0.357   0.036   0.039
G0         0.296     0.357   0.033   0.038
GUiso      0.339     0.392   0.034   0.040
GU         0.186     0.241   0.020   0.025
== Tóm tắt: tỉ số sai số trung vị (so với cách không trọng số cùng họ) ==
[A ] tuyến tính medT: L2D/L0=0.50 LU/L0=0.50 LUz*/L0=0.49 LU*/L0=0.49 (rot LU*/L0=0.47) | GN medT: G2D/G0=0.46 GUiso/G0=0.46 GU/G0=0.46
[B ] tuyến tính medT: L2D/L0=1.90 LU/L0=0.60 LUz*/L0=0.59 LU*/L0=0.45 (rot LU*/L0=0.45) | GN medT: G2D/G0=1.45 GUiso/G0=0.42 GU/G0=0.33
[B'] tuyến tính medT: L2D/L0=0.51 LU/L0=0.49 LUz*/L0=0.49 LU*/L0=0.37 (rot LU*/L0=0.41) | GN medT: G2D/G0=0.36 GUiso/G0=0.33 GU/G0=0.26
[C ] tuyến tính medT: L2D/L0=1.01 LU/L0=0.71 LUz*/L0=0.68 LU*/L0=0.66 (rot LU*/L0=0.69) | GN medT: G2D/G0=1.14 GUiso/G0=0.69 GU/G0=0.66
[D ] tuyến tính medT: L2D/L0=1.00 LU/L0=1.01 LUz*/L0=1.01 LU*/L0=0.54 (rot LU*/L0=0.61) | GN medT: G2D/G0=1.00 GUiso/G0=1.04 GU/G0=0.60
[E ] tuyến tính medT: L2D/L0=1.00 LU/L0=0.98 LUz*/L0=0.97 LU*/L0=0.97 (rot LU*/L0=1.01) | GN medT: G2D/G0=1.00 GUiso/G0=0.99 GU/G0=0.99
Phần 1 tổng: PASS   thời gian 72.9 s
```

Các điều kiện:
- A: chỉ có nhiễu 2D, 1..10 px theo nhóm.
- B: như bài, 2D 1..10 px cộng 3D 0,05..0,5 không đẳng hướng, chỉ số nhóm 2D và 3D hoán vị độc lập.
- B': như B nhưng nhóm 2D và 3D trùng chỉ số.
- C: 3D nhẹ, 0,005..0,05.
- D: kiểu stereo, covariance 3D kéo dài theo tia từ một camera tham chiếu cách 2 m, σ∥ = 0,004·dist², σ⊥ = 0,005, 2D 1 px.
- E: nhiễu đồng nhất cho mọi điểm, 2 px và 3D đẳng hướng 0,02.

Kết luận của tôi [M] (chỉ cho điểm, chỉ trong mô phỏng này):
1. **Tính tới bất định 3D giúp nhiều khi nhiễu 3D lớn và không đồng nhất giữa các điểm.** Ở điều kiện B, so với chỉ-2D, sai số tịnh tiến trung vị giảm từ 1,005 xuống 0,239 ở solver tuyến tính (L2D → LU\*) và từ 0,531 xuống 0,119 ở GN (G2D → GU), tức 4–4,5 lần. So với không trọng số thì còn 0,45× và 0,33×.
2. **Trọng số chỉ-2D có hại khi nhiễu 3D áp đảo và không tương quan với nhiễu 2D.** Ở B, L2D/L0 = 1,90 và G2D/G0 = 1,45. Điều này tái lập thứ tự trong Fig. 3 hàng giữa của bài, nơi CEPPnP và MLPnP xếp dưới PnP cổ điển. Khi nhóm nhiễu 2D và 3D trùng nhau (B') thì trọng số 2D lại giúp "nhờ may", vì nó vô tình xếp đúng thứ tự tin cậy.
3. **Xấp xỉ đẳng hướng (trace/3) giữ được phần lớn lợi ích khi hướng dị hướng là ngẫu nhiên** (B: GUiso 0,153 so với GU 0,119). Nhưng **nó mất hết lợi ích khi dị hướng có cấu trúc kiểu stereo** (D: LU/L0 = 1,01, GUiso/G0 = 1,04, trong khi LU\*/L0 = 0,54 và GU/G0 = 0,60). Đây là trường hợp thực tế nhất, và cũng là nơi EPnPU/DLSU (đẳng hướng theo eq. (13)) không giúp gì.
4. **Chỉ lấy độ sâu từ pose giả thuyết mà vẫn giữ Σx đẳng hướng (LUz\*) gần như không khác LU** ở mọi điều kiện. Điều này khớp với câu "pose giả thuyết không làm chính xác hơn" trong Fig. 3 của bài. Lợi ích của giả thuyết chỉ xuất hiện khi dùng nó để xoay **Σx đầy đủ** (LU\*).
5. **Nơi đánh giá covariance phụ thuộc pose ở bước tinh chỉnh gần như không quan trọng.** IRLS tại pose hiện tại (GU) và cố định tại pose thật (GUgt) khác nhau ở chữ số thứ ba, ở mọi điều kiện.
6. **Khi nhiễu đồng nhất (E) thì mọi cách đặt trọng số ngang nhau** (tỉ số 0,97–1,01): bất định chỉ có ích khi nó *khác nhau* giữa các điểm.
7. Ở điều kiện chỉ 2D (A), mọi phương pháp có trọng số ngang nhau. Việc thêm số hạng 3D không gây hại khi Σx ≈ 0, khớp với Fig. 3 hàng trên.

Giới hạn của kiểm chứng này: tôi **không** cài EPnPU/DLSU thật. Solver tuyến tính của tôi là vector null N = 1, không có bước β, không có PCA có trọng số, không có solver Groebner. Tôi cũng không có RANSAC hay ngoại lai, không có đường, và không làm dữ liệu thật. Vì vậy kết quả ủng hộ **nguyên lý** của eq. (4)/(21), không xác nhận con số của Bảng 1–3.

## 8. Chỗ tôi không tin

- **Abstract và §4.2 nói "uncertain refinement giảm sai số tịnh tiến của EPnP 16%" trên KITTI** [tr. 1, tr. 8]. Bảng 1 lại cho EPnP S = 12,8 cm và U = 13,2 cm, tức U **xấu hơn**. Con số 16% chỉ khớp với EPnP**U\*** (12,6 → 10,6). Đây là lỗi gán nhãn trong phần chữ, và chính phần chữ đó đi vào abstract.
- **§1 nói uncertain refinement tốn thêm 5–10% thời gian** [tr. 2], nhưng Bảng 3 cho U *nhanh hơn* S ở mọi solver, ví dụ EPnP 12,7 so với 13,2 ms [Tab. 3]. Có thể U hội tụ nhanh hơn hoặc lọc inlier khác nhau, nhưng bài không giải thích.
- **"Mostly better" cho uncertain refinement là nói quá** [Tab. 1 chú thích]. Trên KITTI, U làm xấu e_t của 5/10 phương pháp. MLPnP xấu đi mạnh, từ 14,4 lên 35,3 cm. Không có giải thích nào, dù chính bài dùng MLPnP làm baseline mạnh.
- **Trung bình (mean) trên KITTI bị ngoại lai chi phối.** OPnP đạt 277,6 cm (N) và 325,5 cm (U), OPnPL đạt 650,1 cm. Đó là dấu hiệu có vài frame hỏng nặng, trong khi median chỉ có trong supp. mat. Không có số frame, không có độ lệch, không có kiểm định. Mức cải thiện 3 cm (18%) của DLSU có thể chỉ là do vài frame hỏng ít hơn.
- **Bảng 2 và câu "24% sau standard refinement"** [tr. 8] không khớp nhau. Ở cột S, EPnPLU\* 9,8 so với EPnPL 20,4 là 52%. Con số 23% thực ra là cột U (9,3 so với 12,1). Chú thích bảng ghi "23%–52%" là đúng, nhưng phần thân bài gán sai giao thức.
- **Bảng 1 và Bảng 2 dùng cùng KITTI 00–02**, nhưng e_rot của EPnPL (N) chỉ 2,5 (×0,1°) trong khi EPnP (N) ở Bảng 1 là 4,5, và e_t của EPnPL (37,1) lại tệ hơn EPnP (24,0). Có thể tập frame hoặc tập inlier khác nhau, nhưng bài không nói.
- **Tam giác hoá bằng pose ground-truth** [tr. 8] làm covariance 3D "sạch" hơn thực tế. Trong SLAM thật, sai số pose keyframe tạo tương quan giữa các điểm, và mô hình độc lập của bài không bắt được điều đó (mục 2). Lợi ích trên dữ liệu thật vì vậy có thể bị đánh giá cao.
- **Mô tả bản "\*" không nhất quán.** §3.2 nói dùng pose để "tính ước lượng covariance điểm 3D" [tr. 3], còn §3.3 nói "vẫn dùng xấp xỉ đẳng hướng, chỉ dùng pose để ước lượng độ sâu" [tr. 4]. Mô phỏng của tôi cho thấy khác biệt này quyết định việc giả thuyết có ích hay không (LUz\* ≈ LU, còn LU\* tốt hơn hẳn). Kết luận "pose giả thuyết không giúp" [Fig. 3] có thể chỉ là hệ quả của cách cài đặt đẳng hướng.
- **Eq. (18) ghi "→ max"** cho một tổng các bình phương Mahalanobis [tr. 5]. Đúng ra phải là min (hoặc max của log-likelihood âm). Đây là lỗi dấu nhỏ nhưng dễ gây hiểu nhầm.
- "Globally convergent PnP(L) solvers" trong chú thích Fig. 1 [tr. 1] là một tuyên bố không được chứng minh ở đâu trong bài [T].

## 9. Chỗ tôi chưa hiểu (→ `99-chua-biet.md`)

- M_U trong EPnPU được dựng chính xác thế nào [§3.3]? Bài không nói rõ nó là làm trắng từng khối 2 hàng bằng Σ^{-1/2} hay cách khác, và cũng không nói có giữ các nghiệm N = 2..4 và tinh chỉnh β của EPnP không. Cần mã nguồn hoặc supp. mat.
- PCA có trọng số [eq. (11)] có thật sự giúp không, và giúp bao nhiêu? Bài chỉ nhắc đến "thí nghiệm sơ bộ" [tr. 4] mà không cho số.
- Trong eq. (14), ‖l‖² gồm cả thành phần thứ ba của l, vốn phụ thuộc gốc toạ độ ảnh. Việc trọng số của đường phụ thuộc vị trí gốc có hợp lý không, hay đây là hệ quả của việc đẳng hướng hoá Σp?
- DLSU dùng covariance đẳng hướng của eq. (13), nên Σ_rk không phụ thuộc s. Nếu dùng Σx đầy đủ (bản "\*"), Σ_rk sẽ phụ thuộc R. Khi đó họ cố định Σ tại R̂, hay phải bỏ tính đa thức của (17)?
- Việc bỏ log det Σ(θ) trong "full uncertain refinement" có gây chệch (bias) có hệ thống về phía pose làm covariance lớn (đẩy điểm ra xa, tăng độ sâu) không?
- Trong mô phỏng của bài, 10 nhóm nhiễu 2D và 10 nhóm nhiễu 3D được gán cho cùng tập điểm hay độc lập [tr. 6–7]? Mục 7 cho thấy điều này đổi hẳn thứ hạng của các phương pháp chỉ-2D (B so với B').

## 10. Quan hệ với các bài khác trong `refs.bib`

- **Xây trên** `lepetit2009epnp` (EPnP, điểm điều khiển, PCA) và `hesch2011dls` (DLS, Cayley). Solver được sinh bằng `larsson2017syzygy`. Điểm kỳ dị của Cayley được nhắc qua `nakano2015dls` [tr. 2].
- **Mở rộng** `vakhitov2016pnpl` (EPnPL/OPnPL, cùng tác giả đầu) bằng bất định. Residual đường (5) lấy từ đó [tr. 3].
- **Tổng quát hoá** `ferraz2014cepnp` (CEPPnP, cùng nhóm Ferraz/Moreno-Noguer) và `urban2016mlpnp` (MLPnP). Hai bài này chỉ dùng Σu. Khi Σx = 0, eq. (4) rút về x̂(3)²Σu, tức cùng dạng trọng số 2D (tôi suy ra). Không có mâu thuẫn nội dung. Bài chỉ chỉ ra rằng khi nhiễu 3D áp đảo, chúng xếp dưới cả PnP cổ điển [Fig. 3]. Mục 7 tái lập được điều này ở điều kiện B.
- **Liên quan về sau:** `zhan2025gmlpnp` (ước lượng đồng thời pose và covariance bất đẳng hướng) và `liu2023lincov` (covariance tuyến tính hoá của PnP). Tôi chưa đọc hai bài này nên chưa biết chúng có xử lý nhiễu 3D không.
- **Dùng làm baseline**: `zheng2013opnp` (OPnP), `kneip2011p3p` (P3P trong RANSAC).
- Tài liệu cho lan truyền sai số 3D là `hartley2004`, ch. 5 [tr. 5].

## 11. Nó đổi gì trong suy nghĩ

Trước khi đọc, tôi coi "PnP biết covariance" đồng nghĩa với MLPnP/CEPPnP, tức trọng số 2D. Bài này, cộng với mô phỏng ở mục 7, cho thấy trong định vị theo bản đồ tam giác hoá, bất định 3D chiếm phần lớn nhiễu **sau khi chiếu lên ảnh**. Theo eq. (21), 1 cm lệch ngang ở độ sâu 5 m với f = 800 đã là 1,6 px (tôi suy ra). Trong trường hợp đó, trọng số chỉ-2D có thể làm hại. Thêm một bài học thực dụng: **cách xấp xỉ covariance quan trọng hơn chọn solver**. Đẳng hướng hoá Σx làm mất gần hết lợi ích khi dị hướng có cấu trúc (stereo). Chỉ cần một pose giả thuyết cộng Σx đầy đủ và IRLS là lấy lại được lợi ích đó, trong khi nơi đánh giá pose không quan trọng. Với khảo sát: câu hỏi dẫn đường 3 ("giả thiết về nhiễu") cần thêm một cột *"có mô hình nhiễu 3D không, và có giữ dị hướng không"*.

## 12. Câu hỏi tự kiểm (3–5 câu, hỏi *vì sao* / *khi nào hỏng*)

1. Vì sao eq. (13) không phụ thuộc R, còn eq. (4) thì có? Khi nào việc bỏ phụ thuộc đó làm mất gần hết lợi ích (gợi ý: điều kiện D ở mục 7)?
2. Vì sao trọng số chỉ-2D có thể làm pose **tệ hơn** không trọng số khi có nhiễu 3D lớn? Trong cấu hình nào nó lại "tình cờ" giúp?
3. Covariance ở eq. (21) phụ thuộc pose. Vì sao IRLS (đánh giá tại pose vòng trước) vẫn cho kết quả gần như bằng đánh giá tại pose thật? Khi nào điều này hỏng (khởi tạo xa, độ sâu nhỏ, điểm gần mặt phẳng ảnh)?
4. Nếu các điểm 3D được tam giác hoá từ cùng một keyframe có pose sai, giả thiết nào của bài bị vi phạm? Hệ quả với trọng số và với covariance của pose ước lượng được là gì?
5. Vì sao "có pose giả thuyết" lại không làm EPnPU\* chính xác hơn EPnPU trong Fig. 3? Cần đổi gì trong cách dùng giả thuyết để nó có ích?

## Trích đoạn nguyên văn làm bằng chứng

- "Current point-based pose estimation methods use only 2D feature detection uncertainties, and the line-based methods do not take uncertainties into account." [tr. 1]
- "We acknowledge that this is a simplification, however it speeds up the computations, and works in practice" [tr. 3]
- "when 3D noise is added to x, the accuracy of the PCA version degrades." [tr. 4]
- "They cannot be used in a classical Gauss-Newton scheme." [tr. 5]
- "in which we make Gauss-Newton iterations, but update the estimate of the covariances (21, 22) on each step." [tr. 5]
- "The access to a pose hypothesis does not result in better accuracy." [tr. 6]
- "Uncertain (U) is mostly better than standard (S) for the proposed methods" [tr. 7]
