// Machine setup check on module 00: the learner runs a few commands and pastes the output; each paste is checked as they type.
// When every check passes, the setup counts as done in this browser (fde-progress-v1).
(function () {
  var box = document.getElementById("system-check");
  if (!box) return;
  var KEY = "fde-progress-v1";
  var CHECKS = [
    { id: "git", cmd: "git --version", hint: "Looks like: git version 2.43.0", re: /^git version \d+\.\d+/i },
    { id: "python", cmd: "python3 --version", alt: "On Windows: py --version", hint: "Looks like: Python 3.12.4 (3.10 or newer)", re: /^Python 3\.(1\d|[2-9]\d)\b/ },
    { id: "code", cmd: "code --version", hint: "Paste the first line. Looks like: 1.95.3", re: /^\d+\.\d+\.\d+/ },
    { id: "email", cmd: "git config user.email", hint: "The email Git will sign your commits with", re: /^[^\s@]+@[^\s@]+\.[^\s@]+$/ },
    { id: "repo", cmd: "Your journal repository on GitHub", hint: "Looks like: https://github.com/your-name/fde-learning-journal", re: /^https:\/\/github\.com\/[\w.-]+\/[\w.-]+\/?$/ },
  ];
  function load() { try { return JSON.parse(localStorage.getItem(KEY) || "{}") || {}; } catch (e) { return {}; } }
  function save(all) { try { localStorage.setItem(KEY, JSON.stringify(all)); } catch (e) {} }
  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }
  var state = load().setup || { values: {}, passed: false };
  var body = box.querySelector(".mt-body"), status = el("p", "sc-status");
  var list = el("ol", "sc-list");
  CHECKS.forEach(function (c) {
    var li = el("li"), mark = el("span", "sc-mark");
    var head = el("p", "sc-cmd");
    head.append(el("code", "", c.cmd));
    if (c.alt) head.append(el("span", "sc-alt", " " + c.alt));
    var input = el("input");
    input.type = "text"; input.spellcheck = false; input.placeholder = c.hint; input.value = state.values[c.id] || "";
    input.setAttribute("aria-label", "Output of " + c.cmd);
    function check() {
      var v = input.value.trim().split("\n")[0].trim(), ok = c.re.test(v);
      li.classList.toggle("ok", ok);
      mark.textContent = !v ? "" : ok ? "OK" : "Not yet";
      state.values[c.id] = input.value.trim();
      update();
    }
    input.addEventListener("input", check);
    li.append(head, el("div", "sc-row"), mark);
    li.querySelector(".sc-row").append(input, mark);
    list.append(li);
    setTimeout(check, 0);
  });
  function update() {
    var passed = CHECKS.every(function (c) { return c.re.test(String(state.values[c.id] || "").split("\n")[0].trim()); });
    if (passed && !state.passed) state.at = new Date().toISOString();
    state.passed = passed;
    var all = load(); all.setup = state; save(all);
    status.className = "sc-status " + (passed ? "mt-ok" : "");
    status.textContent = passed ? "Machine setup confirmed. This step is complete." : "Run each command in your terminal and paste what it prints. Every line needs to show OK.";
    if (window.fdeProgress) window.fdeProgress.refresh();
  }
  body.replaceChildren(el("p", "", "Open a terminal (the one inside VS Code is fine), run each command below, and paste what it prints."), list, status);
})();
