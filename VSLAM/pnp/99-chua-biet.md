# Sổ những điều chưa biết — khảo sát PnP

Cùng cơ chế với `../99-chua-biet.md`: mỗi mục là một câu hỏi cụ thể tôi biết mình chưa trả lời
được. Mục nào giải xong thì chuyển thành đoạn trong bài học và ghi ngày ở đây.

Ngày lập: 2026-09-25.

## 0. Nợ đọc (ưu tiên cao nhất)

Toàn bộ `refs.bib` đã kiểm **siêu dữ liệu** nhưng **chưa có bài nào được đọc tới lượt hai**.
Mười bài trong "Lộ trình đọc gợi ý" của `danh-muc.md` là mười ghi chú `notes/<bibkey>.md` đầu tiên
phải viết. Trước khi xong, mọi câu "vì sao đọc" trong danh mục chỉ là gợi ý, không phải hiểu biết.

## 1. Câu hỏi nội dung

1. Vì sao P3P có **tối đa bốn** nghiệm thực, và cấu hình nào (danger cylinder) làm hai nghiệm
   nhập làm một — ở đó bộ giải nào mất ổn định số và mất theo kiểu gì?
   *Tiến triển 2026-09-25 (agent, chưa ký):* đã đo — trên danger cylinder Δ của `ding2023p3p` bằng 0
   như bài nói, nhưng mọi bộ giải (Ding, OpenCV P3P, AP3P) trượt 24–49 % số ca; khi ba điểm gần
   thẳng hàng, sai số của Ding tăng ~1/ε² còn AP3P ~1/ε (`notes/ding2023p3p.md` mục 7). Câu "vì
   sao tối đa bốn" vẫn chưa có chứng minh trong các bài đã đọc — `haralick1994review` chỉ khẳng định.
2. EPnP cực tiểu hoá một sai số **đại số**. Trên dữ liệu có nhiễu pixel đẳng hướng, sai số đó
   lệch khỏi sai số tái chiếu bao nhiêu, và sau một bước LM thì chênh lệch còn lại có đáng kể không?
3. SQPnP tuyên bố "tối ưu toàn cục" — tối ưu theo hàm nào (sai số trong không gian vật?), và hàm
   đó trùng với nghiệm hợp lý cực đại dưới nhiễu pixel Gauss khi nào?
4. CPnP tuyên bố nhất quán (consistent) khi n → ∞. EPnP và SQPnP có **không** nhất quán không,
   và độ chệch của chúng lớn cỡ nào ở n = 50 — điều đó có quan trọng cho relocalization không?
5. Với target phẳng, vì sao hàm mục tiêu có đúng hai cực tiểu mà không phải nhiều hơn? (Trỏ sang
   `../../marker/A-nguyen-ly-va-toan-hoc/04-pose-ambiguity-target-phang/` — kiểm xem ở đó đã trả
   lời chưa trước khi viết lại.)
   *Tiến triển 2026-09-25:* `collins2014ippe` chứng minh hai nghiệm IPPE là ảnh gương **chính xác**
   qua mặt phẳng vuông góc tia nhìn tới trọng tâm (kiểm tới 1e-14); `lu2000orthogonal` chỉ ra
   luôn có thêm một nghiệm song sinh **sau camera** cùng giá trị hàm mục tiêu. Câu "đúng hai cực
   tiểu của sai số tái chiếu" vẫn mở. Ghi chú IPPE mục 10 liệt kê ba chỗ chương marker cần sửa.
6. Khi biết trọng lực, P2P có hai nghiệm. Sai số của hướng trọng lực từ IMU (cỡ bao nhiêu độ?)
   lan vào pose thế nào — có lúc nào dùng P3P không cần trọng lực lại tốt hơn?
