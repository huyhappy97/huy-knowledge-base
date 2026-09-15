# Sổ những điều chưa biết — cây VSLAM

Theo tinh thần quyển *"Notebook of things I don't know about"* mà Feynman mở khi làm
nghiên cứu sinh ở Princeton. Mỗi mục là một **câu hỏi cụ thể** mà tôi biết là mình chưa
trả lời được, không phải một chủ đề chung chung.

Sổ này chỉ có giá trị khi được **thu ngắn dần**: mục nào giải quyết xong thì chuyển thành
một đoạn trong bài chính và ghi ngày ở đây.

Ngày lập: 2026-09-13. Lần rà gần nhất: 2026-09-13.

---

## 0. Nợ kiểm chứng (ưu tiên cao nhất, trên mọi câu hỏi nội dung)

**Toàn bộ `refs.bib` chưa được đối chiếu với nguồn gốc.** Các entry được soạn từ trí nhớ
về công trình: tên tác giả, năm và venue đủ chính xác để tra cứu, nhưng chưa mở trang
nhà xuất bản hay arXiv để kiểm. Theo `learning-rules.md` mục 5, như vậy là chưa qua cửa
kiểm chứng nào.

Ưu tiên đối chiếu, theo mức cây dựa vào chúng:
`hartley2004`, `triggs2000ba`, `barfoot2017` (nền của cả Phần A);
`civera2008inversedepth` (lập luận nghịch đảo độ sâu, dùng ở A/06, B/08, C/16);
`strasdat2010scaledrift` (Sim(3) loop closure);
`mourikis2007msckf` (structureless);
`sattler2019understanding` (kết luận về APR — đây là một khẳng định mạnh, phải kiểm);
`zhang2018gaugeba` (so sánh ba cách xử lý gauge);
`pittaluga2019revealing` (map inversion — khẳng định về quyền riêng tư, phải kiểm).

Mỗi entry sau khi đối chiếu cần được dán lại mức tin A/B/C **sau khi** đã đọc được ít nhất
abstract gốc. Mức tin hiện tại trong `refs.bib` là phán đoán chưa đối chiếu.

**Chưa có bài nền tảng nào được đọc tới lượt ba** theo phương pháp Keshav. Ít nhất
`triggs2000ba` và một trong hai `hartley2004` / `barfoot2017` phải qua lượt ba trước khi
coi Phần A là hoàn chỉnh.

**Chưa có thư mục `code/` nào.** Mọi công thức lõi được đánh dấu "cửa (b) — kiểm bằng ví
dụ số" trong header các chương đều là **tính tay**, chưa có script chạy được. Ưu tiên:
Jacobian ở A/03 (đã có mini project, chỉ cần viết ra), phần bù Schur ở A/04, và quan hệ
sigma_z ở A/06.

---

## 1. Câu hỏi về nguyên lý và toán học

**Ngưỡng góc nhỏ cho công thức Rodrigues.** Công thức có kỳ dị 0/0 khi góc tiến về không,
và mọi thư viện chuyển sang Taylor dưới một ngưỡng. Ngưỡng ấy đặt ở đâu thì đúng, và sai
số số học ở lân cận ngưỡng lớn cỡ nào? (A/03 mục 2B nêu vấn đề, không trả lời. Mini project
A/03 có thể đo được con số này.)

**Nhiễu loạn trái và phải có bao giờ cho hai cực tiểu khác nhau?** Với bài toán trơn và
bước nhỏ thì không. Nhưng với LM và damping mạnh trên bài toán không lồi, hai quy ước có
thể đi hai đường khác nhau và rơi vào hai cực tiểu địa phương khác nhau. Tôi chưa kiểm và
chưa tìm được nguồn khẳng định. (A/03 mục 7.)

**Điểm chính sai và yaw sai có tách được không?** A/02 mục 4C nói lệch điểm chính Δcx
tương đương xấp xỉ một yaw Δcx/f. Nhưng tôi ngờ chúng tách được **một phần** khi chuyển
động đủ đa dạng, vì lệch điểm chính gắn với vị trí trong ảnh còn yaw thì không. Làm rõ
điều này cần một phân tích observability cụ thể.

