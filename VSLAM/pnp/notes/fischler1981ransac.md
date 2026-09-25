# Random Sample Consensus: A Paradigm for Model Fitting with Applications to Image Analysis and Automated Cartography — ghi chú đọc

| | |
|---|---|
| bibkey | `fischler1981ransac` |
| Venue, năm | *Communications of the ACM* 24(6), tr. 381–395, tháng 6/1981; DOI 10.1145/358669.358692 (đã đối chiếu Crossref 2026-09-25: đúng tên tạp chí, tập, số, trang) |
| Bản đã đọc | `papers/fischler1981ransac.pdf` — bản quét bản xuất bản do SRI lưu, 15 trang (trang PDF 1–15 = trang tạp chí 381–395) |
| Mức đọc | lượt 2 toàn bài; lượt 3 cho §II (RANSAC, công thức E(k), SD(k), k; cách chọn dung sai và t) và §III + Phụ lục A (P3P, số nghiệm 3/4/5/6 điểm, Fig. 5–7) |
| Người đọc | Claude (agent), 2026-09-25 — **Huy chưa đọc lại để ký** |
| Mức tin | giữ **A** — CACM có phản biện; công thức §II-B và ví dụ Fig. 5 tôi tái lập được (mục 7); RANSAC và kết quả "P3P tối đa 4 nghiệm" đã được nhiều nhóm độc lập dùng và phân tích lại (`haralick1994review`, `gao2003p3p`) |
| Kiểm chứng | E(k), E(k²), SD(k): cửa (a)+(b). k = log(1−z)/log(1−b): (a)+(b). Hệ số quartic (A19)–(A23): (b) trên 3000 cấu hình. Fig. 5 (4 nghiệm P3P), Fig. 6 (P4P 2 nghiệm), Fig. 7 (P5P 2 nghiệm): (b). "4 điểm đồng phẳng → duy nhất": (b) thống kê, không chứng minh. "P6P luôn duy nhất": (b) — **đúng với cấu hình ngẫu nhiên, sai ở cấu hình tới hạn** |

## 1. Bài toán gốc và bối cảnh

Bối cảnh là phân tích ảnh tự động cho bản đồ học tại SRI: đầu vào của bước diễn giải đến từ các bộ dò đặc trưng cục bộ, và các bộ dò này mắc hai loại lỗi khác nhau về bản chất [§I, tr. 3]. Lỗi đo (lệch vị trí vài pixel) gần phân bố chuẩn nên bình phương tối thiểu làm trơn được; lỗi phân loại (nhận nhầm một vùng ảnh là điểm mốc) là *lỗi thô (gross error)*, không trung bình hoá đi được [T] [§I, tr. 3]. Cách xử lý phổ biến trước đó là khớp bình phương tối thiểu trên toàn bộ dữ liệu rồi lặp lại việc loại điểm có phần dư lớn nhất [T] [§I, tr. 1]; Fig. 1 [tr. 2] dựng một ví dụ 7 điểm trong đó chỉ một điểm sai (10, 2) đã kéo đường khớp lệch đủ để heuristic này loại nhầm các điểm đúng và dừng với 4 điểm còn lại, trong đó có điểm sai.

Bài toán ứng dụng là *bài toán xác định vị trí (Location Determination Problem, LDP)*: biết toạ độ 3D của các điểm mốc và ảnh của chúng, tìm điểm trong không gian nơi ảnh được chụp [§III, tr. 5]. Trong trắc địa ảnh, việc này được giải bằng bình phương tối thiểu lặp với người vận hành tự tay ghép điểm ảnh với điểm mốc [T] [§III, tr. 5]; khi ghép tự động thì có ngoại lai, và phương pháp lặp cần điểm khởi tạo tốt [T] [§I, tr. 3]. RANSAC cần một bộ giải từ *ít điểm nhất có thể*, nên bài phải trả lời "cần tối thiểu bao nhiêu điểm mốc" và đưa ra lời giải dạng đóng cho trường hợp tối thiểu [T] [§III, tr. 5]. Chính ở đây bài đặt tên "perspective-n-point problem (PnP)" [§III, tr. 5] — nguồn gốc của thuật ngữ mà cả khảo sát này dùng.

## 2. Giả thiết — kể cả giả thiết ngầm; bỏ đi thì hỏng ở đâu

Giả thiết nêu rõ trong bài:

- Tương ứng 2D–3D đã có (có thể sai), nội tham số đã biết — tiêu cự và điểm chính — để tính được góc giữa hai tia từ tâm chiếu [T] [§III, tr. 5]. Bỏ giả thiết này thì P3P không còn đủ ràng buộc; đó là họ P4Pf/P4Pfr trong `refs.bib` (tôi suy ra).
- Camera nằm "bên ngoài và phía trên" bao lồi của các điểm mốc [T] [§III, tr. 5]. Bài không nói giả thiết này được dùng ở bước nào; tôi đoán nó dùng để loại các nghiệm P3P nằm "dưới" địa hình [M].
- Xác suất một điểm dữ liệu nằm trong dung sai của mô hình đúng là một hằng số w, và các lần rút điểm độc lập [T] [§II-B, tr. 4].
- Xác suất y để một điểm rơi vào dung sai của một mô hình *sai* nhỏ hơn w, và cụ thể dưới 0,5 [T] [§II-C, tr. 4].

Giả thiết ngầm mà tôi thấy khi dựng lại [M]:

- **Lấy mẫu có hoàn lại / tập dữ liệu vô hạn.** Công thức b = wⁿ coi n điểm được rút độc lập. Thực tế RANSAC rút n điểm *khác nhau* từ N điểm; xác suất mẫu sạch là C(wN, n)/C(N, n) < wⁿ. Với N = 20, w = 0,5, n = 4, số lần thử trung bình là 23,1 thay vì 16 (+44 %), và số lần k tính cho z = 0,99 chỉ đạt 0,96 (mục 7). Với N ≥ 100 sai lệch chỉ vài phần trăm.
- **"Mẫu sạch ⇒ mô hình đúng ⇒ tập đồng thuận đủ lớn."** Mô hình dựng từ 3 điểm có nhiễu lệch khá xa so với mô hình thật, nên không phải mọi inlier đều rơi trong dung sai của nó. Trong thí nghiệm của tôi, số lần thử tới khi đạt đồng thuận ≥ 0,8·wN luôn lớn hơn số lần tới mẫu sạch đầu tiên (mục 7). Công thức E(k) của bài chỉ đếm tới *mẫu sạch*, không đếm tới *đồng thuận đủ lớn*.
- **y không phụ thuộc điểm.** Một mô hình dựng từ 2 inlier + 1 ngoại lai vẫn gần đúng quanh hai inlier đó, nên các inlier gần đó dễ rơi vào dung sai hơn hẳn trung bình. Đây là lý do một mô hình sai vẫn có thể đạt t = n + 5 điểm (mục 7).

