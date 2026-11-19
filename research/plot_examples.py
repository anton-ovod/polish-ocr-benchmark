"""Draw sample images from the synthetic dataset and the PHCD scans for the article."""
import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.gridspec import GridSpec
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
CELLS = [("polish_character_confusion", "polish", "polskie znaki"),
         ("word_length_effects", "long_words", "długie słowo"),
         ("context_dependent_errors", "sentences", "zdanie"),
         ("distortion_type", "clean", "czysty"),
         ("distortion_type", "blur", "rozmycie"),
         ("distortion_type", "rotated", "obrót"),
         ("distortion_type", "noisy", "szum"),
         ("distortion_type", "low_resolution", "niska\nrozdz.")]
INK, INK2, AXIS = "#0b0b0b", "#52514e", "#c3c2b7"


def first(labels, typ, category, subcategory):
    row = labels[(labels.type == typ) & (labels.category == category) & (labels.subcategory == subcategory)].iloc[0]
    return row.file


def panel(ax, path, title=None):
    ax.imshow(Image.open(path).convert("RGB"))
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_color(AXIS)
        spine.set_linewidth(0.6)
    if title:
        ax.set_title(title, fontsize=6.3, color=INK2, pad=2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path, default=ROOT / "research" / "data")
    ap.add_argument("--gold", type=Path, default=ROOT / "research" / "gold" / "data")
    ap.add_argument("--out", type=Path, default=ROOT / "docs" / "research" / "article" / "figures")
    args = ap.parse_args()

    labels = pd.read_csv(args.data / "labels.csv", keep_default_na=False)
    gold = pd.read_csv(args.gold / "labels.csv", keep_default_na=False)
    plt.rcParams.update({"font.size": 7.5, "text.color": INK, "pdf.fonttype": 42, "savefig.dpi": 220,
                         "savefig.bbox": "tight"})

    rows = [("druk", "printed"), ("pismo\nodręczne", "handwritten")]
    grid_cells = [c for c in CELLS if c[1] != "sentences"]
    fig = plt.figure(figsize=(4.8, 2.0))
    outer = GridSpec(3, 1, figure=fig, height_ratios=[0.7, 0.7, 2.4], hspace=0.3)
    for r, (name, typ) in enumerate(rows):
        paths = [args.data / first(labels, typ, c, s) for c, s, _ in grid_cells]
        widths = [Image.open(p).width for p in paths]
        inner = outer[r].subgridspec(1, len(paths), width_ratios=widths, wspace=0.05)
        for k, (p, (_, _, title)) in enumerate(zip(paths, grid_cells)):
            ax = fig.add_subplot(inner[k])
            panel(ax, p, title if r == 0 else None)
            if k == 0:
                ax.set_ylabel(name, fontsize=7, color=INK2, rotation=0, ha="right", va="center")
    ax = fig.add_subplot(outer[2])
    panel(ax, args.gold / gold.iloc[0].file, "skan ze zbioru PHCD (po zmniejszeniu do 2048 px)")
    args.out.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(args.out / f"examples.{ext}")
    print(f"wrote {args.out / 'examples.pdf'}")


if __name__ == "__main__":
    main()
