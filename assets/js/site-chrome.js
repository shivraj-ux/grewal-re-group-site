/* Grewal RE Group — site chrome behavior (mobile menu + accessible dropdowns).
   Progressive enhancement: nav works without JS (links are real); JS adds the
   mobile toggle, keyboard dropdowns, Escape-to-close, and outside-click close. */
(function () {
  'use strict';

  function ready(fn) {
    if (document.readyState !== 'loading') fn();
    else document.addEventListener('DOMContentLoaded', fn);
  }

  ready(function () {
    var header = document.querySelector('.gh-header');
    if (!header) return;
    var nav = header.querySelector('.gh-nav');
    var toggle = header.querySelector('.gh-toggle');
    var subToggles = Array.prototype.slice.call(header.querySelectorAll('.gh-sub-toggle'));

    /* ---- Mobile hamburger ---- */
    if (toggle && nav) {
      toggle.addEventListener('click', function () {
        var open = nav.classList.toggle('gh-open');
        toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
        toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
        document.body.style.overflow = open ? 'hidden' : '';
      });
    }

    /* ---- Accessible dropdown submenus (click/keyboard) ---- */
    function closeAllSubs(except) {
      subToggles.forEach(function (t) {
        if (t !== except) t.setAttribute('aria-expanded', 'false');
      });
    }
    subToggles.forEach(function (t) {
      t.addEventListener('click', function (e) {
        e.preventDefault();
        var open = t.getAttribute('aria-expanded') === 'true';
        closeAllSubs(t);
        t.setAttribute('aria-expanded', open ? 'false' : 'true');
      });
    });

    /* ---- Escape closes everything; returns focus sensibly ---- */
    document.addEventListener('keydown', function (e) {
      if (e.key !== 'Escape') return;
      var openSub = subToggles.filter(function (t) { return t.getAttribute('aria-expanded') === 'true'; })[0];
      if (openSub) { openSub.setAttribute('aria-expanded', 'false'); openSub.focus(); return; }
      if (nav && nav.classList.contains('gh-open')) {
        nav.classList.remove('gh-open');
        if (toggle) { toggle.setAttribute('aria-expanded', 'false'); toggle.setAttribute('aria-label', 'Open menu'); toggle.focus(); }
        document.body.style.overflow = '';
      }
    });

    /* ---- Click outside closes open dropdowns ---- */
    document.addEventListener('click', function (e) {
      if (!header.contains(e.target)) closeAllSubs(null);
    });

    /* ---- Transparent over hero -> solid white on scroll (toggles .gh-scrolled) ---- */
    var scrolled = false;
    function onScroll() {
      var on = window.scrollY > 30;
      if (on !== scrolled) { scrolled = on; header.classList.toggle('gh-scrolled', on); }
    }
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll(); /* set correct state if the page loads already scrolled */
  });
})();
