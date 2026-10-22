"""Checks content/mNN.json against content/SCHEMA.md rules; writes all link URLs to a file for verify_links.py."""
import json, os
import re
import sys
from pathlib import Path

CONTENT = Path(__file__).resolve().parent.parent / "content"
DIAGRAM_KEYS = {"flow": "steps", "cycle": "steps", "layers": "layers", "swimlane": "steps", "compare": "columns", "branch": "branches"}

# Names that must not appear in generic content (for example an employer or client), comma separated in CONTENT_BANNED_TERMS.
BANNED = [w.strip().lower() for w in os.environ.get("CONTENT_BANNED_TERMS", "").split(",") if w.strip()]


def words(lesson):
    parts = lesson["sections"] + [lesson.get("example", {}), {"p": [lesson.get("why", "")]}]
    text = " ".join(" ".join(s.get("p", []) + (s.get("list") or [])) for s in parts)
    return len(re.findall(r"\w+", text))


def check(f):
    raw = f.read_text(encoding="utf-8")
    probs = []
    bad = sorted({c for c in raw if ord(c) > 127})
    if bad:
        probs.append(f"non-ASCII: {bad}")
    probs += [f"mentions {w}" for w in BANNED if w in raw.lower()]
    d = json.loads(raw)
    urls = []
    for l in d["lessons"]:
        lid = l.get("id", "?")
        for k in ("id", "title", "summary", "why", "sections", "example", "practice", "pitfalls", "check", "links", "diagram"):
            if k not in l:
                probs.append(f"{lid}: missing {k}")
        dg = l.get("diagram", {})
        if dg.get("type") not in DIAGRAM_KEYS or DIAGRAM_KEYS[dg.get("type")] not in dg:
            probs.append(f"{lid}: bad diagram {dg.get('type')}")
        if dg.get("type") == "swimlane" and any(int(s["lane"]) >= len(dg.get("lanes", [])) for s in dg.get("steps", [])):
            probs.append(f"{lid}: swimlane lane index out of range")
        n = len(l.get("sections", []))
        if not 3 <= n <= 6:
            probs.append(f"{lid}: {n} sections")
        for p in l.get("practice", []):
            for k in ("title", "time", "goal", "steps", "done_when"):
                if k not in p:
                    probs.append(f"{lid}: practice missing {k}")
        if not 4 <= len(l.get("links", [])) <= 8:
            probs.append(f"{lid}: {len(l.get('links', []))} links")
        for x in l.get("links", []):
            if x.get("type") not in ("docs", "video", "course", "book", "cert") or x.get("cost") not in ("free", "paid"):
                probs.append(f"{lid}: bad link fields {x.get('url')}")
            urls.append(x["url"])
        w = words(l)
        if w < 600:
            probs.append(f"{lid}: only {w} words of explanation")
    return d, probs, urls


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    all_urls, failed = set(), False
    for f in sorted(CONTENT.glob("m[0-9][0-9].json")):
        try:
            d, probs, urls = check(f)
        except Exception as e:
            print(f"{f.name}: cannot load ({e})")
            failed = True
            continue
        all_urls.update(urls)
        print(f"{f.name}: {len(d['lessons'])} lessons, {len(urls)} links, {'OK' if not probs else 'PROBLEMS'}")
        for p in probs:
            print("   ", p)
        failed = failed or bool(probs)
    b = CONTENT / "basics.json"
    if b.exists():
        raw = b.read_text(encoding="utf-8")
        d = json.loads(raw)
        urls = [x["url"] for g in d["groups"] for x in g["links"]]
        probs = [f"non-ASCII: {sorted({c for c in raw if ord(c) > 127})}"] if any(ord(c) > 127 for c in raw) else []
        probs += [f"{g['id']}: term missing one/why" for g in d["groups"] for x in g["terms"] if not x.get("one") or not x.get("why")]
        all_urls.update(urls)
        print(f"basics.json: {len(d['groups'])} groups, {sum(len(g['terms']) for g in d['groups'])} terms, {len(urls)} links, {'OK' if not probs else 'PROBLEMS'}")
        for p in probs:
            print("   ", p)
        failed = failed or bool(probs)
    sys.path.insert(0, str(CONTENT.parent))
    import tldr
    all_urls.update(tldr.urls())
    import crash
    all_urls.update(crash.urls())
    print(f"crash.py: {len(crash.urls())} library links")
    print(f"tldr.py: {len(tldr.STEPS)} steps, {len(tldr.urls())} links")
    if out:
        out.write_text("\n".join(sorted(all_urls)) + "\n")
        print(f"{len(all_urls)} unique URLs written to {out}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
