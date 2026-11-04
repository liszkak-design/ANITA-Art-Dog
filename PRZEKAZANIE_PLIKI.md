# Pliki do przeniesienia na nową gałąź i jak to zrobić (stan na 04.11.2026)

Cel: w nowej sesji Claude Code ma po wgraniu tych plików wiedzieć, jak kontynuować optymalizację (instrukcje: `PRZEKAZANIE_SESJI.md`, `CLAUDE.md`, `DECYZJE.md`, `STAN_PRAC.md`) i mieć narzędzia (skrypty, szablony, dane, logi). Źródło: gałąź `claude/adoring-meitner-bvlo8z` repozytorium `liszkak-design/ANITA-Art-Dog` (cała praca), filmy i źródła filmów: gałąź `claude/stoic-edison-coahbl`.

**Zanim cokolwiek zrobisz: nie usuwaj żadnej z tych dwóch gałęzi, dopóki nowa gałąź nie zawiera wszystkiego i nie została sprawdzona (sekcja 5).**

## 1. Pliki konieczne (poziom A, razem ok. 8 MB)

| Ścieżka | Po co |
|---|---|
| `CLAUDE.md` | zasady bezwzględne i kontekst; Claude Code ładuje go automatycznie (musi być w katalogu głównym repozytorium) |
| `PRZEKAZANIE_SESJI.md` | instrukcja pracy dla nowej sesji (playbook, konwencje, API, błędy z przeszłości, pytania do właścicielki) |
| `PRZEKAZANIE_PLIKI.md` | ten plik |
| `DECYZJE.md` | ustalenia właścicielki (reguły treści, nazwy ras, zdjęcia, wideo, decyzje per grupa) |
| `STAN_PRAC.md` | historia i bieżący stan (sekcja "STAN NA 04.11.2026" na górze: tabela grup, skryptów, szablonów) |
| `.gitignore` | wyklucza `.secrets/`, `__pycache__/`, `*.pyc` (NIE zmieniaj) |
| `Audyt_Etsy_ArtDog.xlsx` | audyt (lista typów produktów, sprzedaż) |
| `data/Rasy.xlsx` | nadrzędny plik nazw ras i tłumaczeń (8 języków; wiersze R331 Jagdterrier, R332, R333, R334 Shetland Sheepdog dodane na polecenie właścicielki, status "propozycja") |
| `data/nick_klasyfikacja.csv` | klasyfikacja kolumny E (zdrobnienie/synonim); R334 dopisany |
| `data/EtsyListingsDownload.csv`, `data/EtsyListingsDownload1.csv` | eksport 2304 ofert (nie zawiera ID ofert ani EAN) |
| `data/EtsySoldOrderItems2025-2026.csv` | sprzedaż (wybór kolejności grup) |
| `data/plakietki_wymiary.xlsx`, `data/hanging_wymiary.xlsx`, `data/key_words.txt`, `data/key_words.pdf` | arkusze wymiarów dostarczone przez właścicielkę, sugestie tagów |
| `scripts/*.py` (76 plików) | cały kod: klient API `etsy_api.py`, OAuth `etsy_auth.py`, licznik `api_licznik.py`, moduły wspólne `batch.py`, `batch_urny.py`, `batch_relief.py`, `apply_test_sphynx.py`, skrypty grup (`batch_*.py`), mapowanie (`crawl_*`, `analiza_*`, `*_mapa*.py`, `match_*`), generatory tłumaczeń (`gen_*_tr.py`), korekty (`korekta_*`, `plywood_korekta.py`, `zdjecie7_*`, `zdjecie4_niskie.py`), nowa oferta (`nowa_oferta_urna.py`) |
| `templates/*` (113 plików) | zatwierdzone szablony EN i 8 języków dla wszystkich grup: wzorce do kopiowania przy nowym typie |

## 2. Pliki zalecane (poziom B, razem ok. 70 MB)

