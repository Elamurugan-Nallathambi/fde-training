// Training material: practice ticks kept in this browser; nav shows lessons with all practice done.
(function () {
  var KEY = 'fde-practice-v1', store = {};
  try { store = JSON.parse(localStorage.getItem(KEY) || '{}') || {}; } catch (e) { store = {}; }
  function save() { try { localStorage.setItem(KEY, JSON.stringify(store)); } catch (e) {} }
  var boxes = Array.prototype.slice.call(document.querySelectorAll('[data-done]'));
  function mark() {
    document.querySelectorAll('[data-lesson]').forEach(function (a) {
      var mine = boxes.filter(function (b) { return b.dataset.done.indexOf(a.dataset.lesson + '-') === 0; });
      a.classList.toggle('done', mine.length > 0 && mine.every(function (b) { return b.checked; }));
    });
  }
  boxes.forEach(function (b) {
    b.checked = !!store[b.dataset.done];
    b.addEventListener('change', function () { store[b.dataset.done] = b.checked; save(); mark(); });
  });
  mark();

  // Basics page: filter term cards by text.
  var q = document.getElementById('q');
  if (q) {
    var cards = Array.prototype.slice.call(document.querySelectorAll('.term'));
    q.addEventListener('input', function () {
      var v = q.value.trim().toLowerCase(), shown = 0;
      cards.forEach(function (c) { var hit = !v || c.textContent.toLowerCase().indexOf(v) >= 0; c.dataset.hide = hit ? '' : '1'; if (hit) shown++; });
      document.querySelectorAll('[data-group]').forEach(function (g) { g.dataset.hide = g.querySelector('.term:not([data-hide="1"])') ? '' : '1'; });
      document.getElementById('qcount').textContent = v ? shown + ' matching terms' : '';
    });
  }
})();
