# Quy tắc: Kho tài liệu học tập

Mục đích của kho này là xây một **cây tri thức** có thể đọc lại sau nhiều năm và vẫn hiểu được mạch suy nghĩ, chứ không phải một tập ghi chú rời rạc. Mỗi tài liệu phải đọc được như một chương luận văn: có mở đầu, có mạch phát triển, có kết luận.

Hai điều quyết định kho này có dùng được hay không. Thứ nhất, **mỗi khẳng định quan trọng phải truy được về một nguồn thật** — phần lớn nội dung ở đây được soạn với sự trợ giúp của mô hình ngôn ngữ, và mô hình sai một cách rất tự tin; một ý sai lặng lẽ nằm trong cây sẽ làm hỏng mọi thứ dựng lên trên nó. Thứ hai, **ghi chú phải là sản phẩm của việc suy nghĩ, không phải của việc chép lại**: chép lại tạo ảo giác hiểu, và ảo giác đó chỉ vỡ ra khi đã quá muộn.

Việc khảo sát tài liệu và tổng hợp một chủ đề mới từ các công trình gốc thuộc về `research-rules.md`. Kho này lưu thứ đã hiểu và đã sắp xếp xong.

---

## 1. Cấu trúc cây thư mục

Thư mục là bản đồ tư duy được vật chất hoá. Folder cha là một phạm trù lớn; folder con là một nhánh của phạm trù đó; độ sâu không giới hạn, đi đến đâu chủ đề còn tách được thành nhánh có nghĩa.

```
math/                                  # BIG TOPIC
├── math.tex                           # master: gộp toàn nhánh thành 1 PDF liền mạch
├── math.pdf
├── 00-map.tex                         # bản đồ nhánh: có gì, vì sao, đọc theo thứ tự nào
├── refs.bib                           # bibliography dùng chung cho cả nhánh
├── preamble/
│   └── common.tex                     # style, macro, tcolorbox, font tiếng Việt
│
├── 01-linear-algebra/                 # TOPIC
│   ├── linear-algebra.tex
│   ├── linear-algebra.pdf
│   ├── 00-map.tex
│   │
│   ├── 01-vector-spaces/              # SUBTOPIC
│   ├── 02-eigendecomposition/
│   └── 03-svd/
│       ├── svd.tex
│       ├── svd.pdf
│       ├── figures/
│       └── code/                      # notebook/script tự kiểm chứng
│
├── 02-probability/
└── 03-optimization/
```

**Quy tắc bắt buộc:**

- Tên folder: `NN-ten-chu-de` viết thường, gạch nối, có số thứ tự phản ánh **thứ tự nên đọc**, không phải thứ tự bạn học được.
- Mỗi folder — kể cả folder cha — phải có `00-map.tex`. Đây là file quan trọng nhất của cây: nó nói nhánh này gồm những gì, **vì sao lại chia như vậy**, nhánh nào phụ thuộc nhánh nào, và nên đọc theo trình tự nào. Không có file này thì cây chỉ là thư mục, không phải bản đồ tư duy.
- Mỗi folder có đúng một file `.tex` cùng tên với folder — đó là bản văn chính của chủ đề. Không rải nội dung ra nhiều file nhỏ trong cùng một cấp.
- Muốn tách nội dung thì **tạo folder con**, không tạo thêm file ngang cấp. Cấu trúc file phải trùng khít với cấu trúc khái niệm.
- Khi một subtopic phình to đến mức có nhánh con riêng, nâng nó lên thành folder có `00-map.tex` của chính nó. Cây lớn dần theo hiểu biết.

**Liên kết ngang:** khái niệm ở nhánh này thường phụ thuộc nhánh khác (SVD cần eigendecomposition; PCA ở `machine-learning/` cần SVD). Ghi rõ dependency ở đầu mỗi tài liệu dưới dạng đường dẫn tương đối, và dùng `\hyperref` khi compile chung. Không sao chép nội dung sang chỗ khác — chỉ trỏ về nguồn duy nhất.

