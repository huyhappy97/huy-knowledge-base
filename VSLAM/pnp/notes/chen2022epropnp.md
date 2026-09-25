# EPro-PnP: Generalized End-to-End Probabilistic Perspective-n-Points for Monocular Object Pose Estimation — ghi chú đọc

| | |
|---|---|
| bibkey | `chen2022epropnp` |
| Venue, năm | IEEE/CVF CVPR 2022 (có qua phản biện). Bản mở rộng: `chen2025epropnp` (T-PAMI) — chưa đọc |
| Bản đã đọc | `papers/chen2022epropnp.pdf` — nguồn: CVF open access (`fetch.sh`), 10 trang, bản CVF open access. Chân trang in số 2781–2790; Crossref của DOI 10.1109/CVPR52688.2022.00280 ghi 2771–2780 (khớp `refs.bib`) — hai bản đánh số trang khác nhau. **Không đọc phụ lục (supplementary)**, dù bài chuyển nhiều chi tiết sang đó |
| Mức đọc | lượt 2 toàn bài; lượt 3 cho §3.1–§3.4 (eq. (1)–(10), Alg. 1) |
| Người đọc | Claude (agent), 2026-09-25 — **Huy chưa đọc lại để ký** |
| Mức tin | giữ B: hội nghị đầu ngành, có mã nguồn; toán lõi qua cửa (a)+(b) dưới đây; nhưng mọi con số benchmark chỉ do nhóm tác giả đo, không có phương sai giữa các lần chạy |
| Kiểm chứng | eq. (3)→(5): cửa (a). Eq. (6)/Alg. 1: cửa (b) (C1). Eq. (7)/(8): cửa (a)+(b) (C2, C3). Vai trò số hạng log Z (Fig. 2): cửa (b) (C4). "Laplace không chính xác khi lưỡng nghĩa", "y\* không khả vi": cửa (b) (C1b, C5). Eq. (9)/(10) và các bảng benchmark: **chưa kiểm** |

## 1. Bài toán gốc và bối cảnh

Bài toán là ước lượng pose của một vật thể từ một ảnh RGB, trong đó mạng nơ-ron sinh ra các tương ứng 2D–3D có trọng số rồi một lớp PnP giải ra pose [§1, tr. 1–2]. Cách làm phổ biến trước đó học tương ứng bằng một hàm mất mát thay thế (*surrogate loss*), tức ép mạng khớp các toạ độ 3D hoặc điểm khoá đã định sẵn, chứ không tối ưu trực tiếp sai số pose [§2, tr. 2]. Nhóm "PnP khả vi" (BPnP `chen2020bpnp`, DSAC++ `brachmann2018dsacpp`, BlindPnP `campbell2020blindpnp`) lan truyền gradient của sai số pose ngược qua lớp PnP, nhưng theo tác giả mỗi bài chỉ học được một phần — toạ độ 2D, toạ độ 3D, hoặc trọng số — và vẫn phải kèm loss thay thế để hội tụ [§1, tr. 2; §2, tr. 2]. Chẩn đoán của bài là: nghiệm tất định y\* = PnP(X) không khả vi ở một số điểm vì bài toán PnP có thể lưỡng nghĩa (nhiều nghiệm cục bộ), nên lan truyền ngược qua một nghiệm đơn lẻ không ổn định [§1, tr. 2; §3.1, tr. 3] [T]. Lời giải đề xuất: thay đầu ra điểm bằng một phân bố pose trên SE(3), và học bằng KL divergence tới phân bố đích — tương tự như Softmax thay cho arg max trong phân loại [§1, tr. 2; eq. (3)].

## 2. Giả thiết — kể cả giả thiết ngầm; bỏ đi thì hỏng ở đâu

1. **Mô hình nhiễu Gauss chéo cho từng điểm.** Eq. (2) coi tổng bình phương sai số tái chiếu có trọng số là âm log-likelihood [eq. (2), tr. 3]; vì trọng số `w_i^2D ∈ R²_+` nhân từng trục [eq. (1)], mô hình ngầm là nhiễu pixel Gauss độc lập theo x, y với độ lệch chuẩn 1/w (tôi suy ra). Tương quan giữa hai trục (covariance đầy đủ như MLPnP `urban2016mlpnp`) không biểu diễn được [M].
2. **p(X|y) ở eq. (2) không chuẩn hoá theo X.** Hằng số chuẩn hoá theo quan sát (∝ Π w) bị bỏ, nên đây không phải likelihood thật theo nghĩa thống kê; điều này vô hại cho hậu nghiệm theo y (eq. (3)) nhưng có nghĩa là EPro-PnP **không** học trọng số bằng maximum likelihood của pixel — tín hiệu điều chỉnh độ lớn trọng số đến hoàn toàn từ log Z trên không gian pose (tôi suy ra; kiểm ở C4c).
3. **Tiên nghiệm "không thông tin" trên pose** [tr. 3]. Bài không nói rõ độ đo `dy` trên SE(3) trong phần chính (tôi không tìm thấy); log Z vì thế phụ thuộc cách tham số hoá. Với hậu nghiệm hẹp thì không đáng kể; với hậu nghiệm rộng/nhiều mode thì có (C5, ghi chú kỹ thuật) [M].
4. **Đích Dirac.** Bài dùng phân bố đích hẹp "giống Dirac" quanh y_gt [tr. 3]; với Dirac đúng nghĩa, hằng số bị "bỏ" trong eq. (4) (entropy của t) là vô hạn — chỉ là hằng số theo tham số mạng nên gradient không đổi (tôi suy ra). Với vật đối xứng, một y_gt duy nhất làm loss phạt cả các pose tương đương; bài không nói xử lý thế nào trong phần chính (xem §9).
5. **Tích phân được xấp xỉ tốt bằng AMIS khởi đầu từ Laplace tại nghiệm PnP** [Alg. 1, dòng 1–2, tr. 4]. Đây là giả thiết ngầm quan trọng nhất: chính bài nói xấp xỉ Laplace sai khi có lưỡng nghĩa [tr. 3], nhưng đề xuất ban đầu của AMIS lại là Laplace tại một mode; nếu mode thứ hai ở xa mà đuôi đề xuất không phủ tới, log Z bị ước lượng thiếu (C5c cho thấy mức thiếu ≈ log 2 khi hai mode ngang nhau) [M].
6. **Trong thực nghiệm, sai số được làm bền bằng Huber** [eq. (11), (12), §5.2, tr. 6]; khi đó eq. (2) không còn là Gauss, và công thức gradient eq. (8) (dẫn ra cho dạng bình phương) không còn đúng nguyên văn (tôi suy ra).
7. Biết nội tham số K và có sẵn đề xuất vật thể (hộp 2D) [§3.1, tr. 2; §4.1, tr. 5].

