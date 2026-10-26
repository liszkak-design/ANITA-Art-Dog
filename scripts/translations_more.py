"""Data for the remaining languages (FR, IT, ES, PT, SV). Merged into translations.L by translations.py.
Drafts by Claude, to be checked by a native speaker. Formal address: FR (vous), IT (Lei); informal: ES (tú), PT (o seu),
SV (du). Section heading is the analogue of the Polish "Pamiątka po Twoim przyjacielu". Banks B avoid "lasting/durable".
"""

CORE_SP = lambda s, a, b: (a, b)

MORE = {}

MORE["fr"] = dict(
    name="Français", col="FR nazwa", basket="Plaque commémorative en céramique", feat="à poil long",
    sp={"kot": dict(S="chat"), "pies": dict(S="chien"), "koń": dict(S="cheval"), "kucyk": dict(S="poney")},
    titles=["{B} plaque commémorative pour {S}, plaque funéraire en céramique personnalisée avec photo",
            "{B} plaque commémorative animal, plaque de tombe en céramique avec votre photo, cadeau deuil",
            "{B} plaque funéraire pour {S}, plaque de tombe en céramique avec photo, souvenir personnalisé",
            "{B} décoration de tombe avec photo, plaque en céramique sur mesure pour tombe ou jardin",
            "{B} plaque commémorative avec photo, plaque funéraire céramique personnalisée, en souvenir",
            "{B} plaque commémorative en céramique, plaque de tombe avec votre photo pour {S}, souvenir"],
    A=["{B} : plaque funéraire en céramique ornée d'un portrait au style croquis, créée en souvenir de votre {S} bien-aimé.",
       "Plaque commémorative en céramique pour votre {S} (race : {B}) avec un portrait au style croquis.",
       "Plaque funéraire commémorative avec portrait au style croquis, race : {B}. Un souvenir en céramique de votre {S}.",
       "Plaque commémorative en céramique avec portrait au style croquis, race : {B}. Conçue pour rendre hommage à un compagnon bien-aimé.",
       "{B} – plaque commémorative en céramique : un portrait au style croquis qui garde vivant le souvenir de votre {S}."],
    B=["Placez-la sur une tombe ou dans tout autre lieu de recueillement, en hommage à votre {S} qui a fait partie de votre vie.",
       "Elle peut marquer une tombe ou prendre place dans un endroit calme qui compte pour vous, en souvenir de votre {S} bien-aimé.",
       "Elle sert de marque de tombe ou de souvenir dans un lieu de recueillement, un hommage à votre {S}.",
       "Un hommage digne pour une tombe ou pour tout endroit où vous pensez à votre {S}, résistant aux intempéries."],
    C=["Si vous préférez honorer votre propre {S}, envoyez-nous une photo et nous l'imprimerons à la place du motif.",
       "Vous préférez le portrait de votre propre {S} ? Joignez une photo et nous l'imprimerons sur la plaque.",
       "Vous pouvez aussi faire imprimer sur la plaque une photo de votre propre {S}.",
       "À la place du motif, nous pouvons imprimer votre photo, il suffit de la joindre lors de la commande."],
    fixed='''EN BREF
- Plaque ovale en céramique, env. 10,5 x 7,5 cm (4,13 x 2,95 po), épaisseur env. 0,5 cm (0,2 po)
- Portrait au style croquis (race : {B}) ou avec votre propre photo
- Impression résistante aux intempéries, qui ne se décolore pas
- Bord lisse et arrondi, aucun cadre ni support supplémentaire nécessaire
- Sans trou ni crochet au dos, à fixer avec une colle universelle
- Personnalisation possible : votre photo, style d'impression, nom et dates

SOUVENIR DE VOTRE AMI
Une plaque en céramique est une manière douce et durable de garder vivant le souvenir de votre {S}. Le bord lisse ne demande aucun cadre particulier, l'impression de haute qualité est conçue pour durer, et la personnalisation rend la plaque vraiment unique.

PERSONNALISATION
Commandez la plaque telle qu'elle est présentée, ou personnalisez-la. Chacune des options ci-dessous est facultative.
- Votre photo : nous pouvons imprimer n'importe quelle photo que vous nous envoyez. Joignez-la dans le champ de personnalisation lors de la commande, ou envoyez-la par message Etsy.
- Style : choisissez la photo d'origine, la couleur avec arrière-plan supprimé, ou un style crayon comme sur les photos de l'annonce.
- Nom et dates : ajoutez le nom de votre {S}, ou son nom et ses dates de vie, ou laissez la plaque sans texte.
- Orientation : une plaque avec votre photo peut être placée à la verticale ou à l'horizontale.

Une question sur la personnalisation ? Écrivez-nous, nous serons heureux de vous aider.

Ce sera un honneur pour nous de vous aider à dire adieu avec dignité à votre {S} bien-aimé.

COMMANDES INTERNATIONALES
Nos produits sont expédiés depuis la Pologne ; des frais d'importation peuvent donc s'appliquer dans certains pays. Ils ne concernent pas les pays de l'UE, le Royaume-Uni ni les États-Unis. En cas de doute, contactez-nous pour obtenir des précisions.''',
    core=["plaque commémorative", "plaque de tombe", "plaque funéraire", "cadeau deuil animal", "plaque avec photo"],
    spec={"kot": ("plaque pour chat", "tombe de chat"), "pies": ("plaque pour chien", "tombe de chien"),
          "koń": ("plaque pour cheval", "tombe de cheval"), "kucyk": ("plaque pour poney", "tombe de poney")},
    pool=["plaque en céramique", "plaque sur mesure", "stèle animal", "souvenir extérieur", "souvenir de jardin", "souvenir deuil",
          "cadeau condoléances", "cadeau souvenir", "en mémoire", "pont arc-en-ciel", "souvenir animal", "photo sur céramique",
          "condoléances animal", "décoration de tombe", "plaque résistante", "plaque ovale", "plaque tombe animal",
          "plaque cimetière", "deuil animal", "cadeau mémoire", "hommage animal", "pierre souvenir", "plaque photo animal",
          "souvenir avec photo", "plaque de sépulture", "dans nos cœurs", "souvenir après perte", "plaque pour tombe",
          "plaque mémorial", "tombe animal"])

