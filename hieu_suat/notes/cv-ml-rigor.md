# Cụm CV/ML: musgrave2020 · melis2018 · bouthillier2021 · lipton2019 · sculley2018 · cortes2021 · pineau2021 · simmons2011

**Mức tin.** musgrave2020, melis2018, bouthillier2021, pineau2021, simmons2011 = A (có mã nguồn / dữ liệu toàn hội nghị / đã đổi thực hành). lipton2019, sculley2018 = B/C (bài quan điểm có dẫn chứng). cortes2021 = B (tiền ấn nhưng dữ liệu gốc của chính hội nghị).

- **musgrave2020** — đánh giá lại mảng metric learning trong cùng một khung (cùng backbone, cùng quy trình tinh chỉnh, cùng chia dữ liệu): nhiều bài có khiếm khuyết phương pháp; tiến bộ thật theo thời gian là nhỏ, trong khi các bài tuyên bố tới mức gấp đôi.
- **melis2018** — tinh chỉnh siêu tham số quy mô lớn cho mọi kiến trúc: LSTM tiêu chuẩn được chuẩn hoá tử tế **vượt** các kiến trúc mới hơn. → tinh chỉnh bất đối xứng là confound số một.
- **bouthillier2021** — nguồn dao động: lấy mẫu dữ liệu, khởi tạo, siêu tham số. Kết quả ngược trực giác: **ngẫu nhiên hoá thêm nhiều nguồn** cho ước lượng gần lý tưởng hơn với chi phí nhỏ hơn tới **51×**.
- **cortes2021** (thí nghiệm nhất quán NeurIPS 2014) — ~50 % phương sai điểm chất lượng là chủ quan; trong số bài được nhận, chỉ ~50 % sống sót nếu hội đồng độc lập chấm lại.
- **simmons2011** — bậc tự do của người nghiên cứu đủ để tạo "ý nghĩa thống kê" cho giả thuyết sai; giải pháp là công bố minh bạch (6 yêu cầu cho tác giả, 4 cho phản biện).
- **lipton2019 / sculley2018** — không phân biệt giải thích với suy đoán; không xác định nguồn thật của cải thiện; văn hoá đặt "thắng benchmark" lên trên tri thức.
- **pineau2021** — chương trình tái lập NeurIPS 2019: danh mục kiểm tra, chính sách nộp mã.

**Chỗ tôi không tin.** musgrave2020 và melis2018 là hai mảng con cụ thể (metric learning, mô hình ngôn ngữ); việc suy rộng ra toàn bộ CV là **[M]** — nhưng cùng một hình thái đã lặp ở nhiều mảng, nên tôi coi nó là mẫu hình đáng phòng.

**Dùng ở.** ch. 8 toàn bộ; ch. 9 (phản biện là tín hiệu nhiễu).
