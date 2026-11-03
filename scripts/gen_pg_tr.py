#!/usr/bin/env python3
"""Generuje templates/plakietki_grafika_tlumaczenie_<język>.md dla 7 języków (DE, NL, FR, IT, PT, ES, SV) z polskiego i angielskiego szablonu "with a Graphics" (psy).
Wspólne zdania (zdjęcie, orientacja, pytania, International Orders) kopiowane z zatwierdzonych szablonów płytek "with a Photo" (tlumaczenie_<kod>_plytka.md)."""
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
TPL = ROOT / "templates"
L = {}
L["de"] = dict(name="Deutsch", form="Sie",
 titles=["{B} Gedenkplatte, geometrisches Hundeporträt auf Keramik, personalisierte Grabplatte",
  "{B} Grabplatte aus Keramik mit geometrischem Porträt, Geschenk nach dem Verlust des Hundes",
  "{B} geometrische Erinnerung an den Hund, ovale Keramikplatte, Name oder Foto nach Wunsch",
  "{B} Grabkennzeichnung, Keramikplatte mit geometrischem Hundekopf, personalisiertes Gedenkgeschenk",
  "{B} Grabplatte, geometrische Grafik auf Keramik, auf Wunsch mit Ihrem Foto",
  "{B} Tiergrabstein, modernes geometrisches Porträt, Geschenk zum Beileid"],
 A=["Diese Gedenkplatte für einen Hund der Rasse {B} besteht aus Keramik und ist mit einem modernen geometrischen Porträt verziert, aufgebaut aus feinen Facetten in den Farben der Rasse.",
  "Eine Grabplatte aus Keramik für Ihren Hund (Rasse: {B}) mit einem geometrischen Porträt der Rasse.",
  "Bewahren Sie die Erinnerung an Ihren Hund der Rasse {B} mit einer Keramikplatte, auf die ein geometrisches Porträt der Rasse gedruckt ist.",
  "Diese Gedenkplatte aus Keramik zeigt einen Hund der Rasse {B} als geometrisches Porträt, eine moderne Art, einem geliebten Begleiter Ehre zu erweisen.",
  "Ein Grabzeichen aus Keramik mit einem geometrischen Kopf eines Hundes der Rasse {B}: ein modernes Porträt, das die Erinnerung an Ihren Hund wachhält."],
 B=["Stellen Sie sie auf ein Grab oder an einen anderen Ort der Erinnerung, als Zeichen der Würdigung für den Hund, der Ihr Leben geteilt hat.",
  "Sie kann ein Grab oder einen anderen für Sie wichtigen Ort markieren, an dem Sie sich an Ihr geliebtes Tier erinnern.",
  "Sie dient als Grabkennzeichnung oder als Zeichen an einem anderen Ort der Erinnerung. Sie ist für die Verwendung im Freien geeignet."],
 C=["Wenn Sie lieber Ihren eigenen Hund in Erinnerung behalten möchten, wählen Sie Ihr Foto, und wir drucken es anstelle des im Angebot gezeigten Motivs.",
  "Sie können den Namen Ihres Hundes oder Namen und Lebensdaten über dem Porträt hinzufügen.",
  "Möchten Sie lieber ein Porträt Ihres eigenen Hundes? Fügen Sie ein Foto bei, und wir drucken es im Original oder mit entferntem Hintergrund."],
 portrait="- Modernes geometrisches Porträt eines Hundes der Rasse {B} oder Ihr eigenes Foto",
 th="ERINNERUNG, DIE BEI IHNEN BLEIBT",
 tt="Eine Keramikplatte ist eine behutsame Art, die Erinnerung an einen verstorbenen Hund zu bewahren. Die glatte Kante braucht keine besondere Fassung, der hochwertige Druck ist auf lange Haltbarkeit ausgelegt, und die Personalisierung macht die Platte zu etwas ganz Persönlichem.",
 style="- Stil: Wählen Sie bei Ihrem eigenen Foto das Original oder Farbe mit entferntem Hintergrund.",
 nm="- Name und Daten: Fügen Sie den Namen Ihres Hundes hinzu, oder Name und Lebensdaten, zum geometrischen Porträt oder zu Ihrem Foto, oder lassen Sie die Platte ohne Schrift.",
 close="Es wäre uns eine Ehre, Sie dabei zu unterstützen, würdevoll von Ihrem geliebten Hund Abschied zu nehmen.",
 core=["Hunde Gedenkplatte", "geometrischer Hund", "Trauergeschenk Tier", "Grabkennzeichen", "Grabplatte"],
 pool=["Keramikplatte", "Platte mit Namen", "Platte mit Foto", "Tiergrabstein", "Gedenkstück", "Beileidsgeschenk", "Zum Gedenken", "Gartengedenken", "geometrische Grafik", "Hundeporträt", "Friedhof Hund", "Erinnerung Haustier", "wetterfeste Platte", "ovale Gedenkplatte", "Gedenken draußen", "Gedenkstein Tier", "Regenbogenbrücke", "Kondolenz"])
