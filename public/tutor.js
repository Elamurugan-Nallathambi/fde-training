// FDE path tutor: GitHub journal, domain and project picker, setup guide, step evidence with rule checks and Workers AI suggestions.
const API = "https://api.github.com";
const DIR = "fde";

const S = { data: null, token: "", user: null, owner: "", repo: "", viewOnly: false, configured: false, profile: {}, files: {} };

// ---------- small helpers ----------
const $ = (sel) => document.querySelector(sel);
function h(tag, attrs, ...kids) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v === null || v === undefined || v === false) continue;
    if (k === "class") el.className = v;
    else if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
    else el.setAttribute(k, v === true ? "" : v);
  }
  for (const k of kids.flat(Infinity)) if (k !== null && k !== undefined && k !== false) el.append(k instanceof Node ? k : String(k));
  return el;
}
const safeUrl = (u) => (/^https?:\/\/\S+$/i.test(u || "") ? u : "");
const words = (s) => (String(s || "").trim().match(/\S+/g) || []).length;
const today = () => new Date().toISOString().slice(0, 10);
const store = {
  get(k, d) { try { const v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch (e) { return d; } },
  set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} },
};
const ses = {
  get(k) { try { return sessionStorage.getItem(k) || ""; } catch (e) { return ""; } },
  set(k, v) { try { v ? sessionStorage.setItem(k, v) : sessionStorage.removeItem(k); } catch (e) {} },
};
function toast(msg, bad) {
  const t = h("div", { class: "t-toast" + (bad ? " bad" : ""), role: "status" }, msg);
  document.body.append(t);
  setTimeout(() => t.remove(), 4200);
}
// Runs a GitHub action with the button disabled and a spinner, so a slow call cannot be clicked twice.
async function busy(btn, label, fn) {
  if (btn.dataset.busy) return;
  const old = btn.textContent;
  btn.dataset.busy = "1"; btn.disabled = true; btn.setAttribute("aria-busy", "true");
  btn.replaceChildren(h("span", { class: "t-spin", "aria-hidden": "true" }), label);
  try { await fn(); } finally {
    if (btn.isConnected) { btn.replaceChildren(old); btn.disabled = false; btn.removeAttribute("aria-busy"); delete btn.dataset.busy; }
  }
}
const b64 = (s) => { let bin = ""; new TextEncoder().encode(s).forEach((b) => (bin += String.fromCharCode(b))); return btoa(bin); };
const unb64 = (s) => new TextDecoder().decode(Uint8Array.from(atob(s.replace(/\n/g, "")), (c) => c.charCodeAt(0)));

// ---------- GitHub ----------
async function gh(path, opts = {}) {
  const headers = { Accept: "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28" };
  if (S.token) headers.Authorization = "Bearer " + S.token;
  if (opts.body) headers["Content-Type"] = "application/json";
  const res = await fetch(API + path, { ...opts, headers });
  if (res.status === 404) return null;
  if (!res.ok) throw new Error("GitHub " + res.status + ": " + ((await res.json().catch(() => ({}))).message || res.statusText));
  return res.status === 204 ? {} : res.json();
}
async function readFile(path) {
  const r = await gh(`/repos/${S.owner}/${S.repo}/contents/${path}`);
  return r && r.content !== undefined ? { text: unb64(r.content), sha: r.sha } : null;
}
async function writeFile(path, text, message) {
  const cur = await gh(`/repos/${S.owner}/${S.repo}/contents/${path}`);
  return gh(`/repos/${S.owner}/${S.repo}/contents/${path}`, {
    method: "PUT",
    body: JSON.stringify({ message, content: b64(text), sha: cur && cur.sha ? cur.sha : undefined }),
  });
}
function embedData(obj) { return "<!-- fde-data " + JSON.stringify(obj).replace(/--/g, "-\\u002d") + " -->\n"; }
function parseData(text) {
  const m = /<!-- fde-data (\{[\s\S]*\}) -->/.exec(text || "");
  try { return m ? JSON.parse(m[1]) : null; } catch (e) { return null; }
}

async function loadRepoState() {
  S.profile = {}; S.files = {}; S.work = [];
  try {
    for (let page = 1; page <= 3; page++) {
      const list = await gh(`/repos/${S.owner}/${S.repo}/commits?path=projects&per_page=100&page=${page}`);
      if (!Array.isArray(list) || !list.length) break;
      S.work.push(...list.map((c) => ({ sha: c.sha.slice(0, 7), at: c.commit.author.date, msg: c.commit.message.split("\n")[0], url: c.html_url })));
      if (list.length < 100) break;
    }
  } catch (e) { console.warn("commits", e); }
  const prof = await readFile(`${DIR}/profile.md`);
  if (prof) S.profile = parseData(prof.text) || {};
  const act = await readFile(`${DIR}/activity.md`);
  const logged = (act && parseData(act.text)) || { opens: [] };
  if (!S.viewOnly) {
    const all = store.get("fde-opens", {});
    for (const o of logged.opens || []) {
      if (!o.url) continue;
      const cur = all[o.url];
      if (!cur || o.at < cur.first) all[o.url] = { slug: (cur && cur.slug) || "", title: o.title, mins: o.mins, first: o.at, last: (cur && cur.last) || o.at, count: (cur && cur.count) || 1 };
    }
    store.set("fde-opens", all);
  }
  const qz = await readFile(`${DIR}/quizzes.md`);
  S.quizRemote = ((qz && parseData(qz.text)) || {}).quizzes || {};
  if (!S.viewOnly) {
    mergeRemoteQuiz(S.quizRemote);
    const mentor = await readFile(`${DIR}/mentor.md`);
    if (mentor) applyMentorResets(mentor.text);
  }
  const list = await gh(`/repos/${S.owner}/${S.repo}/contents/${DIR}/steps`);
  if (Array.isArray(list)) {
    await Promise.all(list.filter((f) => f.name.endsWith(".md")).map(async (f) => {
      const file = await readFile(f.path);
      const d = file && parseData(file.text);
      if (d && d.slug) S.files[d.slug] = d;
    }));
  }
}

