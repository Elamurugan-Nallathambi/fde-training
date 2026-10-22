// FDE Training Program overview: track filter (dims other-track rows) and capstone use case filter by industry.
(function () {
  var trackBtns = Array.prototype.slice.call(document.querySelectorAll('[data-show]'));
  trackBtns.forEach(function (btn) {
    btn.addEventListener('click', function () {
      var t = btn.dataset.show;
      trackBtns.forEach(function (b) { b.setAttribute('aria-pressed', b === btn ? 'true' : 'false'); });
      document.querySelectorAll('[data-track]').forEach(function (el) {
        var tr = el.dataset.track;
        el.classList.toggle('dim', t !== 'all' && tr !== 'both' && tr !== t);
      });
    });
  });

  var secBtns = Array.prototype.slice.call(document.querySelectorAll('[data-sector]')).filter(function (el) { return el.tagName === 'BUTTON'; });
  secBtns.forEach(function (btn) {
    btn.addEventListener('click', function () {
      var s = btn.dataset.sector;
      secBtns.forEach(function (b) { b.setAttribute('aria-pressed', b === btn ? 'true' : 'false'); });
      document.querySelectorAll('article.case').forEach(function (c) {
        c.dataset.hide = (s !== 'all' && c.dataset.sector !== s) ? '1' : '';
      });
    });
  });
})();
