# Kiểm một danh sách tên bài qua Crossref: in 3 kết quả đầu (venue, năm, trang, DOI, tác giả).
# Dùng: python3 kiem-crossref.py truy-van-1.txt   (ghi thêm truy-van-1.txt.json cạnh file)
import json, sys, time, urllib.request, urllib.parse
qs = [l.strip() for l in open(sys.argv[1]) if l.strip() and not l.startswith('#')]
out = {}
for q in qs:
    url = "https://api.crossref.org/works?" + urllib.parse.urlencode({"query.bibliographic": q, "rows": 3,
          "select": "title,DOI,container-title,issued,published-print,author,volume,issue,page,type,event", "mailto":"pnp-survey@localhost"})
    d=None
    for attempt in range(4):
        try: d = json.load(urllib.request.urlopen(url, timeout=40)); break
        except Exception as e: time.sleep(3*(attempt+1))
    items = (d or {}).get("message", {}).get("items", [])
    lines=[f"### Q: {q}"]; res=[]
    for i in items:
        au = [f"{a.get('given','')} {a.get('family','')}".strip() for a in i.get("author",[])]
        yr = (i.get("published-print") or i.get("issued") or {}).get("date-parts",[[None]])[0][0]
        r=dict(title=(i.get("title") or [""])[0], venue=(i.get("container-title") or [""])[0], year=yr,
               vol=i.get("volume"), no=i.get("issue"), pp=i.get("page"), doi=i.get("DOI"), type=i.get("type"), authors=au)
        res.append(r)
        lines.append(f"  - {yr} | {r['venue']} | {r['type']} | {r['title']}\n    {', '.join(au[:8])}{' ...' if len(au)>8 else ''}\n    vol={r['vol']} no={r['no']} pp={r['pp']} doi={r['doi']}")
    print("\n".join(lines), flush=True)
    out[q]=res
json.dump(out, open(sys.argv[1]+".json","w"), ensure_ascii=False, indent=1)
