# Danh mục công trình PnP — đã kiểm nguồn, chưa đọc

Ngày lập: 2026-09-25. Lần sửa gần nhất: 2026-09-25. **Rà lại: 3/2027** (các mục 2023–2026
hết hạn nhanh nhất).

Đây là bản đồ đường đi, không phải bài học. Mỗi mục dưới đây là một công trình **có thật, đúng
venue, đúng năm, đúng DOI** — đã đối chiếu với Crossref hoặc trang gốc (chi tiết trong
`search-log.md`). Nhưng tôi **chưa đọc** bài nào quá mức abstract: câu "vì sao đọc" ở mỗi mục
là tóm tắt đóng góp theo abstract (với khoảng 37 bài đã mở abstract gốc) hoặc theo hiểu biết
chung về bài (với các bài kinh điển còn lại — *chưa đối chiếu nguồn*), không phải ghi chú đọc.
Định vị kiểu "mục III, eq. (12)" chỉ được thêm vào khi có `notes/<bibkey>.md`.

**Ký hiệu.** `[A]`/`[B]`/`[C]` là mức tin theo `research-rules.md` mục 4 (xem đầu `refs.bib`).
★ = **nền tảng**, phải đọc nếu muốn hiểu PnP tới gốc; không đánh dấu = **tra khi cần**.
Tên trong ngoặc vuông cuối mục là bibkey trong `refs.bib`; PDF open-access (nếu có) tải bằng
`papers/fetch.sh <bibkey>`.

---

## Lộ trình đọc gợi ý (80/20)

Nếu chỉ có thời gian cho khoảng mười bài, đi theo thứ tự này. Thứ tự đi từ *bài toán* sang
*bộ giải* rồi tới *hệ thống*, không theo năm công bố:

1. **marchand2016arsurvey** — bức tranh toàn cảnh, có mã; đọc trước để có từ vựng.
2. **haralick1994review** — P3P là gì, vì sao có tới bốn nghiệm, lịch sử từ Grunert 1841.
3. **lepetit2009epnp** — bộ giải n điểm được dùng nhiều nhất; ý tưởng bốn điểm điều khiển.
4. **lu2000orthogonal** — cách nghĩ ngược lại: lặp để cực tiểu sai số trong không gian vật.
5. **terzakis2020sqpnp** — PnP tối ưu toàn cục hiện đại, đang là cờ mặc định nên dùng trong OpenCV.
6. **collins2014ippe** — target phẳng và vì sao nó có hai nghiệm; nối sang cây `marker/`.
7. **fischler1981ransac** — RANSAC ra đời chính để giải bài toán định vị kiểu P3P có ngoại lai.
8. **ding2023p3p** — P3P hiện hành của cả OpenCV lẫn PoseLib.
9. **urban2016mlpnp** hoặc **vakhitov2021uncertainty** — khi nhiễu không đẳng hướng.
10. **chen2022epropnp** — PnP trong học sâu: từ nghiệm điểm sang phân bố pose.

Sau mười bài đó, nhánh nào dùng tới thì đọc tiếp nhóm tương ứng dưới đây.

---

## 0. Tổng quan, benchmark, thư viện

Chưa có bài tổng quan riêng về PnP nào ở venue đầu ngành trong 2021–2026 (agent tìm kiếm và
tôi đều không thấy; bài review duy nhất tìm được ở *J. Physics: Conference Series* 2018 quá yếu
để đưa vào). Vì vậy hai tổng quan dưới đây, dù cũ, vẫn là cửa vào tốt nhất; phần cập nhật
phải tự ghép từ các nhóm sau.

- ★ **Pose Estimation for Augmented Reality: A Hands-On Survey** — Marchand, Uchiyama, Spindler — *IEEE TVCG*, 2016 `[A]`. Tổng quan PnP + tracking có mã minh hoạ; đọc đầu tiên để có khung chung. [marchand2016arsurvey]
- **Monocular Model-Based 3D Tracking of Rigid Objects: A Survey** — Lepetit, Fua — *Foundations and Trends in Computer Graphics and Vision*, 2005 `[A]`. Góc nhìn tracking dựa mô hình, trước EPnP. [lepetit2005survey]
- ★ **Multiple View Geometry in Computer Vision** (2nd ed.) — Hartley, Zisserman — Cambridge University Press, 2004 `[A]`. Chương camera resectioning: DLT và Gold Standard — chuẩn để so mọi bộ giải. [hartley2004]
- **BOP: Benchmark for 6D Object Pose Estimation** — Hodaň et al. — *ECCV*, 2018 `[A]`. Nơi các PnP học được so kết quả. [hodan2018bop]
- **Benchmarking 6DOF Outdoor Visual Localization in Changing Conditions** — Sattler et al. — *CVPR*, 2018 `[A]`. Benchmark chuẩn cho định vị bằng pose tuyệt đối (Aachen Day-Night). [sattler2018benchmarking]
- **OpenGV: A Unified and Generalized Approach to Real-Time Calibrated Geometric Vision** — Kneip, Furgale — *ICRA*, 2014 `[A]`. Thư viện cài P3P, EPnP, UPnP, gP3P, NPnP trên cùng một giao diện tia chiếu. [kneip2014opengv]
- **PoseLib** — Larsson và cộng sự — phần mềm, 2020– `[B]`. Bảng bộ giải trong README là cách nhanh nhất biết bộ giải tối thiểu nào đang là mặc định của cộng đồng. [poselib]
- **OpenCV `solvePnP`** — phần mềm `[B]`. Xem mục *Cạm bẫy* ở cuối. [opencvsolvepnp]

