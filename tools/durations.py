"""Finds how long each tutor step resource takes: YouTube length, course hours stated on the page, or reading time (words / 200)."""
import json
import re
import sys
import urllib.request
from html import unescape

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/130 Safari/537.36", "Accept-Language": "en-US,en"}


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read().decode("utf-8", "replace")


def text_of(html):
    html = re.sub(r"(?is)<(script|style|nav|header|footer|noscript)[^>]*>.*?</\1>", " ", html)
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", html)))


def measure(url, kind):
    try:
        html = fetch(url)
    except Exception as e:
        return None, f"fetch failed: {e}"
    if "youtube.com/watch" in url:
        m = re.search(r'"lengthSeconds":"(\d+)"', html)
        return (round(int(m.group(1)) / 60), "YouTube length") if m else (None, "no lengthSeconds")
    t = text_of(html)
    if kind in ("course", "book"):
        hits = re.findall(r"([^.]{0,60}\b\d+(?:\.\d+)?\s*(?:hours?|hrs?|minutes?|mins?)\b[^.]{0,40})", t, re.I)
        return None, "page says: " + " | ".join(h.strip() for h in hits[:4]) if hits else "duration not stated on page"
    words = len(t.split())
    return max(5, round(words / 200)), f"reading estimate, {words} words / 200"


if __name__ == "__main__":
    data = json.load(open(sys.argv[1]))
    for s in data["steps"]:
        for l in s["links"]:
            mins, how = measure(l["url"], l["type"])
            print(f'{s["num"]:>3} | {l["type"]:6} | {mins if mins is not None else "-":>4} | {l["title"][:55]:55} | {how}')
