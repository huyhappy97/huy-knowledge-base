#!/usr/bin/env bash
# Tải bản PDF open-access của các công trình trong ../refs.bib, đặt tên theo bibkey
# (research-rules.md mục 1: papers/<bibkey>.pdf). PDF KHÔNG được commit (xem .gitignore).
#
# Mỗi URL dưới đây đã được kiểm ngày 2026-09-25: trả HTTP 200, content-type application/pdf.
# Chỉ có bản open-access chính thức (CVF open access, ECVA, Copernicus). Bài IEEE / Springer
# / Elsevier không có bản mở thì không nằm ở đây — mở qua DOI trong refs.bib.
#
#   ./fetch.sh            tải mọi bài còn thiếu
#   ./fetch.sh ding2023p3p lepetit2009epnp   chỉ tải các khoá chỉ định
set -u
cd "$(dirname "$0")"
CVF=https://openaccess.thecvf.com
ECVA=https://www.ecva.net/papers
declare -A URL=(
  # --- P3P và bài toán tối thiểu ---
  [ding2023p3p]="$CVF/content/CVPR2023/papers/Ding_Revisiting_the_P3P_Problem_CVPR_2023_paper.pdf"
  [ke2017p3p]="$CVF/content_cvpr_2017/papers/Ke_An_Efficient_Algebraic_CVPR_2017_paper.pdf"
  [persson2018lambdatwist]="$CVF/content_ECCV_2018/papers/Mikael_Persson_Lambda_Twist_An_ECCV_2018_paper.pdf"
  # --- PnP n điểm ---
  [zheng2013opnp]="$CVF/content_iccv_2013/papers/Zheng_Revisiting_the_PnP_2013_ICCV_paper.pdf"
  [terzakis2020sqpnp]="$ECVA/eccv_2020/papers_ECCV/papers/123460460.pdf"
  [urban2016mlpnp]="https://isprs-annals.copernicus.org/articles/III-3/131/2016/isprs-annals-III-3-131-2016.pdf"
  [ferraz2014reppnp]="$CVF/content_cvpr_2014/papers/Ferraz_Very_Fast_Solution_2014_CVPR_paper.pdf"
  # --- camera không chuẩn ---
  [kukelova2013p4pfr]="$CVF/content_iccv_2013/papers/Kukelova_Real-Time_Solution_to_2013_ICCV_paper.pdf"
  [zheng2016dlsf]="$CVF/content_cvpr_2016/papers/Zheng_A_Direct_Least-Squares_CVPR_2016_paper.pdf"
  [larsson2017compact]="$CVF/content_ICCV_2017/papers/Larsson_Making_Minimal_Solvers_ICCV_2017_paper.pdf"
  [larsson2019radial]="$CVF/content_ICCV_2019/papers/Larsson_Revisiting_Radial_Distortion_Absolute_Pose_ICCV_2019_paper.pdf"
  [albl2015r6p]="$CVF/content_cvpr_2015/papers/Albl_R6P_-_Rolling_2015_CVPR_paper.pdf"
  [albl2016rsvertical]="$CVF/content_cvpr_2016/papers/Albl_Rolling_Shutter_Absolute_CVPR_2016_paper.pdf"
  [kukelova2020rsfr]="$ECVA/eccv_2020/papers_ECCV/papers/123500681.pdf"
  [bai2022scanline]="$CVF/content/CVPR2022/papers/Bai_Scanline_Homographies_for_Rolling-Shutter_Plane_Absolute_Pose_CVPR_2022_paper.pdf"
  [camposeco2018hybrid]="$CVF/content_cvpr_2018/papers/Camposeco_Hybrid_Camera_Pose_CVPR_2018_paper.pdf"
  [ventura2023p1ac]="$CVF/content/ICCV2023/papers/Ventura_P1AC_Revisiting_Absolute_Pose_From_a_Single_Affine_Correspondence_ICCV_2023_paper.pdf"
  [ventura2024scaled]="$CVF/content/CVPR2024/papers/Ventura_Absolute_Pose_from_One_or_Two_Scaled_and_Oriented_Features_CVPR_2024_paper.pdf"
  [dibene2025pencils]="$CVF/content/CVPR2025/papers/Dibene_Camera_Resection_from_Known_Line_Pencils_and_a_Radially_Distorted_CVPR_2025_paper.pdf"
  # --- điểm + đường ---
  [vakhitov2021uncertainty]="$CVF/content/CVPR2021/papers/Vakhitov_Uncertainty-Aware_Camera_Pose_Estimation_From_Points_and_Lines_CVPR_2021_paper.pdf"
  [hruby2024pointline]="$CVF/content/CVPR2024/papers/Hruby_Efficient_Solution_of_Point-Line_Absolute_Pose_CVPR_2024_paper.pdf"
  # --- bộ giải tối thiểu: công cụ ---
  [kukelova2016quadrics]="$CVF/content_cvpr_2016/papers/Kukelova_Efficient_Intersection_of_CVPR_2016_paper.pdf"
  [larsson2017syzygy]="$CVF/content_cvpr_2017/papers/Larsson_Efficient_Solvers_for_CVPR_2017_paper.pdf"
  [hruby2022hard]="$CVF/content/CVPR2022/papers/Hruby_Learning_To_Solve_Hard_Minimal_Problems_CVPR_2022_paper.pdf"
  # --- bền vững ---
  [barath2018gcransac]="$CVF/content_cvpr_2018/papers/Barath_Graph-Cut_RANSAC_CVPR_2018_paper.pdf"
  [barath2020magsacpp]="$CVF/content_CVPR_2020/papers/Barath_MAGSAC_a_Fast_Reliable_and_Accurate_Robust_Estimator_CVPR_2020_paper.pdf"
  [barath2022learning]="$CVF/content/CVPR2022/papers/Barath_Learning_To_Find_Good_Models_in_RANSAC_CVPR_2022_paper.pdf"
  [barath2022sprt]="$ECVA/eccv_2022/papers_ECCV/papers/136920715.pdf"
  [wei2023gdransac]="$CVF/content/ICCV2023/papers/Wei_Generalized_Differentiable_RANSAC_ICCV_2023_paper.pdf"
  [campbell2017bnb]="$CVF/content_ICCV_2017/papers/Campbell_Globally-Optimal_Inlier_Set_ICCV_2017_paper.pdf"
  # --- không tương ứng, khả vi, học sâu ---
  [campbell2020blindpnp]="$ECVA/eccv_2020/papers_ECCV/papers/123470239.pdf"
  [an2025mincdpnp]="$CVF/content/ICCV2025/papers/An_MinCD-PnP_Learning_2D-3D_Correspondences_with_Approximate_Blind_PnP_ICCV_2025_paper.pdf"
  [brachmann2017dsac]="$CVF/content_cvpr_2017/papers/Brachmann_DSAC_-_Differentiable_CVPR_2017_paper.pdf"
  [brachmann2018dsacpp]="$CVF/content_cvpr_2018/papers/Brachmann_Learning_Less_Is_CVPR_2018_paper.pdf"
  [brachmann2019esac]="$CVF/content_ICCV_2019/papers/Brachmann_Expert_Sample_Consensus_Applied_to_Camera_Re-Localization_ICCV_2019_paper.pdf"
  [peng2019pvnet]="$CVF/content_CVPR_2019/papers/Peng_PVNet_Pixel-Wise_Voting_Network_for_6DoF_Pose_Estimation_CVPR_2019_paper.pdf"
  [chen2020bpnp]="$CVF/content_CVPR_2020/papers/Chen_End-to-End_Learnable_Geometric_Vision_by_Backpropagating_PnP_Optimization_CVPR_2020_paper.pdf"
  [wang2021gdrnet]="$CVF/content/CVPR2021/papers/Wang_GDR-Net_Geometry-Guided_Direct_Regression_Network_for_Monocular_6D_Object_Pose_CVPR_2021_paper.pdf"
  [chen2022epropnp]="$CVF/content/CVPR2022/papers/Chen_EPro-PnP_Generalized_End-to-End_Probabilistic_Perspective-N-Points_for_Monocular_Object_Pose_Estimation_CVPR_2022_paper.pdf"
  [su2022zebrapose]="$CVF/content/CVPR2022/papers/Su_ZebraPose_Coarse_To_Fine_Surface_Encoding_for_6DoF_Object_Pose_CVPR_2022_paper.pdf"
  [haugaard2022surfemb]="$CVF/content/CVPR2022/papers/Haugaard_SurfEmb_Dense_and_Continuous_Correspondence_Distributions_for_Object_Pose_Estimation_CVPR_2022_paper.pdf"
  [yang2023conformal]="$CVF/content/CVPR2023/papers/Yang_Object_Pose_Estimation_With_Statistical_Guarantees_Conformal_Keypoint_Detection_and_CVPR_2023_paper.pdf"
  [hodan2018bop]="$CVF/content_ECCV_2018/papers/Tomas_Hodan_PESTO_6D_Object_ECCV_2018_paper.pdf"
  # --- định vị thị giác ---
  [sarlin2021pixloc]="$CVF/content/CVPR2021/papers/Sarlin_Back_to_the_Feature_Learning_Robust_Camera_Localization_From_Pixels_CVPR_2021_paper.pdf"
  [brachmann2023ace]="$CVF/content/CVPR2023/papers/Brachmann_Accelerated_Coordinate_Encoding_Learning_to_Relocalize_in_Minutes_Using_RGB_CVPR_2023_paper.pdf"
  [wang2024glace]="$CVF/content/CVPR2024/papers/Wang_GLACE_Global_Local_Accelerated_Coordinate_Encoding_CVPR_2024_paper.pdf"
  [brachmann2024ace0]="$ECVA/eccv_2024/papers_ECCV/papers/07356.pdf"
  [jiang2025rscore]="$CVF/content/CVPR2025/papers/Jiang_R-SCoRe_Revisiting_Scene_Coordinate_Regression_for_Robust_Large-Scale_Visual_Localization_CVPR_2025_paper.pdf"
  # --- bổ sung từ lượt tìm 2021–2026 ---
  [wu2025conic]="$CVF/content/WACV2025/papers/Wu_A_Conic_Transformation_Approach_for_Solving_the_Perspective-Three-Point_Problem_WACV_2025_paper.pdf"
  [hahn2025orderone]="$CVF/content/CVPR2025/papers/Hahn_Order-One_Rolling_Shutter_Cameras_CVPR_2025_paper.pdf"
  [liu2023lincov]="$CVF/content/ICCV2023/papers/Liu_Linear-Covariance_Loss_for_End-to-End_Learning_of_6D_Pose_Estimation_ICCV_2023_paper.pdf"
  [brachmann2019ngransac]="$CVF/content_ICCV_2019/papers/Brachmann_Neural-Guided_RANSAC_Learning_Where_to_Sample_Model_Hypotheses_ICCV_2019_paper.pdf"
  [sattler2018benchmarking]="$CVF/content_cvpr_2018/papers/Sattler_Benchmarking_6DOF_Outdoor_CVPR_2018_paper.pdf"
  # --- tiền ấn arXiv (bản chính thức duy nhất) ---
  [barath2025superansac]="https://arxiv.org/pdf/2506.04803"
)
keys=("$@"); [ ${#keys[@]} -eq 0 ] && keys=("${!URL[@]}")
ok=0; skip=0; fail=0
for k in "${keys[@]}"; do
  u="${URL[$k]:-}"
  if [ -z "$u" ]; then echo "   ??  $k — không có bản open-access trong danh sách, mở DOI trong refs.bib"; fail=$((fail+1)); continue; fi
  if [ -s "$k.pdf" ]; then skip=$((skip+1)); continue; fi
  if curl -fsSL -A 'Mozilla/5.0' -m 120 -o "$k.pdf.part" "$u" && head -c 4 "$k.pdf.part" | grep -q '%PDF'; then
    mv "$k.pdf.part" "$k.pdf"; echo "   ok  $k"; ok=$((ok+1))
  else rm -f "$k.pdf.part"; echo "   !!  $k  ($u)"; fail=$((fail+1)); fi
done
echo "tải mới: $ok · đã có: $skip · lỗi / không có bản mở: $fail"
