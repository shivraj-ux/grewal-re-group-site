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
    var dropdowns = Array.prototype.slice.call(header.querySelectorAll('.gh-has-sub'));

    /* ---- Mobile hamburger ---- */
    if (toggle && nav) {
      toggle.addEventListener('click', function () {
        var open = nav.classList.toggle('gh-open');
        toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
        toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
        document.body.style.overflow = open ? 'hidden' : '';
      });
    }

    /* ---- Accessible dropdown submenus (split pattern: parent link + chevron button) ---- */
    dropdowns.forEach(function (dropdown) {
      var btn = dropdown.querySelector('.gh-sub-toggle');
      var submenu = dropdown.querySelector('.gh-sub');
      if (!btn || !submenu) return;

      /* Open/close submenu on button click */
      btn.addEventListener('click', function (e) {
        e.preventDefault();
        var isOpen = btn.getAttribute('aria-expanded') === 'true';
        closeAllDropdowns(dropdown);
        btn.setAttribute('aria-expanded', isOpen ? 'false' : 'true');
      });

      /* Desktop: open on hover and focus-within */
      dropdown.addEventListener('mouseenter', function () {
        if (window.innerWidth > 900) {
          btn.setAttribute('aria-expanded', 'true');
        }
      });
      dropdown.addEventListener('mouseleave', function () {
        if (window.innerWidth > 900) {
          btn.setAttribute('aria-expanded', 'false');
        }
      });

      /* Keyboard navigation within submenu */
      var links = Array.prototype.slice.call(submenu.querySelectorAll('a'));
      links.forEach(function (link) {
        link.addEventListener('keydown', function (e) {
          if (e.key === 'ArrowDown') {
            e.preventDefault();
            var idx = links.indexOf(link);
            if (idx < links.length - 1) links[idx + 1].focus();
          } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            var idx = links.indexOf(link);
            if (idx > 0) links[idx - 1].focus();
          }
        });
      });
    });

    /* ---- Close all dropdowns except the one passed in ---- */
    function closeAllDropdowns(except) {
      dropdowns.forEach(function (d) {
        if (d !== except) {
          var btn = d.querySelector('.gh-sub-toggle');
          if (btn) btn.setAttribute('aria-expanded', 'false');
        }
      });
    }

    /* ---- Escape closes everything; returns focus sensibly ---- */
    document.addEventListener('keydown', function (e) {
      if (e.key !== 'Escape') return;
      var openBtn = Array.prototype.slice.call(header.querySelectorAll('.gh-sub-toggle'))
        .filter(function (t) { return t.getAttribute('aria-expanded') === 'true'; })[0];
      if (openBtn) {
        openBtn.setAttribute('aria-expanded', 'false');
        openBtn.focus();
        return;
      }
      if (nav && nav.classList.contains('gh-open')) {
        nav.classList.remove('gh-open');
        if (toggle) {
          toggle.setAttribute('aria-expanded', 'false');
          toggle.setAttribute('aria-label', 'Open menu');
          toggle.focus();
        }
        document.body.style.overflow = '';
      }
    });

    /* ---- Click outside closes open dropdowns ---- */
    document.addEventListener('click', function (e) {
      if (!header.contains(e.target)) closeAllDropdowns(null);
    });

    /* ---- Transparent over hero -> solid white on scroll (toggles .gh-scrolled) ---- */
    var scrolled = false;
    function onScroll() {
      var on = window.scrollY > 30;
      if (on !== scrolled) { scrolled = on; header.classList.toggle('gh-scrolled', on); }
    }
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll(); /* set correct state if the page loads already scrolled */

    /* ---- Nav CTA: "Contact" on desktop, "Call" on mobile (<=900px matches the hamburger breakpoint) ---- */
    var cta = header.querySelector('.gh-cta');
    if (cta) {
      var ctaHref = cta.getAttribute('href');
      var ctaText = cta.textContent;
      var mq = window.matchMedia('(max-width: 900px)');
      function syncCta(e) {
        if (e.matches) { cta.textContent = 'Call'; cta.setAttribute('href', 'tel:+15126170001'); }
        else { cta.textContent = ctaText; cta.setAttribute('href', ctaHref); }
      }
      syncCta(mq);
      mq.addEventListener ? mq.addEventListener('change', syncCta) : mq.addListener(syncCta);
    }
  });
})();
