# FDE Training Program

A self-paced program for becoming a forward deployed engineer (FDE): the person who sits with a client, finds the real problem, and builds an AI solution that works in their systems.

**Live site:** https://fde-training-program.pages.dev

It is for engineers who want to learn the business side, and for domain experts (quality, regulatory, operations, R&D) who want to learn to build with AI. It covers how AI really works, how to use it effectively, securely and at low cost, and how to read an industry so you know where AI helps.

## What is in it

| Part | Where | What you get |
|---|---|---|
| Start here | [learn/basics.html](https://fde-training-program.pages.dev/learn/basics.html) | Plain definitions of AI, models, context, APIs, networks, privacy and security, with a quick check |
| Languages and AI SDKs | [learn/languages.html](https://fde-training-program.pages.dev/learn/languages.html) | Which language to use and why, one common pattern for calling any model provider, and a playlist for every major language and DevOps tool |
| Modules 00 to 11 | [learn/m01.html](https://fde-training-program.pages.dev/learn/m01.html) and on | Lessons with diagrams, worked examples, practice and links; a 20-question test at the end of each module (pass at 80 percent) |
| Learning path | [tldr.html](https://fde-training-program.pages.dev/tldr.html) | 13 steps that take one real project from idea to hand-over, with evidence saved to your own GitHub repository and an AI tutor that reviews it |
| Crash course | [crash-course.html](https://fde-training-program.pages.dev/crash-course.html) | Hundreds of curated videos, docs and courses by topic, for going deeper |
| Ask | The Ask button on every page | Answers from this program's content, from the [AI knowledge chat service](https://quick-chat-program.pages.dev) |

## How to learn with it

1. Read **Start here** and pass its quick check. It takes about an hour.
2. Set up your machine and your learning journal (module 00). The journal is a GitHub repository where your progress and evidence live.
3. Work through modules 01 to 11 in order. Read each lesson, do the practice, then pass the module test.
4. In parallel, follow the **learning path**. Pick an industry and a project, then complete the 13 steps. Each step lists what to do, the resources to use and when it counts as done. "Ask the tutor" gives feedback on your evidence.
5. Use the **crash course** and the **languages playlist** whenever a topic is new to you.

Progress (tests passed, setup check, practice ticks) is kept in your browser. Evidence and step progress are saved to your journal repository on GitHub, so a mentor can see exactly what you have done.

You can also follow the path from a terminal. Download `fde.py` from the learning path page into your journal repository, then run `python3 fde.py help`.

## Run it locally

You need Python 3.10 or newer, Node.js 18 or newer (for `npx wrangler`), git and curl.

```bash
git clone https://github.com/Elamurugan-Nallathambi/fde-training.git
```

```bash
cd fde-training && ./setup.sh setup
```

That builds the site into `public/` and serves it at http://127.0.0.1:4321. Other commands: `./setup.sh start | stop | status | logs | build | check | deploy | help`.

The GitHub sign-in, the AI tutor and the Cloudflare connect use Cloudflare Pages Functions (`functions/`). To run those locally too, use `npx wrangler pages dev public` and put local values in `.dev.vars` (never committed).

## How it is built

Content is JSON; Python turns it into a static site.

| Path | What it is |
|---|---|
| `content/` | Lessons (`m00.json` to `m11.json`), the basics, module tests (`quiz/`), help answers (`faq.json`), the learning playlist, crash course library (`library/*.csv`), industry tracks (`variants/`) and topic courses (`topics/`) |
| `content/SCHEMA.md` | The lesson format and writing rules every lesson follows |
| `build.py`, `learn.py`, `tldr.py`, `crash.py` | Build the program page, lesson pages, learning path and crash course into `public/` |
| `public/` | The built site, plus the browser scripts (tutor, tests, progress, code highlighting) |
| `functions/`, `lib/` | Cloudflare Pages Functions: GitHub sign-in, AI tutor feedback, Cloudflare connect |
| `tools/` | Checks for content and links, and the exporter that turns courses into LMS packages |

To change content, edit the JSON in `content/`, then run `./setup.sh build` and `./setup.sh check`. Every link is verified with `python3 tools/verify_links.py URL ...`, and topic courses must pass `python3 tools/check_topic.py content/topics/*.json`.

## Deploy your own copy

Copy `.env.example` to `.env` and set your Cloudflare account id and Pages project name, then run `./setup.sh deploy`. Set these as Pages secrets in your Cloudflare project, never in code:

| Setting | Used for |
|---|---|
| `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET` | GitHub sign-in for the learning journal (a GitHub OAuth app) |
| `CF_OAUTH_CLIENT_ID`, `CF_OAUTH_CLIENT_SECRET`, `CF_OAUTH_SCOPES`, `CF_AI_MODEL` | Optional: learners connect their own Cloudflare account for AI answers |

The AI tutor uses the Workers AI binding in `wrangler.toml`.

## Related

- [Simple RAG via a browser model](https://github.com/Elamurugan-Nallathambi/simple-rag-via-browser-model): the Ask chat (knowledge graph, browser-side search model and read-only API), built from this content.
