#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
BUNDLE=colab/ocr_bundle.zip
rm -f "$BUNDLE"
zip -qr "$BUNDLE" src/*.py polish/data -x '*/__pycache__/*'
tail -n +2 replication/data/sample.csv | cut -d, -f1 | sed 's|^|replication/data/|' | zip -q "$BUNDLE" -@
zip -q "$BUNDLE" replication/data/sample.csv colab/run_replication.py replication/analyze.py \
    replication/authors/cer_wer_calculated.json
ls -lh "$BUNDLE"