async function connectRepo(name) {
  S.owner = S.user.login; S.repo = name;
  let r = await gh(`/repos/${S.owner}/${S.repo}`);
  if (!r) {
    r = await gh(`/user/repos`, { method: "POST", body: JSON.stringify({ name, description: "My FDE training journal: project, evidence and progress", private: false, auto_init: true }) });
    toast("Created repository " + name);
  }
  store.set("fde-repo", name);
  await installLocalTools();
  await loadRepoState();
}

// Puts fde.py and fde/README.md in the journal so learners can track progress from their own machine.
const README = ["# fde folder: your training record", "",
  "The tutor page (" + location.origin + "/tldr) and `fde.py` both read and write the files in this folder.", "",
  "- `profile.md`: your project and how you chose to build it", "- `steps/`: one file per step with your evidence, checks and time",
  "- `progress.md`: the summary your mentor or manager sees", "- `activity.md`: when you opened each resource", "",
  "Please do not edit files in this folder by hand. The line starting with `<!-- fde-data` at the end of each file is read by the tools; changing it can break your progress.",
  "Put your own notes, code and drafts anywhere else in the repository (for example `notes/`, `labs/` or `drafts/`).", "",
  "## Work from your machine", "", "```bash", "git pull", "python3 fde.py init        # create projects/<your-project>/ to build in", "python3 fde.py status      # where you are", "python3 fde.py next        # what to do next",
  "python3 fde.py open 05     # open step 05 resources and start the clock", "python3 fde.py log 05      # write evidence, check it, commit and push", "```", "",
  "On Windows, use `py fde.py` instead of `python3 fde.py`. Run `python3 fde.py help` for all commands.", ""].join("\n");

async function installLocalTools() {
  try {
    const want = await (await fetch("fde.py", { cache: "no-cache" })).text();
    const have = await readFile("fde.py");
    if (!have || have.text !== want) await writeFile("fde.py", want, have ? "Update fde.py helper" : "Add fde.py helper for working from your machine");
    if (!(await readFile(`${DIR}/README.md`))) await writeFile(`${DIR}/README.md`, README, "Add fde folder guide");
  } catch (e) { console.warn("local tools", e); }
}

// ---------- rule checks: these decide whether a step is done ----------
function checkStep(step, values) {
  const out = [];
  for (const f of step.fields) {
    if (f.id === "broke") continue;
    const v = String(values[f.id] || "").trim();
    if (!v) { out.push({ ok: false, text: `${f.label}: missing` }); continue; }
    if (f.kind === "url" && !safeUrl(v)) out.push({ ok: false, text: `${f.label}: needs a full link starting with https://` });
    else if (f.min_words && words(v) < f.min_words) out.push({ ok: false, text: `${f.label}: ${words(v)} of at least ${f.min_words} words` });
    else if (f.need === "number" && !/\d/.test(v)) out.push({ ok: false, text: `${f.label}: should include your numbers` });
    else if (/\b(todo|tbd|lorem ipsum|placeholder)\b/i.test(v)) out.push({ ok: false, text: `${f.label}: still has a placeholder` });
    else out.push({ ok: true, text: f.label });
  }
  return out;
}
const isDone = (slug) => Boolean(S.files[slug] && S.files[slug].checks && S.files[slug].checks.pass);

// Save and tutor buttons stay off until every required field has a few words; the tooltip says what is missing.
const MIN_START = 3;
function startGap(fields, values) {
  const short = fields.filter(([id, label, url, min]) => { const v = String(values[id] || "").trim(); return url ? !safeUrl(v) : words(v) < Math.min(MIN_START, min || MIN_START); }).map((f) => f[1]);
  return short.length ? `Write a few words first in: ${short.join("; ")}` : "";
}
function gate(btns, msg) {
  for (const b of btns) { b.setAttribute("aria-disabled", String(Boolean(msg))); b.classList.toggle("is-off", Boolean(msg)); b.title = msg; }
}
const allowed = (e) => e.currentTarget.getAttribute("aria-disabled") !== "true";

// Project work per step: commits under projects/ after the previous saved step and up to this step's save.
const savedAt = (f) => (f ? f.savedAt || (f.saved ? f.saved + "T23:59:59Z" : "") : "");
function stepWork(step) {
  const steps = S.data.steps, i = steps.indexOf(step);
  const prev = steps.slice(0, i).map((x) => savedAt(S.files[x.slug])).filter(Boolean).sort().pop() || "";
  const end = savedAt(S.files[step.slug]);
  if (!end) {
    const later = steps.slice(i + 1).some((x) => S.files[x.slug]);
    return later ? [] : (S.work || []).filter((c) => c.at > prev);
  }
  return (S.work || []).filter((c) => c.at > prev && c.at <= end);
}
// Points per step, 20 max: checks passed 10, time met 5 (confirmed early 2, self-paced 5), at least one project commit 5.
function stepPoints(step) {
  const f = S.files[step.slug];
  if (!f) return 0;
  let p = f.checks && f.checks.pass ? 10 : 0;
  const t = f.time || {};
  p += !t.total || t.met ? 5 : t.confirmed_early ? 2 : 0;
  if (stepWork(step).length) p += 5;
  return p;
}
const MAX_POINTS = 20;

// ---------- setup guide ----------
const QUESTIONS = [
  { id: "facts", q: "Does the answer need facts from documents or records, not just general knowledge?", a: [["yes", "Yes"], ["no", "No"]] },
  { id: "size", q: "How much text would it need to look through?", a: [["small", "Small: fits in one prompt"], ["large", "Large: many documents or a growing library"]], when: (x) => x.facts === "yes" },
  { id: "codes", q: "Do people search with exact codes, IDs, part numbers or names?", a: [["yes", "Yes, often"], ["no", "Mostly plain language"]], when: (x) => x.facts === "yes" && x.size === "large" },
  { id: "steps", q: "Are the steps the same every time?", a: [["fixed", "Yes, a fixed order"], ["varies", "No, it depends on the case"]] },
  { id: "leave", q: "May this data be sent to an external model provider under a business agreement?", a: [["yes", "Yes"], ["no", "No, it must stay inside"], ["unsure", "Not sure yet"]] },
  { id: "volume", q: "How many items a day will it handle?", a: [["low", "Tens or hundreds"], ["high", "Thousands or more"]] },
];
function recommend(x) {
  const r = {};
  if (x.facts === "no") r.retrieval = "No retrieval: put the instructions and the record itself in the prompt";
  else if (!x.facts) r.retrieval = "";
  else if (x.size === "small") r.retrieval = "Put the documents straight into the prompt, with prompt caching";
  else if (x.codes === "yes") r.retrieval = "Hybrid search: keyword plus vector, so exact codes and meaning both match";
  else if (x.codes === "no") r.retrieval = "Vector search over chunked documents, with citations";
  r.flow = x.steps === "fixed" ? "A fixed workflow: plain code with one or two model calls, and a human approval step"
    : x.steps === "varies" ? "A small agent with a few tools, limited permissions and a human approval step" : "";
  r.model = x.leave === "no" ? "An open-weight model hosted inside the client's environment, or a model in their own cloud account under agreed terms"
    : x.leave === "unsure" ? "Build on synthetic data with a hosted model now, and settle the data question in discovery"
    : x.volume === "high" ? "Prove quality with a frontier model first, then move the high-volume step to a smaller, cheaper model"
    : x.leave === "yes" ? "A frontier model through its API; keep the model name in config so it can change" : "";
  return r;
}