MORE["it"] = dict(
    name="Italiano", col="IT nazwa", basket="Targa commemorativa in ceramica", feat="a pelo lungo",
    sp={"kot": dict(S="gatto", P="il suo gatto", DEL="del suo gatto", AL="al suo gatto"),
        "pies": dict(S="cane", P="il suo cane", DEL="del suo cane", AL="al suo cane"),
        "koń": dict(S="cavallo", P="il suo cavallo", DEL="del suo cavallo", AL="al suo cavallo"),
        "kucyk": dict(S="pony", P="il suo pony", DEL="del suo pony", AL="al suo pony")},
    titles=["{B} targa commemorativa per {S}, targa funeraria in ceramica personalizzata con foto, ricordo",
            "{B} targa commemorativa animale, targa per tomba in ceramica su misura con la sua foto, regalo lutto",
            "{B} targa funeraria per {S}, targa tomba in ceramica con foto, ricordo personalizzato",
            "{B} decorazione tomba con foto, targa in ceramica su misura per tomba o giardino, ricordo",
            "{B} targa commemorativa con foto, targa funeraria in ceramica personalizzata, in ricordo {DEL}",
            "{B} targa commemorativa in ceramica, targa tomba con la sua foto per {S}, ricordo animale"],
    A=["{B}: targa funeraria in ceramica con ritratto in stile schizzo, creata in ricordo {DEL}.",
       "Targa commemorativa in ceramica per {P} (razza: {B}) con ritratto in stile schizzo.",
       "Targa funeraria commemorativa con ritratto in stile schizzo, razza: {B}. Un ricordo in ceramica {DEL}.",
       "Targa commemorativa in ceramica con ritratto in stile schizzo, razza: {B}. Pensata per rendere omaggio a un compagno amato.",
       "{B} – targa commemorativa in ceramica: un ritratto in stile schizzo che conserva il ricordo {DEL}."],
    B=["La collochi su una tomba o in un altro luogo del ricordo, come omaggio {AL}, che è stato parte della sua vita.",
       "Può segnare una tomba o trovare posto in un luogo tranquillo e importante per lei, in ricordo {DEL}.",
       "Serve come segno sulla tomba o come ricordo in un luogo di raccoglimento, un omaggio {AL}.",
       "Un omaggio degno per una tomba o per ogni luogo in cui ricorda {P}, resistente alle intemperie."],
    C=["Se preferisce ricordare il suo animale, ci invii una foto e la stamperemo al posto del motivo.",
       "Preferisce il ritratto del suo animale? Alleghi una foto e la stamperemo sulla targa.",
       "Può anche far stampare sulla targa una foto del suo animale.",
       "Al posto del motivo possiamo stampare la sua foto, basta allegarla all'ordine."],
    fixed='''IN BREVE
- Targa ovale in ceramica, circa 10,5 x 7,5 cm (4,13 x 2,95 pollici), spessore circa 0,5 cm (0,2 pollici)
- Ritratto in stile schizzo (razza: {B}) oppure con la sua foto
- Stampa resistente alle intemperie, non sbiadisce
- Bordo liscio e arrotondato, nessuna cornice o supporto aggiuntivo necessario
- Senza foro né gancio sul retro, da fissare con una colla universale
- Personalizzazione disponibile: la sua foto, stile di stampa, nome e date

RICORDO DEL SUO AMICO
Una targa in ceramica è un modo delicato e duraturo per conservare il ricordo {DEL}. Il bordo liscio non richiede una cornice speciale, la stampa di alta qualità è pensata per durare e la personalizzazione rende la targa davvero unica.

PERSONALIZZAZIONE
Ordini la targa esattamente come illustrata, oppure la personalizzi. Ognuna delle opzioni seguenti è facoltativa.
- La sua foto: possiamo stampare qualsiasi foto ci invii. La alleghi nel campo di personalizzazione durante l'ordine, oppure ce la invii con un messaggio Etsy.
- Stile: scelga la foto originale, il colore con sfondo rimosso oppure lo stile a matita come nelle foto dell'inserzione.
- Nome e date: aggiunga il nome {DEL}, oppure nome e date di vita, o lasci la targa senza testo.
- Orientamento: una targa con la sua foto può essere posizionata in verticale o in orizzontale.

Ha domande sulla personalizzazione? Ci scriva, saremo lieti di aiutarla.

Sarà un onore per noi aiutarla a dire addio con dignità {AL}.

ORDINI INTERNAZIONALI
I nostri prodotti vengono spediti dalla Polonia, quindi in alcuni paesi possono essere applicati costi di importazione. Questi costi non riguardano i paesi UE, il Regno Unito e gli Stati Uniti. In caso di dubbi, ci contatti per i dettagli.''',
    core=["targa commemorativa", "targa per tomba", "targa funeraria", "regalo lutto animale", "targa con foto"],
    spec={"kot": ("targa per gatto", "tomba del gatto"), "pies": ("targa per cane", "tomba del cane"),
          "koń": ("targa per cavallo", "tomba del cavallo"), "kucyk": ("targa per pony", "tomba del pony")},
    pool=["targa in ceramica", "targa personalizzata", "lapide animale", "ricordo all'aperto", "ricordo da giardino", "ricordo lutto",
          "regalo condoglianze", "regalo ricordo", "in ricordo di", "ponte arcobaleno", "ricordo animale", "foto su ceramica",
          "condoglianze animale", "decorazione tomba", "targa resistente", "targa ovale", "targa tomba animale", "targa cimitero",
          "lutto animale", "regalo commemorativo", "omaggio all'animale", "pietra del ricordo", "targa foto animale",
          "ricordo con foto", "lapide con targa", "sempre nel cuore", "ricordo dopo perdita", "targa lapide", "targa memoriale",
          "tomba animale"])

