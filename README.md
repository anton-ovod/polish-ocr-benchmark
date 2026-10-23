# Polski benchmark OCR

Projekt na studia magisterskie: powtórzenie badania z artykułu
Yılmaz i in., *Benchmarking OCR and vision-language models for Turkish text recognition* (IJDAR, 2026,
[DOI 10.1007/s10032-026-00613-6](https://doi.org/10.1007/s10032-026-00613-6)) oraz własne badanie
tej samej metodologii dla języka polskiego.

Stan: **MVP** (22.10.2026). Mały zbiór (20 obrazów na komórkę, razem 440), modele uruchamiane lokalnie na CPU.
Qwen2.5-VL jeszcze nie był liczony.

## Co zostało zrobione

1. **Powtórzenie badania bazowego** (`replication/`)
   - Liczby z artykułu przeliczone z per-obrazowych predykcji autorów. Kod autorów (i zapisany przez nich
     JSON) dzieli odległość edycyjną przez długość *predykcji* zamiast wzorca. Liczby z tekstu artykułu
     odtwarza inny wariant z ich repo: małe litery, bez spacji i interpunkcji, dzielenie przez długość wzorca
     (artykuł tego nie opisuje).
   - Ponowne uruchomienie PaddleOCR i TrOCR na warstwowej próbce 330 obrazów tureckich, z ustawieniami
     z notebooków autorów: 99,7% predykcji identycznych, CER 0,315 wobec 0,314 (Paddle) i 0,376 wobec 0,376 (TrOCR).
2. **Własny zbiór polski** (`src/generate_dataset.py`)
   - Generator TRDG 1.8.0 z parametrami autorów, druk i pismo odręczne, tekst z *Lalki* (Wolne Lektury,
     domena publiczna).
   - Komórki: z polskimi znakami / bez, krótkie / długie słowa, słowo / zdanie, zakłócenia
     (clean, blur, rotated, noisy, low_resolution) na tych samych słowach.
   - Fonty z Google Fonts sprawdzone w `cmap` na 18 polskich liter (`tools/fonts/`).
3. **Modele** (`src/ocr_models.py`, `src/run_ocr.py`): Tesseract `pol`, EasyOCR `pl`, PaddleOCR (`pl` i `en`
   jak u autorów), TrOCR, Qwen2.5-VL (3B lokalnie, 7B przez `colab/qwen_colab.ipynb`).
4. **Ewaluacja** (`src/metrics.py`, `src/summarize.py`): CER i WER (NFC, małe litery, CER obcięty do 1),
   odsetek błędów wyłącznie diakrytycznych, bootstrapowe 95% przedziały ufności i efekty czynników (Δ CER).
   Skrypt zapisuje CSV w `polish/results/summary/` i tabele LaTeX w `docs/article/tables/`.
5. **Dokumenty** (`docs/`): szkic artykułu (LNCS, po polsku) i prezentacja artykułu bazowego (8 slajdów).

### Wstępne wyniki (n = 440, CER)

| Model | Druk | Pismo odręczne | Razem |
|---|---|---|---|
| EasyOCR `pl` | 0,085 | 0,257 | 0,171 |
| PaddleOCR `en` | 0,114 | 0,249 | 0,182 |
| PaddleOCR `pl` | 0,111 | 0,261 | 0,186 |
| TrOCR | 0,122 | 0,283 | 0,202 |
| Tesseract `pol` | 0,114 | 0,329 | 0,221 |

Polskie znaki istotnie podnoszą błąd PaddleOCR (Δ ≈ +0,23; w jego słowniku brak ń, ś, ź, ż) i TrOCR,
a nie Tesseracta ani EasyOCR. Niska rozdzielczość i pismo odręczne szkodzą wszystkim modelom.

## Struktura

```
src/              generator, modele OCR, metryki, podsumowanie
replication/      powtórzenie badania bazowego (analyze.py, build_labels.py, results/)
polish/           teksty, fonty, wygenerowany zbiór (data/) i wyniki (results/)
tools/fonts/      pobieranie i sprawdzanie fontów odręcznych
colab/            notebook dla Qwen2.5-VL na GPU
docs/             artykuł (article/) i prezentacja (presentation/), LaTeX
```

## Uruchomienie

```bash
uv venv -p 3.12 .venv
uv pip install --python .venv/bin/python torch==2.14.1 torchvision==0.29.1 --index-url https://download.pytorch.org/whl/cpu
uv pip install --python .venv/bin/python -r requirements.txt
uv pip install --python .venv/bin/python --no-deps trdg==1.8.0
uv venv -p 3.12 .venv-paddle && uv pip install --python .venv-paddle/bin/python -r requirements-paddle.txt
# Tesseract z polskim modelem: apt install tesseract-ocr tesseract-ocr-pol
#   (albo lokalnie: micromamba create -p .tools/tess -c conda-forge tesseract, wtedy kod sam go znajdzie)

.venv/bin/python src/generate_dataset.py --n 20   # polish/data/ (ziarno 42)
bash src/run_all_local.sh                          # wszystkie modele, można przerywać i wznawiać
.venv/bin/python src/summarize.py                  # tabele i CSV
cd docs/article && latexmk -pdf main.tex
```

Do powtórzenia badania bazowego potrzebne są dane autorów, których nie ma w repo:
- obrazy z Zenodo ([10.5281/zenodo.21923181](https://doi.org/10.5281/zenodo.21923181)), rozpakowane do `replication/data/`;
- `json/cer_wer_calculated.json` z [repo autorów](https://github.com/OCR-benchmark-project/turkish-synthetic-text-recognition-benchmark)
  (commit `966b119`) skopiowany do `replication/authors/`.

Potem `replication/build_labels.py --n 10` i `replication/analyze.py`.

## Licencje

Kod: MIT. Wygenerowane dane i wyniki: CC BY 4.0. Fonty w `polish/fonts/`: SIL OFL / Apache 2.0 (Google Fonts).
Teksty: Wolne Lektury, domena publiczna.
