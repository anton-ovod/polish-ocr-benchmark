"""Download every Google Fonts family in the Handwriting category (one regular-weight TTF per family).

Usage:
    python tools/fonts/fetch_fonts.py metadata.json out_dir/
where metadata.json is https://fonts.google.com/metadata/fonts saved locally.
"""
import argparse
import json
import re
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


def file_name(family):
    return re.sub(r"\W", "_", family) + ".ttf"


def fetch(family, out_dir):
    css_url = "https://fonts.googleapis.com/css2?family=" + urllib.parse.quote(family)
    try:
        # a non-browser user agent makes the CSS API return TTF instead of WOFF2 links
        request = urllib.request.Request(css_url, headers={"User-Agent": "curl/8"})
        css = urllib.request.urlopen(request, timeout=30).read().decode()
        ttf_url = re.search(r"url\((https://[^)]+)\)", css).group(1)
        (out_dir / file_name(family)).write_bytes(urllib.request.urlopen(ttf_url, timeout=60).read())
        return family, None
    except Exception as e:
        return family, str(e)[:80]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("metadata", type=Path)
    ap.add_argument("out_dir", type=Path)
    args = ap.parse_args()

    meta = json.loads(args.metadata.read_text(encoding="utf-8"))["familyMetadataList"]
    families = [f["family"] for f in meta if f["category"] == "Handwriting"]
    args.out_dir.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(16) as pool:
        results = list(pool.map(lambda fam: fetch(fam, args.out_dir), families))
    failed = [(fam, err) for fam, err in results if err]
    print(f"{len(results)} families, {len(failed)} failed")
    for fam, err in failed[:10]:
        print(f"  {fam}: {err}")


if __name__ == "__main__":
    main()
