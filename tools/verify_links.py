#!/usr/bin/env python3
"""Checks links: YouTube via oEmbed (prints real title), other URLs by HTTP status and page title. Usage: verify_links.py URL... or verify_links.py file.txt"""

import json, re, sys, urllib.parse, urllib.request, concurrent.futures as cf

def yt(vid):
    u = "https://www.youtube.com/oembed?format=json&url=" + urllib.parse.quote("https://www.youtube.com/watch?v=" + vid, safe="")
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=20) as r:
            d = json.load(r); return ("OK", vid, f'{d["title"]} | {d["author_name"]}')
    except Exception as e:
        return ("NO", vid, str(e)[:60])

def page(u):
    try:
        req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 Chrome/124 Safari/537.36", "Accept-Language": "en"})
        with urllib.request.urlopen(req, timeout=25) as r:
            body = r.read(400000).decode("utf-8", "ignore"); m = re.search(r"<title[^>]*>(.*?)</title>", body, re.S | re.I)
            return ("OK", u, f"{r.status} {r.geturl() if r.geturl()!=u else ''} | {(m.group(1).strip()[:90] if m else '(pdf/no title)')}")
    except Exception as e:
        return ("NO", u, str(e)[:80])


def check(u):
    m = re.search(r"youtube\.com/watch\?v=([\w-]+)", u)
    return yt(m.group(1)) if m else page(u)

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 1 and not args[0].startswith("http"):
        args = [l.strip() for l in open(args[0]) if l.strip().startswith("http")]
    with cf.ThreadPoolExecutor(10) as ex:
        for s, k, v in ex.map(check, args):
            print(s, k, "|", re.sub(r"\s+", " ", v))
