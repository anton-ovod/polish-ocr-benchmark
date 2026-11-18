# Notatki do wystąpienia na Lab 5

Około 500 słów, czyli 4 minuty przy tempie 120-130 słów na minutę; reszta z 5 minut zostaje na przejścia między slajdami i pokazywanie wykresów. Liczby pochodzą z `research/results/analysis/` (commit 9708a83).

## Slajd 1. Tytuł (10 s)

Przedstawiamy nasz artykuł: ocenę silników OCR i modeli wizyjno-językowych w rozpoznawaniu tekstu polskiego. Punktem wyjścia jest artykuł z IJDAR, który omawialiśmy na poprzednich zajęciach.

## Slajd 2. Cel i pytania (40 s)

Modele wizyjno-językowe i silniki OCR uczy się głównie na tekstach angielskich. Polski ma dziewięć liter z diakrytykami, które od liter łacińskich różni tylko ogonek, kreska albo kropka. Autorzy artykułu bazowego pokazali dla tureckiego, że takie litery są głównym źródłem błędów. My powtarzamy ich protokół dla polskiego. Chcemy wiedzieć, który system najlepiej czyta polski tekst, co najbardziej zwiększa błąd i czy kolejność modeli na danych syntetycznych zgadza się z kolejnością na prawdziwym piśmie.

## Slajd 3. Materiał (45 s)

Mamy dwa zbiory. Pierwszy to 2200 obrazów syntetycznych z „Lalki” Prusa, wygenerowanych tym samym narzędziem co u autorów, czyli TRDG. Każdy font sprawdziliśmy, czy ma wszystkie polskie litery. Kategorie są jak w artykule bazowym: słowa z polskimi znakami i bez nich, krótkie i długie, pojedyncze słowo i zdanie oraz pięć zniekształceń tego samego słowa. Na dole widać przykłady. Drugi zbiór to 1968 skanów z bazy PHCD Politechniki Lubelskiej: różne osoby przepisały odręcznie początek Inwokacji. Tekst jest wszędzie ten sam, zmienia się tylko charakter pisma.

## Slajd 4. Metody (40 s)

Badamy siedem otwartych modeli bez douczania: trzy modele wizyjno-językowe, GOT-OCR2 i trzy silniki klasyczne. Wszystko liczyliśmy w Colabie na A100, każdy model we własnym środowisku. Modele językowe dostają polecenie autorów, tylko z językiem polskim zamiast tureckiego. Główna miara to CER, liczony po zamianie na małe litery i usunięciu interpunkcji. Dodatkowo liczymy WER i odsetek odpowiedzi, które różnią się od wzorca tylko diakrytykami. Przedziały ufności liczymy bootstrapem, a zgodność rankingów korelacją Spearmana.

## Slajd 5. Porównanie modeli (45 s)

Najlepszy na obu zbiorach jest Qwen2.5-VL: błąd znakowy około 6% na danych syntetycznych i 10% na skanach. Na czystym druku klasyczne Tesseract i EasyOCR są prawie bezbłędne, ale pismo odręczne podnosi błąd wszystkim modelom. Skany są wyraźnie trudniejsze niż obrazy syntetyczne. U modeli wizyjno-językowych mniej więcej co trzecia błędna odpowiedź różni się od wzorca tylko diakrytykami, a u Tesseracta tylko 3%.

## Slajd 6. Co utrudnia odczyt (45 s)

Mapa pokazuje błąd w każdej kategorii. Polskie znaki szkodzą modelom wizyjno-językowym, GOT-OCR2 i PaddleOCR, który w wersji 2.9.1 nie ma w słowniku liter ń, ś, ź, ż. Tesseract i EasyOCR, które mają model języka polskiego, prawie na nich nie tracą. Najtrudniejsza dla wszystkich jest niska rozdzielczość. Szum psuje przede wszystkim Tesseract, a rozmycie EasyOCR.

## Slajd 7. Dane syntetyczne a prawdziwe pismo (40 s)