## 3. Cơ chế — năm câu, rồi chi tiết có định vị

**Năm câu.** (1) Thay vì khớp trên mọi dữ liệu rồi loại dần điểm xấu, RANSAC rút ngẫu nhiên đúng n điểm — số tối thiểu để xác định mô hình — dựng mô hình, rồi đếm có bao nhiêu điểm khác nằm trong dung sai của nó (tập đồng thuận) [§II, tr. 3]. (2) Nếu tập đồng thuận vượt ngưỡng t thì làm trơn (bình phương tối thiểu) trên tập đó; nếu không thì rút mẫu mới, và sau một số lần thử định trước thì lấy tập đồng thuận lớn nhất hoặc báo thất bại [§II, tr. 3]. (3) Số lần thử được chọn theo xác suất rút trúng một mẫu toàn điểm đúng: kỳ vọng w⁻ⁿ, và cần k = log(1−z)/log(1−wⁿ) lần để chắc chắn với xác suất z [§II-B, tr. 4]. (4) Với LDP, mô hình tối thiểu là P3P: hệ ba phương trình định lý cos [A*] cho độ dài ba "chân" từ tâm chiếu tới ba điểm mốc, quy về một đa thức bậc bốn, có tối đa 4 nghiệm dương [§III-A, tr. 6; Phụ lục A]. (5) Bài còn khảo sát khi nào nghiệm là duy nhất: 4 điểm đồng phẳng thì duy nhất, 4 hoặc 5 điểm không đồng phẳng có thể có 2 nghiệm, 6 điểm ở vị trí tổng quát thì duy nhất [§III-A, tr. 6–9].

**Chi tiết RANSAC [§II].**

- Phát biểu hình thức ở [§II, tr. 3]; hai cải tiến được gợi ý ngay: chọn mẫu có định hướng nếu bài toán cho phép, và sau khi có mô hình thì thêm mọi điểm phù hợp rồi khớp lại [T] [§II, tr. 3]. Cải tiến thứ hai chính là bước "khớp lại trên inlier" mà mọi cài đặt về sau đều có (tôi suy ra).
- Ba tham số tự do: dung sai, số lần thử, ngưỡng t [§II, tr. 3].
- *Dung sai* [§II-A, tr. 3–4]: nếu không tính giải tích được thì ước lượng bằng thực nghiệm — nhiễu hoá dữ liệu, dựng mô hình, đo sai số, đặt dung sai ở "một hoặc hai độ lệch chuẩn" trên sai số trung bình [T]. Bài thừa nhận dung sai lẽ ra phải khác nhau cho từng điểm, nhưng cho rằng một dung sai chung thường đủ [T] [§II-A, tr. 4].
- *Số lần thử* [§II-B, tr. 4]: với b = wⁿ, a = 1 − b, số lần thử tới mẫu sạch đầu tiên có phân bố hình học: E(k) = b(1 + 2a + 3a² + …) = 1/b = w⁻ⁿ; E(k²) = (2 − b)/b²; SD(k) = √(1 − wⁿ)/wⁿ. Các công thức ở §II **không đánh số**; tôi định vị chúng bằng [§II-B, tr. 4]. Bảng E(k) cho w = 0,2…0,9 và n = 1…6 nằm ở [tr. 4]. Ví dụ trong bài: w = 0,5, n = 4 cho E(k) = 16, SD(k) = 15,5, và k = log(0,1)/log(15/16) = 35,7 cho z = 0,9 [§II-B, tr. 4]. Bài lưu ý SD(k) ≈ E(k) nên nên thử gấp 2–3 lần E(k) [T] [§II-B, tr. 4]; khi wⁿ ≪ 1 thì k ≈ 2,3·E(k) cho z = 0,90 và ≈ 3,0·E(k) cho z = 0,95 [§II-B, tr. 4].
- *Ngưỡng t* [§II-C, tr. 4]: t phải đủ lớn để (i) chắc rằng mô hình đúng đã được tìm và (ii) đủ điểm cho bước làm trơn. Cho (i), muốn y^(t−n) nhỏ; với y < 0,5, chọn t − n = 5 cho xác suất "trùng hợp với mô hình sai" dưới 5 % [T]. Cho (ii), dẫn về lý thuyết bình phương tối thiểu [§II-C, tr. 4–5].
- Ví dụ Fig. 1 với RANSAC [§II-D, tr. 5]: w = 0,85, dung sai 0,8; cặp 2 điểm, kỳ vọng 2–3 lần thử, hoặc duyệt đủ 21 cặp; tìm được tập 6 điểm đúng [T].

**Chi tiết LDP / PnP [§III, Phụ lục A, B].**