// ---------- render: journal ----------
// Cloudflare connection for the help chat; only on deployments built with chat switched on.
async function renderCf(box) {
  box.replaceChildren();
  if (document.body.dataset.chat !== "1" || S.viewOnly) return;
  const row = h("div", { class: "t-cf" }, h("p", { class: "t-note" }, "Checking Cloudflare..."));
  box.append(row);
  let st = {};
  try { st = await (await fetch("/api/cf/status", { cache: "no-store" })).json(); } catch (e) {}
  row.replaceChildren();
  if (!st.configured) { row.append(h("p", { class: "t-note" }, "Cloudflare connection is not switched on for this site yet.")); return; }
  if (st.connected) {
    row.append(h("p", {}, h("b", {}, "Cloudflare connected"), st.account ? ` (${st.account})` : "", ". The help chat can now answer with your Workers AI."),
      h("button", { class: "ghost", onclick: async () => { await fetch("/api/cf/logout", { method: "POST" }); renderAll(); } }, "Disconnect"));
  } else {
    row.append(h("a", { class: "open", href: "/api/cf/login" }, "Connect with Cloudflare"),
      h("p", { class: "t-note" }, "Lets the help chat on every page answer with AI from your own Cloudflare account. The access stays on the server side of this site and is never shown to page scripts; you can disconnect here or revoke it in your Cloudflare profile."));
  }
}

async function renderGh() {
  const box = $("#gh-box"); box.replaceChildren();
  renderCf($("#cf-box"));
  if (S.viewOnly) {
    box.append(h("p", {}, "Viewing the progress of ", h("a", { href: `https://github.com/${S.owner}/${S.repo}`, target: "_blank", rel: "noopener" }, `${S.owner}/${S.repo}`), " (read only). ",
      h("a", { href: "tldr.html" }, "Start your own path")));
    return;
  }
  if (!S.user) {
    if (S.configured) {
      box.append(h("div", { class: "t-row" }, h("a", { class: "open", href: "/api/gh/login", onclick: (e) => { const a = e.currentTarget; if (a.dataset.busy) { e.preventDefault(); return; } a.dataset.busy = "1"; a.setAttribute("aria-disabled", "true"); a.replaceChildren(h("span", { class: "t-spin", "aria-hidden": "true" }), "Opening GitHub..."); } }, "Sign in with GitHub"),
        h("p", { class: "t-note" }, "The page asks for permission to write to your public repositories so it can save your evidence to one journal repository. The access key stays in this browser tab and is gone when you close it.")));
    } else {
      box.append(h("p", { class: "t-warn" }, "GitHub sign-in is not switched on for this site yet. You can still explore domains, projects and steps; saving needs sign-in."));
    }
  } else {
    const input = h("input", { type: "text", value: S.repo || store.get("fde-repo", "fde-learning-journal"), "aria-label": "Journal repository name" });
    const go = h("button", { class: "open", onclick: async () => {
      const name = input.value.trim();
      if (!/^[A-Za-z0-9._-]{1,100}$/.test(name)) return toast("Use letters, numbers, dot, dash or underscore", true);
      await busy(go, "Connecting...", async () => { try { await connectRepo(name); renderAll(); } catch (e) { toast(e.message, true); } });
    } }, S.repo ? "Switch" : "Connect");
    box.append(h("div", { class: "t-row" },
      h("p", {}, "Signed in as ", h("b", {}, S.user.login), ". Journal repository:"), input, go,
      h("button", { class: "ghost", onclick: () => { ses.set("fde-gh", ""); S.token = ""; S.user = null; S.repo = ""; renderAll(); } }, "Sign out")));
    if (S.repo) {
      const share = new URL(`tldr.html?view=${S.owner}/${S.repo}`, location.href).toString();
      box.append(h("p", { class: "t-note" }, "Saving to ", h("a", { href: `https://github.com/${S.owner}/${S.repo}/tree/HEAD/${DIR}`, target: "_blank", rel: "noopener" }, `${S.owner}/${S.repo}/${DIR}`),
        ". Share your progress with your mentor or manager: ", h("a", { href: share }, share)));
      box.append(h("details", { class: "t-view" }, h("summary", {}, "Work from your machine"),
        h("p", { class: "t-note" }, "Your journal includes fde.py, a small helper that uses the same files as this page. Clone the repository once, then run these in its folder:"),
        h("pre", { class: "t-cmd" }, `git clone https://github.com/${S.owner}/${S.repo}.git\ncd ${S.repo}\npython3 fde.py init       # create projects/<your-project>/ from your chosen project\npython3 fde.py status\npython3 fde.py next\npython3 fde.py open 05\npython3 fde.py log 05`),
        h("p", { class: "t-note" }, "Do not edit files inside the fde folder by hand. Your own notes and code can go anywhere else.")));
    }
  }
  const view = h("input", { type: "text", placeholder: "owner/repository", "aria-label": "Repository to view" });
  box.append(h("details", { class: "t-view" }, h("summary", {}, "View someone's progress"),
    h("div", { class: "t-row" }, view, h("button", { class: "ghost", onclick: () => {
      const v = view.value.trim();
      if (/^[\w.-]+\/[\w.-]+$/.test(v)) location.href = "tldr.html?view=" + v; else toast("Enter it as owner/repository", true);
    } }, "View"))));
}

