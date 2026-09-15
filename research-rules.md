# Quy tắc: Kho nghiên cứu và tổng hợp tri thức

Kho học tập (`learning-rules.md`) lưu **thứ tôi đã hiểu và đã sắp xếp lại**. Kho này làm hai việc khác:

1. **Dựng hiểu biết từ con số không.** Phần lớn chủ đề tôi đụng tới là mới với tôi: không có sách giáo khoa, chỉ có vài chục công trình rải rác của nhiều nhóm, mỗi nhóm dùng ký hiệu riêng và tin những thứ mâu thuẫn nhau. Sản phẩm của việc này **không phải một danh sách paper**, mà là **một bài học sâu, liền mạch, dựng lại toàn bộ tri thức của cộng đồng về chủ đề đó**, có trích dẫn tới tận công thức, đọc từ đầu đến cuối là hiểu được lĩnh vực.
2. **Từ bài học đó mở ra nghiên cứu của riêng tôi.** Bài học viết đúng sẽ tự lộ ra chỗ các tác giả bất đồng và chỗ chưa ai trả lời — đó là điểm xuất phát của câu hỏi nghiên cứu, không phải cảm hứng ngẫu nhiên.

Tài liệu học tập đúng khi trình bày rõ ràng. Tài liệu ở kho này chỉ đúng khi **truy được nguồn của từng khẳng định** và **phân biệt được điều đã đo với điều mới chỉ phỏng đoán**.

---

## 1. Hai loại dự án và cấu trúc thư mục

Một dự án **khảo sát** (`survey/`) trả lời câu hỏi *"cộng đồng đã biết gì về X?"*. Một dự án **nghiên cứu** (`research/`) trả lời câu hỏi *"điều này có đúng không?"* — đủ hẹp để có thể sai. Khảo sát luôn đi trước; nghiên cứu mà không có khảo sát thì chỉ là phát minh lại thứ người ta đã bác bỏ mười năm trước.

```
survey/<chu-de>/
├── 00-cau-hoi.md            # phạm vi + các câu hỏi dẫn đường mà bài học phải trả lời
├── search-log.md            # nhật ký tìm kiếm: nguồn, truy vấn, ngày, số bài giữ lại
├── papers/                  # PDF gốc, đặt tên theo bibkey
├── refs.bib                 # bibliography, mỗi entry đủ venue + năm + DOI/arXiv id
├── notes/<bibkey>.md        # một file một công trình
├── matrix.md                # ma trận tổng hợp: hàng = công trình, cột = chủ đề
└── bai-hoc/                 # SẢN PHẨM CHÍNH: bài học sâu, dạng LaTeX như cây học tập
    ├── 00-map.tex
    ├── 01-nen-tang/ …
    └── bai-hoc.tex

research/<cau-hoi>/
├── 00-question.md           # câu hỏi, giả thuyết, mức tin, tiêu chí falsify
├── journal.md               # nhật ký thời gian, chỉ ghi thêm
├── experiments/exp-NNN-<slug>/{hypothesis.md,config/,results/,analysis.md}
├── code/  figures/  paper/{main.tex,refs.bib}
└── 99-archive/              # hướng đã bỏ, kèm lý do bỏ
```

`99-archive/` không được xoá: hướng thất bại là kết quả nghiên cứu thật, và ba tháng sau tôi sẽ quên mất mình từng thử.

Quy trình đi qua sáu bước: **(0)** dựng khung câu hỏi → **(1)** săn nguồn → **(2)** sàng lọc chất lượng → **(3)** đọc và ghi chú từng công trình → **(4)** tổng hợp thành bài học sâu → **(5)** mở ra nghiên cứu. Bốn bước đầu là bắt buộc trước khi viết bất kỳ dòng nào của bài học; nhảy cóc sang bước 4 sẽ cho ra một bản tóm tắt trung bình cộng của vài abstract, đúng thứ tôi không cần.

---

## 2. Bước 0 — Dựng khung câu hỏi trước khi tìm

Tìm kiếm không có khung sẽ cho ra một đống bài liên quan mơ hồ. Trước khi mở công cụ tìm kiếm, viết `00-cau-hoi.md` gồm:

- **Phạm vi**: chủ đề này bao gồm gì và **rõ ràng không bao gồm gì**. Ranh giới quan trọng hơn tâm điểm.
- **Câu hỏi dẫn đường**: từ năm đến chín câu hỏi mà bài học bắt buộc phải trả lời. Đây chính là các cột của ma trận tổng hợp ở bước 4, nên phải viết dạng câu hỏi thực chất — *"đại lượng nào quan sát được và đại lượng nào không?"*, *"các nhóm bất đồng ở giả thiết nào?"*, *"chi phí tính toán thực tế là bao nhiêu và đo trên phần cứng gì?"* — chứ không phải *"có những phương pháp nào?"*.
- **Từ vựng**: thuật ngữ chính kèm **mọi biến thể** mà các nhóm khác nhau dùng cho cùng một thứ. Bỏ sót một biến thể là bỏ sót cả một trường phái.
- **Nền tôi đang thiếu**: những khái niệm phải học trước mới đọc nổi tài liệu. Danh sách này trở thành chương "nền tảng tối thiểu" của bài học, và những mục nào cây học tập đã có thì trỏ sang, không viết lại.

---

## 3. Bước 1 — Săn nguồn: giao thức và chỉ tiêu

Mục tiêu của bước này là **độ phủ**, chưa phải chất lượng. Sàng ở bước 2.

**Bộ hạt giống.** Bắt đầu bằng hai đến ba bài tổng quan (survey) mới nhất ở venue tốt, cộng hai đến ba công trình kinh điển ai cũng trích. Đọc phần related work của chúng để lấy bản đồ sơ bộ về các trường phái.

**Lăn cầu tuyết (snowballing) hai chiều**, theo giao thức của Wohlin: từ mỗi bài trong bộ hạt giống, đi **lùi** qua danh mục tham khảo của nó, và đi **tới** qua danh sách những bài trích dẫn nó (Google Scholar / Semantic Scholar "cited by"). Lặp cho tới khi **bão hoà**: một vòng mới không thêm được công trình nào đáng đọc. Chiều tới quan trọng hơn chiều lùi khi chủ đề đang chuyển động, vì nó tìm ra ai đã bác bỏ bài gốc.

**Nhiều nguồn, nhiều truy vấn.** Google Scholar và Semantic Scholar cho độ phủ; dblp để soi toàn bộ công trình của một tác giả và biết chính xác venue; arXiv cho bài mới; IEEE Xplore / ACM DL cho bản đã phản biện. Mỗi khái niệm chạy lại truy vấn với mọi biến thể thuật ngữ đã liệt kê ở bước 0.

**Chỉ tiêu tối thiểu cho một chủ đề** (dưới mức này coi như chưa khảo sát):

- sàng ít nhất **25–40 công trình**, trong đó ≥ 12 bài đọc tới lượt hai và ≥ 3 bài nền tảng đọc tới lượt ba;
- trải theo thời gian: có bài gốc khai sinh vấn đề, có bài mới trong vòng **hai năm gần nhất**;
- trải theo nhóm: ít nhất **ba nhóm nghiên cứu độc lập**. Nếu toàn bộ tài liệu đến từ một phòng thí nghiệm thì tôi đang học quan điểm của một nhóm chứ không phải của lĩnh vực, và phải ghi rõ điều đó.

**`search-log.md` ghi lại từng lượt tìm**: ngày, nguồn, truy vấn nguyên văn, số kết quả, số giữ lại, lý do loại. Một tìm kiếm không tái lập được thì sau này không thể biết mình đã bỏ sót gì, và cũng không thể mở rộng khảo sát mà không làm lại từ đầu.

---

## 4. Bước 2 — Sàng lọc chất lượng nguồn

**Uy tín nơi công bố là bộ lọc rẻ nhất, dùng đầu tiên.** Với hội nghị, dựa vào xếp hạng CORE (A\* là venue hàng đầu của ngành, A là rất tốt); với tạp chí, dựa vào quartile Scimago (Q1 là 25 % đầu của lĩnh vực) và h5-index. Trong lĩnh vực của tôi, tuyến đầu là T-RO, IJRR, RA-L, T-PAMI, IJCV cho tạp chí và CVPR/ICCV/ECCV, ICRA/IROS/RSS, NeurIPS/ICML/ICLR cho hội nghị. Xếp hạng không đo được chất lượng của một bài cụ thể, nhưng nó loại rất nhanh phần lớn thứ không đáng đọc.

