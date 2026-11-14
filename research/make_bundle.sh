#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
BUNDLE=research/ocr_bundle.zip
rm -f "$BUNDLE"
zip -qr "$BUNDLE" common/*.py research/analyze.py research/data research/gold/data -x '*/__pycache__/*'
ls -lh "$BUNDLE"
