"""Draw the comparison figures from the tables written by summarize.py."""
import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.ticker import FuncFormatter

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "common"))
from summarize import MODEL_NAMES, ordered

ROOT = Path(__file__).resolve().parents[1]

COLORS = {"qwen7b": "#6250d6", "internvl": "#008300", "deepseek": "#d63a6a", "tesseract": "#2a78d6",
          "easyocr": "#eb6834", "paddle": "#1baf7a", "got": "#eda100"}
INK, INK2, MUTED, GRID, AXIS = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
BLUES = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
WIDTH = 4.8

plt.rcParams.update({
    "font.size": 7.5, "axes.titlesize": 8.5, "axes.labelsize": 8, "xtick.labelsize": 7.5, "ytick.labelsize": 7.5,
    "legend.fontsize": 7.5, "axes.edgecolor": AXIS, "axes.labelcolor": INK2, "xtick.color": INK2,
    "ytick.color": INK2, "text.color": INK, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
    "legend.frameon": False, "pdf.fonttype": 42, "savefig.dpi": 200, "savefig.bbox": "tight",
})
decimal_comma = FuncFormatter(lambda x, _: f"{x:g}".replace(".", ","))


def name(m):
    return MODEL_NAMES.get(m, m)


def pl(x, digits=2):
    return f"{x:.{digits}f}".replace(".", ",")


def save(fig, out, stem):
    for ext in ("pdf", "png"):
        fig.savefig(out / f"{stem}.{ext}")
    plt.close(fig)
    print(f"  {stem}")


GROUPS = [
    ("Znaki", [("polish_character_confusion", "non_polish", "bez"), ("polish_character_confusion", "polish", "z")]),
    ("Pismo", [("type", "printed", "druk"), ("type", "handwritten", "pismo")]),
    ("Zniekształcenie", [("distortion_type", "clean", "czysty"), ("distortion_type", "rotated", "obrót"),
                         ("distortion_type", "noisy", "szum"), ("distortion_type", "blur", "rozmycie"),
                         ("distortion_type", "low_resolution", "niska\nrozdz.")]),
    ("Długość", [("word_length_effects", "short_words", "<10"), ("word_length_effects", "long_words", ">10")]),
    ("Kontekst", [("context_dependent_errors", "word", "słowo"), ("context_dependent_errors", "sentences", "zdanie")]),
]
DISTORTIONS = ("clean", "rotated", "noisy", "blur", "low_resolution")


def condition_mean(df, model, col, value):
    sub = df[df.model == model]
    return sub[sub["type" if col == "type" else "subcategory"] == value].cer.mean()


def plot_conditions(df, models, out):
    cmap = LinearSegmentedColormap.from_list("blues", BLUES)
    columns = [(g, col, val, label) for g, cols in GROUPS for col, val, label in cols]
    grid = np.array([[condition_mean(df, m, col, val) for _, col, val, _ in columns] for m in models])
    fig = plt.figure(figsize=(WIDTH, 0.27 * len(models) + 1.5))
    ax = fig.add_axes([0.17, 0.2, 0.83, 0.6])
    xs, x, prev = [], 0.0, None
    for g, *_ in columns:
        if prev is not None and g != prev:
            x += 0.35
        xs.append(x)
        x += 1
        prev = g
    vmax = np.nanmax(grid)
    for j, xj in enumerate(xs):
        for i in range(len(models)):
            v = grid[i, j]
            ax.add_patch(plt.Rectangle((xj - 0.46, i - 0.44), 0.92, 0.88, color=cmap(v / vmax), linewidth=0))
            ax.text(xj, i, pl(v), ha="center", va="center", fontsize=5.6, color="white" if v / vmax > 0.55 else INK)
    ax.set_xlim(-0.6, xs[-1] + 0.6)
    ax.set_ylim(len(models) - 0.4, -0.6)
    ax.set_yticks(range(len(models)), [name(m) for m in models])
    ax.set_xticks(xs, [label for *_, label in columns], fontsize=5.3)
    ax.xaxis.tick_top()
    ax.tick_params(length=0, pad=1.5)
    ax.grid(False)
    for spine in ax.spines.values():
        spine.set_visible(False)
    tops = {}
    for (g, *_), xj in zip(columns, xs):
        tops.setdefault(g, []).append(xj)
    for g, v in tops.items():
        ax.text((v[0] + v[-1]) / 2, -1.55, g, ha="center", va="bottom", fontsize=6.6, fontweight="bold", clip_on=False)
        ax.plot([v[0] - 0.45, v[-1] + 0.45], [-1.45, -1.45], color=AXIS, linewidth=0.8, clip_on=False)
    index = {(col, val): j for j, (_, col, val, _) in enumerate(columns)}

    def col(c, v):
        return grid[:, index[(c, v)]]

    distortions = np.stack([col("distortion_type", d) for d in DISTORTIONS], axis=1)
    counts = [
        ("z znakami\ngorzej", (col("polish_character_confusion", "polish") > col("polish_character_confusion", "non_polish")).sum()),
        ("pismo\ntrudniejsze", (col("type", "handwritten") > col("type", "printed")).sum()),
        ("najtrudniejsza\nniska rozdz.", (distortions.argmax(axis=1) == len(DISTORTIONS) - 1).sum()),
        ("długie\nłatwiejsze", (col("word_length_effects", "long_words") < col("word_length_effects", "short_words")).sum()),
        ("zdanie\nłatwiejsze", (col("context_dependent_errors", "sentences") < col("context_dependent_errors", "word")).sum()),
    ]
    for (g, v), (text, k) in zip(tops.items(), counts):
        ax.text((v[0] + v[-1]) / 2, len(models) - 0.1, f"{text}\nu {k} z {len(models)}", ha="center", va="top",
                fontsize=5.6, color=INK2, linespacing=1.15, clip_on=False)
    cax = fig.add_axes([0.17, 0.94, 0.18, 0.025])
    cax.imshow(np.linspace(0, 1, 100)[None, :], cmap=cmap, aspect="auto")
    cax.set_xticks([0, 99], ["0", pl(vmax)], fontsize=5.8)
    cax.set_yticks([])
    cax.tick_params(length=0, pad=1)
    cax.grid(False)
    for spine in cax.spines.values():
        spine.set_visible(False)
    fig.text(0.0, 0.952, "CER", fontsize=6.5, color=INK2, va="center")
    save(fig, out, "conditions")