## 3. Cơ chế — năm câu, rồi chi tiết có định vị

**Năm câu.** (1) Lớp PnP định nghĩa năng lượng E(y) = ½Σ‖w_i∘r_i(y)‖², và thay vì chỉ lấy arg min, bài coi exp(−E(y)) chuẩn hoá là mật độ hậu nghiệm của pose. (2) Loss huấn luyện là KL từ phân bố đích (Dirac tại y_gt) tới hậu nghiệm đó, rút gọn thành "sai số tái chiếu tại pose đúng" cộng "log hàm phân hoạch" log Z. (3) Số hạng thứ nhất kéo các tương ứng về phía nhất quán với y_gt; số hạng thứ hai đẩy mật độ ra khỏi mọi pose khác, ngăn nghiệm suy biến (thu mọi điểm về một chỗ hoặc thu trọng số về 0). (4) log Z là tích phân 6 chiều, được ước lượng bằng lấy mẫu quan trọng thích nghi AMIS, và gradient của nó là kỳ vọng hậu nghiệm của gradient năng lượng. (5) Vì suy luận vẫn dùng nghiệm LM, bài thêm một loss điều chuẩn trên bước Gauss–Newton tại y\* để bước đó chỉ về y_gt.

**Chi tiết.**

- *Bài toán PnP có trọng số*: y\* = arg min ½Σ_i ‖w_i^2D ∘ (π(R x_i^3D + t) − x_i^2D)‖², với f_i(y) là sai số có trọng số [eq. (1), §3.1, tr. 3].
- *Likelihood và hậu nghiệm*: p(X|y) = exp(−½Σ‖f_i(y)‖²) [eq. (2)]; với tiên nghiệm không thông tin, p(y|X) = exp(−½Σ‖f_i‖²) / ∫exp(−½Σ‖f_i‖²)dy [eq. (3)], được gọi là "Softmax liên tục" [tr. 3].
- *Loss KL*: L_KL = −∫t(y) log p(X|y) dy + log∫p(X|y) dy [eq. (4)]; với đích hẹp tại y_gt: L_KL = ½Σ‖f_i(y_gt)‖² + log∫exp(−½Σ‖f_i(y)‖²)dy = L_tgt + L_pred [eq. (5), tr. 3]. Tôi tự suy dẫn lại eq. (4)→(5) được: D_KL(t‖p) = ∫t log t − ∫t log p(X|y) + log Z, bỏ entropy của t và thay t = δ(y − y_gt) (cửa (a)).
- *So với loss tái chiếu*: chỉ riêng L_tgt (loss thay thế của [4, 10, 11]) cho phép mạng dồn mọi điểm về một chỗ mà không phân biệt pose; L_pred sinh ra từ mẫu số của eq. (3) và là cái làm loss "phân biệt" [§3.1, tr. 3; Fig. 2] [T].
- *So với vi phân ẩn (BPnP, BlindPnP)*: trong khung xác suất, vi phân ẩn qua y\* tương đương xấp xỉ Laplace N(y\*, Σ_y\*); khi Σ đồng nhất thì KL rút thành loss L2 ‖y\* − y_gt‖² của [7]; Laplace sai cho hậu nghiệm không chuẩn/lưỡng nghĩa nên "không bảo đảm hội tụ toàn cục" [§3.1, tr. 3] [T].
- *Monte Carlo*: L_pred ≈ log (1/K)Σ_j exp(−½Σ‖f_i(y_j)‖²)/q(y_j), v_j là trọng số quan trọng [eq. (6), §3.2, tr. 3]. AMIS [Alg. 1, tr. 4] khởi đầu bằng y\*, Σ_y\* từ PnP (dòng 1–2), mỗi vòng lấy K′ mẫu, tính lại trọng số của **mọi** mẫu cũ với mẫu số là trung bình của mọi đề xuất đã dùng (dòng 7–9, "deterministic mixture"), rồi ước lượng đề xuất mới từ toàn bộ mẫu có trọng số (dòng 11); đầu ra L_pred = log (1/(TK′))Σ v (dòng 12). Đề xuất: phân bố t 3 bậc tự do cho vị trí; trộn von Mises + đều cho yaw 1D; angular central Gaussian cho quaternion 3D [§3.2, tr. 4]. Cấu hình: T = 4, K′ = 128 [§5.2, tr. 6].
- *Lan truyền ngược*: ∂L_KL/∂(·) = ∂/∂(·) ½Σ‖f_i(y_gt)‖² − E_{y∼p(y|X)} ∂/∂(·) ½Σ‖f_i(y)‖² [eq. (7), §3.3, tr. 4]. Tôi suy dẫn lại dấu: ∂ log Z = E_{y∼p}[∂(−E(y))] = −E_{y∼p}[∂E(y)], khớp dấu "−" của eq. (7) (cửa (a)); với mẫu AMIS, kỳ vọng này là trung bình tự chuẩn hoá theo v_j.
- *Diễn giải theo trọng số*: −∂L_KL/∂w_i = w_i ∘ (−r_i^∘2(y_gt) + E_{y∼p} r_i^∘2(y)) [eq. (8), tr. 4]; số hạng đầu là "bất định" (sai số lớn tại pose đúng → giảm trọng số), số hạng sau là "phân biệt" (điểm nhạy với pose → tăng trọng số) [§3.3, tr. 4; Fig. 3] [T]. Tôi suy dẫn lại được: ∂(½‖w∘r‖²)/∂w = w∘r^∘2 (cửa (a)).
- *Điều chuẩn đạo hàm*: tại y\* đã tách gradient, tính một bước GN Δy = −(JᵀJ + εI)⁻¹JᵀF(y\*) [eq. (9), tr. 4] và phạt L_reg = l(y\* + Δy, y_gt) [eq. (10)], với l là smooth L1 cho vị trí và cosine similarity cho hướng [§3.4, tr. 5]; gradient chỉ đi qua Δy [tr. 5]. Tác giả tự nhận loss này "rất giống" loss từ vi phân ẩn [tr. 5] [T].
- *Mạng*: (a) CDPN sửa đầu ra thành bản đồ trọng số XY 2 kênh với spatial Softmax và hệ số thang toàn cục động, bỏ nhánh tịnh tiến [§4.1, Fig. 4, tr. 5]; (b) mạng tương ứng biến dạng dựa trên FCOS3D + deformable attention, học cả điểm 2D, điểm 3D (trong không gian NOC) và trọng số từ đầu [§4.2, Fig. 5, tr. 5–6].