- LDP được quy về: biết khoảng cách giữa các điểm mốc và góc nhìn từ tâm chiếu (CP) tới mọi cặp điểm, tìm độ dài các đoạn nối CP với từng điểm mốc; bài gọi đây là PnP [§III, tr. 5]. Khi có ba độ dài thì vị trí CP và hướng mặt ảnh tính trực tiếp được [Phụ lục A mục 4, tr. 12–13].
- P1P, P2P: vô số nghiệm; với P2P, CP nằm trên đường tròn đường kính R_ab / sin θ_ab quay quanh dây AB [§III-A, tr. 6; Fig. 3]. [M] Chính xác hơn, chỉ *cung lớn* (khi θ_ab < 90°) nhìn AB dưới góc θ_ab; cung còn lại nhìn dưới góc π − θ_ab (định lý góc nội tiếp) — tập nghiệm là mặt xuyến xoay từ một cung, không phải cả đường tròn.
- P3P: hệ [A*] gồm ba phương trình (R_ab)² = a² + b² − 2ab·cos θ_ab (và hoán vị) [§III-A, tr. 6]. Lập luận số nghiệm: theo Bézout tối đa 2·2·2 = 8 nghiệm; mọi hạng tử đều bậc 2 hoặc hằng nên (a, b, c) là nghiệm thì (−a, −b, −c) cũng là nghiệm; vậy tối đa 4 nghiệm dương [T] [§III-A, tr. 6]. Fig. 5 [tr. 7] cho ví dụ đạt đủ 4 nghiệm: đáy tam giác đều cạnh 2√3, ba chân dài 4, cos α = 5/8; quay tâm chiếu quanh BC cho chân L′A = 1 [tr. 7], và do đối xứng bậc ba có thêm hai nghiệm nữa.
- Lời giải đại số [Phụ lục A mục 1, tr. 11–12]: đặt b = x·a, c = y·a [eq. (A4)], khử a để được (A8), (A9); đặt K1 = R_bc²/R_ac², K2 = R_bc²/R_ab² [eq. (A10)]; hai phương trình bậc hai theo y [eq. (A11)–(A14)] được khử y để ra đa thức bậc bốn theo x [eq. (A18)] với hệ số G4…G0 [eq. (A19)–(A23)]. Từ mỗi nghiệm dương x: a từ (A24), b = a·x (A25), y từ (A26) nếu m′q ≠ mq′, ngược lại hai giá trị y từ (A27) và phải kiểm lại bằng (A3) [tr. 12]. Bài tự lưu ý rằng vì mỗi nghiệm của (A18) có thể cho hai nghiệm, bản thân đa thức bậc bốn không đủ để chứng minh "tối đa 4" — phải dùng lập luận ở thân bài [T] [Phụ lục A, tr. 12].
- Có kèm một phương pháp lặp đơn giản: trượt đỉnh A dọc tia của nó, mỗi vị trí cho tối đa 4 tam giác thoả hai cạnh R_ab, R_ac; lặp để cạnh thứ ba đúng R_bc [Phụ lục A mục 3, tr. 12; Fig. 8]. Thí nghiệm §IV-D dùng chính phương pháp lặp này chứ không dùng dạng đóng [T] [§IV-D, tr. 10].
- P4P đồng phẳng (CP không nằm trên mặt phẳng, không có 3 điểm thẳng hàng): Phụ lục B cho nghiệm duy nhất qua ma trận collineation 3×3 [T] [§III-A, tr. 6; Phụ lục B, eq. (B1)–(B14), tr. 13–15].
- P4P không đồng phẳng: "ngạc nhiên" là có thể có ít nhất 2 nghiệm; Fig. 6 [tr. 8] dựng ví dụ cụ thể: L(0, 0, 144/5), A(0, 12, 0), B(10, −12, 0), C(−10, −12, 0), D(0, 0, −5), nghiệm thứ hai có A′(0, 828/169, 2880/169) và D′(0, 0, 5), quay quanh BC với cos = 119/169 [§III-A, tr. 6; Fig. 6]. Cách giải đề nghị: chạy P3P trên hai bộ ba khác nhau và lấy nghiệm chung [T] [§III-A, tr. 6].
- P5P: nguyên lý "CP và các điểm mốc cùng nằm trên một đường tròn thì góc nhìn không đổi khi CP chạy trên đường tròn" được dùng để dựng Fig. 7 — 5 điểm, 2 nghiệm [§III-A, tr. 6; Fig. 7, tr. 9]. Bài nói kỹ thuật này mở rộng cho ≥ 6 điểm nhưng khi đó phải có ≥ 4 điểm đồng phẳng [T] [tr. 8].
- P6P: 6 điểm ở vị trí tổng quát luôn cho nghiệm duy nhất, lập luận qua việc giải tuyến tính 12 hệ số của ma trận chiếu T 3×4 (18 phương trình, 18 ẩn, tối đa 17 độc lập), rồi dựng một điểm tổng hợp đồng phẳng với 3 điểm đã cho và dùng Phụ lục B [T] [tr. 8–9].
- Kết luận nói số nghiệm tối đa của P4P, P5P "còn để mở" [§V, tr. 11].

**Thuật toán RANSAC/LD [§IV-A, tr. 9].** Đầu vào là danh sách m bộ 6 (toạ độ 3D, toạ độ ảnh, sai số kỳ vọng tuỳ chọn), tiêu cự và điểm chính, xác suất ghép sai 1 − w, và một "số tin cậy" G. Mỗi vòng: chọn ba điểm "tựa ngẫu nhiên" có phân bố không gian hợp lý; giải P3P dạng đóng, mỗi nghiệm coi như một lần chọn riêng; ước lượng sai số của CP bằng cách nhiễu toạ độ ảnh của ba điểm (mặc định 1 pixel); dùng sai số đó để dựng elip sai số trong ảnh cho mọi điểm mốc và gom các điểm rơi vào elip; nếu đồng thuận ≥ t ("giữa 7 và mw") thì khớp bình phương tối thiểu; dừng sau k = log(1 − G)/log(1 − w³) vòng, và thất bại nếu tập lớn nhất < 6 điểm [§IV-A, tr. 9].

## 4. Ký hiệu của bài ↔ ký hiệu của khảo sát

| Bài | Nghĩa | Khảo sát |
|---|---|---|
| CP, L | tâm chiếu (center of perspective) | tâm camera C = −Rᵀt |
| A, B, C (điểm mốc, control points) | toạ độ 3D đã biết | các hàng của `X_w` |
| a, b, c ("legs") | độ dài đoạn CP–A, CP–B, CP–C | ‖X_c‖ = ‖R X_w + t‖ (độ sâu dọc tia, không phải toạ độ z) |
| θ_ab, θ_ac, θ_bc | góc tại CP giữa hai tia | arccos(f_aᵀ f_b), với `f` là tia đơn vị |
| R_ab, R_ac, R_bc | khoảng cách giữa hai điểm mốc | ‖X_w,A − X_w,B‖ |
| x = b/a, y = c/a | tỉ số chân [eq. (A4)] | ‖X_c,B‖/‖X_c,A‖, … |
| K1, K2 | R_bc²/R_ac², R_bc²/R_ab² [eq. (A10)] | **trùng tên với K nội tham số** — không liên quan |
| focal length, principal point | nội tham số | `K`; **chữ f của bài (tiêu cự, eq. (B4)) khác `f` tia đơn vị của khảo sát** |
| T (3×4) | ma trận chiếu đồng nhất [tr. 8] | K [R \| t] sai khác hằng số |
| T (3×3) | collineation mặt phẳng → ảnh [Phụ lục B] | homography K [r₁ r₂ t] |
| P_i (Phụ lục B) | điểm ảnh | `u` (sau khi trừ điểm chính) |
| n | cỡ mẫu tối thiểu (P3P: 3) | n trong RANSAC |
| w | xác suất một điểm là inlier | 1 − ε (tỉ lệ ngoại lai ε) |
| b = wⁿ, a = 1 − b | xác suất một mẫu sạch / không sạch | — |
| k | số lần thử | số vòng RANSAC |
| z (§II-B), G (§IV-A) | độ tin cậy mong muốn | p (confidence) trong OpenCV |
| t | ngưỡng cỡ tập đồng thuận | — (các cài đặt hiện đại thường không dùng t cứng, tôi suy ra) |
| y | xác suất điểm rơi vào dung sai của mô hình sai [§II-C] | — |
| S1, S1* | mẫu và tập đồng thuận của nó | mẫu, tập inlier |
| m | số bộ tương ứng | N |