// ---------- render: project ----------
function projectDraft() { return Object.assign({ industry: "", example: "", title: "", problem: "", users: "", data: "", measure: "" }, store.get("fde-project", {}), S.profile.project || {}); }

function renderProject() {
  const box = $("#project-box"); box.replaceChildren();
  const p = projectDraft();
  const inds = S.data.industries;
  if (S.viewOnly) {
    box.append(projectSummary(p));
    return;
  }
  if (!inds.length) { box.append(h("p", { class: "t-note" }, "Domain examples are loading soon. You can still enter your own idea below.")); }
  const sel = h("select", { "aria-label": "Industry", onchange: () => { p.industry = sel.value; p.example = ""; store.set("fde-project", p); renderProject(); } },
    h("option", { value: "" }, "Choose your industry"), inds.map((i) => h("option", { value: i.id, selected: i.id === p.industry }, i.name)));
  box.append(h("div", { class: "t-row" }, h("label", {}, h("b", {}, "Industry ")), sel));
  const ind = inds.find((i) => i.id === p.industry);
  if (ind) {
    box.append(h("p", { class: "t-note" }, ind.blurb));
    const grid = h("div", { class: "t-ex-grid" });
    for (const ex of ind.examples) {
      grid.append(h("article", { class: "t-ex" + (p.example === ex.id ? " is-picked" : "") },
        h("p", { class: "t-when" }, ex.function, " / ", ex.pattern),
        h("h3", {}, ex.title),
        h("p", {}, ex.bottleneck),
        h("dl", {}, h("dt", {}, "Data"), h("dd", {}, ex.data), h("dt", {}, "Person approves"), h("dd", {}, ex.approval), h("dt", {}, "Measured by"), h("dd", {}, ex.measure)),
        h("button", { class: p.example === ex.id ? "open" : "ghost", onclick: () => {
          Object.assign(p, { example: ex.id, title: ex.title, problem: ex.bottleneck, data: ex.data, measure: ex.measure, users: p.users || "" });
          store.set("fde-project", p); renderProject(); renderSteps(); $("#project-form").scrollIntoView({ behavior: "smooth", block: "start" });
        } }, p.example === ex.id ? "Chosen" : "Use this project")));
    }
    box.append(grid);
  }
  const fields = [["title", "Project title", "text"], ["problem", "The problem: who struggles, with what, and why it matters", "long"], ["users", "Who will use it, and who approves its output", "text"], ["data", "What data you will use (synthetic or public is fine)", "long"], ["measure", "How you will know it works (your success measure)", "long"]];
  const form = h("div", { class: "t-form", id: "project-form" }, h("h3", {}, p.example ? "Make it yours: edit the project to fit your idea" : "Or describe your own idea"));
  for (const [id, label, kind] of fields) {
    const input = kind === "long" ? h("textarea", { rows: 3 }) : h("input", { type: "text" });
    input.value = p[id] || "";
    input.addEventListener("input", () => { p[id] = input.value; store.set("fde-project", p); gateIdea(); });
    if (id === "title") input.addEventListener("change", renderSteps);
    form.append(h("label", { class: "t-field" }, h("span", {}, label), input));
  }
  const out = h("div", { class: "t-feedback", "aria-live": "polite" });
  const ideaBtns = [h("button", { class: "open", onclick: (e) => allowed(e) && busy(e.currentTarget, "Saving to GitHub...", () => saveProfile({ project: p }, "Save project")) }, "Save project to GitHub"),
    h("button", { class: "ghost", onclick: (e) => allowed(e) && reviewIdea(p, out) }, "Ask the tutor to review my idea")];
  function gateIdea() { gate(ideaBtns, startGap(fields.filter((f) => f[0] !== "title").map(([id, label]) => [id, label]), p)); }
  form.append(h("div", { class: "t-row" }, ...ideaBtns), out);
  gateIdea();
  box.append(form);
}

function projectSummary(p) {
  if (!p.title) return h("p", { class: "t-note" }, "No project saved yet.");
  return h("dl", { class: "t-sum" }, ["title", "problem", "users", "data", "measure"].map((k) => [h("dt", {}, k), h("dd", {}, p[k] || "-")]));
}

// ---------- render: setup guide ----------
function renderDecide() {
  const box = $("#decide-box"); box.replaceChildren();
  const saved = S.profile.setup || store.get("fde-setup", { answers: {}, why: "" });
  const x = saved.answers || {};
  const rec = recommend(x);
  if (!S.viewOnly) {
    for (const q of QUESTIONS) {
      if (q.when && !q.when(x)) continue;
      box.append(h("fieldset", { class: "t-q" }, h("legend", {}, q.q),
        q.a.map(([v, label]) => h("label", {}, h("input", { type: "radio", name: "q-" + q.id, value: v, checked: x[q.id] === v, onchange: () => {
          x[q.id] = v; saved.answers = x; store.set("fde-setup", saved); renderDecide();
        } }), " ", label))));
    }
  }
  const rows = [["Retrieval", rec.retrieval], ["Workflow or agent", rec.flow], ["Model", rec.model]].filter((r) => r[1]);
  box.append(h("div", { class: "t-rec" }, h("p", { class: "eyebrow" }, "Recommended setup"),
    rows.length ? h("dl", {}, rows.map(([k, v]) => [h("dt", {}, k), h("dd", {}, v)])) : h("p", { class: "t-note" }, "Answer the questions to see a recommendation.")));
  if (S.viewOnly) { if (saved.why) box.append(h("p", {}, h("b", {}, "Why it fits: "), saved.why)); return; }
  const why = h("textarea", { rows: 3, placeholder: "Why this setup fits your project, or why you chose differently" });
  why.value = saved.why || "";
  why.addEventListener("input", () => { saved.why = why.value; store.set("fde-setup", saved); });
  box.append(h("label", { class: "t-field" }, h("span", {}, "Your reasoning (at least 15 words)"), why),
    h("button", { class: "open", onclick: (e) => {
      const btn = e.currentTarget;
      if (rows.length < 3) return toast("Answer all the questions first", true);
      if (words(saved.why) < 15) return toast("Write at least 15 words on why it fits", true);
      busy(btn, "Saving to GitHub...", () => saveProfile({ setup: { answers: x, recommended: rec, why: saved.why } }, "Save setup choices"));
    } }, "Save setup to GitHub"));
}

