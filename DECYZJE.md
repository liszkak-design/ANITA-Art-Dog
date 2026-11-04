# Decyzje projektowe (stan z 24.10.2026)

Ten plik zbiera ustalenia właścicielki sklepu Art-Dog. Obowiązuje razem z `CLAUDE.md`. Gdy ustalenie z tego pliku jest sprzeczne z danymi z Etsy (tytuł, opis, tagi istniejącej oferty), obowiązuje ten plik. Gdy coś jest niejasne albo brakuje danych, Code pyta właścicielkę i niczego nie zgaduje.

## 1\. Pliki i hierarchia źródeł

* `data/Rasy.xlsx` jest nadrzędnym plikiem nazw ras, rodzajów, osób i tłumaczeń (8 języków). Arkusze: Instrukcja, Rasy, Do decyzji, Słowa stałe, Warianty w tytułach (archiwum audytu, nazwy kanoniczne mogą być nieaktualne), Do klasyfikacji, Opisy statuetek.
* Kolumna C arkusza Rasy = główna angielska nazwa (do tytułu). Kolumna D = pełna nazwa, jeśli C jest skrócona. Kolumna E = jeden angielski wariant do użycia w pierwszym akapicie opisu (pusta = brak wariantu). Kolumna K = polskie nazwy potoczne.
* Nazwy ras i tłumaczenia bierz z `Rasy.xlsx`, nie z istniejących tytułów i opisów w Etsy (mogą zawierać błędy). Fakty o produktach (wymiary, pojemność, materiał, terminy, cła, wysyłka) mogą pochodzić tylko od właścicielki. Etsy jest tylko źródłem danych wejściowych do kontroli.
* Rasy, których nie ma w `Rasy.xlsx`: zgłoś na liście braków, nie zgaduj nazwy ani tłumaczeń. Jeśli w kontekście oferty tłumaczenie rasy z `Rasy.xlsx` wydaje ci się nie prawidłowe zgłoś jako pytanie.
* Dane pomocnicze: `data/EtsyListingsDownload.csv`, `data/EtsyListingsDownload1.csv` (razem 2304 oferty: 2000 + 304), `data/EtsySoldOrderItems2025-2026.csv`, `Audyt\_Etsy\_ArtDog.xlsx`. W eksporcie ofert kolumna SKU jest pusta, więc nie ma w nim numerów EAN.

## 2\. Statusy tłumaczeń

* Tylko polski jest sprawdzany przez właścicielkę. Żaden inny język nie ma weryfikacji osoby natywnej.
* DE, FR, ES dla psów (nazwy z jej arkusza) mają status "zatwierdzone (właścicielka)". To nie jest weryfikacja natywna.
* NL, IT, PT, SV oraz brakujące wpisy w DE, FR, ES i PL to szkice Claude'a ("szkic (Claude, ...)"). Wymagają kontroli. Polskie szkice sprawdza właścicielka, pozostałe osoba natywna.
* Code nie zmienia statusów na "zatwierdzone" ani "zweryfikowane" bez wyraźnego potwierdzenia właścicielki.
* W językach innych niż angielski i polski nie używamy nazw potocznych, tylko nazwy z kolumny "nazwa". Nazwy potoczne są tylko w EN (kol. E) i PL (kol. K).

## 3\. Reguły dla nazw ras

* W angielskim używamy oficjalnej nazwy z arkusza bez słowa "Dog" na końcu (wyjątki zatwierdzone: Bernese Mountain Dog, Portuguese Water Dog, Australian Cattle Dog, Catahoula Leopard Dog i podobne, gdzie wynik byłby niepełny). Efekt jest już w kolumnie C.
* Odmiana sierści jest w tytule: nazwa ogólna rasy z arkusza Rasy plus słowo z arkusza "Słowa stałe" (Dachshund, Chihuahua, Collie, Fox Terrier). W opisie odmiany nie powtarzamy.
* Oferty bez dopisku (np. Springer Spaniel bez "English" lub "Welsh") zostają bez dopisku.
* Dobermann: w kolumnie C jest "Dobermann", a w ofertach często "Doberman". Obowiązuje kolumna C.
* Pozycje rozstrzygnięte:

  * Bulldog = English Bulldog (American Bulldog to osobna rasa).
  * Great Pyrenees = wiersz Pyrenean Mountain Dog. Pyrenean Shepherd = wiersz Pyrenean Sheepdog.
  * Scottish Sheepdog i Shetland Sheepdog (Sheltie) w ofertach = Collie Rough (decyzja właścicielki).
  * Grand Basset Griffon Vendéen i Petit Basset Griffon Vendéen = jedna pozycja Basset Griffon Vendéen. "Basset Vendéen" też. Podobizna głowy lub popiersia pasuje do obu wersji.
  * Dutch Retriever = osobna rasa. Miniature Pinscher dodany jako rasa.
  * Egyptian Cat = Egyptian Mau. Spitz = Japanese Spitz. Staffordshire Terrier = Staffordshire Bull Terrier.
  * Bichon, Setter, Griffon, Cat zostają jako nazwy ogólne. Bay Horse i Retired Race Horse traktujemy jak nazwy ras.
  * Oferty "The New Set Of" to oferty custom pod konkretnego klienta. Nie podlegają optymalizacji.
