# Urny z płytką ceramiczną "with a Photo": propozycja tekstów EN (do akceptacji, 28.10.2026)

`{BREED}` = kolumna C `Rasy.xlsx`, `{NICK}` = kolumna E (tylko zdrobnienia), `{SYN}` = kolumna E (synonimy), `{S}` = Dog / Cat / Horse (Pony dla kucyków),
pomijane, gdy nazwa rasy już zawiera to słowo. Zasady jak w płytkach: cechy w tytule, nie w opisie; liczb wzorów, wagi zwierzęcia i gatunku drewna nie podajemy.

## 1. Nagłówki akapitów (zamiast IN SHORT)

Do wyboru jeden zestaw. Rekomendacja: zestaw 1.

| | Fakty | Zakończenie | Personalizacja | Wysyłka |
|---|---|---|---|---|
| 1 (rekomendacja) | THE URN AT A GLANCE | A PLACE OF REMEMBRANCE | PERSONALISATION | INTERNATIONAL ORDERS |
| 2 | ABOUT THIS URN | A LASTING KEEPSAKE | MAKE IT YOURS | INTERNATIONAL ORDERS |
| 3 | WHAT TO KNOW ABOUT THE URN | A GENTLE FAREWELL | PERSONALISATION | INTERNATIONAL ORDERS |

## 2. Tytuły (zaczynają się od rasy, limit 140 zn., wzorzec po ID oferty)

1. {BREED} {S} Urn for Ashes, Handmade Wooden Pet Urn with Ceramic Photo Plaque, Personalised Name and Quote
2. {BREED} Pet Urn, Personalized Wooden Cremation Urn with Photo on Ceramic Plaque, Pet Loss Gift
3. {BREED} {S} Memorial Urn, Handmade Wood Urn with Ceramic Photo Plaque, Custom Engraved Name and Dates
4. {BREED} Urn for {S} Ashes, Engraved Wooden Keepsake Urn with Photo Plaque, Personalised Pet Memorial
5. {BREED} {S} Cremation Urn, Wooden Pet Urn with Your Photo, Engraved Quote, Name and Dates
6. {BREED} Ashes Urn for Your {S}, Handmade Personalised Urn with Ceramic Plaque, Sympathy Gift

Dla {BREED}={Beagle, Dog} tytuły mają 88–104 zn. Przy najdłuższych nazwach ras (np. Nova Scotia Duck Tolling Retriever) wzorce 1, 3 i 4 mogą
przekroczyć 140: generator wtedy wybiera krótszy wzorzec (jak w płytkach), bez obcinania.

## 3. Tagi (13 na ofertę, max 20 zn., bez nazw ras, bez powtórzeń)

7 stałych + 6 z puli, losowanie powtarzalne (ziarno = ID oferty), z puli nie więcej niż jeden tag z danym słowem (gift, memorial, keepsake itd.).

**Stałe:** pet urn for ashes (17), personalized urn (16), wooden urn (10), urn with photo (14), pet loss gift (13), {s} ashes urn (dog / cat / horse ashes urn, 14-15), {s} memorial (dog / cat / horse memorial, 12-15).

**Pula (25):** cremation urn (13), memorial urn (12), urn with name (13), engraved urn (12), keepsake urn (12), urn with quote (14), handmade urn (12),
pet memorial (12), ceramic plaque (14), pet cremation urn (17), sympathy gift (13), pet loss keepsake (17), in loving memory (16), rainbow bridge (14),
remembrance gift (16), custom pet urn (14), photo memorial (14), urn for ashes (13), pet bereavement (15), brass handle urn (16), pet memorial gift (17),
always in my heart (18), pet remembrance (15), memorial keepsake (17), engraved keepsake (17).

Nie używamy `cat ashes` przy psach i koniach ani odwrotnie (obecnie wszystkie urny mają `cat ashes`, w tym psy).

## 4. Pierwszy akapit (banki A + B + C, wariant po ID oferty)

Wersja dla psa; dla kota i konia podmieniamy gatunek, a dla koni "paw-shaped" → "horseshoe-shaped". Pełna nazwa rasy w zdaniu A, żadne zdanie nie ma jej dwa razy.

**Zasada wyboru zdania A (decyzja 28.10.2026):** jeśli w `Rasy.xlsx` kolumna E ma wpis, zdanie A losujemy wyłącznie spośród wariantów używających tego wpisu:
zdrobnienie → warianty [N], synonim → warianty [S] (klasyfikacja `data/nick_klasyfikacja.csv`). Gdy kolumna E jest pusta, losujemy z wariantów bez [N]/[S].
Zdrobnienia [N] także w B i C, łącznie max dwa razy w akapicie.