**Ngưỡng parallax tính từ σ — công thức có đủ chặt không?** B/10 mục 2C dẫn
α ≥ σ_px/(f·ε) từ hình học tam giác nhỏ. Nó bỏ qua ảnh hưởng của **số lượng quan sát**
(nhiều quan sát bù được parallax nhỏ tới mức nào?) và bỏ qua phân bố lệch ở A/06. Một
công thức đúng hơn nên tính từ ma trận thông tin đầy đủ.

**Chứng minh phần topology của SO(3).** A/03 mục 7 khẳng định mọi tham số hoá ba số đều
có kỳ dị, đối chiếu với hai nguồn nhưng **không tự chứng minh được**. Đây là một khoản nợ
suy dẫn.

---

## 2. Câu hỏi về observability và bất định

**Thành phần song song trục quay của p_cam^imu: có quan sát được yếu không?**
C/14 mục 6 nêu rằng ngoài ω×p còn có các số hạng ω×(ω×p) và ω̇×p trong biểu thức gia tốc.
Số hạng thứ hai đưa vào một cơ chế quan sát khác nếu **tốc độ góc thay đổi**. Phát biểu
chặt hơn phải là: với ω hằng quanh một trục thì không quan sát được; với ω biến thiên thì
có thể quan sát được yếu. Tôi chưa kiểm bằng số. **Mini project C/14 đo được điều này** —
chỉ cần thêm một quỹ đạo xoay quanh một trục với tốc độ góc biến thiên.

**SLAM hiện đại quá tự tin tới mức nào?** Bệnh này được thiết lập cho EKF-SLAM
(`huang2008fej`, `hesch2014consistency`). Với các hệ tối ưu hoá hiện đại, tôi **suy ra**
từ bốn cơ chế ở A/06 mục 4B rằng bệnh vẫn còn, nhưng không có số liệu về mức độ. Một
khảo sát ANEES trên nhiều hệ và nhiều bộ dữ liệu là một thí nghiệm đáng làm mà tôi không
biết ai đã làm. (Đây cũng là phép kiểm cho hướng 2 ở D/22.)

**Ngưỡng định lượng cho GNC.** B/11 mục 6 nêu rằng back-end bền cần cạnh sai là thiểu số,
nhưng **bao nhiêu phần trăm thì sụp?** Con số phụ thuộc mạnh vào cấu trúc đồ thị. Mini
project B/11 phần ba đo được điều này.

**Marginalization trong cửa sổ trượt tối ưu hoá gây bất nhất tới mức nào?** A/04 mục 7 nêu
rằng vấn đề có thể nhẹ hơn trong bộ lọc vì các biến vẫn được tái tuyến tính hoá trong cửa
sổ, nhưng không có số liệu.

---

## 3. Câu hỏi về phương pháp và triển khai

**Vòng lặp nhiệt → trôi ống kính → trôi hiệu chuẩn có thật không?**
D/20 mục 5 nêu vòng lặp này và ghi rõ rằng **tôi suy ra từ A/02 mục 4C và C/14 mục 4B,
không có số liệu đo và không dẫn được nguồn nào đã đo nó một cách hệ thống**. Đây là
mệnh đề có rủi ro sai cao nhất trong chương đó.

**Phép kiểm rẻ và ưu tiên cao**: ghi nhiệt độ vỏ máy và tham số hiệu chuẩn trực tuyến trên
một thiết bị thật trong vài giờ, xem chúng có tương quan không. Nếu không, phải rút mệnh đề.

**Direct suy giảm nặng hơn indirect với vật động — đúng bao nhiêu?**
D/19 mục 2C suy từ lập luận về tương quan của outlier. Kiểm được bằng cách chạy cả hai họ
trên cùng chuỗi có vật động chiếm các tỉ lệ diện tích khác nhau và vẽ đường cong suy giảm.
Chưa chạy.

**Số inlier có thật sự không tương quan với sai số tư thế không?**
A/01 khối Cạm bẫy và B/10 mục 5 đều khẳng định điều này. Nó dễ kiểm và chưa kiểm: trên một
tập đủ lớn các cặp khung gồm cả cấu hình suy biến, đo tương quan giữa số inlier và sai số
tư thế thật, so với tương quan của parallax trung vị.