## 5. Bằng chứng — dữ liệu, phần cứng, baseline, con số kèm điều kiện, số lần lặp

Toàn bộ phần đánh giá ở [§IV-B–E, tr. 9–10] là ba thí nghiệm nhỏ, không có thống kê lặp lại, không nêu phần cứng ngoài một con số thời gian.

- **Thí nghiệm 1 — heuristic loại dần thất bại** [§IV-C, tr. 9–10]. [Đ] Một LDP với 20 điểm mốc, 5 tương ứng sai lệch hơn 10 pixel, tương ứng đúng có nhiễu chuẩn σ = 1 pixel. Heuristic (khớp tất cả, bỏ điểm lệch nhất, dừng khi điểm bị bỏ không vượt 3σ) loại đúng 2 điểm sai rồi dừng, trả về nghiệm dựa trên 18 tương ứng trong đó còn 3 điểm sai. [Đ] RANSAC tìm ra nghiệm đúng ở bộ ba thứ hai; tập đồng thuận cuối gồm mọi tương ứng đúng và không có điểm sai. Chỉ một bài toán, một lần chạy.
- **Thí nghiệm 2 — 50 LDP tổng hợp** [§IV-D, tr. 10; Tab. I]. [Đ] Mỗi bài 30 tương ứng; điểm sai lệch ≥ 10 pixel; điểm đúng có σ = 1 pixel; hai vị trí camera (nhìn thẳng xuống và nhìn xiên). P3P giải bằng phương pháp lặp của Phụ lục A, thêm một lần khớp bình phương tối thiểu thứ hai để mở rộng tập đồng thuận. [T] RANSAC không đưa điểm sai nào vào tập đồng thuận cuối trong cả 50 bài. [Đ] Tab. I chỉ in 10 bài "tiêu biểu" (5 bài w = 0,8, 5 bài w = 0,6): số tương ứng đúng 22/23/19/25/24 và 21/17/17/18/21; cỡ tập đồng thuận cuối 19/23/19/25/23 và 20/17/16/16/18; số bộ ba đã thử 6/1/2/1/3 và 11/1/6/9/9; số vị trí camera đã xét 10/3/3/2/8 và 21/1/8/21/15. [Đ] Khoảng 1 giây cho mỗi vị trí camera được xét (không nêu máy).
- **Thí nghiệm 3 — ảnh hàng không thật** [§IV-E, tr. 10]. [Đ] Ảnh chụp từ khoảng 4.000 ft với ống kính 6 inch, số hoá 2.000 × 2.000 pixel (khoảng 2 ft/pixel mặt đất); tương quan chéo tìm 25 điểm mốc, 3 điểm sai. RANSAC tìm được tập đồng thuận 17 điểm ở bộ ba đầu tiên, sau lần khớp đầu mở rộng thành đủ 22 điểm đúng. [Đ] Độ lệch chuẩn cuối: X 0,1 ft, Y 6,4 ft, Z 2,1 ft; heading 0,01°, pitch 0,10°, roll 0,12°. Bài không nói độ lệch chuẩn này tính bằng cách nào, cũng không có ground truth.

Không có baseline nào ngoài heuristic loại dần ở thí nghiệm 1, và không có so sánh với lời giải P3P lặp của Church mà bài phê phán [§V, tr. 10] (tôi suy ra từ việc đọc toàn bộ §IV).

## 6. Đóng góp thật sự (thường nhỏ hơn abstract)

[M] Đóng góp lâu dài là **một nguyên lý thiết kế** chứ không phải một thuật toán cụ thể: dựng giả thuyết từ mẫu tối thiểu rồi chấm điểm bằng số điểm đồng thuận, cộng với phép tính số lần thử theo xác suất mẫu sạch. Phần lý thuyết thật ra chỉ là kỳ vọng và phương sai của phân bố hình học — đúng, nhưng sơ cấp. Cách chọn dung sai và t chỉ là quy tắc kinh nghiệm.

[M] Về PnP, bài đóng góp ba thứ: (i) cái tên "perspective-n-point" [§III, tr. 5]; (ii) một lời giải P3P dạng đóng qua đa thức bậc bốn — nhưng không phải lời giải đầu tiên: `haralick1994review` tổng kết các lời giải P3P từ Grunert 1841 (theo ghi chú của entry đó trong `refs.bib`, tôi chưa đọc bài này), nên tuyên bố "tài liệu trắc địa ảnh hiện thời không có lời giải giải tích nào ngoài bình phương tối thiểu và phương pháp Church" [§V, tr. 10] là sai nếu xét cả văn liệu thế kỷ 19; (iii) các ví dụ phản chứng rõ ràng cho tính đa nghiệm của P4P và P5P không đồng phẳng (Fig. 6, 7), mà tôi kiểm được là đúng (mục 7). Kết quả "4 điểm đồng phẳng thì duy nhất" và "6 điểm tổng quát thì duy nhất" là đúng ở mức tổng quát nhưng lập luận cho P6P không loại trừ cấu hình tới hạn.

## 7. Kiểm chứng của người ghi chú — script trong `code/`, lệnh chạy, kết quả thật

Lệnh (từ gốc repo; seed cố định; khoảng 33–36 s trên máy của phiên này):

```
python3 VSLAM/pnp/code/fischler1981ransac_check.py
```

Kết quả thật (cắt bớt dòng; các dòng còn lại là nguyên văn, trừ hai dòng có dấu `…` là tôi gộp/rút gọn):