---

## 2. Văn phong: viết như luận văn

Đây là điều khác biệt cốt lõi so với ghi chú thông thường.

- **Mặc định là văn xuôi liền mạch.** Mỗi tài liệu là một lập luận có mở — thân — kết, đọc từ đầu đến cuối thì hiểu được toàn bộ câu chuyện. Không viết thành danh sách gạch đầu dòng rời rạc.
- **Câu phải nối được với nhau.** Dùng liên từ chỉ quan hệ logic: *do đó*, *ngược lại*, *điều này dẫn tới*, *tuy nhiên vẫn còn vấn đề*. Người đọc sau ba năm phải theo được vì sao ý sau nối tiếp ý trước.
- **Bullet chỉ dùng cho những gì thực sự là danh sách:** liệt kê điều kiện, các bước của một thuật toán, các trường hợp phân loại. Không dùng bullet để né việc viết câu hoàn chỉnh.
- **Mỗi tài liệu mở đầu bằng một đoạn đặt vấn đề**, dài chừng một trang: bài toán gốc là gì, ai gặp phải, vì sao các cách tiếp cận trước không đủ. Không bắt đầu bằng định nghĩa.
- **Kết bằng một đoạn tổng kết** nói rõ ta đã đi được tới đâu, còn bỏ ngỏ điều gì, và nhánh nào nên đọc tiếp.
- Thuật ngữ chuyên môn: giữ tiếng Anh, hoặc dạng *tiếng Việt (English)* ở lần xuất hiện đầu tiên — *phân rã giá trị kỳ dị (singular value decomposition)*. Sau đó dùng nhất quán một dạng trong cả tài liệu.

**Mạch chuẩn cho một tài liệu khái niệm:**

Đặt vấn đề → trực giác/hình học trước khi hình thức hoá → phát triển ý tưởng chính → hệ quả và ứng dụng → giới hạn và trường hợp hỏng → kết nối sang nhánh khác.

---

## 3. Ghi chú theo lối của người làm khoa học

Cách ghi chú tạo ra khác biệt lớn hơn nhiều so với việc học bao lâu. Ba thói quen dưới đây lấy từ những người đã để lại cả hệ thống ghi chép, và cả ba đều có chung một đặc điểm: **chúng buộc người ghi phải xử lý nội dung, không chỉ chuyển nó từ trang sách sang trang vở.**

**Viết bằng lời của chính mình, mỗi ghi chú đứng độc lập được.** Niklas Luhmann phân biệt ghi chú thoáng qua (fleeting), ghi chú đọc (literature) và ghi chú vĩnh viễn (permanent); chỉ loại thứ ba mới vào kho, và nó được viết cẩn thận như thể sắp công bố, tự nó đọc được mà không cần mở lại tài liệu gốc, đồng thời **liên kết** sang các ghi chú khác — cách trình bày này do Sönke Ahrens hệ thống hoá. Trong cây của tôi, mỗi file `.tex` chính là một ghi chú vĩnh viễn, và mục "liên kết ngang" ở phần 1 chính là phần liên kết. Hệ quả thực tế: **cấm chép nguyên văn**. Nếu không diễn đạt lại được bằng lời của mình thì tức là chưa hiểu, và việc chép lại chỉ giấu chỗ chưa hiểu đó đi.

