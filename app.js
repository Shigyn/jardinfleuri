/* Jardin Fleuri — apercu LocWeb : menu, revelations, boutique par categories (paiement sur la boutique SumUp existante). */
(function () {
  document.documentElement.classList.add('js');
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var BOUTIQUE = 'https://jardin-fleuri.sumupstore.com/product/';
  var img = function (id, w) { return 'https://images.weserv.nl/?url=images.sumup.com/' + id + '&w=' + (w || 520) + '&h=' + (w || 520) + '&fit=cover&output=webp&q=76'; };

  // Catalogue repris de la boutique SumUp (prix au 26/11/2026).
  var P = {
    sechees: [
      ['Cloche fleurie rose', '35,00', 'img_41BXHNSGYX8MTS3M70HYWMMN28', 'cloche-avec-fleurs-sechees-rose'],
      ['Cadre fleuri', '35,00', 'img_4N6G8Q62889WSB9KRPHVYR36GS', 'cadre-fleuris-fleurs-sechees'],
      ['Couronne noire, rouge et rose', '30,00', 'img_1155BCQFN28MARCC1FX9A8AZSH', 'couronne-noire-rouge-et-rose'],
      ['Couronne perle rose', '30,00', 'img_3P0Q5VN8H29PRBZX27WS8579KK', 'couronne-perle-rose'],
      ['Peigne à cheveux fleuri', '15,50', 'img_6J10N0TYJ88MKTBZCQGRCPC1NN', 'peigne-cheveux-fleuri'],
      ['Peigne rose et blanc', '15,50', 'img_3SWWJ73CY98P8TC06NQSDEFE52', 'peigne-rose-et-blanc'],
      ['Peigne rose et violet', '15,50', 'img_5ACNVB28M19KN80H5B1V575W0M', 'peigne-rose-et-violet'],
      ['Collier fleurs séchées rose', '10,00', 'img_1A5CDJZKT39N6TCA2G7SZPW24X', 'collier-fleurs-sechee-rose'],
      ['Collier fleurs séchées lavande', '10,00', 'img_6W1C12MQWK9FP9V9GQMNQETKDM', 'collier-fleurs-sechee-lavande'],
      ['Marque-page fleuri', '9,00', 'img_3K1G24P5BA9DH9BY7ZTX5XHZMH', 'marque-page-fleuri'],
      ['Marque-page hiboux', '9,00', 'img_51Q54R62YX8NM8AXGY43AA115T', 'marque-page-hiboux'],
      ['Marque-page plume', '9,00', 'img_1GNZ4Z9DQN8T4SKVSHVN8H6ET7', 'marque-page-photo-plume']
    ],
    plantes: [
      ['Cactus avec pot', '22,90', 'img_3ZY38GDQPH8R7VTNA5BGHVQES1', 'cactus-avec-pot'],
      ['Figuier de Barbarie', '9,90', 'img_4F0BACAEZF9JR9KBXA82R5Y1B9', 'figuier-de-barbarie'],
      ['Cactus Cereus peruvianus', '6,00', 'img_3E9ZHG801T8EPS8EQMMBZ5AH1E', 'cactus-cereus-paruvianus'],
      ['Réserve d’eau en globe', '10,00', 'img_1YPYMWDR9Q9NH8M3GSS4EBYME8', 'reserve-deau-en-forme-de-globe'],
      ['Sérum cactus et plantes vertes', '17,00', 'img_00F3JGKBCP82VSEGV21X5JK0H0', 'serum-cactus-et-plantes-verte-50ml'],
      ['Graines de belle-de-nuit', '1,50', 'img_7TYMVC39TJ9BEVBAAVJZ8NPP6Y', 'graine-belle-de-nuit']
    ],
    senteurs: [
      ['Coffret lavande', '26,00', 'img_40PY1DXZB885Y8R9SPY08X7DCY', 'coffret-lavande'],
      ['Lavande fine', '12,00', 'img_0H279QW6HT9FSBF18XYTT2MZB0', 'lavande-fine'],
      ['Huile essentielle pure', '12,00', 'img_509BMVTMHB9TWA4S2TVY7KX2G5', 'huile-essentielle-pure'],
      ['Diffuseur voiture avec recharge', '11,00', 'img_548F089MN4923BVVVD5ZZ1XFB6', 'diffuseur-voiture-avec-recharge-senteur-pivoine'],
      ['Poudre pour aspirateur', '5,00', 'img_4PEVX27FDP9DJBQBE6WRRNF139', 'poudre-aspirateur-senteur-pivoine']
    ]
  };
  var liste = $('[data-produits]');
  function afficher(cat) {
    liste.innerHTML = P[cat].map(function (p) {
      return '<li class="produit"><a href="' + BOUTIQUE + p[3] + '" target="_blank" rel="noopener">' +
        '<span class="produit-photo"><img src="' + img(p[2]) + '" alt="' + p[0] + '" loading="lazy" width="520" height="520"></span>' +
        '<span class="produit-etiquette"><i>' + p[0] + '</i><b>' + p[1] + ' €</b></span>' +
        '<span class="produit-cta">Commander</span></a></li>';
    }).join('');
  }
  $$('[data-cat]').forEach(function (b) {
    b.addEventListener('click', function () {
      $$('[data-cat]').forEach(function (x) { x.setAttribute('aria-selected', x === b); });
      afficher(b.getAttribute('data-cat'));
    });
  });
  afficher('sechees');

  // En-tete et menu mobile.
  var tete = $('[data-tete]'), burger = $('[data-burger]'), menu = $('[data-menu]');
  function hauteur() { document.documentElement.style.setProperty('--haut-tete', tete.getBoundingClientRect().bottom + 'px'); }
  addEventListener('scroll', function () { tete.classList.toggle('colle', scrollY > 10); hauteur(); }, { passive: true });
  addEventListener('resize', hauteur); hauteur();
  burger.addEventListener('click', function () { hauteur(); var o = menu.classList.toggle('ouvert'); burger.setAttribute('aria-expanded', o); });
  $$('a', menu).forEach(function (a) { a.addEventListener('click', function () { menu.classList.remove('ouvert'); burger.setAttribute('aria-expanded', 'false'); }); });

  // Revelations au defilement.
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('vu'); io.unobserve(e.target); } });
    }, { rootMargin: '0px 0px -8% 0px' });
    $$('.revele').forEach(function (el, i) { el.style.transitionDelay = (i % 3) * 80 + 'ms'; io.observe(el); });
  } else $$('.revele').forEach(function (el) { el.classList.add('vu'); });
})();