```
[1] Số lần thử của RANSAC (§II-B, tr. 4)
  [PASS] chuỗi số w=0.5, n=4: E(k)=16.0000 (1/b=16.0000), SD=15.4919 (sqrt(1-b)/b=15.4919)
  [PASS] chuỗi số w=0.3, n=3: E(k)=37.0370 (1/b=37.0370), SD=36.5336 (sqrt(1-b)/b=36.5336)
  [PASS] ví dụ w=0.5,n=4: E(k)=16, SD(k)≈15.5, k=log(0.1)/log(15/16)≈35.7 — SD=15.492, k=35.678
  [PASS] bảng E(k)=w^-n ở tr. 4: mọi ô lệch <= 1 đơn vị chữ số cuối — ô không khớp làm tròn thông thường: [(0.8, 5, 3.0, 3.0518)]
    z=0.9: k/E(k) = 2.303; ln(1-z) = -2.303 (âm) ; log10(1-z) = -1.000
    z=0.95: k/E(k) = 2.996; ln(1-z) = -2.996 (âm) ; log10(1-z) = -1.301
  [PASS] hệ số 2.3 / 3.0 = -ln(1-z) (log tự nhiên, cần dấu trừ; bản in thiếu dấu)
    N=1000 w=0.5 n=4: w^-n= 16.00 SD= 15.49 | có hoàn lại: mean= 16.01 sd= 15.60 | không hoàn lại: mean= 16.12 sd= 15.61 (1/p_hypergeo= 16.10)
    N=  20 w=0.5 n=4: w^-n= 16.00 SD= 15.49 | có hoàn lại: mean= 15.95 sd= 15.55 | không hoàn lại: mean= 22.88 sd= 22.22 (1/p_hypergeo= 23.07)
  [PASS] N=20,w=0.5,n=4: MC không hoàn lại khớp 1/p_hypergeo, lệch w^-n +44.2%
    N=1000 w=0.5 n=4 z=0.99: k= 72  có hoàn lại 0.9901 | không hoàn lại 0.9911
    N=  20 w=0.5 n=4 z=0.99: k= 72  có hoàn lại 0.9906 | không hoàn lại 0.9597
  [PASS] Fig. 1: 4 đường LS in trong bảng khớp tính lại (±0.01) — [(1.482, 0.158), (1.247, 0.133), (0.962, 0.137), (1.51, 0.06)]
  [PASS] Fig. 1: duyệt 21 cặp, tập đồng thuận lớn nhất (dung sai 0.8) = 6 điểm đúng — max=6
[2] RANSAC + cv2.solveP3P, N=100 tương ứng, nhiễu inlier sigma=1 px, ngoại lai >=10 px
  dung sai theo §II-A: mean=3.98px, sd=4.44px -> tau = mean+2sd = 12.85 px
  tỉ lệ inlier (của mô hình dựng từ mẫu sạch) rơi trong tau: 0.957  (w hiệu dụng < w danh nghĩa)
   eps    w   1/w^3 1/p_hyp         T_sạch T_đồng thuận>=.8wN  k99 P(T_s<=k99) P(T_c<=k99)  y_hat maxC_sai P(C>=8|bẩn) sai@t=8
   0.1  0.9    1.37    1.38   1.39± 0.74      1.58±  0.93      4       0.993       0.980  0.006       10      0.0348    3/150
   0.3  0.7    2.92    2.95   2.91± 2.25      3.30±  3.00     11       0.993       0.973  0.005       44      0.0172    9/150
   0.5  0.5    8.00    8.25   9.41± 8.48     10.68±  9.30     35       0.987       0.973  0.002       27      0.0044    9/150
   0.6  0.4   15.62   16.37  13.72±12.24     17.24± 17.57     70       1.000       0.987  0.002       20      0.0027    8/150
   0.7  0.3   37.04   39.83  40.50±38.86     44.45± 40.94    169       0.993       0.993  0.001       21      0.0020   18/150
  [PASS] eps=0.1 … 0.7: số lần tới mẫu sạch đầu tiên khớp 1/p_hyp trong 4 SE   (7 dòng PASS)
  cv2.solvePnPRansac(flags=P3P, reprojectionError=tau, confidence=0.99, iterationsCount=10000):
    eps=0.1/0.3/0.5/0.7: thành công (sai số quay < 1°) 100/100 mỗi mức
[3] Số nghiệm của bài toán định vị (§III-A, Phụ lục A)
  [PASS] Fig. 5: hệ số quartic = [-0.5625, 3.515625, -5.90625, 3.515625, -0.5625]
    nghiệm quartic: [0.25 1.   1.   4.  ]
  [PASS] Fig. 5: đúng 4 nghiệm {(4,4,4),(1,4,4),(4,1,4),(4,4,1)}
    cv2.solveP3P[P3P] trên cấu hình Fig. 5: trả 4 nghiệm, hợp lệ (tái chiếu < 1e-6 px) 2: [(4.0, 1.0, 4.0), (4.0, 4.0, 4.0)]
    cv2.solveP3P[AP3P] trên cấu hình Fig. 5: trả 4 nghiệm, hợp lệ (tái chiếu < 1e-6 px) 2: [(4.0, 4.0, 1.0), (4.0, 4.0, 4.0)]
  (A19)–(A23) trên 3000 cấu hình ngẫu nhiên: |G(x_thật)| tương đối: trung vị 8.3e-17, max 3.3e-13
  [PASS] hệ số (A19)–(A23) như bản in: x=b/a thật là nghiệm (sai số tương đối < 1e-8)
    histogram số nghiệm thực dương (0..4) — theo (A18)–(A28): [0, 142, 2624, 13, 221] ; cv2 P3P: [0, 142, 2624, 13, 221]
  [PASS] Fig. 6: hai tâm chiếu khác nhau nhìn A,B,C,D dưới cùng mọi góc cặp -> P4P 2 nghiệm
  [PASS] Fig. 6: P3P + kiểm điểm thứ 4 cho đúng 2 tư thế
  Fig. 7: … số tư thế khớp cả 5 điểm = 2
    min |det| của mọi bộ 4 điểm (đồng phẳng nếu = 0): 2400.000; A, D, E, L, P cùng nằm trên mặt x=0
  4 điểm ngẫu nhiên, 2000 lần: số tư thế khớp (0..4) — đồng phẳng [0, 2000, 0, 0, 0] ; không đồng phẳng [0, 2000, 0, 0, 0]
  P6P ngẫu nhiên, 200 lần: hạng ma trận DLT 12x12 = [11]
    6 điểm + tâm chiếu trên cùng một twisted cubic: độ sâu > 0: True; hai giá trị kỳ dị nhỏ nhất / lớn nhất = 6.9e-18, 2.2e-18
  [PASS] cấu hình tới hạn (twisted cubic qua tâm chiếu): DLT mất hạng (<= 10) -> P6P KHÔNG duy nhất
TỔNG: 47/47 PASS; thời gian 33.3s
```

