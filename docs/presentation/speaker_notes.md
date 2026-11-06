## Slajd 2: Czasopismo, wydawca i autorzy (20 s)

Artykuł ukazał się w tym roku w IJDAR, czasopiśmie Springera o analizie i rozpoznawaniu dokumentów. Ma Impact Factor 1,7 i 100 punktów na liście ministerialnej. To praca badawcza czterech autorów z Konya Food and Agriculture University: dwóch młodszych badaczy i dwóch opiekunów projektu.

## Slajd 3: Cel artykułu i pytania badawcze (30 s)

Autorzy chcą sprawdzić, jak dobrze klasyczny OCR i modele wizyjno-językowe czytają tekst turecki i czy wnioski z obrazów generowanych przenoszą się na prawdziwe zdjęcia. Pytają o cztery rzeczy: czy przeszkadzają litery typowe dla tureckiego, czy długie słowa są trudniejsze, czy pomaga kontekst zdania oraz jak działają zniekształcenia i różne rodzaje tekstu.

## Slajd 4: Materiał: zbiór syntetyczny i zdjęcia (40 s)

Teksty pochodzą z dwóch źródeł: z _Nutuka_, czyli słynnego przemówienia Atatürka z 1927 roku, i z tureckiej Wikipedii, po 6600 obrazów z każdego. Do tego dochodzi 90 prawdziwych zdjęć do sprawdzenia wyników. Obrazy są w trzech odmianach: druk, pismo odręczne i napis w scenie. Każda odmiana ma 11 podkategorii po 200 obrazów: z literami tureckimi i bez, krótkie i długie słowa, słowa i zdania oraz pięć rodzajów zniekształceń.

**Przykłady na dole:** najpierw trzy rodzaje tekstu, potem to samo słowo z różnymi zniekształceniami, a na końcu prawdziwe zdjęcie.

## Slajd 5: Metody: modele i miary błędu (35 s)

Porównano dziesięć modeli bez douczania: trzy klasyczne silniki OCR, pięć otwartych modeli wizyjno-językowych i dwa komercyjne. Każdy przeczytał cały zbiór, a modele językowe dostały to samo polecenie: przepisz tekst dokładnie tak, jak jest na obrazku.

Główna miara to CER, czyli jaka część znaków jest błędna: 0,1 to mniej więcej jeden błąd na dziesięć znaków. Dla zdań liczono też WER, czyli to samo na poziomie słów. Do tego przedziały ufności i korelacja Spearmana, która mówi, czy ranking modeli na zdjęciach zgadza się z rankingiem na danych syntetycznych.

## Slajd 6: Wyniki: ranking modeli i walidacja na zdjęciach (40 s)

**Wykres:** niebieski pasek to błąd na danych syntetycznych, pomarańczowy na zdjęciach; im krótszy, tym lepiej. Modele są ułożone od najlepszego.

Prowadzą GPT-4o i otwarty Qwen, więc model otwarty jest praktycznie na poziomie komercyjnego. Claude jest dopiero piąty na danych syntetycznych, ale na zdjęciach awansuje na trzecie miejsce. TrOCR zamyka stawkę w obu zbiorach. Najważniejsze: ranking na zdjęciach prawie pokrywa się z rankingiem na danych syntetycznych, korelacja wynosi 0,92. Na Wikipedii błędy są tylko trochę większe.

## Slajd 7: Wyniki: czynniki utrudniające odczyt (45 s)

**Wykres:** wiersze to modele, kolumny to warunki, a w komórkach jest błąd: im ciemniej, tym gorzej. Ostatni wiersz mówi, u ilu modeli na dziesięć widać dany efekt.

Litery tureckie podnoszą błąd prawie u wszystkich. Najlepsze modele odczytują poprawnie 70–90% tych liter, a TrOCR i PaddleOCR prawie żadnej; najczęściej mylone są ı oraz İ. Najtrudniejsze są pismo odręczne i niska rozdzielczość. Wbrew oczekiwaniom długie słowa nie są trudniejsze, a całe zdanie zamiast pojedynczego słowa pomaga siedmiu modelom na dziesięć. W zdaniach GPT-4o i Qwen mylą mniej więcej co dziewiąte słowo, a GOT-OCR i TrOCR prawie każde.

