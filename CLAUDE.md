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
(artykuł, slajdy) po polsku. W kodzie **nie piszemy komentarzy**, a docstring to najwyżej jedna linia opisu modułu;
ustalenia, które trzeba zachować, trafiają do tego pliku.

### Struktura
- `src/`: generator (`generate_dataset.py`), modele (`ocr_models.py`), runner (`run_ocr.py`, wznawialny),
  metryki (`metrics.py`), podsumowanie i tabele LaTeX (`summarize.py`), wykresy (`plot_results.py` →
  `docs/article/figures/*.{pdf,png}`), `run_all_local.sh`.
- `polish/`: korpus (`texts/`), fonty (`fonts/`), zbiór (`data/labels.csv` + `data/images/`), wyniki
  (`results/<model>.csv`, `results/summary/`).
- `replication/`: powtórzenie badania bazowego. `authors/cer_wer_calculated.json` (predykcje autorów
  z ich repo), `build_labels.py` (etykiety + próbka; używamy `--n 50` = 1650 obrazów, większa próbka zawiera
  mniejszą), `analyze.py`, `results/` (`<model>.csv`, `<model>_vs_authors.csv`, `rerun_vs_authors.csv`,
  `runs.json`, `envs/` z wersjami pakietów). Obrazy autorów z Zenodo w `replication/data/syntetic-turkish-dataset/`.
- `colab/`: `replication_colab.ipynb` + `run_replication.py` (powtórzenie: 8 modeli, każdy we własnym środowisku,
  wznawialne, wyniki na Dysku w `MyDrive/ocr-benchmark/replication/`), `qwen_colab.ipynb` (Qwen 7B na zbiorze
  polskim), `make_bundle.sh` (buduje `ocr_bundle.zip`, poza gitem).
- `docs/presentation/base_article.tex`: 8 slajdów o artykule bazowym (Lab 4, 7.11). `docs/presentation_v2/`: wersja
  kolegi z notatkami do wystąpienia; `base_article.tex` kompilujemy z `-jobname=prezentacja_v2`.
- `docs/article/main.tex`: szkielet LNCS po polsku z `\TODO{}`; tabele `docs/article/tables/*.tex`
  generuje `summarize.py`, nie edytować ręcznie.
- `tools/fonts/`: pobieranie i sprawdzanie fontów.

