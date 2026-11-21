# Notatki do wystąpienia na Lab 5

Około 630 słów, czyli nieco ponad 5 minut przy tempie dwóch słów na sekundę. Jeśli zabraknie czasu, na slajdzie 8 można pominąć ograniczenia, bo są na slajdzie. Liczby są te same co w artykule (`research/results/`, `docs/research/article/tables/overall.tex`). Przykład ze slajdu 7 to skan `images/inwokacja_0000.png` i odpowiedzi modeli z `research/results/gold/*.csv`. W odpowiedziach na pytania są też liczby spoza artykułu: ρ = 0,82 i odsetki niepełnych odczytów (policzone z tych samych plików), czasy z `research/results/runs.json`, liczby obrazów Phi i Pixtrala z `CLAUDE.md`, wersja PaddleOCR z `common/run_models.py` i wyniki powtórzenia z `replication/results/`.

## Slajd 1. Tytuł (15 s)

Dzień dobry. Chcielibyśmy przedstawić nasz artykuł o tym, jak silniki OCR i modele wizyjno-językowe radzą sobie z tekstem polskim, na obrazach syntetycznych i na prawdziwym piśmie odręcznym.

## Slajd 2. Motywacja i cel pracy (50 s)

Modele wizyjno-językowe, w skrócie VLM, uczy się głównie na tekstach angielskich i chińskich. Tymczasem polski alfabet ma dziewięć liter diakrytycznych, które od zwykłych liter łacińskich różni tylko ogonek, kreska albo kropka, więc łatwo o pomyłkę. Badanie dla tureckiego pokazało, że właśnie takie litery są jednym z głównych źródeł błędów, a dla polskiego nie znaleźliśmy porównania VLM z klasycznymi silnikami OCR. Dlatego chcieliśmy sprawdzić, jak dokładnie oba rodzaje narzędzi czytają polski tekst i czy wyniki z tanich danych syntetycznych przenoszą się na prawdziwe pismo. Stąd trzy pytania: które narzędzie jest najdokładniejsze, co zwiększa błąd i czy ranking z danych syntetycznych powtórzy się na skanach rękopisów.

## Slajd 3. Materiał: zbiór syntetyczny i skany (50 s)

Mamy dwa zbiory. Pierwszy wygenerowaliśmy sami w bibliotece TRDG ze słów i zdań z „Lalki”: druk i pismo odręczne, w każdym 11 podkategorii po 100 obrazów, razem 2200. Podkategorie wymienia tabela po prawej, a rysunek pokazuje to samo słowo w wersji czystej, rozmytej, obróconej, z szumem i w niskiej rozdzielczości. Dzięki temu porównujemy grupy, które różnią się tylko jedną cechą. Drugi zbiór to 1968 skanów z bazy PHCD Politechniki Lubelskiej, taki jak ten pod spodem. Na każdym jest ten sam początek inwokacji, więc skany różnią się przede wszystkim charakterem pisma.

## Slajd 4. Metody: narzędzia i miary błędu (40 s)

Porównaliśmy siedem otwartych narzędzi bez douczania: trzy uniwersalne modele wizyjno-językowe, GOT-OCR2, który służy tylko do odczytu tekstu, i trzy klasyczne silniki z modelem języka polskiego. Modele wizyjno-językowe dostały polecenie, żeby przepisać polski tekst z obrazu dokładnie tak, jak wygląda. Główna miara to CER, czyli liczba poprawek potrzebnych, żeby z odpowiedzi modelu zrobić wzorzec, podzielona przez długość wzorca: 0,1 to mniej więcej jeden zły znak na dziesięć. Wcześniej zamieniamy tekst na małe litery i usuwamy interpunkcję, bo osoby przepisujące stawiały ją różnie. Osobno liczymy, jak często model pomylił tylko znak diakrytyczny.

## Slajd 5. Wyniki: czynniki utrudniające odczyt (55 s)

Na obrazach syntetycznych wygrywa Qwen2.5-VL: błąd 0,059, ponad dwa razy mniejszy niż u kolejnych modeli. Mapa pokazuje błąd w każdej grupie. Pismo odręczne jest trudniejsze od druku dla wszystkich, a najbardziej szkodzi niska rozdzielczość. Część narzędzi lepiej czyta długie słowa i całe zdania, bo dłuższy kontekst pomaga uzupełnić niepewne litery. Polskie znaki podnoszą błąd prawie wszystkim, najmniej Tesseractowi i EasyOCR. U modeli wizyjno-językowych i PaddleOCR od jednej czwartej do jednej trzeciej błędnych odpowiedzi różni się od wzorca tylko ogonkiem, kreską albo kropką, czyli słowo jest odczytane dobrze. W PaddleOCR wynika to ze słownika: model języka polskiego nie ma liter ń, ś, ź i ż, więc pisze na przykład „ludnošci” zamiast „ludności”.

## Slajd 6. Wyniki: ranking narzędzi i walidacja na skanach (25 s)

Teraz prawdziwe pismo. Niebieskie słupki to syntetyczne zdania pisane odręcznie, pomarańczowe to skany. Kolejność modeli jest prawie taka sama, korelacja Spearmana wynosi 0,89. Zamieniły się tylko trzy klasyczne silniki ze środka stawki. Poziom błędu jest za to zupełnie inny: na skanach każde narzędzie myli się co najmniej dwa razy częściej.

## Slajd 7. Przykład odczytu skanu PHCD (30 s)

