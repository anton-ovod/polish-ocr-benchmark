"""Comparison figures for the article and slides, drawn from the tables written by summarize.py.

Usage:
    .venv/bin/python src/summarize.py        # first, refreshes polish/results/summary/
    .venv/bin/python src/plot_results.py
Outputs (PDF for LaTeX, PNG for slides and quick previews):
    docs/article/figures/{overall,cells,effects,diacritics,speed}.{pdf,png}

Every model keeps the same colour in every figure; a model without results is simply skipped.
Labels are in Polish because the figures go straight into the article.
"""
import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402

sys.path.insert(0, str(Path(__file__).parent))
from summarize import CELL_ORDER, EFFECTS, MODEL_NAMES, ordered  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

# categorical palette checked for colour-blind separation in MODEL_ORDER (dataviz validate_palette.js)
COLORS = {"qwen7b": "#6250d6", "qwen": "#008300", "tesseract": "#2a78d6", "easyocr": "#eb6834",
          "paddle": "#1baf7a", "trocr": "#eda100"}
INK, INK2, MUTED, GRID, AXIS = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
BLUES = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
WIDTH = 4.8  # inches, LNCS text width
# where the speed plot puts a model's name, in points from the marker (default: to the right)
SPEED_LABELS = {"paddle": (-6, 0, "right", "center"), "easyocr": (0, -8, "center", "top")}

plt.rcParams.update({
    "font.size": 8, "axes.titlesize": 8.5, "axes.labelsize": 8, "xtick.labelsize": 7.5, "ytick.labelsize": 7.5,
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


def plot_overall(overall, out):
    """Mean CER per model with its 95% bootstrap interval, best model on top."""
    o = overall.sort_values("cer", ascending=False)
    fig, ax = plt.subplots(figsize=(WIDTH, 0.35 * len(o) + 0.6))
    y = np.arange(len(o))
    ax.barh(y, o.cer, height=0.6, color=[COLORS.get(m, MUTED) for m in o.index])
    ax.errorbar(o.cer, y, xerr=[o.cer - o.cer_lo, o.cer_hi - o.cer], fmt="none", ecolor=INK, elinewidth=0.9,
                capsize=2.5)
    for yi, (_, r) in zip(y, o.iterrows()):
        ax.text(r.cer_hi + 0.008, yi, pl(r.cer, 3), va="center", fontsize=7, color=INK2)
    ax.set_yticks(y, [name(m) for m in o.index])
    ax.set_xlabel("średni CER (95% przedział ufności, bootstrap)")
    ax.set_xlim(0, o.cer_hi.max() * 1.18)
    ax.xaxis.set_major_formatter(decimal_comma)
    ax.grid(axis="y", visible=False)
    ax.tick_params(axis="y", length=0)
    save(fig, out, "overall")


def plot_cells(df, models, out):
    """Heat map of mean CER in every cell, printed and handwritten side by side."""
    cmap = LinearSegmentedColormap.from_list("blues", BLUES)
    fig, axes = plt.subplots(1, 2, figsize=(WIDTH, 3.6), sharey=True)
    for ax, typ, title in zip(axes, ("printed", "handwritten"), ("druk", "pismo odręczne")):
        sub = df[df.type == typ]
        grid = np.array([[sub[(sub.model == m) & (sub.subcategory == s)].cer.mean() for m in models]
                         for _, s, _ in CELL_ORDER])
        im = ax.imshow(grid, cmap=cmap, vmin=0, vmax=1, aspect="auto")
        for (i, j), v in np.ndenumerate(grid):
            if not np.isnan(v):
                ax.text(j, i, pl(v), ha="center", va="center", fontsize=6.5, color="white" if v > 0.45 else INK)
        # white rules between the four comparison groups
        cats = [c for c, _, _ in CELL_ORDER]
        for i in range(1, len(cats)):
            if cats[i] != cats[i - 1]:
                ax.axhline(i - 0.5, color="white", linewidth=2.5)
        ax.set_title(title)
        ax.set_xticks(range(len(models)), [name(m) for m in models], rotation=40, ha="right")
        ax.set_yticks(range(len(CELL_ORDER)), [label for _, _, label in CELL_ORDER])
        ax.tick_params(length=0)
        ax.grid(False)
        for spine in ax.spines.values():
            spine.set_visible(False)
    bar = fig.colorbar(im, ax=axes, shrink=0.6, pad=0.02)
    bar.set_label("średni CER")
    bar.ax.yaxis.set_major_formatter(decimal_comma)
    bar.outline.set_visible(False)
    save(fig, out, "cells")


def plot_effects(effects, models, out):
    """Forest plot of effect sizes: filled marker when the 95% interval excludes zero."""
    labels = [label for label, *_ in EFFECTS]
    fig, ax = plt.subplots(figsize=(WIDTH, 0.42 * len(labels) + 0.9))
    step = 0.7 / max(len(models) - 1, 1)
    for k, m in enumerate(models):
        e = effects[effects.model == m].set_index("effect").reindex(labels)
        y = np.arange(len(labels)) - 0.35 + k * step
        c = COLORS.get(m, MUTED)
        ax.hlines(y, e.lo, e.hi, color=c, linewidth=1.2)
        sig = e.significant.astype(bool).to_numpy()
        ax.scatter(e.delta[sig], y[sig], s=22, color=c, zorder=3, edgecolor="white", linewidth=0.6)
        ax.scatter(e.delta[~sig], y[~sig], s=22, facecolor="white", edgecolor=c, linewidth=1.2, zorder=3)
    for i in range(0, len(labels), 2):  # alternate bands keep the rows apart
        ax.axhspan(i - 0.5, i + 0.5, color="#f4f3ef", zorder=0, linewidth=0)
    ax.axvline(0, color=INK2, linewidth=0.8)
    ax.set_yticks(range(len(labels)), labels)
    ax.set_ylim(len(labels) - 0.5, -0.5)
    ax.set_xlabel("ΔCER względem grupy odniesienia (95% przedział ufności)")
    ax.xaxis.set_major_formatter(decimal_comma)
    ax.grid(axis="y", visible=False)
    ax.tick_params(axis="y", length=0)
    handles = [Line2D([], [], color=COLORS.get(m, MUTED), marker="o", linewidth=1.2, markersize=4.5, label=name(m))
               for m in models]
    handles += [Line2D([], [], color=INK2, marker="o", linestyle="none", markersize=4.5, label="istotny"),
                Line2D([], [], color=INK2, marker="o", linestyle="none", markersize=4.5, markerfacecolor="white",
                       label="nieistotny")]
    ax.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.45, 1.0), ncol=4, columnspacing=1.2,
              handlelength=1.6)
    save(fig, out, "effects")


