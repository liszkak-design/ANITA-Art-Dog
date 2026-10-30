# Plan optymalizacji: urny z płytką "with Graphics", tylko psy (100 ofert), wersja robocza 30.10.2026

## Stan wejściowy (odczyt API, `plans/grafika_stan_zywy.json`)
- 100 aktywnych ofert psów ("... Urn for Dog Ashes, Personalized Memorial with a Geometric Graphics on a Ceramic Plaque, Pet's Name and Quote"), cena 129 EUR, ilość 47-50, who_made/when_made/czas realizacji jak w pozostałych urnach.
- Każda ma 6 zdjęć (zdjęcia 2-6 identyczne w całej grupie i takie same jak w urnach z płytką), 0 filmów, 0 alt textów, jedno wymagane pole "Personalization", właściwości tylko Primary color i Occasion, materiały tekstowe: wood, brass handles, ceramic plate.
- Serwer: `VIDEO/IV tura/096. Urny psy geom/` ma 100 folderów (po 2 filmy: z "brand" i bez, 4 karty graficzne `*-foto-1..4.jpg`); indeks `plans/grafika_foldery_index.csv`. Zdjęcia live to prawdziwe zdjęcia urn, a `foto-1` na serwerze to karta (infografika), więc dopasowania po obrazie nie da się zrobić jak przy reliefie; mapa wstępna po nazwie rasy: `plans/grafika_mapa_wstepna.csv` (100 ofert = 100 folderów, 1:1). Rasy dublowane (Boxer, Chihuahua, Doberman, Great Dane, Schnauzer, Dachshund x3, Neapolitan Mastiff) rozstrzygnięte wzrokowo po grafice na płytce w żywym zdjęciu 1; wymagają Twojego potwierdzenia.
- Etsy odczytuje alt texty z `&#39;` itd., więc weryfikacja porównuje po html.unescape (jak w urnach z płytką).

## Zakres zmian na ofertę
1. Kopia zapasowa; tytuł (do 14 słów), opis, 13 tagów (nowa pula), materiały bez zmian, Materials (Ceramic, Brass, Pine, Birch), how it's made.
2. Personalizacja: 5 pytań (imię i daty wymagane, cytat opcjonalny, zdjęcie do wgrania, styl wydruku: kolor / kolor bez tła).
3. Alt texty zdjęć 1-6 (zdjęcia nie wymieniane, do potwierdzenia), film 1 (do dostarczenia), film 2 z folderu rasy (bez "brand"), 8 tłumaczeń (po akceptacji EN: PL, potem reszta).
4. Partie max 50, test na jednej ofercie, najpierw mniej oglądane, najbardziej oglądane na końcu (Siberian Husky 526 wyśw., Rottweiler 495, German Shepherd 423, Rhodesian Ridgeback 256, Cane Corso 240 i inne).
