// Code blocks: colour the syntax with highlight.js when it has loaded, and add a Copy button. window.fdeCode(root) re-runs it on new content.
(function () {
  function run(root) {
    (root || document).querySelectorAll(".code").forEach(function (box) {
      var code = box.querySelector("pre code");
      if (!code || box.dataset.ready) return;
      box.dataset.ready = "1";
      if (window.hljs && !code.classList.contains("language-plaintext")) { try { window.hljs.highlightElement(code); } catch (e) {} }
      var btn = document.createElement("button");
      btn.type = "button"; btn.className = "code-copy"; btn.textContent = "Copy";
      btn.addEventListener("click", function () {
        navigator.clipboard.writeText(code.textContent).then(function () { btn.textContent = "Copied"; setTimeout(function () { btn.textContent = "Copy"; }, 1500); },
          function () { btn.textContent = "Select and copy"; });
      });
      box.append(btn);
    });
  }
  window.fdeCode = run;
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", function () { run(); }); else run();
})();
