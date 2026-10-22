# Lesson content format

Each module is one JSON file: `content/mNN.json` (m01 to m09). The site build renders it into `public/learn/mNN.html`.

Audience: people training to become forward deployed engineers. Some come from software, some from a domain or business background (finance, operations, quality, HR). Write so both can follow: explain every term the first time it appears, build from simple to detailed, and use concrete examples from real business work.

## Writing rules (strict)

- Plain, simple technical English. Short sentences. Active voice. Explain the why, not only the what.
- ASCII characters only. No em dashes, en dashes, curly quotes, arrows, bullets or emoji. Use "-" and straight quotes. Write "to" or "then" instead of arrow symbols.
- No company names of training providers or employers as "us". Never name a client or employer. The material is generic.
- No invented statistics, quotes or studies. If you use a number, it must be a worked example you label as an example, or a fact you are sure of.
- Each lesson must give complete understanding of its topic: what it is, why it matters to an FDE, how it works step by step, a worked example, common mistakes, and how to check understanding.
- Length per lesson: 700 to 1200 words across sections (not counting links).
- Code must be correct and runnable as written (Python 3.11+, SQL that runs in SQLite, curl, JSON). Keep code blocks short (under 40 lines). Use placeholder keys like YOUR_API_KEY, never real secrets.

## Links (strict)

- Every link must be verified before you add it. Run:
  `python3 tools/verify_links.py URL1 URL2 ...` (from the project root)
  Only keep links that print `OK`. For YouTube the tool prints the real title and channel: use that exact title and channel name.
- Use the final URL if the tool shows a redirect.
- Udemy sometimes blocks the checker (HTTP 403). Retry once; if still blocked, leave that Udemy link out.
- Per lesson give 4 to 8 links, mixing: official documentation (MDN, Python docs, Git docs, SQLite docs, vendor docs such as platform.claude.com or code.claude.com), at least one YouTube video where a good one exists, and courses (Udemy, Coursera, DeepLearning.AI, Anthropic Academy, freeCodeCamp) or certifications where relevant.
- Prefer official and well-known sources. No blog spam, no aggregator sites.

## JSON shape

```json
{
  "module": 3,
  "title": "Building blocks: code, APIs, data and Git",
  "intro": "Two or three sentences on what this module gives the learner.",
  "lessons": [
    {
      "id": "how-the-web-works",
      "title": "How the web works",
      "summary": "One sentence: what you will understand after this lesson.",
      "why": "One short paragraph: why an FDE needs this on a client engagement.",
      "sections": [
        {"h": "The short version", "p": ["Paragraph.", "Paragraph."]},
        {"h": "Step by step", "p": ["Paragraph."], "list": ["Item one.", "Item two."]},
        {"h": "Going deeper", "p": ["Paragraph."], "code": {"lang": "bash", "text": "curl -i https://example.com"}}
      ],
      "diagram": { "type": "swimlane", "title": "What happens when you open a page", "caption": "One sentence explaining how to read it.",
                   "lanes": ["Browser", "DNS", "Server"],
                   "steps": [ {"lane": 0, "label": "You type a URL"}, {"lane": 1, "label": "Name resolved to an IP address"}, {"lane": 2, "label": "Server returns HTML"} ] },
      "example": {"title": "Worked example: reading a real response", "p": ["Paragraph."], "list": ["Step."], "code": {"lang": "text", "text": "HTTP/2 200"}},
      "practice": [
        {"title": "Inspect a real request", "time": "20 min", "goal": "See every part of an HTTP exchange yourself.",
         "steps": ["Open any website, then open the browser developer tools (F12) and the Network tab.", "Reload the page and click the first request.", "Write down the method, status code, two request headers and two response headers."],
         "done_when": "You can explain to a colleague what each value you wrote down means."}
      ],
      "pitfalls": ["Mistake and how to avoid it.", "Another."],
      "check": ["Question the learner should be able to answer.", "Another.", "Another."],
      "links": [
        {"type": "docs", "title": "Overview of HTTP", "source": "MDN Web Docs", "url": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview", "cost": "free"},
        {"type": "video", "title": "<exact title printed by the tool>", "source": "<channel>", "url": "https://www.youtube.com/watch?v=ID", "cost": "free"}
      ]
    }
  ]
}
```

Field notes:
- `sections`: 3 to 6 per lesson. Each has `h` and `p` (list of paragraphs); `list` and `code` are optional.
- `example`: required. `p` required; `list` and `code` optional.
- `practice`: required, 1 or 2 exercises per lesson. Each needs `title`, `time`, `goal`, `steps` (3 to 7 concrete actions a learner can do today with free tools: a browser, a free LLM chat such as Claude, Python, SQLite, GitHub, a spreadsheet, paper) and `done_when` (a checkable result). Practice is the most important part: the learner should finish the lesson and start doing the work.
- `pitfalls`: 3 to 5. `check`: 3 to 5 questions.
- Reading path: someone with basic understanding should be able to follow the lesson alone, then use the links to go deeper, then do the practice. Write the sections in that spirit: connect the idea to work they already know first, then build detail.
- `links[].type`: one of `docs`, `video`, `course`, `book`, `cert`. `cost`: `free` or `paid`.

## Diagram types (pick the one that explains the topic best; one per lesson)

- `flow`: a left-to-right sequence. `"steps": [{"label": "...", "note": "optional short note"}]` (3 to 8 steps).
- `cycle`: a repeating loop. Same `steps` shape (3 to 8). The last step returns to the first.
- `layers`: a stack, top to bottom. `"layers": [{"label": "...", "note": "..."}]` (3 to 7).
- `swimlane`: who does what, in order. `"lanes": ["A", "B", "C"]` (2 to 5) and `"steps": [{"lane": index, "label": "..."}]` in time order (4 to 12).
- `compare`: side-by-side options. `"columns": [{"title": "...", "items": ["...", "..."]}]` (2 to 4 columns, 3 to 6 items each).
- `branch`: a decision. `"question": "...", "branches": [{"answer": "...", "result": "..."}]` (2 to 4 branches), optional `"start": "..."` label before the question.

Labels: under 40 characters. Notes: under 70 characters.

## Before you finish

1. Validate the JSON: `python3 -c "import json;json.load(open('content/mNN.json'))"`.
2. Check ASCII: `python3 -c "d=open('content/mNN.json').read();print([c for c in set(d) if ord(c)>127])"` must print `[]`.
3. Re-run the link checker on every URL in your file and confirm all print OK.
