"""Summarise OCR results for the Polish dataset: CSV and LaTeX tables."""
import argparse
import sys
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "common"))
from metrics import cer_authors, cer_text, normalize_text, wer_text

ROOT = Path(__file__).resolve().parents[1]
MODEL_ORDER = ["qwen7b", "internvl", "deepseek", "tesseract", "easyocr", "paddle", "got"]
MODEL_NAMES = {"qwen7b": "Qwen2.5-VL 7B", "internvl": "InternVL3-8B", "deepseek": "DeepSeek-VL2", "tesseract": "Tesseract",
               "easyocr": "EasyOCR", "paddle": "PaddleOCR", "got": "GOT-OCR2"}
CELL_ORDER = [
    ("polish_character_confusion", "polish", "z polskimi znakami"),
    ("polish_character_confusion", "non_polish", "bez polskich znaków"),
    ("word_length_effects", "short_words", "krótkie słowa"),
    ("word_length_effects", "long_words", "długie słowa"),
    ("context_dependent_errors", "word", "słowo"),
    ("context_dependent_errors", "sentences", "zdanie"),
    ("distortion_type", "clean", "czysty"),
    ("distortion_type", "blur", "rozmycie"),
    ("distortion_type", "rotated", "obrót"),
    ("distortion_type", "noisy", "szum"),
    ("distortion_type", "low_resolution", "niska rozdzielczość"),
]

EFFECTS = [
    ("polskie znaki", "subcategory", "polish", "non_polish"),
    ("długie słowa", "subcategory", "long_words", "short_words"),
    ("zdanie zamiast słowa", "subcategory", "sentences", "word"),
    ("pismo odręczne", "type", "handwritten", "printed"),
    ("rozmycie", "subcategory", "blur", "clean"),
    ("obrót", "subcategory", "rotated", "clean"),
    ("szum", "subcategory", "noisy", "clean"),
    ("niska rozdzielczość", "subcategory", "low_resolution", "clean"),
]
BOOTSTRAP = 1000


def bootstrap_means(values, rng):
    values = np.asarray(values, dtype=float)
    return rng.choice(values, (BOOTSTRAP, len(values))).mean(axis=1)


def mean_ci(values, rng):
    lo, hi = np.percentile(bootstrap_means(values, rng), [2.5, 97.5])
    return np.mean(values), lo, hi


def effect_ci(a, b, rng):
    lo, hi = np.percentile(bootstrap_means(a, rng) - bootstrap_means(b, rng), [2.5, 97.5])
    return np.mean(a) - np.mean(b), lo, hi


def strip_diacritics(text):
    text = text.replace("ł", "l").replace("Ł", "L")
    return "".join(c for c in unicodedata.normalize("NFD", text) if not unicodedata.combining(c))


def diacritics_only(truth, pred):
    t, p = normalize_text(truth), normalize_text(pred)
    return t != p and strip_diacritics(t) == strip_diacritics(p)


def load(data, results):
    labels = pd.read_csv(data / "labels.csv", keep_default_na=False)
    frames = []
    for path in sorted(results.glob("*.csv")):
        pred = pd.read_csv(path, keep_default_na=False)
        if not {"file", "prediction"} <= set(pred.columns):
            continue
        df = labels.merge(pred, on="file")
        df.insert(0, "model", path.stem)
        frames.append(df)
    df = pd.concat(frames, ignore_index=True)
    df["cer"] = [cer_text(t, p) for t, p in zip(df.text, df.prediction)]
    df["wer"] = [wer_text(t, p) for t, p in zip(df.text, df.prediction)]
    df["cer_authors"] = [cer_authors(t, p) for t, p in zip(df.text, df.prediction)]
    df["exact"] = [normalize_text(t) == normalize_text(p) for t, p in zip(df.text, df.prediction)]
    df["diacritics_only"] = [diacritics_only(t, p) for t, p in zip(df.text, df.prediction)]
    return df


def ordered(models):
    return [m for m in MODEL_ORDER if m in models] + sorted(set(models) - set(MODEL_ORDER))


def fmt(x):
    return "--" if pd.isna(x) else f"{x:.3f}".replace("0.", ".", 1) if x < 1 else f"{x:.2f}"