* Pointery rozstrzygnięte przez właścicielkę 27.10.2026: oferta 664703588 = English Pointer (wiersz R332, szkice tłumaczeń Claude'a), 678557767 = German Wirehaired Pointer, 664742594 = German Longhaired Pointer (wiersz R333, szkice tłumaczeń Claude'a), 664717946 = Pointer bez dopisków (R035). Wiersz German Pointer (R266) zostaje w arkuszu.

## 4\. Zapisy w tytułach ofert, które NIE są nazwami ras

(arkusz "Opisy statuetek" w `Rasy.xlsx`)

* klacz (mare), ogier (stallion), źrebię (foal, Fohlen): płeć lub wiek konia tej samej rasy.
* mother with puppies: statuetka dorosłej suczki karmiącej szczenięta. head on the knee: pies z głową na kolanie.
* sitting, standing, lying: pozycja psa w statuetce.
* hanging: popiersie do powieszenia na ścianie.
* cropped, uncropped: uszy kopiowane lub nie. harlequin: umaszczenie odpowiada malowaniu statuetki.
* big, bigger, smaller, small: osobna oferta z mniejszą lub większą wersją tego samego produktu.
* customized: cecha produktu. macho, power: pomijamy.
* "ashes" w tytule oznacza typ produktu (urna), nie wariant.

## 5\. Zasady treści (po angielsku, tłumaczenia po zatwierdzeniu)

* **Ton:** spokojny, szanujący żałobę. Bez haseł sprzedażowych, bez obietnic zdrowotnych i przesady.
* **Tytuł:** nazwa rasy z kolumny C na początku, potem typ produktu i najważniejsze cechy, do 140 znaków (celujemy w 100-130). Bez upychania słów i powtórzeń.
  * **Na przyszłość, dla kolejnych grup produktów (30.10.2026, wprost z Etsy, "Tips to improve your title"):** rozważ użycie 14 słów lub mniej w tytule. Obowiązuje od następnej grupy; zatwierdzone tytuły płytek, urn z płytką i urn z reliefem nie są zmieniane.
