"""Build the Gold Set: downscale the PHSF invocation scans and write labels.csv."""
import argparse
import csv
import random
import re
import unicodedata
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ("Litwo, Ojczyzno moja! Ty jesteś jak zdrowie; Ile Cię trzeba cenić? Ten tylko się dowie: "
             "Kto cię STRACIŁ. Dziś Piękność Twą w całej ozdobie, Widzę i opisuję - bo tęsknię po tobie.")
NAME = re.compile(r"^inwokacja_\d+_(?:\d\d-\d\d-\d\d_)?(\d{2}|\d{4})_([KM])_(.+)\.png$")
CYRILLIC = str.maketrans("СЕАВ", "CEAB")


def parse(name):
    match = NAME.match(unicodedata.normalize("NFC", name))
    if not match:
        return "", "", ""
    year, sex, code = match.groups()
    if len(year) == 2:
        year = ("20" if int(year) <= 10 else "19") + year
    return year, sex, code.translate(CYRILLIC)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--images", type=Path, default=ROOT / "research" / "gold" / "images")
    ap.add_argument("--out", type=Path, default=ROOT / "research" / "gold" / "data")
    ap.add_argument("--n", type=int, default=None, help="random sample of this many scans (default: all)")
    ap.add_argument("--max-side", type=int, default=2048)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    sources = sorted(args.images.glob("*.png"))
    assert sources, f"no PNG files in {args.images}"
    indexed = list(enumerate(sources))
    if args.n and args.n < len(indexed):
        indexed = sorted(random.Random(args.seed).sample(indexed, args.n))
    (args.out / "images").mkdir(parents=True, exist_ok=True)

    rows = []
    for i, path in indexed:
        with Image.open(path) as image:
            width, height = image.size
            scale = args.max_side / max(width, height)
            if scale < 1:
                image = image.resize((round(width * scale), round(height * scale)), Image.LANCZOS)
            file = f"images/inwokacja_{i:04d}.png"
            image.save(args.out / file)
        birth_year, sex, form_code = parse(path.name)
        rows.append(dict(file=file, text=REFERENCE, type="handwritten", source=path.name, birth_year=birth_year,
                         sex=sex, form_code=form_code, width=width, height=height))

    with open(args.out / "labels.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} of {len(sources)} scans to {args.out} (longest side <= {args.max_side})")


if __name__ == "__main__":
    main()