## 1. P3P — bài toán tối thiểu

Ba điểm là số tương ứng ít nhất xác định được pose (sáu ẩn, mỗi điểm cho hai phương trình), và
bài toán có tối đa bốn nghiệm thực. Lịch sử nhánh này là lịch sử của việc làm cho bộ giải
**ổn định số hơn và nhanh hơn**, vì trong RANSAC nó chạy hàng nghìn lần mỗi ảnh.

- ★ **Review and Analysis of Solutions of the Three Point Perspective Pose Estimation Problem** — Haralick, Lee, Ottenberg, Nölle — *IJCV*, 1994 `[A]`. So sánh các lời giải từ Grunert 1841 trở đi; nền lịch sử và số nghiệm. [haralick1994review]
- **The Perspective View of Three Points** — Wolfe, Mathis, Sklair, Magee — *IEEE T-PAMI*, 1991 `[B]`. Hình học của việc khi nào có nhiều nghiệm. [wolfe1991perspective]
- **Complete Solution Classification for the Perspective-Three-Point Problem** — Gao, Hou, Tang, Cheng — *IEEE T-PAMI*, 2003 `[A]`. Phân loại đầy đủ số nghiệm thực theo cấu hình. [gao2003p3p]
- ★ **A Novel Parametrization of the P3P Problem for a Direct Computation of Absolute Camera Position and Orientation** — Kneip, Scaramuzza, Siegwart — *CVPR*, 2011 `[A]`. Tính thẳng R, t, bỏ bước trung gian qua khoảng cách. [kneip2011p3p]
- **An Efficient Algebraic Solution to the Perspective-Three-Point Problem** — Ke, Roumeliotis — *CVPR*, 2017 `[A]`. Là `SOLVEPNP_AP3P` trong OpenCV. [ke2017p3p]
- ★ **Lambda Twist: An Accurate Fast Robust P3P Solver** — Persson, Nordberg — *ECCV*, 2018 `[A]`. Giải qua chéo hoá, chỉ cần một nghiệm của phương trình bậc ba thay vì bậc bốn. [persson2018lambdatwist]
- ★ **Revisiting the P3P Problem** — Ding, Yang, Larsson, Olsson, Åström — *CVPR*, 2023 `[A]`. P3P như giao của hai conic; hiện là P3P mặc định của **cả** OpenCV 4.x lẫn PoseLib (đã kiểm mã nguồn). [ding2023p3p]
- **A Conic Transformation Approach for Solving the Perspective-Three-Point Problem** — Wu, Bhayani, Heikkilä — *WACV*, 2025 `[B]`. Tiếp nối hướng conic, đưa một conic về parabol chuẩn. [wu2025conic]

## 2. PnP n điểm: lời giải dạng đóng / không lặp

Khi có nhiều hơn ba điểm, câu hỏi chuyển từ "giải được không" sang "dùng hết thông tin ra sao
với chi phí O(n)". Các bộ giải khác nhau chủ yếu ở **hàm mục tiêu đại số** chúng cực tiểu và ở
**cách tham số hoá phép quay** (ma trận, quaternion, Cayley, …) — đây là cột 2 của câu hỏi dẫn
đường trong `00-cau-hoi.md`.

