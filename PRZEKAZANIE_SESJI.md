# Przekazanie pracy do nowej sesji (stan na 04.11.2026)

Ten plik jest instrukcją "jak kontynuować" dla Claude Code w nowej sesji. Czytaj go razem z `CLAUDE.md` (zasady bezwzględne), `DECYZJE.md` (ustalenia właścicielki) i `STAN_PRAC.md` (historia i bieżący stan). Użytkowniczka pisze po polsku, odpowiadaj po polsku i konkretnie. Teksty ofert piszesz po angielsku, potem polski (sprawdza właścicielka) i 7 pozostałych języków (szkice bez weryfikacji natywnej).

## 1. Jak zacząć nową sesję (kolejność)

1. Przeczytaj: `CLAUDE.md`, `PRZEKAZANIE_SESJI.md` (ten plik), `DECYZJE.md`, `STAN_PRAC.md` (sekcja "STAN NA 04.11.2026" na górze).
2. Sprawdź środowisko (sekcja 2): zmienne `ETSY_KEYSTRING`, `ETSY_SHARED_SECRET` (nie wypisuj wartości), dozwolone domeny, autoryzacja OAuth (tokeny trzeba odnowić w każdej nowej sesji: `.secrets/` nie jest w repozytorium).
3. Policz zapytania API w oknie 24 h: `python3 -I scripts/api_licznik.py`. Stop skryptów przy 9000 (limit Etsy 10 000, okno kroczące).
4. Zapytaj właścicielkę, który typ produktu bierzemy dalej (sekcja 4 podaje, co zostało), i prowadź pracę według "Playbooku" (sekcja 6).
5. Po każdym kroku: commit i push na gałąź sesji (hook końca sesji tego wymaga). Przed commitem sprawdź, że w plikach nie ma tokenów ani kluczy.

## 2. Środowisko, dostęp, bezpieczeństwo

* **Sieć (poziom Custom):** `api.etsy.com`, `i.etsystatic.com` (zdjęcia ofert), `www.artdog.com.pl` (wideo i zdjęcia produktów). Nie łącz się z innymi domenami i nie obchodź blokad. Serwer `artdog.com.pl` odrzuca domyślny User-Agent Pythona (403): skrypty używają `curl` albo `User-Agent: ArtDog-Etsy-Tool/1.0`. Dokumentacja Etsy: `developers.etsy.com`.
* **Zmienne środowiskowe (ustawia właścicielka w ustawieniach środowiska, nie w repozytorium):** `ETSY_KEYSTRING` (client_id do OAuth), `ETSY_SHARED_SECRET` (używany tylko w `scripts/etsy_api.py` do złożenia nagłówka `x-api-key`; nigdy nie wypisuj, nie zapisuj w logach i plikach). Proxy sesji nie przepuszcza nagłówka `Authorization` przy sekretach sieciowych, dlatego sekret Etsy NIE jest sekretem sieciowym, tylko zmienną środowiskową.
* **OAuth w nowej sesji:** `scripts/etsy_auth.py`. Wygeneruj PKCE i `state`, zapisz verifier i state w `.secrets/`, wypisz tylko adres `https://www.etsy.com/oauth/connect` z parametrami (client_id = `ETSY_KEYSTRING`, adres przekierowania identyczny z zarejestrowanym, scope najpierw tylko odczyt `listings_r shops_r`; do zapisu `listings_w`). Właścicielka otwiera adres, loguje się (2FA) i wkleja cały adres po przekierowaniu. Wymień kod na token: `python3 -I scripts/etsy_auth.py exchange '<pełny adres>'`. Token dostępu ważny ok. 1 h (odświeża się automatycznie: `etsy_api.py`, `etsy_auth.py refresh`), odświeżający ok. 90 dni. Tokeny tylko w `.secrets/` (w `.gitignore`). Zakres `listings_d` (usuwanie): NIE używamy. Wolno o niego prosić wyłącznie do wymiany zdjęć i tylko po zgodzie właścicielki; wymianę zdjęć robimy przez nadpisanie slotu, bez usuwania.
* **Limity API:** 10 zapytań/s, 10 000/dobę w oknie kroczącym 24 h (nie od północy). `scripts/etsy_api.py` liczy każde zapytanie w `logs/api_requests_<data>.log`, ostrzega przy 8000 i przerywa przy 9000 (`DAILY_STOP`, podniesione z 8000 za zgodą właścicielki 31.10.2026; dotyczy WSZYSTKICH poleceń, także odczytów i odświeżania tokenu). Stan: `python3 -I scripts/api_licznik.py`. Zapisz do logu każde zapytanie, żeby okno było liczone poprawnie po restarcie sesji (pliki `logs/api_requests_*.log` są częścią stanu: przenieś je).
* **GitHub:** repozytorium `liszkak-design/ANITA-Art-Dog`. Praca na gałęzi przydzielonej sesji; push z `git push -u origin <gałąź>`. Pull requestów nie twórz bez prośby.
* **Długie zadania:** uruchamiaj skrypty zapisu w tle (`nohup ... &`) i czekaj monitorem; limit czasu polecenia na pierwszym planie to 10 minut. Skrypty są wznawialne (pomijają wykonane kroki wg logu), więc przerwanie nie szkodzi. Powiadomienie o zakończeniu polecenia startującego (`nohup ... &`) NIE oznacza końca skryptu: sprawdź `ps`/`pgrep`.