MORE["es"] = dict(
    name="Español", col="ES nazwa", basket="Placa conmemorativa de cerámica", feat="pelo largo",
    sp={"kot": dict(S="gato"), "pies": dict(S="perro"), "koń": dict(S="caballo"), "kucyk": dict(S="pony")},
    titles=["{B} placa conmemorativa para {S}, placa funeraria de cerámica personalizada con foto, recuerdo",
            "{B} placa conmemorativa mascota, placa para tumba de cerámica con tu foto, regalo de duelo",
            "{B} placa funeraria para {S}, placa de tumba de cerámica con foto, recuerdo personalizado",
            "{B} decoración de tumba con foto, placa de cerámica a medida para tumba o jardín, recuerdo",
            "{B} placa conmemorativa con foto, placa funeraria de cerámica personalizada, en memoria",
            "{B} placa conmemorativa de cerámica, placa de tumba con tu foto para {S}, recuerdo de mascota"],
    A=["{B}: placa funeraria de cerámica con un retrato estilo boceto, creada en recuerdo de tu {S}.",
       "Placa conmemorativa de cerámica para tu {S} (raza: {B}) con un retrato estilo boceto.",
       "Placa funeraria conmemorativa con retrato estilo boceto, raza: {B}. Un recuerdo de cerámica de tu {S}.",
       "Placa conmemorativa de cerámica con retrato estilo boceto, raza: {B}. Creada para rendir homenaje a un compañero querido.",
       "{B} – placa conmemorativa de cerámica: un retrato estilo boceto que guarda el recuerdo de tu {S}."],
    B=["Colócala en una tumba o en cualquier otro lugar de recuerdo, como homenaje a tu {S}, que fue parte de tu vida.",
       "Puede marcar una tumba o ocupar un lugar tranquilo y especial para ti, como recuerdo de tu {S} querido.",
       "Sirve como señal de tumba o como recuerdo en un lugar de homenaje, un tributo a tu {S}.",
       "Un homenaje digno para una tumba o para cualquier lugar donde recuerdes a tu {S}, resistente a la intemperie."],
    C=["Si prefieres recordar a tu propio {S}, envíanos una foto y la imprimiremos en lugar del diseño.",
       "¿Prefieres el retrato de tu propio {S}? Adjunta una foto y la imprimiremos en la placa.",
       "También puedes encargar la placa con una foto de tu propio {S}.",
       "En lugar del diseño podemos imprimir tu foto, solo tienes que adjuntarla al hacer el pedido."],
    fixed='''EN RESUMEN
- Placa oval de cerámica, aprox. 10,5 x 7,5 cm (4,13 x 2,95 pulgadas), aprox. 0,5 cm (0,2 pulgadas) de grosor
- Retrato estilo boceto (raza: {B}) o con tu propia foto
- Impresión resistente a la intemperie que no se desvanece
- Borde liso y redondeado, no necesita marco ni soporte adicional
- Sin agujero ni gancho en la parte trasera, se fija con pegamento universal
- Personalización disponible: tu foto, estilo de impresión, nombre y fechas

RECUERDO DE TU AMIGO
Una placa de cerámica es una forma delicada y duradera de guardar el recuerdo de tu {S}. El borde liso no necesita un marco especial, la impresión de alta calidad está pensada para durar y la personalización hace que la placa sea realmente tuya.

PERSONALIZACIÓN
Pide la placa tal como se muestra o personalízala. Cada una de las opciones siguientes es voluntaria.
- Tu foto: podemos imprimir cualquier foto que nos envíes. Adjúntala en el campo de personalización al hacer el pedido o envíala por mensaje de Etsy.
- Estilo: elige la foto original, el color con el fondo eliminado o un estilo de dibujo a lápiz como el de las fotos del anuncio.
- Nombre y fechas: añade el nombre de tu {S}, o su nombre y fechas de vida, o deja la placa sin texto.
- Orientación: una placa con tu foto puede colocarse en vertical o en horizontal.

¿Tienes preguntas sobre la personalización? Escríbenos, estaremos encantados de ayudarte.

Será un honor para nosotros ayudarte a despedirte con dignidad de tu {S} querido.

PEDIDOS INTERNACIONALES
Nuestros productos se envían desde Polonia, por lo que en algunos países pueden aplicarse gastos de importación. Estos gastos no afectan a los países de la UE, el Reino Unido ni Estados Unidos. Si tienes dudas, contáctanos para conocer los detalles.''',
    core=["placa conmemorativa", "placa para tumba", "placa funeraria", "regalo duelo mascota", "placa con foto"],
    spec={"kot": ("placa para gato", "tumba de gato"), "pies": ("placa para perro", "tumba de perro"),
          "koń": ("placa para caballo", "tumba de caballo"), "kucyk": ("placa para pony", "tumba de pony")},
    pool=["placa de cerámica", "placa personalizada", "lápida mascota", "recuerdo exterior", "recuerdo de jardín", "recuerdo de duelo",
          "regalo condolencias", "regalo recuerdo", "en memoria de", "puente arcoíris", "recuerdo mascota", "foto en cerámica",
          "condolencias mascota", "decoración tumba", "placa resistente", "placa ovalada", "placa tumba mascota", "placa cementerio",
          "duelo mascota", "regalo homenaje", "homenaje mascota", "piedra recuerdo", "placa foto mascota", "recuerdo con foto",
          "lápida con placa", "en el corazón", "recuerdo pérdida", "placa lápida", "placa memorial", "tumba mascota"])