- **Linear N-Point Camera Pose Determination** — Quan, Lan — *IEEE T-PAMI*, 1999 `[B]`. [quan1999linear]
- **PnP Problem Revisited** — Wu, Hu — *Journal of Mathematical Imaging and Vision*, 2006 `[B]`. Số nghiệm của P4P, P5P. [wu2006pnp]
- ★ **EPnP: An Accurate O(n) Solution to the PnP Problem** — Lepetit, Moreno-Noguer, Fua — *IJCV*, 2009 `[A]`. Biểu diễn mọi điểm qua bốn điểm điều khiển; O(n); là baseline của gần như mọi bài sau. [lepetit2009epnp]
- ★ **A Robust O(n) Solution to the Perspective-n-Point Problem** (RPnP) — Li, Xu, Xie — *IEEE T-PAMI*, 2012 `[A]`. Baseline chuẩn trong benchmark PnP, ổn định với ít điểm. [li2012rpnp]
- **A Direct Least-Squares (DLS) Method for PnP** — Hesch, Roumeliotis — *ICCV*, 2011 `[A]`. Cực tiểu hoá bình phương trực tiếp, tìm mọi cực tiểu. [hesch2011dls]
- **Revisiting the PnP Problem: A Fast, General and Optimal Solution** (OPnP) — Zheng, Kuang, Sugimoto, Åström, Okutomi — *ICCV*, 2013 `[B]`. [zheng2013opnp]
- **ASPnP: An Accurate and Scalable Solution to the PnP Problem** — Zheng, Sugimoto, Okutomi — *IEICE Trans. Inf. & Syst.*, 2013 `[B]`. [zheng2013aspnp]
- ★ **UPnP: An Optimal O(n) Solution to the Absolute Pose Problem with Universal Applicability** — Kneip, Li, Seo — *ECCV*, 2014 `[A]`. Một bộ giải cho cả camera trung tâm và camera tổng quát. [kneip2014upnp]
- **Globally Optimal DLS Method for PnP Problem with Cayley Parameterization** — Nakano — *BMVC*, 2015 `[B]`. Sửa điểm kỳ dị của tham số hoá Cayley trong DLS. [nakano2015dls]
- ★ **A Consistently Fast and Globally Optimal Solution to the Perspective-n-Point Problem** (SQPnP) — Terzakis, Lourakis — *ECCV*, 2020 `[A]`. SQP trên các vùng mỗi vùng chứa một cực tiểu; `SOLVEPNP_SQPNP` trong OpenCV. [terzakis2020sqpnp]
- **CPnP: Consistent Pose Estimator for PnP Problem with Bias Elimination** — Zeng, Chen, Mu, Shi, Wu — *ICRA*, 2023 `[B]`. Trừ độ chệch tiệm cận để ước lượng nhất quán khi n → ∞. [zeng2023cpnp]
- **A Novel Iterative Solution to the PnP Problem via Cost Function Approximation** — Zhou, Wei, Wang — *IEEE T-RO*, 2025 `[B]`. Tuyên bố các bộ giải hiện có lệch khỏi Gold Standard khi dải độ sâu lớn — đáng kiểm. [zhou2025iterative]

## 3. PnP lặp và tinh chỉnh

Lời giải dạng đóng là để khởi tạo; nghiệm cuối cùng gần như luôn đi qua một bước lặp. Nhánh này
cũ nhưng là nơi sinh ra hai quan niệm khác nhau về *sai số nào* nên cực tiểu: sai số tái chiếu
trên ảnh hay sai số trong không gian vật.

- **Pose Estimation from Corresponding Point Data** — Haralick, Joo, Lee, Zhuang, Vaidya, Kim — *IEEE Trans. SMC*, 1989 `[A]`. [haralick1989pose]
- ★ **Model-Based Object Pose in 25 Lines of Code** (POSIT) — DeMenthon, Davis — *IJCV*, 1995 `[A]`. Lặp từ xấp xỉ phối cảnh yếu. [dementhon1995posit]
- **Iterative Pose Estimation Using Coplanar Feature Points** — Oberkampf, DeMenthon, Davis — *CVIU*, 1996 `[A]`. POSIT cho điểm đồng phẳng. [oberkampf1996coplanar]
- ★ **Fast and Globally Convergent Pose Estimation from Video Images** (LHM / orthogonal iteration) — Lu, Hager, Mjolsness — *IEEE T-PAMI*, 2000 `[A]`. Cực tiểu sai số trong không gian vật; hội tụ toàn cục theo tuyên bố của tác giả. [lu2000orthogonal]

## 4. Target phẳng và lưỡng nghĩa

Khi mọi điểm 3D nằm trên một mặt phẳng, hàm mục tiêu thường có **hai cực tiểu** gần nhau, và
bộ giải tổng quát có thể rơi vào cực tiểu sai. Cây `marker/` (ch 3–4, ch 10) đã phân tích sâu
nhánh này cho fiducial; ở đây chỉ giữ công trình gốc.

- **Algorithms for Plane-Based Pose Estimation** — Sturm — *CVPR*, 2000 `[B]`. [sturm2000plane]
- ★ **Robust Pose Estimation from a Planar Target** — Schweighofer, Pinz — *IEEE T-PAMI*, 2006 `[A]`. Chỉ ra và xử lý cực tiểu thứ hai. [schweighofer2006planar]
- ★ **Infinitesimal Plane-Based Pose Estimation** (IPPE) — Collins, Bartoli — *IJCV*, 2014 `[A]`. Trả về cả hai nghiệm; `SOLVEPNP_IPPE` trong OpenCV. [collins2014ippe]

## 5. Tối ưu toàn cục và chứng nhận

Các bộ giải ở nhóm 2 cho "nghiệm tối ưu" theo một hàm đại số. Nhóm này hỏi câu khó hơn: tìm (hoặc
**chứng nhận** đã tìm) được cực tiểu toàn cục của hàm có ý nghĩa hình học, kể cả khi có ngoại lai.