### Uruchamianie
```
.venv/bin/python src/generate_dataset.py --n 20      # 440 obrazów; --n 100 = docelowe 2200 (n=20 to podzbiór)
src/run_all_local.sh                                 # wszystkie modele, wznawialne
.venv/bin/python src/summarize.py                    # tabele + docs/article/tables/
.venv/bin/python src/plot_results.py                 # wykresy z polish/results/summary/ (po summarize.py)
.venv/bin/python replication/build_labels.py --n 50  # próbka powtórzenia, potem colab/make_bundle.sh
.venv/bin/python replication/analyze.py              # powtórzenie badania bazowego (modele liczymy w Colabie)
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
- **Ponowny przebieg 8 otwartych modeli** (2.11.2026, Colab A100, 1650 obrazów = 50 na każdą z 33 komórek,
  25% zbioru; bez GPT-4o i Claude'a). Liczone naszym CER (NFC, małe litery), więc nie są to wartości z tekstu
  artykułu. Kolejność modeli taka sama jak u autorów:

  | Model | Identyczne | CER nasz | CER autorów | s/obraz |
  |---|---:|---:|---:|---:|
  | Qwen2.5-VL 7B | 95,8% | 0,081 | 0,081 | 0,32 |
  | InternVL3-8B | 90,4% | 0,183 | 0,184 | 0,60 |
  | DeepSeek-VL2-tiny | 99,9% | 0,191 | 0,191 | 0,34 |
  | Phi-3.5-vision | 93,8% | 0,242 | 0,241 | 0,91 |
  | PaddleOCR | 99,4% | 0,311 | 0,311 | 0,04 |
  | Pixtral-12B | 28,3% | 0,357 | 0,364 | 0,24 |
  | TrOCR | 99,9% | 0,373 | 0,373 | 0,11 |
  | GOT-OCR2 | 93,5% | 0,393 | 0,392 | 0,29 |

  - Pixtral: średnią da się powtórzyć, pojedynczych predykcji nie (CER między przebiegami 0,389). Prawdopodobnie
    losowość (domyślna temperatura vLLM, brak ziarna), niepotwierdzone drugim własnym przebiegiem.
  - Puste odpowiedzi nasze / autorów / na tych samych obrazach: Paddle 173/173/173, Phi 61/60/59, GOT 1/1/1,
    Pixtral 2/1/0.
  - Próbka a całość: dla predykcji autorów CER różni się od CER z 6600 obrazów najwyżej o 0,010 (TrOCR).
  - Prompty i ustawienia generowania są dosłownie z notebooków autorów. Jedyna różnica to brak flash-attn (nie ma
    gotowych pakietów): Phi i Qwen używają domyślnej uwagi, InternVL własnej. GOT: repo autorów `ucaslcl/GOT-OCR2_0`
    przekierowuje na `stepfun-ai/GOT-OCR2_0`.
  - Środowiska: `paddlepaddle-gpu` 2.6.2 wymaga CUDA 11.8 i cuDNN 8, więc instalujemy je jako pakiety `nvidia-*`
    i dopisujemy do `LD_LIBRARY_PATH` (nie nadpisywać: na Colabie wskazuje sterownik). Torch 2.0 nie uruchamia się
    z `expandable_segments`. Bez GPU Paddle tylko ostrzega i liczy na CPU, dlatego kod zgłasza wtedy błąd.
  - Odtwarzalność środowisk: checkpointy przypięte do commitów (`runs.json`), wersje pakietów w `envs/<model>.txt`.
    Data `--exclude-newer` nie obejmuje kroku z torchem, więc środowiska nie odtwarzają w pełni stanu z 2025 r.
  - TrOCR w tym przebiegu ma włączony cache, a `sec_per_image` obejmuje też pomiar z pierwszych 330 obrazów
    (ta sama karta). Suma dla 8 modeli to ok. 2,85 s/obraz.
- **TrOCR:** checkpoint ma `use_cache=False` (2,5× wolniej na CPU, włączamy cache: wynik identyczny);
  `max_length` domyślne 21 tokenów jak u autorów, więc dłuższe zdania są ucinane (u autorów też).
  Transformers 5 tworzy model na urządzeniu `meta` i nie wypełnia tabeli pozycji, dlatego `trocr()` liczy ją od nowa.
- **Generator:** TRDG 1.8.0 woła `getsize()` usunięte z Pillow 10, więc podmieniamy `get_text_height` jak autorzy.
- **Tesseract:** `--psm 7`, bo obraz zawiera jedną linię tekstu.
- **PaddleOCR `pl`** używa wspólnego słownika łacińskiego (`latin_dict.txt`) bez ń, ś, ź, ż: nie może ich
  zwrócić („ludnošci”, „5piacy”). Przebieg z `en` (ustawienie autorów) dawał to samo (CER 0,18 vs 0,19), więc go usunęliśmy;
  w artykule jest tylko PaddleOCR `pl`, podpisywany po prostu „PaddleOCR”.
- Tekstury papieru autorów nie są opublikowane; renderujemy na białym tle.
- **Obliczenia w artykule** (sekcje 3.3–3.4): wzory (1)–(5) — CER/WER, średnia, odsetek błędów
  diakrytycznych, bootstrap 95% CI (B=1000 jak u autorów), efekt Δ = różnica średnich z CI. Liczy je
  `summarize.py` → `tables/effects.tex` i kolumna CI w `overall.tex`.
- Wstępne wyniki PL (n=20, CER): Tesseract 0,22, EasyOCR 0,17, PaddleOCR 0,19, TrOCR 0,20.

### Do zrobienia
- Wyniki TrOCR i Qwen 3B na zbiorze polskim, potem pełny zbiór `--n 100`.
- Prezentacja: uzupełnić nazwiska, zweryfikować IF w Clarivate JCR.
- Artykuł: wszystkie `\TODO{}`, przegląd literatury (prace o OCR dla polskiego), opis wyników.
- Repo na GitHubie (kod MIT, dane CC BY 4.0).
