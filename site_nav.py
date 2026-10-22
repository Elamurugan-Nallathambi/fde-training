"""Shared top bar for every page: breadcrumb back to the program, the four sections, and the light or dark switch."""
import os
from html import escape

# Ask widget from the AI knowledge service on every page; FDE_KB="" turns it off. The older help chat (FDE_CHAT=1) is used only when the widget is off.
KB = os.environ.get("FDE_KB", "https://quick-chat-program.pages.dev")
CHAT = os.environ.get("FDE_CHAT") == "1" and not KB

# The four ways through the program, in order. Paths are relative to the site root.
SECTIONS = [
 ("start", "1", "Start here", "learn/basics.html"),
 ("modules", "2", "Modules", "learn/m01.html"),
 ("practice", "3", "Practice", "tldr.html"),
 ("crash", "4", "Crash course", "crash-course.html"),
]


def topbar(prefix="", crumbs=(), section="", page="all"):
    """prefix: "" for root pages, "../" for learn pages. crumbs: [(label, href or None)] after the program name."""
    parts = [f'<a href="{prefix}index.html">FDE Training Program</a>']
    for label, href in crumbs:
        parts.append(f'<a href="{prefix}{href}">{escape(label)}</a>' if href else f'<span aria-current="page">{escape(label)}</span>')
    trail = '<span class="sep" aria-hidden="true">/</span>'.join(parts)
    links = "".join(f'<a href="{prefix}{href}"{" aria-current=true" if sid == section else ""}><span>{num}</span>{label}</a>'
                    for sid, num, label, href in SECTIONS)
    return (f'<header class="topbar"><nav class="crumbs" aria-label="Breadcrumb">{trail}</nav>'
            f'<nav class="secnav" aria-label="Program sections">{links}</nav>'
            f'<button class="themebtn" data-theme-toggle aria-label="Switch light or dark mode"></button></header>'
            + (f'<script src="{prefix}chat.js" data-root="{prefix}" data-page="{page}" defer></script>' if CHAT else "")
            + (f'<script src="{KB}/kb.js" defer></script>' if KB else ""))