**Giữ một sổ những điều chưa biết.** Khi làm nghiên cứu sinh ở Princeton, Feynman mở một quyển vở mới và viết ngoài bìa *"NOTEBOOK OF THINGS I DON'T KNOW ABOUT"*, rồi tháo tung từng nhánh vật lý ra, tìm chỗ ráp không khít và chỗ chính mình chỉ hiểu hời hợt — chi tiết này do James Gleick kể lại trong tiểu sử *Genius*. Tôi giữ đúng cơ chế đó: mỗi folder có `99-chua-biet.md` liệt kê những chỗ tôi biết là mình không hiểu, viết dưới dạng **câu hỏi cụ thể** chứ không phải chủ đề chung chung (*"vì sao ma trận thông tin ở đây suy biến khi vận tốc bằng không?"*, không phải *"observability"*). Đây là danh sách công việc học tập, và nó chỉ hữu ích khi được thu ngắn dần: mục nào giải quyết xong thì chuyển thành một mục trong bài chính và ghi ngày.

**Tự giải thích trong lúc đọc, không phải sau khi đọc.** Chi và cộng sự cho thấy người tự giải thích từng đoạn trong lúc đọc hiểu sâu hơn hẳn nhóm đối chứng, vì việc giải thích làm lộ ra chỗ trống trong kiến thức của chính mình. Trong thực hành, cứ sau mỗi bước suy dẫn quan trọng thì dừng lại và viết một câu trả lời cho *"vì sao bước này hợp lệ?"* ngay tại chỗ, trong bài — đó cũng là lý do văn phong ở phần 2 bắt buộc là văn xuôi có lập luận chứ không phải danh sách công thức.

**Những câu hỏi bắt buộc phải trả lời được trước khi coi một khái niệm là đã ghi xong.** Đây là bộ khung áp cho mọi tài liệu; nó không phải một mục riêng trong file, mà là thứ nội dung phải thoả:

1. Bài toán gốc là gì, ai gặp phải nó, và trước đó người ta làm sao?
2. Ý tưởng lõi giải thích trong năm câu là gì — nếu chỉ được giữ một câu thì giữ câu nào?
3. **Giả thiết nào đang được dùng**, kể cả giả thiết ngầm không ai nói ra?
4. **Bỏ đi một giả thiết thì hỏng ở đâu**, hỏng như thế nào, và có nhận ra được lúc nó hỏng không?
5. Vì sao lại làm theo cách này mà không phải cách hiển nhiên hơn — cách hiển nhiên hỏng ở chỗ nào?
6. Đại lượng nào đo được, đại lượng nào chỉ suy ra, và suy ra bằng giả định gì?
7. Ví dụ nhỏ nhất tính tay được là gì, và kết quả có đúng như dự đoán không?
8. Điều gì sẽ chứng minh cách hiểu hiện tại của tôi là sai?
9. Cái này liên hệ thế nào với thứ tôi đã biết ở nhánh khác — giống chỗ nào, khác chỗ nào?
10. Tôi lấy điều này từ đâu, và nguồn đó đáng tin tới mức nào?

Câu 3, 4, 8 và 10 là bốn câu hay bị bỏ nhất, và cũng là bốn câu phân biệt một tài liệu học thật với một bản tóm tắt trôi chảy.

---

## 4. Kỹ thuật học — chọn theo bằng chứng, không rập khuôn

Không phải kỹ thuật học nào cũng có giá trị ngang nhau. Khảo sát của Dunlosky và cộng sự (*Psychological Science in the Public Interest*, 2013) đánh giá mười kỹ thuật phổ biến và xếp **luyện tập truy hồi (practice testing)** cùng **học giãn cách (distributed practice)** ở mức hữu ích cao nhất, trong khi tô đậm (highlighting), đọc lại (rereading) và tóm tắt bị xếp mức thấp — đúng những kỹ thuật cảm giác dễ chịu nhất khi làm. Tự giải thích (self-explanation), chất vấn tinh tiết (elaborative interrogation) và học xen kẽ (interleaving) nằm ở mức trung bình nhưng hợp với loại tài liệu ở kho này.

