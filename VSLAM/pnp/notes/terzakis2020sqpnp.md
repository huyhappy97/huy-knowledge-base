# A Consistently Fast and Globally Optimal Solution to the Perspective-n-Point Problem (SQPnP) — ghi chú đọc

| | |
|---|---|
| bibkey | `terzakis2020sqpnp` |
| Venue, năm | ECCV 2020, LNCS (khớp `refs.bib` về venue và năm; số trang LNCS 478–494 và DOI trong `refs.bib` **không kiểm được** từ bản này, vì bản ECVA đánh số trang 1–17) |
| Bản đã đọc | `papers/terzakis2020sqpnp.pdf` — bản open access của ECVA (theo lời giao việc), 17 trang: tr. 1–14 là bài, tr. 15–17 là tài liệu tham khảo. **Không có supplementary** trong file này, nên chứng minh của Mđ 1, 2, 4, 5, 6, 7 (đều "Provided in the supplementary material") tôi chưa đọc |
| Mức đọc | lượt 3 cho §2–§3 (dựng lại (2)–(14), Alg. 1–2, cài lại bằng numpy); lượt 2 cho §1, §4 |
| Người đọc | Claude (agent), 2026-09-25 — **Huy chưa đọc lại để ký** |
| Mức tin | giữ A cho **công thức** (2)–(7), (12) và thuật toán; **hạ tuyên bố "globally optimal"** xuống mức "tuyên bố có lập luận + kiểm thực nghiệm", vì phần được chứng minh (Mđ 3–6) không bao phủ thuật toán thật sự chạy (xem mục 8). Có hai lỗi trình bày: chỉ số ν trong eq. (14)/Alg. 1 lệch một, và điều kiện while của Alg. 1 thiếu hệ số 3 so với §2.1 |
| Kiểm chứng | (2)→(7): cửa (a) và (b). Mđ 3: cửa (a)+(b), **bác bỏ** nghĩa đen "lồi trong vùng 90°". Mđ 4: cửa (b), đạt (cận chặt là arccos(1/3) = 70.53°). "Luôn tìm được cực tiểu toàn cục": cửa (b) thực nghiệm, gần đúng nhưng **không tuyệt đối** (mục 7). Script `code/terzakis2020sqpnp_check.py` |

## 1. Bài toán gốc và bối cảnh

Bài giải PnP có hiệu chỉnh với n ≥ 3 [§1, tr. 1]. Tác giả chia các bộ giải trước đó thành ba nhóm và chê từng nhóm [§1.1, tr. 2–4]. Nhóm thứ nhất gồm EPnP (`lepetit2009epnp`), REPPnP (`ferraz2014reppnp`), MLPnP (`urban2016mlpnp`) và LHM (`lu2000orthogonal`). Theo bài, các bộ này "heuristic" và không xử lý cấu hình có nhiều cực tiểu như P3P hay P4P đồng phẳng [tr. 3]. Nhóm thứ hai là các bộ giải đa thức dựa trên điều kiện bậc một với tham số hoá xoay tối thiểu: DLS (`hesch2011dls`), OPnP (`zheng2013opnp`), optDLS (`nakano2015dls`). Bài chê rằng chúng không có giới hạn chặt về thời gian chạy [tr. 3]. Họ cũng nói DLS mang điểm kỳ dị của Cayley ở xoay 180° [tr. 3], và các bộ giải này phải thử cỡ 40 nghiệm [tr. 3]. Nhóm thứ ba là cách duy nhất trước đó coi PnP là QCQP, của Schweighofer–Pinz (`schweighofer2008sos`): nới lỏng SOS/SDP, được đánh giá là hiệu quả nhưng chậm, và cần xử lý riêng cho điểm đồng phẳng [§1.2, tr. 4].

Chỗ khó mà bài nhắm vào là có một bộ giải vừa tổng quát (mọi n, mọi cấu hình, kể cả đồng phẳng, không cần nhánh riêng), vừa tìm cực tiểu toàn cục, vừa có thời gian chạy bị chặn và chỉ dùng đại số tuyến tính chuẩn [§1.3, tr. 4].

## 2. Giả thiết — kể cả giả thiết ngầm; bỏ đi thì hỏng ở đâu

- **Camera đã hiệu chỉnh, điểm ảnh chuẩn hoá** m_i = [x_i y_i 1]ᵀ trên mặt Z = 1 [§1, tr. 1; Alg. 1, tr. 11]. Hàm (2) dựa vào thành phần thứ ba của m_i bằng 1, nên không áp dụng trực tiếp cho tia chiếu đơn vị f hay camera toàn hướng. Nếu điểm có z ≤ 0 trên tia (ví dụ fisheye > 180°) thì không biểu diễn được (tôi suy ra).
- **Hàm mục tiêu không phải sai số tái chiếu.** Bài nói (2) "stemming from" (1) [tr. 5], nhưng hai hàm này khác nhau. Tôi dẫn lại (cửa (a), kiểm số ở mục 7 [1]): vì m_i có thành phần z bằng 1 nên (m_i1_zᵀ − I)X_c = z_i m_i − X_c có thành phần thứ ba bằng 0. Do đó mỗi số hạng của (2) bằng z_i²‖m_i − π(X_c,i)‖², tức **sai số tái chiếu trên mặt chuẩn hoá có trọng số bằng bình phương độ sâu** (tôi suy ra). Hệ quả là điểm xa bị phạt nặng hơn điểm gần. Dưới nhiễu pixel Gauss đẳng hướng, cực tiểu của (2) không là ước lượng hợp lý cực đại, và "cực tiểu toàn cục" trong tựa bài là cực tiểu toàn cục **của hàm (2)**, không phải của (1) (tôi suy ra; mục 7 [6] đo độ lệch).
- **Không có ràng buộc cheirality trong bài toán tối ưu.** Cả (2) lẫn (8) đều không biết điểm nằm trước hay sau camera. Bài chỉ nói rằng khi có nhiều nghiệm (null space lớn, n ≤ 6) thì "positive depth test applies" [§2.3, tr. 10]. Với điểm đồng phẳng, phép đối xứng X_c → −X_c cho một phép xoay thật có cùng giá trị (2), vì −R·S với S là phép phản xạ qua mặt phẳng vật có det = +1. Như vậy luôn có một "song sinh" sau camera cùng cost (tôi suy ra; giống hiện tượng đã ghi trong `notes/lu2000orthogonal.md`). Mục 7 [4]: trong 506/2320 cảnh (`--full`), cực tiểu toàn cục không ràng buộc có độ sâu âm.
- **ΣQ_i khả nghịch** [Mđ 1, tr. 5]. Mỗi Q_i có hạng 2 với null vector là m_i, nên ΣQ_i khả nghịch khi và chỉ khi có ít nhất hai điểm ảnh phân biệt (tôi suy ra). Bài phát biểu Mđ 1 không kèm điều kiện.
- **rank(Ω) ≥ 3** là điều kiện của Mđ 7 để hệ SQP có nghiệm duy nhất [tr. 10]. Tôi nghĩ điều kiện đủ thật sự là Ω xác định dương trên không gian tiếp tuyến null(H_r), tức null(Ω) ∩ null(H_r) = {0}; rank(Ω) ≥ 3 chỉ là điều kiện cần về số chiều (tôi suy ra, chưa đọc chứng minh). Trong mọi lần chạy của tôi, hệ 15×15 không lần nào suy biến.
- **Nhiễu nhỏ không phải là giả thiết**, nhưng mọi thí nghiệm đều có n ≤ 10, xoay gần đơn vị và vật ở trước camera [§4.1, tr. 12].