def plot_diacritics(df, overall, models, out):
    """CER without vs with Polish letters, and the share of errors caused by diacritics alone."""
    fig, (a, b) = plt.subplots(1, 2, figsize=(WIDTH, 0.3 * len(models) + 1.1), sharey=True,
                               gridspec_kw={"width_ratios": [1.4, 1]})
    y = np.arange(len(models))
    sub = df[df.category == "polish_character_confusion"].groupby(["model", "subcategory"]).cer.mean()
    for yi, m in zip(y, models):
        c = COLORS.get(m, MUTED)
        without, with_ = sub[(m, "non_polish")], sub[(m, "polish")]
        a.plot([without, with_], [yi, yi], color=AXIS, linewidth=2, zorder=1)
        a.scatter(without, yi, s=26, facecolor="white", edgecolor=c, linewidth=1.3, zorder=3)
        a.scatter(with_, yi, s=32, color=c, edgecolor="white", linewidth=0.6, zorder=3)
    a.set_yticks(y, [name(m) for m in models])
    a.set_ylim(len(models) - 0.5, -0.5)
    a.set_xlabel("średni CER")
    a.set_title("słowa bez polskich znaków i z nimi", loc="left")
    fig.legend(handles=[Line2D([], [], color=INK2, marker="o", linestyle="none", markersize=5, markerfacecolor="white",
                             label="bez polskich znaków"),
                      Line2D([], [], color=INK2, marker="o", linestyle="none", markersize=5, label="z polskimi znakami")],
             loc="upper center", bbox_to_anchor=(0.5, -0.03), ncol=2, handletextpad=0.3)
    a.xaxis.set_major_formatter(decimal_comma)
    a.set_xlim(left=0)

    share = 100 * overall.loc[models, "diacritics_only_share"]
    b.barh(y, share, height=0.6, color=[COLORS.get(m, MUTED) for m in models])
    for yi, v in zip(y, share):
        b.text(v + 0.8, yi, f"{v:.0f}%", va="center", fontsize=7, color=INK2)
    b.set_xlim(0, share.max() * 1.25)
    b.set_xlabel("% błędnych predykcji")
    b.set_title("błędy tylko w diakrytykach", loc="left")
    for ax in (a, b):
        ax.grid(axis="y", visible=False)
        ax.tick_params(axis="y", length=0)
    save(fig, out, "diacritics")


def plot_speed(overall, models, out):
    """Accuracy against CPU time per image (intervals are in the overall figure)."""
    fig, ax = plt.subplots(figsize=(WIDTH * 0.75, 2.4))
    for m in models:
        r = overall.loc[m]
        c = COLORS.get(m, MUTED)
        ax.scatter(r.seconds, r.cer, s=34, color=c, edgecolor="white", linewidth=0.8, zorder=3)
        dx, dy, ha, va = SPEED_LABELS.get(m, (6, 0, "left", "center"))
        ax.annotate(name(m), (r.seconds, r.cer), xytext=(dx, dy), textcoords="offset points", ha=ha, va=va,
                    fontsize=7, color=INK)
    ax.set_xscale("log")
    ax.set_xlabel("czas na obraz [s], CPU, skala logarytmiczna")
    ax.set_ylabel("średni CER")
    lo, hi = overall.loc[models, "seconds"].min(), overall.loc[models, "seconds"].max()
    ax.set_xlim(lo / 4, hi * 4)
    ax.set_ylim(0, overall.loc[models, "cer"].max() * 1.25)
    ax.xaxis.set_major_formatter(decimal_comma)
    ax.yaxis.set_major_formatter(decimal_comma)
    save(fig, out, "speed")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", type=Path, default=ROOT / "polish" / "results" / "summary")
    ap.add_argument("--out", type=Path, default=ROOT / "docs" / "article" / "figures")
    args = ap.parse_args()

    df = pd.read_csv(args.summary / "per_image.csv", keep_default_na=False)
    overall = pd.read_csv(args.summary / "overall.csv", index_col=0)
    effects = pd.read_csv(args.summary / "effects.csv")
    models = ordered(overall.index)
    args.out.mkdir(parents=True, exist_ok=True)

    print(f"Figures for {', '.join(models)} -> {args.out}")
    plot_overall(overall, args.out)
    plot_cells(df, models, args.out)
    plot_effects(effects, models, args.out)
    plot_diacritics(df, overall, models, args.out)
    plot_speed(overall, models, args.out)


if __name__ == "__main__":
    main()
