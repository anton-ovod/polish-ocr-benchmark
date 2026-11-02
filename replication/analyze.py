"""Compare the paper's numbers and our re-runs with the authors' per-image predictions."""
import csv
import json
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))
from metrics import cer, cer_authors, cer_authors_nospace, normalize

OUT = HERE / "results"

PAPER = [
    ("trocr-large-printed", None, None, 0.38, "Sec. 4.2, overall, ranked last"),
    ("claude-3-7-sonnet-20250219", None, None, 0.197, "Sec. 4.2, overall (paper names Claude Sonnet 4)"),
    ("gpt4o", "subcategory", "turkish", 0.065, "Sec. 4.3, 0.055/0.065 across both subcategories"),
    ("gpt4o", "subcategory", "non_turkish", 0.055, "Sec. 4.3"),
    ("gpt4o", "subcategory", "clean", 0.017, "Sec. 4.4, clean images"),
    ("paddleocr", "subcategory", "clean", 0.239, "Sec. 4.4, clean images"),
]
OUR_MODELS = {"trocr": "trocr-large-printed", "paddle": "paddleocr", "qwen7b": "qwen2.5-vl-7b-instruct",
              "internvl": "internvl3-8b", "deepseek": "deepseek-vl2-tiny",
              "phi": "phi-3.5-vision-instruct", "pixtral": "pixtral-12b-2409", "got": "got-ocr2_0"}


def load_authors():
    data = json.loads((HERE / "authors" / "cer_wer_calculated.json").read_text(encoding="utf-8"))
    rows = []
    for key, item in data.items():
        for model, res in item["models"].items():
            pred = res.get("prediction")
            stored = res.get("cer")
            rows.append(dict(key=key, type=item["type"], category=item["category"],
                             subcategory=item["subcategory"], model=model, truth=item["ground_truth"],
                             prediction=pred,
                             stored=1.0 if stored is None else min(float(stored), 1.0),
                             authors_lc=cer_authors(item["ground_truth"], pred, lowercase=True),
                             nospace=cer_authors_nospace(item["ground_truth"], pred),
                             ours=cer(item["ground_truth"], pred)))
    return pd.DataFrame(rows)


def part_a(df):
    variants = ["stored", "authors_lc", "nospace", "ours"]
    overall = df.groupby("model")[variants].mean().sort_values("ours")
    by_type = df.pivot_table(index="model", columns="type", values="ours", aggfunc="mean")
    by_cell = df.groupby(["model", "type", "category", "subcategory"])[variants].mean()
    overall.round(4).to_csv(OUT / "authors_overall.csv")
    by_type.round(4).to_csv(OUT / "authors_by_type.csv")
    by_cell.round(4).to_csv(OUT / "authors_by_cell.csv")
    print("A. Authors' predictions, mean CER over 6600 images\n")
    print(overall.round(3).to_string(), "\n")

    claims = []
    for model, col, val, paper, where in PAPER:
        sub = df[df.model == model] if col is None else df[(df.model == model) & (df[col] == val)]
        claims.append(dict(model=model, subset=val or "all", paper=paper, where=where,
                           **{v: round(sub[v].mean(), 3) for v in variants}))
    claims = pd.DataFrame(claims)
    claims.to_csv(OUT / "paper_claims.csv", index=False)
    print("Values quoted in the paper vs recomputed\n")
    print(claims.drop(columns="where").to_string(index=False), "\n")


def part_b(df):
    print("B. Our re-run vs the authors' predictions on the same images\n")
    labels = pd.read_csv(HERE / "data" / "sample.csv")
    summary = []
    for name, model in OUR_MODELS.items():
        path = OUT / f"{name}.csv"
        if not path.exists() or path.stat().st_size == 0:
            print(f"  {path.name}: no results, skipped")
            continue
        ours = pd.read_csv(path, keep_default_na=False).merge(labels, on="file")
        theirs = df[df.model == model].set_index("key")
        ours["authors_prediction"] = ours["key"].map(theirs["prediction"]).fillna("")
        ours["cer_ours_run"] = [cer(t, p) for t, p in zip(ours.text, ours.prediction)]
        ours["cer_authors_run"] = [cer(t, p) for t, p in zip(ours.text, ours.authors_prediction)]
        ours["identical"] = [normalize(a) == normalize(b) for a, b in zip(ours.prediction, ours.authors_prediction)]
        ours["cer_between_runs"] = [cer(a, b) for a, b in zip(ours.authors_prediction, ours.prediction)]
        ours.to_csv(OUT / f"{name}_vs_authors.csv", index=False)
        for typ, g in [("all", ours)] + list(ours.groupby("type")):
            summary.append(dict(model=name, type=typ, n=len(g), identical=round(g.identical.mean(), 3),
                                cer_our_run=round(g.cer_ours_run.mean(), 3),
                                cer_authors_run=round(g.cer_authors_run.mean(), 3),
                                cer_between_runs=round(g.cer_between_runs.mean(), 3),
                                sec_per_image=round(g.seconds.mean(), 2)))
    if summary:
        summary = pd.DataFrame(summary)
        summary.to_csv(OUT / "rerun_vs_authors.csv", index=False)
        print(summary.to_string(index=False))


def main():
    OUT.mkdir(exist_ok=True)
    pd.set_option("display.width", 200)
    df = load_authors()
    part_a(df)
    part_b(df)


if __name__ == "__main__":
    main()