- **Optimal Estimation of Perspective Camera Pose** — Olsson, Kahl, Oskarsson — *ICPR*, 2006 `[B]`. [olsson2006optimal]
- **Globally Optimal O(n) Solution to the PnP Problem for General Camera Models** — Schweighofer, Pinz — *BMVC*, 2008 `[B]`. Nới lỏng SDP / sum-of-squares. [schweighofer2008sos]
- **Branch-and-Bound Methods for Euclidean Registration Problems** — Olsson, Kahl, Oskarsson — *IEEE T-PAMI*, 2009 `[A]`. [olsson2009bnb]
- **Global Optimization through Rotation Space Search** — Hartley, Kahl — *IJCV*, 2009 `[A]`. Branch-and-bound trên SO(3). [hartley2009rotation]
- **Robust Optimal Pose Estimation** — Enqvist, Kahl — *ECCV*, 2008 `[B]`. Tối ưu toàn cục có ngoại lai. [enqvist2008robust]
- ★ **Certifiably Optimal Outlier-Robust Geometric Perception: Semidefinite Relaxations and Scalable Global Optimization** — Yang, Carlone — *IEEE T-PAMI*, 2023 `[A]`. Khung chứng nhận tổng quát; absolute pose là một trong sáu bài toán thử. [yang2022certifiable]
- **Fast Certifiable Algorithm for the Absolute Pose Estimation of a Camera** — Garcia-Salguero, Dima, Mateus, Gonzalez-Jimenez — *SIAM J. Imaging Sciences*, 2024 `[B]`. Chứng nhận nghiệm PnP trong cỡ micro giây. [garciasalguero2024certpnp]
- **Accelerating Globally Optimal Consensus Maximization in Geometric Vision** — Zhang, Peng, Xu, Kneip — *IEEE T-PAMI*, 2024 `[B]`. [zhang2024consensus]
- **BnB-Based Robust PnP Pose Estimation Method for Outliers** — Long, Hu, Jiang, Li, Ouyang — *IEEE RA-L*, 2025 `[B]`. [long2025bnbpnp]

## 6. Camera không chuẩn: focal chưa biết, méo, rolling shutter, nhiều tâm chiếu

Mỗi giả thiết bị bỏ đi (K đã biết, màn trập toàn cục, một tâm chiếu) thêm ẩn và thêm điểm tối
thiểu. Nhóm Praha–Lund–ETH (Kukelova, Pajdla, Larsson, Sattler, Albl) chiếm phần lớn nhánh này —
**cần lưu ý**: phần lớn tri thức ở đây đến từ một cụm nhóm có hợp tác chặt, theo `research-rules.md`
mục 3 phải ghi rõ điều đó.

