# Nhật ký tìm kiếm — khảo sát PnP

Theo `research-rules.md` mục 3: mỗi lượt tìm ghi ngày, nguồn, truy vấn, số kết quả, số giữ lại
và lý do loại, để tái lập được và mở rộng được mà không làm lại từ đầu. Script và danh sách truy
vấn nguyên văn nằm trong `search/`.

## Tóm tắt trạng thái (2026-09-25)

| | |
|---|---|
| Công trình trong `refs.bib` | 122 entry (119 bài + sách Hartley–Zisserman + 2 mục phần mềm) |
| Kiểm venue/năm/DOI qua Crossref | tất cả, trừ 5: sách `hartley2004`, `jiang2025rscore` (Crossref chưa có, kiểm trên trang CVF), tiền ấn `barath2025superansac` (kiểm trên arXiv), 2 mục phần mềm (kiểm README / header gốc) |
| Có bản PDF open-access đã kiểm URL | 54 bài, tải bằng `papers/fetch.sh` |
| Đã mở abstract gốc | khoảng 37 bài (do agent mở, có trích đoạn nguyên văn); các bài kinh điển còn lại **mới kiểm siêu dữ liệu**, chưa mở abstract |
| Đọc tới lượt 2 hoặc 3 | **0** — chưa có `notes/` nào |
| Trải thời gian | 1981 → 2025; 35 bài trong 2022–2025 |
| Trải nhóm | ≥ 10 nhóm độc lập (Lepetit/Fua/Moreno-Noguer; Kneip; Roumeliotis; Kukelova/Pajdla/Larsson/Sattler; Barath/Matas; Brachmann/Rother; Carlone/Yang; Terzakis/Lourakis; Collins/Bartoli; Kahl/Olsson/Åström; Chin; Ji; …) |

So với chỉ tiêu mục 3: **đủ** về độ phủ (≥ 25–40 bài sàng, có bài gốc và bài trong hai năm gần
nhất, ≥ 3 nhóm). **Chưa đủ** về độ sâu: chỉ tiêu ≥ 12 bài đọc lượt hai và ≥ 3 bài nền tảng đọc
lượt ba chưa làm.

## Lượt 1 — Hạt giống từ trí nhớ, kiểm qua Crossref

- **Ngày:** 2026-09-25.
- **Nguồn:** Crossref REST API, `query.bibliographic`, lấy 3 kết quả đầu.
- **Truy vấn:** `search/truy-van-1.txt` (55 dòng) và `search/truy-van-2.txt` (31 dòng) — tên
  bài + tên tác giả đầu của các công trình kinh điển tôi biết là có.
- **Cách kiểm:** chỉ nhận khi tên bài, tác giả và năm khớp với kết quả Crossref; venue lấy từ
  `container-title`. Với chương sách LNCS, tra thêm `works/<doi>` để biết hội nghị (ECCV / ACCV / DAGM).
- **Giữ lại:** 72. **Loại:** *Revisiting the PnP problem with a GPS* (Pylvänäinen et al., ISVC 2009)
  — venue yếu; *PnP-Net* — Crossref không có bản ghi khớp, không đưa vào; hai truy vấn mơ hồ
  ("point to plane?", "PnP covariance closed form") chỉ trả rác, không giữ gì.
- **Sai lệch phát hiện được:**
  - Crossref ghi tên tác giả đầu của Haralick 1994 là "Bert M." — tên thật là Robert M. Đã sửa.
  - Trang ECVA gắn DOI của SQPnP là `10.1007/978-3-030-58452-8_27`, nhưng DOI này là bài
    *Learning and Aggregating Deep Local Descriptors*. DOI đúng là `…_28`, đã kiểm hai chiều.

## Lượt 2 — Đối chiếu mã nguồn thư viện

- **Ngày:** 2026-09-25.
- **Nguồn:** `opencv/opencv` nhánh `4.x`, file `modules/calib3d/include/opencv2/calib3d.hpp`
  (đọc raw từ GitHub); `PoseLib/PoseLib` `README.md` nhánh `master`.
- **Mục đích:** kiểm các ghi chú kiểu "bộ giải X là mặc định của thư viện Y" trước khi viết.
- **Kết quả:** **ba ghi chú soạn từ trí nhớ bị sai** và đã sửa — `SOLVEPNP_P3P` nay là Ding 2023
  chứ không phải Gao 2003; `SOLVEPNP_UPNP` trỏ tới Penate-Sanchez 2013 chứ không phải Kneip 2014
  (và đang hỏng); P3P của PoseLib là Ding 2023 chứ không phải Lambda Twist. Thêm 5 bài được
  thư viện trích mà danh sách ban đầu thiếu (`search/truy-van-3.txt`): Penate-Sanchez 2013,
  Josephson 2007, Hruby 2024, gDLS 2014, gDLS\* 2020.
- **Bài học cho lần sau:** ghi chú "thư viện nào dùng gì" hết hạn nhanh hơn cả bài báo; phải
  kiểm lại mỗi lần rà.

## Lượt 3 — Quét toàn bộ tiêu đề CVF và ECVA

