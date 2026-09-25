# Ghi chú đọc — lộ trình 10 bài (2026-09-25)

Mười bài của "Lộ trình đọc gợi ý" trong `../danh-muc.md` (mục 9 có hai bài nên có 11 ghi chú). Mỗi bài
được đọc **toàn văn** bởi một agent theo `00-mau-ghi-chu.md`, kèm một script kiểm chứng số trong `../code/`.

**Người đọc là agent, Huy chưa ký.** Những gì đã được kiểm độc lập sau khi agent viết xong:
- mọi trích đoạn nguyên văn khớp đúng trang trong PDF — chạy `python3 search/kiem-trich-dan.py` (cần PDF, tải bằng `papers/fetch.sh`);
- mọi script đã được chạy lại và cho đúng kết quả ghi trong mục 7 của ghi chú;
- một số tuyên bố then chốt được kiểm tay thêm: lỗi in eq. (22) của IPPE, dấu trừ trong công thức k của RANSAC,
  mâu thuẫn 16 % trong abstract của Vakhitov, và lỗi của `cv2.SOLVEPNP_EPNP` trên dữ liệu phẳng không nhiễu
  (đo lại bằng script riêng).

Chưa được kiểm: diễn giải và phê phán trong mục 6, 8, 11 — đó là việc của lần đọc lại.

## Bảng tổng hợp

| # | Ghi chú | Mức đọc | Kiểm chứng số | Phát hiện chính | Mức tin |
|---|---|---|---|---|---|
| 1 | [marchand2016arsurvey](marchand2016arsurvey.md) | lượt 2 | 21/21 | Công thức in thiếu bước: khử thang của DLT, chiều cập nhật exp phải là exp(δq)⁻¹, chuẩn hoá H. DLT cần ≥ 6 điểm không đồng phẳng — bài không nói, nên không dùng được làm bộ giải tối thiểu. | giữ A (tổng quan) |
| 2 | [haralick1994review](haralick1994review.md) | lượt 3 / 2 | tái lập bảng II–V cùng bậc | Bốn lỗi in (eq. 51, hệ số Finsterwalder, v_small, Fig. 2). "Chênh 1000 lần theo thứ tự thế" là do trung bình kéo; trung vị ~23 lần. Phân bố số nghiệm phụ thuộc trường nhìn. | giữ A |
| 3 | [lepetit2009epnp](lepetit2009epnp.md) | lượt 3 | tìm lại chính xác n = 4..50 | Ca phẳng 3 vector nhân thiếu hạng (6/9). **`cv2.SOLVEPNP_EPNP` không phải thuật toán của bài** và trượt trên dữ liệu phẳng không nhiễu. Eq. (15) thiếu dấu bình phương. | giữ A |
| 4 | [lu2000orthogonal](lu2000orthogonal.md) | lượt 3 | cost đơn điệu 24 000/24 000 bước | "Globally convergent" = hội tụ về điểm bất động (Zangwill), **không** phải tối ưu toàn cục. Eq. (16) chuyển vị sai; bước (31) sai nhưng lập luận majorize–minimize cứu được. Hội tụ tuyến tính, không "gần bậc hai". | giữ A |
| 5 | [terzakis2020sqpnp](terzakis2020sqpnp.md) | lượt 3 | 6/2320 ca trượt cực tiểu toàn cục | Tối ưu **Σ z²‖m − π‖²**, không phải sai số tái chiếu. Toàn cục chỉ là thực nghiệm; Mệnh đề 3 sai; eq. (14) lệch chỉ số. OpenCV chỉ dùng một seed mỗi vector riêng nên trượt nhiều hơn (23 so với 8). | A cho công thức; "toàn cục" hạ xuống "thực nghiệm" |
| 6 | [collins2014ippe](collins2014ippe.md) | lượt 3 / 2 | 14/14 | Hai nghiệm là ảnh gương **chính xác** qua mặt phẳng vuông góc tia nhìn. Ba lỗi in (eq. 14, eq. 22 cho σ₁², chứng minh Theorem 5). Mâu thuẫn ba chỗ với chương `marker/` A/04. | giữ A |
| 7 | [fischler1981ransac](fischler1981ransac.md) | lượt 3 / 2 | 47/47 | Công thức số vòng giả định lấy mẫu có hoàn lại — thiếu khi N nhỏ. "6 điểm luôn cho nghiệm duy nhất" sai (twisted cubic). OpenCV 5 P3P/AP3P đánh rơi nghiệm ở cấu hình nghiệm kép. | giữ A |
| 8 | [ding2023p3p](ding2023p3p.md) | lượt 3 | 100k lượt không nhiễu: 100 % | OpenCV 5 `SOLVEPNP_P3P` khớp hành vi của Ding. Khi ba điểm gần thẳng hàng sai số ~1/ε², tệ hơn AP3P (~1/ε). Trên danger cylinder mọi bộ giải trượt 24–49 %. | giữ A |
| 9a | [urban2016mlpnp](urban2016mlpnp.md) | lượt 3 / 2 | 15/15 | Lợi ích đến hoàn toàn từ covariance (sai số xoay 0,25–0,41× khi nhiễu bất đẳng hướng). Covariance nhất quán (NEES) tới ~5 lần nhiễu. Tuyên bố vượt SOTA dựa vào MLPnP+Σ có cơ sở yếu. | giữ B |
| 9b | [vakhitov2021uncertainty](vakhitov2021uncertainty.md) | lượt 3 / 2 | công thức khớp Monte Carlo < 1,5 % | Tính bất định 3D giúp nhiều khi nhiễu 3D lớn và không đều; xấp xỉ đẳng hướng của bài đánh mất lợi ích với nhiễu kiểu stereo. Văn bản mâu thuẫn bảng ở vài chỗ. | giữ B |
| 10 | [chen2022epropnp](chen2022epropnp.md) | lượt 3 / 2 | 11/12 (FAIL = AMIS đơn giản hoá của người kiểm) | Lý do loss kiểu BPnP học kém nghiêng về việc loss không nhạy thang trọng số hơn là tính khả vi. log Z trơn qua chỗ nghiệm đổi nhánh. Ngoại lai bị hạ trọng số tương đối, không về 0. | giữ B |