7. BPnP lấy đạo hàm bằng định lý hàm ẩn tại nghiệm. Khi PnP có nhiều cực tiểu gần nhau, đạo hàm
   đó có còn nghĩa không — và đây có phải lý do EPro-PnP chuyển sang phân bố pose?
   *Tiến triển 2026-09-25:* đo được — với target phẳng ở xa, dịch ảnh 0,1 px làm nghiệm y* nhảy 40°
   sang nhánh kia, nên ánh xạ X → y* không liên tục và đạo hàm hàm ẩn vô nghĩa ở đó; log Z của
   EPro-PnP vẫn trơn (`notes/chen2022epropnp.md` C5). Nhưng thí nghiệm C4 gợi ý lý do chính khiến
   loss kiểu BPnP học kém là loss không nhạy với thang trọng số, không phải tính khả vi.
8. Trong pipeline RANSAC + LM, bộ giải tối thiểu tốt hơn (Lambda Twist so với Kneip 2011) đổi
   **kết quả cuối** hay chỉ đổi **tốc độ**? Chưa thấy bài nào trả lời trực tiếp — ứng viên cho
   một thí nghiệm trong `code/`.

## 2. Câu hỏi phát sinh khi đọc (2026-09-25, từ `notes/`)

Mỗi câu trỏ về ghi chú sinh ra nó; chi tiết và số liệu nằm ở mục 7–9 của ghi chú đó.

**Thư viện và cài đặt (ảnh hưởng trực tiếp tới code thật)**
- OpenCV 5.0.0 `SOLVEPNP_P3P`/`AP3P` đánh rơi 2/4 nghiệm ở cấu hình nghiệm kép (Fig. 5 của RANSAC 1981) — lỗi này có xảy ra gần danger cylinder trong dữ liệu thật không? (`fischler1981ransac`)
- AP3P trong OpenCV 5.0.0 trả trung bình 2,35 nghiệm, 28 % sai hình học — khác bản mà `ding2023p3p` đo (1,74 và 2,2 %). Phiên bản nào đổi, đổi gì?
- Chi tiết nào trong mã OpenCV/PoseLib (hoán vị để BC dài nhất, ngưỡng −1e-12, dừng theo nghiệm dương) làm P3P bền gấp đôi trên danger cylinder nhưng kém hơn khi điểm gần thẳng hàng? (`ding2023p3p`)
- `cv2.solvePnP` ITERATIVE khởi tạo bằng gì khi n ≥ 6 không đồng phẳng, và vì sao ở ~4 % cảnh nó dừng ở cực tiểu tệ hơn EPnP+GN? (`marchand2016arsurvey`)
- ViSP cập nhật pose bằng `exp(v)⁻¹·cMo` hay dạng khác — vì sao công thức in `exp^{δq} q` ở tr. 5 của survey lại phân kỳ? (`marchand2016arsurvey`)

- EPnP phẳng với ba vector nhân: một vòng tái tuyến tính hoá chỉ có hạng 6/9 — bài (hay mã MATLAB gốc) thực sự giải ca này thế nào? (`lepetit2009epnp`)
- Bước MᵀM của EPnP ngầm trọng số sai số pixel theo z²; với dải độ sâu lớn, chuẩn hoá lại theo độ sâu (như CEPnP, MLPnP) lợi bao nhiêu? (`lepetit2009epnp`)
- `cv2.SOLVEPNP_EPNP` hỏng trên dữ liệu phẳng không nhiễu (nghiệm lật): có phải do `cv::invert(DECOMP_SVD)` cắt mất trục độ dài ≈ 0? OpenCV đã ghi nhận chưa? (`lepetit2009epnp`)

**RANSAC**
- Khi N nhỏ và lấy mẫu không hoàn lại, k = log(1−p)/log(1−wⁿ) đánh giá thấp số vòng (N = 20: đạt 0,96 thay vì 0,99). OpenCV, PoseLib, USAC có hiệu chỉnh hypergeometric không? (`fischler1981ransac`)
- Ngưỡng t − n = 5 chỉ bảo đảm cho từng mô hình; dừng ở mô hình đầu tiên đạt t thì 2–12 % lần chạy nhận mô hình sai. SPRT, MAGSAC++, a-contrario kiểm soát xác suất sai tích luỹ thế nào? (`fischler1981ransac`)
- IRLS-Tukey: thang σ ước lượng bằng MAD quanh trung vị hay quanh 0? MAD quanh trung vị làm mọi trọng số về 0 khi khởi tạo lệch ~3°. (`marchand2016arsurvey`)