**Bản tiền ấn arXiv** được nhận có điều kiện: nhóm tác giả có lịch sử công trình được tái lập, có mã nguồn công khai, hoặc đã được trích dẫn nghiêm túc bởi người ngoài nhóm. Luôn dán nhãn *arXiv preprint* và kiểm xem đã có bản hội nghị/tạp chí chưa — nếu có, dùng bản đó vì nội dung thường đã đổi sau phản biện.

**Cờ đỏ, loại thẳng:** hội nghị hoặc tạp chí săn phí (kiểm chéo với DOAJ và các danh sách kế thừa danh sách Beall); bài chỉ khoe con số mà giấu điều kiện thí nghiệm; bài chỉ so với baseline yếu hoặc baseline tự cài đặt kém hơn số công bố gốc; không có mã nguồn và không dùng bộ dữ liệu chuẩn; trích dẫn vòng trong một nhóm nhỏ; văn bản do mô hình ngôn ngữ sinh rồi đăng lại. Với bài định dùng làm nền tảng, kiểm nhanh Retraction Watch / trang nhà xuất bản xem có bị rút hay đính chính không.

**Ba mức tin, dán ngay vào entry bib và vào ghi chú:**

- **A** — đã qua phản biện ở venue đầu ngành **và** đã được người ngoài nhóm tái lập hoặc kiểm chứng độc lập;
- **B** — đã qua phản biện tốt, chưa ai tái lập công khai;
- **C** — tiền ấn chưa kiểm chứng, hoặc nguồn yếu nhưng là công trình duy nhất chạm tới vấn đề.

Quy tắc bắt buộc: **một khẳng định lõi của bài học phải tựa vào ít nhất một nguồn mức A, hoặc hai nguồn mức B độc lập nhau.** Nguồn mức C không bao giờ được đứng một mình làm chỗ dựa; khi dùng, ghi ngay tại chỗ *"chưa kiểm chứng, dùng làm gợi ý chứ không làm bằng chứng"*.

---

## 5. Bước 3 — Đọc và ghi chú từng công trình

**Đọc ba lượt** theo phương pháp của Keshav. Lượt một (5–10 phút): tiêu đề, abstract, phần mở đầu, tiêu đề mục, hình, kết luận — đủ để quyết định có đọc tiếp không; phần lớn công trình dừng ở đây và điều đó là bình thường. Lượt hai (≈ 1 giờ): đọc toàn bộ trừ chứng minh, nắm đóng góp và thiết kế thí nghiệm, đánh dấu tài liệu cần đọc thêm. Lượt ba (nhiều giờ): chỉ dành cho bài nền tảng — dựng lại công trình như thể chính tôi viết ra nó, kiểm từng bước suy dẫn, tìm ra giả thiết ngầm mà tác giả không nói.

Ghi chú `notes/<bibkey>.md` viết **bằng lời của tôi**, không chép abstract, và phải trả lời:

- **Bài toán gốc và bối cảnh**: họ khó ở chỗ nào, trước họ người ta làm sao và hỏng ở đâu.
- **Giả thiết**, kể cả giả thiết ngầm. Nếu bỏ một giả thiết thì kết quả hỏng ở đâu?
- **Cơ chế**: ý tưởng lõi giải thích được trong năm câu, kèm **định vị chính xác** — mục, số hiệu công thức, số hình — để sau này trích lại mà không phải đọc lại cả bài.
- **Ký hiệu của họ**, đối chiếu với ký hiệu tôi dùng. Đây là thứ mất nhiều thời gian nhất khi ghép nhiều công trình, ghi ngay lúc đọc thì sau đỡ khổ.
- **Bằng chứng**: đo trên dữ liệu nào, phần cứng nào, so với baseline nào, con số bao nhiêu, lặp lại mấy lần. Con số không kèm điều kiện là con số vô nghĩa.
- **Đóng góp thật sự** — hầu như luôn nhỏ hơn nhiều so với tuyên bố ở abstract.
- **Chỗ tôi không tin** và **chỗ tôi chưa hiểu**. Hai mục này bắt buộc; ghi chú không có phê phán chỉ là bản tóm tắt, và mục "chưa hiểu" là nguồn cấp cho sổ những điều chưa biết (xem `learning-rules.md`).
- **Quan hệ với các bài khác**: bổ sung ai, mâu thuẫn ai, và mâu thuẫn ở khẳng định nào.
- **Nó đổi gì trong suy nghĩ của tôi.** Nếu không đổi gì, nói rõ như vậy.