MORE["pt"] = dict(
    name="Português", col="PT nazwa", basket="Placa comemorativa em cerâmica", feat="pelo comprido",
    sp={"kot": dict(S="gato", P="o seu gato", DO="do seu gato", AO="ao seu gato"),
        "pies": dict(S="cão", P="o seu cão", DO="do seu cão", AO="ao seu cão"),
        "koń": dict(S="cavalo", P="o seu cavalo", DO="do seu cavalo", AO="ao seu cavalo"),
        "kucyk": dict(S="pónei", P="o seu pónei", DO="do seu pónei", AO="ao seu pónei")},
    titles=["{B} placa comemorativa para {S}, placa funerária em cerâmica personalizada com foto, lembrança",
            "{B} placa comemorativa animal, placa de túmulo em cerâmica com a sua foto, presente de luto",
            "{B} placa funerária para {S}, placa de túmulo em cerâmica com foto, lembrança personalizada",
            "{B} decoração de túmulo com foto, placa de cerâmica por medida para túmulo ou jardim, lembrança",
            "{B} placa comemorativa com foto, placa funerária em cerâmica personalizada, em memória {DO}",
            "{B} placa comemorativa em cerâmica, placa de túmulo com a sua foto para {S}, lembrança de animal"],
    A=["{B}: placa funerária em cerâmica com retrato em estilo esboço, criada em memória {DO}.",
       "Placa comemorativa em cerâmica para {P} (raça: {B}) com retrato em estilo esboço.",
       "Placa funerária comemorativa com retrato em estilo esboço, raça: {B}. Uma lembrança em cerâmica {DO}.",
       "Placa comemorativa em cerâmica com retrato em estilo esboço, raça: {B}. Criada para homenagear um companheiro querido.",
       "{B} – placa comemorativa em cerâmica: um retrato em estilo esboço que guarda a memória {DO}."],
    B=["Coloque-a num túmulo ou noutro local de memória, como homenagem {AO}, que fez parte da sua vida.",
       "Pode marcar um túmulo ou ocupar um lugar tranquilo e especial, em memória {DO}.",
       "Serve como marca de túmulo ou como lembrança num local de memória, uma homenagem {AO}.",
       "Uma homenagem digna para um túmulo ou para qualquer lugar onde recorda {P}, resistente às intempéries."],
    C=["Se preferir recordar o seu próprio animal, envie-nos uma foto e imprimiremos no lugar do motivo.",
       "Prefere o retrato do seu próprio animal? Anexe uma foto e imprimiremos na placa.",
       "Também pode encomendar a placa com uma foto do seu próprio animal.",
       "No lugar do motivo podemos imprimir a sua foto, basta anexá-la ao fazer a encomenda."],
    fixed='''EM RESUMO
- Placa oval em cerâmica, aprox. 10,5 x 7,5 cm (4,13 x 2,95 polegadas), aprox. 0,5 cm (0,2 polegadas) de espessura
- Retrato em estilo esboço (raça: {B}) ou com a sua própria foto
- Impressão resistente às intempéries, que não desbota
- Borda lisa e arredondada, não precisa de moldura nem suporte adicional
- Sem furo nem gancho na parte de trás, fixa-se com cola universal
- Personalização disponível: a sua foto, estilo de impressão, nome e datas

LEMBRANÇA DO SEU AMIGO
Uma placa de cerâmica é uma forma delicada e duradoura de guardar a memória {DO}. A borda lisa não precisa de moldura especial, a impressão de alta qualidade foi pensada para durar e a personalização torna a placa verdadeiramente sua.

PERSONALIZAÇÃO
Encomende a placa tal como é apresentada ou personalize-a. Cada uma das opções abaixo é opcional.
- A sua foto: podemos imprimir qualquer foto que nos envie. Anexe-a no campo de personalização ao fazer a encomenda ou envie-a por mensagem do Etsy.
- Estilo: escolha a foto original, a cor com o fundo removido ou um estilo de desenho a lápis como nas fotos do anúncio.
- Nome e datas: adicione o nome {DO}, ou nome e datas de vida, ou deixe a placa sem texto.
- Orientação: uma placa com a sua foto pode ser colocada na vertical ou na horizontal.

Tem dúvidas sobre a personalização? Escreva-nos, teremos todo o gosto em ajudar.

Será uma honra para nós ajudar a dar um adeus digno {AO}.

ENCOMENDAS INTERNACIONAIS
Os nossos produtos são enviados da Polónia, pelo que em alguns países podem ser aplicados custos de importação. Estes custos não se aplicam aos países da UE, ao Reino Unido nem aos Estados Unidos. Em caso de dúvida, contacte-nos para obter detalhes.''',
    core=["placa comemorativa", "placa para túmulo", "placa funerária", "presente luto pet", "placa com foto"],
    spec={"kot": ("placa para gato", "túmulo de gato"), "pies": ("placa para cão", "túmulo de cão"),
          "koń": ("placa para cavalo", "túmulo de cavalo"), "kucyk": ("placa para pónei", "túmulo de pónei")},
    pool=["placa de cerâmica", "placa personalizada", "lápide animal", "lembrança exterior", "lembrança jardim", "lembrança de luto",
          "presente de pêsames", "presente lembrança", "em memória de", "ponte arco-íris", "lembrança animal", "foto em cerâmica",
          "pêsames animal", "decoração túmulo", "placa resistente", "placa oval", "placa túmulo animal", "placa cemitério",
          "luto animal", "presente homenagem", "homenagem animal", "pedra lembrança", "placa foto animal", "lembrança com foto",
          "lápide com placa", "sempre no coração", "lembrança da perda", "placa lápide", "placa memorial", "túmulo animal"])