**A (otwarcie), bez NICK/SYN**
- A1: This {BREED} dog urn is a handmade wooden urn for ashes, with a ceramic plaque showing a sketch-style portrait of the dog, made to remember a much-loved pet.
- A2: A handmade wooden urn for your {BREED}, decorated with a ceramic plaque with a sketch-style portrait of the breed and a plaque with a quote.
- A3: Remember your {BREED} with this handmade wooden urn for dog ashes, with a ceramic portrait plaque, an engraved quote, and a name and dates.
- A4: This personalised pet urn features a ceramic plaque with a sketch-style portrait of a {BREED}, created to honour a much-loved companion.
- A5: When the saddest day comes, this handmade {BREED} urn offers a quiet, lasting place for the ashes of your dog.

**A, gdy jest zdrobnienie [N]**
- A6 [N]: Remember your beloved {BREED} with this handmade wooden urn, made to honour your faithful {NICK}.
- A7 [N]: A handmade wooden urn with a ceramic sketch-style portrait plaque, made to remember your much-loved {NICK}.
- A8 [N]: This handmade wooden urn keeps your dear {NICK} close, with a ceramic portrait plaque, an engraved quote, and a name and dates.
- A9 [N]: A personalised wooden urn for your {BREED}, made as a lasting place for your faithful {NICK}.
- A10 [N]: When the saddest day comes, this handmade urn offers a quiet, lasting place for the ashes of your {NICK}.

**A, gdy jest synonim [S]**
- A11 [S]: This {SYN} dog urn is a handmade wooden urn for ashes, with a ceramic plaque showing a sketch-style portrait of the dog.
- A12 [S]: A handmade wooden urn for your {SYN}, with a ceramic portrait plaque, an engraved quote, and a name and dates.
- A13 [S]: Remember your {SYN} with this handmade wooden urn for dog ashes, with a sketch-style portrait on a ceramic plaque.
- A14 [S]: This personalised {SYN} urn features a ceramic plaque with a sketch-style portrait, created to honour a much-loved companion.
- A15 [S]: When the saddest day comes, this handmade {SYN} urn offers a quiet, lasting place for the ashes of your dog.

**B (zastosowanie)**
- B1: Keep it at home in a quiet place, a lasting tribute to the dog who shared your life.
- B2: It can stand wherever you remember your dog, a gentle reminder of the companion you loved.
- B3: A fitting place for your dog's ashes, made to be kept close at home.
- B4 [N]: Keep it close as a lasting tribute to your faithful {NICK}.

**C (pełna personalizacja)**
- C1: Every urn is made to order: add your dog's name and dates, choose the quote, or send us your own photo and we will print it on the plaque instead.
- C2: Make it truly yours: the nameplate, the quote and the plaque photo can all be personalised to remember your own dog.
- C3: You can personalise the name, dates and quote, and have the plaque printed with a photo of your own dog.
- C4: Tell us the name, dates and quote you would like, and attach a photo if you wish to see your own dog on the plaque.
- C5 [N]: Add your dog's name and dates, choose the quote, or send us a photo to remember your own {NICK} on the plaque.

## 5. Sekcje stałe (wersja dla psa)

```
THE URN AT A GLANCE
- Handmade wooden urn for pet ashes, made of solid wood and plywood, painted brown
- Oval ceramic plaque with a printed sketch-style portrait of a {BREED}, approx. 7.5 x 10.5 cm (2.95 x 4.13 in), permanently attached
- Paw-shaped plaque with an engraved quote, and a nameplate with the name and dates
- External size: 21 x 29 x 22 cm (8.3 x 11.4 x 8.7 in)
- Internal size: 14 x 21 x 15.5 cm (5.5 x 8.3 x 6.1 in), capacity approx. 4.5 litres (275 cubic inches)
- Brass handles and carved wooden decorations
- Removable lid, not sealed: glue it with any all-purpose glue to close it tightly

A PLACE OF REMEMBRANCE
Losing a dog is one of the saddest days. This urn is a quiet, lasting place to keep your dog close. The brass handles and carved decorations give it a classic, timeless look, and the engravings are applied to painted plywood, so every urn is made for one dog only.

PERSONALISATION
Every urn is made to order. Please tell us:
- Name: the name of your pet, as it should appear on the nameplate.
- Dates: dates of birth and death, in any format you like.
- Quote: the paw-shaped plaque carries "You left paw prints on my heart" unless you give us your own exact wording.
- Plaque photo: the plaque shows the sketch-style portrait you see, or we print your own photo.
- Print style: original photo, full colour with the background removed, or pencil sketch.

Questions about personalising your urn? Send us a message, we will gladly help.

We would be honoured to help you say goodbye to your beloved dog with dignity.

INTERNATIONAL ORDERS
Our products are shipped from Poland, so import charges may apply in some countries. These charges do not apply to EU countries, the United Kingdom and the USA. If you have any doubts, please contact us for details.
```

Domyślny wydruk na płytce: szkic (potwierdzone 28.10.2026). Pojemność 4.5 l potwierdzona.

## 6. Alt text 7. zdjęcia: patrz `templates/alt_urny_plytka.md` (zaakceptowane).
