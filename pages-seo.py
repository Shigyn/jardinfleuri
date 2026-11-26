# Jardin Fleuri : genere les pages SEO a partir de index.html (en-tete, pied et sections reutilises),
# plus sitemap.xml, robots.txt et 404.html.
# Usage : python -I pages-seo.py   (relancer apres toute modification de index.html)
import io, json, os, re

ICI = os.path.dirname(os.path.abspath(__file__))
SITE = 'https://shigyn.github.io/jardinfleuri/'
DOSSIER = '/jardinfleuri/'      # chemin du site sur GitHub Pages (pour la page 404)
APERCU = True                   # False a la mise en ligne : robots.txt ouvert

# Ancres de l'accueil qui deviennent des pages dediees
MENU = {'#creations': 'boutique/', '#evenements': 'evenements/', '#tombes': 'entretien-tombes/'}
# Ancres qui restent sur l'accueil (depuis une sous-page : ../#ancre)
ANCRES_ACCUEIL = ('#kevin', '#contact')
ETIQUETTE = 'sur-titre'
CTA = '<a class="bouton bouton-plein" href="tel:+33662354221">Appeler Kévin : 06 62 35 42 21</a>'
BOUTON_404 = 'bouton bouton-plein'

FAQ_BOUTIQUE = [
    ('Comment commander une création ?', 'Cliquez sur « Commander » sous le produit : vous arrivez sur la boutique sécurisée de Jardin Fleuri pour régler en ligne. Vous pouvez aussi appeler Kévin.'),
    ('Les fleurs séchées durent-elles longtemps ?', 'Oui, plusieurs années si elles restent à l’abri du soleil direct et de l’humidité. Un léger coup de sèche-cheveux à froid suffit à les dépoussiérer.'),
    ('Peut-on demander une création personnalisée ?', 'Oui : couleur, taille, prénom ou occasion, Kévin crée aussi sur mesure. Appelez-le pour en parler.'),
]
FAQ_EVENEMENTS = [
    ('Combien de temps à l’avance réserver pour un mariage ?', 'Idéalement deux à trois mois avant, pour choisir ensemble les fleurs et les couleurs. Pour les petites compositions, quelques semaines suffisent.'),
    ('Proposez-vous des fleurs de deuil ?', 'Oui : gerbes, couronnes et compositions de deuil, préparées avec soin et dans les délais. Appelez Kévin directement.'),
    ('Dans quelle zone intervenez-vous ?', 'À Teillé et dans les communes voisines du Pays d’Ancenis. Pour un événement plus loin, demandez un devis.'),
]
FAQ_TOMBES = [
    ('Je n’habite pas la région, comment faire ?', 'Commandez l’entretien en ligne ou par téléphone : Kévin s’occupe de la tombe de vos proches dans le Pays d’Ancenis, même si vous habitez loin.'),
    ('Que comprend l’entretien ?', 'Le nettoyage de la tombe en une visite. La formule à 60 € ajoute le fleurissement avec des fleurs de saison.'),
    ('Puis-je commander seulement des fleurs, sans nettoyage ?', 'Oui, les commandes sont ouvertes à tous, avec ou sans prestation de nettoyage.'),
    ('Existe-t-il un entretien régulier ?', 'Oui : la formule à l’année (660 €) assure un entretien régulier, toute l’année.'),
]

PAGES = [
    dict(chemin='boutique/', titre='Fleurs séchées et créations florales à Teillé | Jardin Fleuri',
         description='Cloches, cadres, couronnes et bijoux en fleurs séchées, plantes, cactus et senteurs, faits à Teillé (44). Commande en ligne sécurisée, créations sur mesure.',
         sur='La boutique', h1='Fleurs séchées et créations florales',
         intro='Cloches fleuries, cadres, couronnes, peignes et bijoux en fleurs séchées, mais aussi plantes, cactus et senteurs : chaque création est faite à la main par Kévin, à Teillé.',
         blocs=[('section', 'creations', None)], faq=FAQ_BOUTIQUE, fil='Boutique'),
    dict(chemin='evenements/', titre='Fleuriste mariage, anniversaire et deuil, Pays d’Ancenis | Jardin Fleuri',
         description='Bouquet de mariée, centres de table, décoration d’anniversaire, gerbes et couronnes de deuil : Jardin Fleuri compose vos fleurs d’événement à Teillé et dans le Pays d’Ancenis.',
         sur='Événements', h1='Les fleurs de vos événements',
         intro='Mariage, anniversaire ou hommage : Kévin, fleuriste diplômé, compose avec vous des fleurs à votre image, selon vos couleurs, la saison et votre budget. Devis gratuit.',
         blocs=[('section', 'evenements', None)], faq=FAQ_EVENEMENTS, fil='Événements'),
    dict(chemin='entretien-tombes/', titre='Entretien et fleurissement de tombes, Teillé et Pays d’Ancenis | Jardin Fleuri',
         description='Entretien de tombes dès 30 €, avec fleurissement 60 €, ou à l’année : Jardin Fleuri nettoie et fleurit les sépultures à Teillé et dans le Pays d’Ancenis, même à distance.',
         sur='Entretien de sépultures', h1='Entretien et fleurissement de tombes',
         intro='Vous habitez loin ou ne pouvez plus vous déplacer ? Kévin nettoie et fleurit la tombe de vos proches dans les cimetières de Teillé et du Pays d’Ancenis.',
         blocs=[('section', 'tombes', None), ('section', 'contact', None)], faq=FAQ_TOMBES, fil='Entretien de tombes'),
]

