#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
BUNDLE=replication/ocr_bundle.zip
rm -f "$BUNDLE"
zip -qr "$BUNDLE" common/*.py -x '*/__pycache__/*'
tail -n +2 replication/data/sample.csv | cut -d, -f1 | sed 's|^|replication/data/|' | zip -q "$BUNDLE" -@
zip -q "$BUNDLE" replication/data/sample.csv replication/analyze.py \
    replication/authors/cer_wer_calculated.json
ls -lh "$BUNDLE"