**Luyện tập truy hồi** — cuối mỗi tài liệu có 3–7 câu hỏi phải tự trả lời **không nhìn bài**. Roediger và Karpicke (2006) cho thấy: nếu kiểm tra ngay sau khi học thì đọc lại có vẻ tốt hơn, nhưng ở mốc hai ngày và một tuần thì việc đã tự truy hồi cho kết quả tốt hơn hẳn đọc lại. Nghĩa là cảm giác "đọc lại thấy nhớ hơn" là một ảo giác ngắn hạn. Câu hỏi phải hỏi *vì sao* và *khi nào hỏng*, không hỏi *định nghĩa là gì*.

**Học giãn cách** — ghi ngày ôn gần nhất ở đầu mỗi file. Cepeda và cộng sự (2006) tổng hợp 317 thí nghiệm và thấy khoảng cách ôn tối ưu **tăng theo thời gian mình muốn nhớ**: muốn nhớ vài tháng thì khoảng cách vài tuần, không phải vài ngày; lịch giãn dần tốt hơn lịch đều. Thực hành: ôn lần đầu sau vài ngày, rồi hai tuần, rồi hai tháng, rồi nửa năm — mỗi lần ôn là một lần trả lời bộ câu hỏi cuối bài, không phải đọc lại bài.

**Học xen kẽ** — khi ôn, trộn các nhánh khác nhau thay vì đi tuần tự một mạch. Cây thư mục giúp việc này: chọn ngẫu nhiên vài `00-map.tex` rồi tự kiểm tra chéo.

**Kỹ thuật Feynman** — viết lại khái niệm bằng ngôn ngữ đơn giản như đang giảng cho người chưa biết, đến khi không còn chỗ nào phải nói "cái này phức tạp lắm". Dùng khi thấy mình hiểu mơ hồ, hoặc khi khái niệm là nền móng cho nhiều nhánh khác. Không dùng cho nội dung thuần định nghĩa/quy ước; và không cần một hộp "Giải thích kiểu Feynman" ở mọi trang.

**Nguyên tắc 80/20** — ở `00-map.tex`, đánh dấu rõ nhánh nào là **cốt lõi** (phải nắm chắc, quay lại nhiều lần) và nhánh nào là **tham khảo** (biết là có, tra khi cần). Phần cốt lõi viết kỹ; phần tham khảo viết ngắn kèm nguồn ngoài. Không viết mọi nhánh với cùng độ sâu.

**Ví dụ nhỏ nhất tính tay được** — mỗi khái niệm quan trọng nên có một ví dụ đủ nhỏ để tính bằng tay (ma trận 2×2, ba điểm dữ liệu). Ví dụ nhỏ giữ trí nhớ mạnh hơn công thức tổng quát, và nó còn là công cụ kiểm chứng ở phần 5.

**Tư duy sâu thay vì tư duy nông** — thể hiện bằng chất lượng lập luận trong văn xuôi, không phải bằng một mục riêng tên "Tư duy sâu". Tài liệu chỉ mô tả *cái gì* và *làm thế nào* mà không có *vì sao* thì chưa xong.

---

## 5. Trích dẫn và kiểm chứng: chống kiến thức sai lọt vào cây

Phần lớn nội dung ở đây được soạn cùng mô hình ngôn ngữ, và mô hình có hai kiểu sai nguy hiểm: nói một điều sai bằng giọng chắc chắn, và **bịa ra nguồn** trông rất giống thật. Vì vậy kho học tập áp dụng cùng chuẩn truy nguồn như kho nghiên cứu, chỉ nhẹ hơn về khối lượng.

**Ba loại khẳng định bắt buộc phải có trích dẫn ngay tại chỗ** — trong thân bài, ở đúng câu chứa nó, không dồn xuống cuối:

1. **Con số**: bất kỳ hằng số, kết quả thực nghiệm, ngưỡng, độ phức tạp hay so sánh định lượng nào. Ghi kèm điều kiện đo, vì con số không có điều kiện là con số vô nghĩa.
2. **Công thức và định lý không tầm thường**: ghi rõ nguồn và **số hiệu công thức trong bản gốc** (*"chép từ eq. (30) của \cite{...}, đã đổi ký hiệu"*), để sau này kiểm lại mà không phải đọc lại cả bài.
3. **Khẳng định về việc "người ta làm thế nào" hay "cách này tốt hơn cách kia"**: đây là loại mô hình bịa nhiều nhất, vì nó nghe hợp lý và không ai kiểm.