## 4. Ký hiệu của bài ↔ ký hiệu của khảo sát

| Bài | Khảo sát | Ghi chú |
|---|---|---|
| x_i^3D ∈ R³ (toạ độ vật) | X_w | "thế giới" = hệ vật thể |
| x_i^2D ∈ R² | u_i | pixel |
| w_i^2D ∈ R²_+ | (không có; tôi viết w_i) | trọng số theo từng trục, đơn vị px⁻¹ ≈ 1/σ |
| y = (R, t), R x + t | R, t với X_c = R X_w + t | cùng quy ước |
| π(·) (đã gồm nội tham số) | u = π_K(X_c) | K của khảo sát nằm **trong** π |
| f_i(y) = w_i∘r_i(y) | sai số có trọng số | r_i(y) chưa nhân trọng số [tr. 4] |
| N | n | số tương ứng |
| **K** (eq. (6)) | — | **số mẫu Monte Carlo — trùng tên với ma trận nội tham số K** |
| T, K′ | — | số vòng AMIS, số mẫu mỗi vòng |
| q(y), v_j | — | đề xuất, trọng số quan trọng |
| F, J, ε (eq. (9)) | — | vectơ sai số có trọng số, Jacobian, hệ số giảm chấn |
| t(y) | — | phân bố đích (khác t tịnh tiến!) |

## 5. Bằng chứng — dữ liệu, phần cứng, baseline, con số kèm điều kiện, số lần lặp

**Điều kiện chung.** Không có phương sai giữa các lần huấn luyện hay số seed trong bài chính; không báo phần cứng cụ thể (chỉ "4 GPUs" cho nuScenes) và không báo thời gian huấn luyện/suy luận trong bài chính [§5.2, tr. 6] (có thể có ở phụ lục — chưa đọc).

**LineMOD** [§5.1, tr. 6]: 13 chuỗi, mỗi chuỗi ≈ 1,2K ảnh; ≈ 200 ảnh/vật để huấn luyện theo cách chia của [3]; tăng cường bằng dữ liệu tổng hợp của CDPN. Mạng: CDPN với ResNet-34, batch 32, 160 epoch RMSprop; lấy ngẫu nhiên 512 trong 64×64 điểm dày để tính L_KL [§5.2, tr. 6]. Thước đo ADD(-S) ở 0,02d/0,05d/0,1d và n°, n cm.