**Dạng căn bậc hai có đáng không với bài toán số điều kiện nhỏ?**
B/09 mục 7 nêu rằng lợi ích có thể không đo được khi số điều kiện nhỏ. Chưa đo ngưỡng.

**Tốc độ lão hoá của bản đồ trong môi trường thật.**
Mini project C/13 đề nghị đo tỉ lệ landmark từ phiên đầu còn sống sau nhiều phiên. Tôi
không biết ai đã công bố con số này cho một môi trường thật, và nó là một con số có giá trị.

---

## 4. Câu hỏi về học máy trong SLAM

**Bất định học được có thật sự là chỗ trống không?**
C/17 mục 4A khẳng định số công trình về bất định học được ít hơn nhiều so với về front-end
học được, và ghi rõ rằng **đây là ấn tượng từ việc đọc rải rác, không phải kết quả khảo
sát**. Đây là mục có rủi ro sai cao nhất trong chương 17. Làm khảo sát cho nó là việc cần
làm trước khi dùng D/22 hướng 2 và hướng 5 để chọn đề tài.

**Mạng nơ-ron không được hiệu chuẩn — mức độ nghiêm trọng trong SLAM?**
Đây là kết quả đã biết rộng rãi trong cộng đồng học máy, nhưng tôi **không dẫn được nguồn
cụ thể trong ngữ cảnh SLAM**, và không biết mức độ cho các mô hình độ sâu và luồng quang
cụ thể đang dùng.

**Kết luận về APR còn đúng sau 2019 không?**
B/12 mục 3B dựa vào `sattler2019understanding`. Tôi chưa khảo sát tài liệu sau đó về điểm
này, và các kiến trúc mới có thể đã thay đổi kết luận.

---

## 5. Câu hỏi nối sang nhánh khác

**Đối chiếu với `../IMU_Fusion/`.** Cây đó có một dự án thực nghiệm thật
(`../imu_initialization/`) trên một chuỗi EuRoC. Những con số đó nói gì về B/10 mục 3B của
cây này, và có chỗ nào hai cây phát biểu khác nhau không? Có dữ liệu thật trong tay mà chưa
đối chiếu với bài tổng quan là một dạng tự lừa mình rẻ tiền và dễ tránh.

**Đối chiếu với `../marker/`.** Cây đó làm ngân sách sai số pixel→pose ở mức milimet. Các
quan hệ ở A/06 mục 3 của cây này có nhất quán với ngân sách ở đó không? Nếu hai cây cho hai
con số khác nhau cho cùng một đại lượng thì ít nhất một cây sai.

**Marker như lời giải cho perceptual aliasing.** B/11 mục 6C nói rằng công nghiệp giải bài
toán môi trường lặp lại bằng cách dán marker. Cây `../marker/` cho cái giá của giải pháp ấy.
Ghép hai phía lại thành một phân tích đánh đổi đầy đủ là một việc chưa làm.

---

## 6. Khoản nợ về phương pháp (mức cây, không phải mức chương)

**Chương D/22 chưa đạt chuẩn `research-rules.md`** và nó nói rõ điều đó ngay từ đầu. Trước
khi dùng nó để chọn đề tài thật, hướng đã chọn phải được nâng lên thành một dự án `survey/`
đúng chuẩn: bước 0 (khung câu hỏi) tới bước 4 (ma trận tổng hợp).

**Cả cây chưa có con số thực nghiệm nào do tôi đo.** Đây là có chủ ý và được ghi rõ ở
`00-map.tex`, nhưng nó nghĩa là mọi khẳng định định lượng trong cây hoặc là dẫn nguồn, hoặc
là tính tay từ ví dụ tự đặt, hoặc được đánh dấu "(tôi suy ra, chưa đối chiếu nguồn)". Danh
sách các mệnh đề thuộc loại thứ ba nằm rải trong các mục "Điều gì chứng minh cách hiểu này
sai" của từng chương; gom chúng lại thành một danh sách duy nhất là một việc nên làm.

**Phần hết hạn nhanh**: C/16 mục 4 (NeRF và 3DGS), C/17 (toàn chương), E/23 (toàn chương).
Cả ba chốt tại 9/2026. **Rà lại 3/2027.**
