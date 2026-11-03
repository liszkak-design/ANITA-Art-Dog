#!/usr/bin/env python3
"""Generuje templates/plakietki_koty_tlumaczenie_<język>.md (PL + 7 języków) z zatwierdzonych szablonów dla psów (plakietki_grafika_tlumaczenie_<język>.md):
zamiana pies -> kot oraz geometryczny -> kreskówkowy (cartoon) wg list poniżej, z ręcznymi korektami zdań A1/A9/A5. Wynik do przeglądu."""
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
TPL = ROOT / "templates"
R = {}
R["pl"] = [("o psie rasy {B}", "o kocie (rasa: {B})"), ("psa rasy {B}", "kota (rasa: {B})"), ("ozdobiona nowoczesnym geometrycznym portretem, zbudowanym z drobnych ścianek w kolorach rasy", "ozdobiona uroczym kreskówkowym portretem w kolorach rasy"),
 ("geometryczny portret psa na ceramice", "kreskówkowy portret kota na ceramice"), ("geometryczną głową psa", "kreskówkową głową kota"), ("geometryczna pamiątka po psie", "kreskówkowa pamiątka po kocie"),
 ("geometryczna grafika", "kreskówkowa grafika"), ("nowoczesny geometryczny portret psa rasy", "uroczy kreskówkowy portret kota rasy"), ("nowoczesny geometryczny portret", "uroczy kreskówkowy portret"),
 ("geometrycznego portretu", "kreskówkowego portretu"), ("geometrycznym portretem", "kreskówkowym portretem"), ("geometryczny portret", "kreskówkowy portret"), ("geometryczny pies", "kreskówkowy kot"), ("nowoczesny portret, który", "uroczy portret, który"),
 ("grafika geometryczna", "grafika kreskówkowa"), ("Twoim psie", "Twoim kocie"), ("psa rasy", "kota rasy"), ("Twojego psa", "Twojego kota"), ("własnego psa", "własnego kota"), ("imię psa", "imię kota"),
 ("ukochanego psa", "ukochanego kota"), ("po stracie psa", "po stracie kota"), ("po psie", "po kocie"), ("o psie", "o kocie"), ("psa, który", "kota, który"), ("pamięci psa", "pamięci kota"),
 ("grób psa", "grób kota"), ("portret psa", "portret kota"), ("dla psa", "dla kota"), ("z psem", "z kotem"), ("geometryczną głową kota", "kreskówkową głową kota")]
R["de"] = [("mit einem modernen geometrischen Porträt verziert, aufgebaut aus feinen Facetten in den Farben der Rasse", "mit einem niedlichen Cartoon-Porträt in den Farben der Rasse verziert"),
 ("geometrisches Hundeporträt auf Keramik", "Katzenporträt im Cartoon-Stil auf Keramik"), ("geometrische Erinnerung an den Hund", "Erinnerung an die Katze im Cartoon-Stil"), ("geometrischem Hundekopf", "Cartoon-Katzenkopf"),
 ("geometrische Grafik", "Cartoon-Grafik"), ("modernes geometrisches Porträt", "niedliches Cartoon-Porträt"), ("Modernes geometrisches Porträt eines Hundes der Rasse", "Niedliches Cartoon-Porträt einer Katze der Rasse"),
 ("geometrischem Porträt", "Cartoon-Porträt"), ("geometrischen Porträt", "Cartoon-Porträt"), ("geometrisches Porträt", "Cartoon-Porträt"), ("ein modernes Porträt", "ein liebevolles Porträt"), ("geometrischen Kopf eines Hundes der Rasse", "Cartoon-Kopf einer Katze der Rasse"),
 ("Ihrem geliebten Hund", "Ihrer geliebten Katze"), ("für einen Hund der Rasse", "für eine Katze der Rasse"), ("zeigt einen Hund der Rasse", "zeigt eine Katze der Rasse"), ("eines Hundes der Rasse", "einer Katze der Rasse"),
 ("Ihren Hund der Rasse", "Ihre Katze der Rasse"), ("Ihren eigenen Hund", "Ihre eigene Katze"), ("Ihres eigenen Hundes", "Ihrer eigenen Katze"), ("Ihren Hund", "Ihre Katze"), ("Ihres Hundes", "Ihrer Katze"),
 ("verstorbenen Hund", "verstorbene Katze"), ("für den Hund, der", "für die Katze, die"), ("Verlust des Hundes", "Verlust der Katze"), ("Hunde Gedenkplatte", "Katzen Gedenkplatte"), ("geometrischer Hund", "Cartoon Katze"),
 ("Hundeporträt", "Katzenporträt"), ("Friedhof Hund", "Friedhof Katze"), ("Hund der Rasse", "Katze der Rasse")]