L["nl"] = dict(name="Nederlands", form="u/uw",
 titles=["{B} herdenkingsplaat, geometrisch hondenportret op keramiek, gepersonaliseerde grafplaat",
  "{B} keramische grafplaat met geometrisch portret, cadeau na het verlies van een hond",
  "{B} geometrisch aandenken, ovale keramische plaat, naam of foto naar wens",
  "{B} grafmarkering, keramische plaat met geometrische hondenkop, gepersonaliseerd herdenkingscadeau",
  "{B} grafplaat, geometrische afbeelding op keramiek, op verzoek met uw eigen foto",
  "{B} dierengrafsteen, modern geometrisch portret, cadeau bij condoleance"],
 A=["Deze herdenkingsplaat voor een hond van het ras {B} is van keramiek en versierd met een modern geometrisch portret, opgebouwd uit fijne facetten in de kleuren van het ras.",
  "Een keramische grafplaat voor uw hond (ras: {B}) met een geometrisch portret van het ras.",
  "Bewaar de herinnering aan uw hond van het ras {B} met een keramische plaat waarop een geometrisch portret van het ras is geprint.",
  "Deze keramische herdenkingsplaat toont een hond van het ras {B} als geometrisch portret, een moderne manier om een geliefde metgezel te eren.",
  "Een keramische grafmarkering met een geometrische kop van een hond van het ras {B}: een modern portret dat de herinnering aan uw hond dichtbij houdt."],
 B=["Plaats hem op een graf of op een andere herinneringsplek, als eerbetoon aan de hond die uw leven deelde.",
  "Hij kan een graf of een andere voor u belangrijke plek markeren, waar u uw geliefde dier herdenkt.",
  "Hij dient als grafmarkering of als teken op een andere herinneringsplek. Hij is geschikt voor gebruik buiten."],
 C=["Wilt u liever uw eigen hond herdenken, kies dan uw eigen foto en wij drukken die af in plaats van het getoonde ontwerp.",
  "U kunt de naam van uw hond, of naam en levensdata, boven het portret laten zetten.",
  "Liever een portret van uw eigen hond? Voeg een foto toe en wij drukken die af in het origineel of met verwijderde achtergrond."],
 portrait="- Modern geometrisch portret van een hond van het ras {B} of uw eigen foto",
 th="EEN HERINNERING DIE BIJ U BLIJFT",
 tt="Een keramische plaat is een zachte manier om de herinnering aan een overleden hond te bewaren. De gladde rand heeft geen speciale omlijsting nodig, de hoogwaardige print is gemaakt om lang mee te gaan en met personalisatie maakt u de plaat helemaal van uzelf.",
 style="- Stijl: kies bij uw eigen foto het origineel of volledige kleur met verwijderde achtergrond.",
 nm="- Naam en data: voeg de naam van uw hond toe, of naam en levensdata, aan het geometrische portret of aan uw foto, of laat de plaat zonder tekst.",
 close="Het zou ons een eer zijn om u te helpen op waardige wijze afscheid te nemen van uw geliefde hond.",
 core=["gedenkplaat hond", "geometrische hond", "aandenken huisdier", "grafmarkering", "grafplaat"],
 pool=["keramische plaat", "plaat met naam", "plaat met foto", "dierengrafsteen", "gedenkstuk", "condoleance", "ter herinnering", "tuinherinnering", "geometrisch beeld", "hondenportret", "begraafplaats hond", "herinnering dier", "weerbestendige plaat", "ovale herdenkplaat", "buiten herdenken", "gedenksteen dier", "regenboogbrug", "troostcadeau"])