- Ablation [Tab. 1, tr. 7] (ADD(-S) 0,1d / trung bình ba ngưỡng) [Đ]: CDPN-Full (tác giả chạy lại bằng mã chính thức) 91,03 / 63,21; CDPN bỏ nhánh tịnh tiến 74,54 / 45,75; + batch 32, bộ giải LM 79,96 / 52,04; EPro-PnP cơ bản 92,66 / 65,88; + điều chuẩn đạo hàm 93,43 / 67,76; + khởi tạo từ A1 95,76 / 73,22; + lịch dài 320 epoch 95,80 / 74,19. Tách gradient khỏi toạ độ: 90,23 / 62,80; tách khỏi trọng số (kèm loss mặt nạ thay thế): 87,27 / 57,19; bỏ mẫu số Softmax: phân kỳ.
- So với state of the art [Tab. 2, tr. 7] [Đ]: EPro-PnP 2°,2cm 80,99; 5°,5cm 98,54; ADD(-S) 0,1d 95,80, so với PVNet-RePOSE 96,1, DPOD 95,15, GDRNet\* 93,6 (2°,2cm 67,1), HybridPose 91,3, CDPN 89,86. BPnP bị loại khỏi bảng vì dùng cách chia train/test khác [Tab. 2 chú thích] — nên **không có so sánh trực tiếp với BPnP gốc trên cùng dữ liệu**.
- So sánh loss trên cùng mạng [Tab. 3, tr. 7] [Đ]: không có hồi quy toạ độ — vi phân ẩn: phân kỳ; loss tái chiếu: ADD 0,1d 14,56 (2°,2cm 0,16); Monte Carlo (EPro-PnP): 79,46 (2°,2cm 40,96). Có hồi quy toạ độ — vi phân ẩn 88,74; tái chiếu 92,04; Monte Carlo 92,66. **Lưu ý điều kiện**: "vi phân ẩn" ở đây cực tiểu khoảng cách pose của eq. (10), **không** phải loss tái chiếu của BPnP gốc [Tab. 3 chú thích].

**nuScenes** [§5.1, tr. 6]: 1000 cảnh, chia 700/150/150; 10 lớp; 6 camera. Mạng FCOS3D với ResNet-101-DCN, 12 epoch AdamW, batch 12 ảnh trên 4 GPU [§5.2]. Tab. 4 chỉ gồm các phương pháp không dùng tiền huấn luyện ngoài ImageNet [Tab. 4 chú thích, tr. 8].

- Val [Tab. 4] [Đ]: FCOS3D NDS 0,372, mAP 0,295; PGD (TTA) 0,422 / 0,361; EPro-PnP cơ bản 0,425 / 0,349 (mATE 0,676, mAOE 0,363); + hồi quy toạ độ (từ điểm LiDAR thưa) 0,430 / 0,352 (mAOE 0,337); + TTA lật 0,439 / 0,361 (mATE 0,653, mAOE 0,319).
- Test [Tab. 4] [Đ]: EPro-PnP (TTA) NDS 0,453, mAP 0,373, mATE 0,605, mAOE 0,359; PGD (TTA) 0,448 / **0,386** / 0,626 / 0,451. Tức là EPro-PnP cao hơn về NDS và sai số pose nhưng **thấp hơn PGD về mAP** trên test.
- Tác giả thừa nhận một phần cải thiện so với FCOS3D có thể do thêm tham số ở đầu tương ứng [§5.4, tr. 7] [T].
- Định tính: phân bố yaw đa mode cho vật đối xứng (barrier, cone) và quan sát bất định (người đi bộ) [Fig. 6, tr. 8]; bản đồ trọng số/toạ độ [Fig. 7, tr. 8].

## 6. Đóng góp thật sự (thường nhỏ hơn abstract)

Về toán, phần mới là nhìn loss PnP khả vi như KL tới hậu nghiệm Boltzmann exp(−E(y)) và **giữ lại số hạng log Z**, rồi làm cho log Z tính được trong 6 bậc tự do bằng AMIS với đề xuất riêng cho vị trí/hướng (tôi suy ra, dựa trên §3.1–§3.2). Hệ quả thực nghiệm đáng tin nhất là Tab. 3: cùng một mạng, không có giám sát toạ độ, loss tái chiếu và loss kiểu vi phân ẩn đều hỏng, còn loss KL học được (ADD 0,1d 79,46) [Đ]. Phần lớn các con số "vượt SOTA" khác nhỏ hơn giọng abstract: trên LineMOD, EPro-PnP ngang RePOSE chứ không vượt (95,80 vs 96,1) [Tab. 2]; bước +5,46 lớn nhất trong Tab. 1 đến từ khởi tạo bằng CDPN đã học với mặt nạ, không phải từ EPro-PnP [tr. 7] [T]; trên nuScenes test, mAP thấp hơn PGD [Tab. 4]. Tuyên bố "thống nhất các cách tiếp cận trước" [tr. 1–3] là một cách diễn giải (Laplace, điều chuẩn cục bộ), không phải một định lý được chứng minh (tôi suy ra).

## 7. Kiểm chứng của người ghi chú — script trong `code/`, lệnh chạy, kết quả thật

Script: `code/chen2022epropnp_check.py` (numpy/scipy + cv2 cho EPnP/IPPE khởi tạo; seed cố định; ≈ 42 s trên CPU). Tham số hoá y = (ω, δ), R = exp(ω)R₀, t = t₀ + δ, độ đo Lebesgue trên (ω, δ) — đây là lựa chọn của tôi, bài không nêu. Đề xuất AMIS: một phân bố t 6D (ν = 5), cập nhật bằng mô-men có trọng số — **đơn giản hơn** đề xuất tách vị trí/hướng của bài.

Lệnh (từ gốc repo): `python3 VSLAM/pnp/code/chen2022epropnp_check.py`

Kết quả thật (đã cắt bớt):

