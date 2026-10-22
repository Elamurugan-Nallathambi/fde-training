"""Training material pages: renders content/mNN.json into public/learn/mNN.html (see content/SCHEMA.md)."""
import json
import re
from html import escape
from pathlib import Path

from site_nav import topbar

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
OUT = ROOT / "public" / "learn"

TYPE_LABEL = {"video": "Video", "course": "Course", "docs": "Docs", "book": "Book", "cert": "Certificate"}
TYPE_ORDER = ["docs", "video", "course", "book", "cert"]
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Familjen+Grotesk:wght@500;600;700&family=Atkinson+Hyperlegible:wght@400;700&family=IBM+Plex+Mono:wght@500&display=swap">')

# Syntax highlighting and copy buttons for code blocks (highlight.js, pinned version, from cdnjs).
HLJS = ('<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js" defer></script>'
        '<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/dockerfile.min.js" defer></script>')


def t(s):
    """Escape plain text and turn `code` spans into <code>."""
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", escape(str(s), quote=False))


def load_modules():
    mods = []
    for f in sorted(CONTENT.glob("m[0-9][0-9].json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        d["file"] = f.stem
        mods.append(d)
    return sorted(mods, key=lambda m: m["module"])


# ---------- diagrams ----------
def steps_ol(steps, cls):
    lis = "".join(f'<li><b>{t(s["label"])}</b>{f"<span>{t(s.get("note"))}</span>" if s.get("note") else ""}</li>' for s in steps)
    return f'<ol class="{cls}" style="--n:{len(steps)}">{lis}</ol>'


def diagram_html(d):
    kind = d.get("type")
    if kind == "flow":
        body = steps_ol(d["steps"], "dg-flow")
    elif kind == "cycle":
        body = steps_ol(d["steps"], "dg-flow dg-cycle") + f'<p class="dg-return">Then back to step 1: {t(d["steps"][0]["label"])}</p>'
    elif kind == "layers":
        body = '<ol class="dg-layers">' + "".join(
            f'<li><b>{t(x["label"])}</b>{f"<span>{t(x.get("note"))}</span>" if x.get("note") else ""}</li>' for x in d["layers"]) + "</ol>"
    elif kind == "swimlane":
        lanes, steps = d["lanes"], d["steps"]
        cells = "".join(f'<div class="sl-lane" style="grid-row:{i + 2}">{t(l)}</div>' for i, l in enumerate(lanes))
        cells += "".join(f'<div class="sl-num" style="grid-column:{j + 2}">{j + 1}</div>' for j in range(len(steps)))
        cells += "".join(f'<div class="sl-band" style="grid-row:{i + 2}"></div>' for i in range(len(lanes)))
        cells += "".join(f'<div class="sl-step" style="grid-row:{int(s["lane"]) + 2};grid-column:{j + 2}">{t(s["label"])}</div>' for j, s in enumerate(steps))
        body = (f'<div class="sl-wrap"><div class="sl" style="--cols:{len(steps)};--rows:{len(lanes)}" role="img" '
                f'aria-label="{escape(d.get("title", "Swimlane"))}">{cells}</div></div>'
                '<ol class="sr-only">' + "".join(f'<li>{t(lanes[int(s["lane"])])}: {t(s["label"])}</li>' for s in steps) + "</ol>")
    elif kind == "compare":
        body = '<div class="dg-compare">' + "".join(
            f'<div><h5>{t(c["title"])}</h5><ul>{"".join(f"<li>{t(i)}</li>" for i in c["items"])}</ul></div>' for c in d["columns"]) + "</div>"
    elif kind == "branch":
        start = f'<div class="br-start">{t(d["start"])}</div>' if d.get("start") else ""
        brs = "".join(f'<div class="br-arm"><span class="br-ans">{t(b["answer"])}</span><p>{t(b["result"])}</p></div>' for b in d["branches"])
        body = f'<div class="dg-branch">{start}<div class="br-q">{t(d["question"])}</div><div class="br-arms" style="--n:{len(d["branches"])}">{brs}</div></div>'
    else:
        return ""
    hint = " On smaller screens, scroll sideways to see every step." if kind == "swimlane" and len(d.get("steps", [])) > 7 else ""
    cap = f'<figcaption>{t(d["caption"])}{hint}</figcaption>' if d.get("caption") else ""
    return f'<figure class="diagram kind-{kind}"><p class="dg-title">{t(d.get("title", ""))}</p>{body}{cap}</figure>'


# ---------- lesson parts ----------
def block(b, h="h3"):
    out = f'<{h}>{t(b["h"])}</{h}>' if b.get("h") else ""
    out += "".join(f"<p>{t(p)}</p>" for p in b.get("p", []))
    if b.get("list"):
        out += "<ul>" + "".join(f"<li>{t(i)}</li>" for i in b["list"]) + "</ul>"
    if b.get("code"):
        c = b["code"]
        lang = c.get("lang", "text")
        hl = {"text": "plaintext", "csv": "plaintext"}.get(lang, lang)
        out += f'<div class="code"><span class="code-lang">{escape(lang)}</span><pre><code class="language-{escape(hl)}">{escape(c["text"])}</code></pre></div>'
    return out


def links_html(links):
    by = {}
    for l in links:
        by.setdefault(l["type"], []).append(l)
    out = []
    for ty in TYPE_ORDER + [k for k in by if k not in TYPE_ORDER]:
        for l in by.get(ty, []):
            cost = l.get("cost", "free")
            out.append(f'<li class="fl fl-{escape(ty)}"><span class="fl-type">{TYPE_LABEL.get(ty, ty.title())}</span>'
                       f'<a href="{escape(l["url"])}" target="_blank" rel="noopener">{t(l["title"])}</a>'
                       f'<span class="fl-src">{t(l.get("source", ""))}{"<span class=\"cost c-paid\">Paid</span>" if cost == "paid" else ""}</span></li>')
    return "<ul>" + "".join(out) + "</ul>"


def practice_html(m, lesson):
    out = []
    for i, p in enumerate(lesson.get("practice", []), 1):
        key = f'{m["file"]}-{lesson["id"]}-{i}'
        steps = "".join(f"<li>{t(s)}</li>" for s in p["steps"])
        out.append(f'''<div class="ex">
  <div class="ex-head"><span class="ex-tag">Practice {i}</span><h4>{t(p["title"])}</h4><span class="ex-time">{t(p.get("time", ""))}</span></div>
  <p class="ex-goal"><b>Goal:</b> {t(p["goal"])}</p>
  <ol class="ex-steps">{steps}</ol>
  <div class="ex-done"><p><b>Done when:</b> {t(p["done_when"])}</p><label><input type="checkbox" data-done="{key}"> I did this</label></div>
</div>''')
    return "".join(out)


def lesson_html(m, n, lesson):
    lid = f'l-{lesson["id"]}'
    sections = "".join(f'<section class="ls-sec">{block(s)}</section>' for s in lesson["sections"])
    ex = lesson["example"]
    example = f'<section class="worked"><p class="eyebrow">Worked example</p>{block({"h": ex.get("title"), "p": ex.get("p", []), "list": ex.get("list"), "code": ex.get("code")})}</section>'
    fd = lesson.get("field")
    if fd:
        example += f'<section class="worked field"><p class="eyebrow">Experience sharing</p>{block({"h": fd.get("title"), "p": fd.get("p", []), "list": fd.get("list")})}</section>'
    pit = "".join(f"<li>{t(x)}</li>" for x in lesson.get("pitfalls", []))
    chk = "".join(f"<li>{t(x)}</li>" for x in lesson.get("check", []))
    return f'''<article class="lesson" id="{lid}">
  <div class="ls-main">
    <header class="ls-head"><p class="eyebrow">Lesson {m["module"]}.{n}</p><h2>{t(lesson["title"])}</h2><p class="ls-sum">{t(lesson["summary"])}</p></header>
    <div class="why"><p class="eyebrow">Why this matters on a client engagement</p><p>{t(lesson["why"])}</p></div>
    {diagram_html(lesson["diagram"]) if lesson.get("diagram") else ""}
    <div class="prose">{sections}</div>
    {example}
    <section class="practice"><h3>Start practicing</h3>{practice_html(m, lesson)}</section>
    <div class="pc"><section class="pitfalls"><h3>Common mistakes</h3><ul>{pit}</ul></section>
    <section class="checkq"><h3>Check yourself</h3><ol>{chk}</ol></section></div>
  </div>
  <aside class="more" aria-label="Find more on {escape(lesson["title"])}"><div class="more-in"><p class="more-h">Find more here</p>{links_html(lesson.get("links", []))}</div></aside>
</article>'''


def nav_html(mods, cur):
    def item(href, num, title, here, sub="", units=""):
        cls = ' class="here"' if here else ""
        cur_attr = " aria-current=page" if here else ""
        unit_attr = f' data-units="{units}"' if units else ""
        return f'<li{cls}><a href="{href}"{cur_attr}{unit_attr}><span class="ln-n">{num}</span>{title}</a>{sub}</li>'

    def lessons(m):
        return '<ol class="ln-lessons">' + "".join(
            f'<li><a href="#l-{l["id"]}" data-lesson="{m["file"]}-{l["id"]}">{t(l["title"])}</a></li>' for l in m["lessons"]) + "</ol>"

    start = [item("basics.html", "A", "The basics: what is what", cur.get("file") == "basics", "", "basics")]
    items = []
    for m in mods:
        here = m["file"] == cur.get("file")
        sub = lessons(m) if here else ""
        if m["module"] == 0:
            start.append(item(f'{m["file"]}.html', "B", t(m["title"]), here, sub, "setup m00"))
            if (CONTENT / "languages.json").exists():
                start.append(item("languages.html", "L", "Languages, AI SDKs and learning playlists", cur.get("file") == "languages"))
        else:
            items.append(item(f'{m["file"]}.html', f'{m["module"]:02d}', t(m["title"]), here, sub, m["file"]))
    practice = item("../tldr.html", "P", "Your learning path: one real project, 13 steps", False)
    crash = item("../crash-course.html", "C", "Crash course library: go deeper on any topic", False)
    return (f'<nav class="lnav" aria-label="Program"><div class="ln-progress" data-progress></div>'
            f'<p class="ln-h"><span>1</span>Start here</p><ol class="ln-mods">{"".join(start)}</ol>'
            f'<p class="ln-h"><span>2</span>Modules</p><ol class="ln-mods">{"".join(items)}</ol>'
            f'<p class="ln-h"><span>3</span>Practice</p><ol class="ln-mods">{practice}</ol>'
            f'<p class="ln-h"><span>4</span>Crash course</p><ol class="ln-mods">{crash}</ol></nav>')


def test_html(m):
    if not (CONTENT / "quiz" / f'{m["file"]}.json').exists():
        return ""
    setup = ""
    if m["module"] == 0:
        setup = ('<section class="mtest syscheck" id="system-check"><p class="eyebrow">Machine setup check</p>'
                 '<h2>Prove your machine is ready</h2><div class="mt-body"></div></section>')
    return setup + (f'<section class="mtest" id="module-test" data-module="{m["file"]}" data-root="../"><p class="eyebrow">Module test</p>'
            f'<h2>Check you are ready to move on</h2><div class="mt-body"></div></section>')


def quick_html():
    if not (CONTENT / "quiz" / "basics.json").exists():
        return ""
    return ('<section class="mtest" id="module-test" data-module="basics" data-root="../" data-count="10" data-quick="1">'
            '<p class="eyebrow">Quick check</p><h2>Check the basics before module 01</h2><div class="mt-body"></div></section>')


def page_html(mods, i):
    m = mods[i]
    prev_m = mods[i - 1] if i > 0 else None
    next_m = mods[i + 1] if i + 1 < len(mods) else None
    lessons = "".join(lesson_html(m, n, l) for n, l in enumerate(m["lessons"], 1))
    toc = "".join(f'<li><a href="#l-{l["id"]}"><span>{m["module"]}.{n}</span>{t(l["title"])}</a></li>' for n, l in enumerate(m["lessons"], 1))
    nexts = ""
    if prev_m:
        nexts += f'<a class="pn" href="{prev_m["file"]}.html"><span>Previous module</span>{prev_m["module"]:02d} {t(prev_m["title"])}</a>'
    if next_m:
        nexts += f'<a class="pn pn-next" href="{next_m["file"]}.html"><span>Next module</span>{next_m["module"]:02d} {t(next_m["title"])}</a>'
    nlinks = sum(len(l.get("links", [])) for l in m["lessons"])
    nprac = sum(len(l.get("practice", [])) for l in m["lessons"])
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Module {m["module"]}: {escape(m["title"])}</title>
<meta name="description" content="{escape(m["intro"])}">
<script src="../theme.js"></script>
{FONTS}
<link rel="stylesheet" href="../style.css"></head>
<body class="learn">
<a class="skip" href="#main">Skip to content</a>
{topbar("../", (("Start here", "learn/basics.html"), ("Set up your machine", None)) if m["module"] == 0 else (("Modules", "learn/m01.html"), (f"Module {m['module']:02d}", None)), "start" if m["module"] == 0 else "modules", m["file"])}
<div class="lshell">
{nav_html(mods, m)}
<main id="main" class="lmain">
  <header class="mhead">
    <p class="kicker">{"Start here / before module 01" if m["module"] == 0 else f"Module {m['module']:02d} of 11"} / {len(m["lessons"])} lessons / {nprac} practice exercises / {nlinks} links</p>
    <h1>{t(m["title"])}</h1>
    <p class="lede">{t(m["intro"])}</p>
    <div class="howto"><p><b>New to a word?</b> Check <a href="basics.html">Start here: the basics</a> first. <b>How to use this module.</b> Read each lesson top to bottom: the diagram first, then the explanation and the worked example. Use "Find more here" to go deeper with docs, videos and courses. Then do the practice. Tick "I did this" to track your progress in this browser.</p></div>
    <ol class="mtoc">{toc}</ol>
  </header>
  {lessons}
  {test_html(m)}
  <nav class="pnav" aria-label="Other modules">{nexts}</nav>
</main>
</div>
<script src="learn.js" defer></script>
<script src="../progress.js" defer></script>
<script src="../quiz.js" defer></script>
{HLJS}<script src="../code.js" defer></script>
{'<script src="../syscheck.js" defer></script>' if m["module"] == 0 else ""}
</body></html>
'''


def term_html(g, x):
    tid = "t-" + re.sub(r"[^a-z0-9]+", "-", x["term"].lower()).strip("-")
    like = f'<p class="tm-like"><b>Think of it like:</b> {t(x["like"])}</p>' if x.get("like") else ""
    vs = f'<p class="tm-vs"><b>Not the same as:</b> {t(x["vs"])}</p>' if x.get("vs") else ""
    return (f'<article class="term" id="{tid}"><h3>{t(x["term"])}</h3><p class="tm-one">{t(x["one"])}</p>{like}'
            f'<p class="tm-why"><b>Why it matters:</b> {t(x["why"])}</p>{vs}</article>')


# Basics group to crash course area, for the "Go further" link.
CRASH_AREA = {"fits-together": ("ai", "AI, ML and LLMs"), "models": ("ai", "AI, ML and LLMs"), "products": ("ai", "AI, ML and LLMs"),
              "context": ("ai", "AI, ML and LLMs"), "open": ("ai", "AI, ML and LLMs"), "network": ("systems", "Systems and networking"),
              "data": ("security", "Security and privacy"), "build": ("programming", "Programming")}


def crash_link(gid):
    if gid not in CRASH_AREA:
        return ""
    aid, name = CRASH_AREA[gid]
    return f'<a class="cc-go" href="../crash-course.html#{aid}">Go further: {name} in the crash course</a>'


def basics_html(mods):
    b = json.loads((CONTENT / "basics.json").read_text(encoding="utf-8"))
    count = lambda g: f'{len(g["terms"])} terms' if g["terms"] else f'{len(g.get("diagrams", []))} pictures'
    chips = "".join(f'<li><a href="#g-{g["id"]}">{t(g["title"])} <span>{count(g)}</span></a></li>' for g in b["groups"])
    groups = []
    for g in b["groups"]:
        pts = ""
        if g.get("points"):
            pts = '<div class="points"><p class="eyebrow">Why be careful</p><ul>' + "".join(f"<li>{t(x)}</li>" for x in g["points"]) + "</ul></div>"
        dgs = "".join(diagram_html(d) for d in g.get("diagrams", []))
        terms = "".join(term_html(g, x) for x in g["terms"])
        wide = "" if g["terms"] else " wide"
        groups.append(f'''<section class="lesson bgroup{wide}" id="g-{g["id"]}" data-group>
  <div class="ls-main">
    <header class="ls-head"><p class="eyebrow">{count(g)}</p><h2>{t(g["title"])}</h2><p class="ls-sum">{t(g["intro"])}</p></header>
    {pts}{dgs}
    {f'<div class="terms">{terms}</div>' if terms else ""}
  </div>
  <aside class="more" aria-label="Find more on {escape(g["title"])}"><div class="more-in"><p class="more-h">Find more here</p>{links_html(g["links"])}{crash_link(g["id"])}</div></aside>
</section>''')
    nterms = sum(len(g["terms"]) for g in b["groups"])
    cur = {"file": "basics", "module": 0}
    first = mods[0] if mods else None
    nxt = f'<a class="pn pn-next" href="{first["file"]}.html"><span>Next</span>{first["module"]:02d} {t(first["title"])}</a>' if first else ""
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Start here: the basics</title>
<meta name="description" content="Plain-language definitions of AI, LLM, model, context, harness, API, open-weight models, networks, VPC, data privacy and security.">
<script src="../theme.js"></script>
{FONTS}
<link rel="stylesheet" href="../style.css"></head>
<body class="learn">
<a class="skip" href="#main">Skip to content</a>
{topbar("../", (("Start here", "learn/basics.html"), ("The basics", None)), "start", "basics")}
<div class="lshell">
{nav_html(mods, cur)}
<main id="main" class="lmain">
  <header class="mhead">
    <p class="kicker">Start here / {len(b["groups"])} groups / {nterms} terms / read in about 40 minutes</p>
    <h1>{t(b["title"])}</h1>
    <p class="lede">{t(b["intro"])}</p>
    <div class="finder"><label for="q">Find a term</label><input id="q" type="search" placeholder="Try: context, VPC, harness, open-weight" autocomplete="off"><p id="qcount" aria-live="polite"></p></div>
    <ul class="gchips">{chips}</ul>
  </header>
  {"".join(groups)}
  {quick_html()}
  <nav class="pnav" aria-label="Next">{nxt}</nav>
</main>
</div>
<script src="learn.js" defer></script>
<script src="../progress.js" defer></script>
<script src="../quiz.js" defer></script>
</body></html>
'''


LEARN_JS = r"""// Training material: practice ticks kept in this browser; nav shows lessons with all practice done.
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
"""


# ---------- languages, AI SDKs and playlists ----------
def playlist_html():
    pl = load_json(CONTENT / "languages-playlist.json")
    if not pl:
        return ""
    out = []
    for g in pl["groups"]:
        cards = []
        for it in g["items"]:
            levels = "".join(f'<div class="pl-level"><p class="pl-lv">{t(lv["level"])}</p>{links_html(lv["links"])}</div>' for lv in it["levels"])
            cards.append(f'<article class="pl-item" id="pl-{escape(it["id"])}"><h3>{t(it["name"])}</h3><p class="pl-why">{t(it["why"])}</p><div class="pl-levels">{levels}</div></article>')
        chips = "".join(f'<li><a href="#pl-{escape(it["id"])}">{t(it["name"])}</a></li>' for it in g["items"])
        out.append(f'<section class="playlist" id="g-{escape(g["id"])}"><h2>{t(g["title"])}</h2><p class="ls-sum">{t(g["intro"])}</p>'
                   f'<ul class="gchips">{chips}</ul><div class="pl-grid">{"".join(cards)}</div></section>')
    return "".join(out)


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def languages_html(mods):
    d = load_json(CONTENT / "languages.json")
    m = {"module": 0, "file": "languages"}
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{escape(d["title"])}</title>
<meta name="description" content="{escape(d["intro"])}">
<script src="../theme.js"></script>
{FONTS}
<link rel="stylesheet" href="../style.css"></head>
<body class="learn">
<a class="skip" href="#main">Skip to content</a>
{topbar("../", (("Start here", "learn/basics.html"), ("Languages and AI SDKs", None)), "start", "languages")}
<div class="lshell">
{nav_html(mods, m)}
<main id="main" class="lmain">
  <header class="mhead"><p class="kicker">Start here / your choice of language</p><h1>{t(d["title"])}</h1><p class="lede">{t(d["intro"])}</p></header>
  {lesson_html({"module": "L", "file": "languages"}, 1, d["lesson"]).replace("Lesson L.1", "Read first")}
  {playlist_html()}
</main>
</div>
<script src="learn.js" defer></script>
<script src="../progress.js" defer></script>
{HLJS}<script src="../code.js" defer></script>
</body></html>
'''


def build():
    mods = load_modules()
    OUT.mkdir(parents=True, exist_ok=True)
    for i, m in enumerate(mods):
        (OUT / f'{m["file"]}.html').write_text(page_html(mods, i), encoding="ascii")
    if (CONTENT / "basics.json").exists():
        (OUT / "basics.html").write_text(basics_html(mods), encoding="ascii")
    if (CONTENT / "languages.json").exists():
        (OUT / "languages.html").write_text(languages_html(mods), encoding="ascii")
    (OUT / "learn.js").write_text(LEARN_JS, encoding="ascii")
    qdir = ROOT / "public" / "quiz"
    qdir.mkdir(exist_ok=True)
    for f in list((CONTENT / "quiz").glob("m[0-9][0-9].json")) + list((CONTENT / "quiz").glob("basics.json")):
        (qdir / f.name).write_text(json.dumps(json.loads(f.read_text(encoding="utf-8")), ensure_ascii=True), encoding="ascii")
    if (CONTENT / "faq.json").exists():
        (ROOT / "public" / "faq.json").write_text(json.dumps(json.loads((CONTENT / "faq.json").read_text(encoding="utf-8")), ensure_ascii=True), encoding="ascii")
    return mods


if __name__ == "__main__":
    ms = build()
    print("lesson pages:", [m["file"] for m in ms])