L["fr"] = dict(name="Français", form="vous",
 titles=["{B} plaque commémorative, portrait géométrique de chien sur céramique, plaque tombale personnalisée",
  "{B} plaque tombale en céramique avec portrait géométrique, cadeau après la perte d'un chien",
  "{B} souvenir géométrique, plaque ovale en céramique, nom ou photo sur demande",
  "{B} repère de tombe, plaque en céramique avec tête de chien géométrique, cadeau commémoratif personnalisé",
  "{B} plaque tombale, graphisme géométrique sur céramique, avec votre photo sur demande",
  "{B} pierre tombale pour animal, portrait géométrique moderne, cadeau de condoléances"],
 A=["Cette plaque commémorative pour un chien de race {B} est en céramique, ornée d'un portrait géométrique moderne composé de fines facettes aux couleurs de la race.",
  "Une plaque tombale en céramique pour votre chien (race : {B}) avec un portrait géométrique de la race.",
  "Gardez le souvenir de votre chien de race {B} avec une plaque en céramique imprimée d'un portrait géométrique de la race.",
  "Cette plaque commémorative en céramique montre un chien de race {B} sous forme de portrait géométrique, une manière moderne d'honorer un compagnon bien-aimé.",
  "Un repère de tombe en céramique avec une tête géométrique de chien de race {B} : un portrait moderne qui garde vivant le souvenir de votre chien."],
 B=["Placez-la sur une tombe ou dans tout autre lieu de souvenir, en hommage au chien qui a partagé votre vie.",
  "Elle peut marquer une tombe ou un autre lieu important pour vous, où vous vous souvenez de votre animal bien-aimé.",
  "Elle servira de repère de tombe ou de marque dans un autre lieu de souvenir. Elle est adaptée à une utilisation en extérieur."],
 C=["Si vous préférez garder le souvenir de votre propre chien, choisissez votre photo et nous l'imprimerons à la place du motif présenté dans l'annonce.",
  "Vous pouvez ajouter le nom de votre chien, ou son nom et ses dates de vie, au-dessus du portrait.",
  "Vous préférez le portrait de votre propre chien ? Joignez une photo et nous l'imprimerons en version d'origine ou avec l'arrière-plan supprimé."],
 portrait="- Portrait géométrique moderne d'un chien de race {B} ou avec votre propre photo",
 th="UN SOUVENIR QUI RESTE AVEC VOUS",
 tt="Une plaque en céramique est une manière douce de garder vivant le souvenir d'un chien disparu. Le bord lisse ne demande aucun cadre particulier, l'impression de haute qualité est conçue pour durer, et la personnalisation rend la plaque vraiment unique.",
 style="- Style : avec votre propre photo, choisissez la version d'origine ou la couleur avec arrière-plan supprimé.",
 nm="- Nom et dates : ajoutez le nom de votre chien, ou son nom et ses dates de vie, au portrait géométrique ou à votre photo, ou laissez la plaque sans texte.",
 close="Ce sera un honneur pour nous de vous aider à dire adieu avec dignité à votre chien bien-aimé.",
 core=["plaque pour chien", "chien géométrique", "souvenir animal", "repère de tombe", "plaque tombale"],
 pool=["plaque céramique", "plaque avec nom", "plaque avec photo", "tombe animal", "objet commémoratif", "condoléances", "à la mémoire", "souvenir de jardin", "art géométrique", "portrait de chien", "tombe de chien", "mémoire animal", "plaque résistante", "plaque ovale", "hommage extérieur", "pierre du souvenir", "pont arc-en-ciel", "cadeau de deuil"])
