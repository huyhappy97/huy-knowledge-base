# Khảo sát PnP — khung câu hỏi (bước 0 của `research-rules.md`)

Ngày lập: 2026-09-25. Lần sửa gần nhất: 2026-09-25.

Thư mục này là một **dự án khảo sát** theo `../../research-rules.md`, đặt bên trong cây
VSLAM vì PnP là cỗ máy nằm dưới relocalization (ch 12), tracking theo bản đồ, loop closure
và khởi tạo. Nó chưa phải một chương của cây: sản phẩm hiện tại là **danh mục nguồn đã kiểm
chứng** (`danh-muc.md`, `refs.bib`). Bài học LaTeX dựng từ danh mục đó là bước sau.

## Phạm vi

**Bao gồm.** Ước lượng tư thế tuyệt đối 6 bậc tự do của một camera từ tương ứng giữa đặc
trưng ảnh 2D và hình học 3D đã biết trong hệ toạ độ thế giới:

- bài toán tối thiểu (P3P; P2P khi biết trọng lực; P4Pf, P4Pfr khi thiếu nội tham số);
- bộ giải cho n điểm: dạng đóng, lặp, tối ưu toàn cục, có chứng nhận;
- target phẳng và hiện tượng lưỡng nghĩa;
- camera không chuẩn: rolling shutter, camera tổng quát nhiều tâm chiếu, méo xuyên tâm, khúc xạ;
- tương ứng không phải điểm: đường (PnL), trộn điểm + đường (PnPL), tương ứng affine;
- bất định và covariance của pose ước lượng được;
- ước lượng bền vững với ngoại lai (họ RANSAC, branch-and-bound, GNC);
- PnP khả vi và PnP đặt bên trong mạng học sâu (6D object pose, scene coordinate regression).

**Không bao gồm** (trỏ sang chỗ khác, không viết lại):

- pose tương đối 2D–2D (essential, fundamental, homography) → `../A-nguyen-ly-va-toan-hoc/01-hinh-hoc-da-thi/`;
- đăng ký 3D–3D (Horn, Umeyama, ICP, TEASER) — chỉ nhắc khi so sánh;
- hồi quy pose trực tiếp bằng mạng (PoseNet và họ APR) — không giải PnP; xem
  `../B-front-end-va-back-end/12-relocalization/`;
- trường hợp fiducial marker, lưỡng nghĩa của target phẳng nhìn gần, và ngân sách sai số →
  đã viết kỹ ở `../../marker/A-nguyen-ly-va-toan-hoc/03-pnp-va-uoc-luong-tu-the/` và `04-pose-ambiguity-target-phang/`.
  Khảo sát này **không lặp lại** phần đó.

## Câu hỏi dẫn đường

Đây sẽ là các cột của `matrix.md` ở bước 4.

1. **Số nghiệm và hình học của nghiệm.** Với mỗi biến thể (P3P, P4Pf, target phẳng, ...), có bao
   nhiêu nghiệm thực, và cấu hình nào (danger cylinder, điểm đồng phẳng, điểm gần thẳng hàng)
   làm bộ giải suy biến hoặc mất ổn định số?
2. **Hàm mục tiêu thực sự được cực tiểu hoá.** Mỗi bộ giải cực tiểu hoá sai số gì — đại số,
   sai số trong không gian vật (object-space), sai số tái chiếu, sai số góc — và vì sao hàm
   đó được chọn? Nghiệm "tối ưu toàn cục" là tối ưu *theo hàm nào*?
3. **Giả thiết về nhiễu.** Bộ giải nào giả định nhiễu đẳng hướng, bộ nào dùng covariance cho
   từng điểm (MLPnP, CEPnP, EPro-PnP), và bộ nào là nhất quán thống kê (consistent) khi n → ∞?
4. **Độ chính xác so với tốc độ, đo trong điều kiện nào.** Con số thời gian chạy và sai số
   báo cáo được đo trên dữ liệu gì, phần cứng gì, với bao nhiêu ngoại lai — và các con số của
   những bài khác nhau có so sánh được với nhau không?
