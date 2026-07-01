/* Grewal RE Group — GA4 conversion + engagement tracking (G-X3GFZCS0JE)
   Delegated listeners so every page variant is covered with no per-page wiring. */
(function () {
  window.dataLayer = window.dataLayer || [];
  function ev(){ if (typeof window.gtag === 'function') window.gtag.apply(null, arguments);
                else window.dataLayer.push(arguments); }
  var here = function(){ return window.location.href; };

  // ── Clicks: phone, email, and high-intent CTAs ──────────────────────────
  var CTA = /schedule|book a|consultation|strategy call|request (current|more|info|listings)|pre-?approv|home search|talk to shivraj|start your|get started/i;
  document.addEventListener('click', function (e) {
    var el = e.target.closest && e.target.closest('a, button');
    if (!el) return;
    var href = (el.getAttribute && el.getAttribute('href')) || '';
    if (href.indexOf('tel:') === 0) {
      ev('event', 'phone_call_click', { phone_number: href.slice(4), page_location: here() }); return;
    }
    if (href.indexOf('mailto:') === 0) {
      ev('event', 'email_click', { email_address: href.slice(7).split('?')[0], page_location: here() }); return;
    }
    var txt = (el.textContent || '').replace(/\s+/g, ' ').trim();
    if (txt && CTA.test(txt)) {
      ev('event', 'qualify_lead', { button_text: txt.slice(0, 80), page_location: here() });
    }
  }, true);

  // ── Form submissions ────────────────────────────────────────────────────
  document.addEventListener('submit', function (e) {
    var f = e.target;
    if (!f || f.tagName !== 'FORM') return;
    var name = (f.getAttribute('name') || f.id || '').toLowerCase();
    var newsletter = /news|insight|signup|subscribe/.test(name);
    ev('event', newsletter ? 'qualify_lead' : 'close_convert_lead', {
      form_location: window.location.pathname, form_name: name || 'contact', contact_method: 'form'
    });
  }, true);

  // ── Scroll depth on blog + community pages ──────────────────────────────
  var path = window.location.pathname;
  if (/\/blog\/|\/communities\//.test(path)) {
    var marks = [25, 50, 75, 90], hit = {};
    var onScroll = function () {
      var st = window.scrollY || document.documentElement.scrollTop;
      var max = document.documentElement.scrollHeight - window.innerHeight;
      if (max <= 0) return;
      var pct = (st / max) * 100;
      for (var i = 0; i < marks.length; i++) {
        var m = marks[i];
        if (pct >= m && !hit[m]) { hit[m] = true; ev('event', 'scroll_depth', { percent_scrolled: m, page_path: path }); }
      }
      if (hit[90]) window.removeEventListener('scroll', onScroll);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  // ── Sticky CTA (appears after scroll): direct call on mobile ─────────────
  var PHONE = 'tel:+15126170001';
  var isMobile = function () { return window.matchMedia('(max-width: 900px)').matches; };

  function mountCTA() {
    if (document.getElementById('grg-sticky-cta')) return;
    var a = document.createElement('a');
    a.id = 'grg-sticky-cta';
    var cta;
    if (isMobile()) {
      // On phones, skip topic routing entirely — one tap should dial.
      cta = { href: PHONE, text: 'Call', aria: 'Call Shivraj Grewal' };
    } else {
      // Topic-aware CTA: route intent to the most relevant tool/page (routes that exist on the site).
      var hay = (window.location.pathname + ' ' + (document.title || '') + ' ' +
                 ((document.querySelector('h1') || {}).textContent || '')).toLowerCase();
      cta = { href: '/contact.html', text: 'Schedule a Call', aria: 'Schedule a call with Shivraj Grewal' };
      if (/sell|seller|listing|list your|home worth|home value|price your|net proceeds/.test(hay)) {
        cta = { href: '/home-value-estimator.html', text: 'See What Your Home Is Worth', aria: 'Get a free home value estimate' };
      } else if (/reloca|moving to austin|move to austin|relocating/.test(hay)) {
        cta = { href: '/relocation-guide.html', text: 'Get the Relocation Guide', aria: 'Download the Austin relocation guide' };
      } else if (/flood|insurance|risk/.test(hay)) {
        cta = { href: '/contact.html', text: 'Request a Flood Risk Review', aria: 'Request a flood-risk review for an Austin address' };
      }
    }
    a.href = cta.href;
    a.textContent = cta.text;
    a.setAttribute('aria-label', cta.aria);
    a.setAttribute('data-cta-topic', cta.text);
    a.style.cssText = [
      'position:fixed', 'right:18px', 'bottom:18px', 'z-index:9998',
      'background:#b8963e', 'color:#fff', 'font:600 14px/1 Inter,system-ui,sans-serif',
      'padding:14px 20px', 'border-radius:40px', 'text-decoration:none',
      'box-shadow:0 6px 20px rgba(0,0,0,.25)', 'letter-spacing:.02em',
      'opacity:0', 'transform:translateY(12px)', 'transition:opacity .3s,transform .3s'
    ].join(';');
    a.addEventListener('click', function () {
      ev('event', 'qualify_lead', { button_text: 'Sticky CTA — ' + cta.text, page_location: here() });
    });
    document.body.appendChild(a);
    var show = function () {
      var on = (window.scrollY || 0) > 600;
      a.style.opacity = on ? '1' : '0';
      a.style.transform = on ? 'translateY(0)' : 'translateY(12px)';
      a.style.pointerEvents = on ? 'auto' : 'none';
    };
    window.addEventListener('scroll', show, { passive: true }); show();
  }

  // ── Header "Contact" button: direct call on mobile ──────────────────────
  function wireHeaderCTA() {
    if (!isMobile()) return;
    var links = document.querySelectorAll('.gh-cta[href="/contact.html"]');
    for (var i = 0; i < links.length; i++) {
      var a = links[i];
      a.href = PHONE;
      a.textContent = 'Call';
      a.setAttribute('aria-label', 'Call Shivraj Grewal');
    }
  }

  function initCTAs() { mountCTA(); wireHeaderCTA(); }
  if (document.readyState !== 'loading') initCTAs();
  else document.addEventListener('DOMContentLoaded', initCTAs);
})();

/* Exit-intent market-report popup (desktop, once per session) */
(function () {
  function ev(){ if (typeof window.gtag === 'function') window.gtag.apply(null, arguments);
                 else (window.dataLayer = window.dataLayer || []).push(arguments); }
  if (window.innerWidth < 1024) return;
  var KEY = 'grg_exit_shown';
  try { if (sessionStorage.getItem(KEY)) return; } catch (e) {}

  function build() {
    var ov = document.createElement('div');
    ov.id = 'grg-exit';
    ov.setAttribute('role', 'dialog');
    ov.setAttribute('aria-modal', 'true');
    ov.style.cssText = 'position:fixed;inset:0;z-index:10000;display:flex;align-items:center;justify-content:center;background:rgba(12,14,20,.6);backdrop-filter:blur(3px);opacity:0;transition:opacity .25s;padding:20px';
    ov.innerHTML =
      '<div style="background:#fff;max-width:460px;width:100%;border-radius:8px;padding:36px 34px;box-shadow:0 20px 60px rgba(0,0,0,.35);font-family:Inter,system-ui,sans-serif;position:relative;text-align:center">' +
        '<button id="grg-exit-x" aria-label="Close" style="position:absolute;top:12px;right:14px;border:0;background:none;font-size:24px;line-height:1;color:#999;cursor:pointer">&times;</button>' +
        '<p style="font:600 12px/1 Inter;letter-spacing:.16em;text-transform:uppercase;color:#b8963e;margin:0 0 10px">Free Austin Market Report</p>' +
        '<h2 style="font-family:\'Cormorant Garamond\',serif;font-size:1.7rem;line-height:1.2;margin:0 0 10px;color:#1a1a1a">Before You Go — Get Austin\'s Latest Market Report Free</h2>' +
        '<p style="font-size:.92rem;color:#555;margin:0 0 18px">Median prices, inventory, and where values are heading across Austin\'s top neighborhoods. Sent straight to your inbox.</p>' +
        '<form id="grg-exit-form" style="display:flex;flex-direction:column;gap:10px">' +
          '<input name="name" type="text" placeholder="Your name" required style="padding:12px 14px;border:1px solid #d8d4cc;border-radius:4px;font-size:.95rem">' +
          '<input name="email" type="email" placeholder="your@email.com" required style="padding:12px 14px;border:1px solid #d8d4cc;border-radius:4px;font-size:.95rem">' +
          '<button type="submit" style="background:#b8963e;color:#fff;border:0;padding:13px;border-radius:40px;font:600 14px Inter;cursor:pointer;letter-spacing:.02em">Send My Report</button>' +
        '</form>' +
        '<p id="grg-exit-msg" style="font-size:.8rem;color:#888;margin:12px 0 0">No spam. Unsubscribe anytime.</p>' +
      '</div>';
    document.body.appendChild(ov);
    requestAnimationFrame(function(){ ov.style.opacity = '1'; });

    function close(){ ov.style.opacity = '0'; setTimeout(function(){ ov.remove(); }, 250); }
    ov.addEventListener('click', function (e) { if (e.target === ov) close(); });
    document.getElementById('grg-exit-x').addEventListener('click', close);

    document.getElementById('grg-exit-form').addEventListener('submit', function (e) {
      e.preventDefault();
      var fd = new FormData(e.target);
      var name = fd.get('name') || '', email = fd.get('email') || '';
      var body = 'form-name=insights-signup&community=' + encodeURIComponent('Exit Popup') +
                 '&name=' + encodeURIComponent(name) + '&email=' + encodeURIComponent(email);
      fetch('/', { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: body }).catch(function(){});
      ev('event', 'qualify_lead', { button_text: 'Exit Popup — Market Report', page_location: window.location.href });
      document.getElementById('grg-exit-form').style.display = 'none';
      var m = document.getElementById('grg-exit-msg');
      m.textContent = 'Thank you! Your Austin market report is on its way.';
      m.style.color = '#1a7a3a';
      setTimeout(close, 2200);
    });
  }

  function onLeave(e) {
    if (e.clientY > 0 || e.relatedTarget) return;
    try { sessionStorage.setItem(KEY, '1'); } catch (er) {}
    document.removeEventListener('mouseout', onLeave);
    build();
  }
  setTimeout(function(){ document.addEventListener('mouseout', onLeave); }, 4000);
})();
