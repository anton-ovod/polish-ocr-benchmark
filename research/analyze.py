"""Score predictions on both datasets, rank the models and correlate the rankings."""
import argparse
import difflib
import sys
from pathlib import Path

import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "common"))
from metrics import cer_text, normalize_text, wer_text

POLISH = set("ąćęłńóśźż")


def diacritic_errors(truth, pred):
    t, p = normalize_text(truth), normalize_text(pred)
    total = sum(c in POLISH for c in t)
    wrong = 0
    for tag, i1, i2, _, _ in difflib.SequenceMatcher(None, t, p, autojunk=False).get_opcodes():
        if tag in ("replace", "delete"):
            wrong += sum(c in POLISH for c in t[i1:i2])
    return wrong, total


def score(name, data, results):
    labels = pd.read_csv(data / "labels.csv", keep_default_na=False)
    frames = []
    for path in sorted((results / name).glob("*.csv")):
        pred = pd.read_csv(path, keep_default_na=False)
        frame = labels.merge(pred, on="file", how="left")
        frame["prediction"] = frame["prediction"].fillna("").astype(str)
        frame["model"] = path.stem
        frame["cer"] = [cer_text(t, p) for t, p in zip(frame["text"], frame["prediction"])]
        frame["wer"] = [wer_text(t, p) for t, p in zip(frame["text"], frame["prediction"])]
        errors = [diacritic_errors(t, p) for t, p in zip(frame["text"], frame["prediction"])]
        frame["diacritic_wrong"] = [e[0] for e in errors]
        frame["diacritic_total"] = [e[1] for e in errors]
        frame["empty"] = frame["prediction"].str.strip().eq("")
        frames.append(frame)
    return pd.concat(frames, ignore_index=True)


def summarize(scores, by):
    grouped = scores.groupby(["model", *by])
    table = grouped.agg(n=("cer", "size"), cer=("cer", "mean"), wer=("wer", "mean"), empty=("empty", "sum"),
                        sec_per_image=("seconds", "mean"), wrong=("diacritic_wrong", "sum"),
                        total=("diacritic_total", "sum")).reset_index()
    table["diacritic_error_rate"] = table["wrong"] / table["total"].where(table["total"] > 0)
    return table.drop(columns=["wrong", "total"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", type=Path, required=True, help="directory with synthetic/ and gold/ predictions")
    ap.add_argument("--synthetic", type=Path, default=ROOT / "research" / "data")
    ap.add_argument("--gold", type=Path, default=ROOT / "research" / "gold" / "data")
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()
    out = args.out or args.results / "analysis"
    out.mkdir(parents=True, exist_ok=True)

    scores = {"synthetic": score("synthetic", args.synthetic, args.results), "gold": score("gold", args.gold, args.results)}
    for name, frame in scores.items():
        frame.drop(columns=["text"]).to_csv(out / f"scores_{name}.csv", index=False)
    synthetic, gold = scores["synthetic"], scores["gold"]

    overall = pd.concat([summarize(f, ["type"]).assign(dataset=n) for n, f in scores.items()])
    overall.to_csv(out / "overall.csv", index=False)
    summarize(synthetic, ["type", "category", "subcategory"]).to_csv(out / "by_cell.csv", index=False)

    reference = synthetic[(synthetic["type"] == "handwritten") & (synthetic["subcategory"] == "sentences")]
    ranking = pd.DataFrame({"synthetic_cer": reference.groupby("model")["cer"].mean(),
                            "gold_cer": gold.groupby("model")["cer"].mean()}).dropna()
    ranking["synthetic_rank"] = ranking["synthetic_cer"].rank().astype(int)
    ranking["gold_rank"] = ranking["gold_cer"].rank().astype(int)
    ranking.sort_values("gold_rank").to_csv(out / "ranking.csv")
    print(ranking.sort_values("gold_rank").round(3).to_string())
    if len(ranking) >= 3:
        rho, p = spearmanr(ranking["synthetic_cer"], ranking["gold_cer"])
        pd.DataFrame([dict(rho=rho, p=p, models=len(ranking))]).to_csv(out / "spearman.csv", index=False)
        print(f"\nSpearman rho = {rho:.3f} (p = {p:.3f}, n = {len(ranking)} models)")
    print(f"\nwritten to {out}")


if __name__ == "__main__":
    main()
