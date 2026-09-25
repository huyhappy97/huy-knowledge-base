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
2. EPnP cực tiểu hoá một sai số **đại số**. Trên dữ liệu có nhiễu pixel đẳng hướng, sai số đó
   lệch khỏi sai số tái chiếu bao nhiêu, và sau một bước LM thì chênh lệch còn lại có đáng kể không?
3. SQPnP tuyên bố "tối ưu toàn cục" — tối ưu theo hàm nào (sai số trong không gian vật?), và hàm
   đó trùng với nghiệm hợp lý cực đại dưới nhiễu pixel Gauss khi nào?
4. CPnP tuyên bố nhất quán (consistent) khi n → ∞. EPnP và SQPnP có **không** nhất quán không,
   và độ chệch của chúng lớn cỡ nào ở n = 50 — điều đó có quan trọng cho relocalization không?
5. Với target phẳng, vì sao hàm mục tiêu có đúng hai cực tiểu mà không phải nhiều hơn? (Trỏ sang
   `../../marker/A-nguyen-ly-va-toan-hoc/04-pose-ambiguity-target-phang/` — kiểm xem ở đó đã trả
   lời chưa trước khi viết lại.)
6. Khi biết trọng lực, P2P có hai nghiệm. Sai số của hướng trọng lực từ IMU (cỡ bao nhiêu độ?)
   lan vào pose thế nào — có lúc nào dùng P3P không cần trọng lực lại tốt hơn?
7. BPnP lấy đạo hàm bằng định lý hàm ẩn tại nghiệm. Khi PnP có nhiều cực tiểu gần nhau, đạo hàm
   đó có còn nghĩa không — và đây có phải lý do EPro-PnP chuyển sang phân bố pose?
8. Trong pipeline RANSAC + LM, bộ giải tối thiểu tốt hơn (Lambda Twist so với Kneip 2011) đổi
   **kết quả cuối** hay chỉ đổi **tốc độ**? Chưa thấy bài nào trả lời trực tiếp — ứng viên cho
   một thí nghiệm trong `code/`.