* **Tagi:** 13 tagów, max 20 znaków każdy (ze spacjami). Bez nazw ras (decyzja właścicielki). Różnorodne, bez powtarzania fraz, bez powielania kategorii i atrybutów. Liczba mnoga nie wymaga osobnego tagu.
* **Opis:** pierwsze zdanie zawiera pełną nazwę rasy (kol. C) z pominięciem dopisków jak Welsh albo Short-haired, i zwięzłe, naturalne wprowadzenie. Nie kopiuj tytułu. Pierwszy akapit nie może być kopią z podmienioną rasą, ale nie musi różnić się treścią: składamy go z zatwierdzonych przez właścicielkę banków zdań (otwarcie / zastosowanie / zdjęcie klienta), wariant dobierany po ID oferty, sąsiednie oferty różnią się w co najmniej dwóch slotach. Sekcje stałe (IN SHORT, PERSONALISATION, INTERNATIONAL ORDERS itd.) są identyczne w ofertach danego typu produktu. Szablony i banki: `templates/`.
* **Synonimy i zdrobnienia w opisie (tylko angielski i polski, tylko z kolumny E i kolumny K):** pełna nazwa rasy w pierwszym zdaniu (wyjątek: zdanie A może składać się tylko ze zdrobnienia, wtedy pełna nazwa rasy jest w tytule i w sekcji IN SHORT, decyzja 26.10.2026); zdrobnienie może wystąpić już w pierwszym zdaniu pierwszego akapitu i nie musi stać razem z nazwą rasy (może być w zdaniu samo), łącznie raz lub dwa razy w pierwszym akapicie (zmiana reguły 26.10.2026). Jedno zdanie nie zawiera pełnej nazwy rasy dwa razy. Nie w tytule i nie w tagach. Rasy bez wariantu w kolumnie E nie dostają zdrobnienia. Wpisy w kolumnie E, które są synonimami (inna nazwa rasy, nazwa alternatywna, wariant pisowni), nie dostają zdań ze zdrobnieniem, ale synonim ma być w pierwszym akapicie opisu (może stać w zdaniu zamiast nazwy rasy), żeby oferta była znajdowana po mniej znanych nazwach ras; klasyfikacja w `data/nick_klasyfikacja.csv` (18 zdrobnień, 27 synonimów; decyzja 26.10.2026). Zdrobnienie nie może brzmieć sztucznie przy żałobie. Przykład właścicielki (ilustracja, nie szablon): "This urn will proudly serve as a final resting place for your beloved French Bulldog. It's elegant and solid. Your Frenchie's ashes will fit and there will be enough space to keep some other souvenirs like the favorite toy."
* **Alt text:** krótki, opisowy, zgodny z tym, co widać na zdjęciu. Nie zgaduj rasy ze zdjęcia: rasa z tytułu lub danych oferty. Jeśli zdjęcie wygląda na niezgodne z rasą, oznacz do sprawdzenia, nie poprawiaj.
* **Tłumaczenia:** 8 języków (nl, fr, de, it, pl, pt, es, sv). Tłumacz szablony i słownik, nie każdą ofertę z osobna. Sprawdzaj długość każdego tagu (max 20 znaków) i zgłaszaj za długie, nie obcinaj.
* Brak danych o produkcie (wymiary, pojemność, termin, cło): zgłoś jako pytanie, nie wymyślaj.

## 6\. Zdjęcia i wideo

* Wideo: `https://www.artdog.com.pl/VIDEO/`. Zdjęcia: `https://www.artdog.com.pl/allegro/zebraneEAN/`. Domena `www.artdog.com.pl` musi być dopisana do dozwolonych domen środowiska.
* Struktura wideo: folder typu produktu (np. płytki ceramiczne) → podfoldery kot, koń, pies → dla każdego produktu podfoldery z jedną rasą. Nazwa podfolderu zawiera nazwę rasy i numer EAN. Nazwa rasy w folderze może być angielska, polska, niemiecka lub z błędem.
* Zdjęcia znajduje się po numerze EAN w katalogu zdjęć. Dopasowanie folderu do oferty idzie przez nazwę rasy (przez `Rasy.xlsx`) i EAN. Gdy dopasowanie jest niepewne lub zdjęcie nie pasuje do rasy z oferty, Code zgłasza to do sprawdzenia i niczego nie zmienia.
* Właścicielka wskaże, który folder typu produktu ma być opracowany w danej partii.

## 7\. Przebieg prac i kontrola

* Kolejność: kopia zapasowa → test zapisu na jednej ofercie o niskiej sprzedaży → wzorce dla jednego typu produktu (zatwierdzenie) → pilot na 30-40 ofertach z grupą kontrolną → wdrożenie typ po typie → tłumaczenia po zatwierdzeniu angielskiego i słownika → nowe oferty (ok. 200) jako szkice.
* Najpierw typy o niższej sprzedaży. Statuetki z brązu i urny ze statuetką lub grawerem dają ok. 81% przychodu, więc zmieniamy je na końcu i ostrożnie.
* Partie po maks. 50 ofert, log po każdej partii i sprawdzenie próbki przez właścicielkę przed następną. Zapisy tylko po wyraźnym "tak" właścicielki.

## 8\. Sprawy otwarte (nie są jeszcze regułami)