Ngược lại, những suy dẫn chuẩn trong sách giáo khoa và các bước trung gian tự làm được thì không cần trích dẫn — trích dẫn dày đặc cho thứ hiển nhiên cũng làm mất tác dụng cảnh báo của trích dẫn. **Câu không có trích dẫn mặc định là lời của tôi**, nên phải đúng là như vậy; chỗ nào tôi tự suy ra mà chưa kiểm được với nguồn nào thì ghi rõ *(tôi suy ra, chưa đối chiếu nguồn)*.

**Ba cửa kiểm chứng.** Mỗi công thức lõi và mỗi khẳng định cơ chế phải qua ít nhất một cửa, và ghi lại đã qua cửa nào:

- **(a)** tôi tự suy dẫn lại được từ đầu;
- **(b)** kiểm bằng một ví dụ số nhỏ — tính tay hoặc vài dòng code trong `code/` cạnh bài — kể cả chỉ kiểm trường hợp giới hạn, thứ nguyên, hoặc dấu;
- **(c)** đối chiếu với **hai nguồn độc lập** (không cùng nhóm tác giả, không cái này trích cái kia).

Cửa (b) rẻ và bắt được phần lớn lỗi do mô hình sinh ra: một công thức bịa hầu như luôn sai ở trường hợp đơn giản nhất.

**Kiểm nguồn trước khi đưa vào `refs.bib`.** Mở link, đối chiếu tên bài, tác giả, năm và venue với trang gốc của nhà xuất bản hoặc arXiv. Không đoán DOI. Không đưa vào một entry mà tôi chưa mở được ít nhất abstract gốc. Một nguồn bịa nằm im trong cây nhiều năm rồi lộ ra đúng lúc tôi cần dựa vào nó là kịch bản tệ nhất.

**Nguồn phải có uy tín.** Ưu tiên bài đã qua phản biện ở hội nghị/tạp chí đầu ngành, sách giáo khoa chuẩn, hoặc bản tiền ấn của nhóm đã có công trình được kiểm chứng. Loại thẳng "paper rác": hội nghị/tạp chí săn phí, bản arXiv chưa ai kiểm chứng và không có mã nguồn, bài chỉ khoe số mà giấu điều kiện thí nghiệm, nội dung do mô hình ngôn ngữ sinh rồi đăng lại. Khi buộc phải dẫn một nguồn yếu vì chưa có gì tốt hơn, ghi ngay cạnh: *"chưa được kiểm chứng"*. Tiêu chí sàng lọc chi tiết (xếp hạng CORE/Scimago, ba mức tin A/B/C) nằm ở `research-rules.md` mục 4 — áp dụng chung, không chép lại ở đây.

**Đánh dấu thẳng thắn mức đọc.** Công trình mới chỉ xem abstract thì ghi `% chưa đọc kỹ` trong entry. Xếp một bài mình chưa đọc lẫn vào danh sách đã đọc là tự lừa mình ở lần đọc lại sau.

---

## 6. Hình vẽ, bảng, công thức

Ba thứ này phục vụ mạch văn, không thay thế nó.

**Hình vẽ (TikZ/PGFPlots):** dùng khi nội dung có bản chất không gian hoặc luồng — hình học của phép chiếu, pipeline có nhiều nhánh, quan hệ phụ thuộc. Không vẽ sơ đồ cho thứ một câu văn nói rõ hơn. Mỗi hình phải có caption tự đứng được và được nhắc đến trong văn bản (*"Hình 3 cho thấy..."*), không thả hình trôi nổi. Hình chép lại ý tưởng từ một công trình thì ghi nguồn trong caption.

