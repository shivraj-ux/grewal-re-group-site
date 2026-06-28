/* Grewal RE Group — Microsoft Clarity loader (PREVIEW — not yet wired into pages).
   Privacy-safe: Clarity records session replays + heatmaps, so it loads ONLY after
   the visitor grants analytics consent via the existing banner (consent.js sets
   localStorage 'grg_cookie_consent' = 'granted'). No consent => Clarity never loads.

   TO ACTIVATE:
   1. Replace CLARITY_PROJECT_ID below with your real Clarity project ID
      (clarity.microsoft.com → Settings → Overview → "Clarity project id").
   2. Either add  <script defer src="/assets/js/clarity.js"></script>  to the page head,
      OR (zero per-page edits) paste this file's body at the end of consent.js,
      which already loads on every page.
   3. Add  https://www.clarity.ms  to the script-src + connect-src of the CSP in _headers. */
(function () {
  var CLARITY_PROJECT_ID = 'XXXXXXXXXX'; // <-- replace with real ID to activate

  function consentGranted() {
    try { return localStorage.getItem('grg_cookie_consent') === 'granted'; }
    catch (e) { return false; }
  }

  function loadClarity(id) {
    if (window.clarity || document.getElementById('grg-clarity')) return;
    (function (c, l, a, r, i, t, y) {
      c[a] = c[a] || function () { (c[a].q = c[a].q || []).push(arguments); };
      t = l.createElement(r); t.async = 1; t.id = 'grg-clarity';
      t.src = 'https://www.clarity.ms/tag/' + i;
      y = l.getElementsByTagName(r)[0]; y.parentNode.insertBefore(t, y);
    })(window, document, 'clarity', 'script', id);
  }

  function maybeLoad() {
    if (CLARITY_PROJECT_ID === 'XXXXXXXXXX') return;   // inert until a real ID is set
    if (consentGranted()) loadClarity(CLARITY_PROJECT_ID);
  }

  // Load now if consent already given…
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', maybeLoad);
  else maybeLoad();

  // …and the moment the visitor clicks "Accept" on the consent banner.
  document.addEventListener('click', function (e) {
    var el = e.target.closest && e.target.closest('#grg-accept');
    if (el) setTimeout(maybeLoad, 50);
  }, true);
})();