MORE["sv"] = dict(
    name="Svenska", col="SV nazwa", basket="Minnesplatta i keramik", feat="långhårig",
    sp={"kot": dict(S="katt"), "pies": dict(S="hund"), "koń": dict(S="häst"), "kucyk": dict(S="ponny")},
    titles=["{B} minnesplatta för {S}, personlig gravplatta i keramik med foto, minne",
            "{B} minnesplatta för husdjur, gravplatta i keramik med ditt eget foto, present vid sorg",
            "{B} gravplatta för {S}, gravskylt i keramik med foto, personligt minne",
            "{B} gravdekoration med foto, keramikplatta för grav eller trädgård, minne av husdjur",
            "{B} minnesplatta med foto, personlig gravplatta i keramik, till minne av din {S}",
            "{B} minnesplatta i keramik, gravskylt med ditt foto för {S}, minne av husdjur"],
    A=["{B}: gravplatta i keramik med ett skissporträtt, skapad till minne av din {S}.",
       "Minnesplatta i keramik för din {S} (ras: {B}) med ett skissporträtt.",
       "Minnesplatta för grav med skissporträtt, ras: {B}. Ett minne i keramik av din {S}.",
       "Minnesplatta i keramik med skissporträtt, ras: {B}. Skapad för att hedra en älskad följeslagare.",
       "{B} – minnesplatta i keramik: ett skissporträtt som bevarar minnet av din {S}."],
    B=["Placera den på en grav eller på en annan minnesplats, som en hyllning till din {S} som var en del av ditt liv.",
       "Den kan markera en grav eller stå på en stilla plats som betyder något för dig, till minne av din älskade {S}.",
       "Den fungerar som gravmarkering eller som minne på en minnesplats, en hyllning till din {S}.",
       "En värdig hyllning för en grav eller vilken plats som helst där du minns din {S}, tålig mot väder och vind."],
    C=["Om du hellre vill minnas ditt eget djur, skicka oss ett foto så trycker vi det i stället för motivet.",
       "Vill du hellre ha ett porträtt av ditt eget djur? Bifoga ett foto så trycker vi det på plattan.",
       "Du kan också beställa plattan med ett foto av ditt eget djur.",
       "I stället för motivet kan vi trycka ditt foto, bifoga det bara när du beställer."],
    fixed='''KORT OM PRODUKTEN
- Oval keramikplatta, ca 10,5 x 7,5 cm (4,13 x 2,95 tum), ca 0,5 cm (0,2 tum) tjock
- Porträtt i skissstil (ras: {B}) eller med ditt eget foto
- Väderbeständigt tryck som inte bleknar
- Slät, rundad kant, ingen extra ram eller hållare behövs
- Utan hål eller krok på baksidan, fästs med universallim
- Personligt tryck möjligt: ditt foto, tryckstil, namn och datum

ETT MINNE AV DIN VÄN
En keramikplatta är ett varsamt och varaktigt sätt att bevara minnet av din {S}. Den släta kanten behöver ingen särskild ram, det högkvalitativa trycket är gjort för att hålla och med personligt tryck blir plattan helt din egen.

PERSONLIGT TRYCK
Beställ plattan precis som den visas, eller gör den personlig. Varje alternativ nedan är frivilligt.
- Ditt foto: vi kan trycka vilket foto som helst som du skickar oss. Bifoga det i personaliseringsfältet när du beställer, eller skicka det i ett Etsy-meddelande.
- Stil: välj originalfotot, färg med borttagen bakgrund eller en blyertsskiss i stil med bilderna i annonsen.
- Namn och datum: lägg till namnet på din {S}, eller namn och levnadsdatum, eller lämna plattan utan text.
- Orientering: en platta med ditt foto kan placeras stående eller liggande.

Har du frågor om personligt tryck? Skriv till oss, vi hjälper dig gärna.

Det vore en ära för oss att hjälpa dig att ta ett värdigt farväl av din {S}.

INTERNATIONELLA BESTÄLLNINGAR
Våra produkter skickas från Polen, så i vissa länder kan importavgifter tillkomma. Avgifterna gäller inte EU-länder, Storbritannien eller USA. Om du är osäker, kontakta oss så ger vi dig detaljerna.''',
    core=["minnesplatta", "gravplatta", "gravmarkering", "present sorg djur", "platta med foto"],
    spec={"kot": ("minnesplatta katt", "katt grav"), "pies": ("minnesplatta hund", "hund grav"),
          "koń": ("minnesplatta häst", "häst grav"), "kucyk": ("minnesplatta ponny", "ponny grav")},
    pool=["keramikplatta", "personlig platta", "gravsten djur", "minne utomhus", "trädgårdsminne", "minnessak sorg", "kondoleansgåva",
          "minnesgåva", "till minne av", "regnbågsbron", "husdjursminne", "foto på keramik", "kondoleans djur", "gravdekoration",
          "väderbeständig", "oval minnesplatta", "gravplatta djur", "kyrkogårdsskylt", "djursorg", "hyllningsgåva", "hylla husdjur",
          "minnessten", "fotoplatta djur", "minne med foto", "gravsten platta", "alltid i hjärtat", "minne efter förlust", "gravskylt",
          "minnestavla", "djurgrav"])