## 3. Pliki do przeniesienia na nową gałąź

Pełny wykaz, poziomy ważności i polecenia git: patrz `PRZEKAZANIE_PLIKI.md`. W skrócie:
* **Konieczne (małe):** `CLAUDE.md`, `PRZEKAZANIE_SESJI.md`, `PRZEKAZANIE_PLIKI.md`, `DECYZJE.md`, `STAN_PRAC.md`, `.gitignore`, `Audyt_Etsy_ArtDog.xlsx`, `data/` (Rasy.xlsx, eksporty CSV, `nick_klasyfikacja.csv`, arkusze wymiarów), `scripts/`, `templates/`.
* **Zalecane:** `logs/` (bez tego `is_done()` nie wie, które oferty są zrobione; liczniki API), `backup/` (kopie przed zmianami, do cofnięcia), `media/` (zdjęcia przekazane przez właścicielkę), `plans/` (mapy ofert na foldery, plany partii zamrożone do ponownego użycia).
* **Wideo:** pliki `video/*.mp4` leżą na gałęzi `claude/stoic-edison-coahbl` (tam też źródła do generowania filmów `video/src/`). Film kopiuje się do bieżącej gałęzi poleceniem `git fetch origin claude/stoic-edison-coahbl && git checkout origin/claude/stoic-edison-coahbl -- video/<nazwa>.mp4`. Zawsze po `git fetch` (plik mógł być zaktualizowany).

## 4. Co zostało do zrobienia (stan 04.11.2026)

**Zoptymalizowane (zapisane i zweryfikowane):** płytki "with a Photo" 299, urny ze zdjęciem 299, urny z grafiką psy 100, urny z grafiką koty 45, urny z małym reliefem 154, niskie urny z reliefem 154, urny z reliefem z zimnego brązu 38, płytki "plakietki same" (relief) 38, tablice pamiątkowe 38, popiersia wiszące 78, płytki z grafiką psy 100, płytki z grafiką koty 45. Tabela grup, skryptów i szablonów: `STAN_PRAC.md`, sekcja "STAN NA 04.11.2026".

**Zakończone 04.11.2026:** korekta "plywood" w 745 urnach (partie 1-15, wszystkie weryfikacje ok): `scripts/plywood_korekta.py`, plan `plans/plywood_plan.csv`. Skrypt dopisuje "plywood" do istniejących materiałów tekstowych (po "wood") i do właściwości Material (id 5199), niczego nie zastępuje; ten sam wzorzec można użyć do kolejnych zbiorczych korekt materiałów (`apply N --apply [--lid=ID]`, apply pomija oferty z wpisem `plywood_weryfikacja` w logu).

**Do zrobienia:**
* 2 oferty "Big Urn for Horse" (1381486535, 1381486029; cena 199): osobna decyzja i zakres.
* Ok. 40 innych typów produktów (lista: `Audyt_Etsy_ArtDog.xlsx` oraz eksport `data/EtsyListingsDownload*.csv`; fakty o produktach podaje właścicielka).
* Ok. 200 nowych ofert (szkice; wzór: `scripts/nowa_oferta_urna.py`, oferta 4605567054; publikacja po akceptacji właścicielki).
* Statuetki z brązu i urny ze statuetką/grawerem to ok. 81% przychodu: zmieniać na końcu i ostrożnie, najpierw typy o niższej sprzedaży.
* Ręcznie robi właścicielka: SKU (EAN), GPSR, shopping basket summary; kategoria oferty zmienia się tylko na jej decyzję (tablice zostają w "Signs").