**Bảng so sánh:** dùng khi có từ ba phương án trở lên cần đặt cạnh nhau trên cùng tiêu chí. Cột nên gồm: cơ chế, giả thiết, chi phí tính toán, chế độ hỏng, khi nào nên chọn. Với hai phương án thì một đoạn văn thường tốt hơn bảng.

**Công thức:** giữ những suy dẫn thực sự thay đổi cách hiểu, ví dụ chỗ một giả thiết được dùng đến hoặc chỗ lộ ra vì sao thuật toán hoạt động. Bỏ các bước biến đổi đại số thuần tuý — chỉ ghi kết quả và chỉ ra nguồn đầy đủ. Mỗi công thức quan trọng cần một câu diễn giải bằng lời ngay sau đó, và nếu mượn thì kèm số hiệu công thức trong bản gốc theo phần 5.

---

## 7. Chuẩn LaTeX

- Compile được ngay, không cần sửa. UTF-8 và tiếng Việt hoạt động đúng: `\usepackage[vietnamese]{babel}` với `fontspec` (biên dịch bằng XeLaTeX/LuaLaTeX).
- Dùng package `subfiles`: mỗi `.tex` con vừa compile độc lập ra PDF riêng, vừa được `math.tex` gộp lại thành một PDF liền mạch cho cả nhánh. Đây là điều kiện để đọc được dạng luận văn.
- Toàn bộ style, macro toán, định nghĩa `tcolorbox` đặt tập trung ở `preamble/common.tex`. Không định nghĩa lại rải rác.
- Hộp `tcolorbox` dùng tiết chế, chỉ cho ba loại: **Trực giác** (mô hình tư duy trước khi hình thức hoá), **Cạm bẫy** (lỗi thường gặp, hiểu nhầm phổ biến), **Cần nhớ** (điều duy nhất phải mang theo nếu quên hết phần còn lại). Quá ba loại hộp thì trang giấy trở thành nhiễu thị giác.
- Bibliography tập trung ở `refs.bib` cấp folder cha, dùng `biblatex`; entry có DOI hoặc link ổn định.
- Đầu mỗi file ghi metadata dạng comment: ngày tạo, lần sửa gần nhất, **lần ôn gần nhất**, dependency, mức độ (cốt lõi/tham khảo), và trạng thái kiểm chứng của các công thức lõi (cửa a/b/c ở phần 5).

---

## 8. Mục "Đọc thêm" ở cuối mỗi tài liệu

Một chương viết xong vẫn chưa đủ nếu người đọc muốn đi sâu hơn mà không biết đi đâu. Vì vậy **mỗi tài liệu kết thúc bằng một mục "Đọc thêm"** liệt kê các công trình gốc đã dùng, để lần sau có thể lần ngược về nguồn thay vì tin vào trí nhớ của chính mình.

Mỗi mục ghi đủ bốn thông tin: **tên công trình**, **tác giả**, **nơi công bố** (hội nghị hoặc tạp chí — CVPR, ICRA, T-RO, NeurIPS…; nếu chỉ có bản tiền ấn thì ghi rõ *arXiv preprint*), và **năm công bố**. Thiếu nơi công bố và năm thì trích dẫn vô dụng: không phân biệt được bài nền tảng ba mươi năm tuổi với một bản nháp chưa qua phản biện.

Kèm mỗi công trình một câu nói **vì sao nên đọc nó và đọc phần nào** — *"đọc mục III để thấy suy dẫn đầy đủ của công thức (4)"*. Danh sách không chú thích chỉ là trang trí học thuật.

Chia theo mức ưu tiên đúng tinh thần 80/20: nhóm **nền tảng** phải đọc nếu muốn hiểu chương này đến gốc, nhóm **tra khi cần** chỉ mở khi gặp đúng tình huống.