- **A Minimal Solution to the Generalised 3-Point Pose Problem** — Nistér — *CVPR*, 2004 `[A]`. gP3P. [nister2004gp3p]
- **Using Multi-Camera Systems in Robotics: Efficient Solutions to the NPnP Problem** — Kneip, Furgale, Siegwart — *ICRA*, 2013 `[B]`. [kneip2013npnp]
- **gDLS: A Scalable Solution to the Generalized Pose and Scale Problem** — Sweeney, Fragoso, Höllerer, Turk — *ECCV*, 2014 `[B]`. Pose + scale, dùng khi ghép bản đồ. [sweeney2014gdls]
- **gDLS\*: Generalized Pose-and-Scale Estimation Given Scale and Gravity Priors** — Fragoso, DeGol, Hua — *CVPR*, 2020 `[B]`. [fragoso2020gdlsstar]
- **Generalized Pose-and-Scale Estimation using 4-Point Congruence Constraints** — Fragoso, Sinha — *3DV*, 2020 `[B]`. [fragoso2020gp4pc]
- **Minimal Solvers for Generalized Pose and Scale Estimation from Two Rays and One Point** — Camposeco, Sattler, Pollefeys — *ECCV*, 2016 `[B]`. [camposeco2016pose]
- **A General Solution to the P4P Problem for Camera with Unknown Focal Length** — Bujnak, Kukelova, Pajdla — *CVPR*, 2008 `[A]`. P4Pf. [bujnak2008p4pf]
- **Exhaustive Linearization for Robust Camera Pose and Focal Length Estimation** — Penate-Sanchez, Andrade-Cetto, Moreno-Noguer — *IEEE T-PAMI*, 2013 `[B]`. Thứ mà cờ `SOLVEPNP_UPNP` của OpenCV thực sự trỏ tới. [penate2013exhaustive]
- **Real-Time Solution to the Absolute Pose Problem with Unknown Radial Distortion and Focal Length** — Kukelova, Bujnak, Pajdla — *ICCV*, 2013 `[A]`. P4Pfr. [kukelova2013p4pfr]
- **A Direct Least-Squares Solution to the PnP Problem with Unknown Focal Length** — Zheng, Kneip — *CVPR*, 2016 `[B]`. [zheng2016dlsf]
- **A Versatile Approach for Solving PnP, PnPf, and PnPfr Problems** — Nakano — *ECCV*, 2016 `[B]`. [nakano2016versatile]
- **Making Minimal Solvers for Absolute Pose Estimation Compact and Robust** — Larsson, Kukelova, Zheng — *ICCV*, 2017 `[B]`. [larsson2017compact]
- **Revisiting Radial Distortion Absolute Pose** — Larsson, Sattler, Kukelova, Pollefeys — *ICCV*, 2019 `[B]`. Bộ giải tối thiểu đầu tiên ước lượng *mô hình méo* (không phải mô hình khử méo) cùng pose. [larsson2019radial]
- **R6P — Rolling Shutter Absolute Pose Problem** — Albl, Kukelova, Pajdla — *CVPR*, 2015 `[B]`. [albl2015r6p]
- **Rolling Shutter Absolute Pose Problem with Known Vertical Direction** — Albl, Kukelova, Pajdla — *CVPR*, 2016 `[B]`. [albl2016rsvertical]
- ★ **Rolling Shutter Camera Absolute Pose** — Albl, Kukelova, Larsson, Pajdla — *IEEE T-PAMI*, 2020 `[B]`. Bản tạp chí tổng hợp nhánh rolling shutter — đọc bài này thay cho các bài hội nghị. [albl2020rolling]
- **Minimal Rolling Shutter Absolute Pose with Unknown Focal Length and Radial Distortion** — Kukelova, Albl, Sugimoto, Schindler, Pajdla — *ECCV*, 2020 `[B]`. [kukelova2020rsfr]
- **Scanline Homographies for Rolling-Shutter Plane Absolute Pose** — Bai, Sengupta, Bartoli — *CVPR*, 2022 `[B]`. Rolling shutter + target phẳng, không giả định mô hình chuyển động cụ thể. [bai2022scanline]
- **Order-One Rolling Shutter Cameras** — Hahn, Kohn, Marigliano, Pajdla — *CVPR*, 2025 `[B]`. Lý thuyết; chỉ chạm một phần vào pose tuyệt đối. [hahn2025orderone]
- **Absolute Pose for Cameras under Flat Refractive Interfaces** — Haner, Åström — *CVPR*, 2015 `[B]`. Camera sau kính phẳng. [haner2015refractive]
- **Camera Resection from Known Line Pencils and a Radially Distorted Scanline** — Dibene, Dunn — *CVPR*, 2025 `[C]`. Bài toán hẹp, rất mới. [dibene2025pencils]

## 7. Biết hướng trọng lực (prior từ IMU)

Với IMU, hai trong ba bậc tự do quay đã biết, nên bài toán tối thiểu tụt từ ba điểm xuống hai.
Đây là nhánh nối thẳng sang `../C-he-thong-slam-day-du/15-hop-nhat-da-cam-bien/` (cây
`IMU_Fusion/` mà `../README.md` nhắc tới chưa có trong repo) và là lợi thế thực tế lớn cho robot và AR.

- ★ **Closed-Form Solutions to Minimal Absolute Pose Problems with Known Vertical Direction** — Kukelova, Bujnak, Pajdla — *ACCV 2010* (kỷ yếu 2011) `[A]`. P2P; là `up2p` trong PoseLib. [kukelova2010vertical]
- **Efficient Computation of Absolute Pose for Gravity-Aware Augmented Reality** — Sweeney, Flynn, Nuernberger, Turk, Höllerer — *ISMAR*, 2015 `[B]`. [sweeney2015gravity]
- **Absolute Pose from One or Two Scaled and Oriented Features** — Ventura, Kukelova, Sattler, Baráth — *CVPR*, 2024 `[B]`. Dùng scale + hướng của keypoint; một tương ứng là đủ khi biết trọng lực. [ventura2024scaled]

## 8. Điểm, đường, tương ứng affine: PnL, PnPL, P1AC

Đường thẳng sống sót ở những nơi điểm đặc trưng chết (vùng ít texture, nhân tạo), nên PnL và
PnPL quan trọng cho SLAM trong nhà.

- **Globally Optimal Pose Estimation from Line Correspondences** — Mirzaei, Roumeliotis — *ICRA*, 2011 `[B]`. [mirzaei2011pnl]
- ★ **Pose Estimation from Line Correspondences: A Complete Analysis and a Series of Solutions** — Xu, Zhang, Cheng, Koch — *IEEE T-PAMI*, 2017 `[A]`. [xu2017pnl]
- **Accurate and Linear Time Pose Estimation from Points and Lines** — Vakhitov, Funke, Moreno-Noguer — *ECCV*, 2016 `[B]`. EPnPL, OPnPL. [vakhitov2016pnpl]
- **A Complete, Accurate and Efficient Solution for the Perspective-N-Line Problem** — Zhou, Koppel, Kaess — *IEEE RA-L*, 2021 `[B]`. Một bộ giải cho cả trường hợp tối thiểu lẫn bình phương tối thiểu. [zhou2021pnl]
- **Image-Based Localization Using Hybrid Feature Correspondences** — Josephson, Byröd, Kahl, Åström — *CVPR*, 2007 `[B]`. Nguồn của `p2p2pl` trong PoseLib. [josephson2007hybrid]
- **Efficient Solution of Point-Line Absolute Pose** — Hruby, Duff, Pollefeys — *CVPR*, 2024 `[B]`. `p2p1ll`, `p1p2ll` trong PoseLib. [hruby2024pointline]
- **P1AC: Revisiting Absolute Pose From a Single Affine Correspondence** — Ventura, Kukelova, Sattler, Baráth — *ICCV*, 2023 `[B]`. [ventura2023p1ac]
- **Hybrid Camera Pose Estimation** — Camposeco, Cohen, Pollefeys, Sattler — *CVPR*, 2018 `[B]`. Trộn tương ứng 2D–3D và 2D–2D trong cùng RANSAC. [camposeco2018hybrid]

