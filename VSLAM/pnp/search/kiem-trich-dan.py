"""Kiểm máy: mọi trích đoạn nguyên văn trong notes/<bibkey>.md có thật trong papers/<bibkey>.pdf
và nằm đúng trang [tr. N] đã ghi. Cần pdfminer.six. PDF phải tải trước bằng papers/fetch.sh
(hoặc nguồn ghi trong đầu ghi chú).

Dùng:  python3 search/kiem-trich-dan.py            # mọi ghi chú
       python3 search/kiem-trich-dan.py lepetit2009epnp
Trích đoạn nhận dạng: dòng bắt đầu bằng '- "' hoặc '- “' và có '[tr. N]' ở cuối.
Có thể dùng '…' hoặc '...' trong trích để bỏ đoạn giữa; mỗi mảnh được kiểm riêng.
"""
import os, re, sys, unicodedata, glob
from pdfminer.high_level import extract_text
from pdfminer.pdfpage import PDFPage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CACHE = os.path.join(ROOT, "papers", ".txtcache")


def norm(s):
    s = unicodedata.normalize("NFKC", s)
    s = s.replace("ﬁ", "fi").replace("ﬂ", "fl").replace("’", "'").replace("‘", "'")
    s = s.replace("“", '"').replace("”", '"').replace("–", "-").replace("—", "-").replace("−", "-")
    s = re.sub(r"-\s*\n\s*", "", s)          # nối từ bị ngắt dòng
    s = re.sub(r"[^0-9a-zA-Z]+", " ", s).lower()
    return re.sub(r"\s+", " ", s).strip()


def pages(key):
    os.makedirs(CACHE, exist_ok=True)
    c = os.path.join(CACHE, key + ".txt")
    pdf = os.path.join(ROOT, "papers", key + ".pdf")
    if not os.path.exists(c):
        n = len(list(PDFPage.get_pages(open(pdf, "rb"))))
        with open(c, "w") as fh:
            for i in range(n):
                fh.write(f"\f=== {i+1} ===\n" + extract_text(pdf, page_numbers=[i]))
    raw = open(c).read().split("\f")[1:]
    return [norm(p.split("\n", 1)[1]) for p in raw]


def check(key):
    note = os.path.join(ROOT, "notes", key + ".md")
    pg = pages(key)
    full = " ".join(pg)
    ok = bad = 0
    for line in open(note):
        m = re.match(r'\s*-\s*["“](.+)["”]\s*\[tr\.\s*(\d+)(?:[–-](\d+))?\]', line.strip())
        if not m:
            continue
        quote, p1 = m.group(1), int(m.group(2))
        p2 = int(m.group(3) or p1)
        frags = [norm(f) for f in re.split(r"…|\.\.\.", quote) if norm(f)]
        where = " ".join(pg[max(0, p1 - 2):min(len(pg), p2 + 1)])   # cho phép lệch 1 trang
        if all(f in where for f in frags):
            ok += 1
        else:
            anywhere = all(f in full for f in frags)
            bad += 1
            print(f"  !! {key}: {'SAI TRANG' if anywhere else 'KHÔNG TÌM THẤY'} [tr. {m.group(2)}] \"{quote[:70]}…\"")
    print(f"{'ok' if bad == 0 and ok else '!!'}  {key}: {ok} trích khớp, {bad} không khớp")
    return bad == 0 and ok > 0


if __name__ == "__main__":
    keys = sys.argv[1:] or sorted(os.path.basename(p)[:-3] for p in glob.glob(os.path.join(ROOT, "notes", "*.md"))
                                  if not os.path.basename(p).startswith("00-"))
    res = [check(k) for k in keys]
    sys.exit(0 if all(res) else 1)
