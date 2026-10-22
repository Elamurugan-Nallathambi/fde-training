"""Builds review/review.html from review/*.csv: one page to filter, tick and export the candidate resources. Local only, not deployed."""
import csv
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REVIEW = ROOT / "review"


def load():
    rows = []
    for f in sorted(REVIEW.glob("*.csv")):
        with f.open(newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                r["file"] = f.name
                if r.get("cost", "").startswith("free") and r["cost"] != "free":
                    r["why"] = (r.get("why") or "") + " (Free to audit; certificate is paid.)"
                    r["cost"] = "free"
                rows.append({k: (v or "").strip() for k, v in r.items()})
    seen, out = set(), []
    for r in rows:
        key = r["url"].rstrip("/").lower()
        if key and key not in seen:
            seen.add(key)
            out.append(r)
    return out


PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Resource Review</title>
<style>
:root{--bg:#F3F5F7;--panel:#fff;--ink:#13202E;--ink2:#3E4B59;--muted:#647282;--line:#D9DFE6;--a:#2F55C8;--ok:#0E766E;--okbg:#DDF1EE}
@media (prefers-color-scheme:dark){:root{--bg:#0F151B;--panel:#161E26;--ink:#E7EDF2;--ink2:#B7C3CE;--muted:#8C99A6;--line:#2A3540;--a:#8EA9F2;--ok:#5CC7BC;--okbg:#12302D}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 -apple-system,Segoe UI,Roboto,sans-serif}
header{position:sticky;top:0;z-index:2;background:var(--bg);border-bottom:1px solid var(--line);padding:14px 24px}
h1{margin:0 0 6px;font-size:22px}.bar{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
select,input,button{font:inherit;padding:6px 10px;border:1px solid var(--line);border-radius:6px;background:var(--panel);color:var(--ink)}
input[type=search]{min-width:240px;flex:1;max-width:420px}button{cursor:pointer}button.primary{background:var(--ink);color:var(--bg);border-color:var(--ink)}
#count{color:var(--muted);font-size:14px}main{padding:16px 24px 60px}
h2{font-size:18px;margin:22px 0 8px}
table{width:100%;border-collapse:collapse;background:var(--panel);border:1px solid var(--line);border-radius:8px;overflow:hidden}
th,td{text-align:left;vertical-align:top;padding:8px 10px;border-bottom:1px solid var(--line);font-size:14px}
th{font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:var(--muted)}
td.t a{font-weight:600;color:var(--a)}td small{color:var(--muted)}tr.on{background:var(--okbg)}
.tag{display:inline-block;font-size:11.5px;border:1px solid var(--line);border-radius:99px;padding:0 7px;color:var(--ink2);white-space:nowrap}
.why{color:var(--ink2)}input[type=checkbox]{width:18px;height:18px;accent-color:var(--ok)}
</style></head><body>
<header><h1>Resource review</h1>
<div class="bar"><input type="search" id="q" placeholder="Search title, source, topic, why"><select id="area"><option value="">All areas</option></select>
<select id="type"><option value="">All types</option></select><select id="level"><option value="">All levels</option><option>beginner</option><option>intermediate</option><option>advanced</option></select>
<select id="cost"><option value="">Free and paid</option><option>free</option><option>paid</option></select>
<label><input type="checkbox" id="onlyon"> Approved only</label>
<button id="all">Approve shown</button><button id="none">Clear shown</button><button class="primary" id="export">Export approved (CSV)</button>
<span id="count"></span></div></header>
<main id="main"></main>
<script>
const DATA = __DATA__;
const KEY = "fde-review-v1";
let on = {}; try { on = JSON.parse(localStorage.getItem(KEY) || "{}"); } catch (e) {}
const save = () => { try { localStorage.setItem(KEY, JSON.stringify(on)); } catch (e) {} };
const $ = (s) => document.querySelector(s);
const uniq = (k) => [...new Set(DATA.map((r) => r[k]).filter(Boolean))].sort();
uniq("area").forEach((v) => $("#area").append(new Option(v, v)));
uniq("type").forEach((v) => $("#type").append(new Option(v, v)));
function shown() {
  const q = $("#q").value.toLowerCase(), f = { area: $("#area").value, type: $("#type").value, level: $("#level").value, cost: $("#cost").value };
  return DATA.filter((r) => Object.entries(f).every(([k, v]) => !v || r[k] === v) && (!$("#onlyon").checked || on[r.url]) &&
    (!q || [r.title, r.source, r.topic, r.why].join(" ").toLowerCase().includes(q)));
}
function render() {
  const rows = shown(), main = $("#main"); main.replaceChildren();
  const groups = {}; rows.forEach((r) => (groups[r.area] = groups[r.area] || []).push(r));
  for (const [area, list] of Object.entries(groups)) {
    const h = document.createElement("h2"); h.textContent = area + " (" + list.length + ")"; main.append(h);
    const t = document.createElement("table");
    t.innerHTML = "<thead><tr><th></th><th>Resource</th><th>Topic</th><th>Type</th><th>Length</th><th>Level</th><th>Cost</th><th>Why</th></tr></thead>";
    const tb = document.createElement("tbody");
    for (const r of list) {
      const tr = document.createElement("tr"); if (on[r.url]) tr.className = "on";
      const cells = [null, null, r.topic, r.type, r.length, r.level, r.cost, r.why];
      cells.forEach((c, i) => {
        const td = document.createElement("td");
        if (i === 0) { const cb = document.createElement("input"); cb.type = "checkbox"; cb.checked = !!on[r.url];
          cb.onchange = () => { on[r.url] = cb.checked; if (!cb.checked) delete on[r.url]; tr.className = cb.checked ? "on" : ""; save(); count(); }; td.append(cb); }
        else if (i === 1) { td.className = "t"; const a = document.createElement("a"); a.href = r.url; a.target = "_blank"; a.rel = "noopener"; a.textContent = r.title;
          const s = document.createElement("small"); s.textContent = " " + r.source; td.append(a, document.createElement("br"), s); }
        else if (i >= 3 && i <= 6) { const sp = document.createElement("span"); sp.className = "tag"; sp.textContent = c; td.append(sp); }
        else { td.textContent = c; if (i === 7) td.className = "why"; }
        tr.append(td);
      });
      tb.append(tr);
    }
    t.append(tb); main.append(t);
  }
  count();
}
function count() { $("#count").textContent = shown().length + " shown / " + DATA.length + " total / " + Object.keys(on).length + " approved"; }
["#q", "#area", "#type", "#level", "#cost", "#onlyon"].forEach((s) => $(s).addEventListener("input", render));
$("#all").onclick = () => { shown().forEach((r) => (on[r.url] = true)); save(); render(); };
$("#none").onclick = () => { shown().forEach((r) => delete on[r.url]); save(); render(); };
$("#export").onclick = () => {
  const cols = ["area", "topic", "type", "title", "source", "url", "length", "cost", "level", "why"];
  const esc = (v) => '"' + String(v || "").replace(/"/g, '""') + '"';
  const csv = [cols.join(",")].concat(DATA.filter((r) => on[r.url]).map((r) => cols.map((c) => esc(r[c])).join(","))).join("\\n");
  const a = document.createElement("a"); a.href = URL.createObjectURL(new Blob([csv], { type: "text/csv" })); a.download = "approved-resources.csv"; a.click();
};
render();
</script></body></html>
"""


def main():
    rows = load()
    out = REVIEW / "review.html"
    out.write_text(PAGE.replace("__DATA__", json.dumps(rows, ensure_ascii=True)), encoding="utf-8")
    by = {}
    for r in rows:
        by[r["area"]] = by.get(r["area"], 0) + 1
    print(f"{len(rows)} unique items -> {out}")
    for k, v in by.items():
        print(f"  {v:4}  {k}")


if __name__ == "__main__":
    main()
