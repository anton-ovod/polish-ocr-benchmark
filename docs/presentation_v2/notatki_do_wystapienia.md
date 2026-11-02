# Notatki do wystąpienia na Lab 4

Około 600 słów, czyli niecałe 5 minut spokojnym tempem. Czasy przy slajdach są orientacyjne.

## Slajd 1 (15 s)

Omówimy artykuł, który prowadząca zatwierdziła jako bazowy dla naszego projektu: porównanie systemów OCR i modeli wizyjno-językowych w rozpoznawaniu tekstu tureckiego.

## Slajd 2: Czasopismo i autorzy (30 s)

Artykuł ukazał się w 2026 roku w International Journal on Document Analysis and Recognition, czasopiśmie Springera. Impact Factor wynosi 1,7, a pięcioletni 2,3. Na liście ministerialnej ma 100 punktów, w dyscyplinie informatyka techniczna i telekomunikacja. Autorzy pracują na Konya Food and Agriculture University w Turcji. Dwie osoby z zespołu mają w Scopusie po jednej pracy i indeks Hirscha 0, a dwie osoby nadzorujące badania mają indeksy 5 i 9.

## Slajd 3: Cel artykułu (40 s)

Modele OCR i modele wizyjno-językowe uczy się głównie na danych z języków o dużych zasobach, przede wszystkim z angielskiego. Turecki ma mało danych treningowych, siedem własnych liter i długie słowa, bo jest językiem aglutynacyjnym. Wcześniejsze porównania dla tureckiego nie obejmowały modeli wizyjno-językowych i nie było publicznego zbioru z różnymi zniekształceniami. Autorzy stawiają więc cel: pierwsza systematyczna ocena dla tureckiego, z pomiarem wpływu liter, długości słowa, kontekstu, typu tekstu i zniekształceń oraz sprawdzeniem, czy wyniki z danych syntetycznych przenoszą się na prawdziwe zdjęcia.

## Slajd 4: Materiał (45 s)

Autorzy zbudowali własny zbiór: po 6600 syntetycznych obrazów z książki „Nutuk” i z tureckiej Wikipedii oraz 90 prawdziwych zdjęć. Tekst występuje w trzech typach: druk, pismo odręczne i tekst w scenie. Na dole widać przykłady. Każdy typ dzieli się na 11 podkategorii po 200 obrazów, w czterech kategoriach: litery tureckie, długość słowa, słowo albo zdanie oraz zniekształcenia. Dla pisma odręcznego użyli 340 fontów, a nie prawdziwego pisma, i wracają do tego w ograniczeniach. Zdjęcia zrobili sami: szyldy, skany i pismo osób z otoczenia.

## Slajd 5: Metody (40 s)

Porównali dziesięć modeli bez douczania: trzy systemy OCR, pięć otwartych modeli wizyjno-językowych i dwa komercyjne przez API. Każdy dostał to samo polecenie, a odpowiedzi z dodatkowym komentarzem powtórzono z ostrzejszym poleceniem, co dotyczyło 0,56% przypadków. Główna miara to błąd znakowy CER, liczony na małych literach i obcięty do 1, a dla zdań także błąd wyrazowy WER. Przedziały ufności pochodzą z bootstrapu. Litery tureckie analizowano osobno, a zgodność zdjęć z danymi syntetycznymi korelacją Spearmana.

## Slajd 6: Wyniki, porównanie modeli (45 s)

Najlepsze są GPT-4o i otwarty Qwen2.5-VL, z CER około 0,07-0,08. To wyraźnie mniej niż reszta, a Qwen jest modelem otwartym o 7 miliardach parametrów. Komercyjny model nie gwarantuje wyniku: Claude Sonnet 4 jest piąty, choć na prawdziwych zdjęciach awansuje na trzecie miejsce. TrOCR jest ostatni na obu zbiorach. Niebieskie słupki to dane syntetyczne, pomarańczowe to zdjęcia. Kolejność jest bardzo podobna, korelacja Spearmana wynosi 0,92, więc zbiór syntetyczny dobrze przewiduje wyniki na prawdziwych danych. Na zbiorze z Wikipedii błąd jest średnio o 3% wyższy, a kolejność prawie się nie zmienia.

## Slajd 7: Wyniki, co utrudnia odczyt (45 s)

