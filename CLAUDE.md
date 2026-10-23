# Polski benchmark OCR

Grupowy projekt na studia magisterskie: powtórzenie badania z artykułu bazowego i przeprowadzenie
własnego badania ze zmienionym jednym elementem (język polski zamiast tureckiego).

## Artykuł bazowy

Y. Yılmaz, E.G. Hanoğlu, A.G. Özkan, K. Öztoprak, "Benchmarking OCR and vision-language models for
Turkish text recognition: a comprehensive evaluation using synthetic data", IJDAR (Springer), 2026,
DOI 10.1007/s10032-026-00613-6. Lista ministerialna: 100 pkt.

- Dane: Zenodo 10.5281/zenodo.21923181 (CC BY 4.0), generator TRDG 1.8.0.
- Kod: https://github.com/OCR-benchmark-project/turkish-synthetic-text-recognition-benchmark
- Kategorie: litery specyficzne vs bez nich, krótkie vs długie słowa (próg ok. 10 znaków), słowo vs
  zdanie, zakłócenia (clean, rotated, noisy, blur, low_resolution). Typy tekstu: printed, handwritten,
  scene.

## Nasz plan (ustalony 22.10.2026, do omówienia na callu 23.10)

Zasada nadrzędna: **prostota**. Artykuł jest na zaliczenie, nie do publikacji, więc nie dokładamy analiz.

**Tytuł roboczy:** „Ocena silników OCR i modeli wizyjno-językowych w rozpoznawaniu tekstu polskiego na danych
syntetycznych”

**Cel:** porównanie skuteczności klasycznych silników OCR i modeli wizyjno-językowych w rozpoznawaniu tekstu
polskiego oraz określenie, jak na błąd wpływają polskie znaki diakrytyczne, długość tekstu, rodzaj pisma
i zniekształcenia obrazu. Nie porównujemy polskiego z tureckim. Wyniki autorów najwyżej jako jedno zdanie
w dyskusji.

### Dane
- Generator TRDG 1.8.0, tylko druk (printed) i pismo ręczne (handwritten), **bez tekstu w scenie**.
  Generator piszemy sami, kod autorów służy jako wzór parametrów (ma bugi).
- Jeden korpus: Wolne Lektury, **tylko teksty z domeny publicznej** (Prus, Sienkiewicz, Żeromski…),
  słowa filtrowane słownikiem.
- Porównania:
  - z polskimi znakami / bez,
  - krótkie / długie słowa (próg 10 znaków),
  - druk / pismo ręczne,
  - słowo / zdanie (4–8 słów),
  - zniekształcenia: clean, blur, rotated, noisy, low_res (te same słowa, to samo ziarno).
- Około 100 obrazów na komórkę, łącznie około 2000.
- Fonty z Google Fonts, każdy sprawdzony (`cmap`) na 18 polskich liter (ąćęłńóśźż i wielkie).
  **Sprawdzone 22.10:** z 357 fontów odręcznych 272 ma komplet polskich liter i A–Z; po odrzuceniu 104
  niemal identycznych wariantów Playwrite zostaje 168. Lista: `tools/fonts/handwriting_fonts_pl.txt`
  (posortowana wg popularności), skrypty `tools/fonts/fetch_fonts.py` i `tools/fonts/check_fonts.py`.
  W zbiorze używamy 19 najpopularniejszych; Amatic SC wykluczony (same kapitaliki), patrz
  `polish/fonts/excluded/`.
  Uwaga: pole `subsets` w metadanych Google Fonts jest niewiarygodne, trzeba sprawdzać `cmap`.
- Wycięte: tekst w scenie (COCO), Gold Standard z prawdziwymi zdjęciami. W ograniczeniach powołujemy się
  na ρ = 0,92 autorów.

### Modele (5, lokalnie na CPU; Qwen 7B opcjonalnie na Colabie)
- Z artykułu bazowego: TrOCR, PaddleOCR, Qwen2.5-VL (3B lokalnie, 7B jak u autorów tylko na GPU > 20 GB).
- Dodane przez nas: Tesseract `pol`, EasyOCR `pl`.
- Bez modeli komercyjnych. Uzasadnienie w artykule: tylko modele otwarte, uruchamiane lokalnie, dla pełnej
  odtwarzalności i zerowego kosztu (API są zamknięte, płatne i zmieniają się bez wersjonowania).

