"""Short version as a self-study tutor: public/tldr.html (shell), public/tutor-data.json (steps, links, evidence fields, domains)."""
import json
from html import escape
from pathlib import Path

from site_nav import topbar, CHAT

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "public" / "tldr.html"
DATA = ROOT / "public" / "tutor-data.json"
DOMAINS = ROOT / "content" / "tutor.json"


def yt(vid):
    return f"https://www.youtube.com/watch?v={vid}"


def L(ty, title, src, url, cost="free", optional=False):
    """optional: a 'go further' resource; shown with the step but not counted in its required time."""
    return {"type": ty, "title": title, "source": src, "url": url, "cost": cost, **({"optional": True} if optional else {})}


# Minutes per resource: YouTube length, the course page's stated hours, or reading time (words / 200). None = self-paced, not stated.
MINUTES = {
 "LPZh9BOjkQs": 8, "about-claude/glossary": 8, "RGOj5yH7evk": 68, "D2cwvpJSBX4": 10, "Zyw-YA0k3xo": 51,
 "coursera.org/learn/ai-for-everyone": 420, "zjkBMFhNj_g": 60, "rfscVS0vtbw": 267, "GZvSYJDk-us": 140,
 "the-business-model-canvas": 5, "MT4Ig2uqjTc": 32, "c4model.com": 5, "top-10-for-large-language-model-applications": 5,
 "ysPbXH0LpIE": 25, "LP5OCa20Zpg": 18, "building-effective-agents": 14, "hamel.dev": 20, "fqMOX6JJhGo": 130,
 "1hHMwLxN6EM": 14, "develop-tests": 19, "5sLYAQS9sWQ": 6, "s7wmiS2mSXY": 3, "topics/context-window": 12,
 "data-privacy-vs-data-security": 8,
}


def minutes(url):
    for key, mins in MINUTES.items():
        if key in url:
            return mins
    return None


def F(fid, label, kind="long", min_words=0, need=""):
    """Evidence field. kind: long (textarea), text (one line), url. need: 'number' requires a digit."""
    return {"id": fid, "label": label, "kind": kind, "min_words": min_words, "need": need}


BROKE = F("broke", "What broke or confused you, and how you got past it (optional)", "long")