def latex_overall(overall, path):
    lines = [r"\begin{tabular}{lrrrcrrr}", r"\toprule",
             r"Model & \multicolumn{4}{c}{CER} & WER & Diakr. & s/obraz \\",
             r" & druk & pismo & razem & 95\% CI & zdania & [\%] & \\", r"\midrule"]
    for m, r in overall.iterrows():
        lines.append(f"{MODEL_NAMES.get(m, m)} & {fmt(r.printed)} & {fmt(r.handwritten)} & {fmt(r.cer)} & "
                     f"[{fmt(r.cer_lo)}, {fmt(r.cer_hi)}] & {fmt(r.wer_sentences)} & "
                     f"{100 * r.diacritics_only_share:.0f} & {r.seconds:.2f} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def latex_gold(table, path):
    lines = [r"\begin{tabular}{lrrrrrr}", r"\toprule",
             r"Model & \multicolumn{2}{c}{CER} & \multicolumn{2}{c}{Miejsce} & WER & Puste \\",
             r" & syntetyczny & PHCD & syntetyczny & PHCD & PHCD & PHCD \\", r"\midrule"]
    for m, r in table.sort_values("gold_rank").iterrows():
        lines.append(f"{MODEL_NAMES.get(m, m)} & {fmt(r.synthetic_cer)} & {fmt(r.gold_cer)} & {int(r.synthetic_rank)} & "
                     f"{int(r.gold_rank)} & {fmt(r.gold_wer)} & {int(r.gold_empty)} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path, default=ROOT / "research" / "data")
    ap.add_argument("--gold", type=Path, default=ROOT / "research" / "gold" / "data")
    ap.add_argument("--results", type=Path, default=ROOT / "research" / "results")
    ap.add_argument("--tables", type=Path, default=ROOT / "docs" / "research" / "article" / "tables")
    args = ap.parse_args()

    df = load(args.data, args.results / "synthetic")
    models = ordered(df.model.unique())
    out = args.results / "summary"
    out.mkdir(exist_ok=True)
    df.to_csv(out / "per_image.csv", index=False)

    by_cell = df.groupby(["model", "type", "category", "subcategory"]).agg(
        n=("cer", "size"), cer=("cer", "mean"), wer=("wer", "mean"), exact=("exact", "mean"),
        diacritics_only=("diacritics_only", "mean"))
    by_cell.round(4).to_csv(out / "by_cell.csv")

    rng = np.random.default_rng(0)
    ci = pd.DataFrame({m: mean_ci(g.cer, rng) for m, g in df.groupby("model")}, index=["_", "cer_lo", "cer_hi"]).T
    effects = []
    for m, g in df.groupby("model"):
        for label, col, a, b in EFFECTS:
            delta, lo, hi = effect_ci(g[g[col] == a].cer, g[g[col] == b].cer, rng)
            effects.append(dict(model=m, effect=label, a=a, b=b, delta=delta, lo=lo, hi=hi,
                                significant=lo > 0 or hi < 0))
    effects = pd.DataFrame(effects)
    effects.round(4).to_csv(out / "effects.csv", index=False)

    errors = df[~df.exact]
    sentences = df[df.subcategory == "sentences"]
    overall = pd.concat([
        df.pivot_table(index="model", columns="type", values="cer", aggfunc="mean"),
        df.groupby("model")[["cer", "cer_authors", "exact", "seconds"]].mean(),
        ci[["cer_lo", "cer_hi"]],
        sentences.groupby("model").wer.mean().rename("wer_sentences"),
        errors.groupby("model").diacritics_only.mean().rename("diacritics_only_share"),
        df.groupby("model").size().rename("n"),
    ], axis=1).loc[models]
    overall.round(4).to_csv(out / "overall.csv")

    pd.set_option("display.width", 200)
    print(overall.round(3).to_string(), "\n")
    print(by_cell.cer.unstack("model")[models].round(3).to_string(), "\n")
    print(effects.pivot(index="effect", columns="model", values="delta")[models].round(3).to_string())

    gold = load(args.gold, args.results / "gold")
    reference = df[(df.type == "handwritten") & (df.subcategory == "sentences")].groupby("model").cer.mean()
    gold_table = pd.DataFrame({"synthetic_cer": reference, "gold_cer": gold.groupby("model").cer.mean(),
                               "gold_wer": gold.groupby("model").wer.mean(),
                               "gold_empty": gold.groupby("model").prediction.apply(lambda s: (s.str.strip() == "").sum()),
                               "gold_seconds": gold.groupby("model").seconds.mean()}).loc[models]
    gold_table["synthetic_rank"] = gold_table.synthetic_cer.rank().astype(int)
    gold_table["gold_rank"] = gold_table.gold_cer.rank().astype(int)
    rho, p = spearmanr(gold_table.synthetic_cer, gold_table.gold_cer)
    gold_table.round(4).to_csv(out / "gold.csv")
    print("\n" + gold_table.round(3).to_string(), f"\n\nSpearman rho = {rho:.3f}, p = {p:.3f}, n = {len(gold_table)}")

    args.tables.mkdir(parents=True, exist_ok=True)
    latex_gold(gold_table, args.tables / "gold.tex")
    latex_overall(overall, args.tables / "overall.tex")
    print(f"\nLaTeX tables written to {args.tables}")


if __name__ == "__main__":
    main()