Diễn giải (mọi câu dưới đây là [M], rút từ đầu ra trên):

- **E(k), E(k²), SD(k) đúng.** Tổng chuỗi số khớp 1/b, (2 − b)/b², √(1 − b)/b tới 10⁻⁶; Monte-Carlo có hoàn lại khớp w⁻ⁿ. Tự suy dẫn (cửa (a)): số lần thử tới mẫu sạch đầu tiên là biến hình học với xác suất thành công b, nên E = 1/b, Var = (1 − b)/b² — đúng như bài.
- **Hai lỗi in nhỏ ở §II-B.** Công thức xấp xỉ "k ≈ log(1 − z)E(k)" [tr. 4] thiếu dấu trừ: log(1 − z) < 0; hệ số 2,3 và 3,0 mà bài nêu chỉ ra được khi dùng −ln(1 − z) (log tự nhiên). Trong bảng E(k), ô w = 0,8, n = 5 in 3.0 trong khi 0,8⁻⁵ = 3,052 (làm tròn thông thường ra 3.1); 43 ô còn lại khớp.
- **k = log(1 − z)/log(1 − wⁿ) đúng khi N lớn, đánh giá thấp khi N nhỏ.** Với N = 1000, tỉ lệ lần chạy có mẫu sạch trong k lần là 0,901/0,951/0,991 cho z = 0,90/0,95/0,99. Với N = 20 và rút không hoàn lại, chỉ 0,796/0,877/0,960.
- **Đường ống P3P + RANSAC** (100 tương ứng, σ = 1 px, 150 lần chạy mỗi mức ngoại lai): số lần thử tới mẫu sạch đầu tiên khớp 1/p_hypergeo ở mọi mức 10–70 %, trong 4 sai số chuẩn. Số lần tới khi đạt đồng thuận ≥ 0,8·wN luôn lớn hơn (44,5 so với 40,5 ở 70 % ngoại lai), vì chỉ 95,7 % inlier rơi trong dung sai của một mô hình dựng từ mẫu sạch có nhiễu. `cv2.solvePnPRansac` với confidence 0,99 thành công 100/100 ở mọi mức thử.
- **Quy tắc dung sai §II-A cho ngưỡng lớn.** Trung bình + 2 SD của sai số tái chiếu từ mô hình 3 điểm là 12,85 px khi σ = 1 px, vì phân bố này có đuôi dài. Ngưỡng đó lớn hơn khoảng cách tối thiểu 10 px của ngoại lai, tức là một số ngoại lai sẽ bị tính là inlier.
- **Ngưỡng t − n = 5 chỉ bảo đảm cho từng mô hình, không bảo đảm cho cả lần chạy.** Xác suất để một mô hình dựng từ mẫu *bẩn* đạt ≥ 8 điểm đồng thuận là 0,2–3,5 % — phù hợp với lập luận y^(t−n) < 5 % của bài. Nhưng vì RANSAC thử nhiều mô hình, nếu dừng ở mô hình *đầu tiên* đạt t = 8 thì 3–18 trên 150 lần chạy (2–12 %) chấp nhận một mô hình sai, tăng theo tỉ lệ ngoại lai. Mô hình sai tốt nhất gom được tới 44 điểm (ở 30 % ngoại lai), nên giả thiết "y nhỏ và như nhau cho mọi điểm" không đứng vững. Thuật toán §IV-A dùng t "giữa 7 và mw", nên trên thực tế bài đặt t gần mw hơn.
- **P3P: khẳng định của bài đứng vững.** Hệ số (A19)–(A23) **như bản in** là đúng: trên 3000 cấu hình ngẫu nhiên, x = b/a thật luôn là nghiệm, sai số tương đối lớn nhất 3,3·10⁻¹³. Ví dụ Fig. 5 cho lại đúng hệ số [−0.5625, 3.515625, −5.90625, 3.515625, −0.5625], nghiệm {1, 1, 4, 0,25} và bốn bộ chân. Không cấu hình nào có hơn 4 nghiệm dương. Phân bố số nghiệm dương trên 3000 cấu hình ngẫu nhiên: 1 nghiệm 142, 2 nghiệm 2624, 3 nghiệm 13, 4 nghiệm 221.
- **Phát hiện phụ về OpenCV 5.0.0.** Ở cấu hình đối xứng Fig. 5 (nghiệm kép x = 1), cả `SOLVEPNP_P3P` lẫn `SOLVEPNP_AP3P` đều chỉ trả về 2 trong 4 nghiệm hợp lệ: P3P trả thêm 2 nghiệm NaN, AP3P trả thêm 2 nghiệm sai. Bộ giải theo (A18)–(A28) của bài tìm đủ 4, nhưng chỉ sau khi tôi thêm vài bước Newton trên (A1)–(A3) để khử sai số làm tròn của nghiệm kép. Không có bước đó, cách cài đặt thẳng của tôi đánh rơi nghiệm ở một số cấu hình gần suy biến.
- **P4P / P5P.** Toạ độ Fig. 6 nhất quán: cùng một phép quay quanh BC đưa A → A′ và D → D′, cos góc quay = 119/169. Một tâm chiếu thứ hai (0; 16,90; 11,76) nhìn A, B, C, D dưới đúng mọi góc cặp, nên P4P ở đây có 2 nghiệm. Fig. 7 dựng lại theo mô tả (E là ảnh đối xứng của A′ qua đường LP) cũng cho đúng 2 tư thế khớp cả 5 điểm, và không có 4 trong 5 điểm nào đồng phẳng. Tuy vậy, A, D, E cùng L và P đều nằm trên mặt x = 0: ví dụ rất đối xứng, "general position" chỉ theo nghĩa hẹp là không có 4 điểm đồng phẳng.
- **4 điểm.** Trên 2000 cấu hình ngẫu nhiên, 4 điểm đồng phẳng luôn cho đúng 1 tư thế khớp (đúng như Phụ lục B khẳng định), và 4 điểm không đồng phẳng *ngẫu nhiên* cũng luôn cho 1. Ví dụ 2 nghiệm của bài là cấu hình đặc biệt, có độ đo không.
- **P6P: khẳng định "luôn duy nhất" không đúng như phát biểu.** Với 6 điểm ngẫu nhiên, ma trận DLT 12×12 luôn có hạng 11, tức nghiệm duy nhất. Nhưng khi 6 điểm và tâm chiếu cùng nằm trên một twisted cubic — một cấu hình mà không 4 điểm nào đồng phẳng — ma trận mất hạng (hai giá trị kỳ dị nhỏ nhất cỡ 10⁻¹⁸ so với lớn nhất), nên ma trận chiếu không duy nhất. Đây là tập nguy hiểm kinh điển của resectioning mà `hartley2004` trình bày (tôi nhớ là ở chương về cấu hình tới hạn, chưa mở sách để lấy số mục). Bài không nhắc tới nó.

