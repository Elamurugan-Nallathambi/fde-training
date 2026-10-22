#!/usr/bin/env python3
"""fde.py: track your FDE training path from your own machine. Same files as the tutor page (fde/ folder); Python 3.9+, no installs.

Run from your journal repository:  python3 fde.py init | status | next | open STEP | log STEP | check STEP | sync | help
"""
import datetime as dt
import json
import math
import os
import re
import shutil
import subprocess
import sys
import urllib.request
import webbrowser
from pathlib import Path

VERSION = "1"
SITE = "https://fde-training-program.pages.dev"
ROOT = Path(__file__).resolve().parent
DIR = ROOT / "fde"
DRAFTS = ROOT / "drafts"
CACHE = Path.home() / ".fde-steps-cache.json"
BUFFER = 1.3
DATA_RE = re.compile(r"<!-- fde-data (\{[\s\S]*\}) -->")
PLACEHOLDER = re.compile(r"\b(todo|tbd|lorem ipsum|placeholder)\b", re.I)


# ---------- shared file format (must match the tutor page) ----------
def embed(obj):
    return "<!-- fde-data " + json.dumps(obj, ensure_ascii=True, separators=(",", ":")).replace("--", "-\\u002d") + " -->\n"


def parse(text):
    m = DATA_RE.search(text or "")
    try:
        return json.loads(m.group(1)) if m else None
    except ValueError:
        return None


def read_data(path):
    return parse(path.read_text(encoding="utf-8")) if path.exists() else None


def now_iso():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def today():
    return dt.date.today().isoformat()


# ---------- steps (downloaded from the site, cached for offline use) ----------
def site_data():
    try:
        req = urllib.request.Request(SITE + "/tutor-data.json", headers={"User-Agent": "Mozilla/5.0 (fde.py " + VERSION + ")"})
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read().decode("utf-8"))
        CACHE.write_text(json.dumps(data), encoding="utf-8")
        return data
    except Exception:
        if CACHE.exists():
            return json.loads(CACHE.read_text(encoding="utf-8"))
        sys.exit("Could not download the step list and no cached copy exists. Check your internet connection.")


def steps():
    return site_data()["steps"]


def find(all_steps, key):
    key = key.strip().lower()
    for s in all_steps:
        if key in (s["num"].lower(), s["num"].lower().lstrip("0"), s["slug"]):
            return s
    sys.exit(f"No step '{key}'. Use a number like 05, a letter like A, or a name like discovery.")


def step_path(s):
    return DIR / "steps" / f'{s["num"].lower()}-{s["slug"]}.md'


# ---------- checks and time (same rules as the tutor page) ----------
def words(v):
    return len(re.findall(r"\S+", v or ""))


def check(s, values):
    out = []
    for f in s["fields"]:
        if f["id"] == "broke":
            continue
        v = str(values.get(f["id"], "")).strip()
        if not v:
            out.append((False, f'{f["label"]}: missing'))
        elif f["kind"] == "url" and not re.match(r"^https?://\S+$", v, re.I):
            out.append((False, f'{f["label"]}: needs a full link starting with https://'))
        elif f.get("min_words") and words(v) < f["min_words"]:
            out.append((False, f'{f["label"]}: {words(v)} of at least {f["min_words"]} words'))
        elif f.get("need") == "number" and not re.search(r"\d", v):
            out.append((False, f'{f["label"]}: should include your numbers'))
        elif PLACEHOLDER.search(v):
            out.append((False, f'{f["label"]}: still has a placeholder'))
        else:
            out.append((True, f["label"]))
    return out


def opens():
    d = read_data(DIR / "activity.md") or {"opens": []}
    first = {}
    for o in d.get("opens", []):
        if o.get("url") and (o["url"] not in first or o["at"] < first[o["url"]]):
            first[o["url"]] = o["at"]
    return d, first