L["it"] = dict(name="Italiano", form="Lei",
 titles=["{B} targa commemorativa, ritratto geometrico del cane su ceramica, targa tombale personalizzata",
  "{B} targa tombale in ceramica con ritratto geometrico, regalo dopo la perdita di un cane",
  "{B} ricordo geometrico, targa ovale in ceramica, nome o foto su richiesta",
  "{B} segno per la tomba, targa in ceramica con testa geometrica di cane, regalo commemorativo personalizzato",
  "{B} targa tombale, grafica geometrica su ceramica, con la sua foto su richiesta",
  "{B} lapide per animali, ritratto geometrico moderno, regalo di condoglianze"],
 A=["Questa targa commemorativa per un cane di razza {B} è in ceramica ed è decorata con un moderno ritratto geometrico, composto da fini sfaccettature nei colori della razza.",
  "Una targa tombale in ceramica per il Suo cane (razza: {B}) con un ritratto geometrico della razza.",
  "Conservi il ricordo del Suo cane di razza {B} con una targa in ceramica su cui è stampato un ritratto geometrico della razza.",
  "Questa targa commemorativa in ceramica mostra un cane di razza {B} come ritratto geometrico, un modo moderno per onorare un compagno amato.",
  "Un segno per la tomba in ceramica con una testa geometrica di cane di razza {B}: un ritratto moderno che tiene vivo il ricordo del Suo cane."],
 B=["La collochi su una tomba o in un altro luogo del ricordo, come omaggio al cane che ha condiviso la Sua vita.",
  "Può segnare una tomba o un altro luogo importante per Lei, in cui ricorda il Suo amato animale.",
  "Servirà come segno per la tomba o per un altro luogo del ricordo. È adatta all'uso all'aperto."],
 C=["Se preferisce ricordare il Suo cane, scelga la Sua foto e la stamperemo al posto del motivo mostrato nell'inserzione.",
  "Può aggiungere il nome del Suo cane, oppure nome e date di vita, sopra il ritratto.",
  "Preferisce il ritratto del Suo cane? Alleghi una foto e la stamperemo in originale o con lo sfondo rimosso."],
 portrait="- Moderno ritratto geometrico di un cane di razza {B} oppure con la sua foto",
 th="UN RICORDO CHE RESTA CON LEI",
 tt="Una targa in ceramica è un modo delicato per conservare il ricordo di un cane che non c'è più. Il bordo liscio non richiede una cornice speciale, la stampa di alta qualità è pensata per durare e la personalizzazione rende la targa davvero unica.",
 style="- Stile: con la Sua foto scelga l'originale oppure il colore con sfondo rimosso.",
 nm="- Nome e date: aggiunga il nome del Suo cane, oppure nome e date di vita, al ritratto geometrico o alla Sua foto, o lasci la targa senza testo.",
 close="Sarà un onore per noi aiutarla a dire addio con dignità al Suo amato cane.",
 core=["targa per cane", "cane geometrico", "ricordo animale", "segno per tomba", "targa tombale"],
 pool=["targa ceramica", "targa con nome", "targa con foto", "lapide animale", "pensiero in ricordo", "condoglianze", "in ricordo di", "ricordo giardino", "arte geometrica", "ritratto di cane", "tomba del cane", "memoria animale", "targa resistente", "targa ovale", "omaggio all'aperto", "pietra del ricordo", "ponte arcobaleno", "regalo di lutto"])
