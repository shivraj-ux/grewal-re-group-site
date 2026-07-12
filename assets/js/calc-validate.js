/* Shared numeric-input validation for /calculators/* pages.
   Reads the min/max already declared on each <input type="number">
   as the single source of truth for allowed range. */
(function () {
  window.grgVal = function (id, fallback) {
    var el = document.getElementById(id);
    if (!el) return fallback;
    var raw = parseFloat(el.value);
    var min = el.min !== '' ? parseFloat(el.min) : null;
    var max = el.max !== '' ? parseFloat(el.max) : null;
    if (isNaN(raw)) raw = fallback;
    if (min !== null && raw < min) raw = min;
    if (max !== null && raw > max) raw = max;
    return raw;
  };

  function attachFieldWarnings(root) {
    var inputs = (root || document).querySelectorAll('input[type="number"]');
    inputs.forEach(function (el) {
      if (el.dataset.grgValidated) return;
      el.dataset.grgValidated = '1';

      var warn = document.createElement('div');
      warn.className = 'calc-field-warn';
      warn.setAttribute('aria-live', 'polite');
      var wrap = el.closest('.field, .input-group, .hv-field') || el.parentElement;
      wrap.appendChild(warn);

      function rangeText() {
        var min = el.min !== '' ? el.min : null;
        var max = el.max !== '' ? el.max : null;
        if (min !== null && max !== null) return 'Value must be between ' + min + ' and ' + max + '.';
        if (min !== null) return 'Value cannot be below ' + min + '.';
        if (max !== null) return 'Value cannot exceed ' + max + '.';
        return '';
      }

      function isOutOfRange() {
        if (el.value === '') return false;
        var raw = parseFloat(el.value);
        if (isNaN(raw)) return true;
        var min = el.min !== '' ? parseFloat(el.min) : null;
        var max = el.max !== '' ? parseFloat(el.max) : null;
        return (min !== null && raw < min) || (max !== null && raw > max);
      }

      function showWarning() {
        if (isOutOfRange()) {
          el.classList.add('calc-invalid');
          warn.textContent = rangeText();
        } else {
          el.classList.remove('calc-invalid');
          warn.textContent = '';
        }
      }

      function clampOnBlur() {
        if (el.value === '') return;
        var raw = parseFloat(el.value);
        if (isNaN(raw)) { showWarning(); return; }
        var min = el.min !== '' ? parseFloat(el.min) : null;
        var max = el.max !== '' ? parseFloat(el.max) : null;
        var clamped = raw;
        if (min !== null && clamped < min) clamped = min;
        if (max !== null && clamped > max) clamped = max;
        if (clamped !== raw) {
          el.value = clamped;
          el.dispatchEvent(new Event('input', { bubbles: true }));
        }
        showWarning();
      }

      el.addEventListener('input', showWarning);
      el.addEventListener('blur', clampOnBlur);
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    attachFieldWarnings(document);
  });
})();