## 8. Chỗ tôi không tin

- **"P6P luôn có nghiệm duy nhất khi 6 điểm ở vị trí tổng quát"** [tr. 8–9]. Lập luận chỉ đếm phương trình (18 phương trình, 18 ẩn, "tối đa 17 độc lập") mà không chứng minh ma trận có đủ hạng. Mục 7 cho thấy có cấu hình với không 4 điểm nào đồng phẳng mà DLT vẫn suy biến. Nếu "vị trí tổng quát" được hiểu là "tránh mọi tập có độ đo không" thì khẳng định đúng nhưng hiển nhiên. Còn nếu hiểu là "không có 4 điểm đồng phẳng" như chính bài dùng ở P5P [tr. 8] thì khẳng định sai. Bước "dựng điểm tổng hợp đồng phẳng rồi dùng Phụ lục B" cũng thừa: khi đã có T và K thì tách thẳng R, t được (tôi suy ra).
- **Tuyên bố ưu tiên** "tài liệu trắc địa ảnh không có lời giải giải tích nào khác" và "chắc chắn không ai biết P3P có nhiều nghiệm thực" [§V, tr. 10]. Theo ghi chú entry `haralick1994review` trong `refs.bib`, lời giải P3P đã có từ Grunert 1841. Tôi chưa đọc `haralick1994review` nên chưa khẳng định được văn liệu cũ đã biết tới tính đa nghiệm hay chưa.
- **Ngưỡng t − n = 5 "cho xác suất tốt hơn 95 %"** [§II-C, tr. 4]. Đúng cho một mô hình với y < 0,5 cố định, nhưng RANSAC thử hàng chục tới hàng trăm mô hình, và y thay đổi mạnh theo điểm. Mục 7: dừng ở mô hình đầu tiên đạt t = 8 thì 2–12 % lần chạy nhận mô hình sai.
- **Tab. I "tiêu biểu"** [tr. 10]: 10 trên 50 bài, không nói chọn thế nào. Ở 6 trên 10 dòng, tập đồng thuận cuối nhỏ hơn số tương ứng đúng (ví dụ 22 → 19, 21 → 18). Như vậy RANSAC bỏ sót inlier dù có lần khớp thứ hai; bài chỉ tuyên bố "không có điểm sai nào lọt vào" [§IV-D], nhưng người đọc dễ hiểu nhầm với câu "tập đồng thuận cuối có mọi tương ứng đúng" của thí nghiệm §IV-C. Số bộ ba đã thử (trung bình 2,6 ở w = 0,8 và 7,2 ở w = 0,6) lớn hơn E(k) = 1,95 và 4,6 theo w danh nghĩa. Điều này phù hợp với việc w thực tế thấp hơn (19/30 chẳng hạn) và với nhận xét ở mục 2 (đếm tới đồng thuận chứ không tới mẫu sạch), nhưng 5 mẫu thì không kiểm được gì (tôi suy ra).
- **Độ lệch chuẩn ở thí nghiệm ảnh thật** [§IV-E, tr. 10]: X 0,1 ft nhưng Y 6,4 ft — lệch nhau 60 lần mà không giải thích, không có ground truth, không nói cách tính. Tôi không dùng các con số này làm bằng chứng độ chính xác.
- **P2P "anywhere on a circle"** [§III-A, tr. 6]: chỉ một cung của đường tròn nhìn AB dưới góc θ_ab, cung kia nhìn dưới góc π − θ_ab (tôi suy ra từ định lý góc nội tiếp, không chạy code). Lỗi diễn đạt, không ảnh hưởng tới kết luận "vô số nghiệm".
- **Dấu và cơ số log** ở xấp xỉ k ≈ log(1 − z)E(k) [tr. 4]: thiếu dấu trừ, và phải là log tự nhiên (mục 7). Công thức chính k = log(1 − z)/log(1 − b) thì đúng với mọi cơ số.

## 9. Chỗ tôi chưa hiểu (→ `99-chua-biet.md`)

- Giả thiết "camera ở ngoài và phía trên bao lồi các điểm mốc" [§III, tr. 5] được dùng ở đâu? Nó có loại được nghiệm P3P nào trong ví dụ Fig. 5 không? Bài không chỉ ra. Tôi tính lại bằng tay (trilateration, không nằm trong script): với hướng tia cố định, bốn tâm chiếu của Fig. 5 đều ở phía trên mặt đáy, ở độ cao 3,46 (nghiệm đối xứng) và 0,87 (ba nghiệm còn lại, nằm ngoài lăng trụ đứng trên tam giác đáy) — nên giả thiết này, nếu hiểu theo nghĩa "ở trên mặt đáy", không loại được nghiệm nào ở đây.
- Bước (4) của RANSAC/LD [§IV-A, tr. 9] dựng elip sai số trong ảnh cho từng điểm mốc từ sai số ước lượng của CP, theo kỹ thuật của tài liệu [1] (SRI road expert, 1978). Tôi không có tài liệu đó nên không biết elip được lan truyền ra sao: có dùng Jacobian không, hay chỉ nhiễu hữu hạn? Đây là tiền thân của ngưỡng theo từng điểm (như MLPnP/`urban2016mlpnp` dùng covariance), nhưng tôi chưa kiểm được.
- Bài nói Phụ lục B "luôn" cho nghiệm duy nhất với 4 điểm đồng phẳng, và mục 7 xác nhận khi dữ liệu không nhiễu. Nhưng với nhiễu, trường hợp đồng phẳng nổi tiếng là có hai cực tiểu gần nhau (`collins2014ippe`, `schweighofer2006planar`). Khẳng định "duy nhất" của bài chỉ đúng cho dữ liệu chính xác. Khoảng cách nào giữa camera và mặt phẳng thì nghiệm thứ hai trở nên đáng kể? Bài này không trả lời được.
- Số nghiệm tối đa của P4P và P5P không đồng phẳng: bài để mở [§V, tr. 11]; `wu2006pnp` trong `refs.bib` được ghi là phân tích số nghiệm P4P/P5P, tôi chưa đọc.
- Vì sao cả hai bộ giải P3P của OpenCV 5.0.0 đánh rơi 2 nghiệm ở cấu hình nghiệm kép Fig. 5 (mục 7)? Đây là lỗi cài đặt hay giới hạn chung của cách xử lý nghiệm kép? Nó có ảnh hưởng thực tế gần các cấu hình suy biến (danger cylinder) không?

