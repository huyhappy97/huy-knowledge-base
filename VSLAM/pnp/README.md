# PnP — khảo sát Perspective-n-Point

Ước lượng tư thế 6 bậc tự do của camera từ tương ứng 2D–3D. Đây là **dự án khảo sát** theo
`../../research-rules.md`, đặt trong cây VSLAM vì PnP nằm dưới relocalization (ch 12), tracking
theo bản đồ, loop closure và khởi tạo.

**Trạng thái (2026-09-25): đã xong bước 0–2 (khung câu hỏi, săn nguồn, sàng lọc). Chưa làm
bước 3–4 (đọc từng bài, viết bài học).** Tức là ở đây có một danh mục nguồn đáng tin, chưa có
hiểu biết đã tổng hợp.

## Đọc gì trước

1. `danh-muc.md` — **bắt đầu ở đây.** 122 mục (119 bài báo, 1 sách, 2 phần mềm) chia theo 15 nhóm, mỗi mục có tên,
   tác giả, venue, năm, mức tin A/B/C và một câu vì sao đọc. Đầu file có lộ trình mười bài
   (80/20); cuối file có các cạm bẫy của OpenCV phát hiện lúc kiểm nguồn.
2. `00-cau-hoi.md` — phạm vi (gồm gì, **không** gồm gì), chín câu hỏi dẫn đường, từ vựng.
3. `99-chua-biet.md` — câu hỏi cụ thể chưa trả lời được.

## Cấu trúc

```
README.md          file này
00-cau-hoi.md      bước 0: phạm vi, câu hỏi dẫn đường, biến thể thuật ngữ, nền còn thiếu
danh-muc.md        danh mục có chú giải + lộ trình đọc — sản phẩm chính hiện tại
refs.bib           122 entry, mỗi entry có DOI (đã kiểm) và mức tin; mặc định "% chưa đọc kỹ"
search-log.md      nhật ký bốn lượt tìm, tái lập được; lý do loại từng nhóm bài
search/            script kiểm Crossref, quét CVF/ECVA, và danh sách truy vấn nguyên văn
papers/fetch.sh    tải 54 PDF open-access về papers/<bibkey>.pdf
99-chua-biet.md    sổ những điều chưa biết
```

Chưa có (theo `research-rules.md` mục 1, sẽ thêm khi đọc): `notes/<bibkey>.md`, `matrix.md`,
`bai-hoc/` (bài học LaTeX dùng chung `../preamble/common.tex`).

## PDF

Repo này public, nên **PDF gốc không được commit** (`papers/.gitignore`). Tải về máy:

```bash
./papers/fetch.sh                       # mọi bài có bản open-access (54 bài)
./papers/fetch.sh ding2023p3p lepetit2009epnp   # chỉ vài bài
```

Chỉ những bài có bản mở chính thức (CVF open access, ECVA, Copernicus, arXiv) mới nằm trong
script. Bài IEEE / Springer / Elsevier không có bản mở thì mở qua DOI trong `refs.bib`.

## Kiểm nguồn đã làm, và chưa làm

- Mọi entry đã đối chiếu **tên bài + tác giả + venue + năm + DOI** với Crossref hoặc trang gốc.
  Không DOI nào được đoán. Chi tiết và các sai lệch bắt được: `search-log.md`.
- Mức tin A/B/C là **phán đoán ban đầu**; A chỉ được gán khi thấy bằng chứng bộ giải được người
  ngoài nhóm tác giả dùng làm chuẩn (OpenCV, PoseLib, OpenGV, benchmark).
- **Chưa đọc bài nào tới lượt hai.** Đừng trích danh mục này như thể nó là hiểu biết đã kiểm.

## Quan hệ với phần còn lại của kho

- `../../marker/A-nguyen-ly-va-toan-hoc/03-pnp-va-uoc-luong-tu-the/` — chương PnP đã viết cho
  fiducial marker (P3P, EPnP, IPPE, tinh chỉnh Gauss–Newton, PnP trên nhiều tag). Khảo sát này
  mở rộng ra ngoài phạm vi đó, **không lặp lại** nó.
- `../B-front-end-va-back-end/12-relocalization/` — nơi PnP-RANSAC được dùng trong hệ SLAM.
- `../A-nguyen-ly-va-toan-hoc/06-bat-dinh-va-lan-truyen-sai-so/` — nền cho nhóm 9 (bất định).
