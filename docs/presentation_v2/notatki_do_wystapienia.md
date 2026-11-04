# Notatki do wystąpienia na Lab 4

Około 550 słów – bezpieczne 4 minuty 20 sekund spokojnym tempem (zostawia 40 sekund buforu przed limitem 5 minut). Czasy przy slajdach są orientacyjne.

## Slajd 1: Tytułowy (15 s)

Omówimy artykuł, który wybraliśmy jako bazowy dla naszego projektu: kompleksowe porównanie systemów OCR i modeli wizyjno-językowych w rozpoznawaniu tekstu tureckiego na danych syntetycznych.

## Slajd 2: Czasopismo i autorzy (30 s)

Artykuł ukazał się w 2026 roku w _International Journal on Document Analysis and Recognition_, czasopiśmie Springera. Impact Factor wynosi 1,7, a pięcioletni 2,3. Na liście ministerialnej ma 100 punktów w dyscyplinie informatyka techniczna i telekomunikacja. Autorzy pracują na Konya Food and Agriculture University w Turcji: dwóch młodszych badaczy z indeksem Hirscha 0 oraz dwaj promotorzy nadzorujący projekt z indeksami 5 i 9.

## Slajd 3: Cel artykułu (40 s)

Modele wizyjno-językowe i klasyczny OCR trenuje się głównie na językach o wielkich zasobach, przede wszystkim angielskim. Turecki ma mało danych treningowych, siedem liter swoistych i długie słowa wynikające z aglutynacji. Wcześniejsze benchmarki nie obejmowały modeli wizyjno-językowych i brakowało publicznego zbioru z kontrolowanymi zniekształceniami. Autorzy stawiają jasny cel: pierwsza systematyczna ocena OCR i VLM dla tureckiego – pomiar wpływu liter, długości słów, zdań, pisma i zniekształceń oraz sprawdzenie, czy wyniki z syntetyków przekładają się na rzeczywiste zdjęcia.

## Slajd 4: Materiał: zbiór danych (40 s)

Autorzy wygenerowali 13 200 syntetycznych obrazów: po połowie z traktatu politycznego „Nutuk” i z Wikipedii, a do tego zebrali 90 prawdziwych zdjęć. Mamy tu trzy typy tekstu: druk, pismo odręczne z 340 fontów oraz tekst w scenie na tłach COCO. Każdy typ dzieli się na 11 podkategorii w czterech grupach: litery tureckie, długość słowa poniżej i powyżej 10 znaków, słowo lub zdanie oraz pięć rodzajów zniekształceń.

## Slajd 5: Metody: modele i ocena (35 s)

Przetestowano dziesięć modeli bez douczania: trzy silniki OCR, pięć modeli otwartych VLM i dwa komercyjne przez API. Każdy dostał identyczne polecenie wydobycia tekstu. Główna miara to błąd znakowy CER liczony na małych literach i obcięty do 1, a dla zdań dodatkowo błąd wyrazowy WER. Przedziały ufności wyznaczono bootstrapem, a zgodność rankingów na zdjęciach i syntetykach zbadano korelacją Spearmana.

## Slajd 6: Wyniki: porównanie modeli (40 s)

Zdecydowanymi liderami są komercyjny GPT-4o i otwarty Qwen2.5-VL 7B z błędem CER na poziomie 0,07–0,08. Otwarty model dorównuje więc rozwiązaniu komercyjnemu. Co ciekawe, Claude Sonnet 4 zajął dopiero piąte miejsce na syntetykach, choć na zdjęciach awansował na trzecie. TrOCR zamyka stawkę. Kluczowy wniosek: kolejność modeli na danych syntetycznych niemal idealnie pokrywa się ze zdjęciami rzeczywistymi – korelacja Spearmana wynosi aż 0,92.

## Slajd 7: Wyniki: co utrudnia odczyt (40 s)

Wykres podsumowuje wpływ poszczególnych warunków:

- Litery tureckie pogarszają wynik niemal wszystkich modeli – stabilny jest wyłącznie GPT-4o. Najtrudniejsze są litery ı oraz wielkie İ.
- Pismo odręczne i niska rozdzielczość sprawiają największą trudność.
- Zaskoczeniem jest długość słów: dłuższe słowa wcale nie zwiększają błędu, więc aglutynacja nie jest główną przeszkodą.
- Kontekst całego zdania wyraźnie pomaga modelom wizyjno-językowym.

## Slajd 8: Wkład autorów, nowości i nasza replikacja (40 s)

Wkład autorów to budowa pierwszego tak wszechstronnego benchmarku dla tureckiego, publiczny zbiór danych oraz udowodnienie, że dane syntetyczne trafnie przewidują wyniki na zdjęciach.

Jako nasz wkład własny zweryfikowaliśmy pełną odtwarzalność tego badania:

