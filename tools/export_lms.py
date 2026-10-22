#!/usr/bin/env python3
"""Exports LMS topic packages: FDE General (generic and one per industry track in content/variants), FDE Advanced, and every content/topics file.
Lesson HTML is rendered with learn.py so the LMS shows the same lessons as the site. Usage: tools/export_lms.py [out_dir]"""

import json, os, sys, hashlib
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import learn, tldr  # noqa: E402
from learn import t, lesson_html, term_html, diagram_html, links_html, block  # noqa: E402

CONTENT = ROOT / "content"
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(os.environ.get("LMS_PACKAGES_DIR", ROOT / "lms-packages"))
# Extra topic folders (for example a private organisation's own courses), separated by ":".
EXTRA_TOPICS = [Path(d) for d in os.environ.get("LMS_EXTRA_TOPICS", "").split(":") if d]
VERSION = date.today().isoformat()
RULES = {"pass": 0.8, "attempts": 3, "wait_hours": 24, "ask": 20}
GENERAL = list(range(1, 11))


def load(path, default=None):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def module(n, variant=None):
    """Base module with the track overlay applied: full replacement, or lessons added before and after."""
    m = load(CONTENT / f"m{n:02d}.json")
    m["file"] = f"m{n:02d}"
    v = load(CONTENT / "variants" / variant / f"m{n:02d}.json") if variant else None
    if v and not v.get("overlay"):
        m.update({k: v[k] for k in ("title", "intro", "lessons") if k in v})
    elif v:
        m["lessons"] = v.get("add_first", []) + m["lessons"] + v.get("add", [])
        m["intro"] = v.get("intro", m["intro"])
    qs = load(CONTENT / "quiz" / f"m{n:02d}.json", {"questions": []})["questions"]
    vq = load(CONTENT / "variants" / variant / "quiz" / f"m{n:02d}.json") if variant else None
    if vq:
        qs = vq["questions"] if vq.get("replace") else qs + vq["questions"]
    ids = {l["id"] for l in m["lessons"]}
    return m, [q for q in qs if q.get("lesson") in ids]


def module_section(m, qs, ask=None):
    toc = "".join(f'<li><a href="#l-{l["id"]}"><span>{m["module"]}.{i}</span>{t(l["title"])}</a></li>' for i, l in enumerate(m["lessons"], 1))
    head = (f'<header class="mhead"><p class="kicker">Module {m["module"]:02d} / {len(m["lessons"])} lessons</p><h1>{t(m["title"])}</h1>'
            f'<p class="lede">{t(m["intro"])}</p><ol class="mtoc">{toc}</ol></header>')
    return {"id": m["file"], "title": f'{m["module"]:02d} {m["title"]}', "summary": m["intro"],
            "outline": [l["title"] for l in m["lessons"]], "html": head + "".join(lesson_html(m, i, l) for i, l in enumerate(m["lessons"], 1)),
            "questions": qs, **({"ask": ask} if ask else {})}


def basics_section(variant=None):
    b = load(CONTENT / "basics.json")
    groups = b["groups"] + (load(CONTENT / "variants" / variant / "basics.json", {"groups": []})["groups"] if variant else [])
    parts = []
    for g in groups:
        pts = ('<div class="points"><p class="eyebrow">Why be careful</p><ul>' + "".join(f"<li>{t(x)}</li>" for x in g["points"]) + "</ul></div>") if g.get("points") else ""
        terms = "".join(term_html(g, x) for x in g.get("terms", []))
        parts.append(f'''<section class="lesson bgroup{"" if g.get("terms") else " wide"}" id="g-{g["id"]}"><div class="ls-main">
<header class="ls-head"><h2>{t(g["title"])}</h2><p class="ls-sum">{t(g["intro"])}</p></header>{pts}{"".join(diagram_html(d) for d in g.get("diagrams", []))}
{f'<div class="terms">{terms}</div>' if terms else ""}</div>
<aside class="more"><div class="more-in"><p class="more-h">Find more here</p>{links_html(g.get("links", []))}</div></aside></section>''')
    qs = load(CONTENT / "quiz" / "basics.json")["questions"]
    if variant:
        qs = qs + load(CONTENT / "variants" / variant / "quiz" / "basics.json", {"questions": []})["questions"]
    head = f'<header class="mhead"><p class="kicker">Start here</p><h1>{t(b["title"])}</h1><p class="lede">{t(b["intro"])}</p></header>'
    return {"id": "basics", "title": "Start here: the basics", "summary": b["intro"], "outline": [g["title"] for g in groups],
            "html": head + "".join(parts), "questions": qs, "ask": 10}