## Những gì thay đổi trong bức tranh chung sau khi đọc

- **Phần lớn bài nền có lỗi in.** Tám trên mười một bài (trừ Marchand — thiếu bước chứ không in sai —, MLPnP, EPro-PnP) có ít nhất một công thức in sai, và được bắt
  bằng cách cài lại rồi so số. Quy tắc "không chép công thức khi chưa kiểm" (learning-rules mục 5) không
  phải hình thức.
- **"Tối ưu toàn cục" và "hội tụ toàn cục" nghĩa khác hẳn nhau**, và cả hai đều yếu hơn cách các bài sau
  trích lại: Lu–Hager hội tụ về điểm bất động; SQPnP toàn cục theo thực nghiệm và cho một hàm có trọng số.
- **OpenCV không cài đúng bài báo** ở ít nhất ba cờ: EPnP (không tái tuyến tính hoá, không nhánh phẳng),
  SQPnP (một seed), IPPE (translation khác công thức đóng). Cộng thêm DLS/UPnP đã biết là hỏng. Xem
  mục *Cạm bẫy* cuối `../danh-muc.md`.
- **Target phẳng là chỗ mọi thứ hỏng**: EPnP của OpenCV lật nghiệm, SQPnP trượt toàn cục, Lu–Hager dừng ở
  nghiệm khác nghiệm tốt nhất ở 4–46 % số khởi tạo hợp lệ, IPPE chọn nhầm tới 50 % khi target nhỏ 20 px. Đây là lý do thực tế để
  đọc tiếp nhóm 4 và cây `marker/`.
- Câu hỏi 8 của `../00-cau-hoi.md` (PnP khả vi giải bài toán gì) có câu trả lời một phần từ EPro-PnP; câu 4
  và 5 (con số có so được không; bộ giải dạng đóng còn quan trọng tới đâu) vẫn chưa bài nào trả lời trực
  tiếp — nhưng dữ liệu của ghi chú EPnP, SQPnP, Marchand đã đủ để bắt đầu một thí nghiệm trong `../code/`.

## Tiếp theo

1. Huy đọc lại và ký — ưu tiên EPnP, SQPnP, Ding (ba bài nền dùng trực tiếp trong code).
2. Sửa ba chỗ trong `marker/A-nguyen-ly-va-toan-hoc/04-pose-ambiguity-target-phang/` mà ghi chú IPPE mục 10 chỉ ra.
3. Lập `../matrix.md` từ 11 ghi chú (hàng = bài, cột = 9 câu hỏi dẫn đường), rồi viết bài học.