L["pt"] = dict(name="Português (europeu)", form="a sua / o seu",
 titles=["{B} placa memorial, retrato geométrico de cão em cerâmica, placa tumular personalizada",
  "{B} placa tumular em cerâmica com retrato geométrico, presente após a perda de um cão",
  "{B} recordação geométrica, placa oval em cerâmica, nome ou foto à escolha",
  "{B} marca de sepultura, placa em cerâmica com cabeça geométrica de cão, presente memorial personalizado",
  "{B} placa tumular, arte geométrica em cerâmica, com a sua foto a pedido",
  "{B} lápide para animal, retrato geométrico moderno, presente de condolências"],
 A=["Esta placa memorial para um cão da raça {B} é de cerâmica e está decorada com um retrato geométrico moderno, composto por pequenas facetas nas cores da raça.",
  "Uma placa tumular em cerâmica para o seu cão (raça: {B}) com um retrato geométrico da raça.",
  "Guarde a memória do seu cão da raça {B} com uma placa de cerâmica impressa com um retrato geométrico da raça.",
  "Esta placa memorial em cerâmica mostra um cão da raça {B} como retrato geométrico, uma forma moderna de homenagear um companheiro querido.",
  "Uma marca de sepultura em cerâmica com uma cabeça geométrica de cão da raça {B}: um retrato moderno que mantém viva a memória do seu cão."],
 B=["Coloque-a numa sepultura ou noutro lugar de memória, em homenagem ao cão que partilhou a sua vida.",
  "Pode assinalar uma sepultura ou outro lugar importante para si, onde recorda o seu animal querido.",
  "Servirá como marca de sepultura ou de outro lugar de memória. Está preparada para uso no exterior."],
 C=["Se preferir recordar o seu próprio cão, escolha a sua foto e imprimi-la-emos em vez do motivo mostrado no anúncio.",
  "Pode acrescentar o nome do seu cão, ou nome e datas de vida, acima do retrato.",
  "Prefere o retrato do seu próprio cão? Anexe uma foto e imprimi-la-emos no original ou com o fundo removido."],
 portrait="- Retrato geométrico moderno de um cão da raça {B} ou com a sua própria foto",
 th="UMA LEMBRANÇA QUE FICA CONSIGO",
 tt="Uma placa de cerâmica é uma forma delicada de guardar a memória de um cão que partiu. A borda lisa não precisa de moldura especial, a impressão de alta qualidade foi pensada para durar e a personalização torna a placa verdadeiramente sua.",
 style="- Estilo: com a sua própria foto, escolha o original ou a cor com o fundo removido.",
 nm="- Nome e datas: adicione o nome do seu cão, ou nome e datas de vida, ao retrato geométrico ou à sua foto, ou deixe a placa sem texto.",
 close="Será uma honra para nós ajudar a dar um adeus digno ao seu querido cão.",
 core=["placa para cão", "cão geométrico", "lembrança animal", "marca de sepultura", "placa tumular"],
 pool=["placa cerâmica", "placa com nome", "placa com foto", "lápide animal", "objeto memorial", "condolências", "em memória de", "lembrança jardim", "arte geométrica", "retrato de cão", "sepultura de cão", "memória animal", "placa resistente", "placa oval", "homenagem exterior", "pedra de memória", "ponte arco-íris", "presente de luto"])