Ràng buộc còn lại: danh sách sinh từ `refs.bib` qua `biblatex`, không gõ tay. Mục này là bản đồ đường đi tiếp, **không phải nơi trả nợ trích dẫn** — trích dẫn tại chỗ đã làm ở phần 5. Nếu chương thực sự không dựa vào nguồn ngoài nào — nội dung tự suy ra hoặc là kiến thức chuẩn trong sách giáo khoa — thì viết một câu nói rõ điều đó và trỏ về quyển sách chuẩn tương ứng; mục trống không phân biệt được giữa "không có nguồn" và "quên ghi nguồn".

---

## 9. Tiêu chuẩn hoàn thành

Một tài liệu được coi là xong khi thoả cả bảy điều:

1. Đọc liền mạch từ đầu đến cuối mà không cần tra cứu bên ngoài để hiểu mạch chính.
2. Trả lời được mười câu hỏi ở phần 3 — đặc biệt là giả thiết, chỗ hỏng khi bỏ giả thiết, và điều gì sẽ chứng minh cách hiểu này sai.
3. Có ít nhất một ví dụ nhỏ tính tay được.
4. Mọi con số, công thức mượn và khẳng định "người ta làm thế nào" đều có trích dẫn tại chỗ; mọi công thức lõi đã qua ít nhất một cửa kiểm chứng và ghi rõ là cửa nào.
5. Nêu rõ giới hạn và trường hợp phương pháp hỏng.
6. Nối được vào cây: có dependency trỏ lên, có gợi ý đọc tiếp trỏ xuống hoặc sang ngang, và những chỗ chưa hiểu đã được chuyển vào `99-chua-biet.md`.
7. Có bộ câu hỏi tự kiểm cuối bài, có ngày ôn gần nhất ở đầu file, và có mục "Đọc thêm" đủ tên công trình, tác giả, nơi công bố, năm.

Chưa đủ bảy điều thì đánh dấu `% TODO` ở đầu file và ghi rõ còn thiếu gì. Tài liệu dở dang được thừa nhận là dở dang thì vẫn dùng được; tài liệu dở dang giả vờ hoàn chỉnh thì gây hại.

---

## 10. Nguồn của chính các quy tắc trên

- J. Dunlosky, K. A. Rawson, E. J. Marsh, M. J. Nathan, D. T. Willingham, *Improving Students' Learning With Effective Learning Techniques: Promising Directions From Cognitive and Educational Psychology*, Psychological Science in the Public Interest, 2013 — xếp hạng mười kỹ thuật học ở phần 4.
- H. L. Roediger, J. D. Karpicke, *Test-Enhanced Learning: Taking Memory Tests Improves Long-Term Retention*, Psychological Science, 2006 — hiệu ứng truy hồi và ảo giác của việc đọc lại.
- N. J. Cepeda, H. Pashler, E. Vul, J. T. Wixted, D. Rohrer, *Distributed Practice in Verbal Recall Tasks: A Review and Quantitative Synthesis*, Psychological Bulletin, 2006 — khoảng cách ôn tối ưu tăng theo thời gian muốn nhớ.
- M. T. H. Chi và cộng sự, *Eliciting Self-Explanations Improves Understanding*, Cognitive Science, 1994 — cơ sở của việc tự giải thích trong lúc đọc ở phần 3.
- S. Ahrens, *How to Take Smart Notes*, 2017 — hệ thống hoá phương pháp Zettelkasten của Niklas Luhmann: ghi chú thoáng qua / ghi chú đọc / ghi chú vĩnh viễn, viết bằng lời của mình và liên kết với nhau.
- J. Gleick, *Genius: The Life and Science of Richard Feynman*, 1992 — quyển "Notebook of things I don't know about" ở phần 3.
- S. Keshav, *How to Read a Paper*, ACM SIGCOMM CCR, 2007 — phương pháp đọc ba lượt, dùng khi đọc nguồn cho một chương (chi tiết ở `research-rules.md`).