R["nl"] = [("is van keramiek en versierd met een modern geometrisch portret, opgebouwd uit fijne facetten in de kleuren van het ras", "is van keramiek en versierd met een schattig cartoonportret in de kleuren van het ras"),
 ("geometrisch hondenportret op keramiek", "kattenportret in cartoonstijl op keramiek"), ("geometrisch aandenken", "aandenken in cartoonstijl"), ("geometrische hondenkop", "kattenkop in cartoonstijl"),
 ("geometrische afbeelding", "cartoonafbeelding"), ("modern geometrisch portret", "schattig cartoonportret"), ("Modern geometrisch portret van een hond", "Schattig cartoonportret van een kat"),
 ("geometrische portret", "cartoonportret"), ("geometrisch portret", "cartoonportret"), ("een modern portret", "een charmant portret"), ("geometrische kop van een hond", "cartoonkop van een kat"), ("geometrische hond", "cartoonkat"), ("geometrisch beeld", "cartoonbeeld"),
 ("uw eigen hond", "uw eigen kat"), ("uw geliefde hond", "uw geliefde kat"), ("overleden hond", "overleden kat"), ("de hond die", "de kat die"), ("verlies van een hond", "verlies van een kat"),
 ("een hond van het ras", "een kat van het ras"), ("hond van het ras", "kat van het ras"), ("uw hond", "uw kat"), ("gedenkplaat hond", "gedenkplaat kat"), ("hondenportret", "kattenportret"), ("begraafplaats hond", "begraafplaats kat")]
R["fr"] = [("ornée d'un portrait géométrique moderne composé de fines facettes aux couleurs de la race", "ornée d'un adorable portrait de style dessin animé aux couleurs de la race"),
 ("portrait géométrique de chien sur céramique", "portrait de chat de style dessin animé sur céramique"), ("souvenir géométrique", "souvenir de style dessin animé"), ("tête de chien géométrique", "tête de chat de style dessin animé"),
 ("graphisme géométrique", "graphisme de style dessin animé"), ("portrait géométrique moderne", "adorable portrait de style dessin animé"), ("Portrait géométrique moderne d'un chien de race", "Adorable portrait de style dessin animé d'un chat de race"),
 ("portrait géométrique", "portrait de style dessin animé"), ("un portrait moderne", "un portrait charmant"), ("tête géométrique de chien de race", "tête de style dessin animé d'un chat de race"), ("chien géométrique", "chat dessin animé"), ("art géométrique", "art dessin animé"),
 ("un chien de race", "un chat de race"), ("chien de race", "chat de race"), ("votre propre chien", "votre propre chat"), ("votre chien bien-aimé", "votre chat bien-aimé"), ("votre chien", "votre chat"), ("un chien disparu", "un chat disparu"),
 ("au chien qui", "au chat qui"), ("perte d'un chien", "perte d'un chat"), ("plaque pour chien", "plaque pour chat"), ("portrait de chien", "portrait de chat"), ("tombe de chien", "tombe de chat")]