```
== C1: log Z — IS vanilla eq.(6), AMIS Alg.1, Laplace ==
  [gần Gauss (N=12, σ=1px, sâu 4–8m)]  Laplace = -34.7324   tham chiếu IS 8x2^17 mẫu = -34.7336   Laplace - ref = +0.0012
         M |    IS vanilla: TB ± std (20 lần) |       AMIS T=4: TB ± std
       128 |       -34.7331 ± 0.1083          |   -35.0329 ± 0.1393
       512 |       -34.7311 ± 0.0319          |   -34.7887 ± 0.0383
      2048 |       -34.7314 ± 0.0198          |   -34.7465 ± 0.0135
      8192 |       -34.7278 ± 0.0096          |   -34.7380 ± 0.0082
[PASS] C1a: hậu nghiệm gần Gauss: |Laplace - MC| = 0.0012 < 0.05; std AMIS giảm 0.1393 -> 0.0082
    đề xuất khởi đầu tồi (lệch 2σ, cov x0.3), 512 mẫu: IS vanilla -34.868 ± 0.350 | AMIS -35.092 ± 0.213 | ref -34.734
[FAIL] C1c: AMIS sửa được đề xuất tồi: sai lệch |AMIS-ref| = 0.358 < |IS-ref| = 0.135
  [không Gauss (N=4, σ=40px, sâu 20–40m)]  Laplace = 1.4796   tham chiếu IS 8x2^17 mẫu = 1.7464   Laplace - ref = -0.2668
       128 |         1.7289 ± 0.2936          |     0.8777 ± 0.3502
       512 |         1.8654 ± 0.5116          |     1.4626 ± 0.1300
      2048 |         1.8081 ± 0.1875          |     1.6525 ± 0.0435
      8192 |         1.7686 ± 0.1247          |     1.7207 ± 0.0174
[PASS] C1b: hậu nghiệm không Gauss: Laplace lệch MC -0.2668 nat; MC vẫn hội tụ (std 0.3502 -> 0.0174)

== C2: gradient theo trọng số, eq. (8) vs sai phân hữu hạn ==
[PASS] C2: ||eq.(8) - FD|| / ||FD|| = 9.62e-10 (N=20, 512 mẫu AMIS, mẫu cố định)
      T=4, K'=  32: 0.0601 (TB 10 lần)      <- sai số tương đối so với tham chiếu 2^16 mẫu
      T=4, K'= 128: 0.0236 (TB 10 lần)
      T=4, K'= 512: 0.0106 (TB 10 lần)

== C3: diễn giải eq. (8) — ngoại lai (4/20 điểm lệch 8px, σ=1px) ==
    -dL/dw (tổng 2 trục)  ngoại lai: [-24.77  -1.07 -20.46 -12.58]
                          nội điểm : TB +2.029, min -1.898, max +5.691
    ngoại lai: r^2(y_gt) [70.2 44.1 54.3 37.6] | r^2(y*) [44.9 42.9 33.4 24.8] | E_p r^2 [45.4 43.  33.8 25.1]
[PASS] C3a: mọi ngoại lai có -dL/dw < 0 (trọng số bị đẩy xuống), đúng dấu tuyên bố ở §3.3
[NOTE] C3a' (giả thuyết của tôi, mạnh hơn bài nói) 'mọi ngoại lai bị đẩy mạnh hơn mọi nội điểm': SAI: ngoại lai yếu nhất -1.07 vs nội điểm thấp nhất -1.90 ...
    sau 150 bước GD trên log w (lr 0.05): L_KL -16.03 -> -35.74
      w ngoại lai: [1.19  0.75  0.515 1.707] ; w nội điểm: TB 3.044 (min 1.597)
      sai số y* so với GT: quay 0.2484° -> 0.0447°, tịnh tiến 3.28 cm -> 0.34 cm
      tỉ số w ngoại lai / nội điểm (TB): 1.000 -> 0.342; ở điểm dừng |r^2(y_gt) - E_p r^2| ngoại lai [4.47 1.39 3.02 1.35] (điều kiện dừng của eq. (8) là = 0)
[PASS] C3b: tối ưu L_KL hạ tương đối trọng số ngoại lai (tỉ số 0.342 < 0.5) và y* tốt lên; nhưng w ngoại lai KHÔNG về 0 (nhỏ nhất 0.515)

== C4: vì sao cần log Z — quét thang trọng số w = s·(1/σ) ==
         s |     L_tgt | L_pred=logZ |      L_KL |  ||y*-y_gt||^2 (BPnP-kiểu)
      0.05 |     0.019 |      -8.189 |    -8.170 |                  7.449e-04
      0.30 |     0.676 |     -19.554 |   -18.878 |                  7.449e-04
      1.00 |     7.507 |     -32.552 |   -25.045 |                  7.449e-04
      1.50 |    16.891 |     -42.914 |   -26.023 |                  7.449e-04
      3.00 |    67.563 |     -89.888 |   -22.325 |                  7.449e-04
     10.00 |   750.705 |    -674.328 |    76.377 |                  7.449e-04
[PASS] C4a: L_tgt đơn điệu -> 0 khi s -> 0 (suy biến), L_KL có cực tiểu trong khoảng, tại s = 1.5
[PASS] C4b: loss điểm ||y*-y_gt||^2 không đổi theo s (dao động 1.1e-11) -> không học được thang/độ bất định
[PASS] C4c: thang tối ưu của L_KL (MC) s = 1.605 vs dự đoán Laplace sqrt(3/(L_tgt - E*)) = 1.605

== C5: lưỡng nghĩa — target phẳng xa, y* nhảy nhánh, L_KL liên tục ==
     α(px) | ∠(R*,R_gt)° | E nhánh1 | E nhánh2 |  logZ MC | logZ Laplace@y*
     -0.30 |        3.37 |    0.080 |    0.231 |  -14.396 |         -15.256
      0.00 |       43.60 |    0.006 |    0.048 |  -14.269 |         -15.166
      0.30 |       43.85 |    0.140 |    0.374 |  -14.494 |         -15.326
    góc giữa hai nhánh: 45.8°–46.0°
[PASS] C5a: y* (cực tiểu toàn cục) nhảy 40.3° giữa hai bước α cách 0.1 px -> ánh xạ X -> y* không liên tục
[PASS] C5b: log Z (MC, trộn hai mode) trơn: max|Δ² - nền| = 0.0018 nat, Laplace@y* gãy tại chỗ đổi nhánh: 0.0309 nat (độ cong nền -0.040)
[PASS] C5c: Laplace quanh một nghiệm hụt log Z tới 0.906 nat khi hai mode ngang nhau (≈ log 2)

Tổng: 11/12 PASS; thời gian 41.7 s
```