// ---------- profile file ----------
async function saveProfile(patch, msg) {
  if (!S.user || !S.repo) return toast("Sign in and connect your journal repository first", true);
  const prof = Object.assign({}, S.profile, patch, { updated: today() });
  const p = prof.project || {}, s = prof.setup || {};
  const ind = S.data.industries.find((i) => i.id === p.industry);
  const md = [`# My FDE project: ${p.title || "(untitled)"}`, "",
    `Industry: ${ind ? ind.name : "-"}`, `Started from example: ${p.example || "my own idea"}`, `Updated: ${prof.updated}`, "",
    "## Problem", p.problem || "-", "", "## Users and approver", p.users || "-", "", "## Data", p.data || "-", "", "## Success measure", p.measure || "-", "",
    "## How I will build it",
    ...(s.recommended ? [`- Retrieval: ${s.recommended.retrieval || "-"}`, `- Workflow or agent: ${s.recommended.flow || "-"}`, `- Model: ${s.recommended.model || "-"}`] : ["- Not decided yet"]),
    "", "Why: " + (s.why || "-"), "", embedData(prof)].join("\n");
  try {
    await writeFile(`${DIR}/profile.md`, md, msg);
    S.profile = prof;
    await writeProgress();
    renderBadges();
    toast("Saved to GitHub");
  } catch (e) { toast(e.message, true); }
}

async function writeProgress() {
  const steps = S.data.steps;
  const done = steps.filter((s) => isDone(s.slug)).length;
  const rows = steps.map((s) => {
    const f = S.files[s.slug];
    const status = !f ? "not started" : f.checks && f.checks.pass ? "done" : "saved, checks not passing";
    return `| ${s.num} | ${s.title} | ${status} | ${f ? stepWork(s).length : ""} | ${f ? stepPoints(s) : 0} | ${f ? f.saved : ""} |`;
  });
  const pts = steps.reduce((a, s) => a + stepPoints(s), 0);
  const md = [`# FDE path progress: ${done} of ${steps.length} steps proven`, "",
    `Project: ${(S.profile.project || {}).title || "-"}  `, `Points: ${pts} of ${steps.length * MAX_POINTS}  `, `Updated: ${today()}`, "",
    "| Step | Title | Status | Project commits | Points | Saved |", "|---|---|---|---|---|---|", ...rows, "",
    "A step counts as done only when its evidence file is saved here and passes the checks. Points: 10 checks passed, 5 time met, 5 at least one commit under projects/ during the step.",
    "This is a basic tracker for accountability. It counts what is saved and committed; it does not judge quality.", ""].join("\n");
  await writeFile(`${DIR}/progress.md`, md, `Progress: ${done} of ${steps.length}`);
}

// ---------- time on resources ----------
// Opens are kept in this browser and logged to fde/activity.md; a step needs the timed resources' minutes plus 30% since first open.
const BUFFER = 1.3;
const opens = () => store.get("fde-opens", {});
let pendingLog = [], logTimer = null;

function recordOpen(step, link) {
  const all = opens(), now = new Date().toISOString();
  const o = all[link.url] || { slug: step.slug, title: link.title, mins: link.mins, first: now, count: 0 };
  o.last = now; o.count += 1; all[link.url] = o; store.set("fde-opens", all);
  pendingLog.push({ at: now, step: step.num, title: link.title, url: link.url, mins: link.mins });
  if (S.user && S.repo) { clearTimeout(logTimer); logTimer = setTimeout(flushLog, 15000); }
}

async function flushLog() {
  if (!pendingLog.length || !S.user || !S.repo) return;
  const batch = pendingLog; pendingLog = [];
  try {
    const cur = await readFile(`${DIR}/activity.md`);
    const list = ((cur && parseData(cur.text)) || { opens: [] }).opens.concat(batch);
    const rows = list.slice().reverse().map((o) => `| ${o.at.replace("T", " ").slice(0, 16)} | ${o.step} | ${o.title.replace(/\|/g, "/")} | ${o.mins || "self-paced"} |`);
    const md = ["# Learning activity", "", "Resources opened from the tutor page, newest first. Times are UTC, when the link was opened.", "",
      "| When | Step | Resource | Expected minutes |", "|---|---|---|---|", ...rows, "", embedData({ opens: list })].join("\n");
    await writeFile(`${DIR}/activity.md`, md, `Activity: opened ${batch.length} resource${batch.length > 1 ? "s" : ""}`);
  } catch (e) { pendingLog = batch.concat(pendingLog); console.warn("activity log", e); }
}
window.addEventListener("pagehide", () => { if (pendingLog.length) flushLog(); });

function stepTime(step) {
  const all = opens();
  const timed = step.links.filter((l) => l.mins && !l.optional);
  const total = timed.reduce((a, l) => a + l.mins, 0);
  const required = Math.ceil(total * BUFFER);
  const opened = step.links.filter((l) => all[l.url]);
  const firsts = opened.map((l) => Date.parse(all[l.url].first)).filter((x) => !isNaN(x));
  const first = firsts.length ? Math.min(...firsts) : null;
  const elapsed = first ? Math.floor((Date.now() - first) / 60000) : 0;
  const unopened = timed.filter((l) => !all[l.url]);
  return { total, required, elapsed, first, unopened, selfPaced: step.links.filter((l) => !l.mins), opened,
    met: total > 0 && !unopened.length && elapsed >= required };
}
function stepTimeLabel(step) {
  const total = step.links.reduce((a, l) => a + (l.optional ? 0 : l.mins || 0), 0);
  const selfPaced = step.links.some((l) => !l.mins && !l.optional);
  if (!total) return " / self-paced";
  return " / " + fmtMin(Math.ceil(total * BUFFER)) + (selfPaced ? " + self-paced" : "");
}
const fmtMin = (m) => (m >= 60 ? `${Math.floor(m / 60)} h ${m % 60 ? (m % 60) + " min" : ""}`.trim() : `${m} min`);

