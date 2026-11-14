#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
BUNDLE=research/ocr_bundle.zip
rm -f "$BUNDLE"
zip -qr "$BUNDLE" common/*.py research/*.py research/texts/lalka-tom-*.txt research/fonts/printed research/fonts/handwritten \
    research/gold/images -x '*/__pycache__/*'
ls -lh "$BUNDLE"
