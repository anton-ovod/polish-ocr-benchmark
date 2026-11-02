#!/usr/bin/env bash
# Pack the code and images needed on Colab into colab/ocr_bundle.zip (~30 MB):
#   src/, polish/data/ (images + labels.csv), the Turkish replication sample, and what
#   colab/replication_colab.ipynb needs: the runner, analyze.py, the authors' predictions and our earlier re-runs.
set -euo pipefail
cd "$(dirname "$0")/.."
rm -f colab/ocr_bundle.zip
zip -qr colab/ocr_bundle.zip src/*.py polish/data -x '*/__pycache__/*'
# Turkish sample: images listed in sample.csv, plus sample.csv itself
(cd replication/data && tail -n +2 sample.csv | cut -d, -f1 | zip -q ../../colab/ocr_bundle.zip -@ && zip -q ../../colab/ocr_bundle.zip sample.csv)
# zip stores the Turkish files relative to replication/data; move them under that prefix
python3 - <<'EOF'
import zipfile, shutil
src, dst = "colab/ocr_bundle.zip", "colab/ocr_bundle.tmp.zip"
with zipfile.ZipFile(src) as zin, zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        name = item.filename
        if not name.startswith(("src/", "polish/")):
            name = "replication/data/" + name
        zout.writestr(name, zin.read(item))
shutil.move(dst, src)
EOF
zip -q colab/ocr_bundle.zip colab/run_replication.py replication/analyze.py replication/authors/cer_wer_calculated.json \
    replication/results/trocr.csv replication/results/paddle.csv
ls -lh colab/ocr_bundle.zip