STEPS = [
 dict(num="A", slug="basics", title="The basics: what is what", when="Before week 1", page="learn/basics.html",
      what="What a model, an LLM, context and a harness are; Claude app versus API; open versus closed models; networks; data privacy and security.",
      links=[L("video", "Large Language Models explained briefly", "3Blue1Brown", yt("LPZh9BOjkQs")),
             L("video", "How Large Language Models Work", "IBM Technology", yt("5sLYAQS9sWQ")),
             L("video", "What is an API? (in 3 minutes)", "MuleSoft Videos", yt("s7wmiS2mSXY")),
             L("docs", "What is a context window?", "IBM", "https://www.ibm.com/think/topics/context-window"),
             L("docs", "Data privacy vs. data security: what is the core difference?", "Cloud Security Alliance", "https://cloudsecurityalliance.org/articles/data-privacy-vs-data-security-what-is-the-core-difference"),
             L("docs", "Glossary", "Claude Platform Docs", "https://platform.claude.com/docs/en/about-claude/glossary"),
             L("course", "Generative AI for Everyone", "DeepLearning.AI", "https://www.deeplearning.ai/courses/generative-ai-for-everyone/", optional=True),
             L("course", "Introduction to Generative AI", "Google Skills", "https://www.skills.google/course_templates/536", optional=True),
             L("course", "Introduction to generative AI and agents", "Microsoft Learn", "https://learn.microsoft.com/training/modules/fundamentals-generative-ai", optional=True),
             L("course", "Elements of AI", "University of Helsinki and MinnaLearn", "https://www.elementsofai.com/", optional=True)],
      task="Watch the three short videos and read the short pages above; each question below has a matching resource. Then answer the three questions in your own words. The courses marked optional go further when you have time.",
      done="You can explain, without notes: model versus app versus API, what context is, and privacy versus security.",
      fields=[F("explain", "What is the difference between a model, an app and an API?", min_words=15),
              F("context", "What does context mean for a model?", min_words=8),
              F("privacy", "How is privacy different from security?", min_words=10), BROKE]),
 dict(num="B", slug="setup", title="Set up your machine", when="Before week 1", page="learn/m00.html",
      what="Git, VS Code, Python and one AI coding assistant on your machine, working in your journal repository.",
      links=[L("video", "Git and GitHub for Beginners - Crash Course", "freeCodeCamp.org", yt("RGOj5yH7evk")),
             L("video", "Getting Started with Python in VS Code (Official Video)", "Visual Studio Code", yt("D2cwvpJSBX4"))],
      task="Install Git, VS Code, Python and one AI coding assistant. Copy your journal repository to your laptop and push one small change from there.",
      done="A commit made from your own machine is in your journal repository.",
      fields=[F("tools", "Which AI coding assistant did you set up?", "text", min_words=1),
              F("asked", "One thing you asked it to do", "text", min_words=5),
              F("commit_url", "Link to a commit you pushed from your machine", "url"), BROKE]),
 dict(num="01", slug="fde-role", title="The FDE role", when="Week 1", page="learn/m01.html",
      what="What a forward deployed engineer does: embed, discover, frame, design, build, evaluate, demo and hand over.",
      links=[L("video", "The FDE Playbook for AI Startups, with Bob McGrew", "Y Combinator", yt("Zyw-YA0k3xo")),
             L("course", "AI For Everyone", "DeepLearning.AI on Coursera", "https://www.coursera.org/learn/ai-for-everyone")],
      task="Watch the FDE video. Then answer three short questions about your project.",
      done="You can name the seven steps and say how an FDE differs from a consultant.",
      fields=[F("loop", "Who is the client in your project, and what is their problem?", min_words=10),
              F("first", "What would you build for them first?", min_words=10),
              F("vs_consultant", "How is an FDE different from a consultant?", min_words=10), BROKE]),
 dict(num="02", slug="llm-foundations", title="LLM foundations", when="Weeks 1-2", page="learn/m02.html",
      what="How LLMs produce text, tokens and cost, prompting, hallucination and grounding, responsible use.",
      links=[L("video", "Intro to Large Language Models (1 hour talk)", "Andrej Karpathy", yt("zjkBMFhNj_g")),
             L("course", "AI Fluency: Framework and Foundations", "Anthropic Academy", "https://anthropic.skilljar.com/ai-fluency-framework-foundations")],
      task="Pick one real task from your project. Ask an AI model to do it three times: once plainly, once with examples, and once with an exact output format. Write down what changed each time.",
      done="Your prompt log is saved and you hold the AI Fluency certificate.",
      fields=[F("prompt_log", "Your task, and what came back from the plain prompt", min_words=10),
              F("examples", "What changed when you added examples?", min_words=8),
              F("format", "What changed when you asked for an exact output format?", min_words=8),
              F("cert_url", "Link to your AI Fluency certificate", "url"), BROKE]),
 dict(num="03", slug="building-blocks", title="Building blocks: code, APIs, data, Git", when="Weeks 2-4", page="learn/m03.html",
      what="Enough Python, APIs, JSON, SQL and Git to build and read a small working tool.",
      links=[L("video", "Learn Python, full course for beginners", "freeCodeCamp", yt("rfscVS0vtbw")),
             L("video", "APIs for Beginners, how to use an API", "freeCodeCamp", yt("GZvSYJDk-us"))],
      task="Make some sample data for your project (made-up data is fine). Write a small script that loads it into a SQLite database and answers one useful question with SQL.",
      done="Someone else can run your script from its README.",
      fields=[F("code_url", "Link to the script in your repository", "url"),
              F("loads", "What data does it load?", "text", min_words=4),
              F("what_it_does", "What question does it answer, and what is the answer?", min_words=10), BROKE]),
 dict(num="04", slug="business", title="Domain, business and value", when="Weeks 3-4", page="learn/m04.html",
      what="How the business makes money, where its systems sit, and how to size the value of a change.",
      links=[L("docs", "The Business Model Canvas", "Strategyzer", "https://www.strategyzer.com/library/the-business-model-canvas"),
             L("course", "Business Analysis Fundamentals (IIBA endorsed)", "Udemy", "https://www.udemy.com/course/business-analysis-ba/", "paid")],
      task="Work out what your project is worth: how many cases a month, minutes saved per case, and cost per hour. Add any quality or risk benefit, and note where each number came from.",
      done="Every number in your business case points to where it came from.",
      fields=[F("inputs", "Cases a month, minutes saved per case, and cost per hour", "text", min_words=4, need="number"),
              F("case", "Value per month, and how you worked it out", min_words=8, need="number"),
              F("sources", "Where did each number come from?", min_words=10), BROKE]),
 dict(num="05", slug="discovery", title="Discovery and requirements", when="Weeks 5-6", page="learn/m05.html",
      what="Interviews about real past cases, a process map, and a one-page brief with acceptance criteria.",
      links=[L("video", "How to Talk to Users", "Y Combinator, Eric Migicovsky", yt("MT4Ig2uqjTc")),
             L("book", "The Mom Test", "Rob Fitzpatrick", "https://www.momtestbook.com/", "paid")],
      task="Talk to one person who does the work your project helps. Draw their process step by step, then write a one-page brief: the problem, today's numbers, the goal and what done looks like.",
      done="The person you interviewed agrees the map is how the work really happens.",
      fields=[F("who", "Who did you interview? (role, not name)", "text", min_words=2),
              F("map_url", "Link to your process map", "url"),
              F("brief", "The problem and today's numbers", min_words=12, need="number"),
              F("goal", "How will you know it works?", min_words=8),
              F("scope", "What is in scope, and what is not?", min_words=8),
              F("agreed", "How did they confirm the map?", "text", min_words=5), BROKE]),
 dict(num="06", slug="design", title="Solution design and options", when="Weeks 6-7", page="learn/m06.html",
      what="Automation levels, architecture, data flow, LLM security, model choice and cost, low-code or custom.",
      links=[L("docs", "The C4 model for software architecture diagrams", "c4model.com", "https://c4model.com/"),
             L("docs", "OWASP Top 10 for Large Language Model Applications", "OWASP", "https://owasp.org/www-project-top-10-for-large-language-model-applications/")],
      task="Write down three ways to build your project, including one without AI. Compare them on cost, risk and effort, estimate the monthly cost, and pick one.",
      done="You can defend your recommendation in two minutes, including when not to use AI.",
      fields=[F("options", "Your three options, one line each (one without AI)", min_words=15),
              F("recommendation", "Which one do you pick, and why?", min_words=10),
              F("cost", "Monthly cost estimate", "text", min_words=1, need="number"), BROKE]),
 dict(num="07", slug="build", title="Build the POC", when="Weeks 7-9", page="learn/m07.html",
      what="Prompts and structured output in code, tool use, retrieval, agents, MCP, and building with an AI coding assistant.",
      links=[L("video", "Prompting 101", "Anthropic", yt("ysPbXH0LpIE")),
             L("course", "Building with the Claude API", "Anthropic Academy", "https://anthropic.skilljar.com/claude-with-the-anthropic-api")],
      task="Build a first working version: it takes your sample data, uses an AI model the way you chose, and gives the result your brief asks for. Record a two-minute demo.",
      done="It runs end to end from the README, and a two-minute screen recording exists.",
      fields=[F("repo_url", "Link to the POC repository", "url"),
              F("recording_url", "Link to your two-minute screen recording", "url"),
              F("works", "What does it do today, end to end?", min_words=15), BROKE]),
 dict(num="08", slug="dependable", title="From demo to dependable", when="Weeks 8-9", page="learn/m08.html",
      what="Where AI belongs (code, model or human), designing for failure, safe rollout, portfolio and interviews.",
      links=[L("video", "Tips for building AI agents", "Anthropic", yt("LP5OCa20Zpg")),
             L("docs", "Building effective agents", "Anthropic Engineering", "https://www.anthropic.com/engineering/building-effective-agents")],
      task="Go through each step of your project and mark it as plain code, AI or a person. List the five most likely ways it can go wrong and how your project handles each one.",
      done="Every failure mode has a handling, and a one-page portfolio write-up exists.",
      fields=[F("map", "Which steps are plain code, which use AI, and which need a person?", min_words=15),
              F("failures", "Five ways it can go wrong, and how each is handled (one line each)", min_words=25),
              F("writeup_url", "Link to your one-page portfolio write-up", "url"), BROKE]),
 dict(num="09", slug="evaluate", title="Evaluate, deploy and operate", when="Weeks 9-10", page="learn/m09.html",
      what="Evaluation sets, pass rates, human review gates, deployment, secrets and observability.",
      links=[L("docs", "Your AI product needs evals", "Hamel Husain", "https://hamel.dev/blog/posts/evals/"),
             L("video", "Docker tutorial for beginners, full DevOps course", "freeCodeCamp", yt("fqMOX6JJhGo"))],
      task="Make a test set of 30 real-looking cases with the right answers. Run your project on them, fix the biggest problem, and put it online behind a login.",
      done="You have a before and after pass rate and a live URL.",
      fields=[F("pass_rate", "Pass rate before and after, for example 31/40 then 36/40", "text", need="number"),
              F("top_failure", "What was the top failure, and what did you change?", min_words=12),
              F("live_url", "Live URL of the deployed POC", "url"), BROKE]),
 dict(num="10", slug="demo", title="Demo and hand-over", when="Week 10", page="learn/m10.html",
      what="A demo that starts from the problem, the path from POC to pilot, and a hand-over pack someone else can run.",
      links=[L("video", "How to Plan an MVP", "Y Combinator, Michael Seibel", yt("1hHMwLxN6EM")),
             L("book", "INSPIRED: How to Create Tech Products Customers Love", "Marty Cagan, SVPG", "https://www.svpg.com/books/inspired-how-to-create-tech-products-customers-love-2nd-edition/", "paid")],
      task="Show your project in a ten-minute demo to someone acting as the client. Write a short hand-over guide and ask someone else to run it from your README.",
      done="Someone outside your pair ran the POC from your README alone.",
      fields=[F("demo_url", "Link to your demo recording", "url"),
              F("handover_url", "Link to your hand-over pack", "url"),
              F("tester", "Who ran it from the README (role), and what happened?", "text", min_words=6), BROKE]),
 dict(num="11", slug="capstone", title="Final project", when="Weeks 11-12", page="learn/m11.html",
      what="One client, one POC, end to end, with a mentor playing the client.",
      links=[L("video", "The FDE Playbook for AI Startups, with Bob McGrew", "Y Combinator", yt("Zyw-YA0k3xo")),
             L("docs", "Define success criteria and build evaluations", "Claude Platform Docs", "https://platform.claude.com/docs/en/test-and-evaluate/develop-tests")],
      task="Run the whole loop on your project with a mentor playing the client, then present it to the review panel.",
      done="The panel scores you FDE-ready in discovery, build quality, evaluation and safety, and communication.",
      fields=[F("capstone_url", "Link to your final project folder or repository", "url"),
              F("panel", "Panel result and the feedback you got", min_words=12), BROKE]),
]

