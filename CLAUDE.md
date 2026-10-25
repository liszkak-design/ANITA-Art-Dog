# Projekt: audyt i optymalizacja SEO ofert w sklepie Etsy (Art-Dog)

Użytkowniczka pisze po polsku. Odpowiadaj po polsku, konkretnie. Teksty ofert piszesz po angielsku (potem tłumaczenia), chyba że poproszę inaczej.

**Na początku każdej sesji przeczytaj `DECYZJE.md`.** Zawiera ustalone reguły treści, reguły nazw ras, zapisy w tytułach, zdjęcia i wideo oraz sprawy otwarte. Gdy `DECYZJE.md` jest sprzeczny z danymi z Etsy, obowiązuje `DECYZJE.md`.

## Kontekst

* Sklep sprzedaje pamiątki po zmarłych zwierzętach (urny, statuetki, tabliczki nagrobne). Ton: spokojny, empatyczny, bez nachalności i haseł typu "kup teraz". Klient jest w żałobie.
* Ok. 2300 działających ofert + ok. 200 nowych. Ok. 40 typów produktów. Oferty seryjne: ten sam produkt, różne rasy.
* Oferty po angielsku. Główne rynki: USA i UK, dużo Niemiec i Holandii, czasem Francja.
* Statuetki z brązu i urny ze statuetką/grawerem dają ok. 81% przychodu. Te oferty zmieniamy na końcu i ostrożnie.
* Dane w repozytorium: `data/Rasy.xlsx` (nadrzędny plik nazw ras, osób i tłumaczeń), `data/EtsyListingsDownload.csv`, `data/EtsyListingsDownload1.csv` (eksport ofert, 2304), `data/EtsySoldOrderItems2025-2026.csv` (sprzedaż), `Audyt\_Etsy\_ArtDog.xlsx` (audyt). Nazwy ras i tłumaczenia bierz tylko z `Rasy.xlsx`, nie z tekstów ofert w Etsy. 

## Zasady bezwzględne

1. Domyślnie tryb próbny (dry-run): skrypty zapisują planowane zmiany do `plans/\*.csv` i niczego nie wysyłają do Etsy. Zapis tylko z flagą `--apply` i tylko po wyraźnym "tak" użytkowniczki w czacie dla konkretnej partii.
2. Nigdy nie usuwaj (ofert, zdjęć, personalizacji, tłumaczeń, wideo) bez osobnej, wyraźnej zgody dla konkretnej operacji. Nie proś o uprawnienie `listings\_d`.
3. Nigdy nie wypisuj w czacie ani nie commituj: kluczy, Shared Secret, tokenów, verifierów PKCE. Sekrety i tokeny tylko w `.secrets/` (w .gitignore). Przed każdym commitem sprawdź, że w plikach nie ma tokenów.
4. Przed zmianą istniejącej oferty zapisz jej stan w `backup/<listing\_id>\_<data>.json` (tytuł, opis, tagi, materiały, personalizacja, zdjęcia z kolejnością i alt textem, wideo).
5. Partie maksymalnie po 50 ofert. Po każdej partii: log w `logs/` (id oferty, pole, wartość przed, po, status, czas) i prośba o sprawdzenie próbki w Etsy, zanim ruszy następna partia.
6. Skrypty muszą dać się wznowić (pomijają wykonane pozycje według logu) i obsługiwać błędy i limity API bez zgadywania.
7. Limity API: 10 zapytań/s i 10 000/dobę. Licz zapytania w logu i przerwij przy 8 000 danego dnia.
8. Nie wymyślaj danych o produktach (wymiary, pojemność, materiał, terminy, ceny, cła, wysyłka). Braki zgłoś jako pytanie. Nie zgaduj rasy ze zdjęcia, nazwy rasy ani tłumaczeń: braki w `Rasy.xlsx` zgłoś na liście. Jeśli w kontekście oferty tłumaczenie rasy z `Rasy.xlsx` wydaje ci się nie prawidłowe zgłoś jako pytanie.
9. Nie uruchamiaj kilku zapisów do sklepu równolegle.
10. Nie zmieniaj cen, stanów, profili wysyłki ani statusu aktywności ofert, chyba że użytkowniczka wyraźnie poprosi.
11. Nie ustawiaj statusów "zatwierdzone" ani "zweryfikowane" w `Rasy.xlsx` bez wyraźnego potwierdzenia użytkowniczki. Tylko polski sprawdza ona. Pozostałe języki nie mają weryfikacji osoby natywnej.

## Zasady treści (szczegóły w DECYZJE.md, punkt 5)