def cases_section(variant, label):
    cases = load(CONTENT / "variants" / variant / "cases.json", [])
    if not cases:
        return None
    cards = "".join(f'''<article class="case"><p class="eyebrow">{t(c.get("area", ""))}</p><h3>{t(c["title"])}</h3>
<p><b>Client:</b> {t(c.get("client", ""))}</p><p><b>Pain:</b> {t(c.get("pain", ""))}</p><p><b>Data:</b> {t(c.get("data", ""))}</p>
<p><b>Deliver:</b></p><ul>{"".join(f"<li>{t(d)}</li>" for d in c.get("deliver", []))}</ul>
<p><b>Person approves:</b> {t(c.get("approval", ""))}</p><p><b>Measured by:</b> {t(c.get("measure", ""))}</p></article>''' for c in cases)
    head = (f'<header class="mhead"><p class="kicker">Practice projects</p><h1>{t(label)} practice projects</h1>'
            '<p class="lede">Pick one to carry through FDE Advanced. Use synthetic data only.</p></header>')
    return {"id": "projects", "title": f"Practice projects: {label}", "summary": "Projects to carry into FDE Advanced.",
            "outline": [c["title"] for c in cases], "html": head + f'<div class="cases lms-cases">{cards}</div>', "questions": []}


def languages_section():
    d = load(CONTENT / "languages.json")
    if not d:
        return None
    head = f'<header class="mhead"><p class="kicker">Start here</p><h1>{t(d["title"])}</h1><p class="lede">{t(d["intro"])}</p></header>'
    html = head + lesson_html({"module": "L", "file": "languages"}, 1, d["lesson"]).replace("Lesson L.1", "Read first") + learn.playlist_html()
    return {"id": "languages", "title": "Languages, AI SDKs and learning playlists", "summary": d["intro"], "outline": [d["lesson"]["title"]], "html": html, "questions": []}


def fde_general(variant=None):
    meta = load(CONTENT / "variants" / variant / "variant.json", {}) if variant else {}
    label = meta.get("label")
    secs = [basics_section(variant)] + ([languages_section()] if languages_section() else []) + [module_section(*module(n, variant)) for n in GENERAL]
    if variant:
        c = cases_section(variant, label)
        if c:
            secs.append(c)
    return {"id": "fde-general" + (f"-{variant}" if variant else ""), "topic_id": "fde", "topic_title": "Forward Deployed Engineer",
            "title": "FDE General" + (f": {label}" if label else ""), "category": "AI", "track": label or "All industries", "level": 1,
            "level_label": "Level 1: theory",
            "summary": meta.get("summary") or "What an FDE does and how, from the basics to evaluation and hand-over. Self-paced, with a check at the end of every section.",
            "audience": "Engineers and domain experts moving into forward deployed engineering.",
            "version": VERSION, "status": "active", "rules": RULES,
            "certificate": {"title": "FDE General" + (f" ({label})" if label else ""), "valid_months": 24}, "sections": secs}