| Ścieżka | Po co / skutek braku |
|---|---|
| `logs/zapis_*.jsonl` (1890 plików, 15 MB) | NIEZBĘDNE do pracy skryptów: `is_done()` i wznawianie krok po kroku czytają te logi. Bez nich skrypt uzna oferty za niezrobione i zapisze je drugi raz |
| `logs/partia_*.jsonl`, `logs/api_requests_*.log` (4 MB) | wyniki weryfikacji partii; licznik API okna 24 h (przynajmniej logi z ostatnich 2 dób, inaczej licznik zaniży zużycie i można przekroczyć limit) |
| `backup/*.json` (2042 pliki, 42 MB) | kopie ofert przed zmianą (cofanie zmian, ocena stanu sprzed optymalizacji; skrypt `plywood_korekta.py plan` czyta je do oczekiwanych materiałów) |
| `media/` (11 plików, 5 MB) | zdjęcia przekazane przez właścicielkę (`media/plytki_with_photo/original.jpg`, `urny_with_photo/`, `urny_graphics/original_geometryczna.jpg` i `original_kot.jpg`, `plakietki_grafika/tyl_plytki.jpg` i `oryginal_kolorowe.jpg`, `urny_brelok/`, `urny_brelok_niskie/`, `hanging/zblizenie_haczyk_filc.jpg`) |
| `plans/` mapy i dane stałe (ok. 4 MB) | mapy ofert na foldery EAN, stan żywy, indeksy folderów, decyzje: `plans/*mapa*.csv`, `plans/*stan_zywy.json`, `plans/*foldery_index.csv`, `plans/*decyzje*.json`, `plans/*sekcja_lista.json`, `plans/plywood_plan.csv`, `plans/listing_ids*.csv`, `plans/*plan_optymalizacji.md`, `plans/etsy_materials_lista_tx2844.json`, `plans/plakietki_material_ids.json`, `plans/deski_wlasciwosci_ids.json` |

## 3. Pliki opcjonalne (poziom C, ok. 37 MB)

* `plans/partia_*_dryrun.json` (46 plików, 37 MB) i `plans/partia_*.csv` (44 pliki): zamrożone plany zakończonych partii (dokumentacja co i kiedy zapisano). Nie są potrzebne do dalszej pracy, ale warto zachować w historii gałęzi.
* `plans/podglad_*.html`, `plans/*_kontrola/`, `plans/porownanie_*`, `plans/test_sfinks_*.md`: podglądy i arkusze kontrolne.

## 4. Wideo (osobna gałąź)

Pliki filmów są w gałęzi `claude/stoic-edison-coahbl` w `video/`. Używane filmy 1: `video-ceramic-plaques-anita.mp4` (płytki ze zdjęciem), `video-urn-dogs-anita.mp4`, `video-urn-cats-anita.mp4`, `video-urn-horses-anita.mp4` (urny ze zdjęciem), `video-urn-graphics-dogs-anita.mp4`, `video-urn-graphics-cats-anita.mp4` (urny z grafiką), `video-urn-relief-dogs-anita.mp4`, `video-urn-brelok-dogs-anita.mp4`, `video-urn-low-brelok-dogs-anita.mp4`, `video-ceramic-geom-dogs-anita.mp4`, `video-ceramic-geom-cats-anita.mp4` (płytki z grafiką), `video-big-urn-horses-anita.mp4`. Źródła filmów: `video/src/` (Remotion). Nowe filmy dostarcza właścicielka, zapisując je na tej gałęzi.
W bieżącej gałęzi plik film 1 kopiuje się poleceniem (zawsze po `git fetch`):
```
git fetch origin claude/stoic-edison-coahbl
git checkout origin/claude/stoic-edison-coahbl -- video/<nazwa>.mp4
```
Folder `video/` na gałęzi roboczej zawiera obecnie kopie użytych filmów (52 MB). Do nowej gałęzi kopiuj tylko pliki potrzebne w danej sesji.

## 5. Jak przenieść (polecenia git)

**Wariant 1 (zalecany): nowa sesja pobiera pliki z gałęzi roboczej.** W nowej sesji (repozytorium sklonowane, gałąź sesji np. `claude/<nazwa>`), poproś Claude'a o wykonanie (wszystkie ścieżki istnieją na gałęzi `claude/adoring-meitner-bvlo8z`):
```
git fetch origin claude/adoring-meitner-bvlo8z
git checkout origin/claude/adoring-meitner-bvlo8z -- CLAUDE.md PRZEKAZANIE_SESJI.md PRZEKAZANIE_PLIKI.md DECYZJE.md STAN_PRAC.md .gitignore Audyt_Etsy_ArtDog.xlsx data scripts templates logs backup media plans
git add -A
git commit -m "Przeniesienie plików projektu z gałęzi claude/adoring-meitner-bvlo8z"
git push -u origin <gałąź nowej sesji>
```
Wersja minimalna (bez ciężkich plików poziomu B/C; skutki: patrz sekcja 2): zamiast `logs backup media plans` użyj
```
git checkout origin/claude/adoring-meitner-bvlo8z -- logs media 'plans/*mapa*.csv' 'plans/*stan_zywy.json' 'plans/*foldery_index.csv' 'plans/*decyzje*.json' 'plans/*sekcja_lista.json' plans/plywood_plan.csv
```
(`logs` zawsze razem, bo licznik API i `is_done`). Przy składni z `*` w `git checkout -- <pathspec>` ujmij wzorce w apostrofy.