## 3. Cơ chế — năm câu, rồi chi tiết có định vị

**Năm câu.** Nhân sai số tái chiếu với độ sâu cho hàm (2), vốn bậc hai theo cả vec(R) lẫn t. Nhờ vậy t tối ưu là hàm tuyến tính t = Pr, và cost còn lại là một dạng toàn phương rᵀΩr với Ω là ma trận 9×9 nửa xác định dương [eq. (5)–(7)]. Bài toán PnP trở thành cực tiểu rᵀΩr trên SO(3) nhúng trong mặt cầu bán kính √3 của R⁹ [eq. (8)]. Bỏ ràng buộc trực giao nhưng giữ ‖x‖² = 3 thì các điểm dừng là ±√3 e_j, với e_j là vector riêng của Ω [eq. (9)–(10)]. Thuật toán lấy rotation gần nhất với ±√3 e_9 (vector riêng có trị riêng nhỏ nhất) làm điểm khởi tạo, chạy SQP trên ràng buộc trực giao [eq. (12)–(13), Alg. 2], rồi chuyển lần lượt sang e_8, e_7, … khi cực tiểu tìm được chưa nhỏ hơn 3·s_j [§2.1, tr. 9].

**Chi tiết.**
- *Hàm mục tiêu* [eq. (2), tr. 5]: E² = Σ‖1_zᵀ(RM_i + t)m_i − (RM_i + t)‖², khoảng cách giữa điểm dựng lại z·m_i và điểm thật X_c trong hệ camera. Bài gọi đây là "back-projection error" và nói nó phổ biến, dẫn [17, 34] (`hesch2011dls`, `lu2000orthogonal`) [tr. 5]. Hàm của LHM thì khác: nó chiếu vuông góc lên tia nhìn, ‖(I − V̂)X_c‖², còn (2) đo song song với mặt ảnh (tôi suy ra).
- *Tuyến tính hoá theo r* [eq. (3), tr. 5]: r ∈ R⁹ là các **hàng** của R xếp chồng. A_i = blockdiag(M_iᵀ, M_iᵀ, M_iᵀ) ∈ R^{3×9}, nên RM_i = A_ir.
- *Dạng toàn phương* [eq. (4), tr. 5]: E² = Σ(A_ir + t)ᵀQ_i(A_ir + t), với Q_i = (m_i1_zᵀ − I₃)ᵀ(m_i1_zᵀ − I₃).
- *Khử t* [tr. 5, eq. (5)–(6)]: đạo hàm theo t bằng 0 cho (ΣQ_i)t = −(ΣQ_iA_i)r, nên t = Pr với P = −(ΣQ_i)⁻¹(ΣQ_iA_i). Khử được dạng đóng vì E² là đa thức bậc hai **đồng thời** theo (r, t). Điều đó đúng chính là nhờ bỏ phép chia cho độ sâu của (1) (tôi suy ra).
- *Ma trận dữ liệu* [eq. (7), tr. 6]: Ω = Σ(A_i + P)ᵀQ_i(A_i + P), và E² = rᵀΩr. Mỗi điểm góp hạng 2 và việc khử t lấy đi 3, nên rank Ω ≤ min(9, 2n − 3) (tôi suy ra; đo được 3, 5, 7, 9 cho n = 3, 4, 5, 6). Với điểm đồng phẳng, thành phần R·n (n là pháp tuyến mặt vật) không ảnh hưởng hiệu các điểm, nên null(Ω) ≥ 3 chiều với mọi n (tôi suy ra; đo được hạng 6 với n ≥ 5).
- *NLQP* [eq. (8), tr. 6]: min xᵀΩx với h(x) = 0₆, trong đó h gồm hai ràng buộc chuẩn hàng 1, 2, ba tích vô hướng giữa các hàng, và det(mat(x)) − 1. Chuẩn của hàng 3 bị bỏ vì thừa [tr. 6]. Chú thích 3 nói ràng buộc det bậc ba có thể thay bằng ba ràng buộc bậc hai để thành QCQP [tr. 6].
- *Mđ 2* [tr. 6]: rank(mat(x)) ≥ 2 thì Jacobian H_x có hạng 6, nên null(H_x) là không gian tiếp tuyến 3 chiều.
- *Nới lỏng lên mặt cầu* [eq. (9)–(10), tr. 7]: f(x) = xᵀΩx trên S⁸ bán kính √3 có 18 điểm dừng ±√3 e_j, với giá trị 3s_j. Từ đây có cận dưới chặt chẽ duy nhất trong bài, dù bài không phát biểu nó thành lời: mọi rotation đều có E² ≥ 3s₉ (tôi suy ra).
- *Mđ 3* [tr. 7]: f "lồi" trong vùng 90° quanh một cực tiểu địa phương. Chứng minh ba dòng nói điểm uốn gần nhất phải là một vector riêng khác, nên cách ít nhất 90°. Mục 8 giải thích vì sao phát biểu này sai theo nghĩa lồi trắc địa.
- *Mđ 4* [eq. (11), tr. 7]: rotation gần √3e nhất (bài toán NOMP) cách e dưới 71°, nên vùng 90° luôn chứa rotation.
- *Mđ 5–6* [tr. 7–8]: trong vùng 90° có đúng 4 ma trận trực giao ξ₁…ξ₄ là điểm tới hạn của khoảng cách tới √3e, và cực tiểu khả thi trong vùng đó đạt được bằng cách đi xuống từ ít nhất một ξ_i. Mđ 6 được trình bày là "đủ để đi an toàn tới cực tiểu toàn cục" [tr. 8]. Hình minh hoạ SO(2) ở [Fig. 2, tr. 8].
- *Chỉ dùng 2 trong 4 ξ*: "We empirically determined" rằng đi xuống từ hai điểm gần nhất là đủ [tr. 10]. Cụ thể là rotation gần √3e và rotation gần −√3e [eq. (13), tr. 10].
- *SQP* [eq. (12), tr. 9]: tại r, giải min δᵀΩδ + 2rᵀΩδ với H_rδ = −h(r). Hệ KKT được viết tường minh trong Alg. 2: [Ω H_rᵀ; H_r 0][δ; λ] = [−Ωr; −h(r)] [tr. 11]. Ma trận góc trên chỉ là Ω, **không** có số hạng Σλ_j∇²h_j của Hessian Lagrangian, nên đây không phải SQP–Newton đầy đủ. Hội tụ vì thế tuyến tính chứ không bậc hai (tôi suy ra; đo được ‖δ‖ giảm khoảng ×0.01–0.04 mỗi bước, mục 7).
- *Trường hợp tổng quát* [eq. (14), §2.3, tr. 10]: khi Ω có null space k chiều, lấy 2k điểm khởi tạo từ ± mỗi vector cơ sở của null space. Null space lớn (tới 6) ứng với n nhỏ (tới 6) [tr. 10].
- *Thuật toán* [Alg. 1–2, tr. 11]: ε ≤ 10⁻⁵, T ≥ 15. Bài nói "SQP typically converges within 10 iterations" [tr. 11]. Thí nghiệm dùng T = 15 và ε = 10⁻⁸ [chú thích 5, tr. 13]. NOMP được giải bằng FOAM, không dùng SVD [tr. 12].