def plot_ranking(overall, phsf_scores, models, out):
    rng = np.random.default_rng(42)
    rows = []
    for m in models:
        values = phsf_scores[phsf_scores.model == m].cer.to_numpy()
        boots = rng.choice(values, size=(1000, len(values))).mean(axis=1)
        rows.append((m, overall.loc[m, "cer"], overall.loc[m, "cer_lo"], overall.loc[m, "cer_hi"], values.mean(),
                     np.percentile(boots, 2.5), np.percentile(boots, 97.5)))
    order = sorted(rows, key=lambda r: r[1])
    fig, ax = plt.subplots(figsize=(WIDTH, 0.42 * len(order) + 0.7))
    y = np.arange(len(order))
    h = 0.36
    ax.barh(y - h / 2, [r[1] for r in order], height=h, color="#2a78d6", label="zbiór syntetyczny (2200 obrazów)")
    ax.barh(y + h / 2, [r[4] for r in order], height=h, color="#eb6834", label="PHSF (1968 skanów)")
    ax.errorbar([r[1] for r in order], y - h / 2, xerr=[[r[1] - r[2] for r in order], [r[3] - r[1] for r in order]],
                fmt="none", ecolor=INK2, elinewidth=0.8, capsize=1.8)
    ax.errorbar([r[4] for r in order], y + h / 2, xerr=[[r[4] - r[5] for r in order], [r[6] - r[4] for r in order]],
                fmt="none", ecolor=INK2, elinewidth=0.8, capsize=1.8)
    ax.set_yticks(y, [name(r[0]) for r in order])
    ax.set_ylim(len(order) - 0.5, -0.5)
    ax.set_xlim(0, 0.9)
    ax.xaxis.set_major_formatter(decimal_comma)
    ax.set_xlabel("średni CER (mniej = lepiej), wąsy: 95% przedział ufności")
    ax.grid(axis="y", visible=False)
    ax.tick_params(axis="y", length=0)
    ax.text(1.02, -0.85, "synt.", transform=ax.get_yaxis_transform(), fontsize=6.5, color=MUTED, ha="left")
    ax.text(1.16, -0.85, "PHSF", transform=ax.get_yaxis_transform(), fontsize=6.5, color=MUTED, ha="left")
    for yi, r in zip(y, order):
        ax.text(1.02, yi, pl(r[1], 3), transform=ax.get_yaxis_transform(), fontsize=7, va="center")
        ax.text(1.16, yi, pl(r[4], 3), transform=ax.get_yaxis_transform(), fontsize=7, va="center")
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2, handlelength=1.2, columnspacing=1.2)
    save(fig, out, "ranking")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", type=Path, default=ROOT / "research" / "results" / "summary")
    ap.add_argument("--analysis", type=Path, default=ROOT / "research" / "results" / "analysis")
    ap.add_argument("--out", type=Path, default=ROOT / "docs" / "research" / "article" / "figures")
    args = ap.parse_args()

    df = pd.read_csv(args.summary / "per_image.csv", keep_default_na=False)
    overall = pd.read_csv(args.summary / "overall.csv", index_col=0)
    phsf_scores = pd.read_csv(args.analysis / "scores_gold.csv", keep_default_na=False)
    models = ordered(overall.index)
    args.out.mkdir(parents=True, exist_ok=True)

    print(f"Figures for {', '.join(models)} -> {args.out}")
    plot_conditions(df, models, args.out)
    plot_ranking(overall, phsf_scores, models, args.out)


if __name__ == "__main__":
    main()