R["it"] = [("è in ceramica ed è decorata con un moderno ritratto geometrico, composto da fini sfaccettature nei colori della razza", "è in ceramica ed è decorata con un grazioso ritratto in stile cartoon nei colori della razza"),
 ("ritratto geometrico del cane su ceramica", "ritratto del gatto in stile cartoon su ceramica"), ("ricordo geometrico", "ricordo in stile cartoon"), ("testa geometrica di cane", "testa di gatto in stile cartoon"),
 ("grafica geometrica", "grafica in stile cartoon"), ("ritratto geometrico moderno", "grazioso ritratto in stile cartoon"), ("Moderno ritratto geometrico di un cane di razza", "Grazioso ritratto in stile cartoon di un gatto di razza"),
 ("ritratto geometrico", "ritratto in stile cartoon"), ("un ritratto moderno", "un ritratto grazioso"), ("cane geometrico", "gatto cartoon"), ("arte geometrica", "arte cartoon"), ("un cane di razza", "un gatto di razza"), ("cane di razza", "gatto di razza"),
 ("Suo cane", "Suo gatto"), ("Suo amato cane", "Suo amato gatto"), ("al cane che", "al gatto che"), ("di un cane che non c'è più", "di un gatto che non c'è più"), ("perdita di un cane", "perdita di un gatto"),
 ("targa per cane", "targa per gatto"), ("ritratto di cane", "ritratto di gatto"), ("tomba del cane", "tomba del gatto")]
R["pt"] = [("é de cerâmica e está decorada com um retrato geométrico moderno, composto por pequenas facetas nas cores da raça", "é de cerâmica e está decorada com um retrato fofo em estilo de desenho animado nas cores da raça"),
 ("retrato geométrico de cão em cerâmica", "retrato de gato em estilo de desenho animado em cerâmica"), ("recordação geométrica", "recordação em estilo de desenho animado"), ("cabeça geométrica de cão", "cabeça de gato em estilo de desenho animado"),
 ("arte geométrica", "arte cartoon"), ("retrato geométrico moderno", "retrato fofo em estilo de desenho animado"), ("Retrato geométrico moderno de um cão da raça", "Retrato fofo em estilo de desenho animado de um gato da raça"),
 ("retrato geométrico", "retrato em estilo de desenho animado"), ("um retrato moderno", "um retrato encantador"), ("cão geométrico", "gato cartoon"), ("um cão da raça", "um gato da raça"), ("cão da raça", "gato da raça"),
 ("o seu próprio cão", "o seu próprio gato"), ("o seu querido cão", "o seu querido gato"), ("o seu cão", "o seu gato"), ("um cão que partiu", "um gato que partiu"), ("ao cão que", "ao gato que"),
 ("perda de um cão", "perda de um gato"), ("placa para cão", "placa para gato"), ("retrato de cão", "retrato de gato"), ("sepultura de cão", "sepultura de gato"), ("do seu cão", "do seu gato")]
R["es"] = [("es de cerámica y está decorada con un retrato geométrico moderno, formado por finas facetas en los colores de la raza", "es de cerámica y está decorada con un adorable retrato de estilo dibujos animados en los colores de la raza"),
 ("retrato geométrico de perro en cerámica", "retrato de gato de estilo dibujos animados en cerámica"), ("recuerdo geométrico", "recuerdo de estilo dibujos animados"), ("cabeza geométrica de perro", "cabeza de gato de estilo dibujos animados"),
 ("arte geométrico", "arte cartoon"), ("retrato geométrico moderno", "adorable retrato de estilo dibujos animados"), ("Retrato geométrico moderno de un perro de raza", "Adorable retrato de estilo dibujos animados de un gato de raza"),
 ("retrato geométrico", "retrato de estilo dibujos animados"), ("un retrato moderno", "un retrato encantador"), ("perro geométrico", "gato cartoon"), ("un perro de raza", "un gato de raza"), ("perro de raza", "gato de raza"),
 ("tu propio perro", "tu propio gato"), ("tu querido perro", "tu querido gato"), ("tu perro", "tu gato"), ("un perro que se ha ido", "un gato que se ha ido"), ("al perro que", "al gato que"), ("pérdida de un perro", "pérdida de un gato"),
 ("placa para perro", "placa para gato"), ("retrato de perro", "retrato de gato"), ("tumba de perro", "tumba de gato")]
