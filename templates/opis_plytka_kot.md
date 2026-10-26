# Szablon opisu: płytka ceramiczna, kot (wersja robocza do zatwierdzenia)

Język oferty: angielski. Nazwa rasy `{BREED}` = kolumna C arkusza Rasy w `data/Rasy.xlsx` (np. Siamese).
Dla psa i konia zmieniają się tylko: rzeczownik (cat / dog / horse), nazwa rasy i banki zdań pierwszego akapitu.
Reszta (sekcje stałe) jest taka sama dla wszystkich ofert z płytkami.

## 1. Pierwszy akapit (składany z banków)

Akapit = zdanie A + zdanie B + zdanie C. Każdy slot ma kilka zatwierdzonych wariantów. Wariant wybierany jest
deterministycznie po ID oferty, a sąsiednie oferty w partii różnią się co najmniej w dwóch slotach.
Pełna nazwa rasy `{BREED}` musi być w zdaniu A. Zdrobnienie z kolumny E (tylko EN, tylko pies) wolno użyć
najwyżej dwa razy w całym akapicie, także w zdaniu A (obok pełnej nazwy rasy, nie zamiast niej; zasada z 26.10.2026).
Koty i konie nie mają wpisów w kolumnie E. Jedno zdanie nie zawiera pełnej nazwy rasy dwa razy.

**Slot A (otwarcie, nazwa rasy + słowa kluczowe)**
- A1: This {BREED} cat memorial plaque is a ceramic tombstone plaque with a sketch-style portrait of the breed, made to remember a much-loved cat.
- A2: A ceramic memorial plaque for your {BREED} cat, decorated with a sketch-style portrait of the breed.
- A3: Remember your {BREED} with this ceramic tombstone plaque, printed with a sketch-style portrait of the breed.
- A4: This ceramic pet memorial plaque features a sketch-style portrait of a {BREED} cat, created to honour a much-loved companion.
- A5: A {BREED} cat memorial plaque in ceramic: a sketch-style portrait that keeps the memory of your cat close.

**Slot B (zastosowanie)**
- B1: Place it on a grave or in any other place of remembrance, as a lasting tribute to the cat who shared your life.
- B2: It can mark a grave or sit in a quiet spot that is special to you, a lasting reminder of the cat you loved.
- B3: Use it as a grave marker or as a keepsake in a place of remembrance, a lasting tribute to your cat.
- B4: A fitting tribute for a grave or any place where you remember your cat, made to last outdoors.

**Slot C (zdjęcie klienta)**
- C1: If you would rather remember your own cat, send us a photo and we will print it instead.
- C2: Prefer your own cat's portrait? Attach a photo and we will print it on the plaque.
- C3: You can also have the plaque printed with a photo of your own cat.
- C4: Your own photo can be printed instead, just attach it when ordering.

## 2. Sekcje stałe (gotowy tekst, wersja dla kota)

```
IN SHORT
- Ceramic oval plaque, approx. 10.5 x 7.5 cm (4.13 x 2.95 in), approx. 0.5 cm (0.2 in) thick
- Sketch-style portrait of a {BREED} cat, or personalised with your own photo
- Weather-resistant print that does not fade
- Smooth, rounded edge, no extra frame or setting needed
- No hole or hook on the back, attach it with any universal adhesive
- Personalisation available: your photo, print style, name and dates

A LASTING TRIBUTE
A ceramic plaque is a gentle and lasting way to remember a cat who has passed away. The smooth edge needs no special frame, the high-quality print is made to last, and personalisation lets you make the plaque truly yours.

PERSONALISATION
Order the plaque exactly as shown, or personalise it. Every option below is optional.
- Your photo: we can print any photo you send us. Attach it in the personalisation box when ordering, or send it by Etsy message.
- Style: choose the original photo, full colour with the background removed, or a pencil-sketch style like the one shown.
- Name and dates: add your cat's name, or name and dates of life, or leave the plaque without text.
- Orientation: a plaque with your photo can be placed vertically or horizontally.

Questions about personalising your plaque? Send us a message, we will gladly help.

We would be honoured to help you say goodbye to your beloved cat with dignity.

INTERNATIONAL ORDERS
Our products are shipped from Poland, so import charges may apply in some countries. These charges do not apply to EU countries, the United Kingdom and the USA. If you have any doubts, please contact us for details.
```