Trong ghi chú, **mỗi câu phải chỉ được nguồn của nó**: `[§III-B]`, `[eq. (12)]`, `[Fig. 4]` cho điều tác giả nói; `(tôi suy ra)` cho điều tôi tự thêm. Trộn hai loại này là con đường chắc chắn nhất dẫn tới việc trích dẫn sai người khác vì một ý mà chính tôi nghĩ ra.

---

## 6. Bước 4 — Tổng hợp thành bài học sâu (sản phẩm chính)

Đây là điểm khác biệt lớn nhất giữa kho này và một thư mục PDF. Đích đến là **một bài học đọc được như một chương sách**, nơi tri thức của nhiều tác giả đã được **sắp xếp lại theo mạch khái niệm của chủ đề**, chứ không theo thứ tự tôi tình cờ đọc.

### 6.1 Ma trận tổng hợp, và quy tắc "viết theo cột"

Lập `matrix.md` dạng bảng: **hàng là công trình, cột là câu hỏi dẫn đường** ở bước 0; mỗi ô ghi công trình đó nói gì về câu hỏi đó (kèm định vị), ô trống nghĩa là họ không đụng tới.

Rồi **viết theo cột, không viết theo hàng**. Viết theo hàng cho ra "Nguyễn làm thế này. Trần làm thế kia. Lê làm thế nọ." — một danh sách tóm tắt, không phải bài học, và đọc lại sau một năm sẽ không rút ra được gì. Viết theo cột cho ra: *"Cả ba nhóm đều phải xử lý X. Hai hướng khả dĩ: A và B. Hướng A giả định điều này nên rẻ nhưng hỏng khi …; hướng B trả giá tính toán để bỏ giả định đó."* Mỗi mệnh đề trong đó gắn với công trình sinh ra nó.

### 6.2 Mạch của bài học

0. **Nền tảng tối thiểu.** Vì chủ đề mới, chương đầu dựng lại từ đầu đúng những khái niệm cần để đọc phần sau — không nhiều hơn. Cái gì cây học tập đã có thì trỏ sang bằng đường dẫn tương đối, không chép lại.
1. **Đặt vấn đề và lịch sử ngắn**: bài toán gốc, ai gặp phải, vì sao các cách trước không đủ, mốc nào đã đổi cách nghĩ của lĩnh vực.
2. **Khung ký hiệu thống nhất.** Bắt buộc, và phải làm sớm: mỗi nhóm dùng ký hiệu khác nhau, nên bài học phải chọn **một** hệ ký hiệu và kèm **bảng đối chiếu** ký hiệu của từng công trình sang hệ đó. Không có bảng này thì các công thức của các tác giả khác nhau không ghép được, và mọi so sánh về sau đều là so sánh mù.
3. **Các trường phái và ý tưởng lõi**, trình bày theo trật tự khái niệm: ý đơn giản trước, ý tổng quát sau; mỗi ý gắn với công trình khai sinh ra nó, và nói rõ nó ra đời để chữa khuyết điểm nào của ý trước.
4. **Suy dẫn các công thức then chốt.** Giữ những bước làm lộ ra *vì sao* phương pháp chạy được, bỏ biến đổi đại số thuần tuý. Mỗi công thức mượn ghi rõ nguồn và số hiệu trong bản gốc, cộng một câu nói bước nào đã đổi ký hiệu.
5. **Bằng chứng thực nghiệm**, dạng bảng: ai đo, trên bộ dữ liệu nào, phần cứng gì, chỉ số gì, con số bao nhiêu, so với baseline nào. Ghi rõ khi các con số **không so sánh được với nhau** vì khác điều kiện — đây là trường hợp phổ biến và là chỗ dễ tự lừa mình nhất.
6. **Bất đồng chưa giải quyết**: các nhóm mâu thuẫn nhau ở đâu, bằng chứng nghiêng về bên nào, và vì sao chưa ngã ngũ. Một bài tổng hợp không nêu được bất đồng thực sự nào là dấu hiệu chưa đọc đủ.
7. **Giới hạn và chế độ hỏng** của cả lĩnh vực, không chỉ của từng phương pháp.
8. **Khoảng trống → giả thuyết**: câu hỏi dẫn đường nào chưa ai trả lời, và câu hỏi nghiên cứu nào của tôi mọc ra từ đó. Đây là cầu nối sang `research/`.
9. **Đọc thêm**, chia tầng: nhóm **nền tảng** phải đọc để hiểu đến gốc, nhóm **tra khi cần**.

