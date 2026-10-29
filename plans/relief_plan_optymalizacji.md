# Plan optymalizacji: urny z reliefem "Custom urn for dog's ashes" (38 ofert), wersja robocza 29.10.2026

## Stan wejściowy
- 38 aktywnych ofert, 139 EUR, ilość 3-10, materiały tekstowe: wood, brass handles, cold cast bronze bust. Każda ma 6 zdjęć (wg eksportu z X.2025): zdjęcie 1 = urna z reliefem, zdjęcia 2-6 = te same 5 zdjęć co w urnach z płytką ceramiczną (uchwyt, uchwyt pod kątem, listwa, narożnik, wnętrze).
- Serwer: `VIDEO/V tura/109. Plakietki na urnie/` ma 38 folderów (po 2 filmy: `*-brand.mp4` i `*.mp4`, oraz 4 zdjęcia `*-foto-1..4.jpg`); indeks `plans/relief_foldery_index.csv`. Zdjęcie 1 do nadpisania = `*-foto-1.jpg` z folderu (karta: urna z reliefem + napis "Cold cast bronze portrait relief, small/large"); pliku `allegro/zebraneEAN/<EAN>/1.jpg` dla tych EAN nie ma (404).
- Folder ma w nazwie rozmiar reliefu: mały/średni/duży (np. 3 x Bulldog, 2 x German Shepherd, 3 x Mastino), więc dopasowanie oferta -> folder trzeba zrobić po zdjęciu 1 z żywych ofert (jak przy urnach z płytką).
- 7 folderów, gdzie na zdjęciu 1 nie ma tabliczki z grawerem (relief duży): 18 Borzoi Russian Wolfhound, 21 Rottweiler, 23 Rottweiler (mały), 24 Staffordshire Bullterrier, 28 Dachshund (wire), 29 Newfoundland, 38 Irish Wolfhound. Pozostałe 31 mają tabliczkę (imię, daty, cytat, łapa w dłoni).
- Etsy zgłasza chwilowo "Exceeded daily rate limit" (okno kroczące 24 h, ok. 10 700 zapytań); odczyt żywego stanu 38 ofert (zdjęcia, personalizacja, właściwości) możliwy po ok. 22:00-23:00 UTC 29.10.2026. Licznik w skrypcie zmieniony na okno kroczące.

## Zakres zmian na ofertę (jak w urnach z płytką)
1. Kopia zapasowa, tytuł, opis, 13 tagów (nowa baza), materiały tekstowe (wood, brass handles, cold cast bronze relief, bez ceramiki), właściwość Materials, who_made/when_made.
2. Personalizacja: wariant A (31 ofert z tabliczką): Name (wymagane), Dates (wymagane), Quote (opcjonalne; domyślnie "When I needed a hand, you gave me your paw"). Wariant B (7 ofert bez grawerunku): Name i Dates opcjonalne, bez cytatu (tabliczka na życzenie).
3. Zdjęcie 1 nadpisane z `*-foto-1.jpg` (nowy alt text), zdjęcia 2-6 bez zmian (alt jak przy urnach z płytką), bez zdjęcia 7 (do potwierdzenia).
4. Film 1: uniwersalny (do dostarczenia), film 2: z folderu rasy, plik bez "brand".
5. Tłumaczenia w 8 językach (PL, potem pozostałe z PL), bez tłumaczenia pól personalizacji.
6. Partie max 50 (tu jedna partia 38 lub pilot + reszta), każda oferta raz, weryfikacja po zapisie, top 4 (German Shepherd 1366245946, Dogue de Bordeaux 1380250289, Rottweiler 1380245821, Golden Retriever 1366250756) na końcu.