**Đọc kết quả.**

- *C1 (eq. (6), Alg. 1).* Khi hậu nghiệm gần Gauss, Laplace với Hessian Gauss–Newton JᵀJ khớp tham chiếu MC tới 0,001 nat, và cả IS lẫn AMIS hội tụ với độ lệch chuẩn giảm cỡ 1/√M [M]. Với ngân sách của bài (T = 4, K′ = 128, tức 512 mẫu) AMIS lệch thấp ≈ 0,055 nat — độ chệch Jensen của log-trung-bình, không phải lỗi [M]. Trong ca không Gauss (4 điểm, nhiễu 40 px, xa 20–40 m), Laplace thiếu 0,27 nat, và AMIS có độ lệch chuẩn nhỏ hơn IS thường 7 lần ở 8192 mẫu (0,017 so với 0,125) — đây là chỗ AMIS đáng tiền [M]. **Kết quả âm (C1c):** khi đề xuất ban đầu bị làm tồi có chủ ý (lệch 2σ, covariance ×0,3), AMIS của tôi ở 512 mẫu còn tệ hơn IS thường; tức là AMIS với ngân sách nhỏ không "tự sửa" được khởi đầu kém trong 6D. Cách cập nhật đề xuất của tôi thô hơn của bài, nên đây không bác bỏ bài, nhưng cho thấy chất lượng log Z phụ thuộc mạnh vào khởi đầu Laplace [M].
- *C2 (eq. (8)).* Công thức giải tích của gradient theo w khớp sai phân hữu hạn của chính ước lượng MC tới 1e-9 khi giữ mẫu cố định (tức coi đề xuất q là hằng — điều bài ngầm làm khi "lan truyền ngược từng mẫu có trọng số" [§3.3]) [M]. Sai số tương đối của gradient MC so với tham chiếu là ≈ 2,4 % ở cấu hình của bài.
- *C3 (diễn giải eq. (8)).* Đúng dấu: cả 4 ngoại lai nhận gradient làm giảm trọng số [M]. Nhưng dấu phụ thuộc vào r²(y_gt) − E_p r² ≈ r²(y_gt) − r²(y\*), **không phải** vào độ lớn r²(y_gt): ngoại lai số 2 có r² tại y_gt là 44,1 px² nhưng r² tại y\* là 42,9 px² nên gradient gần 0 (−1,07), yếu hơn cả một nội điểm [M]. Khi tối ưu trọng số theo L_KL, trọng số ngoại lai giảm tương đối (tỉ số 0,34) và pose tốt lên (0,25° → 0,045°), nhưng **không về 0**: điều kiện dừng là r²(y_gt) = E_p r², nên ngoại lai được coi như điểm có phương sai lớn chứ không bị loại [M]. Trên một cảnh duy nhất, trọng số nội điểm cũng bị đẩy lên quá 1/σ (TB 3,04) — dấu hiệu quá khớp một mẫu (tôi suy ra).
- *C4 (Fig. 2, §3.1).* Chỉ L_tgt thì trọng số tối ưu là 0 (suy biến); L_KL có cực tiểu hữu hạn; loss kiểu điểm ‖y\* − y_gt‖² hoàn toàn bất biến theo thang trọng số (y\* không đổi khi nhân mọi w với s) nên không mang thông tin về độ tập trung/bất định [M]. Dưới Laplace, L_KL(s) = s²(L_tgt − E\*) − 6 log s + const, nên s_opt² (L_tgt − E\*) = d/2 = 3; MC cho s = 1,605 đúng như dự đoán — nghĩa là EPro-PnP hiệu chuẩn trọng số trong **không gian pose** (khoảng Mahalanobis của y_gt), không trong không gian pixel (tôi suy ra, cửa (a)+(b)).
- *C5 (lưỡng nghĩa).* Với hình vuông phẳng 20 cm ở 6 m, dịch ảnh 0,1 px làm cực tiểu toàn cục y\* nhảy 40° sang nhánh kia — ánh xạ X → y\* không liên tục, đúng chẩn đoán ở §1/§3.1 [M]. log Z tính bằng MC trơn (độ gãy 0,002 nat, cỡ nhiễu), còn Laplace tại y\* có gãy nhỏ (0,03 nat) và hụt 0,6–0,9 nat so với MC vì bỏ sót mode thứ hai. Ghi chú kỹ thuật: lần đầu tôi đặt toạ độ tích phân quanh y\*, khi y\* đổi nhánh thì độ đo Lebesgue trên toạ độ exp (không phải độ đo Haar) tự sinh một chỗ gãy giả ≈ 0,01–0,02 nat; phải cố định điểm tham chiếu mới hết — minh hoạ cụ thể cho giả thiết 3 ở §2.
- Cách tôi xử lý các FAIL ban đầu (ghi lại cho trung thực): phiên bản đầu có 5 FAIL; ba cái do tiêu chí của tôi sai (ngưỡng tương đối 1e-10 quá chặt cho C4b; tiêu chí C5b dùng sai phân bậc một nên lẫn với độ dốc tự nhiên; C3 đòi "về 0" là mạnh hơn bài nói) và đã sửa tiêu chí; C3a′ giữ lại dưới dạng NOTE; C1c giữ là FAIL (đề xuất "tồi" ban đầu của tôi — lệch 3σ theo từng trục trong 6D có tương quan — quá cực đoan nên đã dịu lại còn 2σ dọc trục chính, và vẫn FAIL).
- **Chưa kiểm**: eq. (9)/(10) (điều chuẩn đạo hàm), đề xuất von Mises/ACG, Huber eq. (11)/(12), mọi con số benchmark.