### 6.3 Trích dẫn tại chỗ — quy tắc cứng

**Mỗi ý mượn, mỗi công thức, mỗi hình, mỗi con số đều mang trích dẫn ngay tại câu chứa nó**, kèm định vị đủ để mở đúng trang:

> Ý tưởng tích phân trước các phép đo IMU trên đa tạp để tránh tích phân lại khi trạng thái đổi đến từ \cite{forster2017preintegration} (mục IV-A); công thức (12) dưới đây chép từ eq. (30) của công trình đó, đã đổi sang ký hiệu ở Bảng 1. Con số 2,1 cm là APE trung vị họ báo trên EuRoC MH\_01 với cấu hình stereo-inertial \cite[Bảng III]{campos2021orbslam3}, không phải kết quả của tôi.

Hệ quả trực tiếp: **câu không có trích dẫn mặc định là lời của tôi** — nên phải đúng là như vậy. Dồn hết trích dẫn xuống mục "Đọc thêm" ở cuối là vô dụng, vì một năm sau tôi sẽ không biết câu nào là của ai.

Dùng ba nhãn xuyên suốt và không được trộn trong cùng một câu:

- **[Đ]** tác giả **đo được** (có số, có điều kiện thí nghiệm);
- **[T]** tác giả **tuyên bố hoặc suy luận** nhưng không đo trực tiếp;
- **[M]** **tôi** suy ra, hoặc tôi ghép từ nhiều nguồn — kể cả khi ghép nghe rất hiển nhiên.

### 6.4 Hai điều cấm

**Không chép nguyên văn.** Diễn đạt lại bằng ngôn từ của mình là phần việc tạo ra hiểu biết; chép lại tạo ra ảo giác hiểu. Khi bắt buộc phải giữ nguyên văn (định nghĩa chuẩn, tuyên bố cần trích chính xác để phê phán), đặt trong ngoặc kép kèm trang.

**Không bỏ trống câu hỏi dẫn đường.** Câu hỏi nào tài liệu không trả lời được thì viết thẳng *"chưa có công trình nào trả lời câu hỏi này"* — đó chính là khoảng trống nghiên cứu, và nó có giá trị hơn một đoạn văn lấp chỗ.

---

## 7. Bước 5 — Từ bài học sang nghiên cứu

`00-question.md` mở đầu mọi dự án nghiên cứu và ghi rõ: **câu hỏi** một câu, đủ cụ thể để có đáp án đúng/sai; **giả thuyết hiện tại kèm mức tin bằng số** (*tin khoảng 60 %*) — ghi số buộc tôi trung thực với chính mình; **điều gì sẽ chứng minh tôi sai**, viết trước khi chạy; **vì sao đáng trả lời và ai đã trả lời gần giống** (trỏ thẳng vào mục 8 của bài học). Cập nhật mức tin theo thời gian kèm ngày và lý do — đường đi của niềm tin cho thấy bằng chứng nào thực sự có sức thuyết phục.

**Viết `hypothesis.md` trước khi chạy** thí nghiệm: dự đoán kết quả, kết quả nào bác bỏ giả thuyết, biến nào được kiểm soát. Dự đoán viết trước là hàng rào duy nhất ngăn việc tự thuyết phục mình sau khi đã nhìn thấy số.

**Thí nghiệm đánh số tăng dần, không sửa lại thí nghiệm cũ.** Sai thì chạy `exp-005` mới và ghi trong đó vì sao `exp-004` không dùng được. Ghi đủ để tái lập: commit hash, seed, phiên bản dữ liệu, cấu hình đầy đủ, phần cứng.

**Baseline trước, phương pháp sau.** Rất nhiều cải tiến biến mất khi baseline được chỉnh tử tế; nếu baseline của tôi yếu hơn số công bố trong bài gốc thì sửa baseline trước đã.

**Ghi cả kết quả âm** trong `analysis.md`: điều gì đã không xảy ra. Đây là phần hay bị bỏ nhất và tốn kém nhất khi mất.