**P3P**
- Khi chạy thật (không có oracle), S_wn của Haralick nên tính tại nghiệm nào, và tiêu chí chọn thứ tự thế có còn hiệu quả? (`haralick1994review`)
- Finsterwalder: khi cubic (14) có ba nghiệm thực, chọn λ0 nào ổn định nhất — Lambda Twist có trả lời không? (`haralick1994review`)
- Tỉ lệ P3P có 1/2/3/4 nghiệm dương phụ thuộc trường nhìn thế nào (camera thường 44° → 88 % hai nghiệm; phân bố của Haralick → 66 % một nghiệm)? (`haralick1994review`)
- Phân loại theo dấu Δ ở Bảng 1 của Ding có còn đúng khi cả hai conic là hyperbola? Chuỗi "danger cylinder ⇒ Jacobian suy biến ⇒ nghiệm kép ⇒ conic tiếp xúc ⇒ Δ = 0" có đúng từng mắt xích? (`ding2023p3p`)

**Target phẳng**
- Ngưỡng cho thống kê likelihood-ratio n(e₂² − e₁²)/σ² khi chọn nghiệm IPPE, và ước lượng σ thế nào khi n = 4? (`collins2014ippe`)
- Sau LM, nghiệm thứ hai của IPPE có hội tụ về cực tiểu thứ hai của RPP-SP (`schweighofer2006planar`) không? (`collins2014ippe`)
- Vì sao homography Harker–O'Leary tốt nhất cho IPPE mà DLT lại tốt nhất cho phân rã homography? (`collins2014ippe`)

**Lặp trong không gian vật**
- Các điểm bất động "giả" của orthogonal iteration là cực tiểu địa phương hay có cả điểm yên ngựa? Hệ số co tuyến tính 0,45–0,87 phụ thuộc hình học ra sao, vì sao target phẳng chậm hơn? (`lu2000orthogonal`)
- Bản có trọng số 1/d² (eq. 46) còn là majorize–minimize, còn đơn điệu không khi trọng số đổi theo vòng lặp? (`lu2000orthogonal`)

**Bất định**
- MLPnP+Σ trong thí nghiệm tổng hợp lấy covariance từ đâu, khi eq. (24)–(25) chỉ định nghĩa cho chuỗi khung thật? Dùng Q = AΣAᵀ của khung trước làm nhiễu đo khung sau có cơ sở thống kê nào? (`urban2016mlpnp`)
- Bước GN của MLPnP trong OpenGV có chia phần dư cho λᵢ như eq. (10) không? (`urban2016mlpnp`)
- EPnPU\*/DLSU\* thật sự dùng Σx đầy đủ xoay theo pose (§3.2) hay chỉ lấy độ sâu (§3.3)? Mô phỏng: chỉ độ sâu thì gần như không có lợi, Σx đầy đủ giảm ~40–45 % sai số với nhiễu kiểu stereo. Cần mở mã gốc. (`vakhitov2021uncertainty`)
- Khi điểm 3D tam giác hoá từ cùng keyframe có pose sai (nhiễu 3D tương quan), trọng số eq. (21) có làm covariance pose quá lạc quan? (`vakhitov2021uncertainty`)

**Học sâu**
- EPro-PnP dùng độ đo nào trên SE(3) (Haar hay Lebesgue trên toạ độ exp), và khi hậu nghiệm rộng thì lựa chọn này đổi log Z bao nhiêu? (`chen2022epropnp`)
- Với vật đối xứng, đích Dirac tại một y_gt phạt các pose tương đương — EPro-PnP (hay `chen2025epropnp`) xử lý thế nào? (`chen2022epropnp`)
- Với Huber và ngưỡng thích nghi (eq. 11), ngoại lai có bị đẩy trọng số về 0 không? Thí nghiệm không-Huber cho thấy chỉ giảm tương đối (tỉ số 0,34), không về 0. (`chen2022epropnp`)