## 5. Zasady postępowania (skrót; pełne: CLAUDE.md)

* Domyślnie dry-run. Zapis tylko z `--apply` i po wyraźnym "tak, zapisz ..." dla KONKRETNEJ partii (lub testu). Pytanie o zapis zadawaj osobno, nawet gdy właścicielka wcześniej zatwierdziła teksty. Akceptacja tekstów ("zatwierdzam, rób test") nie jest zgodą na zapis partii. Jeśli odpowiedź jest niejednoznaczna, dopytaj. Jeżeli właścicielka odpowiada "tak" na pytanie z propozycją zapisu, to jest to zgoda na ten zapis.
* Przed zmianą oferty kopia `backup/<id>_<data>.json`. Partie do 50 ofert. Po partii log i prośba o sprawdzenie próbki przed następną. Skrypty muszą być wznawialne. Jedna partia zapisu na raz (bez równoległych zapisów).
* Nie usuwaj niczego (ofert, zdjęć, personalizacji, tłumaczeń, wideo) bez osobnej, wyraźnej zgody dla konkretnej operacji. Gdy trzeba coś usunąć (np. błędnie wgrany film), poproś właścicielkę o ręczne usunięcie w Etsy i dopiero wtedy wgraj poprawne pliki.
* Nie zmieniaj cen, stanów, profili wysyłki, statusu aktywności i kategorii bez wyraźnej prośby. Nie ruszaj "Home style" (Art deco), jeśli właścicielka nie poprosi.
* Nie wymyślaj danych o produktach (wymiary, pojemność, materiał, terminy). Braki zgłoś jako pytanie. Nazwy ras i ich tłumaczenia tylko z `data/Rasy.xlsx`; brak rasy zgłoś, nie zgaduj. Nie ustawiaj statusów "zatwierdzone"/"zweryfikowane" w `Rasy.xlsx` bez potwierdzenia właścicielki (wiersze dodane na jej polecenie dostają status "propozycja (do sprawdzenia)").
* Nigdy nie wypisuj i nie commituj kluczy, Shared Secret, tokenów, verifierów PKCE.
* Zawsze zadawaj pytania o to, czego nie wiesz (właścicielka tego oczekuje: "Zadaj pytania"). Odpowiadaj na pytania o stan konkretnymi liczbami z logów.
* Po zakończeniu każdej partii zaktualizuj `STAN_PRAC.md`.

## 6. Playbook: nowy typ produktu (krok po kroku, sprawdzony 12 razy)

Szablonem do klonowania jest najnowszy pełny skrypt grupowy: `scripts/batch_plakietki_grafika.py` (płytki, bez wymiarów) albo `scripts/batch_urny_koty_grafika.py` (urny, zdjęcie 7) albo `scripts/batch_hanging.py` (wymiary, 3 atrybuty, bez personalizacji). Wszystkie mają trzy polecenia: `raport`, `plan N [--lid=ID] [--size=K]`, `apply N --apply`.