5. **Vai trò trong pipeline.** Khi đã có RANSAC + tinh chỉnh LM, độ chính xác của bộ giải dạng
   đóng còn quan trọng tới đâu? Khi nào bộ giải tối thiểu tốt hơn quyết định kết quả cuối,
   khi nào chỉ đổi tốc độ?
6. **Ngoại lai.** Loại ngoại lai nằm ở đâu — trong RANSAC, trong chính bộ giải (REPPnP), hay
   trong tối ưu có chứng nhận — và đánh đổi của từng chỗ là gì?
7. **Thông tin phụ trợ.** Trọng lực từ IMU, focal chưa biết, rolling shutter, nhiều camera:
   mỗi thứ đổi số bậc tự do và số điểm tối thiểu ra sao, và lợi thực tế là bao nhiêu?
8. **Học sâu.** PnP khả vi (BPnP, EPro-PnP, DSAC) giải bài toán gì mà PnP cổ điển không giải —
   hay chỉ làm cho tín hiệu học đi xuyên qua được bộ giải? Đầu ra pose có còn diễn giải được
   như một ước lượng hình học không?
9. **Kiểm chứng độc lập.** Bộ giải nào đã được người ngoài nhóm tác giả cài lại và dùng làm
   mặc định (OpenCV, PoseLib, OpenGV, COLMAP), và tuyên bố nào chỉ có nhóm gốc xác nhận?

## Từ vựng và các biến thể thuật ngữ

Các nhóm gọi cùng một bài toán bằng tên khác nhau; tìm kiếm phải chạy với mọi biến thể.

| Khái niệm | Các biến thể gặp trong tài liệu |
|---|---|
| bài toán chính | Perspective-n-Point, PnP, absolute pose, camera resectioning, space resection (trắc địa ảnh), exterior orientation, 2D–3D registration, pose from n points |
| bài toán tối thiểu | P3P, perspective-three-point, three-point pose, Grunert's problem, minimal absolute pose |
| thiếu nội tham số | PnPf, P4Pf, PnPfr, P4Pfr, P5Pfr, uncalibrated absolute pose, unknown focal length / radial distortion |
| biết trọng lực | upright pose, known vertical direction, gravity-aware, P2P, up2p |
| nhiều tâm chiếu | generalized camera, non-central, gP3P, NPnP, multi-camera, gPnP, pose and scale (gDLS) |
| đường | PnL, perspective-n-line, pose from lines; trộn: PnPL, point-line absolute pose |
| khả vi | differentiable PnP, backpropagating PnP, end-to-end PnP, declarative layer, implicit differentiation |
| không có tương ứng | blind PnP, correspondence-free, simultaneous pose and correspondence |
| tinh chỉnh | LM refinement, Gold Standard, bundle adjustment of pose only, motion-only BA |

## Nền tảng tôi đang thiếu (thành chương "nền tảng tối thiểu" của bài học)

Các mục cây đã có thì trỏ sang, không viết lại:

- mô hình chiếu, ma trận K, tia chiếu (bearing vector) → `../A-nguyen-ly-va-toan-hoc/02-mo-hinh-camera/`;
- tham số hoá SO(3)/SE(3), Gauss–Newton trên đa tạp → `../A-nguyen-ly-va-toan-hoc/03-lie-group-va-toi-uu-tren-da-tap/`;
- lan truyền covariance từ pixel sang pose → `../A-nguyen-ly-va-toan-hoc/06-bat-dinh-va-lan-truyen-sai-so/` và
  `../../marker/A-nguyen-ly-va-toan-hoc/05-lan-truyen-sai-so-pixel-sang-pose/`;
- **chưa có trong cây, phải học mới:** hình học đại số cho bộ giải tối thiểu (cơ sở Gröbner,
  action matrix, resultant); nới lỏng SDP và chứng nhận tối ưu (Shor relaxation, sum-of-squares);
  định lý hàm ẩn cho lớp tối ưu khả vi.