L["es"] = dict(name="Español", form="tú",
 titles=["{B} placa conmemorativa, retrato geométrico de perro en cerámica, placa de tumba personalizada",
  "{B} lápida de cerámica con retrato geométrico, regalo tras la pérdida de un perro",
  "{B} recuerdo geométrico, placa ovalada de cerámica, nombre o foto a elegir",
  "{B} señal de tumba, placa de cerámica con cabeza geométrica de perro, regalo conmemorativo personalizado",
  "{B} placa funeraria, arte geométrico en cerámica, con tu foto si lo deseas",
  "{B} lápida para mascota, retrato geométrico moderno, regalo de condolencias"],
 A=["Esta placa conmemorativa para un perro de raza {B} es de cerámica y está decorada con un retrato geométrico moderno, formado por finas facetas en los colores de la raza.",
  "Una lápida de cerámica para tu perro (raza: {B}) con un retrato geométrico de la raza.",
  "Guarda el recuerdo de tu perro de raza {B} con una placa de cerámica impresa con un retrato geométrico de la raza.",
  "Esta placa conmemorativa de cerámica muestra a un perro de raza {B} como retrato geométrico, una forma moderna de honrar a un compañero querido.",
  "Una señal de tumba de cerámica con una cabeza geométrica de perro de raza {B}: un retrato moderno que mantiene vivo el recuerdo de tu perro."],
 B=["Colócala en una tumba o en cualquier otro lugar de recuerdo, como homenaje al perro que compartió tu vida.",
  "Puede señalar una tumba u otro lugar importante para ti, donde recuerdas a tu querido animal.",
  "Servirá como señal de tumba o de otro lugar de recuerdo. Está preparada para su uso en exterior."],
 C=["Si prefieres recordar a tu propio perro, elige tu foto y la imprimiremos en lugar del diseño que se ve en el anuncio.",
  "Puedes añadir el nombre de tu perro, o nombre y fechas de vida, encima del retrato.",
  "¿Prefieres el retrato de tu propio perro? Adjunta una foto y la imprimiremos en el original o con el fondo eliminado."],
 portrait="- Retrato geométrico moderno de un perro de raza {B} o con tu propia foto",
 th="UN RECUERDO QUE SE QUEDA CONTIGO",
 tt="Una placa de cerámica es una forma delicada de guardar el recuerdo de un perro que se ha ido. El borde liso no necesita un marco especial, la impresión de alta calidad está pensada para durar y la personalización hace que la placa sea realmente tuya.",
 style="- Estilo: con tu propia foto, elige el original o el color con el fondo eliminado.",
 nm="- Nombre y fechas: añade el nombre de tu perro, o nombre y fechas de vida, al retrato geométrico o a tu foto, o deja la placa sin texto.",
 close="Será un honor para nosotros ayudarte a despedirte con dignidad de tu querido perro.",
 core=["placa para perro", "perro geométrico", "recuerdo mascota", "señal de tumba", "placa funeraria"],
 pool=["placa cerámica", "placa con nombre", "placa con foto", "lápida mascota", "objeto conmemorativo", "condolencias", "en memoria de", "recuerdo jardín", "arte geométrico", "retrato de perro", "tumba de perro", "memoria mascota", "placa resistente", "placa ovalada", "homenaje exterior", "piedra de recuerdo", "puente arcoíris", "regalo de duelo"])
L["sv"] = dict(name="svenska", form="du",
 titles=["{B} minnesplatta, geometriskt hundporträtt på keramik, personlig gravplatta",
  "{B} gravplatta i keramik med geometriskt porträtt, present efter förlusten av en hund",
  "{B} geometriskt minne, oval keramikplatta, namn eller foto efter önskemål",
  "{B} gravmarkering, keramikplatta med geometriskt hundhuvud, personlig minnesgåva",
  "{B} gravsten, geometrisk grafik på keramik, med ditt eget foto på begäran",
  "{B} husdjursgravsten, modernt geometriskt porträtt, present vid kondoleans"],
 A=["Den här minnesplattan för en hund av rasen {B} är gjord av keramik och dekorerad med ett modernt geometriskt porträtt, uppbyggt av fina fasetter i rasens färger.",
  "En gravplatta i keramik för din hund (ras: {B}) med ett geometriskt porträtt av rasen.",
  "Bevara minnet av din hund av rasen {B} med en keramikplatta tryckt med ett geometriskt porträtt av rasen.",
  "Den här minnesplattan i keramik visar en hund av rasen {B} som ett geometriskt porträtt, ett modernt sätt att hedra en älskad följeslagare.",
  "En gravmarkering i keramik med ett geometriskt huvud av en hund av rasen {B}: ett modernt porträtt som håller minnet av din hund nära."],
 B=["Placera den på en grav eller på en annan minnesplats, som en hyllning till hunden som delade ditt liv.",
  "Den kan markera en grav eller en annan plats som är viktig för dig, där du minns ditt älskade djur.",
  "Den fungerar som gravmarkering eller som minnesmärke på en annan minnesplats. Den är gjord för användning utomhus."],
 C=["Om du hellre vill minnas din egen hund, välj ditt eget foto så trycker vi det i stället för motivet som visas i annonsen.",
  "Du kan lägga till din hunds namn, eller namn och levnadsdatum, ovanför porträttet.",
  "Föredrar du ett porträtt av din egen hund? Bifoga ett foto så trycker vi det i original eller med borttagen bakgrund."],
 portrait="- Modernt geometriskt porträtt av en hund av rasen {B} eller med ditt eget foto",
 th="ETT MINNE SOM STANNAR HOS DIG",
 tt="En keramikplatta är ett varsamt sätt att bevara minnet av en hund som har gått bort. Den släta kanten behöver ingen särskild ram, det högkvalitativa trycket är gjort för att hålla och med personligt tryck blir plattan helt din egen.",
 style="- Stil: välj originalet eller färg med borttagen bakgrund för ditt eget foto.",
 nm="- Namn och datum: lägg till din hunds namn, eller namn och levnadsdatum, till det geometriska porträttet eller till ditt foto, eller lämna plattan utan text.",
 close="Det vore en ära för oss att hjälpa dig att ta ett värdigt farväl av din älskade hund.",
 core=["hund minnesplatta", "geometrisk hund", "minne av husdjur", "gravmarkering", "gravplatta"],
 pool=["keramikplatta", "platta med namn", "platta med foto", "husdjursgrav", "minnessak", "kondoleans", "till minne av", "trädgårdsminne", "geometrisk konst", "hundporträtt", "grav för hund", "husdjursminne", "väderfast platta", "oval minnesplatta", "minne utomhus", "minnessten djur", "regnbågsbron", "sorgpresent"])


