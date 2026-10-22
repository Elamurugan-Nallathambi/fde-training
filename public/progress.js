// Course completion: 14 checks (basics quick check, machine setup check, 12 module tests), read from this browser.
// Draws a bar into every [data-progress] element and turns a menu number green when its checks are done.
(function () {
  var UNITS = ["basics", "setup", "m00", "m01", "m02", "m03", "m04", "m05", "m06", "m07", "m08", "m09", "m10", "m11"];
  function read(key) { try { return JSON.parse(localStorage.getItem(key) || "{}") || {}; } catch (e) { return {}; } }
  function done(id) {
    if (id === "setup") { var s = read("fde-progress-v1").setup; return Boolean(s && s.passed); }
    var q = read("fde-quiz-v1")[id];
    return Boolean(q && q.passed);
  }
  function refresh() {
    var n = UNITS.filter(done).length, pct = Math.round((100 * n) / UNITS.length);
    document.querySelectorAll("[data-progress]").forEach(function (box) {
      box.replaceChildren();
      var label = document.createElement("p");
      label.className = "cp-label";
      label.textContent = pct + "% complete";
      var small = document.createElement("span");
      small.textContent = " (" + n + " of " + UNITS.length + " checks passed)";
      label.append(small);
      var bar = document.createElement("div");
      bar.className = "cp-bar";
      bar.setAttribute("role", "progressbar");
      bar.setAttribute("aria-valuemin", "0");
      bar.setAttribute("aria-valuemax", "100");
      bar.setAttribute("aria-valuenow", String(pct));
      bar.setAttribute("aria-label", "Course completion");
      var fill = document.createElement("span");
      fill.style.width = pct + "%";
      bar.append(fill);
      box.append(label, bar);
    });
    document.querySelectorAll("[data-units]").forEach(function (el) {
      el.classList.toggle("unit-done", el.dataset.units.split(" ").every(done));
    });
  }
  window.fdeProgress = { refresh: refresh, done: done, units: UNITS };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", refresh); else refresh();
  window.addEventListener("storage", refresh);
})();
