"""Generate the Polish synthetic OCR dataset with TRDG 1.8.0, following Yılmaz et al. (IJDAR 2026).

Usage:
    .venv/bin/python src/generate_dataset.py --n 20     # MVP: 20 images per cell (440 images)
    .venv/bin/python src/generate_dataset.py --n 100    # full dataset (2200 images)

Cells, for each text type (printed, handwritten); names mirror the authors' JSON:
    polish_character_confusion: polish / non_polish            (words, clean image)
    word_length_effects:        short_words (<10) / long_words (>10)
    context_dependent_errors:   word / sentences (4-8 words)
    distortion_type:            clean / blur / rotated / noisy / low_resolution (same words)

Sampling is prefix-stable: the set for --n 20 is a subset of the set for --n 100, so results
computed on the small sample remain valid when the dataset grows.
"""
import argparse
import csv
import random
import re
import unicodedata
from collections import Counter
from pathlib import Path

import numpy as np
from fontTools.ttLib import TTFont
from PIL import Image

import trdg.computer_text_generator as ctg
from trdg.data_generator import FakeTextDataGenerator

# TRDG 1.8.0 calls getsize(), removed in Pillow 10; same fix as the authors' notebooks
ctg.get_text_height = lambda font, text: font.getbbox(text)[3]

ROOT = Path(__file__).resolve().parents[1]
POLISH = set("ąćęłńóśźżĄĆĘŁŃÓŚŹŻ")
LETTERS = "a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ"
SENTENCE_OK = re.compile(rf"^[{LETTERS}][{LETTERS} ,.;:!?-]*[.!?]$")

# Rendering parameters from the authors' trdg_distortions_creator.ipynb
HEIGHT = 64
MARGINS = (15, 15, 15, 15)
DISTORTIONS = {
    "clean": dict(),
    "blur": dict(blur=2),
    "rotated": dict(skewing_angle=16, random_skew=True),
    "noisy": dict(noise_std=50),
    "low_resolution": dict(size=40),
}


def load_text(path):
    text = path.read_text(encoding="utf-8")
    text = text.split("\n-----\n")[0]  # drop the Wolne Lektury footer
    return unicodedata.normalize("NFC", text)


def word_pool(text, min_count=2):
    """Lowercased words with at least 3 letters that occur at least `min_count` times."""
    counts = Counter(w.lower() for w in re.findall(rf"[{LETTERS}]+", text))
    return sorted(w for w, c in counts.items() if c >= min_count and len(w) >= 3)


def sentence_pool(text, min_words=4, max_words=8):
    flat = re.sub(r"\s*\n\s*", " ", text)
    sentences = (s.strip() for s in re.split(r"(?<=[.!?])\s+", flat))
    return sorted({s for s in sentences if SENTENCE_OK.match(s) and min_words <= len(s.split()) <= max_words})


def font_coverage(font_dir, chars):
    """Map font path -> set of `chars` with a non-empty glyph; fonts lacking any Polish letter are skipped."""
    fonts = {}
    for path in sorted(font_dir.glob("*.ttf")):
        font = TTFont(path)
        cmap = font.getBestCmap()
        glyf = font["glyf"] if "glyf" in font else None
        covered = {c for c in chars
                   if ord(c) in cmap and (glyf is None or glyf[cmap[ord(c)]].numberOfContours != 0)}
        if POLISH <= covered:
            fonts[str(path)] = covered
    return fonts


def render(text, font, seed, size=HEIGHT, blur=0, skewing_angle=0, random_skew=False, noise_std=0):
    random.seed(seed)  # TRDG draws the skew angle from the global `random` module
    img = FakeTextDataGenerator.generate(
        0, text, font, None, size, "png", skewing_angle, random_skew, blur, False,
        1, 0, 0, False, 2, -1, 0, "#000000", 0, 1.0, 0, MARGINS, False, False, True, "",
    )
    if noise_std:  # Gaussian noise added after rendering, as in the authors' add_gaussian_noise()
        arr = np.asarray(img).astype(float)
        arr += np.random.default_rng(seed).normal(0, noise_std, arr.shape)
        img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=20, help="images per cell")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--text", type=Path, default=ROOT / "polish" / "texts" / "lalka-tom-pierwszy.txt")
    ap.add_argument("--out", type=Path, default=ROOT / "polish" / "data")
    args = ap.parse_args()

    text = load_text(args.text)
    words, sentences = word_pool(text), sentence_pool(text)
    chars = (set("".join(sentences)) | set("".join(words)) | POLISH) - {" "}
    fonts = {t: font_coverage(ROOT / "polish" / "fonts" / t, chars) for t in ("printed", "handwritten")}
    print(f"words: {len(words)}, sentences: {len(sentences)}, fonts: { {t: len(f) for t, f in fonts.items()} }")

    def sample(pool, keep, name):
        candidates = [x for x in pool if keep(x)]
        random.Random(f"{args.seed}-{name}").shuffle(candidates)
        assert len(candidates) >= args.n, f"not enough candidates for {name}: {len(candidates)}"
        return candidates[: args.n]

    def has_polish(s):
        return bool(POLISH & set(s))

    cells = []  # (type, category, subcategory, texts, distortion)
    for typ in fonts:
        cells += [
            (typ, "polish_character_confusion", "polish", sample(words, has_polish, f"{typ}-polish"), "clean"),
            (typ, "polish_character_confusion", "non_polish",
             sample(words, lambda w: not has_polish(w), f"{typ}-non_polish"), "clean"),
            (typ, "word_length_effects", "short_words", sample(words, lambda w: len(w) < 10, f"{typ}-short"), "clean"),
            (typ, "word_length_effects", "long_words", sample(words, lambda w: len(w) > 10, f"{typ}-long"), "clean"),
            (typ, "context_dependent_errors", "word", sample(words, lambda w: True, f"{typ}-word"), "clean"),
            (typ, "context_dependent_errors", "sentences", sample(sentences, lambda s: True, f"{typ}-sent"), "clean"),
        ]
        shared = sample(words, lambda w: True, f"{typ}-distortion")
        cells += [(typ, "distortion_type", d, shared, d) for d in DISTORTIONS]

    (args.out / "images").mkdir(parents=True, exist_ok=True)
    rows = []
    for typ, cat, sub, texts, distortion in cells:
        font_rng = random.Random(f"{args.seed}-{typ}-{cat}-fonts")  # same font for the same word across distortions
        for i, t in enumerate(texts):
            font = font_rng.choice(sorted(f for f, cov in fonts[typ].items() if set(t) - {" "} <= cov))
            seed = random.Random(f"{args.seed}-{typ}-{cat}-{i}").randrange(2**31)
            file = f"images/{typ}_{cat}_{sub}_{i:04d}.png"
            render(t, font, seed, **DISTORTIONS[distortion]).save(args.out / file)
            rows.append(dict(file=file, text=t, type=typ, category=cat, subcategory=sub, font=Path(font).stem,
                             has_polish_chars=int(has_polish(t)), length=len(t), seed=seed))
        print(f"{typ:12s} {cat:27s} {sub:15s} {len(texts)}")

    with open(args.out / "labels.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} images to {args.out}")


if __name__ == "__main__":
    main()