## 4. Ký hiệu của bài ↔ ký hiệu của khảo sát

| Bài | Khảo sát | Ghi chú |
|---|---|---|
| M_i ∈ R³ | X_w,i | điểm thế giới |
| m_i = [x_i y_i 1]ᵀ | K⁻¹[u_i; 1] (chưa chuẩn hoá độ dài) | f_i = m_i/‖m_i‖ là tia đơn vị của khảo sát; bài dùng m_i, không dùng f_i |
| R, t với RM_i + t | R, t với X_c = RX_w + t | cùng quy ước; Fig. 1 nói t là vector từ tâm camera tới gốc thế giới [tr. 2] |
| r ∈ R⁹, mat(r) | vec theo **hàng** của R | trùng với `R.ravel()` của numpy (row-major); khác vec theo cột thường gặp trong sách |
| 1_z = [0 0 1]ᵀ | — | |
| A_i, Q_i, P, Ω | — | eq. (3), (4), (6), (7) |
| E² | cost (2) | = Σ z_i²‖m_i − π(X_c,i)‖² (tôi suy ra) |
| x ∈ R⁹, h(x), H_x | — | biến nới lỏng, ràng buộc, Jacobian |
| s_1 > … > s_9, e_1 … e_9 | — | trị riêng giảm dần; e_9 ứng với trị riêng **nhỏ nhất** |
| ξ₁…ξ₄ | — | nghiệm NOMP (điểm tới hạn) trong O(3) |
| f (focal, §4.1) | K[0,0] | trùng chữ với f(x) của eq. (9) |

## 5. Bằng chứng — dữ liệu, phần cứng, baseline, con số kèm điều kiện, số lần lặp

- **Chỉ có dữ liệu tổng hợp** [§4.1, tr. 12–14]. M_i ~ N([3/4, 3/4, 12]ᵀ, 3²I₃) (đơn vị mét). Vị trí camera b ~ N(0, 0.2²I₃) và tham số MRP ψ ~ N(0, 0.05²I₃) [eq. (15)]. Focal 1400 px, ảnh 1800×1800 [tr. 12]. Vì σ nhỏ nên xoay gần đơn vị và camera nhìn thẳng vào đám điểm. Bài không có dữ liệu thật và không có thí nghiệm đồng phẳng định lượng (chỉ có ảnh minh hoạ [Fig. 1(b)]).
- **Nhiễu và kích thước mẫu** [tr. 12]: phương sai nhiễu σ² ∈ {2, 5, 8, 11, 14, 17} px². Mỗi mức sinh 100 điểm; với mỗi n ∈ {4, …, 10} bốc 500 tập n điểm.
- **Thước đo** [Fig. 3, tr. 13]: **giá trị lớn nhất** của sai số tái chiếu bình phương (theo (1), không theo (2)) trên 500 lần chạy. Mốc so sánh "Ground Truth+LM" là LM trên (1) khởi tạo từ pose thật [tr. 13]. EPnP và REPPnP được cộng thêm LM [tr. 14].
- **Baseline** [tr. 12]: DLS, LHM, RPnP, OPnP, MLPnP, REPPnP, EPnP, optDLS; DLS và optDLS có tiền xử lý xoay 90° ba lần để tránh kỳ dị Cayley. UPnP bị loại, với lý do dẫn từ [37] [tr. 12].
- **Kết quả độ chính xác** [T, tr. 14]: SQPnP "không lệch khỏi ground truth quá 10⁻³" trong cả 500 lần chạy, với mọi n và mọi mức nhiễu. Bài không nói rõ 10⁻³ là hiệu của đại lượng nào, theo đơn vị nào; đọc Fig. 3 thì đó là hiệu của sai số tái chiếu bình phương lớn nhất, đơn vị px² (tôi suy ra). SQPnP ngang OPnP và tốt hơn DLS, optDLS. EPnP, REPPnP, MLPnP "erratic" khi nhiễu tăng [tr. 14].
- **Thời gian** [Đ, Tab. 1, tr. 14]: cài bằng Matlab, trung bình trên mọi lần chạy với 4 ≤ n ≤ 10, không tính tinh chỉnh LM. Trung bình / trung vị (ms): SQPnP 2.7/2.0, optDLS 3.5/3.5, LHM 4.7/4.7, DLS 3.5/3.5, OPnP 14.0/14.1, MLPnP 2.3/2.4, RPnP 0.7/0.8, EPnP 1.1/1.1, REPPnP 2.1/2.1. **Không ghi phần cứng.** Bài tự cảnh báo rằng Matlab kém hiệu quả hơn C++ [tr. 12].
- **Không có** thí nghiệm với n lớn, dù bài tuyên bố độ phức tạp tuyến tính theo n [§1.3, tr. 4]. Theo bài, supplementary có sai số trung bình và sai số xoay/dịch [tr. 13], nhưng tôi không có file đó.

