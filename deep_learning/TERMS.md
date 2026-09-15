# Quy ước thuật ngữ — bắt buộc cho toàn cây `deep_learning`

Mục đích: **một khái niệm, một cách gọi**. Người đọc không phải đoán "lượt ngược" và "lan truyền ngược"
có phải một thứ không. Mọi file trong cây phải tuân thủ bảng này.

## Cách dùng

- Lần xuất hiện **đầu tiên trong mỗi file**: `\vn{cách gọi chuẩn}{English}` — ví dụ `\vn{lan truyền ngược}{backpropagation}`.
- Các lần sau trong cùng file: dùng **cách gọi chuẩn** ở cột 2, không dùng biến thể.
- Thuật ngữ ở nhóm "giữ nguyên tiếng Anh": luôn `\en{...}` ở lần đầu, sau đó viết trần.
- Không viết hoa chữ cái đầu thuật ngữ giữa câu (`focal loss`, không phải `Focal loss`).

## A. Những chỗ đang mâu thuẫn — chốt cách gọi

| English | CHUẨN (dùng cái này) | Cấm dùng |
|---|---|---|
| backpropagation | **lan truyền ngược** | truyền ngược, backprop |
| backward pass | **lượt ngược** | lượt backward, pha ngược |
| forward pass | **lượt xuôi** | lượt forward, lượt thuận, lượt tiến |
| loss function | **hàm mất mát** | hàm lỗi, hàm mục tiêu¹ |
| inference | **suy luận** | suy diễn, suy một lần |
| training | **huấn luyện** | đào tạo, tập huấn |
| feature | **đặc trưng** | thuộc tính |
| dataset | **tập dữ liệu** | bộ dữ liệu |
| layer | **tầng** | lớp² |
| bundle adjustment | **hiệu chỉnh chùm tia** | tinh chỉnh bó |
| ground truth | **chân trị** | nhãn thật |
| optical flow | **dòng quang** | luồng quang |
| residual connection | **kết nối tắt** | kết nối dư |
| normalization | **chuẩn hoá** | chuẩn hoá giữa mạng³ |
| label assignment | **gán mẫu** | gán nhãn⁴, gán nhãn mẫu, quy tắc gán mẫu dương/âm |
| non-maximum suppression | **triệt phi cực đại** | triệt tiêu không cực đại |
| Hungarian matching | **ghép cặp Hungary** | ghép Hungary |
| translation equivariance | **đẳng biến tịnh tiến** | tính đồng biến với tịnh tiến |
| brightness constancy | **độ sáng không đổi** | độ sáng bất biến |
| cross-validation | **kiểm định chéo** | (viết thường giữa câu) |
| data leakage | **rò rỉ dữ liệu** | (viết thường giữa câu) |
| perceptual loss | **mất mát tri giác** | loss tri giác |
| feed-forward | **tiến thẳng** | suy một lần |
| inter-annotator agreement | **mức đồng thuận giữa người gán nhãn** | (bản rút gọn) |
| capacity | **sức chứa** | năng lực mô hình |
| latency | **độ trễ** | (giữ tiếng Anh)⁷ |
| frame | **khung hình** | (giữ tiếng Anh)⁷ |
| pixel | **điểm ảnh** hoặc **pixel** | — cả hai đều được, giữ nhất quán trong một file |
| receptive field | **trường tiếp nhận** | vùng tiếp nhận |
| likelihood | **độ hợp lý** | hợp lý |
| hyperparameter | **siêu tham số** | tham số siêu |
| empirical risk minimization | **tối thiểu hoá rủi ro thực nghiệm** | tối thiểu rủi ro thực nghiệm |
| extrinsic calibration | **hiệu chỉnh ngoại** | hiệu chỉnh ngoại tại |
| throughput | **thông lượng** | (viết thường giữa câu) |
| activation (tensor) | **kích hoạt** | hoạt ảnh, hàm phi tuyến⁵ |
| activation function | **hàm kích hoạt** | hàm phi tuyến⁵ |
| baseline (stereo) | **đường cơ sở** | đường đáy |
| baseline (đối chứng) | giữ nguyên `\en{baseline}` | đường cơ sở⁶ |