## Slajd 8: Wkład autorów i elementy nowości (35 s)

Autorzy wnoszą dwie rzeczy: publiczny zbiór obrazów i zdjęć oraz porównanie dziesięciu modeli w tych samych warunkach. Nowe jest to, że dla tureckiego po raz pierwszy zestawiono modele wizyjno-językowe z klasycznym OCR, każdy czynnik zbadano osobno, błędy rozbito na poszczególne litery tureckie, a wyniki potwierdzono na prawdziwych zdjęciach.

Słabsze strony to pismo odręczne z czcionek, brak dostrajania modeli i mało zdjęć. Dane i kod są publiczne. Osiem otwartych modeli uruchomiliśmy ponownie i dostaliśmy praktycznie te same wyniki co autorzy.

Dziękujemy.

---

## Gdyby padły pytania (Q&A)

### Metodyka i zbiór danych

- **Dlaczego dane syntetyczne, a nie prawdziwe dokumenty?** Dla tureckiego nie było publicznego zbioru z kontrolowanymi zniekształceniami i długościami. Generator pozwala zmieniać jeden czynnik naraz, a korelacja 0,92 ze zdjęciami pokazuje, że wnioski się przenoszą.
- **Dlaczego TrOCR i PaddleOCR prawie nie czytają liter tureckich?** TrOCR był trenowany na angielskim, a PaddleOCR działał z domyślnym modelem, którego słownik nie ma tych znaków. Oba wstawiają łacińskie odpowiedniki albo pomijają literę.
- **Ograniczenia według autorów:**
    1. Pismo z czcionek zamiast prawdziwego.
    2. Tekst w scenie wklejony w losowe zdjęcia COCO, bez prawdziwej geometrii i oświetlenia.
    3. Tylko 90 zdjęć.
    4. Brak dostrajania modeli do tureckiego.
- **Impact Factor:** 1,7 i pięcioletni 2,3 to oficjalne wartości z Journal Citation Reports za 2025 rok, podane na stronie Springera. Inne serwisy podają nieoficjalne szacunki.
- **Rozbieżności w artykule:**
    - _GPT-4o na literach tureckich:_ tekst podaje 0,055 i 0,065, a rys. 4 pokazuje 0,066 i 0,065 (tekst pominął puste odpowiedzi, a rysunek wliczył je jako błąd).
    - _Pixtral:_ tekst mówi, że lepiej czyta długie słowa, a na rys. 7 ma na nich minimalnie wyższy błąd (0,334 wobec 0,329).
    - _Tekstury:_ folder `textures` w repozytorium autorów jest pusty; gotowe obrazy z tłami papieru są na Zenodo.

### Czy wyniki artykułu udało się odtworzyć?

- **Liczby z artykułu a predykcje autorów.** Autorzy opublikowali odpowiedzi modeli dla 6600 obrazów _Nutuka_. Liczby z artykułu wychodzą z nich co do 0,001, ale tylko przy CER liczonym na małych literach i bez spacji oraz interpunkcji. Tak liczy skrypt w repozytorium autorów, a artykuł tego nie opisuje. Przykłady: TrOCR 0,380 (w artykule 0,38), GPT-4o na słowach z literami tureckimi 0,065 (0,065), GPT-4o na czystych obrazach 0,017 (0,017). Nie zgadzają się dwie wartości: GPT-4o na słowach bez liter tureckich (0,066 wobec 0,055) i PaddleOCR na czystych obrazach (0,260 wobec 0,239). Claude'a nie da się sprawdzić, bo w danych autorów jest Claude 3.7 Sonnet, a artykuł opisuje Sonnet 4.
- **Ponowne uruchomienie modeli.** Osiem otwartych modeli uruchomiliśmy na Colabie (A100) z poleceniami i ustawieniami autorów, na 1650 obrazach (50 z każdej z 33 kombinacji typu tekstu i podkategorii). Średni CER zgadza się z wynikami autorów na tych samych obrazach co do 0,001 dla siedmiu modeli, a ranking modeli jest taki sam. Wyjątkiem jest Pixtral (0,357 wobec 0,364).