## 6. Đóng góp thật sự (thường nhỏ hơn abstract)

(1) Một cách viết gọn: hàm (2) với t khử dạng đóng, gói mọi dữ liệu vào một ma trận Ω 9×9 duy nhất. Từ đó toàn bộ phần lặp có chi phí độc lập với n (dựng Ω là O(n)). Ý này không mới về bản chất (LHM và DLS đều khử t), nhưng dạng Ω gọn và dễ cài. (2) Một chiến lược khởi tạo đơn giản mà hiệu quả thực nghiệm cao: lấy rotation gần nhất với các vector riêng nhỏ nhất của Ω, cả hai dấu, rồi chạy SQP có số bước bị chặn. Cách này tự xử lý trường hợp đồng phẳng và n nhỏ qua null space của Ω, không cần nhánh riêng. (3) Mã C++ công khai, sau này vào OpenCV (`SOLVEPNP_SQPNP`). Phần "khung toán học chứng minh đầy đủ" [§1.3, điểm 2] thì yếu hơn lời tuyên bố: nó chỉ lập luận cho vùng quanh một vector riêng, với 4 điểm khởi tạo, trong khi thuật toán dùng 2 điểm và một quy tắc dừng không được chứng minh (mục 8). Thực nghiệm của tôi (mục 7) ủng hộ tuyên bố thực hành "gần như luôn tìm được cực tiểu toàn cục của (2)", nhưng không ủng hộ chữ "luôn".

## 7. Kiểm chứng của người ghi chú — script trong `code/`, lệnh chạy, kết quả thật

Script: `code/terzakis2020sqpnp_check.py`. Nó dùng `common.py`, numpy và cv2 5.0.0 (không dùng scipy) (wheel pip, `Eigen: NO` trong build info, nên OpenCV dùng nhánh SVD như bài). Seed cố định. Lần chạy mặc định mất 85 s; `--full` (40 cảnh mỗi cấu hình, 2320 cảnh) mất 358 s. Tôi tự cài Ω, P theo (3)–(7), SQP theo đúng hệ KKT của Alg. 2, và Alg. 1 với bốn biến thể:

- `fixed`: đã sửa chỉ số (khởi tạo từ ±√3e₉ hoặc từ cơ sở null), điều kiện dừng 3s_j như §2.1, ε = 10⁻⁸, T = 15 như chú thích 5;
- `conv`: như `fixed` nhưng ε = 10⁻¹², T = 200, để tách lỗi hội tụ khỏi lỗi chọn lưu vực;
- `literal`: chỉ số ν của eq. (14) và điều kiện while của Alg. 1 chép nguyên văn;
- `e9only`: bỏ vòng while.

Ngoài ra có biến thể `one`: một điểm khởi tạo cho mỗi vector riêng, ε = 10⁻⁵, T = 15, mô phỏng cách OpenCV thực sự làm (giải thích ở dưới). NOMP giải bằng SVD thay vì FOAM. "Cực tiểu toàn cục" tham chiếu là min của cùng hàm rᵀΩr trên SO(3), tìm bằng LM (Gauss–Newton có giảm chấn trên SO(3)) từ 96 điểm khởi tạo ngẫu nhiên đều (128 khi `--full`), cộng thêm nghiệm của mọi bộ giải làm điểm khởi tạo. Một ca bị tính là "sai" khi E²_solver − E²_glob > 10⁻⁶E²_glob + 10⁻¹²tr(Ω), và là "sai lớn" khi gap tương đối > 10⁻³. Cột A so với min không ràng buộc; cột C so với min trong các cực tiểu có độ sâu dương, với phép thử độ sâu giống OpenCV (trọng tâm z > 0 hoặc đa số điểm z > 0). Cảnh `tổng quát` và `phẳng` lấy từ `common.make_scene` (K mặc định, độ sâu 4–8). `bài §4.1` là cảnh theo eq. (15). `nhiễu 50px` có độ sâu 0.5–20.

```
python3 VSLAM/pnp/code/terzakis2020sqpnp_check.py          # 85 s
python3 VSLAM/pnp/code/terzakis2020sqpnp_check.py --full   # 358 s, chỉ khác số cảnh ở [4]/[5b]
```

Kết quả thật, lần chạy mặc định (cắt các dòng toàn 0 của bảng [4]):

