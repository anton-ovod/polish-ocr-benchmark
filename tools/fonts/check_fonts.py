"""Check which downloaded fonts really draw all Polish letters and A-Z/a-z.

The `subsets` field in Google Fonts metadata is unreliable (fonts tagged latin-ext may miss Polish letters and
vice versa), so each glyph is looked up in the font's cmap and must have at least one contour.
Near-identical Playwrite variants are dropped from the output list.

Usage:
    python tools/fonts/check_fonts.py fonts_dir/ metadata.json tools/fonts/handwriting_fonts_pl.txt
The output lists usable families, most popular first.
"""
import argparse
import json
import re
from collections import Counter
from pathlib import Path

from fontTools.ttLib import TTFont

POLISH = "ąćęłńóśźżĄĆĘŁŃÓŚŹŻ"
BASIC = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def missing_glyphs(path, chars):
    font = TTFont(path)
    cmap = font.getBestCmap()
    glyf = font["glyf"] if "glyf" in font else None

    def drawn(c):
        name = cmap.get(ord(c))
        if name is None:
            return False
        return glyf is None or glyf[name].numberOfContours != 0  # an empty outline renders as a blank

    return "".join(c for c in chars if not drawn(c))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fonts_dir", type=Path)
    ap.add_argument("metadata", type=Path)
    ap.add_argument("out", type=Path)
    args = ap.parse_args()

    meta = json.loads(args.metadata.read_text(encoding="utf-8"))["familyMetadataList"]
    by_file = {re.sub(r"\W", "_", f["family"]) + ".ttf": f for f in meta}
    rows = []
    for path in sorted(args.fonts_dir.glob("*.ttf")):
        info = by_file[path.name]
        rows.append(dict(family=info["family"], popularity=info["popularity"],
                         latin_ext="latin-ext" in info["subsets"],
                         missing_polish=missing_glyphs(path, POLISH), missing_basic=missing_glyphs(path, BASIC)))

    complete = [r for r in rows if not r["missing_polish"] and not r["missing_basic"]]
    print("checked:", len(rows))
    print("complete (18 Polish + A-Z a-z):", len(complete))
    print("missing only uppercase Polish:", sum(1 for r in rows if not r["missing_basic"] and r["missing_polish"]
                                                and r["missing_polish"].isupper()))
    print("tagged latin-ext but incomplete:", sum(1 for r in rows if r["latin_ext"] and r not in complete))
    print("not tagged latin-ext but complete:", sum(1 for r in complete if not r["latin_ext"]))
    print("most often missing:", Counter(c for r in rows for c in r["missing_polish"]).most_common(18))

    usable = sorted((r for r in complete if not r["family"].startswith("Playwrite")), key=lambda r: r["popularity"])
    args.out.write_text("".join(r["family"] + "\n" for r in usable), encoding="utf-8")
    print(f"{len(usable)} families without Playwrite variants -> {args.out}")


if __name__ == "__main__":
    main()
