#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PY=.venv/bin/python
PADDLE=.venv-paddle/bin/python

$PY src/run_ocr.py --model tesseract --lang pol --data polish/data --out polish/results/tesseract.csv
$PY src/run_ocr.py --model easyocr --lang pl --data polish/data --out polish/results/easyocr.csv
$PADDLE src/run_ocr.py --model paddle --lang pl --data polish/data --out polish/results/paddle.csv
$PY src/run_ocr.py --model trocr --data polish/data --out polish/results/trocr.csv
$PY src/run_ocr.py --model qwen --lang Polish --checkpoint Qwen/Qwen2.5-VL-3B-Instruct --data polish/data \
    --out polish/results/qwen.csv