NL = '\n'

# ------------------------------------------------------------------ outils
def element(html, tag, ident):
    m = re.search(r'<%s\b[^>]*\bid="%s"[^>]*>' % (tag, re.escape(ident)), html)
    if not m:
        raise SystemExit('introuvable : %s#%s' % (tag, ident))
    pos, prof = m.end(), 1
    motif = re.compile(r'<(/?)%s\b' % tag)
    while prof:
        n = motif.search(html, pos)
        prof += -1 if n.group(1) else 1
        pos = n.end()
    return html[m.start():html.index('>', pos) + 1]

def pages_cibles():
    return set(v.split('#')[0] for v in MENU.values())

def reecrire_liens(bloc, prefixe):
    """Ancres devenues pages -> prefixe + page ; pages deja relatives -> prefixe + page ; ancres de l'accueil -> prefixe + ancre."""
    for ancre, page in MENU.items():
        bloc = bloc.replace('href="%s"' % ancre, 'href="%s%s"' % (prefixe, page))
    if prefixe:
        for page in pages_cibles():
            bloc = re.sub(r'href="(?!\.\./|https?:)%s' % re.escape(page), 'href="%s%s' % (prefixe, page), bloc)
        for ancre in ANCRES_ACCUEIL:
            bloc = bloc.replace('href="%s"' % ancre, 'href="%s%s"' % (prefixe, ancre))
        bloc = bloc.replace('href="#haut"', 'href="%s"' % prefixe)
    return bloc

def faq_html(faq):
    items = (NL + '      ').join('<details class="revele"><summary>%s</summary><p>%s</p></details>' % (q, a) for q, a in faq)
    return ('  <section class="faq">' + NL + '    <h2 class="faq-titre revele">Questions fréquentes</h2>' + NL
            + '    <div class="faq-liste">' + NL + '      ' + items + NL + '    </div>' + NL + '  </section>')

def jsonld(o):
    return '<script type="application/ld+json">%s</script>' % json.dumps(o, ensure_ascii=False)

def ecrire(chemin, texte):
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    io.open(chemin, 'w', encoding='utf-8', newline='').write(texte)

# ------------------------------------------------------------------ accueil
src = io.open(os.path.join(ICI, 'index.html'), encoding='utf-8').read()
tete = src[src.index('<header class="tete"'):src.index('</main>')]  # en-tete + contenu : les cartes et boutons pointent aussi vers les pages
accueil = src.replace(tete, reecrire_liens(tete, ''))
if 'rel="canonical"' not in accueil:
    accueil = accueil.replace('<meta name="description"', '<link rel="canonical" href="%s">' % SITE + NL + '<meta name="description"', 1)
ecrire(os.path.join(ICI, 'index.html'), accueil)
src = accueil

head = src[:src.index('</head>')]
head = re.sub(r'<script type="application/ld\+json">.*?</script>\n?', '', head, flags=re.S)
head = re.sub(r'<link rel="canonical" href="[^"]*">\n?', '', head)
corps_debut = src[src.index('<body>'):src.index('<main id="haut">')]
corps_fin = src[src.index('</main>'):]

