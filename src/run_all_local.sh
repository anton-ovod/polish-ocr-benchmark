#!/usr/bin/env bash
# Run every locally feasible OCR experiment (CPU only). Resumable: re-running skips finished images.
# Qwen2.5-VL-3B runs last on CPU (~25 s/image); the 7B variant used by the authors needs a GPU, see
# colab/qwen_colab.ipynb.
set -euo pipefail
cd "$(dirname "$0")/.."
PY=.venv/bin/python
PADDLE=.venv-paddle/bin/python

# Polish study
$PY src/run_ocr.py --model tesseract --lang pol --data polish/data --out polish/results/tesseract.csv
$PY src/run_ocr.py --model easyocr --lang pl --data polish/data --out polish/results/easyocr.csv
$PADDLE src/run_ocr.py --model paddle --lang pl --data polish/data --out polish/results/paddle.csv
# authors' Paddle setting (lang='en') on Polish, to separate the language model from the engine
$PADDLE src/run_ocr.py --model paddle --lang en --data polish/data --out polish/results/paddle_en.csv

# Replication on a stratified sample of the authors' Turkish images, same settings as their notebooks
$PADDLE src/run_ocr.py --model paddle --lang en --data replication/data --labels sample.csv \
    --out replication/results/paddle.csv
$PY src/run_ocr.py --model trocr --data replication/data --labels sample.csv --out replication/results/trocr.csv

# the transformer models are the slowest, so they go last (TrOCR ~4 s/image, Qwen 3B ~25 s/image on CPU)
$PY src/run_ocr.py --model trocr --data polish/data --out polish/results/trocr.csv
$PY src/run_ocr.py --model qwen --lang Polish --checkpoint Qwen/Qwen2.5-VL-3B-Instruct --data polish/data \
    --out polish/results/qwen.csv
