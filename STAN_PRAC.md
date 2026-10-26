# Stan prac (aktualizowany na koniec sesji; czytaj razem z DECYZJE.md i CLAUDE.md)

Ostatnia aktualizacja: 26.10.2026 (wieczór, po teście zapisu na Sphynxie). Zakres: płytki ceramiczne "with a Photo" (299 ofert do optymalizacji).

## Gotowe
* Mapa ofert i folderów: `plans/mapa_koncowa.csv` (kolumny: źródło w eksporcie, gatunek, rasa z kolumny C, `rasa_id`, folder, EAN, decyzja OPTYMALIZUJ lub POMIŃ). Skrypty w `scripts/`.
* Szablony (EN zatwierdzone): `templates/opis_plytka_*.md`, `templates/tytuly_tagi_plytka.md`. Tłumaczenia wszystkich 8 języków zatwierdzone przez właścicielkę 26.10.2026 (bez kontroli natywnej; portugalski europejski): `templates/tlumaczenie_<kod>_plytka.md`, testy `plans/test_sfinks_678653467_<KOD>.md`, dane w `scripts/translations.py` i `scripts/translations_more.py`.
* Film: `video/video-ceramic-plaques-anita.mp4` (zatwierdzony). Zdjęcie nieedytowane: `media/plytki_with_photo/original.jpg`.
* Plan testu na jednej ofercie (Sphynx, listing 678653467): `plans/test_sfinks_678653467.md` oraz wersje we wszystkich 8 językach.
* Generatory tytułu, opisu i tagów: `scripts/generators.py` (ziarno = listing ID).
* Rasa Jagdterrier dodana do `data/Rasy.xlsx` (R331). Reguły dopasowania nazw: DECYZJE.md, sekcja 9a.

## Test zapisu na Sphynxie (678653467): WYKONANY 26.10.2026
* Skrypt `scripts/apply_test_sphynx.py` (dry-run domyślnie, `--apply` zapisuje), log `logs/zapis_678653467_2026-10-26.jsonl`, kopia przed zmianą `backup/678653467_2026-10-26.json`. Zapisane: tytuł, opis, 13 tagów, materiał, personalizacja (5 pytań), 7 zdjęć z alt textami, film, tłumaczenia 8 języków. Cena 16, stan 50 i status active bez zmian (sprawdzone po zapisie).
* Do sprawdzenia przez właścicielkę w Etsy: kolejność i miniatura zdjęć po nadpisaniu slotu 1, wygląd personalizacji dla kupującego, tłumaczenia, film.
* Pominięte w teście: SKU (zapis tylko przez uploadListingInventory z pełną tablicą products, ryzyko dla ceny i stanu), shopping basket summary (brak pola w API), GPSR, how it's made, occasion (nazwy pól niezweryfikowane).
* Limity z dokumentacji personalizacji: pytanie max 45 zn., etykieta opcji listy max 20 zn. (nie 30), instrukcja max 120. Opcja "Original, background removed" skrócona do "No background". Pole "Name and dates": limit 50 znaków. Dokumentacja: developers.etsy.com/documentation/tutorials/personalization-migration/ (domena dozwolona).
* Poprawki po teście (26.10.2026): "Materials" (lista, property 148789511893) ustawione na Ceramic (value_id 83) przez `PUT .../properties/148789511893` (value_ids=83, values=Ceramic). Okazja już była "Pet loss".
* **"How it's made", ustalone ręcznie przez właścicielkę:** opcja "A member of my shop" odpowiada w API `who_made = collective` (NIE `someone_else`: Etsy odrzuca `someone_else` błędem "you cannot sell this item on Etsy"). `when_made = made_to_order`, `is_supply = false` (już były). `updateListing` wymaga wysłania `who_made`, `when_made` i `is_supply` razem. `production_partner_ids` nie ruszamy (sklep nie ma partnerów produkcyjnych). Dla kolejnych ofert: ustawiać `collective` skryptem, po teście na jednej ofercie.
* **GPSR producent i bezpieczeństwo produktu:** brak pola w API (oferta ma tylko `ecgt_*` gwarancja/serwis). Wypełnia właścicielka ręcznie w Etsy ("Legal and compliance"). Po jej ręcznym dodaniu w danych oferty zmieniło się tylko `ecgt_commercial_guarantee_enabled` (null -> false); samej treści GPSR przez API nie widać, więc nie da się jej zweryfikować ani skopiować do innych ofert skryptem.
* Shopping basket summary: brak pola w API (też w tłumaczeniach: API tłumaczeń ma tylko tytuł, opis, tagi). Do ręcznego uzupełnienia, teksty w `plans/test_sfinks_678653467_<KOD>.md`.
* Backupy tej oferty: `backup/678653467_2026-10-26.json` (pierwotny, przed zmianami) i `backup/678653467_2026-10-26_po_zapisie1.json` (po pierwszym zapisie). Przy kolejnych backupach tej samej oferty używać osobnych nazw (funkcja `backup()` nadpisuje plik z tą samą datą).
* Token OAuth ma teraz zakres listings_w (ważny 1 h); po utracie sesji autoryzację trzeba powtórzyć.