## 8. Chỗ tôi không tin

- **"Nghiệm tất định vốn không khả vi" như lời giải thích cho thất bại của BPnP.** Ánh xạ X → y\* chỉ gián đoạn trên tập đổi nhánh (C5a) và khả vi hầu khắp nơi theo định lý hàm ẩn; một luận cứ "không khả vi ở một số điểm" [tr. 2] không tự nó giải thích vì sao huấn luyện phân kỳ. C4b gợi ý một nguyên nhân khác, cụ thể hơn: loss điểm ‖y\* − y_gt‖² bất biến theo thang trọng số, nên không có gì ngăn trọng số trôi hay suy biến; và L_tgt thì có nghiệm suy biến. Tức là cái thiếu là **số hạng chuẩn hoá**, không phải tính khả vi [M]. Bài chính cũng nói L_pred "crucial to a discriminative loss" [tr. 3], nên hai cách giải thích tồn tại song song trong bài mà không được tách bằng thí nghiệm.
- **Baseline "vi phân ẩn" trong Tab. 3 không phải BPnP.** Nó cực tiểu khoảng cách pose của eq. (10) thay vì loss tái chiếu của BPnP [Tab. 3 chú thích], và BPnP gốc bị loại khỏi Tab. 2 vì chia dữ liệu khác. Vậy tuyên bố "BPnP không học được toàn bộ tương ứng từ đầu" chỉ được kiểm trên một biến thể do chính tác giả dựng, một lần chạy, không có phương sai [M].
- **Diễn giải eq. (8) là "điểm có sai số tái chiếu lớn bị giảm trọng số"** [tr. 4] chỉ đúng tương đối so với E_p r², mà E_p r² ≈ r²(y\*); ngoại lai mà pose dự đoán không "hút" được vẫn gần như không bị phạt (C3). Và ngoại lai không bị đưa về 0 (C3b): KL với likelihood Gauss coi ngoại lai là điểm nhiễu lớn, chưa phải loại bỏ — có lẽ đó là lý do thực nghiệm thêm Huber [eq. (11)] (tôi suy ra).
- **Fig. 3 "tách" trọng số học được thành nghịch bất định × phân biệt** — trong bài chính tôi không tìm thấy cách hai thành phần này được tính ra; có thể chỉ là minh hoạ [Fig. 3, tr. 4].
- **Tính vòng tròn giữa Laplace và AMIS.** Bài chê Laplace không chính xác khi lưỡng nghĩa [tr. 3] nhưng khởi đầu AMIS bằng chính Laplace tại một nghiệm [Alg. 1]; với ngân sách 512 mẫu, C1c cho thấy AMIS (bản của tôi) không cứu được khởi đầu kém. Việc Fig. 6 bắt được yaw đa mode có lẽ nhờ thành phần đều trong đề xuất von Mises + đều cho yaw 1D (tôi suy ra), không hiển nhiên chuyển được sang hướng 3D.
- **Con số không có phương sai**: các bước +0,97 (B3) hay +1,88 (B1) trong Tab. 1 là một lần chạy; tôi không biết chúng có vượt nhiễu giữa các seed không.
- **"Đóng khoảng cách với các phương pháp dẫn đầu"** [tr. 1]: trên nuScenes test, mAP của EPro-PnP (0,373) thấp hơn PGD (0,386) [Tab. 4]; lợi thế nằm ở mATE/mAOE và NDS.

## 9. Chỗ tôi chưa hiểu (→ `99-chua-biet.md`)

- Độ đo `dy` trên SE(3) mà bài thực sự dùng (Haar? Lebesgue trên toạ độ nào?) và nó có ảnh hưởng gì tới hậu nghiệm rộng (nuScenes, yaw) — phụ lục có thể nói, tôi chưa đọc.
- Với vật đối xứng (ADD-S trên LineMOD; barrier/cone trên nuScenes) đích Dirac tại một y_gt phạt các pose tương đương; bài xử lý bằng cách nào (đích đa mode? chọn GT gần nhất?) — không thấy trong bài chính.
- Gradient của L_pred có đi qua đề xuất q (qua y\*, Σ_y\*) hay q bị tách? Về lý thuyết IS vẫn không chệch nếu tách (tôi suy ra, C2 dùng cách tách), nhưng bài chính không ghi.
- Eq. (8) dẫn cho dạng bình phương; với Huber [eq. (11)] và "ngưỡng thích nghi" (phụ lục) diễn giải bất định/phân biệt còn đúng không?
- Vì sao bỏ mẫu số Softmax không gian thì phân kỳ [Tab. 1, D0] trong khi L_KL (qua C4) đã tự có cực tiểu theo thang trọng số — phải chăng do bất biến thang giữa w và "global weight scaling" tạo hướng phẳng?
- AMIS ước lượng log của trung bình nên chệch âm ở mẫu nhỏ (≈ −0,055 nat ở 512 mẫu trong C1); gradient của log Z vì thế là ước lượng tự chuẩn hoá có chệch — có ảnh hưởng gì tới huấn luyện không?