1. **Rozpoznanie grupy (tylko odczyt).** Znajdź sekcję sklepu i oferty grupy: `GET /v3/application/shops/{shop_id}/shop-sections/listings?shop_section_ids=<ID>&limit=100&offset=0&sort_on=created|price&sort_order=asc|desc` (jedno wywołanie zwraca max 100; zsumuj widok z 4 sortowań; offset >0 w sekcjach nie działa; przy całym sklepie `GET /shops/{id}/listings?state=active&limit=100&offset=N` offset działa). Zapisz listę do `plans/<grupa>_sekcja_lista.json` (listing_id, tytuł). Typ oferty rozpoznaj po tytule (np. "Hanging Statue", "Graphics").
2. **Stan żywy.** `scripts/analiza_<grupa>.py` (wzór: `analiza_hanging.py`): 1 zapytanie na ofertę z `includes=Images,Videos,Personalization,Translations`; zapis `plans/<grupa>_stan_zywy.json` (tytuł, wyświetlenia, cena, ilość, zdjęcia z id i alt, wideo, personalizacja, materiały, tagi, tłumaczenia, who_made, sekcja). Sprawdź: ile zdjęć w każdej ofercie (czy wszędzie tyle samo), czy są filmy, personalizacja, tłumaczenia.
3. **Foldery wideo/zdjęć.** `scripts/crawl_<grupa>.py` (wzór: `crawl_hanging.py`; używa `curl` z User-Agentem): indeks `plans/<grupa>_foldery_index.csv` (folder, nazwa, EAN, pliki wideo z rozmiarem, zdjęcia). Adres folderu podaje właścicielka. W folderze rasy są zwykle 2 filmy: bez i z końcówką `-brand`.
4. **Mapa oferta -> folder (EAN).** Pobierz miniatury zdjęć ofert i `https://www.artdog.com.pl/allegro/zebraneEAN/<EAN>/<n>.JPG|jpg` (n=0..6, pomniejsz do 400 px). Porównaj po obrazie: cosinus podobieństwa szarych miniatur 48x48 po odjęciu średniej (wynik ≥0,99 = ten sam obraz). Kilka folderów może mieć te same zdjęcia (duplikaty): wtedy rozstrzygnij po nazwie folderu/oferty i wymiarach, nie po obrazie. Wynik `plans/<grupa>_mapa.csv` (listing_id, wyświetlenia, nazwa w tytule, folder, ean, podobieństwo, rasa z Rasy.xlsx, odmiana, uwagi). Rasy rozwiąż przez `batch_urny.resolve` z użyciem `NAME_FIX` (skróty z tytułów) i `FEATURE_BY_LID` (odmiany: Wire-haired, Long-haired, cropped ears).
5. **Wymiary (jeśli produkt je ma).** Arkusz dostarcza właścicielka (kolumny: nazwa, EAN, waga, wysokość, szerokość, długość = głębokość). SPRAWDŹ z liczbami na zdjęciu z wymiarami w ofercie (odczyt wzrokowy z arkuszy kontrolnych: przytnij dolny lewy róg zdjęcia). Arkusze miały pomyłki (zamienione kolumny, skopiowane wiersze). Każdą rozbieżność zgłoś w tabeli i czekaj na decyzję; zapisuj decyzje do `plans/<grupa>_decyzje.json`.
6. **Pytania do właścicielki (zadaj zanim napiszesz teksty).** Zobacz sekcję 13 (lista kontrolna pytań).
7. **Szkic EN** w `templates/<grupa>_propozycja_tekstow.md` w ustalonym formacie (sekcje `## 1. Tytuły`, `## 2. Tagi`, `## 3. Pierwszy akapit` z bankami A/B/C, `## 4. Sekcje stałe` w bloku kodu, pola personalizacji, alt texty). Zacznij od zatwierdzonego szablonu najbliższego produktu (tabela w `STAN_PRAC.md`) i zamień tylko to, co się różni. Zasady treści: sekcja 8.
8. **Akceptacja EN -> polski.** `templates/<grupa>_tlumaczenie_pl.md` (te same sekcje: tytuły, banki A/B/C bez wariantów ze zdrobnieniem i synonimem, sekcje stałe, tagi z licznikiem długości). Właścicielka sprawdza polski i wnosi poprawki; wprowadzaj je także do EN, gdy dotyczą treści.
9. **Pozostałe 7 języków** (DE, NL, FR, IT, PT europejski, ES, SV) z polskiego i angielskiego. Dane trzymaj w skrypcie generatora (`scripts/gen_*_tr.py`), który zapisuje `templates/<grupa>_tlumaczenie_<kod>.md`. Zdania wspólne (zdjęcie, orientacja, pytania, International Orders) kopiuj z zatwierdzonych szablonów tego samego typu, nie tłumacz od nowa. Formy zwracania się: DE Sie, NL u, FR vous, IT Lei, PT a sua / o seu, ES tú, SV du. Tagi max 20 znaków (skrypt sprawdza i przerywa). Nazwy ras w językach tylko z `Rasy.xlsx` (`U.NAME_COL[kod]`).
10. **Skrypt grupowy** (klon wzorca, zob. sekcja 7), `raport` (kontrola wszystkich ofert bez zapisu: tytuły, słowa, powtórzenia, tagi, filmy), `plan 1 --lid=<oferta o najniższych wyświetleniach>` (dry-run testu). Pokaż właścicielce: tytuł, tagi, opis, alty, personalizację, materiały, wymiary, filmy, tłumaczenia, liczbę zapytań i stan licznika, i zapytaj o "tak" dla testu.
11. **Test na jednej ofercie** (`apply 1 --apply`), weryfikacja po zapisie (cena, stan, status, zdjęcia z tymi samymi id i kolejnością, alty, filmy z NAZWAMI plików, personalizacja, tłumaczenia, materiały, wymiary). Prośba o sprawdzenie w Etsy; czekaj na akceptację próbki.
12. **Partie po maks. 50** (`plan N`, pokaż, "tak", `apply N --apply` w tle, monitor, weryfikacja z logu, commit, push, prośba o próbkę). Kolejność: od najmniej oglądanych, najczęściej oglądane na końcu.
13. **Zakończenie:** `STAN_PRAC.md` (wpis o grupie), skrypty i szablony w repozytorium, podsumowanie dla właścicielki z liczbami.