R["sv"] = [("är gjord av keramik och dekorerad med ett modernt geometriskt porträtt, uppbyggt av fina fasetter i rasens färger", "är gjord av keramik och dekorerad med ett gulligt tecknat porträtt i rasens färger"),
 ("geometriskt hundporträtt på keramik", "tecknat kattporträtt på keramik"), ("geometriskt minne", "tecknat minne"), ("geometriskt hundhuvud", "tecknat kattansikte"), ("geometrisk grafik", "tecknad grafik"),
 ("modernt geometriskt porträtt", "gulligt tecknat porträtt"), ("Modernt geometriskt porträtt av en hund av rasen", "Gulligt tecknat porträtt av en katt av rasen"), ("geometriska porträttet", "tecknade porträttet"),
 ("geometriskt porträtt", "tecknat porträtt"), ("ett modernt porträtt", "ett charmigt porträtt"), ("geometriskt huvud av en hund av rasen", "tecknat huvud av en katt av rasen"), ("geometrisk hund", "tecknad katt"), ("geometrisk konst", "tecknad konst"),
 ("en hund av rasen", "en katt av rasen"), ("hund av rasen", "katt av rasen"), ("din egen hund", "din egen katt"), ("din älskade hund", "din älskade katt"), ("din hund", "din katt"), ("din hunds", "din katts"),
 ("hunden som", "katten som"), ("en hund som har gått bort", "en katt som har gått bort"), ("förlusten av en hund", "förlusten av en katt"), ("hund minnesplatta", "katt minnesplatta"), ("hundporträtt", "kattporträtt"), ("grav för hund", "grav för katt")]


def main():
    for code, pairs in R.items():
        t = (TPL / f"plakietki_grafika_tlumaczenie_{code}.md").read_text(encoding="utf-8")
        for a, b in pairs:
            t = t.replace(a, b)
        t = t.replace("(EN: dog memorial plaque, geometric dog,", "(EN: cat memorial plaque, cartoon cat,")
        t = t.replace("Status: EN zatwierdzony przez właścicielkę 03.11.2026. Polski sprawdza właścicielka.", "Status: wersja dla kotów oparta na zatwierdzonej wersji dla psów (04.11.2026), do sprawdzenia. Polski sprawdza właścicielka.")
        t = t.replace("Status: EN i PL zatwierdzone przez właścicielkę 03.11.2026.", "Status: wersja dla kotów oparta na zatwierdzonych EN i PL dla psów (04.11.2026).")
        t = t.replace("geometryczne psy, 100 ofert", "koty (grafika kreskówkowa), 45 ofert").replace("(geometryczne psy, 100 ofert;", "(koty, grafika kreskówkowa, 45 ofert;")
        # przeliczenie długości tagów
        out = []
        for ln in t.split("\n"):
            if ln.startswith("**Stałe:**") or ln.startswith("**Pula:**"):
                head, rest = ln.split("** ", 1)
                en = ""
                if " (EN:" in rest:
                    rest, en = rest.split(" (EN:", 1)
                    en = " (EN:" + en
                items = [re.sub(r" \(\d+\)$", "", x.strip()) for x in rest.split(", ")]
                ln = head + "** " + ", ".join(f"{x} ({len(x)})" for x in items) + en
            out.append(ln)
        (TPL / f"plakietki_koty_tlumaczenie_{code}.md").write_text("\n".join(out), encoding="utf-8")
    print("ok")


if __name__ == "__main__":
    main()