Porównujemy błąd na syntetycznych zdaniach pisanych odręcznie z błędem na skanach. Korelacja Spearmana wynosi 0,89 i jest istotna. Trzy pierwsze miejsca i ostatnie są takie same, zamieniają się tylko trzy silniki klasyczne. Dane syntetyczne przewidują więc kolejność modeli, ale nie poziom błędu. GOT-OCR2 i PaddleOCR często przerywają odczyt w połowie strony, co tłumaczy ich wysoki błąd na skanach.

## Slajd 8. Wnioski i wkład własny (40 s)

Podsumowując: Qwen2.5-VL czyta polski tekst najdokładniej, polskie znaki szkodzą modelom wizyjno-językowym, a tanie dane syntetyczne dobrze przewidują kolejność modeli na prawdziwym piśmie. Nowe w naszej pracy jest przeniesienie protokołu na polski, dodanie silników z modelem polskim, ocena na skanach z PHCD i analiza błędów diakrytycznych. Powtórzyliśmy też badanie bazowe: siedem z ośmiu modeli autorów dało ten sam średni błąd z dokładnością do 0,001, a Pixtral do 0,007. Kod i odpowiedzi modeli są na GitHubie.

## Na pytania

- **Dlaczego 7 modeli, a nie 9 z planu?** Phi-3.5-vision i Pixtral-12B nie zostały policzone, bo Colab przestał przydzielać A100. Phi policzono dla 833 z 2200 obrazów, Pixtrala dla całego zbioru syntetycznego i 200 skanów; tych cząstkowych wyników nie używamy.
- **Dlaczego stary PaddleOCR 2.9.1?** Tej wersji używali autorzy artykułu bazowego. PaddleOCR 3.x ma w modelu polskim wszystkie 18 polskich liter.
- **Dlaczego bez TrOCR?** Model `trocr-large-printed` czyta tylko pojedyncze linie angielskiego druku, a nie całe strony.
- **Czym różni się miara od autorów?** Obie zamieniają tekst na małe litery i usuwają interpunkcję. Autorzy usuwali też spacje, my je zostawiamy, więc sklejone słowa liczą się jako błąd. CER jest obcięty do 1, a pusta odpowiedź liczy się jako 1.
- **Czy korelacja zależy od wyboru zdań?** Dla całego syntetycznego pisma odręcznego, a nie tylko zdań, wynosi 0,82, nadal powyżej progu istotności (około 0,79 dla 7 modeli).
- **Co ze skanami?** 1968 skanów z katalogu `phsf/inwokacja` bazy PHCD (Tokovarov, Kaczorowska, Miłosz, ASTRJ 2020). Wzorcem jest tekst z formularza po usunięciu interpunkcji (168 znaków). Pomyłki osób przepisujących zostają w danych. Skany zmniejszamy do 2048 pikseli dłuższego boku.
- **GOT-OCR2 na skanach:** w 67% przypadków zwraca mniej niż połowę tekstu (mediana 28 ze 168 znaków), PaddleOCR w 46%, DeepSeek-VL2 w 15%, pozostałe w najwyżej 1%.
- **Powtórzenie badania bazowego:** 8 otwartych modeli na 1650 obrazach tureckich (50 z każdej z 33 komórek). Średni CER różni się od odpowiedzi autorów najwyżej o 0,001, u Pixtrala o 0,007. Pixtral daje inne pojedyncze odpowiedzi (28% takich samych), prawdopodobnie dlatego, że losuje tekst bez ustalonego ziarna; tego nie sprawdzono drugim przebiegiem.
- **Czas obliczeń:** 7 modeli na obu zbiorach zajęło około 7,3 godziny na A100; Qwen2.5-VL potrzebuje 0,25 s na obraz syntetyczny i 3,4 s na skan.
- **Dostęp do danych:** kod i odpowiedzi modeli dla każdego obrazu są na GitHubie (MIT). Zbiór syntetyczny (11 MB) można odtworzyć z generatora i ziarna 42, archiwum obrazów trzeba jeszcze opublikować. Skany pobiera się ze strony PHCD.