## 10. Quan hệ với các bài khác trong `refs.bib`

- `chen2020bpnp` (BPnP): vi phân ẩn qua y\*; EPro-PnP xếp nó vào "xấp xỉ Laplace" [§3.1, tr. 3] và coi eq. (10) là họ hàng của loss từ vi phân ẩn [tr. 5]. Mâu thuẫn ở khẳng định: BPnP có học được toàn bộ tương ứng không cần loss thay thế — EPro-PnP nói không [tr. 2, Tab. 3], nhưng kiểm trên biến thể, không phải BPnP gốc (§8).
- `campbell2020blindpnp` ([7]): loss L2 trên pose, là trường hợp đặc biệt Σ đồng nhất của Laplace [tr. 3] [T].
- `brachmann2017dsac`: Softmax rời rạc trên tập giả thuyết hữu hạn; EPro-PnP tự nhận là phiên bản liên tục [§2, tr. 2]. `brachmann2018dsacpp` ([4]): học toạ độ 3D qua PnP khả vi [tr. 2].
- `peng2019pvnet` ([31]) và MonoRUn ([11], không có trong `refs.bib`): học tương ứng có nhận thức bất định, theo bài chỉ có số hạng "bất định" của eq. (8) [tr. 4] [T].
- `urban2016mlpnp`, `vakhitov2021uncertainty`: PnP có covariance từng điểm, giả thiết nhiễu đã biết; EPro-PnP **học** trọng số (≈ nghịch độ lệch chuẩn chéo) bằng tín hiệu pose (tôi suy ra) — câu hỏi 3 của `00-cau-hoi.md`.
- `schweighofer2006planar` ([33]), `collins2014ippe`: nguồn gốc lưỡng nghĩa phẳng mà bài viện dẫn [tr. 2–3]; C5 dùng IPPE để lấy hai nhánh.
- `wang2021gdrnet` ([39]), `liu2025gdrnpp`: hướng ngược lại — thay PnP bằng mô-đun học; GDRNet\* cùng baseline CDPN nên so sánh ở Tab. 2 là công bằng theo tác giả [Tab. 2 chú thích].
- `chen2025epropnp`: bản T-PAMI mở rộng — chưa đọc.
- Không có trong `refs.bib`: CDPN [24], MonoRUn [11], AMIS của Cornuet và cộng sự [12], Deep declarative networks của Gould và cộng sự [16], RePOSE [20], FCOS3D [41], PGD [42].

## 11. Nó đổi gì trong suy nghĩ

Với câu hỏi 8 của khảo sát ("PnP khả vi giải bài toán gì?"), bài này (cộng C4) cho tôi một câu trả lời sắc hơn: vấn đề chính của học qua PnP không nằm ở việc lấy đạo hàm của y\*, mà ở chỗ một loss chỉ nhìn vào nghiệm điểm không ràng buộc được **độ tập trung** của năng lượng quanh nghiệm — cần số hạng log Z, giống mẫu số Softmax [M]. Đầu ra lúc suy luận vẫn là nghiệm LM của eq. (1) [§3.4, tr. 4], nên pose vẫn là một ước lượng hình học diễn giải được; phần mới là trọng số học được có nghĩa thống kê (nghịch độ lệch chuẩn), được hiệu chuẩn trên không gian pose (C4c) chứ không trên pixel [M]. Tôi cũng bớt tin vào câu "nghiệm tất định không khả vi" như một lời giải thích: nó đúng nhưng hiếm (C5a), và không phải lý do chính (§8).

## 12. Câu hỏi tự kiểm (3–5 câu, hỏi *vì sao* / *khi nào hỏng*)

1. Vì sao chỉ cực tiểu L_tgt (sai số tái chiếu tại y_gt) lại suy biến khi học cả trọng số, và số hạng log Z ngăn điều đó bằng cơ chế nào? Viết L_KL(s) dưới Laplace và tìm s tối ưu.
2. Khi nào gradient eq. (8) **không** giảm trọng số của một ngoại lai rõ ràng? (Gợi ý: so r²(y_gt) với r²(y\*).)
3. Vì sao loss ‖y\* − y_gt‖² không học được thang trọng số, và điều đó liên quan gì tới câu "Laplace với Σ đồng nhất" ở §3.1?
4. Khi nào AMIS khởi đầu từ Laplace tại một nghiệm PnP ước lượng sai log Z, và sai theo chiều nào (thiếu hay thừa)?
5. Nếu thay độ đo `dy` (Haar ↔ Lebesgue trên toạ độ exp), điều gì trong L_KL đổi và khi nào sự khác biệt đáng kể?

## Trích đoạn nguyên văn làm bằng chứng

- "a PnP problem can have ambiguous solutions [27,33], which makes backpropagation unstable." [tr. 2]
- "Previous work [4, 7, 10] only backpropagates through a local solution y∗, which is inherently unstable and non-differentiable." [tr. 3]
- "Eq. (3) can be interpreted as a continuous counterpart of categorical Softmax." [tr. 3]
- "the first term alone cannot handle learning all 2D-3D points without imposing strict regularization" [tr. 3]
- "is inaccurate for non-normal posteriors with ambiguity, therefore does not guarantee global convergence." [tr. 3]
- "correspondences with large reprojection error (hence high uncertainty) shall be weighted less." [tr. 4]
- "The positive sign indicates that sensitive correspondences should be weighted more, because they provide stronger pose discrimination." [tr. 4]
- "when the coordinate regression loss is removed, both implicit differentiation and reprojection loss fail to learn the pose properly." [tr. 7]