¹ *hàm mục tiêu (objective function)* là khái niệm **khác**: nó có thể gồm hàm mất mát cộng các số hạng
chính quy hoá. Chỉ dùng khi thực sự nói về objective, và khi dùng phải nêu rõ khác biệt.
² *lớp* đã bị chiếm nghĩa cho **class** trong phân loại — tuyệt đối không dùng cho *layer*.
³ khi cần nói riêng normalization đặt giữa mạng thì viết "chuẩn hoá giữa mạng", nhưng thuật ngữ nền vẫn là "chuẩn hoá".
⁷ Ba từ này từng bị xếp nhầm vào nhóm "giữ nguyên tiếng Anh". Bản dịch tiếng Việt của chúng đã phổ biến
và đọc tự nhiên hơn hẳn ("ràng buộc độ trễ" dễ đọc hơn "ràng buộc latency"), nên dùng tiếng Việt.

⁵ *hàm phi tuyến (nonlinearity)* là cách gọi khác của **hàm kích hoạt**; chọn một và giữ nhất quán —
cây này dùng "hàm kích hoạt". Còn **kích hoạt** (danh từ) là tensor đầu ra của một tầng, khái niệm khác hẳn.
⁶ *baseline* có hai nghĩa không liên quan: khoảng cách giữa hai camera trong stereo (**đường cơ sở**), và
phương pháp đối chứng trong thực nghiệm (giữ nguyên tiếng Anh). Không được dùng lẫn.

⁴ *gán nhãn (labelling/annotation)* là việc con người tạo nhãn; *gán mẫu (label assignment)* là bước trong
detector quyết định anchor/điểm nào là dương hay âm. Hai việc hoàn toàn khác nhau, không được dùng lẫn.

## B. Cặp dễ nhầm — phải phân biệt rõ, không được coi là đồng nghĩa

| Cặp | Khác nhau ở đâu |
|---|---|
| lan truyền ngược ↔ lượt ngược | thuật toán ↔ một lần chạy thuật toán đó |
| gán nhãn ↔ gán mẫu | người tạo nhãn ↔ detector chọn mẫu dương/âm |
| hàm mất mát ↔ hàm mục tiêu | phần đo sai lệch ↔ toàn bộ thứ được tối ưu |
| tham số ↔ siêu tham số | học được từ dữ liệu ↔ do người đặt trước |
| lớp (class) ↔ tầng (layer) | nhãn trong phân loại ↔ khối tính toán trong mạng |
| mẫu (sample: một quan sát) ↔ mẫu (sample: lấy mẫu) | danh từ ↔ động từ; nêu rõ nghĩa ở khối `nentang` |
| chuẩn hoá (normalization) ↔ chuẩn hoá (standardization) | đưa về dải ↔ trừ trung bình chia độ lệch chuẩn |
| độ lệch (bias thống kê) ↔ thiên lệch quy nạp (inductive bias) ↔ tham số \(b\) | ba nghĩa khác nhau của *bias* |

## C. Giữ nguyên tiếng Anh — dùng `\en{...}`, không dịch

`attention`, `embedding`, `anchor`, `backbone`, `neck`, `head`, `token`, `patch`, `transformer`,
`batch`, `epoch`, `dropout`, `overfitting`, `underfitting`, `gradient`, `learning rate`, `momentum`,
`checkpoint`, `pipeline`, `baseline`, `ablation`, `benchmark`, `kernel`,
`convolution`, `pooling`, `softmax`, `logit`, `prompt`, `fine-tune`, `zero-shot`, `scaling law`,
`splat`, `voxel`, `mesh`, `point cloud`, `stride`, `padding`.

Lý do: bản dịch của những từ này gây khó hiểu hơn bản gốc, và người đọc sẽ gặp chúng ở dạng tiếng Anh
trong mọi paper và mọi thư viện.
