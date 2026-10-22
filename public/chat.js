// Help chat on every page: prepared answers first (faq.json, matched by keywords), then the learner's own Cloudflare Workers AI if connected.
(function () {
  var me = document.currentScript, root = (me && me.dataset.root) || "", page = (me && me.dataset.page) || "all";
  var faq = null, cf = null;
  var STOP = { the: 1, a: 1, an: 1, is: 1, are: 1, what: 1, how: 1, do: 1, i: 1, to: 1, of: 1, in: 1, and: 1, or: 1, for: 1, on: 1, it: 1, my: 1, can: 1, does: 1, with: 1, why: 1, when: 1, where: 1, which: 1, this: 1, that: 1, be: 1, you: 1, me: 1, we: 1, should: 1, about: 1 };
  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }
  function words(s) { return (s.toLowerCase().match(/[a-z0-9]+/g) || []).filter(function (w) { return !STOP[w] && w.length > 1; }); }

  var btn = el("button", "chat-btn", "Ask a question");
  btn.setAttribute("aria-expanded", "false");
  var panel = el("aside", "chat-panel");
  panel.setAttribute("aria-label", "Help chat");
  panel.hidden = true;
  var head = el("div", "chat-head");
  head.append(el("b", "", "Ask about this page"));
  var close = el("button", "ghost", "Close");
  head.append(close);
  var log = el("div", "chat-log");
  log.setAttribute("aria-live", "polite");
  var form = el("form", "chat-form"), input = el("input");
  input.type = "text"; input.placeholder = "For example: what is a harness?"; input.setAttribute("aria-label", "Your question");
  var send = el("button", "open", "Ask");
  form.append(input, send);
  var foot = el("p", "chat-foot");
  panel.append(head, log, form, foot);
  document.body.append(btn, panel);

  function toggle(open) {
    panel.hidden = !open; btn.setAttribute("aria-expanded", String(open));
    if (open) { input.focus(); ensure(); }
  }
  btn.onclick = function () { toggle(panel.hidden); };
  close.onclick = function () { toggle(false); };

  function ensure() {
    if (!faq) fetch(root + "faq.json", { cache: "no-cache" }).then(function (r) { return r.json(); }).then(function (d) { faq = d.answers || []; }).catch(function () { faq = []; });
    if (!cf) fetch("/api/cf/status", { cache: "no-store" }).then(function (r) { return r.ok ? r.json() : {}; }).catch(function () { return {}; })
      .then(function (s) { cf = s || {}; foot.replaceChildren(); footer(); });
    if (!log.childNodes.length) say("bot", "Ask anything about this page or the program. I answer from the course's prepared answers first.");
  }
  function footer() {
    if (cf && cf.connected) foot.append("Extra answers use your Cloudflare Workers AI" + (cf.account ? " (" + cf.account + ")" : "") + ".");
    else { foot.append("Connect Cloudflare on the "); var a = el("a", "", "Practice page"); a.href = root + "tldr.html#connect"; foot.append(a, " for AI answers beyond the prepared ones."); }
  }
  function say(who, text, link, extra) {
    var m = el("div", "chat-msg " + who);
    m.append(el("p", "", text));
    if (link) { var a = el("a", "", "Read more"); a.href = root + link; m.append(a); }
    if (extra) m.append(extra);
    log.append(m); log.scrollTop = log.scrollHeight;
    return m;
  }
  function match(q) {
    var qw = words(q), ql = " " + q.toLowerCase() + " ", best = [];
    (faq || []).forEach(function (f) {
      var s = 0;
      (f.keywords || []).forEach(function (k) {
        var re = new RegExp("(^|[^a-z0-9])" + k.toLowerCase().replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + "([^a-z0-9]|$)");
        if (re.test(ql)) s += k.indexOf(" ") > 0 ? 4 : 3;
      });
      var fw = words(f.q);
      qw.forEach(function (w) { if (fw.indexOf(w) >= 0) s += 1; });
      if (s && (f.page === page || f.page === "all")) s += 1;
      if (s) best.push({ f: f, s: s });
    });
    return best.sort(function (a, b) { return b.s - a.s; });
  }
  function related(list) {
    if (!list.length) return null;
    var wrap = el("div", "chat-rel");
    wrap.append(el("span", "", "Related: "));
    list.forEach(function (x) { var b = el("button", "chat-chip", x.f.q); b.type = "button"; b.onclick = function () { ask(x.f.q); }; wrap.append(b); });
    return wrap;
  }
  function context() {
    var main = document.querySelector("main") || document.body;
    return (document.title + "\n" + main.innerText).slice(0, 3500);
  }
  // Needle 3 meaning search: used when keywords find nothing strong; answers only when one prepared question clearly wins.
  var needle = null, vecs = null, nid = 1, pend = {};
  function loadNeedle() {
    if (needle) return needle;
    needle = new Promise(function (resolve, reject) {
      var w = new Worker(root + "needle-worker.js");
      var t = setTimeout(function () { reject(new Error("timeout")); }, 120000);
      w.onmessage = function (e) {
        var m = e.data;
        if (m.type === "ready") { clearTimeout(t); resolve(w); return; }
        if (m.type === "failed") { clearTimeout(t); reject(new Error(m.error)); return; }
        var p = pend[m.id]; if (!p) return; delete pend[m.id];
        if (m.error) p.reject(new Error(m.error)); else p.resolve(m.vec);
      };
    });
    needle.catch(function () { needle = null; });
    return needle;
  }
  function embed(w, text) { return new Promise(function (resolve, reject) { var id = nid++; pend[id] = { resolve: resolve, reject: reject }; w.postMessage({ id: id, text: text }); }); }
  function semantic(q) {
    return Promise.all([loadNeedle(), vecs || fetch(root + "faq-vec.json").then(function (r) { return r.json(); })]).then(function (x) {
      vecs = x[1];
      return embed(x[0], q).then(function (v) {
        var c = Array.prototype.map.call(v, function (y, i) { return y - vecs.mean[i]; });
        var len = Math.hypot.apply(null, c) || 1;
        var scores = vecs.vecs.map(function (u, i) { var s = 0; for (var k = 0; k < u.length; k++) s += u[k] * c[k] / len; return { id: vecs.ids[i], s: s }; })
          .sort(function (a, b) { return b.s - a.s; });
        if (scores[0].s >= 0.40 && scores[0].s - scores[1].s >= 0.10) return (faq || []).filter(function (f) { return f.id === scores[0].id; })[0] || null;
        return null;
      });
    });
  }
  function ask(q) {
    say("me", q);
    var hits = match(q);
    if (hits.length && hits[0].s >= 3) {
      say("bot", hits[0].f.a, hits[0].f.link, related(hits.slice(1, 3)));
      return;
    }
    var wait = say("bot", needle ? "Searching by meaning..." : "Searching by meaning. The first search loads a small model (about 34 MB) into your browser once.");
    semantic(q).then(function (f) { wait.remove(); if (f) say("bot", f.a, f.link); else fallback(q, hits); },
      function () { wait.remove(); fallback(q, hits); });
  }
  function fallback(q, hits) {
    if (!(cf && cf.connected)) {
      say("bot", "I do not have a prepared answer for that yet. Try different words, or connect Cloudflare on the Practice page so I can answer with AI.", "tldr.html#connect", related(hits.slice(0, 3)));
      return;
    }
    var wait = say("bot", "Thinking...");
    fetch("/api/cf/chat", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ question: q, context: context(), page: page }) })
      .then(function (r) { return r.json().then(function (d) { return { ok: r.ok, d: d }; }); })
      .then(function (x) {
        wait.remove();
        if (x.ok && x.d.answer) say("bot", x.d.answer + "\n\n(AI answer from your Cloudflare account. It can be wrong; check the lessons.)");
        else if (x.d.error === "reconnect" || x.d.error === "not_connected") say("bot", "Your Cloudflare connection has expired. Reconnect it on the Practice page.", "tldr.html#connect");
        else say("bot", "The AI request did not work: " + (x.d.error || "unknown error") + ".");
      })
      .catch(function () { wait.remove(); say("bot", "Could not reach the AI service. Check your connection."); });
  }
  form.onsubmit = function (e) { e.preventDefault(); var q = input.value.trim(); if (!q) return; input.value = ""; if (!faq) { ensure(); setTimeout(function () { ask(q); }, 400); } else ask(q); };
})();
