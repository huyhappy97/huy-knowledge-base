# Quét toàn bộ danh sách bài của CVF open access và ECVA, lọc tiêu đề theo biểu thức PnP.
# Dùng: python3 quet-cvf-ecva.py > ket-qua.txt
# Lượt chạy ngày 2026-09-25 quét CVPR 2021–2025, ICCV 2021/2023/2025, WACV 2024/2025, ECCV 2018–2024.
# (CVPR 2019/2020, ICCV 2019 dùng định dạng trang khác, chưa quét — xem search-log.md.)
import re, urllib.request
PAT = re.compile(r'perspective-n|\bpnp|p3p|p4p|absolute pose|absolute camera pose|camera resection|'
                 r'resectioning|pose solver|minimal solver|minimal problem|ransac|scene coordinate|'
                 r'point-line|\bpnl\b|6d object pose|6dof object pose|object pose estimation|gravity|'
                 r'upright|rolling shutter|differentiable.*pose|pose.*uncertaint|certifi', re.I)
def get(u):
    req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=120).read().decode("utf-8", "ignore")
for conf in ["CVPR2021", "CVPR2022", "CVPR2023", "CVPR2024", "CVPR2025",
             "ICCV2021", "ICCV2023", "ICCV2025", "WACV2024", "WACV2025"]:
    s = get(f"https://openaccess.thecvf.com/{conf}?day=all")
    for link, t in re.findall(r'<dt class="ptitle"><br><a href="([^"]+)">([^<]+)</a></dt>', s):
        if PAT.search(t):
            print(conf, "|", t.strip(), "|", "https://openaccess.thecvf.com" + link.replace("/html/", "/papers/").replace(".html", ".pdf"))
s = get("https://www.ecva.net/papers.php")
for t, rest in re.findall(r'<dt class="ptitle">(.*?)</dt>(.*?)(?=<dt class="ptitle">|$)', s, re.S):
    tt = re.sub("<[^>]+>", "", t).strip()
    if PAT.search(tt):
        pdf = re.search(r"href=['\"]([^'\"]*papers_ECCV/papers/[^'\"]*\.pdf)", rest)
        yr = re.search(r"eccv_(\d{4})", rest)
        print("ECCV" + (yr.group(1) if yr else "?"), "|", tt, "|", ("https://www.ecva.net/" + pdf.group(1)) if pdf else "")