## (Rozwiązane) Zablokowane: dostęp do prywatnych funkcji API Etsy z sesji w chmurze
* Token OAuth (zakres `listings_r shops_r`) udało się uzyskać, ale zapytania z nagłówkiem `Authorization` do endpointów wymagających tokenu kończą się błędem "Access token is required". Proxy sesji w chmurze zarządza nagłówkami dla `api.etsy.com` (sekret sieciowy z `x-api-key`) i nie przepuszcza własnego `Authorization`. Odpowiedź wsparcia: dla jednego hosta można mieć tylko jeden zarządzany sekret, nie ma udokumentowanego przepuszczania drugiego nagłówka.
* Obejście od wsparcia: nie trzymać Etsy w sekretach sieciowych, tylko wysyłać oba nagłówki z kodu. Do zrobienia przez właścicielkę w ustawieniach środowiska: usunąć sekret Etsy, dodać zmienną środowiskową `ETSY_SHARED_SECRET` (obok istniejącej `ETSY_KEYSTRING`), dopisać `api.etsy.com` do dozwolonych domen i otworzyć NOWĄ sesję. Skrypty (`scripts/etsy_api.py`, `scripts/etsy_auth.py`) są gotowe: gdy jest `ETSY_SHARED_SECRET`, same ustawiają `x-api-key` = `keystring:shared_secret`.
* Zasada o Shared Secret w CLAUDE.md jest już zmieniona (zgoda 26.10.2026). W nowej sesji: sprawdź, czy jest `ETSY_SHARED_SECRET` (nie wypisuj wartości), autoryzacja OAuth (odczyt), sprawdzenie `users/me`, kopia zapasowa oferty 678653467 (`scripts/backup_listing.py`), test zapisu na jednej ofercie po zatwierdzeniu.

## Dalej (po odblokowaniu)
1. Kopia zapasowa i test na ofercie Sphynx (tytuł, opis, tagi, materiały: ceramic, 7 zdjęć nadpisane w kolejności 3, 4, 5, 2, 6, 7, original, alt texty, wideo, pola personalizacji, SKU tylko jeśli bezpieczne, tłumaczenie DE), kontrola w Etsy przez właścicielkę.
2. Partie po maks. 50 ofert, log w `logs/`, próbka do sprawdzenia przed następną partią. Licznik zapytań: `logs/api_requests_<data>.log` (stop przy 8000 dziennie).
3. Tłumaczenia pozostałych języków i ich wgranie po zatwierdzeniu.

## Uruchomienie nowej sesji
* Cała praca jest na gałęzi `claude/stoic-edison-coahbl` (to jedyna gałąź na GitHubie, brak gałęzi domyślnej z tymi plikami). Nową sesję trzeba zacząć z tej gałęzi (wskaż ją jako gałąź źródłową).
* Zmienne środowiskowe (w tym `ETSY_SHARED_SECRET`) wczytują się tylko przy starcie sesji. Stara sesja ich nie widzi.
* Pierwsza wiadomość w nowej sesji: "Kontynuujemy test na Sphynxie, przeczytaj STAN_PRAC.md".
