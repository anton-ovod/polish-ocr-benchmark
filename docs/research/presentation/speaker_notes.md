# Notatki do wystąpienia na Lab 5

Około 570 słów, czyli 4,5-5 minut przy spokojnym tempie. Liczby są te same co w artykule (`research/results/`, `docs/research/article/tables/overall.tex`). Przykład ze slajdu 7 to skan `images/inwokacja_0000.png` i odpowiedzi modeli z `research/results/gold/*.csv`. Dwóch liczb z odpowiedzi na pytania nie ma w artykule (ρ = 0,82 i odsetki niepełnych odczytów skanów), policzono je osobno z tych samych plików.

## Slajd 1. Tytuł (10 s)

Dzień dobry. Chcielibyśmy przedstawić nasz artykuł o tym, jak silniki OCR i modele wizyjno-językowe radzą sobie z tekstem polskim, na obrazach syntetycznych i na prawdziwym piśmie odręcznym.

## Slajd 2. Motywacja i cel pracy (40 s)

Modele wizyjno-językowe są uczone głównie na tekstach angielskich i chińskich, więc nie wiadomo, jak dobrze radzą sobie z językami, które mają własne litery. W języku polskim jest ich dziewięć, a od zwykłych liter łacińskich różni je tylko ogonek, kreska albo kropka, więc łatwo o pomyłkę. Badanie dla języka tureckiego pokazało, że właśnie takie litery są jednym z głównych źródeł błędów. Dla polskiego nie znaleźliśmy porównania, które obejmowałoby zarówno modele wizyjno-językowe, jak i klasyczne silniki OCR. Dlatego postawiliśmy trzy pytania: które narzędzie czyta polski tekst najlepiej, od czego zależy błąd i czy ranking ustalony na tanich danych syntetycznych powtórzy się na prawdziwym piśmie.

## Slajd 3. Materiał badawczy (40 s)

Mamy dwa zbiory. Pierwszy wygenerowaliśmy sami w bibliotece TRDG ze słów i zdań z „Lalki”: 2200 obrazów. Na rysunku górny wiersz to druk, a dolny pismo odręczne. Po lewej stronie widać słowo z polskimi znakami i długie słowo, dalej to samo słowo w pięciu wersjach: czystej, rozmytej, obróconej, z szumem i w niskiej rozdzielczości. Każda grupa różni się więc od innych tylko jedną cechą. Drugi zbiór to 1968 skanów z bazy PHCD Politechniki Lubelskiej, taki jak ten pod spodem. Na każdym jest ten sam początek inwokacji, więc skany różnią się przede wszystkim charakterem pisma.

## Slajd 4. Metody badawcze (40 s)

Porównaliśmy siedem otwartych narzędzi: trzy uniwersalne modele wizyjno-językowe, GOT-OCR2, który służy tylko do odczytu tekstu, i trzy klasyczne silniki z modelem języka polskiego. W planie były jeszcze Phi-3.5-vision i Pixtral, ale bez karty A100 nie dało się ich policzyć do końca. Główna miara to CER, czyli liczba poprawek potrzebnych, żeby z odpowiedzi modelu zrobić wzorzec, podzielona przez długość wzorca. Wcześniej zamieniamy tekst na małe litery i usuwamy interpunkcję, bo osoby przepisujące stawiały ją różnie. Osobno liczymy, jak często model pomylił tylko znak diakrytyczny.

## Slajd 5. Wyniki: zbiór syntetyczny (45 s)

Na obrazach syntetycznych wygrywa Qwen2.5-VL: błąd 0,059, ponad dwa razy mniejszy niż u kolejnych modeli. Mapa pokazuje błąd w każdej grupie. Pismo odręczne jest trudniejsze od druku dla wszystkich, a najbardziej szkodzi niska rozdzielczość. Polskie znaki podnoszą błąd prawie wszystkim, najmniej Tesseractowi i EasyOCR. U modeli wizyjno-językowych i PaddleOCR od jednej czwartej do jednej trzeciej błędnych odpowiedzi różni się od wzorca tylko ogonkiem albo kreską: słowo jest odczytane dobrze, brakuje tylko polskiej litery.

## Slajd 6. Wyniki: skany PHCD (40 s)

