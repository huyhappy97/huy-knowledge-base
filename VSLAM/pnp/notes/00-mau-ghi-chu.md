# Mẫu ghi chú đọc — `notes/<bibkey>.md`

Theo `research-rules.md` mục 5. Viết **bằng lời của mình**, tiếng Việt, thuật ngữ giữ tiếng Anh
hoặc dạng *tiếng Việt (English)* ở lần đầu. Không chép abstract.

**Quy tắc định vị — bắt buộc ở mọi câu:**
- `[§3.2]`, `[eq. (12)]`, `[Fig. 4]`, `[Tab. 2]`, `[tr. 7]` cho điều tác giả nói — dùng số mục,
  số công thức, số hình **của bản gốc**; `tr.` là số trang trong file PDF ở `papers/`.
- `(tôi suy ra)` cho điều người ghi chú tự thêm.
- Nhãn `[Đ]` tác giả đo được (có số, có điều kiện) · `[T]` tác giả tuyên bố / suy luận ·
  `[M]` người ghi chú suy ra hoặc ghép. Không trộn hai nhãn trong một câu.

**Ký hiệu thống nhất của khảo sát** (xem `code/common.py`): `X_w` điểm thế giới, `R, t` với
`X_c = R X_w + t`, `K` nội tham số, `u` pixel, `f` tia chiếu đơn vị.

---

```markdown
# <Tên bài> — ghi chú đọc

| | |
|---|---|
| bibkey | `<bibkey>` |
| Venue, năm | … |
| Bản đã đọc | `papers/<bibkey>.pdf` — nguồn: <URL>, <số trang> trang (bản tác giả / bản xuất bản) |
| Mức đọc | lượt 2 / lượt 3 (Keshav) |
| Người đọc | Claude (agent), ngày … — **Huy chưa đọc lại để ký** |
| Mức tin | giữ / đổi thành … vì … |
| Kiểm chứng | cửa (a)/(b)/(c) cho từng công thức lõi — xem mục 7 |

## 1. Bài toán gốc và bối cảnh
## 2. Giả thiết — kể cả giả thiết ngầm; bỏ đi thì hỏng ở đâu
## 3. Cơ chế — năm câu, rồi chi tiết có định vị
## 4. Ký hiệu của bài ↔ ký hiệu của khảo sát
## 5. Bằng chứng — dữ liệu, phần cứng, baseline, con số kèm điều kiện, số lần lặp
## 6. Đóng góp thật sự (thường nhỏ hơn abstract)
## 7. Kiểm chứng của người ghi chú — script trong `code/`, lệnh chạy, kết quả thật
## 8. Chỗ tôi không tin
## 9. Chỗ tôi chưa hiểu (→ `99-chua-biet.md`)
## 10. Quan hệ với các bài khác trong `refs.bib`
## 11. Nó đổi gì trong suy nghĩ
## 12. Câu hỏi tự kiểm (3–5 câu, hỏi *vì sao* / *khi nào hỏng*)
## Trích đoạn nguyên văn làm bằng chứng
- "…" [tr. N]   (mỗi trích ≤ 40 từ, 4–8 trích, để kiểm rằng bài thực sự nói điều được gán)
```