### Ewaluacja
- CER (jiwer), a dla zdań też WER.
- Wszystko małymi literami, normalizacja Unicode do NFC, CER obcięty do 1,0.
- Prompt dla Qwena: prompt autorów z „Turkish” zamienionym na „Polish”.

### Elementy nowości
1. Metodologia benchmarku przeniesiona na język polski.
2. Klasyczne silniki OCR z polskim modelem językowym (Tesseract `pol`, EasyOCR `pl`), których autorzy
   nie badali.
3. Wpływ polskich znaków diakrytycznych na błąd rozpoznawania.
4. Otwarty zbiór i kod, odtwarzalne na zwykłym laptopie (CPU).

### Kod i dane
- Jedno publiczne repo na GitHubie: generator, notebook Colab, skrypt CER/WER, CSV z wynikami, README.
- Obrazy jako zip w GitHub Release (dają się też odtworzyć z generatora przy stałym ziarnie).
- Licencje: kod MIT, dane CC BY 4.0. Fonty mają licencję OFL.

### Role (osoby jeszcze nieprzypisane)
- **A: dane.** Generator, słownik, sprawdzanie fontów, kategorie, zniekształcenia. Wynik: obrazy
  i CSV z etykietami. Ścieżka krytyczna, startuje pierwsza.
- **B: modele i ewaluacja.** Notebook z 5 modelami, skrypt CER/WER. Na start testuje na kilkunastu
  ręcznie zrobionych obrazkach.
- **C: artykuł bazowy i tekst.** Prezentacja 7.11, szkielet LNCS, wstęp, przegląd literatury,
  bibliografia (do 10 pozycji). Naturalnie osoba, która ma już powtórzenie badania z artykułu bazowego.
- Na koniec wszyscy razem: wyniki, dyskusja, redakcja.

### Harmonogram
| Termin | Co |
|---|---|
| ~25.10, Lab 3 | powtórzenie badania z artykułu bazowego, z liczbami porównanymi do tabeli autorów |
| do 7.11 | generator i pełny zbiór (A), modele na próbce (B), **prezentacja bazowego na Lab 4, 7.11** (C) |
| do 15.11 | **pełne wyniki 5 modeli**, tabela CER/WER |
| 16–22.11 | wykresy, slajdy z własnym badaniem, **Lab 5 (zaliczenie) 22.11** |
| 23.11–7.12 | pisanie 6 stron LNCS, wplatamy uwagi z Lab 5 |
| 8–10.12 | bufor i złożenie w turze I (tura II 15.01 jako zapas) |

### Do ustalenia na callu
- Kto bierze rolę A, B i C.
- Czy powtórzenie badania z artykułu bazowego na Lab 3 ma liczby porównane z tabelą autorów.
- ~~Kto zakłada repo na GitHubie.~~ Założone 22.10: https://github.com/anton-ovod/polish-ocr-benchmark (prywatne;
  upublicznić: `gh repo edit --visibility public --accept-visibility-change-consequences`).

## Stan prac (MVP, 22.10.2026)

Kod, identyfikatory, komentarze, nazwy plików i kolumny CSV piszemy **po angielsku**; dokumenty
(artykuł, slajdy) po polsku.

### Struktura
- `src/`: generator (`generate_dataset.py`), modele (`ocr_models.py`), runner (`run_ocr.py`, wznawialny),
  metryki (`metrics.py`), podsumowanie i tabele LaTeX (`summarize.py`), `run_all_local.sh`.
- `polish/`: korpus (`texts/`), fonty (`fonts/`), zbiór (`data/labels.csv` + `data/images/`), wyniki
  (`results/<model>.csv`, `results/summary/`).
- `replication/`: powtórzenie badania bazowego. `authors/cer_wer_calculated.json` (predykcje autorów
  z ich repo), `build_labels.py` (etykiety + próbka 10 obrazów/komórkę = 330), `analyze.py`, `results/`.
  Obrazy autorów z Zenodo w `replication/data/syntetic-turkish-dataset/`.