**Trước khi tin một kết quả**, kiểm theo thứ tự: có rò rỉ dữ liệu không; có ổn định qua nhiều seed không; chênh lệch có lớn hơn nhiễu chạy-tới-chạy không; có yếu tố nào ngoài phương pháp giải thích được nó không. Kết quả bất ngờ theo hướng có lợi cho mình phải bị nghi ngờ mạnh hơn kết quả bất lợi.

**Khi có sự cố kỹ thuật cần truy nguyên** — hệ thống hỏng, số liệu mâu thuẫn — dùng khung năm bước: *hiện tượng* (quan sát được gì, điều kiện nào, tái lập được không) → *truy nguyên* xuống tới ràng buộc gốc (giới hạn vật lý, observability, nhiễu, degeneracy, lỗi cài đặt), dừng khi chạm tầng không hỏi tiếp được → *cơ chế đề xuất* giải thích vì sao cách sửa chạm đúng nguyên nhân → *đánh đổi* được gì mất gì → *kiểm chứng* bằng một phép đo xác nhận nguyên nhân gốc đã hết, không phải triệu chứng đã biến mất.

`journal.md` chỉ ghi thêm, không sửa, không xoá: mỗi mục có ngày, hôm nay làm gì, kết quả ra sao, hiểu biết đổi thế nào, mai làm gì. Giá trị của nó nằm ở chỗ ghi lại **tôi đã nghĩ gì tại thời điểm đó**, kể cả những suy nghĩ về sau hoá ra sai; trí nhớ sẽ tự viết lại lịch sử theo hướng tôi luôn đúng, nhật ký thì không.

---

## 8. Khi giao việc tìm kiếm và tổng hợp cho agent

Agent là công cụ mở rộng độ phủ, **không phải nguồn tri thức**. Nó đọc nhanh hơn tôi nhiều lần nhưng cũng bịa ra trích dẫn và con số một cách rất tự tin, nên phải ràng buộc chặt.

**Giao việc**: mỗi agent nhận **một cụm câu hỏi dẫn đường**, kèm từ khoá và biến thể, chỉ tiêu số lượng, tiêu chuẩn venue ở mục 4, và định dạng trả về. Chạy nhiều agent song song cho các cụm khác nhau thì rẻ và phủ rộng hơn một agent làm tất.

**Mỗi công trình agent trả về phải kèm**: entry bib đầy đủ (tác giả, tên bài, **tên venue viết đủ**, năm, DOI hoặc arXiv id); link mở được; mức tin A/B/C kèm lý do; một câu đóng góp thật sự; **định vị** (mục / số hiệu công thức / số hình) cho từng ý sẽ được dùng; và một trích đoạn nguyên văn ngắn làm bằng chứng rằng bài đó thực sự nói điều được gán cho nó.

**Cấm tuyệt đối**: bịa trích dẫn; bịa hoặc "ước lượng" con số thí nghiệm; đoán DOI; tóm tắt một bài chưa mở được toàn văn hoặc ít nhất abstract gốc. Thà trả về *"không tìm được"* còn hơn một entry trông hợp lý mà sai. Trước khi bất kỳ entry nào vào `refs.bib`, đối chiếu tên bài + năm + venue với trang gốc của nhà xuất bản hoặc arXiv.

**Kiểm chứng bắt buộc trước khi tin một bài học do agent soạn**, mỗi công thức lõi phải qua ít nhất một trong ba cửa: **(a)** tôi tự suy dẫn lại; **(b)** kiểm bằng một ví dụ số nhỏ tính tay hoặc bằng vài dòng code; **(c)** đối chiếu với hai nguồn độc lập. Kèm theo bài học một checklist ghi rõ công thức nào đã qua cửa nào.

**Trách nhiệm cuối cùng là của tôi.** Các bài nền tảng phải chính tôi đọc tới lượt ba. Không ký tên vào một bài học dựng trên tóm tắt của agent mà tôi chưa mở lấy một bản gốc nào.

---

## 9. Trung thực trong trình bày

