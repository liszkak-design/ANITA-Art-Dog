# Szablon opisu: płytka ceramiczna, pies (wersja robocza do zatwierdzenia)

Język oferty: angielski. Zasady i sekcje stałe jak w `opis_plytka_kot.md` (zatwierdzone).
`{BREED}` = kolumna C arkusza Rasy w `data/Rasy.xlsx`. `{NICK}` = kolumna E (Potoczne EN), jeśli jest wpisana.

## 1. Pierwszy akapit (składany z banków)

Akapit = zdanie A + zdanie B + zdanie C. Wariant wybierany deterministycznie po ID oferty, sąsiednie oferty
w partii różnią się co najmniej w dwóch slotach. Pełna nazwa rasy `{BREED}` jest w zdaniu A.

Zdrobnienie `{NICK}`: w slotach A, B i C (od 26.10.2026 także w zdaniu A), tylko w wariantach oznaczonych [N], tylko gdy kolumna E
jest wpisana, najwyżej dwa razy w całym akapicie. Zdrobnienie nie musi stać razem z nazwą rasy, może być w zdaniu samo. Jedno zdanie
nie zawiera pełnej nazwy rasy dwa razy. Zdanie A (wariant [N]: A9-A11, nowe, do przeglądu w partii 1) może składać się tylko ze zdrobnienia, bez nazwy rasy:
pełna nazwa rasy jest wtedy w tytule oferty i w sekcji IN SHORT (decyzja właścicielki 26.10.2026). Gdy kolumna E jest pusta, używamy wyłącznie wariantów bez [N].
Wartości z kolumny E użyte są dokładnie tak, jak wpisano w arkuszu, z wyjątkiem poprawek zatwierdzonych przez
właścicielkę (arkusz `Rasy.xlsx` niezmieniony): Affenpinscher: `Affie` (w arkuszu `ffie`), Newfoundland: `Newfie`
(w arkuszu `Newfies`), Central Asia Shepherd: `Alabay` (w arkuszu `Alabai, Alabay`).
Wpisy w kolumnie E, które są synonimami (np. Alsatian, Saint Bernard, Russian Wolfhound; 27 z 45), NIE dostają zdań ze zdrobnieniem [N],
ale mają synonim w zdaniu A (warianty [S] A12-A16, nowe, do przeglądu w partii 1: synonim zamiast nazwy rasy),
żeby oferta była znajdowana po tych nazwach (decyzja 26.10.2026). Klasyfikacja: `data/nick_klasyfikacja.csv` (18 zdrobnień, 27 synonimów).

**Slot A (otwarcie, nazwa rasy + słowa kluczowe)**
- A1: This {BREED} dog memorial plaque is a ceramic tombstone plaque with a sketch-style portrait of the dog, made to remember a much-loved pet.
- A2: A ceramic memorial plaque for your {BREED} dog, decorated with a sketch-style portrait of the breed.
- A3: Remember your {BREED} with this ceramic tombstone plaque, printed with a sketch-style portrait of the dog.
- A4: This ceramic pet memorial plaque features a sketch-style portrait of a {BREED}, created to honour a much-loved companion.
- A5: A {BREED} dog memorial plaque in ceramic: a sketch-style portrait that keeps the memory of your dog close.
- A6 [N]: Remember your beloved {BREED} with this ceramic tombstone plaque, a sketch-style portrait made to honour your faithful {NICK}.
- A7 [N]: This ceramic memorial plaque with a sketch-style portrait of the breed is made to remember your much-loved {BREED}, your faithful {NICK}.
- A8 [N]: A ceramic tombstone plaque for your {BREED}: a sketch-style portrait that keeps the memory of your dear {NICK} close.
- A9 [N]: A ceramic tombstone plaque with a sketch-style portrait, made to remember your much-loved {NICK}.
- A10 [N]: Remember your faithful {NICK} with this ceramic memorial plaque, decorated with a sketch-style portrait of the dog.
- A11 [N]: This ceramic plaque keeps the memory of your dear {NICK} close, with a sketch-style portrait of the dog.
- A12 [S]: This {SYN} dog memorial plaque is a ceramic tombstone plaque with a sketch-style portrait of the dog, made to remember a much-loved pet.
- A13 [S]: A ceramic memorial plaque for your {SYN} dog, decorated with a sketch-style portrait of the breed.
- A14 [S]: Remember your {SYN} with this ceramic tombstone plaque, printed with a sketch-style portrait of the dog.
- A15 [S]: This ceramic pet memorial plaque features a sketch-style portrait of a {SYN}, created to honour a much-loved companion.
- A16 [S]: A {SYN} dog memorial plaque in ceramic: a sketch-style portrait that keeps the memory of your dog close.

**Slot B (zastosowanie)**
- B1: Place it on a grave or in any other place of remembrance, as a lasting tribute to the dog who shared your life.
- B2: It can mark a grave or sit in a quiet spot that is special to you, a lasting reminder of the dog you loved.
- B3: Use it as a grave marker or as a keepsake in a place of remembrance, a lasting tribute to your dog.
- B4: A fitting tribute for a grave or any place where you remember your dog, made to last outdoors.
- B5 [N]: Place it on a grave or in any other place of remembrance, as a lasting tribute to your faithful {NICK}.
- B6 [N]: It can mark a grave or sit in a quiet spot that is special to you, a lasting reminder of your beloved {NICK}.

**Slot C (zdjęcie klienta)**
- C1: If you would rather remember your own dog, send us a photo and we will print it instead.
- C2: Prefer your own dog's portrait? Attach a photo and we will print it on the plaque.
- C3: You can also have the plaque printed with a photo of your own dog.
- C4: Your own photo can be printed instead, just attach it when ordering.
- C5 [N]: If you would like to remember your own {NICK}, send us a photo and we will print it instead.
- C6 [N]: You can also have your own {NICK} on the plaque: attach a photo and we will print it.

## 2. Sekcje stałe (gotowy tekst, wersja dla psa)

```
IN SHORT
- Ceramic oval plaque, approx. 10.5 x 7.5 cm (4.13 x 2.95 in), approx. 0.5 cm (0.2 in) thick
- Sketch-style portrait of a {BREED}, or personalised with your own photo
- Weather-resistant print that does not fade
- Smooth, rounded edge, no extra frame or setting needed
- No hole or hook on the back, attach it with any universal adhesive
- Personalisation available: your photo, print style, name and dates

A LASTING TRIBUTE
A ceramic plaque is a gentle and lasting way to remember a dog who has passed away. The smooth edge needs no special frame, the high-quality print is made to last, and personalisation lets you make the plaque truly yours.

PERSONALISATION
Order the plaque exactly as shown, or personalise it. Every option below is optional.
- Your photo: we can print any photo you send us. Attach it in the personalisation box when ordering, or send it by Etsy message.
- Style: choose the original photo, full colour with the background removed, or a pencil-sketch style like the one shown.
- Name and dates: add your dog's name, or name and dates of life, or leave the plaque without text.
- Orientation: a plaque with your photo can be placed vertically or horizontally.

Questions about personalising your plaque? Send us a message, we will gladly help.

We would be honoured to help you say goodbye to your beloved dog with dignity.

INTERNATIONAL ORDERS
Our products are shipped from Poland, so import charges may apply in some countries. These charges do not apply to EU countries, the United Kingdom and the USA. If you have any doubts, please contact us for details.
```
