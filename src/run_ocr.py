"""Run one OCR model over a dataset and append predictions to a CSV (safe to interrupt and resume).

Examples:
    .venv/bin/python src/run_ocr.py --model tesseract --lang pol --data polish/data --out polish/results/tesseract.csv
    .venv-paddle/bin/python src/run_ocr.py --model paddle --lang pl --data polish/data --out polish/results/paddle.csv

Input:  <data>/labels.csv with a `file` column holding image paths relative to <data>.
Output: CSV with columns file, prediction, seconds.
"""
import argparse
import csv
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from ocr_models import MODELS  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=MODELS)
    ap.add_argument("--lang", default=None, help="model language code (e.g. pol, pl, en); model default if omitted")
    ap.add_argument("--data", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--checkpoint", default=None, help="Hugging Face model id for trocr/qwen (default in ocr_models.py)")
    ap.add_argument("--labels", default="labels.csv", help="labels file inside --data (e.g. a subset)")
    ap.add_argument("--limit", type=int, default=None, help="only the first N images (smoke test)")
    args = ap.parse_args()

    with open(args.data / args.labels, encoding="utf-8") as f:
        files = [row["file"] for row in csv.DictReader(f)][: args.limit]
    done = set()
    if args.out.exists():
        with open(args.out, encoding="utf-8") as f:
            done = {row["file"] for row in csv.DictReader(f)}
    todo = [p for p in files if p not in done]
    print(f"{args.model}: {len(done)} done, {len(todo)} to go", flush=True)
    if not todo:
        return

    options = {"lang": args.lang, "model": args.checkpoint}
    read = MODELS[args.model](**{k: v for k, v in options.items() if v})
    args.out.parent.mkdir(parents=True, exist_ok=True)
    new_file = not args.out.exists() or args.out.stat().st_size == 0
    with open(args.out, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if new_file:
            writer.writerow(["file", "prediction", "seconds"])
            f.flush()
        errors_in_row = 0
        for i, file in enumerate(todo, 1):
            t0 = time.perf_counter()
            try:
                pred = read(args.data / file)
                errors_in_row = 0
            except Exception as e:  # one bad image must not stop the whole run...
                print(f"error {file}: {e}", flush=True)
                errors_in_row += 1
                if errors_in_row >= 5:  # ...but a broken model must not fill the CSV with empty predictions
                    raise
                pred = ""
            writer.writerow([file, pred, round(time.perf_counter() - t0, 3)])
            if i % 25 == 0:
                f.flush()
                print(f"  {i}/{len(todo)}", flush=True)


if __name__ == "__main__":
    main()
