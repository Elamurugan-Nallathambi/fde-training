// Module test: 20 questions, pass at 80 percent, 3 attempts, 24 hours between attempts, then mentor review.
// Results stay in this browser (fde-quiz-v1); the learning path page copies them into the learner's GitHub journal.
(function () {
  var box = document.getElementById("module-test");
  if (!box) return;
  var mod = box.dataset.module, root = box.dataset.root || "../";
  var COUNT = Number(box.dataset.count) || 20, QUICK = box.dataset.quick === "1";
  var KEY = "fde-quiz-v1", PASS = 0.8, MAX = QUICK ? Infinity : 3, WAIT = QUICK ? 0 : 24 * 3600 * 1000;
  function load() { try { return JSON.parse(localStorage.getItem(KEY) || "{}") || {}; } catch (e) { return {}; } }
  function save(all) { try { localStorage.setItem(KEY, JSON.stringify(all)); } catch (e) {} }
  function rec() { var all = load(); return all[mod] || { attempts: [], passed: false, lockedUntil: 0, needsMentor: false }; }
  function put(r) { var all = load(); all[mod] = r; save(all); }
  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }
  function shuffle(a) { a = a.slice(); for (var i = a.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)); var t = a[i]; a[i] = a[j]; a[j] = t; } return a; }
  function fmtWait(ms) { var h = Math.floor(ms / 3600000), m = Math.ceil((ms % 3600000) / 60000); return h ? h + " h " + m + " min" : m + " min"; }
  var data = null;

  function status() {
    var r = rec(), body = box.querySelector(".mt-body");
    body.replaceChildren();
    var fails = r.attempts.filter(function (a) { return !a.pass; }).length;
    var last = r.attempts[r.attempts.length - 1];
    if (r.passed) {
      var best = r.attempts.filter(function (a) { return a.pass; }).pop();
      body.append(el("p", "mt-ok", "Passed with " + best.score + " of " + best.total + (QUICK ? ". This check is complete." : ". This module is complete.")));
      return;
    }
    if (r.needsMentor) {
      body.append(el("p", "mt-warn", "3 attempts used. A mentor will go through the module with you and reset your attempts."),
        el("p", "t-note", "Mentors reset attempts in your journal. Until then, review the lessons above, especially the ones listed in your last result."));
      return;
    }
    var info = el("p", "", QUICK ? COUNT + " quick questions on the basics. Pass mark 80 percent (" + Math.ceil(COUNT * PASS) + " of " + COUNT + "). Retake it as often as you like."
      : COUNT + " questions from this module. Pass mark 80 percent (" + Math.ceil(COUNT * PASS) + " of " + COUNT + "). You have " + (MAX - fails) + " of " + MAX + " attempts left, with 24 hours between attempts.");
    body.append(info);
    if (last && !last.pass) {
      var p = el("p", "mt-warn", "Last attempt: " + last.score + " of " + last.total + ". Review these lessons: ");
      (last.review || []).forEach(function (id, i) {
        var anchor = document.getElementById("l-" + id) ? "l-" + id : "g-" + id;
        var sec = document.getElementById(anchor), h = sec && sec.querySelector("h2");
        var a = el("a", "", h ? h.textContent : id); a.href = "#" + anchor;
        if (i) p.append(", "); p.append(a);
      });
      body.append(p);
    }
    if (r.lockedUntil > Date.now()) {
      body.append(el("p", "mt-wait", "Next attempt opens in " + fmtWait(r.lockedUntil - Date.now()) + "."));
      return;
    }
    var b = el("button", "open", (r.attempts.length ? "Retake" : "Start") + (QUICK ? " the quick check" : " the module test"));
    b.onclick = start;
    body.append(b);
  }

  function start() {
    var body = box.querySelector(".mt-body");
    body.replaceChildren(el("p", "t-note", "Loading questions..."));
    var go = function () {
      var qs = shuffle(data.questions).slice(0, COUNT).map(function (q) {
        var order = shuffle(q.options.map(function (_, i) { return i; }));
        return { q: q, order: order };
      });
      var form = el("form", "mt-form");
      qs.forEach(function (item, n) {
        var fs = el("fieldset", "mt-q");
        fs.append(el("legend", "", (n + 1) + ". " + item.q.q));
        item.order.forEach(function (oi) {
          var lab = el("label"), inp = document.createElement("input");
          inp.type = "radio"; inp.name = "q" + n; inp.value = oi; lab.append(inp, " " + item.q.options[oi]); fs.append(lab);
        });
        form.append(fs);
      });
      var msg = el("p", "mt-warn"), sub = el("button", "open", "Submit answers");
      sub.type = "submit"; form.append(msg, sub);
      form.onsubmit = function (e) {
        e.preventDefault();
        var picks = qs.map(function (_, n) { var c = form.querySelector('input[name="q' + n + '"]:checked'); return c ? Number(c.value) : null; });
        if (picks.some(function (p) { return p === null; })) { msg.textContent = "Answer all " + qs.length + " questions before you submit."; return; }
        var right = 0, review = {};
        qs.forEach(function (item, n) { if (picks[n] === item.q.answer) right++; else review[item.q.lesson] = true; });
        var total = qs.length, pass = right / total >= PASS, r = rec();
        r.attempts.push({ at: new Date().toISOString(), score: right, total: total, pass: pass, review: Object.keys(review) });
        if (pass) { r.passed = true; r.lockedUntil = 0; }
        else {
          r.lockedUntil = Date.now() + WAIT;
          if (r.attempts.filter(function (a) { return !a.pass; }).length >= MAX) r.needsMentor = true;
        }
        put(r);
        if (window.fdeProgress) window.fdeProgress.refresh();
        box.scrollIntoView({ behavior: "smooth", block: "start" });
        status();
        var nav = document.querySelector('.ln-mods a[aria-current="page"]');
        if (pass && nav) nav.classList.add("passed");
      };
      body.replaceChildren(form);
    };
    if (data) return go();
    fetch(root + "quiz/" + mod + ".json", { cache: "no-cache" }).then(function (r) { return r.json(); }).then(function (d) { data = d; go(); })
      .catch(function () { body.replaceChildren(el("p", "mt-warn", "Could not load the questions. Check your connection and reload the page.")); });
  }

  var r0 = rec();
  if (r0.passed) { var nav0 = document.querySelector('.ln-mods a[aria-current="page"]'); if (nav0) nav0.classList.add("passed"); }
  status();
  setInterval(function () { if (rec().lockedUntil > Date.now()) status(); }, 60000);
})();