// ---------- module tests: results from this browser, saved to fde/quizzes.md; mentors reset with a line in fde/mentor.md ----------
const QKEY = "fde-quiz-v1";
function quizState() { return S.viewOnly ? (S.quizRemote || {}) : store.get(QKEY, {}); }
function applyMentorResets(text) {
  const all = store.get(QKEY, {});
  let changed = false;
  for (const m of String(text || "").matchAll(/reset\s+(m\d\d)(?:\s+(\d{4}-\d{2}-\d{2}))?/gi)) {
    const mod = m[1].toLowerCase(), day = m[2] || "", r = all[mod];
    if (!r || !r.needsMentor) continue;
    const last = r.attempts.length ? r.attempts[r.attempts.length - 1].at.slice(0, 10) : "";
    if (day && day < last) continue;
    all[mod] = { attempts: [], passed: false, lockedUntil: 0, needsMentor: false, resets: (r.resets || 0) + 1, history: (r.history || []).concat(r.attempts) };
    changed = true;
  }
  if (changed) store.set(QKEY, all);
}
function mergeRemoteQuiz(remote) {
  const all = store.get(QKEY, {});
  for (const [mod, r] of Object.entries(remote || {})) if (!all[mod] || (r.passed && !all[mod].passed)) all[mod] = r;
  store.set(QKEY, all);
}
function quizLine(mod, r) {
  if (!r || !r.attempts) return "not taken";
  if (r.passed) { const b = r.attempts.filter((a) => a.pass).pop(); return `passed ${b.score}/${b.total}`; }
  if (r.needsMentor) return "needs mentor review";
  const fails = r.attempts.filter((a) => !a.pass).length;
  if (!fails) return "not taken";
  return `${fails} of 3 attempts used` + (r.lockedUntil > Date.now() ? ", next attempt opens later" : ", can retake now");
}
async function syncQuizzes() {
  if (S.viewOnly || !S.user || !S.repo) return;
  const all = store.get(QKEY, {});
  if (JSON.stringify(all) === JSON.stringify(S.quizRemote || {})) return;
  const rows = (S.data.modules || []).map((m) => `| ${m.file.slice(1)} | ${m.title} | ${quizLine(m.file, all[m.file])} |`);
  const md = ["# Module tests", "", "Each module test has 20 questions. Pass mark 80 percent. 3 attempts, 24 hours apart. After 3 fails a mentor reviews the module with the learner.", "",
    "To reset a learner's attempts after a review, a mentor adds a line like `reset m04 " + today() + "` to fde/mentor.md.", "",
    "| Module | Title | Result |", "|---|---|---|", ...rows, "", embedData({ quizzes: all })].join("\n");
  try { await writeFile(`${DIR}/quizzes.md`, md, "Module test results"); S.quizRemote = all; } catch (e) { console.warn("quiz sync", e); }
}
function renderQuizzes(box) {
  const mods = S.data.modules || [];
  if (!mods.length) return;
  const st = quizState();
  const passed = mods.filter((m) => st[m.file] && st[m.file].passed).length;
  box.append(h("div", { class: "t-tests" }, h("p", { class: "eyebrow" }, `Module tests: ${passed} of ${mods.length} passed`),
    h("ul", {}, mods.map((m) => {
      const r = st[m.file], line = quizLine(m.file, r);
      const cls = r && r.passed ? "ok" : r && r.needsMentor ? "warn" : "";
      return h("li", { class: cls }, h("a", { href: `learn/${m.file}.html#module-test`, target: "_blank", rel: "noopener" }, `${m.file.slice(1)} ${m.title}`), h("span", {}, line));
    }))));
}

// ---------- render: steps ----------
function renderSummary() {
  const box = $("#summary-box"); box.replaceChildren();
  const n = S.data.steps.length, done = S.data.steps.filter((s) => isDone(s.slug)).length;
  const bar = h("div", { class: "pbar" }, h("span", { style: `width:${(100 * done) / n}%` }));
  const pts = S.data.steps.reduce((a, s) => a + stepPoints(s), 0);
  box.append(h("div", { class: "t-progress" }, bar, h("p", {}, `${done} of ${n} steps proven`), h("p", { class: "t-points" }, `${pts} of ${n * MAX_POINTS} points`)),
    h("p", { class: "t-note" }, S.repo ? `Counted from the journal repository: ${(S.work || []).length} commits under projects/ so far. Per step: 10 points for evidence that passes the checks, 5 for time, 5 for project commits.` : "Sign in and connect a journal to start counting proven steps."));
  renderQuizzes(box);
  if (done === n) box.append(h("p", { class: "t-win" }, "Path complete. Every step has saved evidence that passes the checks. Share your journal link with your mentor for the final review panel."));
}