## 9. Bất định, nhiễu bất đẳng hướng, suy biến

Phần lớn bộ giải giả định nhiễu pixel đẳng hướng và bằng nhau ở mọi điểm. Nhóm này bỏ giả thiết
đó — và là nhóm nối thẳng vào `../A-nguyen-ly-va-toan-hoc/06-bat-dinh-va-lan-truyen-sai-so/`.

- ★ **MLPnP — A Real-Time Maximum Likelihood Solution to the PnP Problem** — Urban, Leitloff, Hinz — *ISPRS Annals*, 2016 `[B]`. Đưa covariance của tia chiếu vào bộ giải. [urban2016mlpnp]
- **Leveraging Feature Uncertainty in the PnP Problem** (CEPnP) — Ferraz, Binefa, Moreno-Noguer — *BMVC*, 2014 `[B]`. [ferraz2014cepnp]
- **Very Fast Solution to the PnP Problem with Algebraic Outlier Rejection** (REPPnP) — Ferraz, Binefa, Moreno-Noguer — *CVPR*, 2014 `[B]`. Loại ngoại lai ngay trong bộ giải, không qua RANSAC. [ferraz2014reppnp]
- ★ **Uncertainty-Aware Camera Pose Estimation from Points and Lines** — Vakhitov, Ferraz, Agudo, Moreno-Noguer — *CVPR*, 2021 `[B]`. Bất định ở **cả** 2D lẫn 3D. [vakhitov2021uncertainty]
- **Generalized Maximum Likelihood Estimation for PnP Problem** — Zhan, Xu, Zhang, Zhu — *IEEE RA-L*, 2025 `[B]`. Ước lượng đồng thời pose và covariance. [zhan2025gmlpnp]
- **Object Pose Estimation with Statistical Guarantees: Conformal Keypoint Detection and Geometric Uncertainty Propagation** — Yang, Pavone — *CVPR*, 2023 `[B]`. Vùng bất định của pose với cận sai số tệ nhất có chứng minh. [yang2023conformal]
- **Algebra and Geometry of Camera Resectioning** — Connelly, Duff, Loucks-Tavitas — *Mathematics of Computation*, 2025 `[B]`. Nền đại số; gần nhất với một bài về cấu hình suy biến. [connelly2025resection]

## 10. Ước lượng bền vững: họ RANSAC

- ★ **Random Sample Consensus** — Fischler, Bolles — *Communications of the ACM*, 1981 `[A]`. RANSAC ra đời trong chính bài toán định vị từ điểm mốc. [fischler1981ransac]
- **Locally Optimized RANSAC** — Chum, Matas, Kittler — *DAGM*, 2003 `[A]`. [chum2003lo]
- ★ **USAC: A Universal Framework for Random Sample Consensus** — Raguram, Chum, Pollefeys, Matas, Frahm — *IEEE T-PAMI*, 2013 `[A]`. Khung tổng hợp mọi cải tiến RANSAC tới 2013. [raguram2013usac]
- **Graph-Cut RANSAC** — Barath, Matas — *CVPR*, 2018 `[A]`. [barath2018gcransac]
- **MAGSAC++, a Fast, Reliable and Accurate Robust Estimator** — Barath, Noskova, Ivashechkin, Matas — *CVPR*, 2020 `[A]`. [barath2020magsacpp]
- **Neural-Guided RANSAC** — Brachmann, Rother — *ICCV*, 2019 `[B]`. [brachmann2019ngransac]
- **Learning to Find Good Models in RANSAC** — Barath, Cavalli, Pollefeys — *CVPR*, 2022 `[B]`. [barath2022learning]
- **Space-Partitioning RANSAC** — Barath, Valasek — *ECCV*, 2022 `[B]`. [barath2022sprt]
- **Generalized Differentiable RANSAC** — Wei, Patel, Shekhovtsov, Matas, Barath — *ICCV*, 2023 `[B]`. [wei2023gdransac]
- **Globally-Optimal Inlier Set Maximisation for Simultaneous Camera Pose and Feature Correspondence** — Campbell, Petersson, Kneip, Li — *ICCV*, 2017 `[B]`. [campbell2017bnb]
- **SupeRANSAC: One RANSAC to Rule Them All** — Barath — *arXiv preprint*, 2025 `[C]`. Phân tích chi tiết nào thực sự làm RANSAC chạy tốt cho từng bài toán, kể cả absolute pose. **Chưa qua phản biện** — gợi ý, không phải bằng chứng. [barath2025superansac]