CERTS = [
 ("Anthropic Academy certificates", "Claude API, Claude Code and MCP courses.", "https://anthropic.skilljar.com/"),
 ("AWS Certified AI Practitioner", "Paid exam. Or the matching one for your cloud.", "https://aws.amazon.com/certification/certified-ai-practitioner/"),
 ("Microsoft Azure AI Fundamentals", "Paid exam. For teams on Azure.", "https://learn.microsoft.com/en-us/credentials/certifications/azure-ai-fundamentals/"),
 ("Google Cloud Generative AI Leader", "Paid exam. Business-level generative AI.", "https://cloud.google.com/learn/certification/generative-ai-leader"),
 ("IIBA ECBA", "Paid exam. Business analysis basics, good for software people.", "https://www.iiba.org/business-analysis-certifications/ecba/"),
 ("GitHub certifications", "Paid exam. Good for domain people building technical skills.", "https://docs.github.com/en/get-started/showcase-your-expertise-with-github-certifications/about-github-certifications"),
]


def page():
    certs = "".join(f'<li><a href="{escape(u)}" target="_blank" rel="noopener">{escape(n)}</a><span>{escape(d)}</span></li>' for n, d, u in CERTS)
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>FDE Path Tutor</title>
<meta name="description" content="Pick your domain and a project, then build it step by step. Evidence is saved to your own GitHub repository and checked by the tutor.">
<meta name="referrer" content="no-referrer">
<script src="theme.js"></script>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Familjen+Grotesk:wght@500;600;700&family=Atkinson+Hyperlegible:wght@400;700&family=IBM+Plex+Mono:wght@500&display=swap">
<link rel="stylesheet" href="style.css"></head>
<body class="tldr"{' data-chat="1"' if CHAT else ""}>
{topbar("", (("Practice", None), ("Learning path", None)), "practice", "tldr")}
<main class="t-main">
  <header class="t-head">
    <p class="kicker">FDE training program / learning path / 12 weeks</p>
    <h1>From engineer or domain expert to forward deployed engineer.</h1>
    <p class="lede">Your own path through the program: pick your industry and one real project, choose how to build it, and work through 13 steps over 12 weeks. Each step saves evidence to your GitHub repository and the tutor checks it, so anyone you share it with can see exactly what you have done.</p>
    <ol class="t-how"><li><b>Connect</b>GitHub journal</li><li><b>Choose</b>domain and project</li><li><b>Decide</b>how to build it</li><li><b>Build</b>13 steps with evidence</li><li><b>Prove</b>progress in your repo</li></ol>
  </header>

  <section class="t-panel t-setup" id="accounts">
    <h2><span>0</span>Two accounts to set up first</h2>
    <p class="t-note">Set these up once before step 1. They make your learning easier to track and give you a real place to build, host and test your work.</p>
    <div class="t-acc">
      <div><h3>GitHub</h3><p>Your learning journal lives here: your project, the evidence for each step, and your progress. Your mentor opens one link to see where you are, and every project you build is saved with its history.</p>
        <a class="open" href="https://docs.github.com/en/get-started/start-your-journey/creating-an-account-on-github" target="_blank" rel="noopener">Create a GitHub account</a></div>
      <div><h3>Cloudflare</h3><p>A place to host the pages and small apps you build, and to run AI models on Workers AI while you practise. The account plan you sign up with covers the exercises in this course.</p>
        <a class="open" href="https://developers.cloudflare.com/fundamentals/account/create-account/" target="_blank" rel="noopener">Create a Cloudflare account</a></div>
    </div>
  </section>

  <section class="t-panel" id="connect">
    <h2><span>1</span>Journal tracker<em class="t-badge" id="badge-connect"></em></h2>
    <div id="gh-box"><p class="t-note">Loading...</p></div>
    <div id="cf-box"></div>
  </section>

  <section class="t-panel" id="project">
    <h2><span>2</span>Domain and project<em class="t-badge" id="badge-project"></em></h2>
    <div id="project-box"></div>
  </section>

  <section class="t-panel" id="decide">
    <h2><span>3</span>How to build it<em class="t-badge" id="badge-decide"></em></h2>
    <p class="t-note">Answer six questions. The guide recommends a setup; you write why it fits. This goes into your project file, so your choices stay accountable.</p>
    <div id="decide-box"></div>
  </section>

  <section class="t-panel" id="path">
    <h2><span>4</span>The 13 steps<em class="t-badge" id="badge-path"></em></h2>
    <div class="cp-tldr" data-progress></div>
    <div id="summary-box"></div>
    <div id="steps-box"></div>
    <p class="t-closing">This is a basic tracker for accountability. It counts what you save and commit, not how good the work is. You own your learning; your mentor's review is what counts.</p>
  </section>

  <section class="t-panel t-certs">
    <h2>Certificates worth having</h2>
    <p class="t-note">Optional. They never replace the final project. Start with the Anthropic Academy ones, then one paid exam that matches your clients' cloud or your gap.</p>
    <ul>{certs}</ul>
    <p class="t-note">Want more depth? <a href="crash-course.html">Crash course library</a> / <a href="index.html">Full program</a> / <a href="learn/basics.html">The basics</a> / <a href="learn/m00.html">Set up your machine</a></p>
  </section>