def step_section(s):
    links = links_html([{"type": l["type"], "title": l["title"], "source": l["source"], "url": l["url"], "cost": l.get("cost", "free")} for l in s["links"]])
    fields = "".join(f"<li>{t(f['label'])}</li>" for f in s["fields"] if f["id"] != "broke")
    html = (f'<section class="lesson"><div class="ls-main"><header class="ls-head"><p class="eyebrow">Step {t(s["num"])} / {t(s["when"])}</p>'
            f'<h2>{t(s["title"])}</h2><p class="ls-sum">{t(s["what"])}</p></header>'
            f'<div class="prose"><section class="ls-sec"><h3>What to do</h3><p>{t(s["task"])}</p></section>'
            f'<section class="ls-sec"><h3>Done when</h3><p>{t(s["done"])}</p></section>'
            f'<section class="ls-sec"><h3>Evidence your mentor reviews</h3><ul>{fields}</ul></section></div></div>'
            f'<aside class="more"><div class="more-in"><p class="more-h">Find more here</p>{links}</div></aside></section>')
    guide = load(CONTENT / "lms-project-guides.json", {}).get(s["slug"])
    if guide:
        groups = [("Decision to make", [guide["decision"]]), ("Worked fictional example", [guide["example"]]),
                  ("Build and test", guide["work"]), ("Evidence to submit", guide["evidence"]), ("Mentor review criteria", guide["review"])]
        html += '<section class="lesson wide"><div class="ls-main"><div class="prose">' + "".join(
            '<section class="ls-sec"><h3>' + t(title) + '</h3>' + ("".join('<p>' + t(item) + '</p>' for item in items) if index < 2 else '<ol>' + "".join('<li>' + t(item) + '</li>' for item in items) + '</ol>') + '</section>'
            for index, (title, items) in enumerate(groups)) + '</div></div></section>'
    return {"id": "step-" + s["slug"], "title": f'Step {s["num"]}: {s["title"]}', "summary": s["what"], "outline": [s["task"]], "html": html, "questions": []}


def fde_advanced():
    m00, q00 = module(0)
    m11, q11 = module(11)
    steps = [step_section(s) for s in tldr.STEPS if s["num"] not in ("A", "B")]
    return {"id": "fde-advanced", "topic_id": "fde", "topic_title": "Forward Deployed Engineer", "title": "FDE Advanced", "category": "AI",
            "track": "All industries", "level": 2, "level_label": "Level 2: project",
            "summary": "Guided project work: set up your tools, take one real project through every FDE step with a mentor, and present it to a panel.",
            "audience": "People who passed FDE General.", "version": VERSION, "status": "active", "rules": RULES,
            "certificate": {"title": "FDE Advanced", "valid_months": 24},
            "sections": [module_section(m00, q00)] + steps + [module_section(m11, q11)]}


def topic(path):
    d = load(path)
    m = {"module": 1, "file": d["id"]}
    secs = []
    for s in d["sections"]:
        sec = {"id": s["id"], "title": s["title"], "summary": s.get("summary", ""), "outline": s.get("outline", []), "questions": s.get("questions", [])}
        if s.get("lessons"):
            sec["html"] = (f'<header class="mhead"><p class="kicker">{t(d["title"])}</p><h1>{t(s["title"])}</h1><p class="lede">{t(s.get("summary", ""))}</p></header>'
                           + "".join(lesson_html(m, i, l) for i, l in enumerate(s["lessons"], 1)))
        secs.append(sec)
    complete = all(s.get("html") for s in secs)
    return {"id": d["id"], "topic_id": d["id"], "topic_title": d["title"], "title": d["title"], "category": d.get("category", "General"),
            "track": d.get("track"), "level": d.get("level", 1), "level_label": d.get("level_label", "Level 1: theory"), "summary": d.get("summary"),
            "audience": d.get("audience"), "version": VERSION, "status": "active" if complete else "outline", "rules": {**RULES, "ask": 10},
            "certificate": {"title": d["title"], "valid_months": 24}, "sections": secs}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    pkgs = [fde_general()] + [fde_general(v.name) for v in sorted((CONTENT / "variants").glob("*")) if (v / "variant.json").exists()]
    topic_files = sorted((CONTENT / "topics").glob("*.json")) + sorted(f for d in EXTRA_TOPICS for f in d.glob("*.json"))
    pkgs += [fde_advanced()] + [topic(p) for p in topic_files]
    for p in pkgs:
        existing = load(OUT / f'{p["id"]}.json', {})
        content = {k: v for k, v in p.items() if k != "version"}
        prior = {k: v for k, v in existing.items() if k != "version"}
        p["version"] = existing["version"] if content == prior else VERSION + "." + hashlib.sha256(json.dumps(content, sort_keys=True).encode()).hexdigest()[:8]
        (OUT / f'{p["id"]}.json').write_text(json.dumps(p, ensure_ascii=True), encoding="ascii")
        q = sum(len(s.get("questions", [])) for s in p["sections"])
        ready = sum(1 for s in p["sections"] if s.get("html"))
        print(f'{p["id"]:32} {p["status"]:8} sections {ready}/{len(p["sections"])} questions {q}')
    print("wrote", len(pkgs), "packages to", OUT)


if __name__ == "__main__":
    main()