**Wariant 2: nowa gałąź z całą historią.** Jeśli sesja ma kontynuować tę samą linię historii: `git fetch origin claude/adoring-meitner-bvlo8z && git checkout -B <nowa-gałąź> origin/claude/adoring-meitner-bvlo8z`, potem `git push -u origin <nowa-gałąź>`. Zawiera wszystko (ok. 170 MB w katalogu roboczym) razem z historią commitów.

**Wariant 3: ręczne wgranie przez GitHub (bez Claude'a).** Na stronie repozytorium wybierz gałąź docelową, "Add file" > "Upload files" i przeciągnij katalogi z lokalnej kopii (limit przeglądarki: do 100 plików na raz, plik do 25 MB; dla katalogów `logs` i `backup` z tysiącami plików użyj wariantu 1 lub 2).

**Czego NIE przenosić i nie commitować:** `.secrets/` (tokeny, verifier PKCE: autoryzację OAuth powtarza się w nowej sesji), plików z kluczami lub Shared Secret (nie powinno ich być w żadnym pliku), `__pycache__/`. Przed commitem uruchom kontrolę: `grep -rEl "ETSY_SHARED_SECRET *= *['\"]|access_token\"|refresh_token\"" . --include=*.json --include=*.py --include=*.md --include=*.log` (wynik ma być pusty poza skryptami, które tylko odczytują zmienną środowiskową).

## 6. Kontrola po przeniesieniu (bez zapytań do Etsy)

1. `ls CLAUDE.md PRZEKAZANIE_SESJI.md DECYZJE.md STAN_PRAC.md` oraz `ls scripts | wc -l` (76 plików `.py` + `__pycache__` pomijany) i `ls templates | wc -l` (113).
2. `python3 -I scripts/api_licznik.py` (czyta lokalne logi): licznik zapytań z ostatnich 24 h.
3. `python3 -I scripts/plywood_korekta.py plan` (tylko lokalne dane): ma wypisać `ofert: 745 | partii: 15` i zapisać ten sam plan co dotychczas (plan zawiera także oferty już poprawione; `apply` pomija je po wpisie `plywood_weryfikacja` w logu). Jeśli liczby są inne, brakuje `logs/zapis_*.jsonl` lub `backup/`.
4. `python3 -I scripts/batch_urny_koty_grafika.py raport` (lokalnie): `ofert: 45 | z uwagami: 45`, a każda uwaga to "już zoptymalizowana" (to dowód, że skrypt poprawnie czyta logi `logs/zapis_*.jsonl`; przed zapisem grupy, która jeszcze nie była robiona, oczekuj `z uwagami: 0`).
5. Autoryzacja OAuth (sekcja 2 w `PRZEKAZANIE_SESJI.md`), potem pierwszy odczyt (`GET users/me`) i dopiero praca na ofertach.
6. Sprawdź, że w środowisku są: zmienne `ETSY_KEYSTRING`, `ETSY_SHARED_SECRET` (bez wypisywania wartości) i dozwolone domeny `api.etsy.com`, `i.etsystatic.com`, `www.artdog.com.pl`.

## 7. Lista plików dokumentacji (co w którym jest)

* `CLAUDE.md`: zasady bezwzględne (1-11), konwencje treści, sieć, API, OAuth, kolejność prac.
* `PRZEKAZANIE_SESJI.md`: jak zacząć, środowisko, co zostało, zasady postępowania i zgody, playbook (13 kroków), architektura skryptów, konwencje treści, Etsy API, nazwy ras, błędy z przeszłości, rzeczy ręczne, pytania do właścicielki.
* `PRZEKAZANIE_PLIKI.md`: ten wykaz plików i polecenia przeniesienia.
* `DECYZJE.md`: ustalenia właścicielki (źródła danych, tłumaczenia, nazwy ras, zapisy w tytułach, zasady treści, zdjęcia i wideo, przebieg prac, sprawy otwarte, ustalenia per grupa produktów z sekcji 9-16).
* `STAN_PRAC.md`: stan na 04.11.2026 (tabela grup) i chronologia wszystkich prac z numerami ofert, partii i plików.