```
[1] eq. (2)-(7): loại bỏ t, E^2 = r^T Omega r
  200 cảnh ngẫu nhiên (n=3..29, nửa phẳng, 2px):
  max |r'Om r - E2(eq2)|/E2           = 6.5e-14  PASS
  max ||P r - t_lstsq|| / ||t_lstsq||   = 8.4e-15  PASS
  max |E2 - sum z^2 ||m-pi||^2| / E2    = 4.8e-16  PASS  (E2 = reproj. error có trọng số z^2)
  không nhiễu, pose đúng: max(cost/tr, ||Pr - t||) = 4.5e-15  PASS
[2] Hạng của Omega (nhiễu 1px) — số trị riêng > 1e-10 * s1
  tổng quát n=3:3  n=4:5  n=5:7  n=6:9  n=8:9  n=20:9
  phẳng     n=3:-  n=4:5  n=5:6  n=6:6  n=8:6  n=20:6
[3] Mệnh đề 3 và 4
  f dọc cung trắc địa e9 -> e1: f''<0 từ góc ~45 độ (giải tích: 45 độ) -> 'lồi trong vùng 90 độ' của Mđ 3 KHÔNG đúng theo nghĩa lồi trắc địa
  Mđ 4: góc(e, NOMP(sqrt3 e)) lớn nhất trên 20000 e ngẫu nhiên = 65.9 độ; e = diag(1,1,-1)/sqrt3 cho 70.53 độ (= arccos(1/3)); cận 71 độ: PASS
[4]+[5] ...
  cảnh         n sigma   N |   fixed/A    conv/A literal/A  e9only/A   fixed/C    conv/C     one/C     cv2/C | twin
  tổng quát    3  20.0   8 |       1/1       1/1       1/1       1/1       1/1       1/1       1/1       1/1 |    8
  tổng quát    4   1.0   8 |       0/0       0/0       1/1       0/0       0/0       0/0       1/1       0/0 |    0
  ...
  phẳng        4   5.0   8 |       0/0       0/0       0/0       0/0       0/0       0/0       0/0       1/1 |    8
  nhiễu 50px   3  50.0   8 |       1/1       1/1       1/1       1/1       1/1       1/1       1/1       1/1 |    8
  TỔNG                 464 |       2/2       2/2     10/10       6/6       2/2       2/2       5/5       4/3
  cảnh mà cực tiểu toàn cục không ràng buộc có độ sâu âm: 96/464
  Alg.2 (eps=1e-8, T=15), 2704 lời gọi: số bước median 9, 90% 15, tỉ lệ chạm T mà chưa hội tụ 18.0%
  góc trong R^9 giữa ±sqrt3 e (vector riêng sinh seed) và nghiệm SQP: median 67.5 độ, 90% 102.1, max 180.0; tỉ lệ > 90 độ (ra khỏi 'vùng 90 độ'): 18.1%
  số lời gọi SQP / cảnh (fixed): min 2  median 6  max 12
  góc R(cv2) vs R(numpy conv, có kiểm độ sâu): median 0.0e+00 độ; > 1 độ ở 19/464 cảnh
[5b] Hai seed (eq. 13) so với một seed/vector riêng (như OpenCV), 6 phép quay ngẫu nhiên của cơ sở null(Omega)
  tổng quát  n= 4 sigma=0.0: 2 seed: 0/50 cảnh, 0/300 lần | 1 seed: 3/50 cảnh, 3/300 lần | cv2: 1/50
  tổng quát  n= 4 sigma=1.0: 2 seed: 0/50 cảnh, 0/300 lần | 1 seed: 4/50 cảnh, 6/300 lần | cv2: 0/50
  tổng quát  n= 5 sigma=1.0: 2 seed: 0/50 cảnh, 0/300 lần | 1 seed: 0/50 cảnh, 0/300 lần | cv2: 0/50
  phẳng      n= 6 sigma=1.0: 2 seed: 0/50 cảnh, 0/300 lần | 1 seed: 0/50 cảnh, 0/300 lần | cv2: 0/50
  phẳng      n=20 sigma=1.0: 2 seed: 0/50 cảnh, 0/300 lần | 1 seed: 0/50 cảnh, 0/300 lần | cv2: 0/50
[6] Hàm (2) không phải hàm (1): RMSE tái chiếu (px) của SQPnP trước/sau LM theo (1)
  n= 6 sigma= 1.0px: RMSE SQPnP median 1.065, sau LM 1.045; max tăng tương đối 6.5%; góc lệch R max 0.137 độ
  n= 6 sigma=20.0px: RMSE SQPnP median 21.395, sau LM 20.506; max tăng tương đối 10.9%; góc lệch R max 8.885 độ
  n=20 sigma= 5.0px: RMSE SQPnP median 6.443, sau LM 6.410; max tăng tương đối 2.2%; góc lệch R max 0.349 độ
  n= 4 sigma=20.0px: RMSE SQPnP median 12.566, sau LM 12.222; max tăng tương đối 597.2%; góc lệch R max 47.616 độ
[7] Thời gian (ms, median 10 lần, 1 luồng CPU của container) theo n — cảnh tổng quát, 2px
  n=    4: numpy dựng Omega   0.131  numpy SQP 14.612  cv2 SQPNP (toàn bộ)   0.147
  n=   10: numpy dựng Omega   0.121  numpy SQP  2.771  cv2 SQPNP (toàn bộ)   0.051
  n=  100: numpy dựng Omega   0.421  numpy SQP  2.613  cv2 SQPNP (toàn bộ)   0.056
  n= 1000: numpy dựng Omega   3.519  numpy SQP  2.734  cv2 SQPNP (toàn bộ)   0.121
  n=10000: numpy dựng Omega  33.585  numpy SQP  3.067  cv2 SQPNP (toàn bộ)   0.575
tổng thời gian chạy: 85 s
```

Lần chạy `--full` (2320 cảnh; chỉ dán dòng tổng và các dòng có lỗi lớn ở cột `conv`):

```
  phẳng        4   5.0  40 |       2/2       2/2       2/2       2/2       2/2       2/2       3/3       2/2 |   40
  phẳng        4  20.0  40 |       4/3       3/3       4/3       4/3       4/3       3/3       7/6       6/4 |   40
  nhiễu 50px   3  50.0  40 |       1/1       1/1       1/1       1/1       1/1       1/1       1/1       1/1 |   40
  TỔNG                2320 |      11/6       6/6     83/78     29/24      13/8       8/8     26/21     23/18
  cảnh mà cực tiểu toàn cục không ràng buộc có độ sâu âm: 506/2320
  Alg.2 (eps=1e-8, T=15), 13524 lời gọi: số bước median 9, 90% 15, tỉ lệ chạm T mà chưa hội tụ 18.3%
  góc trong R^9 ... median 66.9 độ, 90% 103.8, max 180.0; tỉ lệ > 90 độ (ra khỏi 'vùng 90 độ'): 18.7%
  góc R(cv2) vs R(numpy conv, có kiểm độ sâu): median 1.2e-06 độ; > 1 độ ở 123/2320 cảnh
[5b] tổng quát  n= 4 sigma=0.0: 2 seed: 0/150 cảnh, 0/900 lần | 1 seed: 10/150 cảnh, 11/900 lần | cv2: 2/150
     tổng quát  n= 4 sigma=1.0: 2 seed: 0/150 cảnh, 0/900 lần | 1 seed: 7/150 cảnh, 10/900 lần | cv2: 0/150
     phẳng      n= 6 sigma=1.0: 2 seed: 1/150 cảnh, 6/900 lần | 1 seed: 1/150 cảnh, 6/900 lần | cv2: 1/150
[6]  n= 4 sigma=20.0px: RMSE SQPnP median 13.170, sau LM 12.854; max tăng tương đối 23.1%; góc lệch R max 27.100 độ
```

