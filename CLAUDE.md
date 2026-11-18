# Polski benchmark OCR

Powtórzenie badania z artykułu bazowego i własne badanie tej samej metodologii dla języka polskiego.

## Artykuł bazowy

Y. Yılmaz, E.G. Hanoğlu, A.G. Özkan, K. Öztoprak, "Benchmarking OCR and vision-language models for
Turkish text recognition: a comprehensive evaluation using synthetic data", IJDAR (Springer), 2026,
DOI 10.1007/s10032-026-00613-6.

- Dane: Zenodo 10.5281/zenodo.21923181 (CC BY 4.0), generator TRDG 1.8.0.
- Kod: https://github.com/OCR-benchmark-project/turkish-synthetic-text-recognition-benchmark
- Kategorie: litery specyficzne vs bez nich, krótkie vs długie słowa (próg ok. 10 znaków), słowo vs
  zdanie, zakłócenia (clean, rotated, noisy, blur, low_resolution). Typy tekstu: printed, handwritten,
  scene.

## Własne badanie

**Tytuł roboczy:** „Ocena silników OCR i modeli wizyjno-językowych w rozpoznawaniu tekstu polskiego na danych
syntetycznych i rzeczywistych”

**Cel:** porównanie skuteczności klasycznych silników OCR i modeli wizyjno-językowych w rozpoznawaniu tekstu
polskiego oraz określenie, jak na błąd wpływają polskie znaki diakrytyczne, długość tekstu, rodzaj pisma
i zniekształcenia obrazu. Polskiego nie porównujemy z tureckim.

**Pytania badawcze:**
1. Który model najlepiej rozpoznaje polski tekst (oba zbiory)?
2. Jak na błąd wpływają polskie znaki, długość, druk / pismo ręczne i zniekształcenia (zbiór syntetyczny)?
3. Czy ranking modeli na danych syntetycznych zgadza się z rankingiem na prawdziwym piśmie ręcznym
   (korelacja Spearmana, jak ρ = 0,92 u autorów)?

### Dane
- Generator TRDG 1.8.0, tylko druk (printed) i pismo ręczne (handwritten), **bez tekstu w scenie**.
  Generator piszemy sami, kod autorów służy jako wzór parametrów (ma bugi).
- Jeden korpus: Wolne Lektury, **sama „Lalka” Prusa, tom I i II** (domena publiczna), słowa filtrowane słownikiem.
- Porównania:
  - z polskimi znakami / bez,
  - krótkie / długie słowa (próg 10 znaków),
  - druk / pismo ręczne,
  - słowo / zdanie (4–8 słów),
  - zniekształcenia: clean, blur, rotated, noisy, low_res (te same słowa, to samo ziarno).
- 22 komórki (11 na rodzaj pisma). Po 100 obrazów na komórkę, łącznie 2200 (`generate_dataset.py --n 100 --seed 42`).
  Zbiór generujemy lokalnie (generator to nie model) i dołączamy do `ocr_bundle.zip`; notebook go nie generuje.
- Fonty z Google Fonts, każdy sprawdzony (`cmap`) na 18 polskich liter (ąćęłńóśźż i wielkie).
  Z 357 fontów odręcznych 272 ma komplet polskich liter i A–Z; po odrzuceniu 104
  niemal identycznych wariantów Playwrite zostaje 168. Lista: `research/fonts_tools/handwriting_fonts_pl.txt`
  (posortowana wg popularności), skrypty `research/fonts_tools/fetch_fonts.py` i `check_fonts.py`.
  W zbiorze używamy 19 najpopularniejszych; Amatic SC wykluczony (same kapitaliki), patrz
  `research/fonts/excluded/`.
  Uwaga: pole `subsets` w metadanych Google Fonts jest niewiarygodne, trzeba sprawdzać `cmap`.
- Wycięte: tekst w scenie (COCO).

