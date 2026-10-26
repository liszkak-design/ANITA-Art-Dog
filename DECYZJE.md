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
* **Synonimy i zdrobnienia w opisie (tylko angielski i polski, tylko z kolumny E i kolumny K):** pełna nazwa rasy w pierwszym zdaniu (wyjątek: zdanie A może składać się tylko ze zdrobnienia, wtedy pełna nazwa rasy jest w tytule i w sekcji IN SHORT, decyzja 26.10.2026); zdrobnienie może wystąpić już w pierwszym zdaniu pierwszego akapitu i nie musi stać razem z nazwą rasy (może być w zdaniu samo), łącznie raz lub dwa razy w pierwszym akapicie (zmiana reguły 26.10.2026). Jedno zdanie nie zawiera pełnej nazwy rasy dwa razy. Nie w tytule i nie w tagach. Rasy bez wariantu w kolumnie E nie dostają zdrobnienia. Zdrobnienie nie może brzmieć sztucznie przy żałobie. Przykład właścicielki (ilustracja, nie szablon): "This urn will proudly serve as a final resting place for your beloved French Bulldog. It's elegant and solid. Your Frenchie's ashes will fit and there will be enough space to keep some other souvenirs like the favorite toy."
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
  * Wirehaired, Longhaired, Shorthaired, Smooth, Fohlen i podobne w nazwach folderów to cecha (długość lub rodzaj sierści, wiek), nie osobna rasa, jak przy Chihuahua i Dachshund. Dlatego: Wirehaired Vizsla = Vizsla, German Longhaired Pointer = German Pointer, Wirehaired Dachshund i Smooth Fox Terrier = Dachshund i Fox Terrier, Kurilian Bobtail Longhaired i Selkirk Rex Longhaired lub Shorthaired = Kurilian Bobtail i Selkirk Rex, Haflinger Fohlen = Haflinger.
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