Tak to wygląda na jednym skanie. Qwen pomylił się w dwóch słowach drugiego wersu: zamiast „Ile Cię trzeba cenić” przeczytał „Je Cię trzeba ocalić”. DeepSeek zgubił ogonki i przekręcił większość słów, a GOT-OCR2 z całej strony zwrócił kilka liter. Każde z siedmiu narzędzi zajmuje tu to samo miejsce co w rankingu na całym zbiorze skanów.

## Slajd 8. Wnioski (40 s)

Najlepiej polski tekst czyta Qwen2.5-VL, na obu zbiorach. Polskie znaki i niska rozdzielczość szkodzą prawie wszystkim narzędziom, a klasycznym silnikom najbardziej pismo odręczne i zniekształcenia. Ranking z danych syntetycznych powtarza się na prawdziwym piśmie, więc takie dane wystarczą do wstępnego wyboru modelu, ale nie powiedzą, jaki będzie błąd. Nowością jest porównanie VLM z klasycznymi silnikami dla polskiego, na kontrolowanym zbiorze i na prawdziwych rękopisach, oraz osobne liczenie pomyłek diakrytycznych. Badanie ma też ograniczenia: obrazy syntetyczne to jedna linia na białym tle, skany zawsze zawierają ten sam znany tekst, a przy siedmiu narzędziach korelacja jest istotna dopiero od 0,79. Dziękujemy za uwagę.

## Na pytania

### Dlaczego siedem narzędzi, a w planie było dziewięć?

Phi-3.5-vision i Pixtral potrzebowały karty A100, której Colab przestał przydzielać. Phi policzono dla 833 z 2200 obrazów, Pixtrala dla całego zbioru syntetycznego i 200 skanów; niepełnych wyników nie używamy.

### Jak duże były modele?

Qwen2.5-VL ma 7 mld parametrów, InternVL3 8 mld, a DeepSeek-VL2 był w wersji tiny (1 mld aktywnych). Większych i zamkniętych modeli nie badaliśmy, to ograniczenie opisane w artykule.

### Czy wszystkie modele wizyjno-językowe dostały to samo polecenie?

Qwen2.5-VL i InternVL3 dostały pełne polecenie z badania dla tureckiego, ze słowem „Turkish” zamienionym na „Polish”. DeepSeek-VL2 dostał krótszą wersję „Extract the Polish text exactly” w formacie, którego wymaga ten model.

### Dlaczego PaddleOCR nie zwraca ń, ś, ź, ż?

Użyta wersja 2.9.1 ma dla języka polskiego wspólny słownik liter łacińskich bez tych znaków. PaddleOCR 3.x ma już cały polski alfabet.

### Dlaczego bez interpunkcji?

Osoby przepisujące stawiały ją niespójnie, a modele dodają ją przypadkowo, więc liczylibyśmy nawyki, a nie odczytane litery. Polskie znaki zostają bez zmian.

### Dlaczego CER jest obcięty do 1?

Gdy model dopisze dużo tekstu, CER jednego obrazu może przekroczyć 1. Po obcięciu taki obraz liczy się najwyżej jak całkowicie błędny odczyt i nie zawyża średniej.

### Dlaczego na skanach błąd jest tak wysoki?

Skany to prawdziwe, zróżnicowane pismo, a modele dostają całą stronę z czterema wersami, bez dzielenia na linie. Obrazy syntetyczne mają jedną linię tekstu na białym tle. Do tego wzorcem jest oryginalny tekst inwokacji, więc gdy osoba przepisująca się pomyliła, nawet wierny odczyt liczy się jako błąd.

### Czy wynik korelacji zależy od tego, że wzięliśmy same zdania?

Dla całego syntetycznego pisma odręcznego ρ wynosi 0,82, nadal powyżej progu istotności dla siedmiu modeli (około 0,79).

### Czy modele nie znały inwokacji na pamięć?

Mogły ją widzieć podczas trenowania, to jedno z ograniczeń opisanych w artykule. Dlatego obok skanów jest zbiór syntetyczny z tekstem z „Lalki”.

### Dlaczego GOT-OCR2 nie jest klasycznym silnikiem OCR?

Klasyczne silniki najpierw wykrywają tekst, a potem rozpoznają znaki, i nie mają modelu językowego. GOT-OCR2 jest zbudowany jak model wizyjno-językowy (koder obrazu i dekoder, który generuje tekst), ale uczono go wyłącznie odczytu tekstu, dlatego stoi w osobnej grupie.

### Dlaczego GOT-OCR2 jest ostatni?

Według autorów obsługuje głównie angielski i chiński. Na skanach w 67% przypadków zwraca mniej niż połowę tekstu (PaddleOCR w 46%), więc duża część jego błędu to niedokończony odczyt.

### Jakie wyniki miały narzędzia, których nie ma w tabeli na slajdzie 7?

CER tego skanu: Tesseract 0,66, EasyOCR 0,67, PaddleOCR 0,86.

### Ile trwały obliczenia?

Siedem narzędzi na obu zbiorach około 7,3 godziny na A100. Qwen2.5-VL potrzebuje 0,25 s na obraz syntetyczny i 3,4 s na skan.

### Skąd skany i czy są w repozytorium?

Z publicznej bazy PHCD Politechniki Lubelskiej (Tokovarov i in., 2020). W repozytorium są tylko odpowiedzi modeli, skany pobiera się ze strony bazy.

### Czy sprawdzaliście wyniki z artykułu Yılmaza?

Tak, osobno, poza artykułem. Uruchomiliśmy ponownie osiem otwartych modeli na 1650 obrazach tureckich: u siedmiu średni CER różnił się od policzonego na odpowiedziach autorów najwyżej o 0,001, u Pixtrala o 0,007.