function renderSteps() {
  const box = $("#steps-box"); box.replaceChildren();
  for (const step of S.data.steps) {
    const f = S.files[step.slug];
    const status = !f ? ["Not started", ""] : f.checks && f.checks.pass ? ["Done", "ok"] : ["Saved, checks not passing", "warn"];
    const values = Object.assign({}, store.get("fde-draft-" + step.slug, {}), f ? f.fields : {});
    const checksEl = h("ul", { class: "t-checks" });
    const feedback = h("div", { class: "t-feedback", "aria-live": "polite" }, f && f.tutor ? f.tutor : "");
    const stepBtns = [];
    const required = step.fields.filter((fd) => fd.id !== "broke").map((fd) => [fd.id, fd.label, fd.kind === "url", fd.min_words]);
    const paint = () => { gate(stepBtns, startGap(required, values)); checksEl.replaceChildren(...checkStep(step, values).map((c) => h("li", { class: c.ok ? "ok" : "no" }, (c.ok ? "OK  " : "Not yet  ") + c.text))); };
    const body = h("div", { class: "t-step-body" },
      h("p", { class: "t-what" }, step.what),
      h("ul", { class: "t-links" }, step.links.map((l) => h("li", {}, h("span", { class: "t-ty t-" + l.type }, { video: "Watch", docs: "Read", course: "Course", book: "Book" }[l.type] || l.type),
        h("a", { href: l.url, target: "_blank", rel: "noopener", onclick: () => recordOpen(step, l), onauxclick: (e) => { if (e.button === 1) recordOpen(step, l); } }, l.title),
        h("span", { class: "t-src" }, l.source + (l.cost === "paid" ? " / paid" : "") + " / " + (l.optional ? "optional, go further" : l.mins ? fmtMin(l.mins) : "self-paced"))))),
      h("p", { class: "t-do" }, h("b", {}, "What to do: "), step.task),
      h("p", { class: "t-donewhen" }, h("b", {}, "Done when: "), step.done),
      h("p", { class: "t-full" }, h("a", { href: step.page, target: "_blank", rel: "noopener" }, "Full lesson"),
        step.crash && step.crash[0] ? [" / ", h("a", { href: "crash-course.html#" + step.crash[0], target: "_blank", rel: "noopener" }, "Go further: " + step.crash[1] + " in the crash course")] : null));
    if (S.repo) {
      const work = stepWork(step);
      body.append(h("div", { class: "t-work" }, h("p", {}, h("b", {}, "Project work in this step: "),
        work.length ? `${work.length} commit${work.length > 1 ? "s" : ""} under projects/` : "no commits under projects/ yet. Build and commit your work there."),
        work.length ? h("ul", {}, work.slice(0, 5).map((c) => h("li", {}, h("a", { href: safeUrl(c.url), target: "_blank", rel: "noopener" }, c.sha), " ", c.msg, " ", h("small", {}, c.at.slice(0, 10))))) : null));
    }
    if (S.viewOnly) {
      if (f && f.time) body.append(h("p", { class: "t-time" + (f.time.met ? " ok" : "") }, f.time.met ? `Time met: ${fmtMin(f.time.elapsed)} since first open, ${fmtMin(f.time.required)} needed.` : `Saved ${fmtMin(f.time.elapsed)} after first open, ${fmtMin(f.time.required)} needed; learner confirmed they went through everything.`));
      if (f) body.append(h("dl", { class: "t-sum" }, step.fields.map((fd) => {
        const v = String((f.fields || {})[fd.id] || "");
        if (!v) return null;
        return [h("dt", {}, fd.label), h("dd", {}, fd.kind === "url" && safeUrl(v) ? h("a", { href: v, target: "_blank", rel: "noopener" }, v) : v)];
      })), feedback);
    } else {
      const form = h("div", { class: "t-form" });
      for (const fd of step.fields) {
        const input = fd.kind === "long" ? h("textarea", { rows: 4 }) : h("input", { type: fd.kind === "url" ? "url" : "text" });
        input.value = values[fd.id] || "";
        input.addEventListener("input", () => { values[fd.id] = input.value; store.set("fde-draft-" + step.slug, values); paint(); });
        form.append(h("label", { class: "t-field" }, h("span", {}, fd.label + (fd.min_words ? ` (at least ${fd.min_words} words)` : "")), input));
      }
      stepBtns.push(h("button", { class: "open", onclick: (e) => allowed(e) && busy(e.currentTarget, "Saving to GitHub...", () => saveStep(step, values, feedback)) }, "Save evidence to GitHub"),
        h("button", { class: "ghost", onclick: (e) => allowed(e) && reviewStep(step, values, feedback) }, "Ask the tutor"));
      body.append(form, h("p", { class: "eyebrow" }, "Checks"), checksEl, h("div", { class: "t-row" }, ...stepBtns), feedback);
    }
    paint();
    box.append(h("details", { class: "t-step2", id: "step-" + step.slug },
      h("summary", {}, h("span", { class: "t-num" }, step.num), h("span", { class: "t-st-title" }, h("b", {}, step.title), h("small", {}, step.when, h("span", { class: "t-st-time" }, stepTimeLabel(step)))), h("span", { class: "t-pill " + status[1] }, status[0] + (f ? ` / ${stepPoints(step)} pts` : ""))), body));
  }
}

async function saveStep(step, values, feedback) {
  if (!S.user || !S.repo) return toast("Sign in and connect your journal repository first", true);
  const checks = checkStep(step, values);
  const pass = checks.every((c) => c.ok);
  const t = stepTime(step);
  if (t.total && !t.met) {
    const why = !t.first ? "You have not opened any of this step's resources from this page yet."
      : t.unopened.length ? `You have not opened: ${t.unopened.map((l) => l.title).join(", ")}.`
      : `You first opened them ${fmtMin(t.elapsed)} ago; going through them fully takes about ${fmtMin(t.required)} including a 30% buffer.`;
    if (!window.confirm(why + "\n\nDid you fully go through all the resources for this step? Your answer is saved with the step.")) return;
  }
  const time = { total: t.total, required: t.required, elapsed: t.elapsed, met: t.met, confirmed_early: Boolean(t.total && !t.met),
    opened: t.opened.map((l) => ({ title: l.title, mins: l.mins || null, first: opens()[l.url].first })) };
  const rec = { time, slug: step.slug, step: step.num, title: step.title, fields: values, checks: { pass, failed: checks.filter((c) => !c.ok).map((c) => c.text) }, tutor: feedback.textContent || "", saved: today(), savedAt: new Date().toISOString() };
  const md = [`# Step ${step.num}: ${step.title}`, "", `Project: ${(S.profile.project || {}).title || "-"}  `, `Status: ${pass ? "checks passed" : "checks not passed yet"}  `, `Saved: ${rec.saved}`, "",
    ...step.fields.flatMap((fd) => (values[fd.id] ? [`## ${fd.label}`, String(values[fd.id]), ""] : [])),
    ...(rec.tutor ? ["## Tutor feedback", rec.tutor, ""] : []),
    "## Time on resources", time.total ? `Needed: ${time.required} min (${time.total} min of resources plus 30%). Since first open: ${time.elapsed} min. ${time.met ? "Time met." : "Saved early; learner confirmed they went through everything."}` : "Self-paced step.",
    ...time.opened.map((o) => `- ${o.title}: ${o.mins ? o.mins + " min" : "self-paced"}, first opened ${o.first.replace("T", " ").slice(0, 16)} UTC`), "",
    embedData(rec)].join("\n");
  try {
    await writeFile(`${DIR}/steps/${step.num.toLowerCase()}-${step.slug}.md`, md, `Step ${step.num}: ${step.title} (${pass ? "done" : "draft"})`);
    S.files[step.slug] = rec;
    await writeProgress();
    await flushLog();
    toast(pass ? "Saved. Step done." : "Saved as a draft. Some checks are not passing yet.", !pass);
    renderSummary(); renderSteps(); renderBadges();
    const el = document.getElementById("step-" + step.slug); if (el) el.open = true;
  } catch (e) { toast(e.message, true); }
}