def entete_page(titre, description, canonical, prefixe_css):
    h = head
    h = re.sub(r'<title>.*?</title>', '<title>%s</title>' % titre, h)
    h = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="%s">' % description, h)
    h = re.sub(r'<meta property="og:title" content="[^"]*">', '<meta property="og:title" content="%s">' % titre, h)
    h = re.sub(r'<meta property="og:description" content="[^"]*">', '<meta property="og:description" content="%s">' % description, h)
    if canonical:
        h = h.replace('<meta name="description"', '<link rel="canonical" href="%s">' % canonical + NL + '<meta name="description"', 1)
    return re.sub(r'href="style\.css', 'href="%sstyle.css' % prefixe_css, h)

# ------------------------------------------------------------------ sous-pages
for p in PAGES:
    r = '../'
    h = entete_page(p['titre'], p['description'], SITE + p['chemin'], r)
    ld = [
        {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Accueil', 'item': SITE},
            {'@type': 'ListItem', 'position': 2, 'name': p['fil'], 'item': SITE + p['chemin']}]},
        {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
            {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in p['faq']]},
    ]
    h += NL.join(jsonld(o) for o in ld) + NL

    debut = reecrire_liens(corps_debut, r)
    actuelle = 'href="%s%s"' % (r, p['chemin'])
    debut = debut.replace(actuelle, actuelle + ' aria-current="page"', 1)

    blocs = []
    for tag, ident, enveloppe in p['blocs']:
        b = element(src, tag, ident)
        b = ('  <section class="%s">' % enveloppe + NL + '    ' + b + NL + '  </section>') if enveloppe else '  ' + b
        blocs.append(reecrire_liens(b, r))

    entete = ('  <nav class="ariane" aria-label="Fil d’Ariane"><a href="%s">Accueil</a><span aria-current="page">%s</span></nav>' % (r, p['fil']) + NL
              + '  <header class="page-entete">' + NL
              + '    <p class="%s">%s</p>' % (ETIQUETTE, p['sur']) + NL
              + '    <h1>%s</h1>' % p['h1'] + NL
              + '    <p>%s</p>' % p['intro'] + NL
              + '    ' + CTA + NL + '  </header>')
    fin = corps_fin.replace('src="app.js', 'src="%sapp.js' % r)
    html = (h + '</head>' + NL + debut + '<main id="haut">' + NL + entete + NL + NL
            + (NL + NL).join(blocs) + NL + NL + faq_html(p['faq']) + NL + fin)
    ecrire(os.path.join(ICI, p['chemin'], 'index.html'), html)

# ------------------------------------------------------------------ sitemap, robots, 404
urls = [SITE] + [SITE + p['chemin'] for p in PAGES]
ecrire(os.path.join(ICI, 'sitemap.xml'),
       '<?xml version="1.0" encoding="UTF-8"?>' + NL + '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + NL
       + NL.join('  <url><loc>%s</loc></url>' % u for u in urls) + NL + '</urlset>' + NL)

robots = ('# Apercu : site cache aux moteurs. A la mise en ligne, mettre APERCU = False dans pages-seo.py.' + NL
          + 'User-agent: *' + NL + 'Disallow: /' + NL) if APERCU else ('User-agent: *' + NL + 'Allow: /' + NL)
ecrire(os.path.join(ICI, 'robots.txt'), robots + NL + 'Sitemap: %ssitemap.xml' % SITE + NL)

h404 = entete_page('Page introuvable | ' + re.search(r'<title>(.*?)</title>', head).group(1).split(' : ')[0],
                   'Cette page n’existe pas ou a changé d’adresse.', None, DOSSIER)
if '<meta name="robots"' not in h404:
    h404 = h404.replace('<title>', '<meta name="robots" content="noindex">' + NL + '<title>', 1)
debut404 = reecrire_liens(corps_debut, DOSSIER)
html404 = (h404 + '</head>' + NL + debut404 + '<main id="haut">' + NL
           + '  <header class="page-entete page-404">' + NL
           + '    <p class="%s">Erreur 404</p>' % ETIQUETTE + NL
           + '    <h1>Cette page n’existe pas</h1>' + NL
           + '    <p>Le lien est peut-être ancien, ou la page a changé d’adresse.</p>' + NL
           + '    <a class="%s" href="%s">Revenir à l’accueil</a>' % (BOUTON_404, DOSSIER) + NL
           + '  </header>' + NL + corps_fin.replace('src="app.js', 'src="%sapp.js' % DOSSIER))
ecrire(os.path.join(ICI, '404.html'), html404)
print('%d pages + accueil, sitemap.xml, robots.txt, 404.html' % len(PAGES))