Ta tabela zbiera wyniki z pięciu rysunków artykułu, ciemniejszy kolor to większy błąd. Litery tureckie pogarszają wynik u dziewięciu modeli z dziesięciu, stabilny jest tylko GPT-4o. Pismo odręczne jest najtrudniejsze u wszystkich, a spośród zniekształceń najbardziej szkodzi niska rozdzielczość. Niespodzianka to długość słowa: dłuższe słowa nie są trudniejsze, więc aglutynacja nie jest głównym problemem. Zdania pomagają siedmiu modelom. Na poziomie pojedynczych liter GPT-4o czyta poprawnie 86-94%, a TrOCR i PaddleOCR prawie żadnej litery tureckiej.

## Slajd 8: Wkład własny autorów i elementy nowości (40 s)

Na koniec to, co w tym artykule najważniejsze. Wkład własny autorów: sami zbudowali zbiór 13 200 obrazów i zebrali 90 prawdziwych zdjęć, porównali dziesięć modeli w jednym protokole oraz udostępnili dane i kod. Elementy nowości: według autorów to pierwszy systematyczny benchmark OCR i modeli wizyjno-językowych dla tureckiego, uwzględniający zniekształcenia i kontekst. Nowy jest też publiczny zbiór dla trzech typów tekstu, analiza każdej z siedmiu liter tureckich i sprawdzenie, czy wyniki przenoszą się na prawdziwe zdjęcia. Dane są na Zenodo, kod na GitHubie, ale bez części wyników wersji opublikowanej, więc odtwarzalność jest częściowa. Sami uruchomiliśmy ponownie osiem otwartych modeli na 1650 obrazach i średni CER zgadza się z predykcjami autorów.

## Gdyby padły pytania

- Skąd elementy nowości: autorzy wprost wymieniają jako swój wkład (rozdz. 1) pierwszy benchmark uwzględniający zniekształcenia i kontekst oraz nowy, publiczny zbiór razem z 90 zdjęciami. Analizy liter tam nie wymieniają, a sprawdzenie przenoszenia wyników opisują w rozdz. 4.10. Te dwa punkty dopisaliśmy do listy po lekturze całego artykułu.
- Nasze sprawdzenie: z plików autorów odtwarzamy wszystkie 65 036 zapisanych wartości CER (`test_ocr/`), a osiem otwartych modeli uruchomiliśmy ponownie na 1650 obrazach, po 50 na komórkę (GPU A100, `replication/results/rerun_vs_authors.csv`). Średni CER różni się od predykcji autorów najwyżej o 0,001, a u Pixtrala o 0,007. Predykcje identyczne: 90,4-99,9%, poza Pixtralem (28,3%), który działa z domyślną temperaturą i bez ziarna, więc prawdopodobnie jest losowy. Liczymy CER na małych literach i dzielimy przez długość wzorca, dlatego wartości mogą się różnić od tych z tekstu artykułu na slajdzie 6 (np. TrOCR na tej próbce 0,373, w artykule 0,38).
- Ograniczenia według autorów (rozdz. 5): pismo odręczne z fontów zamiast prawdziwego, tekst w scenie na losowych tłach COCO, mały zbiór zdjęć, tylko język turecki, brak pełnego strojenia hiperparametrów.
- Impact Factor: 1,7 i 2,3 to wartości za 2025 rok ze strony czasopisma u Springera. Serwisy takie jak SciJournal podają inne liczby (np. 2,48), ale nie są źródłem oficjalnym.
- GPT-4o na literach tureckich: tekst artykułu (rozdz. 4.3) podaje 0,055 i 0,065, a rysunek 4 pokazuje 0,066 i 0,065. Różnica bierze się z pustych odpowiedzi, które tekst pomija, a rysunek liczy jako błąd.
- Długość słowa: tekst (rozdz. 4.6) mówi, że Pixtral radzi sobie wyraźnie lepiej z długimi słowami, a na rysunku 7 jest jedynym modelem z minimalnie gorszym wynikiem na długich (0,334 wobec 0,329).
- Tekstury papieru: autorzy użyli pięciu rodzajów papieru z serwisu Vecteezy, a folder `textures` w ich repozytorium jest pusty. Same gotowe obrazy z tymi tłami są na Zenodo.
- Skąd liczby na wykresach: autorzy podają w tekście tylko część wartości, więc resztę odczytaliśmy z grafiki wektorowej rysunków. Dla dziewięciu modeli zgadza się to z plikami autorów co do 0,0001 (`dane_wykresow.csv`).