1. Przeliczyliśmy wszystkie 65 tysięcy wartości CER z plików autorów – wyniki są w 100% spójne.
2. Na platformie Google Colab z GPU A100 uruchomiliśmy ponownie osiem otwartych modeli na reprezentatywnej próbce 1650 obrazów.
3. Uzyskaliśmy zgodność średniego błędu CER z autorami co do 0,001 dla siedmiu modeli i 0,007 dla Pixtrala.
4. Wykryliśmy też braki w repozytorium autorów: brak logów Claude'a, brak zapisu wyników dla zdjęć i brak plików tekstur papieru.

---

## Gdyby padły pytania (Q&A)

### Modele na Colabie i replikacja (wkład własny)

- **Jakie modele uruchomiliśmy na Colabie?** Wszystkie 8 otwartych modeli autorów: GOT-OCR 2.0, DeepSeek-VL2-tiny, Phi-3.5-Vision, Qwen2.5-VL-7B, InternVL3-8B, Pixtral-12B, TrOCR i PaddleOCR (`colab/run_replication.py`).
- **Na jakim sprzęcie i w jakim środowisku?** Google Colab z kartą Nvidia A100 (40 GB VRAM). Każdy model miał odizolowane środowisko wirtualne ze ściśle przypiętymi wersjami zależności i rewizjami wag z HuggingFace (`replication/results/runs.json`).
- **Dlaczego nie uruchomiliśmy GPT-4o i Claude Sonnet 4?** Ponieważ to komercyjne modele dostępne wyłącznie przez płatne, zamknięte API. Dostawcy regularnie podmieniają wagi pod tymi samymi endpointami bez wersjonowania, co wyklucza pełną, niezależną odtwarzalność naukową.
- **Dlaczego u Pixtrala zgodność predykcji wynosi 28,3%, a CER różni się o 0,007?** Pixtral w kodzie autorów był wywoływany z domyślną temperaturą i bez sztywnego ziarna generatora losowego, co wprowadziło drobną stochastyczność. Pozostałe 7 modeli osiągnęło 90,4–100% identycznych odpowiedzi.
- **Skąd drobne różnice w liczbach (np. TrOCR 0,373 vs 0,38)?** Autorzy w tekście podają zaokrąglone wartości z całego zbioru 13 200 obrazów; nasza próba to 1650 obrazów (po 50 na każdą z 33 komórek), a CER liczymy po normalizacji do małych liter ze standardowym wzorem Levenshteina.

### Metodyka i zbiór danych

- **Dlaczego zbiór syntetyczny zamiast prawdziwych dokumentów?** Dla języka tureckiego nie istniał żaden publiczny, anotowany zbiór rzeczywisty zawierający zrównoważone kategorie zniekształceń i długości. Generator pozwolił ściśle wyizolować pojedyncze czynniki trudności. Wysoka korelacja ($\rho = 0{,}92$) ze zdjęciami potwierdziła słuszność tego podejścia.
- **Dlaczego TrOCR i PaddleOCR miały blisko 0% na literach tureckich?** Były ewaluowane w trybie _zero-shot_ – TrOCR uczył się na angielskim, a Paddle używał modelu domyślnego. Ich tokenizery i słowniki nie zawierają specyficznych tureckich znaków (ı, İ, ğ, ş), więc modele te zastępują je literami łacińskimi lub je pomijają.
- **Jakie są słabe strony i ograniczenia artykułu (rozdz. 5 wg autorów)?**
  1. Pismo odręczne wygenerowano z fontów Google Fonts, a nie prawdziwego pisma ludzkiego (brak naturalnych wahań linii i nacisku).
  2. Tekst w scenie to napisy nałożone na losowe tła COCO, co nie oddaje w pełni geometrii i oświetlenia naturalnych scen.
  3. Skromny zbiór prawdziwych zdjęć (tylko 90 fotografii).
  4. Brak dostrajania (_fine-tuningu_) modeli do języka tureckiego.
- **Impact Factor:** 1,7 oraz 5-letni 2,3 to oficjalne wartości z bazy Journal Citation Reports (JCR) za 2025 rok podane bezpośrednio na stronie wydawnictwa Springer. Serwisy trzecie (np. SciJournal) podają nieoficjalne estymaty.
- **Rozbieżności w artykule wyłapane podczas lektury:**
  - _GPT-4o na literach tureckich:_ w tekście podano 0,055 i 0,065, a na rys. 4 jest 0,066 i 0,065 (tekst pominął puste odpowiedzi, a rysunek wliczył je jako błąd).
  - _Długość słów u Pixtrala:_ tekst twierdzi, że Pixtral lepiej czyta długie słowa, podczas gdy na rys. 7 ma na nich minimalnie wyższy błąd (0,334 vs 0,329).
  - _Tekstury:_ folder `textures` w repozytorium autorów jest pusty, choć same gotowe obrazy z tłami papieru udostępniono na Zenodo.