### Gold Set: zdjęcia rzeczywiste
- Zbiór PHCD (Polish Handwritten Characters Database, Politechnika Lubelska, https://cs.pollub.pl/phcd/; cytowanie: Tokovarov, Kaczorowska, Miłosz, ASTRJ 14(3), 2020; dokumentacja `documentation.pdf` nazywa się „PHSF Documentation”, a katalog w paczce to `phsf`). Używamy **tylko `phsf/inwokacja/png`**:
  **wszystkie 1968** skanów całych stron z odręcznie przepisaną Inwokacją (szarość, szerokość 2500–5900 px,
  wysokość 640–1680 px, 4 linie). Kopia w `research/gold/images/` (115 MB, poza gitem). Pomijamy `phsf/znaki`
  (pojedyncze znaki 32×32), `ocr_files` i `.npy`. Modelom podajemy skany zmniejszone do 2048 px dłuższego boku
  (`research/prepare_gold.py`), ten sam rozmiar dla wszystkich modeli. Oceniamy wszystkie 1968 skanów;
  przygotowane obrazy i `labels.csv` powstają lokalnie (`prepare_gold.py`) i trafiają do zipa.
- Nazwa pliku: `inwokacja_<nr>_<rok urodzenia>_<K/M>_<kod formularza>.png`. Nazwy bywają nieregularne
  (pełna data, cyrylica w kodzie, spacja), więc metadane z nazw parsujemy ostrożnie.
- Zmienia się tylko charakter pisma, więc różnice w wynikach to różnice między modelami, a nie treścią.
- Zdjęcia przetwarzamy w całości (cała strona), **bez cięcia na linie**.
- **Tekst wzorcowy:** Inwokacja z „Pana Tadeusza” (cztery pierwsze wersy), linie scalone w jeden ciąg, małe litery,
  NFC, bez interpunkcji (patrz Ewaluacja). Na skanach (obejrzane wyrywkowo) tekst z formularza różni się od
  edycji kanonicznej interpunkcją: „Litwo, Ojczyzno moja! Ty jesteś jak zdrowie; / Ile Cię trzeba cenić? Ten tylko
  się dowie: / Kto cię STRACIŁ. Dziś Piękność Twą w całej ozdobie, / Widzę i opisuję - bo tęsknię po tobie.”
  Po normalizacji wzorzec to: „litwo ojczyzno moja ty jesteś jak zdrowie ile cię trzeba cenić ten tylko się dowie
  kto cię stracił dziś piękność twą w całej ozdobie widzę i opisuję bo tęsknię po tobie”. Błędy przepisujących
  zostają.
- Służy do pytań 1 i 3; ranking porównujemy z rankingiem na syntetycznym piśmie ręcznym.

### Modele (7, w Colabie na GPU)
- Z artykułu bazowego (5): Qwen2.5-VL 7B, InternVL3-8B, DeepSeek-VL2-tiny, GOT-OCR2, PaddleOCR. Środowiska i ustawienia
  jak w powtórzeniu (`common/run_models.py`).
- Dodane przez nas (2): Tesseract `pol`, EasyOCR `pl`.
- Pominięte: Phi-3.5-vision i Pixtral-12B (Colab przestał przydzielać A100/H100; Phi policzony tylko dla 833 z 2200 obrazów
  syntetycznych, Pixtral dla całego syntetycznego, ale tylko 200 z 1968 skanów Gold; ich cząstkowych wyników nie
  przechowujemy i nie wchodzą do analizy ani artykułu; oba są w replikacji), TrOCR (checkpoint `trocr-large-printed` rozpoznaje tylko pojedyncze linie angielskiego druku,
  nie obsługuje całych stron), GPT-4o i Claude (komercyjne). Uzasadnienie w artykule: tylko modele otwarte
  dla pełnej odtwarzalności i zerowego kosztu (API są zamknięte, płatne i zmieniają się bez wersjonowania).
- Przy 7 modelach Spearman ma sens, ale próg istotności (dwustronny, 0,05) to ρ ≈ 0,79; przy 5 modelach tylko ρ = 1.

### Ewaluacja
- CER (jiwer) i WER jak w artykule bazowym (WER dla zdań i Gold Setu).
- Badanie własne (oba zbiory): `normalize_text` w `common/metrics.py`: małe litery, NFC, **interpunkcja usunięta po
  obu stronach**, białe znaki do jednej spacji, polskie znaki zostają; CER obcięty do 1,0. Powód: interpunkcja
  przepisujących jest niespójna, a modele zwracają ją losowo (mierzylibyśmy nawyki, nie rozpoznawanie liter);
  autorzy bazowego też liczą liczby z tekstu bez interpunkcji. Replikacja zostaje przy dotychczasowym `normalize`.
- Odsetek błędów na polskich znakach diakrytycznych (oba zbiory).
- Korelacja Spearmana rankingów: CER na zdaniach pisma ręcznego (czyste) ze zbioru syntetycznego vs Gold Set
  (`research/analyze.py`).
- Prompty modeli wizyjno-językowych: prompty autorów z „Turkish” zamienionym na „Polish”.

## Repozytorium

Kod, identyfikatory, komentarze, nazwy plików i kolumny CSV piszemy **po angielsku**; dokumenty
(artykuł, slajdy) po polsku. W kodzie **nie piszemy komentarzy**, a docstring to najwyżej jedna linia opisu modułu;
decyzje, które trzeba zachować, trafiają do tego pliku.

**Nic nie uruchamiamy lokalnie.** Modele, generator i ewaluacja działają tylko w Colabie (notebook jest jedynym
punktem wejścia). Lokalnie najwyżej LaTeX. Brak venvów i `requirements*.txt`: zależności instalują notebooki.
Każdy katalog zawiera tylko to, czego faktycznie używa.

### Struktura
- `common/`: kod wspólny dla obu badań: loadery modeli (`ocr_models.py`), runner (`run_ocr.py`, wznawialny),
  środowiska modeli i uruchamianie na wielu zbiorach (`run_models.py`),
  metryki (`metrics.py`).
- `replication/`: powtórzenie badania bazowego. `replication.ipynb` (Colab, 8 modeli, każdy we własnym środowisku,
  wznawialne, wyniki na Dysku w `MyDrive/ocr-benchmark/replication/`),
  `make_bundle.sh` (buduje `ocr_bundle.zip`, poza gitem), `build_labels.py` (etykiety + próbka; używamy `--n 50` =
  1650 obrazów, większa próbka zawiera mniejszą), `analyze.py`, `authors/cer_wer_calculated.json` (predykcje autorów
  z ich repo), `results/` (`<model>.csv`, `<model>_vs_authors.csv`, `rerun_vs_authors.csv`, `runs.json`, `envs/`
  z wersjami pakietów). Obrazy autorów z Zenodo w `replication/data/syntetic-turkish-dataset/`.
- `research/`: nasze badanie (polskie). `texts/` (korpus), `fonts/` (fonty), `fonts_tools/` (pobieranie i sprawdzanie
  fontów), `generate_dataset.py`, `summarize.py` (tabele LaTeX do `docs/research/article/tables/`), `plot_results.py`
  (wykresy do `docs/research/article/figures/`). `prepare_gold.py` (skalowanie skanów i etykiety),
  `analyze.py` (CER, WER, błędy na znakach diakrytycznych, ranking, Spearman), `make_bundle.sh` (buduje `ocr_bundle.zip` z kodem i gotowymi zbiorami,
  poza gitem), `research.ipynb` (Colab, jedyny punkt wejścia). `summarize.py` (tabele `overall.tex`, `gold.tex`) i `plot_results.py` (wykresy `conditions`, `ranking`) czytają wyniki `analyze.py`.
  Wygenerowane obrazy i skany nie są w repo (`research/data/`, `research/gold/`); predykcje i podsumowania z Colaba są w `research/results/`.
- `docs/replication/`: dokumenty do powtórzenia badania bazowego. `presentation/`: `presentation.tex` (prezentacja
  artykułu bazowego, 8 slajdów, bez naszej replikacji), `speaker_notes.md`. `article/`: PDF artykułu bazowego (poza gitem).
- `docs/research/`: dokumenty do naszego badania. `article/`: `main.tex` (szkielet LNCS po polsku z `\TODO{}`),
  `references.bib`, `tables/*.tex` (generuje `summarize.py`, nie edytować ręcznie), `figures/`. `presentation/`:
  `presentation.tex` (Lab 5, 8 slajdów, do 5 minut), `speaker_notes.md` (z odpowiedziami na pytania), wykresy
  `model_ranking.pdf`, `conditions_heatmap.pdf`, `examples.pdf` i `phcd_scan.png`. Wykresy zrobione poza repo
  (szkic kolegi), liczby z `research/results/analysis/`; odsetek błędnych odpowiedzi różnych od wzorca tylko
  diakrytykami (26–33% dla VLM i PaddleOCR, 3% Tesseract) liczony osobno, nie przez `analyze.py`.

### Uruchamianie
- Replikacja: `python replication/build_labels.py --n 50`, `replication/make_bundle.sh`, `ocr_bundle.zip` na
  `MyDrive/ocr-benchmark/`, potem `replication/replication.ipynb` w Colabie (A100).
- Nasze badanie: `research/make_bundle.sh`, `ocr_bundle.zip` na `MyDrive/ocr-benchmark/`, potem `research/research.ipynb`
  w Colabie (A100). Notebook uruchamia 7 modeli (`common/run_models.py`) na obu zbiorach i liczy wyniki.
- LaTeX: `cd docs/research/article && latexmk -pdf main.tex` (analogicznie `docs/replication/presentation` i `docs/research/presentation`, `presentation.tex`).

### Ustalenia techniczne
- **CER w kodzie autorów** (`cer_wer_calculation.py`, zamienione argumenty) dzieli odległość przez długość
  *predykcji*; tak liczone są wszystkie 65 036 wartości `cer` w ich JSON-ie (bez małych liter). Liczby
  z tekstu artykułu odtwarza jednak inny wariant z ich repo (`graphs_lower_trocr.py`): małe litery,
  **bez spacji i interpunkcji**, /długość prawdy; artykuł tego nie opisuje. Kolumna `nospace` w
  `replication/results/`: TrOCR 0,380 vs 0,38; GPT-4o turkish 0,065 vs 0,065, clean 0,017 vs 0,017.
  Nieodtworzone: GPT-4o non_turkish 0,066 vs 0,055, Paddle clean 0,260 vs 0,239. W tym wariancie TrOCR
  jest ostatni (0,380), a GOT-OCR2, który gubi spacje, ma 0,311 (poprawny CER 0,391, czyli ostatni).
- **Claude:** JSON autorów zawiera Claude 3.7 Sonnet (CER 0,349), artykuł podaje Sonnet 4 z CER 0,197.
- **Ponowny przebieg 8 otwartych modeli** (Colab A100, 1650 obrazów = 50 na każdą z 33 komórek,
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
- **Opcje loaderów:** `--option` trafia tylko do loaderów, które ją przyjmują (`max_new_tokens=512` dla Qwena; replikacja
  używa 128 jak autorzy). `temperature=0` dotyczyło tylko Pixtrala (usunięty z badania własnego).
- **TrOCR:** checkpoint ma `use_cache=False` (2,5× wolniej na CPU, włączamy cache: wynik identyczny);
  `max_length` domyślne 21 tokenów jak u autorów, więc dłuższe zdania są ucinane (u autorów też).
  Transformers 5 tworzy model na urządzeniu `meta` i nie wypełnia tabeli pozycji, dlatego `trocr()` liczy ją od nowa.
- **Generator:** TRDG 1.8.0 woła `getsize()` usunięte z Pillow 10, więc podmieniamy `get_text_height` jak autorzy.
- **Tesseract:** `--psm 7` dla obrazów niższych niż 200 px (jedna linia, zbiór syntetyczny), `--psm 6` dla stron Gold Setu.
- **PaddleOCR `pl`** używa wspólnego słownika łacińskiego (`latin_dict.txt`) bez ń, ś, ź, ż: nie może ich
  zwrócić („ludnošci”, „5piacy”). Przebieg z `en` (ustawienie autorów) dawał to samo (CER 0,18 vs 0,19), więc go usunęliśmy;
  w artykule jest tylko PaddleOCR `pl`, podpisywany po prostu „PaddleOCR”.
- Tekstury papieru autorów nie są opublikowane; renderujemy na białym tle.
- **Obliczenia w artykule** (sekcje 3.3–3.4): wzory (1)–(5) — CER/WER, średnia, odsetek błędów
  diakrytycznych, bootstrap 95% CI (B=1000 jak u autorów), efekt Δ = różnica średnich z CI. Liczy je
  `summarize.py` → `summary/effects.csv` i kolumna CI w `tables/overall.tex`.

### Do zrobienia
- Artykuł (`main.tex`, ok. 5,4 strony treści): autorzy i uczelnia (`\TODO{}`), dopracowanie przeglądu literatury o OCR dla polskiego, sprawdzenie wyniku GOT-OCR2 na skanach (0,795) na surowych predykcjach.
- Prezentacja naszego badania (`docs/research/presentation/`): potwierdzić datę Lab 5 (22.11).