## 7. Architektura skryptów grupowych (jak klonować bez błędów)

Wspólne moduły: `scripts/etsy_api.py` (klient, licznik, odświeżanie tokenu), `scripts/batch.py` (`SHOP_ID`, `rasy()`, `feature_words()`, `e_class()`, `backup_unique`, `is_done`, `done_steps`, `zlog`, `MATERIAL_PROPERTY`), `scripts/batch_urny.py` (`resolve`, `breed_lookup`, `pick`, `FORMS`, `NAME_COL`, `alt_existing`, `LANG_ALL`, `MATERIAL_VALUES`), `scripts/batch_relief.py` (`sec`, `curl_to`, `preflight`), `scripts/apply_test_sphynx.py` (`send`, `ok`, `multipart`).

Wzorzec każdego skryptu:
* Teksty ładowane z szablonów w `templates/` (regexy po nagłówkach `## 1. Tytuły` itd.); liczby wariantów w asercjach (EN: A 11-15, B 4, C 3-5; tłumaczenia: A5, B3, C3-4, tagi stałe 5-7 + pula 16-19).
* Wybór wariantów deterministyczny po ID oferty (`U.pick(lid, slot, n)`), więc ponowne uruchomienie daje ten sam wynik. Zdanie A zależy od zdrobnienia [N] / synonimu [S] z kolumny E `Rasy.xlsx` (klasyfikacja `data/nick_klasyfikacja.csv`). Tagi: 5-7 stałych + losowane z puli (kolejność po `sha256(lid:tag:...)`, bez więcej niż 3 powtórzeń słowa kluczowego; tłumaczenia z jednym tagiem o zdjęciu).
* Tytuł: pierwszy wzorzec od wylosowanego, który mieści się w 14 słowach i 140 znakach i nie powtarza słów (funkcja `repeated`, nazwa rasy wyłączona z kontroli); gdy rasa ma słowo "Dog"/"Cat" w nazwie, pomijaj je we wzorcu.
* `check()` blokuje ofertę przy: tytule >140 zn. lub >14 słów, powtórzonych słowach, zakazanych słowach, tagach (nie 13, >20 zn.), niepodstawionych znacznikach `{...}`, w tłumaczeniach też.
* `plan N` zapisuje `plans/partia_<grupa>_00N.csv` i `..._dryrun.json` (zamrożony plan z pełnymi tekstami, alt, tłumaczeniami, nazwami filmów, `images_before`). `apply N` czyta WYŁĄCZNIE zamrożony plan.
* `apply`: `backup_unique` (kopia: oferta z Images/Videos/Translations/Personalization, właściwości, inwentarz), preflight (status active, liczba i id zdjęć jak w planie, brak wideo, tytuł jak w planie), kroki po kolei z logiem `logs/zapis_<id>_<data>.jsonl` (id kroku, wartość przed/po, status): `listing` (PATCH tytuł/opis/tagi/ew. materiały), `wlasciwosc_materials` (PUT Material), `how_its_made` (who_made collective), `personalizacja` (POST), `alt_<n>`, `zdjecie_<n>` (nowe zdjęcia), `wideo_1_*`, `wideo_2_*`, `tlumaczenie_<kod>` (POST, a gdy istnieje: PUT), na końcu `weryfikacja` z odczytem (do 4 prób). Zatrzymanie na pierwszym błędzie; ponowne uruchomienie pomija kroki ze statusem ok.
* Weryfikacja sprawdza też NAZWY plików filmów w logu (błąd z 04.11.2026: skrypt wskazywał stary plik filmu i weryfikacja liczyła tylko filmy). Przed testem porównaj stałe `VIDEO1`, `PHOTO7`, ścieżki `media/` i `BASE_V` ze zleceniem właścicielki.
* Kopiując skrypt, przejrzyj WSZYSTKIE stałe (gatunek "pies"/"kot", foldery, nazwy plików planu, słowo "Dog"/"Cat", materiały, stan liczby zdjęć w preflight i weryfikacji) i uruchom `raport` oraz `plan 1 --lid=...` przed pokazaniem czegokolwiek właścicielce.