def tile_paras(code):
    t = (TPL / f"tlumaczenie_{code}_plytka.md").read_text(encoding="utf-8")
    return re.search(r"```\n(.*?)\n```", t, re.S).group(1).split("\n\n")


def main():
    for code, d in L.items():
        for k in ("core", "pool"):
            for x in d[k]:
                assert len(x) <= 20, (code, x, len(x))
        assert len(d["titles"]) == 6 and len(d["A"]) == 5 and len(d["B"]) == 3 and len(d["C"]) == 3 and len(d["core"]) == 5 and len(d["pool"]) == 18, code
        for tt in d["titles"]:
            assert len(tt.replace("{B}", "Basset Fauve de Bretagne Kurzhaar")) <= 140, (code, tt)
        p = tile_paras(code)
        sh = p[0].split("\n")
        short = "\n".join([sh[0], sh[1], d["portrait"]] + sh[3:])
        ps = p[2].split("\n")  # nagłówek, wstęp, Twoje zdjęcie, styl, imię i daty, orientacja
        pers = "\n".join([ps[0], ps[1], ps[2], d["style"], d["nm"], ps[5]])
        fixed = "\n\n".join([short, d["th"] + "\n" + d["tt"], pers, p[3], d["close"], p[5]])
        md = [f"# Tłumaczenie ({d['name']}): płytki ceramiczne \"with a Graphics\" (geometryczne psy, 100 ofert; szkic Claude'a, bez weryfikacji osoby natywnej, 03.11.2026)", "",
              "Status: EN i PL zatwierdzone przez właścicielkę 03.11.2026. `{B}` = nazwa rasy z Rasy.xlsx dla tego języka. Wspólne zdania (zdjęcie, orientacja, pytania, zamówienia międzynarodowe) z zatwierdzonych szablonów płytek \"with a Photo\". "
              f"Forma zwracania się: {d['form']}. Pola personalizacji Etsy nie są tłumaczone.", "", "## Tytuł (6 wzorców)"] + [f"{i}. {x}" for i, x in enumerate(d["titles"], 1)] \
             + ["", "## Pierwszy akapit: banki", "**A**"] + [f"- A{i}: {x}" for i, x in enumerate(d["A"], 1)] + ["", "**B**"] + [f"- B{i}: {x}" for i, x in enumerate(d["B"], 1)] \
             + ["", "**C**"] + [f"- C{i}: {x}" for i, x in enumerate(d["C"], 1)] + ["", "## Sekcje stałe", "```", fixed, "```", "", "## Tagi (max 20 znaków, długości policzone skryptem)",
                "**Stałe:** " + ", ".join(f"{x} ({len(x)})" for x in d["core"]), "**Pula:** " + ", ".join(f"{x} ({len(x)})" for x in d["pool"]), ""]
        (TPL / f"plakietki_grafika_tlumaczenie_{code}.md").write_text("\n".join(md), encoding="utf-8")
        print(code, "ok")


if __name__ == "__main__":
    main()
