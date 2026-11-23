"""Build data/qumulex-kb-index.json from the public Qumulex KB (www.qumulex.com/kb).

Reads the site sitemap, fetches each KB article, and stores title, URL,
category path, meta description and article text for the hub's type-ahead search.
Usage: python scripts/build_qumulex_index.py [output.json]
"""
import json, re, sys, html, urllib.request, concurrent.futures as cf
from bs4 import BeautifulSoup

OUT = sys.argv[1] if len(sys.argv) > 1 else "data/qumulex-kb-index.json"
SITEMAP = "https://www.qumulex.com/sitemap.xml"
SKIP = {"https://www.qumulex.com/kb", "https://www.qumulex.com/kb/kb-search-results", "https://www.qumulex.com/kb/kb-404"}
UA = {"User-Agent": "qxr-support-hub-indexer"}

def fetch(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
        return r.read().decode("utf-8", "replace")

urls = [u for u in re.findall(r"<loc>([^<]+)</loc>", fetch(SITEMAP))
        if "qumulex.com/kb" in u and u not in SKIP]

def parse(url):
    try:
        s = BeautifulSoup(fetch(url), "html.parser")
    except Exception as e:
        print("FAILED", url, e, file=sys.stderr); return None
    art = s.select_one("article")
    if not art:
        return None
    title = s.title.get_text(strip=True) if s.title else url
    if title.upper().startswith("[INTERNAL]"):
        return None
    crumbs = [x.get_text(strip=True) for x in s.select(".hs-kb-breadcrumb_item")]
    md = s.find("meta", attrs={"name": "description"})
    desc = re.sub(r"\s+", " ", html.unescape(md["content"])).strip()[:200] if md else ""
    body = re.sub(r"\s+", " ", art.get_text(" ", strip=True))
    if body.startswith(title):
        body = body[len(title):].strip()
    return {"t": title, "u": url, "c": " › ".join(crumbs[1:]), "d": desc, "b": body}

with cf.ThreadPoolExecutor(6) as ex:
    out = [a for a in ex.map(parse, urls) if a]
out.sort(key=lambda a: a["t"].lower())
if len(out) < 20:
    sys.exit(f"Only {len(out)} articles found; refusing to overwrite the index.")
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print(f"{len(out)} Qumulex articles -> {OUT}")