Đọc kết quả:

- **[1] Công thức lõi đúng** [Đ, của tôi]. rᵀΩr khớp (2) tới 10⁻¹³, t = Pr khớp nghiệm lstsq độc lập, và đồng nhất thức E² = Σz²‖m − π‖² khớp tới 10⁻¹⁶. Như vậy hàm được cực tiểu hoá **là sai số tái chiếu (chuẩn hoá) có trọng số z²**, không phải (1).
- **[2]** rank Ω = 2n − 3 cho tới 9, và 6 với điểm đồng phẳng (n ≥ 5), khớp suy luận ở mục 3.
- **[3]** Mđ 4 đứng vững: cận trên thực là arccos(1/3) = 70.53°, đạt ở e ∝ diag(1, 1, −1). Mđ 3 thì không đúng theo nghĩa lồi trắc địa (mục 8).
- **[4] Tối ưu toàn cục, thực nghiệm** [Đ, của tôi]. Trên 2320 cảnh, bản đã hội tụ (`conv`) trả về cực tiểu không toàn cục của rᵀΩr ở **6 cảnh (0.26%)**, mọi ca đều là sai lớn. Năm ca ở target phẳng n = 4 với nhiễu 5–20 px (5/80 cảnh loại đó), một ca ở n = 3 với nhiễu 50 px. Mọi cấu hình khác có cột `conv/A` bằng 0, kể cả cảnh theo eq. (15) của bài. Cột `conv/C` (có kiểm độ sâu) có thêm 2 ca: phẳng n = 6 với 20 px, và n = 4 với 50 px. Bản `fixed` (ε = 10⁻⁸, T = 15) sai 11 ca, nhưng 5 ca trong đó chỉ do chưa hội tụ (gap < 10⁻³). Bản `literal` sai **83 ca** (78 ca lớn), rải đều ở mọi n. Bỏ vòng while (`e9only`) cho 29 ca sai, chủ yếu ở nhiễu lớn, nên vòng while có ích thật.
- **cv2 SOLVEPNP_SQPNP** (cột C, có kiểm độ sâu như chính nó làm): sai 23/2320 (18 lớn), so với 8/2320 của bản numpy theo đúng eq. (13). Ví dụ (từ `--full`): n = 4 không nhiễu, cv2 cho E² = 0.0102 trong khi min toàn cục là 0 (nhiễu số), tức pose sai hoàn toàn trên dữ liệu sạch. Trong lúc gỡ lỗi (script nháp, không nằm trong `code/`), tôi thấy ở n = 4 kết quả của cv2 lật giữa nghiệm đúng và nghiệm sai chỉ vì những nhiễu loạn cỡ 10⁻¹⁶: đổi thứ tự điểm, đưa pixel ở dạng float32, hay đưa toạ độ chuẩn hoá với K = I.
- **Vì sao cv2 kém hơn bài.** Tôi đọc mã OpenCV (`modules/geometry/src/sqpnp.cpp`, nhánh 5.x). Hàm `nearestRotationMatrixFOAM` đảo dấu λ khi det(e) < 0, nên với det(e) < 0 nó trả về rotation gần **−e** nhất. Tôi port hàm này sang Python và kiểm trên 20 000 vector ngẫu nhiên (script nháp): 0/9885 ca lệch SVD khi det > 0, và 10112/10115 ca lệch khi det < 0, lúc đó kết quả trùng với rotation gần −e nhất. Hệ quả là FOAM(e) và FOAM(−e) cho **cùng một** rotation, nên OpenCV chỉ có một điểm khởi tạo cho mỗi vector riêng, trái với eq. (13). Biến thể `one` mô phỏng đúng điều này, và nó sai với tần suất tương đương cv2 (26 so với 23 trên 2320). Ở [5b] (n = 4, 900 lần chạy với cơ sở null ngẫu nhiên): hai điểm khởi tạo sai 0 lần, một điểm khởi tạo sai 11 và 10 lần. Kết luận này là [M]: tôi chưa chạy chính mã C++ đã sửa để chứng minh nhân quả.
- **Cơ sở null tuỳ ý.** Với hai điểm khởi tạo, đổi cơ sở null ngẫu nhiên không gây sai ở n = 4, 5 (0/900). Nhưng có 1/150 cảnh phẳng n = 6 sai ở cả 6/6 cơ sở, với cả hai biến thể lẫn cv2: đó là một ca thất bại thật của thuật toán, không phụ thuộc cơ sở.
- **Độ sâu.** Ở 506/2320 cảnh, cực tiểu toàn cục không ràng buộc của (2) đặt vật sau camera. Có 1000 cảnh có song sinh cùng cost (cột `twin`: mọi cảnh n = 3 và mọi cảnh phẳng), và 506 xấp xỉ một nửa số đó. Tôi đoán phần lớn 506 ca nằm trong nhóm này, nhưng chưa tách số theo cảnh (tôi suy ra). Nếu cài theo đúng bài (chọn min cost, không kiểm độ sâu) thì chọn giữa hai song sinh là tung đồng xu. Kiểm độ sâu là **bắt buộc**, không phải "khi có nhiều nghiệm" như bài viết [tr. 10].
- **SQP.** Median 9 bước, nhưng 18% lời gọi chạm T = 15 mà chưa đạt ε = 10⁻⁸. Có 18–19% lời gọi kết thúc ở góc > 90° trong R⁹ so với ±√3e sinh ra điểm khởi tạo, tức ra khỏi "vùng 90°".
- **[6] (2) ≠ (1).** Từ nghiệm SQPnP (cv2), LM trên (1) hạ RMSE tái chiếu 2–11% ở n = 6–20 và xoay R tới 0.1–9°. Ở n = 4 với nhiễu 20 px, có ca LM xoay đi 27–48° và RMSE của SQPnP cao gấp 6.97 lần (tăng 597%) so với sau LM, tức hai hàm có cực tiểu toàn cục ở lưu vực khác nhau.
- **[7] Thời gian.** cv2 (C++, một luồng): 0.05–0.15 ms với n ≤ 1000 và 0.58 ms với n = 10⁴. Phần phụ thuộc n là dựng Ω, O(n); phần SQP gần như hằng. Bản numpy của tôi chậm hơn khoảng 50 lần vì vòng lặp Python, và không phản ánh thuật toán. Tuyên bố "tuyến tính theo n" [tr. 4] đứng vững trên cv2. Con số của bài (2.7 ms, Matlab) không so sánh được với con số này.