## 10. Quan hệ với các bài khác trong `refs.bib`

- **Họ RANSAC:** `chum2003lo` (LO-RANSAC) chữa đúng chỗ mục 7 chỉ ra: mô hình từ mẫu sạch có nhiễu không gom đủ inlier, nên cần tối ưu cục bộ (tôi suy ra từ tên và ghi chú; chưa đọc). `raguram2013usac`, `barath2018gcransac`, `barath2020magsacpp`, `barath2022sprt` thay ngưỡng cứng và quy tắc dừng của bài này; chưa đọc. Ý "chọn mẫu có định hướng thay cho ngẫu nhiên nếu có lý do" [§II, tr. 3] là mầm của các biến thể chọn mẫu có hướng dẫn về sau (tôi suy ra).
- **P3P:** `haralick1994review` tổng kết các lời giải P3P từ Grunert, trong đó có lời giải của bài này (theo ghi chú entry). `gao2003p3p` phân loại đầy đủ số nghiệm thực, tức là trả lời trọn câu hỏi mà bài này chỉ chặn trên bằng 4. `wolfe1991perspective` bàn hình học của số nghiệm P3P. `kneip2011p3p`, `persson2018lambdatwist`, `ding2023p3p` là các bộ giải nhanh và ổn định hơn. Mục 7 cho thấy lời giải quartic của bài đúng về đại số nhưng cài đặt thẳng thì nhạy với nghiệm kép — cùng loại vấn đề ổn định số mà các bài sau nhắm tới (tôi suy ra, chưa đọc các bài đó).
- **P4P/P5P/P6P:** `wu2006pnp` (số nghiệm P4P, P5P) tiếp tục câu hỏi bài này để mở. `hartley2004` cho DLT và cấu hình tới hạn của resectioning — bổ sung cho lập luận P6P thiếu sót của bài.
- **Phẳng:** Phụ lục B là lời giải homography sơ khai cho target phẳng; `collins2014ippe` và `schweighofer2006planar` xử lý tính lưỡng nghĩa khi có nhiễu mà bài này không thấy.
- **Thư viện:** `opencvsolvepnp` — `solvePnPRansac` là hậu duệ trực tiếp. Tôi đo được `cv2.solvePnPRansac(..., flags=SOLVEPNP_P3P)` báo lỗi khi có ít hơn 4 điểm (assert `npoints >= 4` trong OpenCV 5.0.0), nên có thể nó dùng mẫu 4 điểm (P3P + 1 điểm để chọn nghiệm) chứ không phải 3. Tôi chưa đọc mã nguồn để khẳng định.

## 11. Nó đổi gì trong suy nghĩ

[M] Trước khi đọc, tôi coi công thức k = log(1 − p)/log(1 − wⁿ) là "định lý" của RANSAC. Sau khi đọc và chạy mục 7, tôi thấy nó chỉ đếm tới *mẫu sạch đầu tiên* dưới giả thiết rút có hoàn lại. Hai điều nó bỏ qua — N hữu hạn, và nhiễu làm mẫu sạch không cho mô hình đủ tốt — đều đẩy số lần thử thật lên. Cơ chế dừng bằng ngưỡng t cứng cũng yếu hơn tôi tưởng: bảo đảm "95 %" là cho từng mô hình, không phải cho cả lần chạy.

Về PnP, bài làm tôi đổi cách nhìn "4 nghiệm của P3P". Đó không phải chi tiết kỹ thuật cần chịu đựng, mà là lý do RANSAC cho LDP phải xét *mọi* nghiệm như những giả thuyết riêng [§IV-A bước 2, tr. 9]. Nó cũng là lý do bài phê phán các phương pháp lặp: vì các nghiệm có thể gần nhau tuỳ ý, khởi tạo gần nghiệm đúng vẫn không chắc hội tụ về nghiệm đúng [§V, tr. 10]. Tôi cũng đổi đánh giá về độ tin các bộ giải thư viện: ở cấu hình nghiệm kép, OpenCV 5.0.0 bỏ sót nghiệm.

## 12. Câu hỏi tự kiểm

1. Vì sao E(k) = w⁻ⁿ đánh giá thấp số lần thử thực tế khi N nhỏ, và khi mô hình tối thiểu dựng từ dữ liệu có nhiễu? Hai hiệu ứng này có cùng hướng không?
2. Lập luận "(a, b, c) là nghiệm thì (−a, −b, −c) cũng là nghiệm, nên tối đa 4 nghiệm dương" dựa vào tính chất nào của hệ [A*]? Nó hỏng thế nào nếu thay tia đơn vị bằng camera có méo xuyên tâm chưa biết?
3. Khi nào t − n = 5 *không* đủ để tránh chấp nhận mô hình sai? Hãy nêu một cơ chế làm y của một mô hình sai lớn hơn nhiều so với trung bình.
4. Vì sao 4 điểm đồng phẳng cho nghiệm duy nhất khi dữ liệu chính xác, còn 4 điểm không đồng phẳng thì có thể không? Và vì sao với dữ liệu nhiễu thì trực giác này gần như đảo ngược (target phẳng lại là trường hợp lưỡng nghĩa)?
5. Lập luận P6P qua DLT hỏng ở cấu hình nào, và tại sao đếm "số phương trình = số ẩn" không bao giờ đủ để chứng minh nghiệm duy nhất?

## Trích đoạn nguyên văn làm bằng chứng

- "Classification errors, however, are gross errors, having a significantly larger effect than measurement errors, and do not average out." [tr. 3]
- "RANSAC uses as small an initial data set as feasible and enlarges this set with consistent data when possible." [tr. 3]
- "it is certainly reasonable to assume that it is less than w" [tr. 4]
- "Finally, we assume that the camera resides outside and above a convex hull enclosing the control points." [tr. 5]
- "for every real positive solution there is a geometrically isomorphic negative solution" [tr. 6]
- "Surprisingly, when all four control points do not lie in the same plane, a unique solution cannot always be assured" [tr. 6]
- "even when an iterative technique is initialized to a value close to the correct solution there is no assurance that it will converge to the desired value." [tr. 10]
- "The issue of determining the maximum number of solutions possible for the P4P and P5P problems remains open" [tr. 11]