* **Nowe zasady Etsy z 22.10.2026** ("Bot-generated listings without any human involvement aren't allowed"; wymóg co najmniej jednego niemodyfikowanego zdjęcia prawdziwego przedmiotu): zgodność naszego procesu nieomówiona do końca. Możliwe zabezpieczenia do rozważenia: zatwierdzanie każdej nowej oferty osobno, log zatwierdzeń, treść różnicowana realnymi cechami, kontrola natywna tłumaczeń, brak edycji zdjęć przez AI. 
* Test na jednej ofercie: czy nadpisanie zdjęcia przy zmianie alt textu zachowuje kolejność i miniaturę (do tego czasu alt textów nie zmieniamy masowo).
* Plik `Typy\_produktow.xlsx` z faktami o ok. 40 typach produktów jeszcze nie istnieje. Dane musi wpisać właścicielka.
* Format nagłówka `x-api-key` (keystring:shared\_secret) i adres przekierowania OAuth to założenia do potwierdzenia przy pierwszym teście.
* Ok. 200 nowych ofert: wystawiane jako szkice, publikacja po akceptacji właścicielki.


## 9\. Płytki ceramiczne "with a Photo" (ustalenia z 25.10.2026)

* Zakres: tylko 302 oferty płytek "with a Photo" (1 zdjęcie, cena 16, bez wariantów). Rodzinę "with Graphics" (145 ofert) odkładamy.
* Szukanie folderów: zbiorczy folder wideo `https://www.artdog.com.pl/VIDEO/VII%20tura/38.%20SUBLIMACJA/6.%20Plyta%20Nagrobna/`, w nim podfoldery typu `195. Plyta nagro KOTY`, `196. Plyta nagro PSY` itd. Z nazwy folderu rasy bierzemy EAN, zdjęcia są w `https://www.artdog.com.pl/allegro/zebraneEAN/<EAN>/`.
* Zdjęcia w ofercie, kolejność: `3.jpg` (główne), `4.jpg`, `5.jpg`, `2.jpg`, `6.jpg`, `7.jpg`, na końcu `original.jpg` (nieedytowane zdjęcie prawdziwej płytki, jedno dla wszystkich ofert z tej grupy, plik `media/plytki_with_photo/original.jpg`). Pliki `1.jpg` i `Druk.jpg` nie są używane. Zdjęć nie edytujemy. Zdjęcie `6.jpg` (płytka na urnie) to przykład zastosowania, urna nie jest częścią oferty.
* Właścicielka zgodziła się na usunięcie istniejącego zdjęcia w tych ofertach i zastąpienie go nowym. Wymianę robimy przez nadpisanie slotów (`uploadListingImage`), bez uprawnienia `listings_d`. Zgoda dotyczy tylko zdjęć w ofertach z tej grupy.
* Wideo: film o personalizacji (`video/video-ceramic-plaques-anita.mp4`). Żadna oferta nie powinna mieć jeszcze wideo. Jeśli któraś ma, zgłosić i nie dodawać.
* Pilot z grupą kontrolną: odpuszczony. Po teście na jednej ofercie idziemy w partiach po maks. 50.
* SKU = EAN: dodajemy tylko, jeśli API pozwala zapisać samo SKU bez ryzyka dla ceny i stanu. W razie wątpliwości pomijamy i zgłaszamy.
* "Shopping basket summary": "Ceramic memorial plaque" (tłumaczymy na 8 języków).
* Szablony opisów: `templates/opis_plytka_kot.md`, `opis_plytka_pies.md`, `opis_plytka_kon.md` (zatwierdzone). Plik `data/key_words.txt` (z `data/key_words.pdf`) to tylko sugestia do tagów: 180 z 317 fraz ma więcej niż 20 znaków.

### 9a\. Dopasowanie nazw z ofert i folderów do Rasy.xlsx (reguły do wszystkich typów produktów)

