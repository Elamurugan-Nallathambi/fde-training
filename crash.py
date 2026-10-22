"""Crash course library: public/crash-course.html from content/library/*.csv, ordered must do, recommended, go deeper."""
import csv
import json
import re
from html import escape
from pathlib import Path

from site_nav import topbar

ROOT = Path(__file__).resolve().parent
LIB = ROOT / "content" / "library"
OUT = ROOT / "public" / "crash-course.html"

# Learning order and short ids used in links from other pages (crash-course.html#programming).
AREAS = [
 ("Systems and networking", "systems", "How computers, operating systems and the internet work: the ground every system stands on."),
 ("Programming", "programming", "Python, clean object-oriented code, tests and Git: enough to build and read real tools."),
 ("Databases and data", "data", "SQL, data modelling, pipelines and vector search: where client data lives and how to use it."),
 ("Cloud and DevOps", "cloud", "Cloud, containers, CI/CD, APIs, events and system design: how solutions connect and run."),
 ("Security and privacy", "security", "Access, encryption, OWASP, prompt injection and privacy law: how to keep client data and systems safe."),
 ("AI, ML and LLMs", "ai", "From neural networks to agents, RAG and evals, including the papers that started it."),
 ("FDE role and business skills", "business", "Discovery, requirements, consulting, product, writing and change: how to turn work into adopted solutions."),
]
TIERS = [("must", "Must do", "Start here. The shortest clear explanation of each topic."),
         ("rec", "Recommended", "Once the must-dos are done: more depth and practice."),
         ("deep", "Go deeper", "Papers, books, advanced material and long courses, when a project needs it.")]
TYPE_LABEL = {"video": "Watch", "article": "Read", "docs": "Docs", "course": "Course", "book": "Book", "paper": "Paper", "interactive": "Practice"}


def minutes(length):
    s = (length or "").lower()
    m = re.match(r"^\s*(\d+):(\d{2}):(\d{2})\b", s)
    if m:
        return int(m.group(1)) * 60 + int(m.group(2))
    m = re.match(r"^\s*(\d+):(\d{2})\b", s)
    if m:
        return int(m.group(1)) + (1 if int(m.group(2)) >= 30 else 0)
    h = re.search(r"(\d+(?:\.\d+)?)\s*(?:h\b|hours?|hrs?)", s)
    mi = re.search(r"(\d+)\s*min", s)
    if h or mi:
        return int(round(float(h.group(1)) * 60 if h else 0)) + (int(mi.group(1)) if mi else 0)
    return None


def nice(mins):
    if mins is None:
        return ""
    return f"{mins // 60} h {mins % 60} min" if mins >= 60 and mins % 60 else (f"{mins // 60} h" if mins >= 60 else f"{mins} min")


def tiers_for(items):
    """Must do: per topic, the first beginner item of an hour or less; topics left without one take their first short intermediate item."""
    musts = set()
    for r in items:
        t, lvl, mins = r["type"], r["level"], r["mins"]
        if t in ("paper", "book") or lvl == "advanced" or (mins is not None and mins > 240 and lvl != "beginner"):
            r["tier"] = "deep"
        elif lvl == "beginner" and r["topic"] not in musts and mins is not None and mins <= 60:
            r["tier"] = "must"; musts.add(r["topic"])
        else:
            r["tier"] = "rec"
    for r in items:
        if r["topic"] not in musts and r["tier"] == "rec" and r["mins"] is not None and r["mins"] <= 60:
            r["tier"] = "must"; musts.add(r["topic"])