## 11. Không biết trước tương ứng (blind PnP)

- **SoftPOSIT: Simultaneous Pose and Correspondence Determination** — David, DeMenthon, Duraiswami, Samet — *IJCV*, 2004 `[A]`. [david2004softposit]
- **Pose Priors for Simultaneously Solving Alignment and Correspondence** — Moreno-Noguer, Lepetit, Fua — *ECCV*, 2008 `[B]`. [morenonoguer2008priors]
- **Solving the Blind PnP Problem End-to-End with Robust Differentiable Geometric Optimization** — Campbell, Liu, Gould — *ECCV*, 2020 `[B]`. [campbell2020blindpnp]
- **Efficient and Outlier-Robust Simultaneous Pose and Correspondence Determination by Branch-and-Bound and Transformation Decomposition** — Wang, Liu, Wang, Li, Wang — *IEEE T-PAMI*, 2022 `[B]`. [wang2022rif]
- **Is Geometry Enough for Matching in Visual Localization?** (GoMatch) — Zhou, Agostinho, Ošep, Leal-Taixé — *ECCV*, 2022 `[B]`. [zhou2022gomatch]
- **MinCD-PnP: Learning 2D-3D Correspondences with Approximate Blind PnP** — An et al. — *ICCV*, 2025 `[C]`. [an2025mincdpnp]

## 12. PnP khả vi và PnP trong mạng học sâu

Có ba lập trường, và đây là chỗ có **bất đồng thực sự** đáng theo dõi: (a) học tương ứng, giữ
PnP-RANSAC cổ điển ở cuối (PVNet, ZebraPose, SurfEmb); (b) cho gradient đi xuyên qua PnP
(DSAC, BPnP, EPro-PnP); (c) thay hẳn PnP bằng mô-đun học (GDR-Net, GDRNPP). Liu và cộng sự
(ICCV 2023) tuyên bố PnP khả vi gặp vấn đề "lấy trung bình" khi huấn luyện `[T]` — một câu hỏi
mở của `00-cau-hoi.md` câu 8.

- ★ **DSAC — Differentiable RANSAC for Camera Localization** — Brachmann et al. — *CVPR*, 2017 `[A]`. [brachmann2017dsac]
- **Learning Less is More — 6D Camera Localization via 3D Surface Regression** (DSAC++) — Brachmann, Rother — *CVPR*, 2018 `[A]`. [brachmann2018dsacpp]
- **Expert Sample Consensus Applied to Camera Re-Localization** — Brachmann, Rother — *ICCV*, 2019 `[B]`. [brachmann2019esac]
- ★ **Visual Camera Re-Localization from RGB and RGB-D Images Using DSAC** (DSAC\*) — Brachmann, Rother — *IEEE T-PAMI*, 2022 `[A]`. PnP-RANSAC khả vi mà ACE, GLACE, ACE0 đều dùng lại. [brachmann2021dsacstar]
- **PVNet: Pixel-Wise Voting Network for 6DoF Pose Estimation** — Peng, Liu, Huang, Zhou, Bao — *CVPR*, 2019 `[A]`. [peng2019pvnet]
- ★ **End-to-End Learnable Geometric Vision by Backpropagating PnP Optimization** (BPnP) — Chen, Parra, Cao, Li, Chin — *CVPR*, 2020 `[B]`. Đạo hàm qua PnP bằng định lý hàm ẩn. [chen2020bpnp]
- **GDR-Net: Geometry-Guided Direct Regression Network for Monocular 6D Object Pose Estimation** — Wang, Manhardt, Tombari, Ji — *CVPR*, 2021 `[B]`. [wang2021gdrnet]
- ★ **EPro-PnP: Generalized End-to-End Probabilistic Perspective-n-Points for Monocular Object Pose Estimation** — Chen, Wang, Wang, Tian, Xiong, Li — *CVPR*, 2022 `[B]`; bản mở rộng *IEEE T-PAMI*, 2025. PnP xuất phân bố pose trên SE(3). [chen2022epropnp, chen2025epropnp]
- **ZebraPose: Coarse to Fine Surface Encoding for 6DoF Object Pose Estimation** — Su et al. — *CVPR*, 2022 `[B]`. [su2022zebrapose]
- **SurfEmb: Dense and Continuous Correspondence Distributions for Object Pose Estimation** — Haugaard, Buch — *CVPR*, 2022 `[B]`. [haugaard2022surfemb]
- **Linear-Covariance Loss for End-to-End Learning of 6D Pose Estimation** — Liu, Hu, Salzmann — *ICCV*, 2023 `[B]`. [liu2023lincov]
- **GDRNPP: A Geometry-Guided and Fully Learning-Based Object Pose Estimator** — Liu et al. — *IEEE T-PAMI*, 2025 `[A]`. [liu2025gdrnpp]

