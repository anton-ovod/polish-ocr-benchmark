# Polski benchmark OCR

Projekt na studia magisterskie: powtórzenie badania z artykułu
Yılmaz i in., *Benchmarking OCR and vision-language models for Turkish text recognition* (IJDAR, 2026,
[DOI 10.1007/s10032-026-00613-6](https://doi.org/10.1007/s10032-026-00613-6)) oraz własne badanie
tej samej metodologii dla języka polskiego. Plan i ustalenia: `CLAUDE.md`.

Wszystko liczymy w Google Colab (GPU). Lokalnie nic się nie uruchamia poza kompilacją LaTeX-a.

## Struktura

```
common/       loadery modeli, runner, metryki (wspólne dla obu badań)
replication/  powtórzenie badania bazowego (notebook Colab, wyniki, analiza)
research/     nasze badanie: korpus, fonty, generator, tabele i wykresy
docs/         artykuł (article/) i prezentacja artykułu bazowego (presentation/), LaTeX
```

## Powtórzenie badania bazowego

Ponowne uruchomienie 8 otwartych modeli z artykułu (bez GPT-4o i Claude'a) na warstwowej próbce 1650 obrazów
tureckich (A100). Średni CER różni się od predykcji autorów najwyżej o 0,001, a u Pixtrala o 0,007. Liczby dla
każdego modelu: `replication/results/rerun_vs_authors.csv`.

Dane autorów nie są w repo:
- obrazy z Zenodo ([10.5281/zenodo.21923181](https://doi.org/10.5281/zenodo.21923181)) do `replication/data/`;
- `json/cer_wer_calculated.json` z [repo autorów](https://github.com/OCR-benchmark-project/turkish-synthetic-text-recognition-benchmark)
  (commit `966b119`) do `replication/authors/`.

Potem `python replication/build_labels.py --n 50` i `replication/make_bundle.sh`. Powstały
`replication/ocr_bundle.zip` trafia do `MyDrive/ocr-benchmark/`, a `replication/replication.ipynb` uruchamia modele
na GPU. Wyniki z `MyDrive/ocr-benchmark/replication/` kopiujemy do `replication/results/` i uruchamiamy
`replication/analyze.py` (wymaga `jiwer`, `editdistance`).

## Własne badanie

W przygotowaniu (`research/`): zbiór syntetyczny TRDG z polskim korpusem, 1008 zdjęć odręcznej Inwokacji
i 9 modeli. Notebook `research/research.ipynb` jeszcze nie istnieje.

## Licencje

Kod: MIT. Fonty w `research/fonts/`: SIL OFL / Apache 2.0 (Google Fonts). Teksty: Wolne Lektury, domena publiczna.
