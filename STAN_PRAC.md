# Stan prac (aktualizowany na koniec sesji; czytaj razem z DECYZJE.md i CLAUDE.md)

Ostatnia aktualizacja: 26.10.2026. Zakres: płytki ceramiczne "with a Photo" (299 ofert do optymalizacji).

## Gotowe
* Mapa ofert i folderów: `plans/mapa_koncowa.csv` (kolumny: źródło w eksporcie, gatunek, rasa z kolumny C, `rasa_id`, folder, EAN, decyzja OPTYMALIZUJ lub POMIŃ). Skrypty w `scripts/`.
* Szablony (EN zatwierdzone): `templates/opis_plytka_*.md`, `templates/tytuly_tagi_plytka.md`. Tłumaczenia wszystkich 8 języków zatwierdzone przez właścicielkę 26.10.2026 (bez kontroli natywnej; portugalski europejski): `templates/tlumaczenie_<kod>_plytka.md`, testy `plans/test_sfinks_678653467_<KOD>.md`, dane w `scripts/translations.py` i `scripts/translations_more.py`.
* Filmy (zatwierdzone): `video/video-ceramic-plaques-anita.mp4` (płytki ceramiczne) i `video/video-urn-dogs-anita.mp4` (urny dla psów). Skrypt dla urn: `video/src/render_urn.py <dog|cat|horse> WYJŚCIE.mp4`, grafiki w `video/src/assets_urn/<gatunek>/` (`<gatunek>-1.jpg` kolor z tłem, `-2` bez tła, `-3` szkic). Urny kotów i koni zatwierdzone: `video/video-urn-cats-anita.mp4`, `video/video-urn-horses-anita.mp4`. Film z dużą urną (koń, 3 zdjęcia 25/26/27): `video/video-big-urn-horses-anita.mp4`, zatwierdzony; skrypt `video/src/render_big_urn.py horse WYJŚCIE.mp4`, grafiki w `video/src/assets_big_urn/horse/`; plansza końcowa 50 breeds. Na planszy końcowej filmów urn: 200 breeds dla psów, 50 dla kotów i koni. Zdjęcie nieedytowane: `media/plytki_with_photo/original.jpg`.
* Plan testu na jednej ofercie (Sphynx, listing 678653467): `plans/test_sfinks_678653467.md` oraz wersje we wszystkich 8 językach.
* Generatory tytułu, opisu i tagów: `scripts/generators.py` (ziarno = listing ID).
* Rasa Jagdterrier dodana do `data/Rasy.xlsx` (R331). Reguły dopasowania nazw: DECYZJE.md, sekcja 9a.

## Zablokowane: dostęp do prywatnych funkcji API Etsy z sesji w chmurze
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