## 13. PnP trong định vị thị giác

Chỉ giữ công trình mà đóng góp chạm vào bước giải pose. ACE, GLACE, ACE0, R-SCoRe đóng góp chủ
yếu ở biểu diễn cảnh; chúng ở đây vì là SOTA của pipeline *scene coordinate regression → PnP-RANSAC*,
không phải vì cải tiến PnP.

- **Back to the Feature: Learning Robust Camera Localization from Pixels to Pose** (PixLoc) — Sarlin et al. — *CVPR*, 2021 `[B]`. Tinh chỉnh pose bằng căn chỉnh đặc trưng học được, thay sai số tái chiếu. [sarlin2021pixloc]
- **Accelerated Coordinate Encoding** (ACE) — Brachmann, Cavallari, Prisacariu — *CVPR*, 2023 `[B]`. [brachmann2023ace]
- **GLACE: Global Local Accelerated Coordinate Encoding** — Wang, Jiang, Galliani, Vogel, Pollefeys — *CVPR*, 2024 `[B]`. [wang2024glace]
- **Scene Coordinate Reconstruction** (ACE0) — Brachmann et al. — *ECCV*, 2024 `[B]`. SfM chỉ bằng SCR + PnP-RANSAC. [brachmann2024ace0]
- **R-SCoRe: Revisiting Scene Coordinate Regression for Robust Large-Scale Visual Localization** — Jiang, Wang, Galliani, Vogel, Pollefeys — *CVPR*, 2025 `[C]`. [jiang2025rscore]

## 14. Công cụ dựng bộ giải tối thiểu

Nền hình học đại số mà `00-cau-hoi.md` liệt kê là "chưa có trong cây".

- **Automatic Generator of Minimal Problem Solvers** — Kukelova, Bujnak, Pajdla — *ECCV*, 2008 `[A]`. [kukelova2008generator]
- **Efficient Solvers for Minimal Problems by Syzygy-Based Reduction** — Larsson, Åström, Oskarsson — *CVPR*, 2017 `[A]`. [larsson2017syzygy]
- **Efficient Intersection of Three Quadrics and Applications in Computer Vision** (E3Q3) — Kukelova, Heller, Fitzgibbon — *CVPR*, 2016 `[A]`. Bộ giải PoseLib dùng cho `gp3p`, `p4pf`. [kukelova2016quadrics]
- **Learning to Solve Hard Minimal Problems** — Hruby, Duff, Leykin, Pajdla — *CVPR*, 2022 `[B]`. [hruby2022hard]

---

## Cạm bẫy phát hiện ngay trong lúc kiểm nguồn

Đọc thẳng header `calib3d.hpp` của OpenCV 4.x ngày 2026-09-25 (không phải tài liệu thứ cấp):

- `SOLVEPNP_P3P` **không còn** là Gao 2003 như nhiều tutorial cũ ghi — nó đã trỏ sang Ding 2023.
- `SOLVEPNP_DLS` và `SOLVEPNP_UPNP` được ghi là *"Broken implementation"* và **âm thầm chạy EPnP**.
  Code gọi hai cờ này sẽ không báo lỗi, chỉ ra kết quả của một thuật toán khác.
- `SOLVEPNP_UPNP` trỏ tới Penate-Sanchez 2013, **không phải** UPnP của Kneip 2014 dù trùng tên.
- `SOLVEPNP_P3P` / `SOLVEPNP_AP3P` đòi **đúng 4 điểm**: ba điểm để giải, điểm thứ tư để chọn nghiệm.

Cũng trong lúc kiểm: trang ECVA gắn DOI của SQPnP là `…-58452-8_27`, nhưng DOI đó thuộc một bài
khác; DOI đúng (Crossref) là `…-58452-8_28`. Một ví dụ cụ thể cho quy tắc "không đoán DOI, không
chép DOI từ trang tổng hợp".

## Khoảng trống ban đầu (chưa phải kết luận — mới ở mức tìm kiếm)

- Không có **bài tổng quan PnP** ở venue đầu ngành trong 2021–2026.
- Không thấy bài riêng về **cấu hình suy biến (critical configuration)** của PnP ở venue thị giác;
  gần nhất là bài toán học connelly2025resection.
- Không thấy **PnP học được** ở NeurIPS/ICLR; nhánh này sống ở CVPR/ICCV/ECCV và T-PAMI.
- Câu hỏi 4 và 5 trong `00-cau-hoi.md` (con số có so được với nhau không; bộ giải dạng đóng còn
  quan trọng tới đâu khi đã có LM) — chưa bài nào trong danh mục được thiết kế để trả lời trực tiếp.
  Đây là ứng viên đầu tiên cho một thí nghiệm nhỏ trong `code/` khi viết bài học.