// ---------- tutor ----------
// Suggestions come from /api/review (Workers AI on the site's account); the rule checks decide the verdict.
const MODEL_NOTE = "\n\n(Suggestions come from an AI model. They can be wrong; the checks above decide whether the step is done.)";

async function askTutor(kind, text) {
  const r = await fetch("/api/review", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ kind, text }) });
  const d = await r.json().catch(() => ({}));
  if (r.ok && d.answer) return d.answer;
  if (d.error === "limit") throw new Error("today's AI allowance is used up. The checks still work; try again tomorrow");
  if (d.error === "too_short") throw new Error("write a little more first");
  throw new Error("the AI service is not available right now");
}

async function reviewStep(step, values, out) {
  const checks = checkStep(step, values);
  const missing = checks.filter((c) => !c.ok).map((c) => "- " + c.text);
  const verdict = missing.length ? "Verdict: NOT YET. Fix these first:\n" + missing.join("\n") : "Verdict: READY. All checks pass.";
  out.textContent = verdict + "\n\nGetting suggestions...";
  const p = projectDraft();
  const ev = step.fields.map((f) => `${f.label}:\n${values[f.id] || "(empty)"}`).join("\n\n");
  try {
    const reply = await askTutor("step", `Project: ${p.title || "-"} - ${p.problem || ""}\nStep: ${step.title}\nTask: ${step.task}\nDone when: ${step.done}\n\nEvidence:\n${ev}`);
    out.textContent = verdict + "\n\nSuggestions:\n" + reply + MODEL_NOTE;
  } catch (e) { out.textContent = verdict + "\n\nNo suggestions: " + e.message + "."; }
}

async function reviewIdea(p, out) {
  const gaps = [];
  if (words(p.problem) < 15) gaps.push("- Describe the problem in more detail: who, what, how often");
  if (!/\d/.test(p.measure || "") && words(p.measure) < 8) gaps.push("- Make the success measure countable (a rate, a time, a count)");
  if (words(p.data) < 6) gaps.push("- Say what data you will use and where it comes from");
  if (!/approv|review|check|sign/i.test(p.users || "")) gaps.push("- Name who approves the output before it is final");
  const verdict = gaps.length ? "Before you start, tighten these:\n" + gaps.join("\n") : "The idea covers the basics: problem, users and approver, data and a measure.";
  out.textContent = verdict + "\n\nGetting suggestions...";
  try {
    const reply = await askTutor("idea", ["title", "problem", "users", "data", "measure"].map((k) => `${k}: ${p[k] || "(empty)"}`).join("\n"));
    out.textContent = verdict + "\n\nSuggestions:\n" + reply + MODEL_NOTE;
  } catch (e) { out.textContent = verdict + "\n\nNo suggestions: " + e.message + "."; }
}

// ---------- GitHub status badges on each section heading ----------
function badge(id, text, kind) {
  const el = document.getElementById(id);
  if (!el) return;
  el.textContent = text;
  el.className = "t-badge " + (kind || "");
}
function renderBadges() {
  const tracked = Boolean(S.repo && (S.user || S.viewOnly));
  if (S.viewOnly) badge("badge-connect", `Viewing ${S.owner}/${S.repo} in GitHub`, "ok");
  else badge("badge-connect", tracked ? `Tracked in GitHub: ${S.owner}/${S.repo}` : "Not tracked in GitHub", tracked ? "ok" : "warn");
  const saved = (x) => (!tracked ? ["Not tracked", "warn"] : x ? ["Saved in GitHub", "ok"] : ["Not saved yet", ""]);
  badge("badge-project", ...saved(S.profile.project && S.profile.project.title));
  badge("badge-decide", ...saved(S.profile.setup && S.profile.setup.why));
  const n = S.data.steps.filter((st) => S.files[st.slug]).length;
  badge("badge-path", tracked ? `${n} of ${S.data.steps.length} saved in GitHub` : "Not tracked", tracked ? (n ? "ok" : "") : "warn");
}

// ---------- boot ----------
function renderAll() { renderGh(); renderProject(); renderDecide(); renderSummary(); renderSteps(); renderBadges(); syncQuizzes(); }

async function boot() {
  const gb = $("#gh-box");
  if (gb) gb.replaceChildren(h("p", { class: "t-loading" }, h("span", { class: "t-spin", "aria-hidden": "true" }), "Checking your GitHub sign-in..."));
  S.data = await (await fetch("tutor-data.json", { cache: "no-cache" })).json();
  const hash = new URLSearchParams(location.hash.slice(1));
  if (hash.get("gh")) { ses.set("fde-gh", hash.get("gh")); history.replaceState(null, "", location.pathname + location.search); }
  if (hash.get("cf") === "connected") { toast("Cloudflare connected"); history.replaceState(null, "", location.pathname + location.search); }
  if (hash.get("cf_error")) { toast("Cloudflare connection did not complete: " + hash.get("cf_error"), true); history.replaceState(null, "", location.pathname + location.search); }
  if (hash.get("gh_error")) { toast("GitHub sign-in did not complete: " + hash.get("gh_error"), true); history.replaceState(null, "", location.pathname + location.search); }
  const view = new URLSearchParams(location.search).get("view");
  try { S.configured = (await (await fetch("/api/gh/status", { cache: "no-store" })).json()).configured; } catch (e) { S.configured = false; }
  if (view && /^[\w.-]+\/[\w.-]+$/.test(view)) {
    S.viewOnly = true; [S.owner, S.repo] = view.split("/");
    try { await loadRepoState(); } catch (e) { toast(e.message, true); }
  } else {
    S.token = ses.get("fde-gh");
    if (S.token && gb) gb.replaceChildren(h("p", { class: "t-loading" }, h("span", { class: "t-spin", "aria-hidden": "true" }), "Loading your journal from GitHub..."));
    if (S.token) {
      try {
        S.user = await gh("/user");
        const name = store.get("fde-repo", "");
        if (S.user && name && (await gh(`/repos/${S.user.login}/${name}`))) { S.owner = S.user.login; S.repo = name; await loadRepoState(); }
      } catch (e) { toast(e.message, true); S.token = ""; ses.set("fde-gh", ""); S.user = null; }
    }
  }
  renderAll();
}
boot();