</main>
<script src="progress.js" defer></script>
<script type="module" src="tutor.js"></script>
</body></html>
'''


# Crash course area that goes deeper for each step.
STEP_AREA = {"basics": ("ai", "AI, ML and LLMs"), "setup": ("programming", "Programming"), "fde-role": ("business", "FDE role and business skills"),
             "llm-foundations": ("ai", "AI, ML and LLMs"), "building-blocks": ("programming", "Programming"), "business": ("business", "FDE role and business skills"),
             "discovery": ("business", "FDE role and business skills"), "design": ("security", "Security and privacy"), "build": ("ai", "AI, ML and LLMs"),
             "dependable": ("cloud", "Cloud and DevOps"), "evaluate": ("cloud", "Cloud and DevOps"),
             "demo": ("business", "FDE role and business skills"), "capstone": ("ai", "AI, ML and LLMs")}


def build():
    for st in STEPS:
        st["crash"] = list(STEP_AREA.get(st["slug"], ("", "")))
        for l in st["links"]:
            l["mins"] = minutes(l["url"])
    domains = json.loads(DOMAINS.read_text(encoding="utf-8")) if DOMAINS.exists() else {"industries": []}
    import learn
    mods = [{"file": m["file"], "title": m["title"]} for m in learn.load_modules() if (ROOT / "content" / "quiz" / f'{m["file"]}.json').exists()]
    DATA.write_text(json.dumps({"steps": STEPS, "industries": domains["industries"], "modules": mods}, ensure_ascii=True), encoding="ascii")
    OUT.write_text(page(), encoding="ascii")
    return OUT


def urls():
    return sorted({l["url"] for s in STEPS for l in s["links"]} | {c[2] for c in CERTS})


if __name__ == "__main__":
    print(build())
