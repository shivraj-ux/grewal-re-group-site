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

  // ── Sticky "Schedule a Call" CTA (appears after scroll) ─────────────────
  function mountCTA() {
    if (document.getElementById('grg-sticky-cta')) return;
    var a = document.createElement('a');
    a.id = 'grg-sticky-cta';
    a.href = '/#contact';
    a.textContent = 'Schedule a Call';
    a.setAttribute('aria-label', 'Schedule a call with Shivraj Grewal');
    a.style.cssText = [
      'position:fixed', 'right:18px', 'bottom:18px', 'z-index:9998',
      'background:#b8963e', 'color:#fff', 'font:600 14px/1 Inter,system-ui,sans-serif',
      'padding:14px 20px', 'border-radius:40px', 'text-decoration:none',
      'box-shadow:0 6px 20px rgba(0,0,0,.25)', 'letter-spacing:.02em',
      'opacity:0', 'transform:translateY(12px)', 'transition:opacity .3s,transform .3s'
    ].join(';');
    document.body.appendChild(a);
    var show = function () {
      var on = (window.scrollY || 0) > 600;
      a.style.opacity = on ? '1' : '0';
      a.style.transform = on ? 'translateY(0)' : 'translateY(12px)';
      a.style.pointerEvents = on ? 'auto' : 'none';
    };
    window.addEventListener('scroll', show, { passive: true }); show();
  }
  if (document.readyState !== 'loading') mountCTA();
  else document.addEventListener('DOMContentLoaded', mountCTA);
})();
