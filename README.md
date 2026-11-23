# QXR Support Hub

Mockup of a combined support landing page for **Qumulex** and **Rosslare** (QXR Security), meant to replace axtraxng.com with one official hub.

- `index.html` – Support Hub: product cards, AxTraxNG end-of-life info, popular articles, downloads, tools, contact.
- `rosslare.html` – Rosslare section: AxTraxPro / AxTraxNG, installation guides, videos, manuals, utilities, licensing.

## Search

The hub search shows results as you type from **both** knowledge bases:

| Source | Articles | Index file |
|---|---|---|
| Qumulex KB (qumulex.com/kb, HubSpot) | ~120 | `data/qumulex-kb-index.json` |
| Rosslare KB (support.rosslaresecurity.com, Zoho Desk) | ~118 | `data/rosslare-kb-index.json` |

Each entry holds title, URL, category, summary and article text. Pressing Enter without picking a suggestion runs the full search on the KB chosen in the dropdown.

The indexes are rebuilt nightly by `.github/workflows/rebuild-index.yml` (or run it by hand from the **Actions** tab). The scripts stop without overwriting if a source returns fewer than 20 articles.

Run locally:

```
pip install beautifulsoup4
python scripts/build_qumulex_index.py
python scripts/build_rosslare_index.py
```

> The index files are loaded with `fetch()`, so open the site through GitHub Pages or a local server (`python -m http.server`), not by double-clicking the file.

## Status

Mockup. Links marked `#` and values in `[BRACKETS]` still need real targets.