def parse_iso(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def step_time(s):
    _, first = opens()
    timed = [l for l in s["links"] if l.get("mins") and not l.get("optional")]
    total = sum(l["mins"] for l in timed)
    required = math.ceil(total * BUFFER)
    opened = [l for l in s["links"] if l["url"] in first]
    starts = [parse_iso(first[l["url"]]) for l in opened]
    start = min(starts) if starts else None
    elapsed = int((dt.datetime.now(dt.timezone.utc) - start).total_seconds() // 60) if start else 0
    unopened = [l for l in timed if l["url"] not in first]
    return dict(total=total, required=required, elapsed=elapsed, start=start, unopened=unopened, opened=opened, first=first,
                met=bool(total) and not unopened and elapsed >= required)


# ---------- project work and points (same rules as the tutor page) ----------
MAX_POINTS = 20


def work_commits():
    if not (ROOT / ".git").exists():
        return []
    out = subprocess.run(["git", "log", "--format=%h|%aI|%s", "--", "projects"], cwd=ROOT, capture_output=True, text=True).stdout
    commits = []
    for line in out.splitlines():
        sha, at, msg = (line.split("|", 2) + ["", ""])[:3]
        try:
            commits.append(dict(sha=sha, at=parse_iso(at).astimezone(dt.timezone.utc), msg=msg))
        except ValueError:
            pass
    return commits


def saved_at(f):
    if not f:
        return None
    if f.get("savedAt"):
        return parse_iso(f["savedAt"])
    return parse_iso(f["saved"] + "T23:59:59+00:00") if f.get("saved") else None


def step_work(all_steps, s, commits=None):
    commits = work_commits() if commits is None else commits
    i = all_steps.index(s)
    prevs = [saved_at(read_data(step_path(x))) for x in all_steps[:i]]
    prev = max([p for p in prevs if p], default=None)
    end = saved_at(read_data(step_path(s)))
    if not end:
        if any(read_data(step_path(x)) for x in all_steps[i + 1:]):
            return []
        return [c for c in commits if not prev or c["at"] > prev]
    return [c for c in commits if (not prev or c["at"] > prev) and c["at"] <= end]


def step_points(all_steps, s, commits=None):
    f = read_data(step_path(s))
    if not f:
        return 0
    p = 10 if f.get("checks", {}).get("pass") else 0
    t = f.get("time") or {}
    p += 5 if (not t.get("total") or t.get("met")) else (2 if t.get("confirmed_early") else 0)
    return p + (5 if step_work(all_steps, s, commits) else 0)


def fmt(m):
    if m >= 60:
        return f"{m // 60} h {m % 60} min" if m % 60 else f"{m // 60} h"
    return f"{m} min"


# ---------- git ----------
def git(*args, check_ok=True):
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    if check_ok and r.returncode != 0:
        sys.exit("git " + " ".join(args) + " failed:\n" + (r.stderr or r.stdout).strip())
    return r.stdout.strip()


def pull():
    if not (ROOT / ".git").exists():
        sys.exit("Run fde.py from inside your journal repository (the folder you cloned from GitHub).")
    if git("remote", check_ok=False):
        git("pull", "--rebase", "--autostash", "--quiet")


def commit_push(paths, message):
    git("add", *[str(p.relative_to(ROOT)) for p in paths])
    if not git("diff", "--cached", "--name-only"):
        print("Nothing changed.")
        return
    git("commit", "-m", message, "--quiet")
    if git("remote", check_ok=False):
        if input("Push to GitHub now? [Y/n] ").strip().lower() in ("", "y", "yes"):
            git("push", "--quiet")
            print("Pushed. The tutor page will show it on next load.")
        else:
            print("Committed locally. Run 'git push' when ready.")


# ---------- files the tutor page also writes ----------
def write_activity(new_opens):
    d, _ = opens()
    lst = d.get("opens", []) + new_opens
    rows = [f'| {o["at"].replace("T", " ")[:16]} | {o["step"]} | {o["title"].replace("|", "/")} | {o.get("mins") or "self-paced"} |' for o in reversed(lst)]
    md = "\n".join(["# Learning activity", "", "Resources opened from the tutor page, newest first. Times are UTC, when the link was opened.", "",
                    "| When | Step | Resource | Expected minutes |", "|---|---|---|---|", *rows, "", embed({"opens": lst})])
    (DIR / "activity.md").write_text(md, encoding="utf-8")


def write_progress(all_steps):
    prof = read_data(DIR / "profile.md") or {}
    commits = work_commits()
    done, pts, rows = 0, 0, []
    for s in all_steps:
        f = read_data(step_path(s))
        status = "not started" if not f else "done" if f.get("checks", {}).get("pass") else "saved, checks not passing"
        done += status == "done"
        p = step_points(all_steps, s, commits)
        pts += p
        rows.append(f'| {s["num"]} | {s["title"]} | {status} | {len(step_work(all_steps, s, commits)) if f else ""} | {p} | {f["saved"] if f else ""} |')
    md = "\n".join([f"# FDE path progress: {done} of {len(all_steps)} steps proven", "",
                    f'Project: {(prof.get("project") or {}).get("title") or "-"}  ', f"Points: {pts} of {len(all_steps) * MAX_POINTS}  ", f"Updated: {today()}", "",
                    "| Step | Title | Status | Project commits | Points | Saved |", "|---|---|---|---|---|---|", *rows, "",
                    "A step counts as done only when its evidence file is saved here and passes the checks. Points: 10 checks passed, 5 time met, 5 at least one commit under projects/ during the step.",
                    "This is a basic tracker for accountability. It counts what is saved and committed; it does not judge quality.", ""])
    (DIR / "progress.md").write_text(md, encoding="utf-8")


def write_step(s, values, tutor=""):
    checks = check(s, values)
    ok = all(c[0] for c in checks)
    t = step_time(s)
    if t["total"] and not t["met"]:
        if not t["start"]:
            why = "You have not opened any of this step's resources yet (use: python3 fde.py open " + s["num"] + ")."
        elif t["unopened"]:
            why = "You have not opened: " + ", ".join(l["title"] for l in t["unopened"]) + "."
        else:
            why = f'You first opened them {fmt(t["elapsed"])} ago; going through them fully takes about {fmt(t["required"])} including a 30% buffer.'
        print("\n" + why)
        if input("Did you fully go through all the resources for this step? [y/N] ").strip().lower() not in ("y", "yes"):
            sys.exit("Not saved. Finish the resources, then run log again.")
    time = dict(total=t["total"], required=t["required"], elapsed=t["elapsed"], met=t["met"], confirmed_early=bool(t["total"] and not t["met"]),
                opened=[dict(title=l["title"], mins=l.get("mins"), first=t["first"][l["url"]]) for l in t["opened"]])
    prof = read_data(DIR / "profile.md") or {}
    rec = dict(time=time, slug=s["slug"], step=s["num"], title=s["title"], fields=values,
               checks=dict(**{"pass": ok}, failed=[c[1] for c in checks if not c[0]]), tutor=tutor, saved=today(), savedAt=now_iso())
    lines = [f'# Step {s["num"]}: {s["title"]}', "", f'Project: {(prof.get("project") or {}).get("title") or "-"}  ',
             f'Status: {"checks passed" if ok else "checks not passed yet"}  ', f'Saved: {rec["saved"]}', ""]
    for f in s["fields"]:
        if values.get(f["id"]):
            lines += [f'## {f["label"]}', str(values[f["id"]]), ""]
    lines += ["## Time on resources",
              (f'Needed: {time["required"]} min ({time["total"]} min of resources plus 30%). Since first open: {time["elapsed"]} min. '
               + ("Time met." if time["met"] else "Saved early; learner confirmed they went through everything.")) if time["total"] else "Self-paced step."]
    lines += [f'- {o["title"]}: {str(o["mins"]) + " min" if o["mins"] else "self-paced"}, first opened {o["first"].replace("T", " ")[:16]} UTC' for o in time["opened"]]
    lines += ["", embed(rec)]
    p = step_path(s)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(lines), encoding="utf-8")
    return p, ok, checks


# ---------- drafts: write evidence in your editor ----------
def draft_path(s):
    return DRAFTS / f'{s["num"].lower()}-{s["slug"]}.md'


def make_draft(s):
    existing = (read_data(step_path(s)) or {}).get("fields", {})
    out = [f'# Step {s["num"]}: {s["title"]}', "", f'Task: {s["task"]}', f'Done when: {s["done"]}', "",
           "Write under each heading. Keep the headings as they are; delete these instruction lines if you like.", ""]
    for f in s["fields"]:
        hint = " (link)" if f["kind"] == "url" else (f' (at least {f["min_words"]} words)' if f.get("min_words") else "")
        out += [f'## {f["label"]}{hint}', existing.get(f["id"], ""), ""]
    p = draft_path(s)
    DRAFTS.mkdir(exist_ok=True)
    if not p.exists():
        p.write_text("\n".join(out), encoding="utf-8")
    return p


def read_draft(s, p):
    text = p.read_text(encoding="utf-8")
    values = {}
    for f in s["fields"]:
        m = re.search(r"^## " + re.escape(f["label"]) + r"[^\n]*\n([\s\S]*?)(?=^## |\Z)", text, re.M)
        if m:
            values[f["id"]] = m.group(1).strip()
    return values


def edit(p):
    editor = os.environ.get("VISUAL") or os.environ.get("EDITOR")
    if shutil.which("code"):
        subprocess.run(["code", "--wait", str(p)])
    elif editor:
        subprocess.run(editor.split() + [str(p)])
    else:
        print(f"Open {p} in your editor, write your evidence, save it, then come back here.")
        input("Press Enter when you have saved the file... ")


# ---------- commands ----------
def slugify(title):
    s = re.sub(r"[^a-z0-9]+", "-", (title or "").lower()).strip("-")
    return (s[:40].rsplit("-", 1)[0] if len(s) > 40 else s) or "my-project"


def cmd_init():
    pull()
    prof = read_data(DIR / "profile.md") or {}
    p = prof.get("project") or {}
    if not p.get("title"):
        sys.exit(f"No project saved yet. Choose and save one on the tutor page ({SITE}/tldr), then run git pull and init again.")
    data = site_data()
    ind = next((i["name"] for i in data.get("industries", []) if i["id"] == p.get("industry")), "-")
    setup = prof.get("setup") or {}
    rec = setup.get("recommended") or {}
    folder = ROOT / "projects" / slugify(p["title"])
    if folder.exists():
        sys.exit(f"{folder.relative_to(ROOT)} already exists. Keep building there.")
    for sub in ("data", "src", "tests", "eval"):
        (folder / sub).mkdir(parents=True, exist_ok=True)
    for sub in ("data", "src", "tests"):
        (folder / sub / ".gitkeep").write_text("", encoding="utf-8")
    (folder / "eval" / "cases.csv").write_text("case_id,type,input,expected,output,pass,failure_note\n", encoding="utf-8")
    readme = [f'# {p["title"]}', "", f"Industry: {ind}", "", "## Problem", p.get("problem") or "-", "", "## Users and approver", p.get("users") or "-", "",
              "## Data", p.get("data") or "-", "", "Use synthetic or public data only. Never put real client or personal data in this repository.", "",
              "## Success measure", p.get("measure") or "-", "", "## How I will build it",
              f'- Retrieval: {rec.get("retrieval") or "not decided yet"}', f'- Workflow or agent: {rec.get("flow") or "not decided yet"}',
              f'- Model: {rec.get("model") or "not decided yet"}', "", "## Folders", "- `data/` sample or synthetic data", "- `src/` your code",
              "- `tests/` your tests", "- `eval/cases.csv` your evaluation set (step 09)", "",
              "Commit your work here as you go. The tutor counts commits under `projects/` for each step.", ""]
    (folder / "README.md").write_text("\n".join(readme), encoding="utf-8")
    commit_push([folder], f'Start project: {p["title"]}')
    print(f"Created {folder.relative_to(ROOT)}. Build, test and commit your work there.")


def cmd_status(all_steps):
    prof = read_data(DIR / "profile.md") or {}
    title = (prof.get("project") or {}).get("title")
    print(f'Project: {title or "(not set - choose one on the tutor page: " + SITE + "/tldr)"}\n')
    commits = work_commits()
    done, nxt, pts = 0, None, 0
    print(f'  {"":7} {"":3} {"Step":38}  {"Time":>12}  {"Commits":>7}  {"Points":>6}')
    for s in all_steps:
        f = read_data(step_path(s))
        t = step_time(s)
        state = "DONE " if f and f.get("checks", {}).get("pass") else "SAVED" if f else "     "
        done += state == "DONE "
        if not f or state != "DONE ":
            nxt = nxt or s
        need = "time met" if t["met"] else (fmt(t["required"]) if t["total"] else "self-paced")
        p = step_points(all_steps, s, commits)
        pts += p
        print(f'  [{state}] {s["num"]:>2}  {s["title"][:38]:38}  {need:>12}  {len(step_work(all_steps, s, commits)):>7}  {p:>3}/{MAX_POINTS}')
    bar = "#" * done + "." * (len(all_steps) - done)
    print(f"\n  {bar}  {done} of {len(all_steps)} steps proven, {pts} of {len(all_steps) * MAX_POINTS} points")
    print("  Basic tracker for accountability: it counts what you save and commit, not how good the work is.")
    if nxt:
        print(f'\nNext: step {nxt["num"]} {nxt["title"]}.  Run: python3 fde.py next')


def cmd_next(all_steps, key=None):
    s = find(all_steps, key) if key else next((x for x in all_steps if not (read_data(step_path(x)) or {}).get("checks", {}).get("pass")), all_steps[-1])
    t = step_time(s)
    print(f'Step {s["num"]}: {s["title"]}  ({s["when"]})\n\n{s["what"]}\n')
    for i, l in enumerate(s["links"], 1):
        seen = "opened" if l["url"] in t["first"] else "not opened"
        print(f'  {i}. {l["title"]} ({l["source"]}, {"optional" if l.get("optional") else fmt(l["mins"]) if l.get("mins") else "self-paced"}, {seen})\n     {l["url"]}')
    print(f'\nWhat to do: {s["task"]}\nDone when: {s["done"]}')
    print(f'Time: {fmt(t["required"]) + " including 30% buffer" if t["total"] else "self-paced"}.')
    print(f'\nOpen the resources:  python3 fde.py open {s["num"]}\nSave your evidence:  python3 fde.py log {s["num"]}')


def cmd_open(all_steps, key):
    s = find(all_steps, key)
    pull()
    _, first = opens()
    new = []
    for l in s["links"]:
        print(f'Opening {l["title"]} ({fmt(l["mins"]) if l.get("mins") else "self-paced"})')
        webbrowser.open(l["url"])
        new.append(dict(at=now_iso(), step=s["num"], title=l["title"], url=l["url"], mins=l.get("mins")))
    write_activity(new)
    commit_push([DIR / "activity.md"], f'Activity: opened step {s["num"]} resources')
    t = step_time(s)
    if t["total"]:
        print(f'\nGive it about {fmt(t["required"])} (resources plus 30%). Then run: python3 fde.py log {s["num"]}')


def cmd_log(all_steps, key):
    s = find(all_steps, key)
    pull()
    p = make_draft(s)
    print(f"Your draft: {p.relative_to(ROOT)}")
    edit(p)
    values = read_draft(s, p)
    for ok, text in check(s, values):
        print(("  OK       " if ok else "  NOT YET  ") + text)
    path, ok, _ = write_step(s, values)
    write_progress(all_steps)
    commit_push([path, DIR / "progress.md"], f'Step {s["num"]}: {s["title"]} ({"done" if ok else "draft"})')
    print("Step done." if ok else "Saved as a draft. Fix the NOT YET items and run log again.")


def cmd_check(all_steps, key):
    s = find(all_steps, key)
    p = draft_path(s)
    values = read_draft(s, p) if p.exists() else (read_data(step_path(s)) or {}).get("fields", {})
    for ok, text in check(s, values):
        print(("  OK       " if ok else "  NOT YET  ") + text)
    t = step_time(s)
    if t["total"]:
        print(f'  Time: {"met" if t["met"] else fmt(t["elapsed"]) + " of " + fmt(t["required"])}')


def main():
    args = sys.argv[1:]
    cmd = args[0] if args else "help"
    if cmd in ("help", "-h", "--help"):
        print(__doc__.strip() + "\n\n  init          create projects/<your-project>/ from the project saved on the tutor page\n  status        where you are on every step\n  next [STEP]   what to do next: task, links, done when\n"
              "  open STEP     open the step's resources in your browser and record the time\n"
              "  log STEP      write your evidence in a draft file, check it, commit and push\n"
              "  check STEP    run the checks without saving\n  sync          pull the latest from GitHub\n\n"
              "Do not hand-edit files inside fde/. Use the tutor page or this script for those.")
        return
    if cmd == "sync":
        pull(); print("Up to date."); return
    if cmd == "init":
        cmd_init(); return
    all_steps = steps()
    if cmd == "status":
        cmd_status(all_steps)
    elif cmd == "next":
        cmd_next(all_steps, args[1] if len(args) > 1 else None)
    elif cmd in ("open", "log", "check"):
        if len(args) < 2:
            sys.exit(f"Which step? For example: python3 fde.py {cmd} 05")
        {"open": cmd_open, "log": cmd_log, "check": cmd_check}[cmd](all_steps, args[1])
    else:
        sys.exit(f"Unknown command '{cmd}'. Run: python3 fde.py help")


if __name__ == "__main__":
    main()
