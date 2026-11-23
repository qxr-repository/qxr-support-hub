"""Build data/rosslare-kb-index.json from the public Rosslare support portal KB
(support.rosslaresecurity.com, Zoho Desk). Uses the same public, no-login
endpoints the portal's own knowledge base pages load from.

Usage: python scripts/build_rosslare_index.py [output.json]
"""
import json, re, sys, html, urllib.request, concurrent.futures as cf

OUT = sys.argv[1] if len(sys.argv) > 1 else "data/rosslare-kb-index.json"
SITE = "https://support.rosslaresecurity.com"
API = SITE + "/portal/api/"
UA = {"User-Agent": "qxr-support-hub-indexer"}

def fetch(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
        return r.read().decode("utf-8", "replace")

page = fetch(SITE + "/portal/en/kb/knowledge-base")
m = re.search(r"portalId\\x22:\\x22([a-z0-9]+)", page) or re.search(r'"portalId"\s*:\s*"([a-z0-9]+)"', page)
if not m:
    sys.exit("Could not find the portal ID on the knowledge base page.")
P = m.group(1)

arts, start = [], 1
while True:
    batch = json.loads(fetch(f"{API}kbArticles?portalId={P}&locale=en&from={start}&limit=50")).get("data", [])
    arts += batch
    if len(batch) < 50:
        break
    start += 50

def text(h):
    h = re.sub(r"(?is)<(script|style).*?</\1>", "", h or "")
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", h))).strip()

def detail(a):
    try:
        return a, json.loads(fetch(f"{API}kbArticles/{a['id']}?portalId={P}")).get("answer", "")
    except Exception as e:
        print("FAILED", a.get("webUrl"), e, file=sys.stderr); return a, ""

with cf.ThreadPoolExecutor(4) as ex:
    out = [{"t": a["title"].strip(), "u": a["webUrl"],
            "c": (a.get("category") or {}).get("name", ""),
            "d": re.sub(r"\s+", " ", a.get("summary") or "").strip()[:200],
            "b": text(h)} for a, h in ex.map(detail, arts)]
out.sort(key=lambda a: a["t"].lower())
if len(out) < 20:
    sys.exit(f"Only {len(out)} articles found; refusing to overwrite the index.")
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print(f"{len(out)} Rosslare articles -> {OUT}")
