/* Grewal RE Group — lightweight cookie consent + Google Consent Mode v2.
   Self-hosted, no third party. Pairs with the inline gtag('consent','default',{denied})
   that runs before GA loads on each page. On Accept -> grants analytics/ads storage;
   on Decline -> stays denied (GA still sends anonymized, cookieless modeled pings). */
(function () {
  var KEY = 'grg_cookie_consent';

  function gtag() { window.dataLayer = window.dataLayer || []; window.dataLayer.push(arguments); }

  function apply(granted) {
    gtag('consent', 'update', {
      'ad_storage': granted ? 'granted' : 'denied',
      'analytics_storage': granted ? 'granted' : 'denied',
      'ad_user_data': granted ? 'granted' : 'denied',
      'ad_personalization': granted ? 'granted' : 'denied'
    });
  }

  function store(val) { try { localStorage.setItem(KEY, val); } catch (e) {} }
  function read() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }

  // Let the privacy page (or any element) re-open the choice.
  function wirePrefs() {
    var els = document.querySelectorAll('[data-cookie-prefs]');
    for (var i = 0; i < els.length; i++) {
      els[i].addEventListener('click', function (e) {
        e.preventDefault();
        try { localStorage.removeItem(KEY); } catch (err) {}
        location.reload();
      });
    }
  }

  function buildBanner() {
    var css = document.createElement('style');
    css.textContent =
      '#grg-consent{position:fixed;left:0;right:0;bottom:0;z-index:99999;background:#0a0a0a;color:#fff;' +
      'box-shadow:0 -6px 24px rgba(0,0,0,.25);font-family:Inter,system-ui,sans-serif;animation:grgcup .35s ease}' +
      '@keyframes grgcup{from{transform:translateY(100%)}to{transform:none}}' +
      '#grg-consent .grg-in{max-width:1100px;margin:0 auto;padding:1rem 1.25rem;display:flex;gap:1rem;' +
      'align-items:center;justify-content:space-between;flex-wrap:wrap}' +
      '#grg-consent p{margin:0;font-size:.85rem;line-height:1.55;color:rgba(255,255,255,.82);flex:1;min-width:240px}' +
      '#grg-consent a{color:#cdae5f;text-decoration:underline}' +
      '#grg-consent .grg-btns{display:flex;gap:.6rem;flex-shrink:0}' +
      '#grg-consent button{font:inherit;font-size:.82rem;font-weight:600;letter-spacing:.04em;padding:.6rem 1.3rem;' +
      'border-radius:4px;cursor:pointer;border:1.5px solid #B8963E;transition:all .18s}' +
      '#grg-consent .grg-accept{background:#B8963E;color:#fff}#grg-consent .grg-accept:hover{background:#9a7c33;border-color:#9a7c33}' +
      '#grg-consent .grg-decline{background:transparent;color:#cdae5f}#grg-consent .grg-decline:hover{background:rgba(184,150,62,.15)}' +
      '@media(max-width:560px){#grg-consent .grg-in{flex-direction:column;align-items:stretch;gap:.75rem}#grg-consent .grg-btns{justify-content:flex-end}}';
    document.head.appendChild(css);

    var bar = document.createElement('div');
    bar.id = 'grg-consent';
    bar.setAttribute('role', 'dialog');
    bar.setAttribute('aria-label', 'Cookie consent');
    bar.innerHTML =
      '<div class="grg-in">' +
      '<p>We use cookies to measure site traffic and improve your experience. Accept analytics cookies, or decline and we\'ll keep things anonymous. See our <a href="/privacy">Privacy Policy</a>.</p>' +
      '<div class="grg-btns">' +
      '<button type="button" class="grg-decline" id="grg-decline">Decline</button>' +
      '<button type="button" class="grg-accept" id="grg-accept">Accept</button>' +
      '</div></div>';
    document.body.appendChild(bar);

    function choose(granted) {
      store(granted ? 'granted' : 'denied');
      apply(granted);
      if (bar.parentNode) bar.parentNode.removeChild(bar);
    }
    document.getElementById('grg-accept').addEventListener('click', function () { choose(true); });
    document.getElementById('grg-decline').addEventListener('click', function () { choose(false); });
  }

  function init() {
    wirePrefs();
    var choice = read();
    if (choice === 'granted') { apply(true); return; }
    if (choice === 'denied') { apply(false); return; }
    buildBanner();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
