"""Build labels for the authors' Turkish benchmark (Zenodo 10.5281/zenodo.21923181).

Writes, next to the extracted dataset:
    replication/data/labels.csv  all 6600 images
    replication/data/sample.csv  stratified sample, --n images per (type, category, subcategory) cell

Ground truth and cell metadata come from the authors' replication/authors/cer_wer_calculated.json, keyed by
"N.png"; the key is checked against text_category/<type>/text_labels.txt from Zenodo.

Usage:
    .venv/bin/python replication/build_labels.py --n 10
"""
import argparse
import csv
import json
import random
import unicodedata
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
BENCHMARK = "syntetic-turkish-dataset/benchmark"  # sic, the folder name in the Zenodo archive


def read_text_labels(path):
    labels = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            name, _, text = line.partition(" ")
            labels[name] = text
    return labels


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=10, help="sample size per cell")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--data", type=Path, default=HERE / "data")
    args = ap.parse_args()

    authors = json.loads((HERE / "authors" / "cer_wer_calculated.json").read_text(encoding="utf-8"))
    rows, mismatches = [], 0
    zenodo = {}
    for name, item in sorted(authors.items(), key=lambda kv: int(kv[0].split(".")[0])):
        typ = item["type"]
        if typ not in zenodo:
            zenodo[typ] = read_text_labels(args.data / BENCHMARK / "text_category" / typ / "text_labels.txt")
        nfc = lambda s: unicodedata.normalize("NFC", s.strip())
        mismatches += nfc(zenodo[typ].get(name, "")) != nfc(item["ground_truth"])
        rows.append(dict(file=f"{BENCHMARK}/text_category/{typ}/{name}", text=item["ground_truth"], type=typ,
                         category=item["category"], subcategory=item["subcategory"], key=name))
    print(f"{len(rows)} images, {mismatches} ground-truth mismatches between JSON and Zenodo labels")

    cells = defaultdict(list)
    for row in rows:
        cells[row["type"], row["category"], row["subcategory"]].append(row)
    sample = []
    for cell in sorted(cells):
        sample += random.Random(f"{args.seed}-{'-'.join(cell)}").sample(cells[cell], args.n)
    print(f"sample: {len(sample)} images from {len(cells)} cells")

    for name, data in (("labels.csv", rows), ("sample.csv", sample)):
        with open(args.data / name, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(data)


if __name__ == "__main__":
    main()
