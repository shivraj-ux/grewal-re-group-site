/* Grewal RE Group — motion system (reveals, counters, rails, Core Story slider, parallax). Vanilla JS, no deps. */
(function () {
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---- Reveal on view ---- */
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) { e.target.classList.add('inview'); io.unobserve(e.target); }
    });
  }, { threshold: 0.16 });
  document.querySelectorAll('.reveal, .reveal-line, .wipe').forEach(function (el) { io.observe(el); });
  /* Safety net: if IntersectionObserver never fires for an element (slow script
     load, tab backgrounded on load, browser quirk), force it visible after 2.5s
     so content is never permanently hidden. */
  setTimeout(function () {
    document.querySelectorAll('.reveal:not(.inview), .reveal-line:not(.inview), .wipe:not(.inview)').forEach(function (el) {
      el.classList.add('inview');
    });
  }, 2500);

  /* ---- Counters ---- */
  var cio = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (!e.isIntersecting) return;
      cio.unobserve(e.target);
      var el = e.target, target = parseFloat(el.dataset.count);
      var prefix = el.dataset.prefix || '', suffix = el.dataset.suffix || '';
      var decimals = el.dataset.count.indexOf('.') > -1 ? el.dataset.count.split('.')[1].length : 0;
      if (reduced) { el.textContent = prefix + target.toFixed(decimals) + suffix; return; }
      var t0 = null;
      function tick(t) {
        if (!t0) t0 = t;
        var p = Math.min((t - t0) / 1500, 1);
        var eased = 1 - Math.pow(1 - p, 3);
        el.textContent = prefix + (target * eased).toFixed(decimals) + suffix;
        if (p < 1) requestAnimationFrame(tick);
      }
      requestAnimationFrame(tick);
    });
  }, { threshold: 0.6 });
  document.querySelectorAll('[data-count]').forEach(function (el) { cio.observe(el); });

  /* ---- Horizontal rails ---- */
  var rails = [];
  document.querySelectorAll('[data-rail]').forEach(function (section) {
    rails.push({ section: section, track: section.querySelector('[data-track]'), bar: section.querySelector('[data-progress]') });
  });
  function sizeRails() {
    rails.forEach(function (r) {
      r.overflow = Math.max(r.track.scrollWidth - innerWidth, 0);
      r.section.style.height = (innerHeight + r.overflow) + 'px';
    });
  }
  function moveRails() {
    rails.forEach(function (r) {
      var rect = r.section.getBoundingClientRect();
      var p = r.overflow ? Math.min(Math.max(-rect.top / r.overflow, 0), 1) : 0;
      r.track.style.transform = 'translateX(' + (-p * r.overflow) + 'px)';
      if (r.bar) r.bar.style.width = (p * 100) + '%';
    });
  }

  /* ---- Core Story slider: vertical scroll drives chapter index ---- */
  var stories = [];
  document.querySelectorAll('[data-story]').forEach(function (section) {
    var chapters = [].slice.call(section.querySelectorAll('.story-chapter'));
    var dots = [].slice.call(section.querySelectorAll('.story-progress i'));
    section.style.height = (chapters.length * 100) + 'vh';
    stories.push({ section: section, chapters: chapters, dots: dots });
  });
  function moveStories() {
    stories.forEach(function (s) {
      var rect = s.section.getBoundingClientRect();
      var total = rect.height - innerHeight;
      var p = total > 0 ? Math.min(Math.max(-rect.top / total, 0), 0.9999) : 0;
      var idx = Math.floor(p * s.chapters.length);
      idx = Math.max(0, Math.min(idx, s.chapters.length - 1));
      var within = (p * s.chapters.length) - idx;
      s.chapters.forEach(function (c, i) { c.classList.toggle('active', i === idx); });
      s.dots.forEach(function (d, i) {
        d.classList.toggle('done', i < idx);
        var b = d.querySelector('b');
        if (i === idx) b.style.width = (within * 100) + '%';
        else if (i > idx) b.style.width = '0%';
      });
    });
  }

  /* ---- Scroll parallax ---- */
  var pars = [].slice.call(document.querySelectorAll('[data-par]'));
  function movePars() {
    pars.forEach(function (el) {
      var rect = el.getBoundingClientRect();
      if (rect.bottom < -200 || rect.top > innerHeight + 200) return;
      var p = (rect.top + rect.height / 2 - innerHeight / 2) / innerHeight;
      el.style.setProperty('--py', (p * -60).toFixed(1));
    });
  }

  function onScroll() {
    moveRails();
    moveStories();
    if (!reduced) movePars();
  }
  sizeRails();
  addEventListener('resize', function () { sizeRails(); onScroll(); });
  addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ---- Magnetic buttons (fine pointers only) ---- */
  if (!reduced && matchMedia('(pointer: fine)').matches) {
    document.querySelectorAll('[data-magnet]').forEach(function (btn) {
      btn.addEventListener('mousemove', function (e) {
        var r = btn.getBoundingClientRect();
        btn.style.transform = 'translate(' + ((e.clientX - r.left - r.width / 2) * 0.16) + 'px,' + ((e.clientY - r.top - r.height / 2) * 0.26) + 'px)';
      });
      btn.addEventListener('mouseleave', function () { btn.style.transform = ''; });
    });
  }
})();