def load():
    rows, seen = [], set()
    for f in sorted(LIB.glob("*.csv")):
        with f.open(newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                r = {k: (v or "").strip() for k, v in r.items()}
                key = r["url"].rstrip("/").lower()
                if not key or key in seen:
                    continue
                seen.add(key)
                if r["cost"].startswith("free") and r["cost"] != "free":
                    r["cost"] = "free"
                r["mins"] = minutes(r["length"])
                rows.append(r)
    by_area = {a: [] for a, _, _ in AREAS}
    for r in rows:
        by_area.setdefault(r["area"], []).append(r)
    for items in by_area.values():
        tiers_for(items)
    return by_area


def card(r):
    length = nice(r["mins"]) if r["mins"] is not None else ("" if r["length"] in ("not stated", "self-paced") else r["length"])
    meta = " / ".join(x for x in [r["source"], length, "paid" if r["cost"] == "paid" else ""] if x)
    return (f'<li class="cc-item" data-type="{escape(r["type"])}" data-cost="{escape(r["cost"])}" data-text="{escape((r["title"] + " " + r["source"] + " " + r["topic"] + " " + r["why"]).lower())}">'
            f'<span class="cc-ty cc-{escape(r["type"])}">{TYPE_LABEL.get(r["type"], r["type"])}</span>'
            f'<div><a href="{escape(r["url"])}" target="_blank" rel="noopener">{escape(r["title"])}</a>'
            f'<p class="cc-meta">{escape(meta)}</p><p class="cc-why">{escape(r["why"])}</p></div></li>')


def page():
    by_area = load()
    total = sum(len(v) for v in by_area.values())
    toc, sections = [], []
    for i, (name, aid, blurb) in enumerate(AREAS, 1):
        items = by_area.get(name, [])
        must = [r for r in items if r["tier"] == "must"]
        must_min = sum(r["mins"] or 0 for r in must)
        toc.append(f'<li><a href="#{aid}"><span>{i:02d}</span>{escape(name)}<small>{len(must)} must do / {len(items)} total</small></a></li>')
        tiers = []
        for tid, tname, tdesc in TIERS:
            group = [r for r in items if r["tier"] == tid]
            if not group:
                continue
            mins = sum(r["mins"] or 0 for r in group)
            tiers.append(f'<section class="cc-tier cc-{tid}" data-tier="{tid}"><header><h3>{tname}</h3><p>{tdesc} {len(group)} items'
                         f'{", about " + nice(mins) + " of timed material" if mins else ""}.</p></header><ul class="cc-list">{"".join(card(r) for r in group)}</ul></section>')
        sections.append(f'''<section class="cc-area" id="{aid}" data-area>
  <header class="cc-head"><p class="eyebrow">Area {i:02d} / {len(items)} resources / must do about {nice(must_min) or "self-paced"}</p><h2>{escape(name)}</h2><p class="ls-sum">{escape(blurb)}</p></header>
  {"".join(tiers)}
</section>''')
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>FDE Crash Course Library</title>
<meta name="description" content="{total} hand-checked articles, videos, courses, books and papers for forward deployed engineers, ordered from must do to go deeper.">
<script src="theme.js"></script>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Familjen+Grotesk:wght@500;600;700&family=Atkinson+Hyperlegible:wght@400;700&family=IBM+Plex+Mono:wght@500&display=swap">
<link rel="stylesheet" href="style.css"></head>
<body class="crash">
{topbar("", (("Crash course library", None),), "crash", "crash")}
<main class="t-main">
  <header class="t-head">
    <p class="kicker">FDE training program / crash course library</p>
    <h1>The crash course: the best material, in the order to take it.</h1>
    <p class="lede">{total} articles, videos, courses, books and papers across seven areas, every link checked. In each area, do the <b>Must do</b> items first; they are short and cover each topic once. Come back to <b>Recommended</b> and <b>Go deeper</b> when a lesson or project needs more.</p>
    <ol class="cc-toc">{"".join(toc)}</ol>
    <div class="cc-filter">
      <input type="search" id="ccq" placeholder="Search: DNS, OAuth, RAG, pandas, discovery..." aria-label="Search the library">
      <div class="rfilter" role="group" aria-label="Show tiers"><span>Show:</span><button data-tier-btn="all" aria-pressed="true">All tiers</button><button data-tier-btn="must" aria-pressed="false">Must do only</button></div>
      <div class="rfilter" role="group" aria-label="Type"><span>Type:</span><button data-type-btn="all" aria-pressed="true">All</button><button data-type-btn="video" aria-pressed="false">Videos</button><button data-type-btn="article" aria-pressed="false">Articles</button><button data-type-btn="course" aria-pressed="false">Courses</button><button data-type-btn="interactive" aria-pressed="false">Practice</button><button data-type-btn="paper" aria-pressed="false">Papers</button><button data-type-btn="book" aria-pressed="false">Books</button></div>
      <label class="cc-free"><input type="checkbox" id="ccfree"> Hide paid</label>
      <p id="cccount" class="t-note" aria-live="polite"></p>
    </div>
    <p class="t-note">Part of the program: <a href="index.html">Program overview</a> / <a href="learn/basics.html">The basics</a> / <a href="tldr.html">Learning path</a>. Lengths: video lengths are exact; reading times are estimates.</p>
  </header>
  {"".join(sections)}
</main>
<script>
(function () {{
  var st = {{ q: "", tier: "all", type: "all", free: false }};
  var items = Array.prototype.slice.call(document.querySelectorAll(".cc-item"));
  function apply() {{
    var shown = 0;
    items.forEach(function (li) {{
      var tierEl = li.closest("[data-tier]");
      var ok = (!st.q || li.dataset.text.indexOf(st.q) >= 0) && (st.type === "all" || li.dataset.type === st.type) &&
        (!st.free || li.dataset.cost === "free") && (st.tier === "all" || tierEl.dataset.tier === st.tier);
      li.dataset.hide = ok ? "" : "1"; if (ok) shown++;
    }});
    document.querySelectorAll("[data-tier]").forEach(function (t) {{ t.dataset.hide = t.querySelector('.cc-item:not([data-hide="1"])') ? "" : "1"; }});
    document.querySelectorAll("[data-area]").forEach(function (a) {{ a.dataset.hide = a.querySelector('.cc-item:not([data-hide="1"])') ? "" : "1"; }});
    document.getElementById("cccount").textContent = shown + " of " + items.length + " shown";
  }}
  function group(attr, key) {{
    var btns = Array.prototype.slice.call(document.querySelectorAll("[" + attr + "]"));
    btns.forEach(function (b) {{ b.addEventListener("click", function () {{
      st[key] = b.getAttribute(attr); btns.forEach(function (x) {{ x.setAttribute("aria-pressed", x === b ? "true" : "false"); }}); apply(); }}); }});
  }}
  group("data-tier-btn", "tier"); group("data-type-btn", "type");
  document.getElementById("ccq").addEventListener("input", function (e) {{ st.q = e.target.value.trim().toLowerCase(); apply(); }});
  document.getElementById("ccfree").addEventListener("change", function (e) {{ st.free = e.target.checked; apply(); }});
  apply();
}})();
</script>
</body></html>
'''


def build():
    OUT.write_text(page(), encoding="ascii")
    return OUT


def stats():
    by_area = load()
    for name, aid, _ in AREAS:
        items = by_area.get(name, [])
        c = {t: sum(1 for r in items if r["tier"] == t) for t, _, _ in TIERS}
        print(f'{aid:12} total {len(items):3}  must {c["must"]:3}  rec {c["rec"]:3}  deep {c["deep"]:3}  must-minutes {sum(r["mins"] or 0 for r in items if r["tier"] == "must")}')


def urls():
    return sorted({r["url"] for items in load().values() for r in items})


if __name__ == "__main__":
    stats()
    print(build())
