# Sổ những điều chưa biết — cây marker

Theo tinh thần quyển *"Notebook of things I don't know about"* của Feynman
(`learning-rules.md` mục 3). Mỗi mục là một **câu hỏi cụ thể** mà tôi biết là
mình chưa trả lời được, không phải một chủ đề chung chung.

Sổ này chỉ có giá trị khi được **thu ngắn dần**: mục nào giải quyết xong thì
chuyển thành một đoạn trong bài chính và ghi ngày.

Ngày tạo: 2026-09-13 | Sửa gần nhất: 2026-09-14

---

## Nợ kiểm chứng — ưu tiên cao nhất

**1. Phá tính đồng phẳng có thật sự khử ambiguity không, đo bằng đại lượng đúng?**

`C/16` mục 3C đo được rằng kê nghiêng 20° chỉ cải thiện độ tản mát góc **1,24
lần**, trong khi `B/09` mục 4 ngụ ý đòn bẩy lớn hơn nhiều. Ba giả thuyết chưa
phân biệt được: (a) cấu hình đã đủ tốt sẵn nên lợi ích nhỏ lại; (b) lợi ích
thật nằm ở việc **loại lỗi thô** chứ không giảm nhiễu, và tôi đã đo nhầm đại
lượng; (c) độ nghiêng chưa đủ.

Cách giải quyết: mini project của `C/16` — đo **tỉ lệ chọn nhầm nghiệm** thay
vì độ tản mát, và quét độ nghiêng từ 0° tới 45°.

Đây là mục quan trọng nhất của sổ vì nó ảnh hưởng tới một khuyến nghị thiết kế
cơ khí đã được đưa ra ở `B/09`.

**2. Vì sao tag nhô ra theo chiều sâu mạnh hơn nêm nghiêng hai lần?**

`C/16` mục 3E đo được phương án D (tag nhô ra 60 mm) cho pitch 0,064° so với
0,124° của phương án C (nêm nghiêng 20°). Hai giả thuyết: đó là hiệu ứng thật
của độ lệch khỏi mặt phẳng lớn hơn (60 mm so với 26 mm — tỉ số đúng bằng 2, một
sự trùng khớp đáng chú ý), hoặc đó chỉ là hệ quả của việc có thêm một tag thứ
năm với bốn góc nữa.

Phép thử phân biệt: so phương án D với một phương án E gồm năm tag nhưng tất cả
đồng phẳng. `B/09` hiện không nêu kết luận này và tôi chưa có lý thuyết giải
thích nó.

**3. Quan hệ δθ ∝ 1/B có tuyến tính chính xác không?**

`C/16` mục 3D: từ B = 0,1 tới 0,8 m (tám lần), yaw chỉ cải thiện 3,4 lần chứ
không phải 8. Giải thích hiện tại — khi yaw tốt lên thì các trục khác thành ràng
buộc và bài toán hợp nhất phân bổ lại thông tin — là hợp lý nhưng chưa được
kiểm. Cần một mô phỏng tách bạch từng trục với baseline theo **cả hai** phương.

**4. Toàn cây chưa có một phép đo phần cứng nào.**

Mọi con số đã kiểm trong cây đến từ mô phỏng. Theo `C/16` mục 6, mô phỏng
**không** kiểm được: các nguồn sai số bị bỏ sót, và tính đúng của mô hình nhiễu.
Đây là chỗ nợ lớn nhất của toàn bộ cây.

**5. `refs.bib` chưa được đối chiếu với nguồn gốc.**

Soạn từ trí nhớ về công trình gốc; tên tác giả, năm và venue đúng ở mức tra cứu
được nhưng chưa mở trang nhà xuất bản. Theo `learning-rules.md` mục 5, như vậy
là chưa qua cửa kiểm chứng nào. Ưu tiên các công trình mà cây dựa vào nhiều
nhất: `collins2014ippe`, `schweighofer2006robust`, `wang2016apriltag2`,
`heikkila2000geometric`, `tsai1989handeye`, `brockett1983asymptotic`.

---

## Câu hỏi về nguyên lý và toán học

**Điểm chính sai Δ px gây thiên lệch pose bao nhiêu?** `A/01` mục 5 dẫn ra rằng
nó dịch mọi tia nhìn đi Δ/f radian, và với Δ=10 px, f=600 px thì là 0,95°. Nhưng
tôi chưa đo bằng mô phỏng xem bao nhiêu phần của thiên lệch ấy bị hấp thụ vào
các tham số pose khác, và bao nhiêu còn lại ở đầu ra. Đây là dòng lớn nhất của
bảng ngân sách ví dụ ở `C/15`, nên nó đáng kiểm sớm.

**Blur gây thiên lệch hay chỉ tăng phương sai?** `A/06` mục 3 lập luận rằng
profile độ sáng của một ô bị nhoè mất đối xứng nên phép khớp cạnh lệch. Chưa
kiểm. Cách kiểm: mô phỏng một tag, tích phân ảnh qua một đoạn dịch chuyển, chạy
detector, so với chân trị. Nếu blur chỉ gây nhiễu thì lập luận cho stop-and-go
mất một chân (rolling shutter vẫn còn).