## 8. Konwencje treści (obowiązują w nowych grupach)

* **Tytuł:** rasa z kolumny C na początku (plus odmiana ze "Słowa stałe": Wire-haired, Long-haired, Smooth-haired, Short-haired, Collie Rough, Fox Terrier Wire, "Cropped Ears" tylko przy uszach przyciętych; nigdy "Natural Ears"). Do 14 słów (wyraz z myślnikiem = 1), do 140 znaków (cel 100-130, ale nie upychamy), BEZ powtórzeń słów (zalecenie Etsy; zwłaszcza dog, for), bez "cold cast bronze". Tytuły zróżnicowane słowem kluczowym między ofertami (np. bust, hanging dog head, sculpture, statue, statuette).
* **Tagi:** 13, max 20 znaków, bez nazw ras, bez powtórzeń, 5-7 stałych + z puli.
* **Opis:** pierwszy akapit z banków A (otwarcie z nazwą rasy), B (zastosowanie), C (personalizacja lub zawieszenie); jedno zdanie nie zawiera pełnej nazwy rasy dwa razy; zdrobnienie (kol. E, typ "zdrobnienie") najwyżej 2 razy; synonim (typ "synonim") w zdaniu A; nie powtarzaj tej samej informacji w dwóch zdaniach akapitu (np. filc i haczyk tylko w jednym). Sekcje stałe z nagłówkami wielkimi literami; na końcu zawsze INTERNATIONAL ORDERS (tekst z szablonów). Bez zdania o pożegnaniu w produktach nie żałobnych; ton spokojny, bez haseł sprzedażowych.
* **Zakazy językowe:** w polskim nigdy "trwały/trwałe", "ciche miejsce", "daty życia" zamiast "daty" przy datach; "Cannot be personalised" tylko gdy dotyczy. "bust" tylko dla trójwymiarowych głów (popiersia wiszące), dla płyt i reliefów: relief/bas-relief/płaskorzeźba; "plaque" nie dla przedmiotów trójwymiarowych; "statue", "sculpture", "statuette" dozwolone dla popiersi wiszących.
* **Brąz:** słowa sugerujące podobieństwo ("cold cast bronze" z objaśnieniem materiału, "bronze-look", "o wyglądzie brązu", "looks like a classic bronze piece") są poprawne; samo "bronze relief"/"relief z brązu" jako materiał jest nieprawdziwe (klienci skarżą się, że żywica to plastik). Tagi mogą zostać.
* **Proces wykonania statuetek:** model rzeźbiony ręcznie przez artystę, forma, odlew (też ręczny, bez polerowania). Pisz "designed by hand" / "hand-designed", NIE "finished by hand"; ręczne jest tylko zamocowanie filcu i haczyka. Nie opisuj procesu wprost.
* **Zdjęcia:** domyślnie ich nie wymieniamy (tylko alt texty do istniejących, rodzaj zdjęcia rozpoznaj z obrazu, nie z pozycji). Dodajemy zdjęcia wskazane przez właścicielkę na końcu (np. zdjęcie 7 "Unedited photo of ..."). Nieedytowane zdjęcie prawdziwego przedmiotu zawsze ostatnie. Alt: opisowy, zgodny z obrazem, rasa jak w tytule, z poprawnym a/an. Pliki dostarczone przez właścicielkę zapisuj w `media/<grupa>/`.
* **Filmy:** max 2 na ofertę. Film 1 = plik zatwierdzony przez właścicielkę dla typu (gałąź `claude/stoic-edison-coahbl`, `video/video-*-anita.mp4`), film 2 = film rasy z folderu EAN (zwykle wersja BEZ `-brand`; w starszych grupach wersja z brand jako drugi film, jeśli właścicielka tak zleciła). Zawsze sprawdź, który wariant zlecono.
* **Personalizacja (wszystkie warianty dobrowolne, o ile nie napisano inaczej; limity Etsy: pytanie max 45 zn., etykieta opcji listy max 20 zn., instrukcja max 120 zn., pole tekstowe do 1024):** płytki: "Do you want to personalize the plaque?" (No, as shown / Yes, personalize it), "Your photo (optional)" (wgranie), "Print style (if own photo)" (Original photo / No background), "Name and dates (optional)" (50 zn.), "Plaque orientation (if own photo)" (Vertical / Horizontal). Urny z grafiką: Name (50, wymagane), Dates (50, wymagane), Quote on the plaque (600, opcjonalne, domyślny cytat "You left paw prints on my heart"), Pet photo (wgranie), "How should we print the photo?" (Color + background / Color, no background). Tablice pamiątkowe: Name, Dates (wymagane), Quote on the name plate (1024). Popiersia wiszące: bez personalizacji. Portretu geometrycznego/kreskówkowego na życzenie nie robimy (klient może przesłać własne zdjęcie).
* **Materiały:** tekstowe i z listy Etsy (właściwość Material multi, id 148789511893). Id wartości: Bronze 71, Resin 227, Composite 96, Metal 174, Brass 68, Pine 203, Birch 1059, Ceramic 83, Wood 286, Plywood 5199. Płytki i urny: Ceramic (+ Brass, Pine, Birch, Metal, Plywood zależnie od grupy). Tablice: Bronze, Resin, Composite (tekstowe: cold cast bronze, MDF board, engraving laminate). Popiersia: Bronze, Resin (tekstowe: cold cast bronze). **Plywood: dodawany do istniejących materiałów (tekstowych i z listy) we wszystkich urnach; nie zastępuje obecnych zapisów.** Właściwości wymiarów: Height 47626759834, Width 47626759898, Depth 54142602037 (wartości tekstowe, np. "14.5", `scale_id` 7 = cm; pola `item_*` nie są widoczne w interfejsie).
* **Ustawienia oferty:** `who_made = collective`, `when_made = made_to_order`, `is_supply = false` (wysyłać razem w `updateListing`; `someone_else` jest odrzucane).
* **Rasy i nazwy:** Zawsze kolumna C `Rasy.xlsx`. Rozstrzygnięcia: DECYZJE.md sekcje 3, 9a, 14.
* **Cytaty i tabliczki:** cytaty po angielsku w każdym języku (domyślny cytat nie jest tłumaczony); w polskim "daty" jako "daty życia".