- Phân biệt rạch ròi ba mức **đã đo được / suy ra từ số liệu / phỏng đoán**, dùng từ ngữ khác nhau và không trộn chúng trong cùng một câu (đây là các nhãn [Đ], [T], [M] ở mục 6.3 áp dụng cho chính kết quả của tôi).
- Nêu giới hạn ngay trong phần chính, không đẩy hết xuống cuối: người đọc phải biết phạm vi áp dụng **trước khi** tin kết quả.
- Không tuyên bố vượt quá bằng chứng: *"cải thiện 2 điểm trên tập X trong điều kiện Y"* khác hẳn *"phương pháp tốt hơn"*.
- Trích dẫn đúng nguồn gốc của ý tưởng, kể cả khi nguồn đó bất tiện cho lập luận của tôi.
- Khi kết quả của tôi mâu thuẫn với công trình đã công bố, nói rõ điều đó **và** trình bày cả khả năng tôi mới là bên sai.

---

## 10. Chuẩn kỹ thuật

- LaTeX compile được ngay; UTF-8 và tiếng Việt đúng (XeLaTeX/LuaLaTeX với `fontspec`). Bài học dùng cùng bộ `preamble/` và quy ước `subfiles` như cây học tập.
- Thuật ngữ giữ tiếng Anh, hoặc *tiếng Việt (English)* ở lần đầu xuất hiện, sau đó nhất quán.
- Văn xuôi liền mạch theo chuẩn học thuật; bullet chỉ cho thứ thực sự là danh sách.
- Danh mục tham khảo sinh từ `refs.bib` qua `biblatex`, không gõ tay. Mỗi entry có DOI hoặc link ổn định, và một trường ghi mức tin A/B/C.
- Hình sinh bằng script từ dữ liệu thô, không chỉnh tay; script nằm cạnh hình.
- Code, config, bản thảo cùng một repo git; mỗi con số trong bản thảo truy được về một commit và một thư mục `experiments/`.
- Dữ liệu lớn để ngoài git, ghi checksum và cách lấy lại.

---

## 11. Tiêu chuẩn hoàn thành

Một **bài học khảo sát** xong khi: đủ chỉ tiêu nguồn ở mục 3 và có `search-log.md` tái lập được; mọi câu hỏi dẫn đường đều được trả lời hoặc được tuyên bố là còn bỏ ngỏ; có bảng đối chiếu ký hiệu; mọi ý mượn, công thức, con số đều có trích dẫn tại chỗ kèm định vị; ba nhãn [Đ]/[T]/[M] dùng nhất quán; nêu được ít nhất một bất đồng thực sự giữa các nhóm; kết bằng khoảng trống và giả thuyết; và người đọc chưa biết gì về chủ đề vẫn đi được từ đầu tới cuối nhờ chương nền tảng.

Một **kết quả nghiên cứu** đáng tin khi: có `hypothesis.md` viết trước; tái lập được từ commit + seed + config; baseline không yếu hơn số công bố gốc; chênh lệch lớn hơn nhiễu qua nhiều lần chạy; kết quả âm được ghi lại; và mọi khẳng định phân biệt rõ đo được với phỏng đoán.

Chưa đủ thì đánh dấu `% TODO` ở đầu file kèm điều còn thiếu. Tài liệu dở dang thừa nhận là dở dang thì vẫn dùng được; tài liệu dở dang giả vờ hoàn chỉnh thì gây hại.

---

## 12. Nguồn của chính các quy tắc trên

- S. Keshav, *How to Read a Paper*, ACM SIGCOMM Computer Communication Review, 2007 — nguồn của phương pháp đọc ba lượt ở mục 5.
- C. Wohlin, *Guidelines for Snowballing in Systematic Literature Studies and a Replication in Software Engineering*, EASE 2014 — nguồn của giao thức lăn cầu tuyết lùi/tới và tiêu chí bão hoà ở mục 3.
- CORE Conference Ranking (portal chính thức) và SCImago Journal Rank — nguồn của thang xếp hạng venue ở mục 4; DOAJ và các danh sách kế thừa danh sách Beall dùng để nhận diện tạp chí săn phí.
- Hướng dẫn *synthesis matrix* của các thư viện đại học (Duke, Williams, FIU) — nguồn của ma trận tổng hợp và quy tắc "viết theo cột thay vì theo hàng" ở mục 6.1.
- S. Ahrens, *How to Take Smart Notes*, 2017, hệ thống hoá phương pháp Zettelkasten của Niklas Luhmann — nguồn của quy tắc viết ghi chú bằng lời của mình ở mục 5 và điều cấm chép nguyên văn ở mục 6.4.