Teraz prawdziwe pismo. Niebieskie słupki to syntetyczne zdania pisane odręcznie, pomarańczowe to skany. Kolejność modeli jest prawie taka sama, korelacja Spearmana wynosi 0,89. Zamieniły się tylko trzy klasyczne silniki ze środka stawki. Poziom błędu jest za to zupełnie inny: na skanach każde narzędzie myli się co najmniej dwa razy częściej.

## Slajd 7. Przykład odczytu skanu PHCD (35 s)

Tak to wygląda na jednym skanie. Qwen pomylił się w dwóch słowach drugiego wersu: zamiast „Ile Cię trzeba cenić” przeczytał „Je Cię trzeba ocalić”. DeepSeek zgubił ogonki, a GOT-OCR2 z całej strony zwrócił kilka liter. Na tym jednym skanie kolejność wszystkich siedmiu narzędzi jest taka sama jak średnio na całym zbiorze.

## Slajd 8. Wnioski (45 s)

Najlepiej polski tekst czyta Qwen2.5-VL, na obu zbiorach. Polskie znaki i niska rozdzielczość szkodzą prawie wszystkim narzędziom, a klasycznym silnikom najbardziej pismo odręczne i zniekształcenia. Ranking z danych syntetycznych powtarza się na prawdziwym piśmie, więc takie dane wystarczą do wstępnego wyboru modelu, ale nie powiedzą, jaki będzie błąd. Nowe jest to, że dla polskiego porównujemy naraz modele wizyjno-językowe i klasyczne silniki, na kontrolowanym zbiorze i na prawdziwych rękopisach, i osobno liczymy pomyłki w diakrytykach. Kod, generator i odpowiedzi modeli są na GitHubie. Dziękujemy.

## Na pytania

- **Dlaczego siedem narzędzi, a w planie było dziewięć?** Phi-3.5-vision i Pixtral potrzebowały karty A100, której Colab przestał przydzielać. Phi policzono dla 833 z 2200 obrazów, Pixtrala dla całego zbioru syntetycznego i 200 skanów; niepełnych wyników nie używamy.
- **Dlaczego PaddleOCR nie zwraca ń, ś, ź, ż?** Użyta wersja 2.9.1 ma dla języka polskiego wspólny słownik liter łacińskich bez tych znaków. PaddleOCR 3.x ma już cały polski alfabet.
- **Dlaczego bez interpunkcji?** Osoby przepisujące stawiały ją niespójnie, a modele dodają ją przypadkowo, więc liczylibyśmy nawyki, a nie odczytane litery. Polskie znaki zostają bez zmian.
- **Czy wynik korelacji zależy od tego, że wzięliśmy same zdania?** Dla całego syntetycznego pisma odręcznego ρ wynosi 0,82, nadal powyżej progu istotności dla siedmiu modeli (około 0,79).
- **Czy modele nie znały inwokacji na pamięć?** Mogły ją widzieć podczas trenowania, to jedno z ograniczeń opisanych w artykule. Dlatego obok skanów jest zbiór syntetyczny z tekstem z „Lalki”.
- **Dlaczego GOT-OCR2 jest ostatni?** Według autorów obsługuje głównie angielski i chiński. Na skanach w 67% przypadków zwraca mniej niż połowę tekstu (PaddleOCR w 46%), więc duża część jego błędu to niedokończony odczyt.
- **Jakie wyniki miały narzędzia, których nie ma w tabeli na slajdzie 7?** CER tego skanu: Tesseract 0,66, EasyOCR 0,67, PaddleOCR 0,86.
- **Ile trwały obliczenia?** Siedem narzędzi na obu zbiorach około 7,3 godziny na A100. Qwen2.5-VL potrzebuje 0,25 s na obraz syntetyczny i 3,4 s na skan.
- **Skąd skany i czy są w repozytorium?** Z publicznej bazy PHCD Politechniki Lubelskiej (Tokovarov i in., 2020). W repozytorium są tylko odpowiedzi modeli, skany pobiera się ze strony bazy.
- **Czy sprawdzaliście wyniki z artykułu Yılmaza?** Tak, osobno, poza artykułem: osiem otwartych modeli na 1650 obrazach tureckich dało średni CER różny od odpowiedzi autorów najwyżej o 0,001 (Pixtral o 0,007).
