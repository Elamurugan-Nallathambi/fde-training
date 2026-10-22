#!/usr/bin/env python3
"""Checks LMS topic files (content/topics/*.json): every section with a lesson must meet the lesson standard and carry 10 sound questions.
Usage: tools/check_topic.py content/topics/qms-fundamentals.json [...]   Exit code 1 when anything fails."""

import json, os, sys
from collections import Counter

# Names that must not appear in generic content (for example an employer or client), comma separated in CONTENT_BANNED_TERMS.
BANNED = [w.strip().lower() for w in os.environ.get("CONTENT_BANNED_TERMS", "").split(",") if w.strip()]
DIAGRAMS = {"flow", "cycle", "layers", "swimlane", "compare", "branch"}


def words(lesson):
    return len(" ".join(p for s in lesson.get("sections", []) for p in s.get("p", []) + s.get("list", [])).split())


def check_lesson(where, l, ids):
    out = []
    for k in ("id", "title", "summary", "why", "sections", "diagram", "example", "practice", "pitfalls", "check", "links"):
        if not l.get(k):
            out.append(f"{where}: missing {k}")
    if l.get("id") in ids:
        out.append(f"{where}: duplicate lesson id {l.get('id')}")
    ids.add(l.get("id"))
    n = words(l)
    if not 700 <= n <= 1300:
        out.append(f"{where}: {n} words in sections (need 700 to 1200)")
    if not 3 <= len(l.get("sections", [])) <= 7:
        out.append(f"{where}: {len(l.get('sections', []))} sections (need 3 to 6)")
    if any("p" not in s or not s["p"] for s in l.get("sections", [])):
        out.append(f"{where}: a section has no paragraphs")
    if (l.get("diagram") or {}).get("type") not in DIAGRAMS:
        out.append(f"{where}: diagram type must be one of {sorted(DIAGRAMS)}")
    if not 4 <= len(l.get("links", [])) <= 8:
        out.append(f"{where}: {len(l.get('links', []))} links (need 4 to 8)")
    if not 3 <= len(l.get("pitfalls", [])) <= 5:
        out.append(f"{where}: {len(l.get('pitfalls', []))} pitfalls (need 3 to 5)")
    for p in l.get("pitfalls", []):
        if len(p.split()) < 6:
            out.append(f"{where}: pitfall too short to be a real mistake: {p!r}")
    for pr in l.get("practice", []):
        if not 3 <= len(pr.get("steps", [])) <= 7 or not pr.get("done_when"):
            out.append(f"{where}: practice needs 3 to 7 steps and done_when")
    return out


def check_questions(where, qs, lesson_ids):
    out = []
    if len(qs) != 10:
        out.append(f"{where}: {len(qs)} questions (need 10)")
    longest = 0
    for q in qs:
        opts, a = q.get("options", []), q.get("answer")
        if not q.get("id") or not q.get("q") or not q.get("why"):
            out.append(f"{where}: question missing id, q or why: {q.get('id')}")
        if len(opts) != 4 or not isinstance(a, int) or not 0 <= a < len(opts):
            out.append(f"{where}: {q.get('id')} needs 4 options and a valid answer index")
            continue
        if q.get("lesson") not in lesson_ids:
            out.append(f"{where}: {q.get('id')} lesson field must be one of {sorted(lesson_ids)}")
        if len(opts[a]) == max(len(o) for o in opts) and sum(len(o) == len(opts[a]) for o in opts) == 1:
            longest += 1
    if longest > 2:
        out.append(f"{where}: the correct option is the longest in {longest} questions (max 2)")
    spread = Counter(q.get("answer") for q in qs)
    if qs and max(spread.values()) > 5:
        out.append(f"{where}: answers bunched on one position {dict(spread)}")
    return out


def main(paths):
    problems, ids = [], set()
    for p in paths:
        text = open(p, encoding="utf-8").read()
        bad = sorted({c for c in text if ord(c) > 127})
        if bad:
            problems.append(f"{p}: non-ASCII characters {bad}")
        problems += [f"{p}: mentions {w}" for w in BANNED if w in text.lower()]
        t = json.loads(text)
        for s in t["sections"]:
            where = f'{t["id"]}/{s["id"]}'
            if not s.get("lessons"):
                problems.append(f"{where}: still an outline (no lesson)")
                continue
            lids = set()
            for l in s["lessons"]:
                problems += check_lesson(where, l, ids)
                lids.add(l.get("id"))
            problems += check_questions(where, s.get("questions", []), lids)
    for x in problems:
        print("FAIL", x)
    print(f"{len(problems)} problems in {len(paths)} files")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
