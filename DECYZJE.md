# Decyzje projektowe (stan z 24.10.2026)

Ten plik zbiera ustalenia właścicielki sklepu Art-Dog. Obowiązuje razem z `CLAUDE.md`. Gdy ustalenie z tego pliku jest sprzeczne z danymi z Etsy (tytuł, opis, tagi istniejącej oferty), obowiązuje ten plik. Gdy coś jest niejasne albo brakuje danych, Code pyta właścicielkę i niczego nie zgaduje.

## 1\. Pliki i hierarchia źródeł

* `data/Rasy.xlsx` jest nadrzędnym plikiem nazw ras, rodzajów, osób i tłumaczeń (8 języków). Arkusze: Instrukcja, Rasy, Do decyzji, Słowa stałe, Warianty w tytułach (archiwum audytu, nazwy kanoniczne mogą być nieaktualne), Do klasyfikacji, Opisy statuetek.
* Kolumna C arkusza Rasy = główna angielska nazwa (do tytułu). Kolumna D = pełna nazwa, jeśli C jest skrócona. Kolumna E = jeden angielski wariant do użycia w pierwszym akapicie opisu (pusta = brak wariantu). Kolumna K = polskie nazwy potoczne.
* Nazwy ras i tłumaczenia bierz z `Rasy.xlsx`, nie z istniejących tytułów i opisów w Etsy (mogą zawierać błędy). Fakty o produktach (wymiary, pojemność, materiał, terminy, cła, wysyłka) mogą pochodzić tylko od właścicielki. Etsy jest tylko źródłem danych wejściowych do kontroli.
* Rasy, których nie ma w `Rasy.xlsx`: zgłoś na liście braków, nie zgaduj nazwy ani tłumaczeń. Jeśli w kontekście oferty tłumaczenie rasy z `Rasy.xlsx` wydaje ci się nie prawidłowe zgłoś jako pytanie.
* Dane pomocnicze: `data/EtsyListingsDownload.csv`, `data/EtsyListingsDownload1.csv` (2304 oferty), `data/EtsySoldOrderItems2025-2026.csv`, `Audyt\_Etsy\_ArtDog.xlsx`. W eksporcie ofert kolumna SKU jest pusta, więc nie ma w nim numerów EAN.

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
* Zawsze do sprawdzenia przez właścicielkę ze zdjęciem produktu (Code nie przypisuje rasy sam): Pointer (możliwe English Pointer), German Pointer (German Wirehaired Pointer lub German Shorthaired Pointer). Wiersze English Pointer i German Shorthaired Pointer usunięto z arkusza (brak ofert). Jeśli zdjęcie wskaże taką rasę, trzeba najpierw dodać wiersz.

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
* **Tagi:** 13 tagów, max 20 znaków każdy (ze spacjami). Bez nazw ras (decyzja właścicielki). Różnorodne, bez powtarzania fraz, bez powielania kategorii i atrybutów. Liczba mnoga nie wymaga osobnego tagu.
* **Opis:** pierwsze zdanie zawiera pełną nazwę rasy (kol. C) z pominięciem dopisków jak Welsh albo Short-haired, i zwięzłe, naturalne wprowadzenie. Nie kopiuj tytułu. Pierwszy akapit nie może być kopią z podmienioną rasą, ale nie musi różnić się treścią: składamy go z zatwierdzonych przez właścicielkę banków zdań (otwarcie / zastosowanie / zdjęcie klienta), wariant dobierany po ID oferty, sąsiednie oferty różnią się w co najmniej dwóch slotach. Sekcje stałe (IN SHORT, PERSONALISATION, INTERNATIONAL ORDERS itd.) są identyczne w ofertach danego typu produktu. Szablony i banki: `templates/`.
* **Synonimy i zdrobnienia w opisie (tylko angielski i polski, tylko z kolumny E i kolumny K):** pełna nazwa w pierwszym zdaniu, zdrobnienie dopiero w dalszym (drugie lub trzecie zdanie), raz lub dwa razy. Nie w tytule i nie w tagach. Rasy bez wariantu w kolumnie E nie dostają zdrobnienia. Zdrobnienie nie może brzmieć sztucznie przy żałobie. Przykład właścicielki (ilustracja, nie szablon): "This urn will proudly serve as a final resting place for your beloved French Bulldog. It's elegant and solid. Your Frenchie's ashes will fit and there will be enough space to keep some other souvenirs like the favorite toy."
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

