# Analiza zainteresowania ofertami "with Graphics" (29.10.2026)

Dane: sprzedaż `data/EtsySoldOrderItems2025-2026.csv` (03.01.2025 - 20.10.2026), wyświetlenia i ulubione z API (odczyt, `plans/with_graphics_zainteresowanie.csv`).
Uwaga: "views" z API to licznik Etsy, w tym zbiorze nie jest wiarygodnym wskaźnikiem popytu (4 z 5 sprzedanych urn Graphics miało 0 wyświetleń).

| Grupa | Ofert | Sprzedane szt. | Przychód EUR | Ofert ze sprzedażą | Szt./ofertę | EUR/ofertę |
|---|---|---|---|---|---|---|
| Płytki with Photo | 300 | 21 | 215,80 | 15 (5,0%) | 0,070 | 0,72 |
| Płytki with Graphics | 145 | 3 | 29,97 | 2 (1,4%) | 0,021 | 0,21 |
| Urny with Photo | 299 | 18 | 1782,00 | 11 (3,7%) | 0,060 | 5,96 |
| Urny with Graphics | 145 | 7 | 693,00 | 5 (3,4%) | 0,048 | 4,78 |

Wyświetlenia i ulubione (stan z API): płytki Graphics: mediana 31 wyśw., 100% ofert z wyświetleniem, 63% z ulubionym; płytki Photo (próbka 100): mediana 18, 51%, 38%;
urny Graphics: mediana 0 wyśw., 24% ofert z wyświetleniem, 13% z ulubionym (najlepsza: Rottweiler 661034442, 495 wyśw., 7 ulubionych, 3 sprzedane = 297 EUR); urny Photo (299, część liczników po naszej optymalizacji): mediana 39, 100%, 59%.
Ceny: urna Graphics 99 EUR (Photo 129 EUR), płytki ok. 9,99 EUR.