**Méo làm cong cạnh khuếch đại sai số góc bao nhiêu?** `A/01` mục 4 dẫn ra cơ
chế ba tầng và có ví dụ số cho độ lớn méo (53 px ở rìa), nhưng phần **khuếch đại
tại giao điểm** chưa được đo.

**Ngưỡng độ lệch khỏi mặt phẳng là bao nhiêu?** `B/09` mục 4B khuyến nghị ít
nhất 20% kích thước tag và ghi rõ đó là phỏng đoán. Liên quan chặt với mục 1 của
sổ này.

**Tỉ lệ baseline đứng trên ngang nên là bao nhiêu?** `B/09` mục 3 khuyến nghị
không dưới một phần ba, dựa trên lập luận rằng ma trận gần suy biến làm sai số
rò rỉ sang hướng khác. Chưa kiểm. `C/16` mục 3D cho thấy pitch và yaw thật sự
tách biệt, nên câu hỏi này giờ đo được.

---

## Câu hỏi về phương pháp và triển khai

**Ngưỡng ρ nên đặt ở đâu, và nó phụ thuộc gì?** `B/10` mục 3B nói rõ không có
hằng số phổ quát và phải dẫn ra bằng Monte Carlo. `C/16` mục 3B cho dữ liệu đầu
tiên (ρ từ 1,33 tới 66,6 theo góc nghiêng) nhưng chưa có đường cong **tỉ lệ chọn
sai theo ρ** — đường cong ấy mới là thứ cho ngưỡng.

**IMU loại được nghiệm sai trong trường hợp nào?** `B/10` mục 5 dẫn ra rằng nó
phụ thuộc hướng của trục lật so với trọng lực. Chưa kiểm bằng mô phỏng.

**Saddle point có thật sự chính xác hơn giao hai đường không, và bao nhiêu?**
`B/08` mục 3 lập luận bằng số hướng ràng buộc (bốn so với hai) và được ủng hộ
gián tiếp bởi việc cộng đồng hiệu chuẩn dùng chessboard. Chưa có so sánh định
lượng trên cùng điều kiện. Đây là mệnh đề nền của đề xuất target lai, nên nó
đáng kiểm.

**Teach-by-showing mất hiệu lực ở khoảng cách nào?** `B/13` mục 3C lập luận rằng
triệt tiêu chỉ ở bậc nhất quanh tư thế dạy. Mini project của `B/13` đo được điều
này nhưng cần phần cứng.

**Thứ tự hiệu chuẩn sai gây sai số bao nhiêu?** `B/12` mục 2 lập luận rằng đảo
thứ tự làm sai số bước trước bị hấp thụ vào bước sau **mà residual vẫn nhỏ**.
Chưa kiểm bằng mô phỏng, và nó kiểm được dễ.

**Chiếu sáng chủ động cải thiện tính ổn định của σ bao nhiêu?** `B/14` mục 4
phát biểu định tính và ghi rõ là không có con số. Mini project của `B/14` đo
được, cần phần cứng.

---

## Câu hỏi nối sang nhánh khác

**Quan hệ với `../IMU_Fusion/`.** Chương `B/11` của cây này (ước lượng theo thời
gian) chồng lấn đáng kể với Phần B của cây IMU_Fusion, đặc biệt là chương về hợp
nhất dựa trên bộ lọc và chương về tối ưu. Câu hỏi cụ thể: nguyên tắc "giữ phép
đo ở dạng nguyên thuỷ nhất mà mô hình nhiễu còn đúng" ở `B/11` mục 4 có tương
đương với nguyên tắc tiền tích phân ở cây kia không, hay chúng là hai ý khác
nhau? Nếu tương đương thì nên trỏ sang thay vì viết lại.

**Quan hệ với bài toán khởi tạo VIO.** `B/10` (xử lý ambiguity) và bài toán chọn
nghiệm trong khởi tạo thị giác-quán tính có cấu trúc giống nhau: cả hai đều là
chọn giữa các nghiệm rời rạc dựa trên một chỉ báo liên tục. Có thể học được gì
từ bên kia không?

---

## Việc đã làm xong

**2026-09-14 — Chạy script Monte Carlo.** Cửa kiểm chứng (b) cho `A/05` (hai
quan hệ tịnh tiến) và `A/04` (ambiguity) đã qua. Kết quả ở `C/16` mục 3, log ở
`C-ngan-sach-sai-so/16-danh-gia-va-nghiem-thu/code/ket-qua-chay-2026-09-14.txt`.
Trong quá trình chạy phát hiện hai lỗi của chính script (quy ước hệ quy chiếu,
và việc báo cáo góc bằng một con số vô hướng) — cả hai đã ghi vào `C/16` mục 2
vì chúng là cạm bẫy chung của mọi mô phỏng loại này.