- `colab/`: `qwen_colab.ipynb` i `make_bundle.sh` (tylko do Qwen 7B na GPU).
- `docs/presentation/base_article.tex`: 8 slajdów o artykule bazowym (Lab 4, 7.11).
- `docs/article/main.tex`: szkielet LNCS po polsku z `\TODO{}`; tabele `docs/article/tables/*.tex`
  generuje `summarize.py`, nie edytować ręcznie.
- `tools/fonts/`: pobieranie i sprawdzanie fontów.

### Uruchamianie
```
.venv/bin/python src/generate_dataset.py --n 20      # 440 obrazów; --n 100 = docelowe 2200 (n=20 to podzbiór)
src/run_all_local.sh                                 # wszystkie modele, wznawialne
.venv/bin/python src/summarize.py                    # tabele + docs/article/tables/
.venv/bin/python replication/analyze.py              # powtórzenie badania bazowego
cd docs/article && latexmk -pdf main.tex             # analogicznie docs/presentation
```
Środowiska: `.venv` (py3.12, torch CPU; brak pip, instalacja `uv pip install --python .venv/bin/python`),
`.venv-paddle` (paddleocr 2.9.1), Tesseract w `.tools/tess`. Wyniki Qwen: `qwen.csv` = 3B, `qwen7b.csv` = 7B.

### Ustalenia (do artykułu i prezentacji)
- **CER w kodzie autorów** (`cer_wer_calculation.py`, zamienione argumenty) dzieli odległość przez długość
  *predykcji*; tak liczone są wszystkie 65 036 wartości `cer` w ich JSON-ie (bez małych liter). Liczby
  z tekstu artykułu odtwarza jednak inny wariant z ich repo (`graphs_lower_trocr.py`): małe litery,
  **bez spacji i interpunkcji**, /długość prawdy; artykuł tego nie opisuje. Kolumna `nospace` w
  `replication/results/`: TrOCR 0,380 vs 0,38; GPT-4o turkish 0,065 vs 0,065, clean 0,017 vs 0,017.
  Nieodtworzone: GPT-4o non_turkish 0,066 vs 0,055, Paddle clean 0,260 vs 0,239. W tym wariancie TrOCR
  jest ostatni (0,380), a GOT-OCR2, który gubi spacje, ma 0,311 (poprawny CER 0,391, czyli ostatni).
- **Claude:** JSON autorów zawiera Claude 3.7 Sonnet (CER 0,349), artykuł podaje Sonnet 4 z CER 0,197.
- **Ponowny przebieg PaddleOCR i TrOCR** (330 obrazów): po 99,7% predykcji identycznych z autorami.
- **TrOCR:** checkpoint ma `use_cache=False` (2,5× wolniej na CPU, włączamy cache: wynik identyczny);
  `max_length` domyślne 21 tokenów jak u autorów, więc dłuższe zdania są ucinane (u autorów też).
- **PaddleOCR `pl`** używa wspólnego słownika łacińskiego (`latin_dict.txt`) bez ń, ś, ź, ż: nie może ich
  zwrócić („ludnošci”, „5piacy”), stąd `pl` ≈ `en`.
- Tekstury papieru autorów nie są opublikowane; renderujemy na białym tle.
- **Obliczenia w artykule** (sekcje 3.3–3.4): wzory (1)–(5) — CER/WER, średnia, odsetek błędów
  diakrytycznych, bootstrap 95% CI (B=1000 jak u autorów), efekt Δ = różnica średnich z CI. Liczy je
  `summarize.py` → `tables/effects.tex` i kolumna CI w `overall.tex`.
- Wstępne wyniki PL (n=20, CER): Tesseract 0,22, EasyOCR 0,17, Paddle pl 0,19, Paddle en 0,18.

### Do zrobienia
- Wyniki TrOCR i Qwen 3B na zbiorze polskim, potem pełny zbiór `--n 100`.
- Prezentacja: uzupełnić nazwiska, zweryfikować IF w Clarivate JCR.
- Artykuł: wszystkie `\TODO{}`, przegląd literatury (prace o OCR dla polskiego), opis wyników.
- Repo na GitHubie (kod MIT, dane CC BY 4.0).