## 9. Etsy API: id, endpointy i pułapki

* Sklep: `B.SHOP_ID`. Endpointy używane: `PATCH /shops/{id}/listings/{lid}` (updateListing: tytuł, opis, tagi (CSV), materiały (CSV), who_made/when_made/is_supply), `PUT /shops/{id}/listings/{lid}/properties/{property_id}` (value_ids, values, scale_id; ZASTĘPUJE całą listę wartości, więc przy dopisywaniu odczytaj obecne), `POST .../personalization` (zastępuje cały zestaw pytań; JSON z `personalization_questions`; typy `text_input`, `dropdown`, `unlabeled_upload`), `POST .../images` (alt do istniejącego: `listing_image_id`+`rank`+`overwrite=true`+`alt_text`; nowe zdjęcie: plik + `rank` + `overwrite=false`; nadpisanie slotu: plik + `rank` + `overwrite=true`), `POST .../videos` (multipart, max 2), `POST/PUT .../translations/{język}` (POST, a gdy istnieje: PUT; tylko tytuł, opis, tagi; 8 języków: nl fr de it pl pt es sv).
* Brak w API: SKU bez ryzyka dla ceny i stanu, shopping basket summary, GPSR, kategoria nie jest zmieniana. Usuwanie zdjęć i wideo wymaga `listings_d` (nie używamy).
* Odczyt anonimowy listy ofert sekcji: max 100 wyników na sortowanie; zsumuj `created` asc/desc i `price` asc/desc.
* Odpowiedzi PATCH i PUT zawierają nowy stan (`materials`, `value_ids`), więc weryfikację można oprzeć na nich (oszczędza zapytania).
* Po zapisie alt textu raz odpowiedź była ok, a alt się nie zapisał: skrypt weryfikuje po zapisie i powtarza (`U.alt_existing`).
* HTML w opisach i tytułach z API jest zakodowany (`&#39;`): porównuj po `html.unescape`.
* Koszt zapytań na ofertę (typowy): backup 3 (oferta, właściwości, inwentarz) + PATCH, PUT, how_its_made, personalizacja, alty, zdjęcia, 2 wideo, 8 tłumaczeń + weryfikacja 2-3 = ok. 30-40.

## 10. Ustalenia o nazwach i pozostałe rozstrzygnięcia (skrót)