* Tytuł: nazwa rasy z kolumny C `Rasy.xlsx` na początku, potem typ produktu i cechy, do 140 znaków (cel 100-130), bez upychania.
* Tagi: 13, max 20 znaków, bez nazw ras, różnorodne, bez powtórzeń.
* Opis: pierwsze zdanie z pełną nazwą rasy, nie kopiuj tytułu. Pierwszy akapit składaj z zatwierdzonych banków zdań (otwarcie / zastosowanie / zdjęcie klienta), tak żeby oferty nie były kopią z podmienioną rasą (szczegóły w `templates/`). Zdrobnienia tylko z kolumny E, w dalszym zdaniu, raz lub dwa razy.
* Alt text: opisowy, zgodny z tym, co widać, rasa jak w tytule oferty. Niezgodność zdjęcia z rasą oznacz do sprawdzenia.
* Tłumaczenia: 8 języków (nl, fr, de, it, pl, pt, es, sv). Tłumacz szablony i słownik, nie każdą ofertę. Długość tagu sprawdzaj i zgłaszaj, nie obcinaj.
* Zapisy typu mare, stallion, mother with puppies, hanging, big/smaller, cropped to cechy produktu, nie rasy (arkusz "Opisy statuetek").

## Sieć

* Poziom sieci Custom. Dozwolone domeny: `api.etsy.com` (przez sekret sieciowy), `i.etsystatic.com` (zdjęcia ofert), `www.artdog.com.pl` (wideo i zdjęcia produktów, do dopisania w ustawieniach środowiska). Nie próbuj łączyć się z innymi domenami ani obchodzić blokad. Jeśli potrzebny jest dostęp do innej domeny zgłoś to.
* Zdjęcia i wideo: struktura folderów i zasady dopasowania po EAN są w `DECYZJE.md`, punkt 6.

## API Etsy (Open API v3)

* Każde żądanie wymaga nagłówka `x-api-key`. W tym środowisku (keystring:shared\_secret) dodaje go proxy sieciowe. Shared Secret nie jest dla Ciebie dostępny i nie wolno go szukać ani wpisywać.
* Keystring (`client\_id` do OAuth) jest w zmiennej `ETSY\_KEYSTRING`. Używaj go tylko do adresu autoryzacji i wymiany kodu na token. Nie wypisuj go w czacie.
* Operacje na ofertach wymagają tokenu OAuth (Bearer). Zakres: najpierw tylko odczyt (`listings\_r`, `shops\_r`), zapis (`listings\_w`) dopiero po kopii zapasowej i teście na jednej ofercie.
* Potwierdzone w dokumentacji: `createListingTranslation`, `updateListingTranslation` (tytuł, opis, tagi, 8 języków), `uploadListingImage` (pole `alt\_text`, opcja nadpisania), `uploadListingVideo` (do 2 na ofertę), `updateListing`, edycja i usuwanie personalizacji.
* Niepotwierdzone, do testu na jednej ofercie: czy nadpisanie zdjęcia przy zmianie `alt\_text` zachowuje kolejność i miniaturę. Do czasu testu nie zmieniaj alt textów masowo.

## Autoryzacja OAuth w chmurze

1. Wygeneruj PKCE (verifier, challenge) i `state`; zapisz verifier i state w `.secrets/`. Wypisz tylko adres autoryzacji `https://www.etsy.com/oauth/connect` z parametrami (`client\_id` = `ETSY\_KEYSTRING`).
2. Użytkowniczka otwiera adres w swojej przeglądarce, loguje się (2FA), zatwierdza i wkleja w czacie cały adres z paska po przekierowaniu (zawiera `code` i `state`).
3. Sprawdź `state`, wymień kod na token (`POST https://api.etsy.com/v3/public/oauth/token`), zapisz tokeny w `.secrets/`. Nie wypisuj ich.
4. Token dostępu ważny ok. 1 h, odświeżający ok. 90 dni. Po utracie sesji (VM odłączona) autoryzację trzeba powtórzyć.
5. Adres przekierowania identyczny z zarejestrowanym w aplikacji Etsy (https, wielkość liter, bez dodatkowego ukośnika).

## Kolejność prac

1. Test połączenia z API (bez autoryzacji użytkowniczki, jedno wywołanie).
2. Wczytaj `Rasy.xlsx` i porównaj z tytułami ofert z eksportu. Zapisz raport do `plans/rasy\_raport.csv`: rasy z ofert bez wiersza w `Rasy.xlsx`, niejednoznaczne zapisy (Pointer, German Pointer), rozbieżności. Niczego nie zmieniaj w pliku `Rasy.xlsx`.
3. Autoryzacja tylko do odczytu → pełna kopia zapasowa ofert w `backup/` (tylko odczyt).
4. Test zapisu na JEDNEJ ofercie o niskiej sprzedaży (tytuł, tagi, opis, alt text jednego zdjęcia, jedno tłumaczenie) i sprawdzenie w Etsy przez użytkowniczkę.
5. Wzorce (tytuły, tagi, wstępy opisów, alt texty) dla jednego typu produktu → zatwierdzenie.
6. Pilot na 30-40 ofertach z grupą kontrolną bez zmian → pomiar po 4-8 tygodniach.
7. Wdrożenie typ po typie (najpierw niższa sprzedaż, bestsellery na końcu).
8. Tłumaczenia po zatwierdzeniu angielskich wersji i słownika: najpierw 1-2 języki, potem reszta.
9. Nowe oferty (ok. 200) jako szkice, publikacja po akceptacji użytkowniczki.