* Nazwa w tytule oferty lub folderu serwera, której nie ma w kolumnie C, jest dopasowywana wg poniższych rozstrzygnięć. Obowiązuje zawsze nazwa z kolumny C.
  * Akita Inu = Akita. Russian Tsvetnaya Bolonka = Bolonka. Catahoula Cur = Catahoula Leopard Dog. Laekenois Dog = Laekenois Belgian Shepherd. Scottish Deerhound = Deerhound. Basset (folder) i Basset Hound = Basset Hound. Tosa (folder) = Tosa Inu. Pyrenean Shepherd = Pyrenean Sheepdog.
  * Schnauzer Cropped = Schnauzer (Cropped to cecha produktu, nie rasa).
  * Wirehaired, Longhaired, Shorthaired, Smooth, Fohlen i podobne w nazwach folderów to cecha (długość lub rodzaj sierści, wiek), nie osobna rasa, jak przy Chihuahua i Dachshund. Dlatego: Wirehaired Vizsla = Vizsla, German Longhaired Pointer = osobna rasa (R333, od 27.10.2026; wcześniej: German Pointer), Wirehaired Dachshund i Smooth Fox Terrier = Dachshund i Fox Terrier, Kurilian Bobtail Longhaired i Selkirk Rex Longhaired lub Shorthaired = Kurilian Bobtail i Selkirk Rex, Haflinger Fohlen = Haflinger.
  * Percheron to osobna rasa (R222), nie Belgian Horse.
  * Jagdterrier dodany do `Rasy.xlsx` jako R331 (tłumaczenia to szkice Claude'a, do sprawdzenia).
* Dwie oferty tej samej rasy z różnymi grafikami (np. Boxer z uszami przyciętymi i naturalnymi) dopasowujemy do dwóch folderów porównując zdjęcie oferty z `1.jpg` w folderze (`scripts/match_by_image.py`). To tylko dopasowanie oferty do folderu, rasy ze zdjęcia nie ustalamy.
* Gdy tytuł oferty nie pasuje do zdjęcia, właścicielka rozstrzyga rasę. Oferta "Fox Terrier" (`EtsyListingsDownload.csv:131`) ma zdjęcie Brittany Spaniel, więc optymalizujemy ją jako Brittany Spaniel (poprawiamy rasę w tytule).
* Oferty bez pasującego folderu (Clydesdale `664826022`, Laekenois Dog `678580977`) pomijamy. Duplikaty produktu (dwie oferty Bengal na jednym folderze): optymalizujemy jedną, drugą pomijamy.
* Foldery bez oferty (Cornish Rex, Smooth Fox Terrier): można wystawić nowe oferty.
* Mapa końcowa płytek "with a Photo": `plans/mapa_koncowa.csv` (299 ofert do optymalizacji, 3 pominięte).

## 10\. Tłumaczenia płytek ceramicznych (ustalenia z 26.10.2026)

* Polski szablon płytek (`templates/tlumaczenie_pl_plytka.md`) zatwierdzony przez właścicielkę. Zmiany z jej przeglądu: nagłówek sekcji "PAMIĄTKA PO TWOIM PRZYJACIELU" (zamiast "TRWAŁY HOŁD"), w bankach B bez słów "trwały, trwałe". Po polsku bez zdrobnień z kolumny K. Nazwa rasy w tekście zawsze w mianowniku (bez odmiany).
* Pliki do sprawdzenia dla właścicielki: nagłówki sekcji muszą być wyświetlane w osobnej linii, treść w bloku kodu (jak w planach testu).
* Kolejność tłumaczeń: polski, potem niemiecki i jeden kolejny język, na końcu pozostałe.

### 10a\. Zatwierdzenia tłumaczeń (26.10.2026)

* Właścicielka zatwierdziła szablony płytek we wszystkich 8 językach (PL, DE, NL, FR, IT, ES, PT, SV). To nie jest weryfikacja natywna. Portugalski: wariant europejski (pónei, Polónia, encomenda).
* Zasada o Shared Secret zmieniona za zgodą właścicielki: patrz CLAUDE.md, sekcja "API Etsy".


## 11\. Ustalenia ogólne z prac po 28.10.2026 (obowiązują we wszystkich nowych grupach)

* **Zgoda na zapis:** tylko "tak, zapisz test/partię N" dla konkretnej partii (też "tak" na pytanie o zapis). Zatwierdzenie tekstów nie jest zgodą na zapis partii. Skrypty czytają zamrożony plan; próbka każdej partii jest sprawdzana przez właścicielkę przed następną.
* **Tytuły nowych grup:** do 14 słów (wyraz z myślnikiem = 1), do 140 znaków, bez powtórzeń słów (zwłaszcza dog i for; podpowiedź Etsy, 03.11.2026), rasa z kolumny C na początku, bez "cold cast bronze", zróżnicowane słowa kluczowe między ofertami. Nigdy "Natural Ears" (tylko "Cropped Ears" przy uszach przyciętych).
* **Język:** w polskim nigdy "trwały/trwałe", "ciche miejsce"; przy datach "daty życia". "bust" tylko dla trójwymiarowych głów (popiersia wiszące); dla płyt i reliefów: relief/bas-relief/płaskorzeźba. Nie "plaque" dla przedmiotów 3D. Zapis "statue", "sculpture", "statuette" dozwolony dla popiersi wiszących (tytuły i tagi). Brąz: sformułowania sugerujące podobieństwo ("cold cast bronze" z objaśnieniem, "bronze-look", "looks like a classic bronze piece") są poprawne; "bronze relief" jako materiał jest nieprawdziwe (02.11.2026). Statuetki odlewane: "designed by hand" (model rzeźbiony ręcznie, forma, odlew), NIE "finished by hand"; ręcznie tylko zamocowanie filcu i haczyka (03.11.2026).
* **Zdjęcia:** domyślnie nie wymieniamy (tylko alt texty do istniejących, rodzaj zdjęcia rozpoznany z obrazu, nie z pozycji). Wyjątek (28.10.2026, urny ze zdjęciem): nadpisanie zdjęcia nr 1 zdjęciem z serwera, bo część ofert miała błędne zdjęcie (wymiana przez nadpisanie slotu, bez `listings_d`). Dodatkowe zdjęcia wskazuje właścicielka, zawsze na końcu; nieedytowane zdjęcie prawdziwego przedmiotu ("Unedited photo of ...") jest ostatnie.
* **Filmy:** max 2. Film 1 zatwierdzony dla typu (gałąź `claude/stoic-edison-coahbl`, `video/video-*-anita.mp4`), film 2 z folderu rasy (zwykle bez `-brand`; w starszych grupach drugi film z brandem, jeśli tak zlecono). Wymiana filmu: właścicielka usuwa ręcznie, potem wgrywamy (przykłady: Sloughi 29.10.2026, urna testowa kotów 674828881 04.11.2026).
* **Personalizacja:** wzory pól per typ w `PRZEKAZANIE_SESJI.md` sekcja 8. Portretu geometrycznego ani kreskówkowego na życzenie nie robimy; klient może przesłać własne zdjęcie (druk w oryginale albo z usuniętym tłem; bez stylu szkicu przy grafikach).
* **Materiały:** wartości tekstowe i z listy Etsy per grupa (patrz niżej i `PRZEKAZANIE_SESJI.md`). **Plywood (04.11.2026):** dopisujemy do materiałów tekstowych i do listy (id 5199) we wszystkich urnach, bez zastępowania obecnych zapisów.
* **Ustawienia ofert:** `who_made = collective`, `when_made = made_to_order`, `is_supply = false`. Cena, stan, status, kategoria, "Home style" bez zmian, chyba że właścicielka zdecyduje (tablice zostają w kategorii Signs, 03.11.2026; popiersia w Home Decor > Statues).
* **Ręcznie robi właścicielka:** SKU (EAN), GPSR, shopping basket summary, publikacja nowych ofert, usuwanie czegokolwiek w Etsy, dostarczanie filmów i plików.
* **Wiersze dodane do `Rasy.xlsx` na polecenie właścicielki:** R331 Jagdterrier, R332 English Pointer, R333 German Longhaired Pointer, R334 Shetland Sheepdog (zdrobnienie Sheltie; 03.11.2026; tłumaczenia to propozycje bez statusu zatwierdzone). Klasyfikacja kol. E: `data/nick_klasyfikacja.csv`.

## 12\. Urny ze zdjęciem (299 ofert, 28-29.10.2026)

* Skrypt `scripts/batch_urny.py`; szablony `templates/urny_propozycja_tekstow.md` (pies), `urny_koty_konie.md`, `urny_tlumaczenie_<język>.md`, `alt_urny_plytka.md`. Materials: Ceramic, Brass, Pine, Birch (tekstowe: wood, brass handles, ceramic plate; od 04.11 dodatkowo plywood). Pojemność 4,5 l, wymiary zewnętrzne 21 x 29 x 22 cm, wnętrze 14 x 21 x 15,5 cm (dla psów, kotów i koni). Cytat domyślny psa i kota: "You left paw prints on my heart"; konia (podkowa): "If love could have saved you, you would have lived forever."
* Zdjęcia: nadpisanie zdjęcia 1 zdjęciem z serwera, alt 2-6 (uchwyt, uchwyt pod kątem, listwa, narożnik, wnętrze), zdjęcie 7 "original" per gatunek (`media/urny_with_photo/`). Film 1 per gatunek (`video-urn-dogs|cats|horses-anita.mp4`), film 2 z folderu rasy.
* Rozstrzygnięcia: 660303860 (duplikat Bedlington) usunięty przez właścicielkę; Boxer 674148773 i Dobermann 660269244: "Cropped Ears"; Amstaff = R027, Mastino Neapolitano = R048, 660383022 = R333, 674161421 = R035; Kurilian Bobtail i Selkirk Rex: słowa długowłosy/krótkowłosy ze "Słowa stałe"; Sloughi 660384830: folder 182 z błędem w nazwie. Nowa oferta dla folderu 155 Laekenois: szkic 4605567054.

## 13\. Urny z reliefem (28 + 154 + 154 ofert, 29.10-01.11.2026)

* **Urny "Custom urn for dog's ashes" z reliefem z zimnego brązu (38 ofert, 139 EUR):** `scripts/batch_relief.py`, `templates/relief_*`; materiały tekstowe: wood, brass handles, cold cast bronze relief (po korekcie "bust" → "relief"); Materials: Brass, Pine, Birch. Korekta brązu: `scripts/korekta_brazu_relief.py` (02.11.2026).
* **Urna z małą posrebrzaną płaskorzeźbą (sekcja "Urn with relief" 25445424, 154 oferty; pominięte 2 "Big Urn for Horse": 1381486535, 1381486029):** `scripts/batch_brelok.py`, `templates/brelok_*`; relief ze stopu cynku i aluminium pokryty srebrem (nie "bronze"); materiały tekstowe: wood, brass handles, silver plated metal relief; Materials: Brass, Pine, Birch, Metal (id 174). Bez wymiarów reliefu, relief nie jest personalizowany; na urnie dwie małe tabliczki (imię, daty) i duża z cytatem; Rough Collie (659836252) zachowuje nazwę Rough Collie; nowe tytuły, opisy i tagi różne od dotychczasowych. Film 1: `video-urn-brelok-dogs-anita.mp4`.
* **Niska urna z posrebrzaną płaskorzeźbą (sekcja "Lower urn with relief", 154 oferty):** `scripts/batch_brelok_niskie.py`, `templates/brelok_niskie_*`; wymiary 21 x 29 x 11 cm, wnętrze 21 x 14 x 5 cm (analogicznie), pojemność ok. 1,5 l, bez mosiężnych uchwytów, rzeźbienia tak; układ tabliczek: górna z cytatem, dolna z imieniem i datami; cytat "You left our lives, but you will never leave our hearts"; materiały tekstowe: wood, silver plated metal relief; Materials: Pine, Birch, Metal; zdjęcie 4 wymienione na `media/urny_brelok_niskie/zdjecie_4.jpg` (nadpisanie rank 4, alt bez zmian); "compact" nie w każdym tytule. Film 1: `video-urn-low-brelok-dogs-anita.mp4`.

## 14\. Płytki i tablice z reliefem, popiersia wiszące (02-03.11.2026)

* **Płytki "plakietki same" (38 ofert, sekcja "Plaques with dog" 25604492):** `scripts/batch_plakietki.py`, `templates/plakietki_*`; relief na płycie, bez personalizacji, bez zmiany zdjęć; tytuł bez "bust" i bez "cold cast bronze"; wymiary jako atrybuty Height/Width/Depth (pierwsza kolumna arkusza = szerokość, druga = wysokość); Afghan Hound szerokość 10; Rottweiler mały 7,5 x 6,5; zalecenie dwuskładnikowego przezroczystego kleju epoksydowego (bez wzmianki o braku kleju w zestawie); Materials: Bronze, Resin. Home style: Art deco ustawia właścicielka.
* **Tablice pamiątkowe "Memorial Board" (38 ofert, sekcja 25604726):** `scripts/batch_deski.py`, `templates/deski_*`; deska MDF 34 x 24 cm (kolor wiśni), relief z cold cast bronze, złota szczotkowana tabliczka z czarnym grawerem; personalizacja: Name (50, wymagane), Dates (50, wymagane), Quote (1024, domyślny "You'll always be here with me, even if you're gone, you'll always have my love, our memory will live on."); materiały tekstowe: cold cast bronze, MDF board, engraving laminate; Materials: Bronze, Resin, Composite; Height 34, Width 24, bez Depth; kategoria Signs; alt 1 z "bronze-look". Nazwy: Mastino Napoletano z synonimem, Staffordshire Bull Terrier, Borzoi, Dachshund Wire-haired (1380916947).
* **Popiersia wiszące "Hanging Statue" (78 ofert, sekcja 25604726, cena 179):** `scripts/batch_hanging.py`, `templates/hanging_*`; cold cast bronze, filc i haczyk z tyłu; bez personalizacji; Materials: Bronze, Resin; wymiary (wys. x szer. x głęb.) z arkusza `data/hanging_wymiary.xlsx` po kontroli ze zdjęciem 2 oferty (decyzje w `plans/hanging_decyzje.json`: przy 11 rozbieżnościach wartości wg zdjęcia lub arkusza podane przez właścicielkę; Greyhound i Whippet to jedna statuetka w dwóch ofertach); zbliżenie haczyka i filcu (`media/hanging/zblizenie_haczyk_filc.jpg`) dodane jako ostatnie zdjęcie tam, gdzie go brakowało (6 ofert miało własne); nazwy: Basset Griffon Vendéen (zamiast Grand Basset), Shetland Sheepdog R334 (zdrobnienie Sheltie), Collie Rough (zamiast Scottish Sheep Dog), Bouvier R085, Pointer bez odmiany; oferta 971393258 usunięta przez właścicielkę; statuetka może wisieć na zewnątrz, kolor może się zmieniać; bez wagi w opisie; tłumaczenia tylko 8 języków (bez ja, ru, en-GB).

## 15\. Płytki i urny z grafiką (30.10-04.11.2026)

* **Urny "with Graphics" psy (100 ofert):** `scripts/batch_grafika.py`, `templates/grafika_*`; płytka z grafiką geometryczną rasy (na życzenie własne zdjęcie w kolorze lub z usuniętym tłem), zdjęcie 7 nieedytowane (`media/urny_graphics/original_geometryczna.jpg`, alt zaczyna się od "Unedited photo of"); personalizacja: Name, Dates (wymagane), Quote (600), Pet photo, "How should we print the photo?"; film 1 `video-urn-graphics-dogs-anita.mp4`. Skróty z tytułów: Amstaff = R027, Labrador = R002, Dachshund Wirehaired = R025 + Wire-haired.
* **Urny "with Graphics" koty (45 ofert, sekcja 25475952):** `scripts/batch_urny_koty_grafika.py`, `templates/urny_koty_grafika_*`; ta sama konstrukcja co dla psów, kreskówkowa grafika kota ("cartoon-style portrait"), zdjęcie 7 `media/urny_graphics/original_kot.jpg`, film 1 `video-urn-graphics-cats-anita.mp4`; "play, cuddles and quiet evenings" zamiast "walks"; Norwegian Forest Cat (R174), Dragon Li (R259).
* **Płytki "with Graphics" psy (100 ofert, sekcja 25604492) i koty (45 ofert, sekcja 25615639):** `scripts/batch_plakietki_grafika.py`, `batch_plakietki_koty.py`, `templates/plakietki_grafika_*`, `plakietki_koty_*`; płytka 10,5 x 7,5 x 0,5 cm; Material z listy Ceramic (materiał tekstowy "ceramic plate" bez zmian), bez wymiarów w atrybutach; personalizacja: Do you want to personalize the plaque? (No, as shown / Yes, personalize it), Your photo (optional), Print style (if own photo): Original photo / No background, Name and dates (optional), Plaque orientation (if own photo); zdjęcia: 2 istniejące (alt) + tył płytki + kolorowy oryginał z cytatem (`media/plakietki_grafika/`); film 1 `video-ceramic-geom-dogs|cats-anita.mp4`, film 2 bez brandu; tag "dog cemetery marker" (dla kotów "cat cemetery marker"), "kondolencje" w puli polskiej; Welsh Corgi = Pembroke Welsh Corgi, Cavalier = Cavalier King Charles Spaniel, Jack Russel = Jack Russell Terrier, Belgian Sheepdog = Belgian Shepherd.

## 16\. Korekta "plywood" w urnach (04.11.2026)

* Zakres: 745 zoptymalizowanych urn (299 ze zdjęciem, 154 z małym reliefem, 154 niskie, 100 z grafiką dla psów, 38 z reliefem z zimnego brązu); urny z grafiką dla kotów mają plywood od początku. Zasada: dopisanie do istniejących wartości (tekstowych po "wood" i z listy Material id 5199), bez zmiany obecnych zapisów. `scripts/plywood_korekta.py plan|apply N --apply [--lid=ID]`, plan `plans/plywood_plan.csv` (15 partii po 50, od najmniej oglądanych). Zapisane partie 1-10; zostały 11-15 (najczęściej oglądane), każda po "tak" i próbce poprzedniej.