Cửa đã qua: (2)–(7) qua (a) và (b). Mđ 4 qua (b). Mđ 3 bị (a) và (b) **bác** theo nghĩa đen. Tuyên bố toàn cục qua (b) thực nghiệm với tỉ lệ sai 0.26% trên phân bố cảnh của tôi, tập trung ở n = 3–4 và target phẳng nhỏ.

## 8. Chỗ tôi không tin

1. **"Always determines the global minima"** [abstract, tr. 1] **không được chứng minh cho thuật toán thật sự chạy.** Chuỗi Mđ 3–6 nói về vùng 90° quanh **một** vector riêng cực tiểu, với **4** điểm khởi tạo ξ₁…ξ₄. Alg. 1 chỉ dùng **2** điểm, và chính bài ghi rằng lựa chọn này được "empirically determined" [tr. 10]. Quy tắc dừng, tức chỉ xét e_j tiếp theo khi min E² ≥ 3s_j [tr. 9], cũng không có chứng minh. Không có mệnh đề nào nói rằng một cực tiểu khả thi có giá trị nhỏ hơn 3s_j không thể nằm trong vùng của e_j' với j' < j. Mục 7 [4] cho thấy phiên bản hội tụ đầy đủ (ε = 10⁻¹², T = 200) vẫn trả về cực tiểu không toàn cục của chính hàm (2) ở 6/2320 cảnh (`--full`): năm ca ở target phẳng n = 4 với nhiễu 5–20 px, một ca ở n = 3 với nhiễu 50 px. Phần chứng minh thì nằm trong supplementary mà tôi chưa đọc.
2. **Mđ 3 sai theo nghĩa đen** [tr. 7]. Dọc cung trắc địa từ e₉ tới e₁ trên mặt cầu thì f(θ) = 3(s₉cos²θ + s₁sin²θ). Đạo hàm bậc hai tỉ lệ với cos 2θ nên đổi dấu ở **45°**, không phải ở 90°. Điểm uốn gần nhất không phải một vector riêng, trái với chứng minh ba dòng của bài (tôi suy ra; mục 7 [3] đo được 45°). Điều đúng trong vùng 90° là f tăng đơn điệu dọc mọi cung trắc địa xuất phát từ e₉ (tôi suy ra). Có thể lập luận của Mđ 5–6 chỉ cần tính đơn điệu đó, nhưng bài viết "convex".
3. **Eq. (14) và Alg. 1 có chỉ số lệch một.** ν = 9 − k + i − ⌊i/k⌋k cho ν = 8 khi k = 1 với cả i = 1 và i = 2. Tổng quát hơn, ν trỏ vào e_{9−k} thay vì e₉ khi i = k và i = 2k, trong khi null space là ⟨e_{10−k}, …, e₉⟩ [tr. 10]. Viết đúng phải là ν = 10 − k + ((i − 1) mod k) (tôi suy ra). Cài nguyên văn thì thuật toán **không bao giờ** khởi tạo từ e₉ khi Ω khả nghịch. Mục 7 [4]: biến thể "literal" sai 83/2320 cảnh, so với 11/2320 của bản đã sửa chỉ số (cùng ε, T).
4. **Điều kiện while của Alg. 1 là min E² ≥ s_{9−k}** [tr. 11], trong khi §2.1 so với 3s₈ [tr. 9]. Giá trị f tại √3e_j là 3s_j, nên hệ số 3 là đúng. Mã OpenCV (đọc ở `modules/geometry/src/sqpnp.cpp`, nhánh 5.x) dùng `3 * s_[index]`. Sai sót này chỉ làm thuật toán tìm nhiều hơn chứ không ít hơn, nên vô hại về độ đúng (tôi suy ra).
5. **Lời kể "đi xuống trong vùng 90°" không mô tả điều SQP làm.** Các bước SQP đầu tiên có ‖δ‖ cỡ 1–2, trên một mặt cầu bán kính √3. Tính góc trong R⁹ giữa nghiệm cuối và ±√3e dùng để khởi tạo thì có median 67°, và 18–19% lời gọi kết thúc ở góc > 90° (mục 7 [4]). Vậy SQP không ở lại vùng mà Mđ 6 nói tới; phần "đảm bảo" dựa trên vùng không áp vào quỹ đạo thật (tôi suy ra).
6. **"SQP typically converges within 10 iterations"** [tr. 11]. Với ε = 10⁻⁸ như trong thí nghiệm của bài [chú thích 5], tôi đo được median 9 bước, nhưng 18% lời gọi chạm T = 15 mà chưa đạt ε. Hội tụ tuyến tính do Hessian thiếu số hạng ràng buộc (mục 3), nên khẳng định trên chỉ đúng với ε = 10⁻⁵.
7. **Thước đo của §4 không đo điều bài tuyên bố.** Bài tối ưu (2) nhưng báo cáo sai số theo (1) so với LM trên (1) [tr. 13]. Hai hàm có cực tiểu khác nhau, nên "không lệch quá 10⁻³" không thể là kiểm chứng của tối ưu toàn cục; tốt nhất nó chỉ nói nghiệm của (2) gần nghiệm của (1) trong phân bố cảnh dễ này. Mục 7 [6]: ở n = 6–20, RMSE tái chiếu của SQPnP cao hơn nghiệm LM(1) 2–11%; ở n = 4 với nhiễu 20 px có ca cao gấp 6.97 lần (tăng 597%).
8. **Tuyên bố tổng quát cho điểm đồng phẳng** [abstract; §1.3] chỉ có một ảnh minh hoạ [Fig. 1(b)], không có thí nghiệm định lượng trong bài chính.
9. **Tab. 1 không ghi phần cứng**, và so Matlab với Matlab thì không nói lên thời gian C++. Mục 7 [7] đo bản OpenCV (C++) riêng.

## 9. Chỗ tôi chưa hiểu (→ `99-chua-biet.md`)

