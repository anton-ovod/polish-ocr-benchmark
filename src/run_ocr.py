"""Run one OCR model over a dataset and append predictions to a CSV."""
import argparse
import csv
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from ocr_models import MODELS


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
        failed = []
        for i, file in enumerate(todo, 1):
            t0 = time.perf_counter()
            try:
                pred = read(args.data / file)
            except Exception as e:
                print(f"error {file}: {e}", flush=True)
                failed.append(file)
                if len(failed) >= 5:
                    f.flush()
                    raise
                continue
            writer.writerows([name, "", 0] for name in failed)
            failed.clear()
            writer.writerow([file, pred, round(time.perf_counter() - t0, 3)])
            if i % 25 == 0:
                f.flush()
                print(f"  {i}/{len(todo)}", flush=True)
        writer.writerows([name, "", 0] for name in failed)


if __name__ == "__main__":
    main()