- **Ngày:** 2026-09-25.
- **Nguồn:** trang "all papers" của CVF open access cho CVPR 2021–2025, ICCV 2021/2023/2025,
  WACV 2024/2025; trang `papers.php` của ECVA cho ECCV 2018–2024.
- **Truy vấn:** biểu thức chính quy trên tiêu đề, xem `search/quet-cvf-ecva.py`.
- **Kết quả:** khoảng 150 tiêu đề khớp. Phần lớn là rác do từ khoá rộng (rolling shutter
  correction, certified robustness của mạng, category-level object pose không dùng PnP, "PnP-DETR"
  trùng tên).
- **Giữ lại:** 15, kiểm qua Crossref bằng `search/truy-van-4.txt` (14 có bản ghi; R-SCoRe
  CVPR 2025 chưa có bản ghi Crossref, kiểm trên trang CVF).
- **Loại có lý do:** *Map-Free Visual Relocalization* (ECCV 2022) — pose tương đối, không phải PnP;
  các bài APR (DFNet, PoseNet họ) — ngoài phạm vi; các bài category-level và render-and-compare —
  không giải PnP; *Learning to Solve Hard Minimal Problems* được giữ dù không riêng PnP vì là
  hướng mới cho bộ giải tối thiểu.
- **Chưa quét:** CVPR 2019/2020 và ICCV 2019 (trang CVF dùng định dạng khác, trả trang rỗng);
  ICRA/IROS/RA-L/T-RO (không có danh sách tiêu đề mở tương đương) — giao cho lượt 4.

## Lượt 4 — Agent tìm kiếm 2021–2026 (giao theo `research-rules.md` mục 8)

- **Ngày:** 2026-09-25.
- **Giao việc:** một agent, sáu cụm câu hỏi (bộ giải mới; bền vững; khả vi / học sâu; bất định
  và suy biến; benchmark và tổng quan; PnP trong định vị), danh sách venue ở `research-rules.md`
  mục 4, bắt buộc trả kèm DOI đã thấy, URL đã mở, trích đoạn nguyên văn từ abstract, mức tin.
- **Nguồn agent dùng:** WebSearch để khám phá; Crossref, trang CVF, arXiv, Springer để kiểm;
  OpenAlex cho abstract khi trang IEEE chặn (403). dblp chặn bot.
- **Agent trả về:** 37 bài đã kiểm + 6 tiền ấn mức C + 5 bài chưa kiểm được.
- **Tôi kiểm lại:** mọi DOI mới qua Crossref `works/<doi>` — cả 17 khớp tên bài, tác giả, venue.
  Trang arXiv của SupeRANSAC mở được, khớp tên.
- **Giữ lại:** 16 bài mới (phần còn lại đã có từ lượt 1–3).
- **Không nhận từ agent:** ghi chú "PoseLib có `p3p_lambdatwist`" — tôi không thấy trong bảng
  README đã đọc, nên không đưa vào. Sáu tiền ấn mức C (*P3P Made Easy*, *Optimal DLT-based
  Solutions for PnP*, gravity-aware affine PnP arXiv 2608.20056, EPRO-GDR, PoseGravity,
  virtual-point gPnP) — chưa đưa vào `refs.bib`, liệt kê ở dưới để theo dõi. Năm bài agent
  không mở được trang gốc (AEPnP ECCV-W 2024; bài T-CSVT 2023 về hướng đã biết; bài arXiv
  2608.04673; DynaWeightPnP; bài SSRN về cấu hình kỳ dị P3P) — không đưa vào.
- **Agent báo lệch:** số trang trên trang CVF thường lệch 1–5 trang so với số trang IEEE (DOI).
  `refs.bib` dùng số trang theo Crossref (IEEE).

## Theo dõi — tiền ấn mức C, xét lại ở lần rà 3/2027

- S. H. Lee, P. Vandewalle, J. Civera, *P3P Made Easy*, arXiv 2508.01312 — comment arXiv ghi nhận ở ECCV Workshop 2026.
- S. Henry, J. A. Christian, *Optimal DLT-based Solutions for the Perspective-n-Point*, arXiv 2410.14164.
- M. Valtonen Örnhag, A. Jaenal, S. Adalbjörnsson, *Gravity-aware partially calibrated absolute pose estimation from affine- or rotation-covariant features*, arXiv 2608.20056 — comment ghi ECCV 2026, chưa kiểm được trong kỷ yếu.
- AEPnP (Wei, Leutenegger, Kneip) — ECCV 2024 Workshops theo kết quả tìm kiếm, chưa mở trang gốc.

## Lượt tiếp theo nên làm

1. **Snowballing chiều tới** (Semantic Scholar "cited by") từ EPnP, SQPnP, Ding 2023, EPro-PnP —
   API Semantic Scholar trả 429 hôm nay, thử lại.
2. Quét tiêu đề ICRA/IROS 2021–2025 và RA-L/T-RO qua Crossref `filter=container-title:…`.
3. Quét CVPR 2019/2020, ICCV 2019 với định dạng URL cũ của CVF.
