"""Summarise OCR results for the Polish dataset: CSV tables and LaTeX tables for the article.

Reads <data>/labels.csv and every <results>/<model>.csv (columns file, prediction, seconds); a Colab run
of Qwen only needs to drop qwen.csv into the same folder.

Usage:
    .venv/bin/python src/summarize.py
Outputs:
    polish/results/summary/{per_image,by_cell,overall,effects}.csv
    docs/article/tables/{overall,cells,effects}.tex

Uncertainty follows the base paper: 95% percentile bootstrap intervals from 1000 resamples of per-image CER.
An effect is the difference of mean CER between two groups of images (e.g. with vs without Polish letters);
it is significant when its bootstrap interval excludes zero.
"""
import argparse
import sys
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from metrics import cer, cer_authors, normalize, wer  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
MODEL_ORDER = ["qwen7b", "qwen", "tesseract", "easyocr", "paddle", "trocr"]
MODEL_NAMES = {"qwen7b": "Qwen2.5-VL-7B", "qwen": "Qwen2.5-VL-3B", "tesseract": "Tesseract", "easyocr": "EasyOCR", "paddle": "PaddleOCR",
               "trocr": "TrOCR"}
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

# (label in the article, column, group A, group B): effect = mean CER(A) - mean CER(B)
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
BOOTSTRAP = 1000  # resamples, as in the base paper


def bootstrap_means(values, rng):
    values = np.asarray(values, dtype=float)
    return rng.choice(values, (BOOTSTRAP, len(values))).mean(axis=1)


def mean_ci(values, rng):
    """Mean and its 95% percentile bootstrap interval."""
    lo, hi = np.percentile(bootstrap_means(values, rng), [2.5, 97.5])
    return np.mean(values), lo, hi


def effect_ci(a, b, rng):
    """Difference of means and its 95% bootstrap interval; the two groups are resampled independently."""
    lo, hi = np.percentile(bootstrap_means(a, rng) - bootstrap_means(b, rng), [2.5, 97.5])
    return np.mean(a) - np.mean(b), lo, hi


def strip_diacritics(text):
    text = text.replace("ł", "l").replace("Ł", "L")  # ł has no Unicode decomposition
    return "".join(c for c in unicodedata.normalize("NFD", text) if not unicodedata.combining(c))


def diacritics_only(truth, pred):
    """The prediction is wrong only because of missing or wrong diacritics."""
    t, p = normalize(truth), normalize(pred)
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
    df["cer"] = [cer(t, p) for t, p in zip(df.text, df.prediction)]
    df["wer"] = [wer(t, p) for t, p in zip(df.text, df.prediction)]
    df["cer_authors"] = [cer_authors(t, p) for t, p in zip(df.text, df.prediction)]
    df["exact"] = [normalize(t) == normalize(p) for t, p in zip(df.text, df.prediction)]
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


def latex_cells(by_cell, models, path):
    head = " & ".join(MODEL_NAMES.get(m, m) for m in models)
    lines = [r"\begin{tabular}{l" + "c" * len(models) + "}", r"\toprule", f"Podkategoria & {head} \\\\", r"\midrule"]
    previous = None
    for cat, sub, label in CELL_ORDER:
        if previous and cat != previous:
            lines.append(r"\midrule")
        previous = cat
        cells = []
        for m in models:
            p, h = (by_cell.get((m, typ, cat, sub), float("nan")) for typ in ("printed", "handwritten"))
            cells.append(f"{fmt(p)} / {fmt(h)}")
        lines.append(f"{label} & " + " & ".join(cells) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def latex_effects(effects, models, path):
    """Effect per model; bold when the 95% interval excludes zero."""
    head = " & ".join(MODEL_NAMES.get(m, m) for m in models)
    lines = [r"\begin{tabular}{l" + "r" * len(models) + "}", r"\toprule", f"Czynnik & {head} \\\\", r"\midrule"]
    for label, *_ in EFFECTS:
        cells = []
        for m in models:
            r = effects.get((m, label))
            if r is None:
                cells.append("--")
                continue
            text = f"{r['delta']:+.3f}".replace("0.", ".", 1)
            cells.append(rf"\textbf{{{text}}}" if r["lo"] > 0 or r["hi"] < 0 else text)
        lines.append(f"{label} & " + " & ".join(cells) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path, default=ROOT / "polish" / "data")
    ap.add_argument("--results", type=Path, default=ROOT / "polish" / "results")
    ap.add_argument("--tables", type=Path, default=ROOT / "docs" / "article" / "tables")
    args = ap.parse_args()

    df = load(args.data, args.results)
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
        # share of wrong predictions that are wrong only because of diacritics
        errors.groupby("model").diacritics_only.mean().rename("diacritics_only_share"),
        df.groupby("model").size().rename("n"),
    ], axis=1).loc[models]
    overall.round(4).to_csv(out / "overall.csv")

    pd.set_option("display.width", 200)
    print(overall.round(3).to_string(), "\n")
    print(by_cell.cer.unstack("model")[models].round(3).to_string(), "\n")
    print(effects.pivot(index="effect", columns="model", values="delta")[models].round(3).to_string())

    args.tables.mkdir(parents=True, exist_ok=True)
    latex_overall(overall, args.tables / "overall.tex")
    latex_cells(by_cell.cer.to_dict(), models, args.tables / "cells.tex")
    latex_effects(effects.set_index(["model", "effect"]).to_dict("index"), models, args.tables / "effects.tex")
    print(f"\nLaTeX tables written to {args.tables}")


if __name__ == "__main__":
    main()