- Chứng minh của Mđ 5 và Mđ 6 (supplementary). Tôi không biết "descending" trong Mđ 6 là đi xuống theo đường liên tục trên đa tạp (gradient flow) hay là SQP rời rạc; lập luận chỉ có ý nghĩa với loại thứ nhất.
- Vì sao 2 điểm khởi tạo mỗi vector riêng (cả hai dấu) lại đủ, trong khi 1 điểm thì không. Mục 7 [5b] cho thấy ở n = 4, một điểm khởi tạo sai ở 5–7% cảnh (10/150 và 7/150), còn hai điểm thì không sai lần nào trong 1800 lần chạy. Tôi chưa có lời giải thích hình học.
- Có thể cấp **chứng nhận tối ưu** (dual certificate, kiểu nới lỏng Shor của QCQP (8) với ràng buộc bậc hai) cho nghiệm SQPnP không? Nếu làm được thì "thực nghiệm toàn cục" sẽ thành toàn cục có chứng nhận cho từng lần chạy. Bài không bàn tới.
- Cực tiểu toàn cục của (2) và của (1) nằm khác lưu vực trong những cấu hình nào? Mục 7 [6] cho thấy LM trên (1) khởi tạo từ nghiệm SQPnP có lúc xoay đi 27–48° ở n = 4, nhiễu 20 px.
- Cách OpenCV chọn nghiệm khi các cost chênh nhau dưới 10⁻⁶ (tuyệt đối, đơn vị m²; `EQUAL_SQUARED_ERRORS_DIFF`) phụ thuộc thang đo của cảnh. Tôi chưa đo ảnh hưởng của nó.

## 10. Quan hệ với các bài khác trong `refs.bib`

- `lu2000orthogonal` (LHM): cùng tinh thần "sai số không gian vật, khử t dạng đóng". Nhưng LHM đo khoảng cách vuông góc tới tia, còn (2) đo song song với mặt ảnh, tức sai số tái chiếu nhân z² (tôi suy ra). Cả hai thiên về điểm xa và đều có song sinh sau camera với target phẳng. LHM là lặp địa phương; SQPnP thêm chiến lược khởi tạo từ phổ của Ω.
- `schweighofer2008sos`: cách QCQP duy nhất trước đó, giải bằng nới lỏng SOS/SDP [§1.2, tr. 4]. SQPnP chọn lối không nới lỏng, đổi chứng nhận lấy tốc độ.
- `hesch2011dls`, `nakano2015dls`, `zheng2013opnp`: bộ giải đa thức làm baseline. Bài thừa nhận OPnP có độ chính xác tương đương nhưng chậm hơn khoảng 5 lần trong Matlab [Tab. 1].
- `lepetit2009epnp`, `urban2016mlpnp`, `ferraz2014reppnp`, `li2012rpnp`: baseline "heuristic" [tr. 3]. `kneip2014upnp` bị loại khỏi so sánh với lý do lấy từ `nakano2015dls` [tr. 12].
- `collins2014ippe`: cho target phẳng. Hiện tượng song sinh sau camera ở mục 2 và lưỡng nghĩa hai nghiệm của IPPE là hai chuyện khác nhau: song sinh là đối xứng chính xác của hàm cost, còn lưỡng nghĩa IPPE là hai cực tiểu cùng ở trước camera (tôi suy ra).
- Bài dẫn [47] (MRP, Terzakis–Lourakis–Ait-Boudaoud, JMIV 2018) và [30, 31] (FOAM cho absolute orientation). Cả ba **không có trong `refs.bib`**.

## 11. Nó đổi gì trong suy nghĩ

Trước khi đọc, tôi coi "SQPnP = PnP tối ưu toàn cục" như một định lý. Sau khi đọc và chạy thử, tôi thấy có ba điều cần nói kèm. Thứ nhất, hàm được tối ưu là sai số tái chiếu có trọng số z², không phải sai số tái chiếu; muốn có ML dưới nhiễu pixel thì vẫn phải thêm một bước LM trên (1). Thứ hai, tính toàn cục là thực nghiệm, rất tốt nhưng không tuyệt đối, và phần chứng minh không bao phủ thuật toán đang chạy. Thứ ba, bản OpenCV khác bài ở chỗ quan trọng: FOAM trả về cùng một rotation cho +e và −e, nên mỗi vector riêng chỉ còn một điểm khởi tạo, và ở n = 4 điều này làm nó sai nhiều hơn bản cài theo đúng eq. (13). Ý hay nhất tôi giữ lại là xem phổ của một ma trận dữ liệu 9×9 như bản đồ để chọn điểm khởi tạo cho tối ưu trên SO(3).

## 12. Câu hỏi tự kiểm (3–5 câu, hỏi *vì sao* / *khi nào hỏng*)

1. Vì sao hàm (2) cho phép khử t dạng đóng còn hàm (1) thì không, và cái giá của việc thay (1) bằng (2) là gì dưới nhiễu pixel Gauss?
2. Vì sao null(Ω) có ít nhất 3 chiều với điểm đồng phẳng, bất kể n? Điều đó buộc Alg. 1 làm gì khác?
3. Khi nào cực tiểu toàn cục của rᵀΩr trên SO(3) đặt vật **sau** camera, và vì sao với target phẳng điều này luôn có một song sinh cùng cost?
4. Mđ 3 nói f lồi trong vùng 90°. Dọc một cung trắc địa từ e₉ thì f'' đổi dấu ở đâu, và việc đó ảnh hưởng thế nào tới lập luận của Mđ 5–6?
5. Nếu chỉ khởi tạo từ một dấu của mỗi vector riêng (như OpenCV thực tế làm) thì SQPnP hỏng ở cấu hình nào, và vì sao việc đó phụ thuộc vào cơ sở tuỳ ý của null(Ω)?

## Trích đoạn nguyên văn làm bằng chứng

- "identifies regions in the parameter space that contain unique minima with guarantees that at least one of them will be the global minimum" [tr. 1]
- "The squared terms in eq. (2) penalize the distances between the reconstructed and the actual 3D points in the camera frame." [tr. 5]
- "Proposition 6 is sufficient to enable safe navigation to the global minimum." [tr. 8]
- "Similar searches may be performed in the regions of eigenvectors that may simply be saddle points" [tr. 9]
- "In these cases, the typical treatment involving the positive depth test applies." [tr. 10]
- "SQP typically converges within 10 iterations, hence the recommendation T ≥ 15." [tr. 11]
- "As expected, we observe that SQPnP does not deviate from the ground truth more than 10−3 in any of the 500 executions, regardless of the number of points or levels of additive noise." [tr. 14]