DECYZJE.md sekcje 3, 9a i 14 zawierają pełną listę (Basset Griffon Vendéen, Shetland Sheepdog R334 ze zdrobnieniem Sheltie, Scottish Sheep Dog = Collie Rough, Norwegian Forest Cat R174, Dragon Li R259, Labrador Retriever R002, Amstaff R027, Dobermann, Greyhound i Whippet = ta sama statuetka w dwóch ofertach itd.). Gdy w nowej grupie pojawia się nazwa spoza `Rasy.xlsx`: zgłoś (nie zgaduj), a wiersz dodaj do arkusza dopiero na polecenie właścicielki, ze statusem "propozycja (do sprawdzenia)" i dopisaniem do `data/nick_klasyfikacja.csv`, gdy ma zdrobnienie.

## 11. Błędy z przeszłości i jak ich uniknąć (lista kontrolna przed zapisem)

1. Stałe skopiowane ze starego skryptu (np. plik filmu psi zamiast kociego): przejrzyj stałe, porównaj nazwy plików w planie z poleceniem, sprawdź nazwy filmów w logu po teście.
2. Przypisanie oferty do złej grupy lub typu (analiza pomyłkowo dotyczyła tablic zamiast płyt): przed analizą potwierdź z właścicielką przykładową ofertę i sekcję.
3. Powtórzone słowa w tytule (dog, for) i zdania o tym samym elemencie dwa razy w akapicie: kontrola w `check()`.
4. Rasa z prefiksem w polskim ("Kot abisyński"): używaj formy "(rasa: {B})".
5. Gender i rodzaj w językach z deklinacją (DE "für Ihre Katze", IT/ES/PT/FR inne końcówki): przeglądaj tytuły i zdania A po zamianie gatunku.
6. Limity: pytanie personalizacji ≤45 zn., etykieta ≤20 zn.; tagi ≤20 zn.; tytuł ≤140 zn.
7. Okno 24 h: nie zaczynaj dużej partii bez sprawdzenia licznika; partia ma się mieścić do 9000.
8. Dwukrotny zapis tej samej oferty: `is_done` + kroki w logu; nie usuwaj logów.
9. Wymiary w arkuszu a na zdjęciu: sprawdzaj każdą ofertę wzrokowo, rozbieżności zgłaszaj.
10. Zakaz usuwania: przy konieczności usunięcia poproś właścicielkę o ręczne usunięcie.
11. Statusy w Rasy.xlsx: nie zatwierdzaj tłumaczeń bez potwierdzenia.
12. Sekrety: nigdy w logach, planach, commitach (przed commitem `grep` po plikach).

## 12. Co robi ręcznie właścicielka (nie ruszaj, nie obiecuj)

SKU, GPSR (producent i bezpieczeństwo), shopping basket summary, publikacja nowych ofert, ręczne usuwanie ofert/zdjęć/filmów, dostarczanie plików filmów (na gałąź `claude/stoic-edison-coahbl`), zdjęć i arkuszy wymiarów, wiersze do `Rasy.xlsx` (gdy sama dodaje), kontrola próbek po każdej partii, weryfikacja polskich tekstów, uzupełnianie ustawień środowiska (sekrety, domeny).

## 13. Lista pytań do właścicielki przy nowym typie produktu

1. Przykładowa oferta typu, sekcja/zakres (które oferty wchodzą, które pomijamy, czy dotyczy psów/kotów/koni).
2. Folder wideo i zdjęć (adres), film 1 (plik na gałęzi?), film 2 (z brandem czy bez), ile filmów.
3. Zdjęcia: czy zostają bez zmian, czy coś dodajemy (jakie, na jakim miejscu, jaki alt), czy dodajemy "oryginał bez edycji" jako ostatnie.
4. Fakty o produkcie: wymiary (arkusz? zgodność ze zdjęciem?), materiał (tekstowy i z listy), pojemność, kolor grawerunku, cytat domyślny, czy personalizacja i jaka (pola, limity, wymagane/dobrowolne).
5. Czy produkt jest 3D czy płaski (słownictwo: bust/relief/plaque), czy dotyczy go zasada o brązie.
6. Przeznaczenie i ton (pamiątka żałobna, dekoracja, nagroda, prezent): dobór banków B i sekcji stałych (nazwy akapitów).
7. Skróty i niejasne nazwy ras z tytułów, odmiany (sierść, uszy), duplikaty ofert, oferty do pominięcia.
8. Czy zostają: cena, kategoria, "Home style", sekcja; czy "who made = collective".
9. Kolejność i podział na partie, test na której ofercie (domyślnie najniższe wyświetlenia), pilot z grupą kontrolną (dotąd pomijany).
10. Wersja dla kotów/koni: czy wolno wygenerować z wersji dla psów przez zamianę słów (z przeglądem zdań).
