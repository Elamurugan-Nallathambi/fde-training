#!/usr/bin/env python3
"""Builds the FDE training program page (public/index.html). Every external link here was verified on 2026-10-19."""
from html import escape
from pathlib import Path

import learn
import tldr
import crash
from site_nav import topbar

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "public"

def yt(vid): return f"https://www.youtube.com/watch?v={vid}"

# type: video | course | docs | book | cert ; cost: free | paid ; track: A (software background), B (domain/business background), both
R = {
 "fde-playbook": ("video", "The FDE Playbook for AI Startups, with Bob McGrew", "Y Combinator", yt("Zyw-YA0k3xo"), "free"),
 "agentic-ng": ("video", "What's next for AI agentic workflows, with Andrew Ng", "Sequoia Capital", yt("sal78ACtGTc"), "free"),
 "effective-agents": ("docs", "Building effective agents", "Anthropic Engineering", "https://www.anthropic.com/engineering/building-effective-agents", "free"),
 "genai-everyone": ("course", "Generative AI for Everyone", "DeepLearning.AI on Coursera", "https://www.coursera.org/learn/generative-ai-for-everyone", "free"),
 "ai-everyone": ("course", "AI For Everyone", "DeepLearning.AI on Coursera", "https://www.coursera.org/learn/ai-for-everyone", "free"),
 "karpathy-intro": ("video", "Intro to Large Language Models (1 hour talk)", "Andrej Karpathy", yt("zjkBMFhNj_g"), "free"),
 "karpathy-deep": ("video", "Deep Dive into LLMs like ChatGPT", "Andrej Karpathy", yt("7xTGNNLPyMI"), "free"),
 "karpathy-use": ("video", "How I use LLMs", "Andrej Karpathy", yt("EWvNQjAaOHw"), "free"),
 "3b1b-brief": ("video", "Large Language Models explained briefly", "3Blue1Brown", yt("LPZh9BOjkQs"), "free"),
 "3b1b-transformers": ("video", "Transformers, the tech behind LLMs", "3Blue1Brown", yt("wjZofJX0v4M"), "free"),
 "ibm-rag": ("video", "What is Retrieval-Augmented Generation (RAG)?", "IBM Technology", yt("T-D1OfcDW1M"), "free"),
 "ai-fluency": ("course", "AI Fluency: Framework and Foundations", "Anthropic Academy", "https://anthropic.skilljar.com/ai-fluency-framework-foundations", "free"),
 "google-genai": ("course", "Beginner: Introduction to Generative AI (learning path)", "Google Skills", "https://www.cloudskillsboost.google/paths/118", "free"),
 "cs50x": ("course", "CS50x: Introduction to Computer Science", "Harvard", "https://cs50.harvard.edu/x/", "free"),
 "cs50sql": ("course", "CS50's Introduction to Databases with SQL", "Harvard", "https://cs50.harvard.edu/sql/", "free"),
 "missing": ("course", "The Missing Semester of Your CS Education", "MIT", "https://missing.csail.mit.edu/", "free"),
 "mdn-web": ("docs", "How the web works", "MDN Web Docs", "https://developer.mozilla.org/en-US/docs/Learn_web_development/Getting_started/Web_standards/How_the_web_works", "free"),
 "fcc-intro": ("video", "Introduction to Programming and Computer Science", "freeCodeCamp", yt("zOjov-2OZ0E"), "free"),
 "fcc-python": ("video", "Learn Python, full course for beginners", "freeCodeCamp", yt("rfscVS0vtbw"), "free"),
 "mosh-python": ("video", "Python for Beginners in 1 hour", "Programming with Mosh", yt("kqtD5dpn9C8"), "free"),
 "dlai-python": ("course", "AI Python for Beginners", "DeepLearning.AI", "https://www.deeplearning.ai/courses/ai-python-for-beginners", "free"),
 "fcc-apis": ("video", "APIs for Beginners, how to use an API", "freeCodeCamp", yt("GZvSYJDk-us"), "free"),
 "fcc-sql": ("video", "SQL Tutorial, full database course for beginners", "freeCodeCamp", yt("HXV3zeQKqGY"), "free"),
 "fcc-git": ("video", "Git and GitHub for Beginners, crash course", "freeCodeCamp", yt("RGOj5yH7evk"), "free"),
 "fireship-web": ("video", "100+ Web Development Things you Should Know", "Fireship", yt("erEgovG9WBs"), "free"),
 "gh-hello": ("docs", "Hello World on GitHub", "GitHub Docs", "https://docs.github.com/en/get-started/using-github/hello-world", "free"),
 "udemy-git": ("course", "The Git and GitHub Bootcamp", "Udemy, Colt Steele", "https://www.udemy.com/course/git-and-github-bootcamp/", "paid"),
 "yc-ideas": ("video", "How to Get and Evaluate Startup Ideas", "Y Combinator", yt("Th8JoIan4dg"), "free"),
 "bmc": ("docs", "The Business Model Canvas", "Strategyzer", "https://www.strategyzer.com/library/the-business-model-canvas", "free"),
 "vpc": ("docs", "The Value Proposition Canvas", "Strategyzer", "https://www.strategyzer.com/library/the-value-proposition-canvas", "free"),
 "market-research": ("course", "Market Research and Consumer Behavior", "IE Business School on Coursera", "https://www.coursera.org/learn/market-research", "free"),
 "google-data": ("cert", "Google Data Analytics Professional Certificate", "Google on Coursera", "https://www.coursera.org/professional-certificates/google-data-analytics", "paid"),
 "babok": ("docs", "BABOK Guide, business analysis standard of practice", "IIBA", "https://www.iiba.org/career-resources/a-business-analysis-professionals-foundation-for-success/babok/", "paid"),
 "udemy-ba": ("course", "Business Analysis Fundamentals (IIBA endorsed)", "Udemy", "https://www.udemy.com/course/business-analysis-ba/", "paid"),
 "rm-pm": ("docs", "Product Manager roadmap", "roadmap.sh", "https://roadmap.sh/product-manager", "free"),
 "yc-users": ("video", "How to Talk to Users", "Y Combinator, Eric Migicovsky", yt("MT4Ig2uqjTc"), "free"),
 "momtest": ("book", "The Mom Test", "Rob Fitzpatrick", "https://www.momtestbook.com/", "paid"),
 "cdh": ("book", "Continuous Discovery Habits", "Teresa Torres", "https://www.producttalk.org/continuous-discovery-habits/", "paid"),
 "bpmn": ("docs", "BPMN, business process model and notation", "Object Management Group", "https://www.bpmn.org/", "free"),
 "stories": ("docs", "User stories with examples and a template", "Atlassian", "https://www.atlassian.com/agile/project-management/user-stories", "free"),
 "raci": ("docs", "RACI chart: what it is and how to use it", "Atlassian", "https://www.atlassian.com/work-management/project-management/raci-chart", "free"),
 "adkar": ("docs", "The ADKAR change management model", "Prosci", "https://www.prosci.com/methodology/adkar", "free"),
 "udemy-pm": ("course", "Become a Product Manager: learn the skills, get the job", "Udemy", "https://www.udemy.com/course/become-a-product-manager-learn-the-skills-get-the-job/", "paid"),
 "c4": ("docs", "The C4 model for software architecture diagrams", "c4model.com", "https://c4model.com/", "free"),
 "12factor": ("docs", "The Twelve-Factor App", "12factor.net", "https://12factor.net/", "free"),
 "owasp-llm": ("docs", "OWASP Top 10 for Large Language Model Applications", "OWASP", "https://owasp.org/www-project-top-10-for-large-language-model-applications/", "free"),
 "context-eng": ("docs", "Effective context engineering for AI agents", "Anthropic Engineering", "https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents", "free"),
 "openai-agents": ("docs", "A practical guide to building agents (PDF)", "OpenAI", "https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf", "free"),
 "n8n": ("docs", "n8n documentation (low-code workflow automation)", "n8n", "https://docs.n8n.io/", "free"),
 "claude-api": ("course", "Building with the Claude API", "Anthropic Academy", "https://anthropic.skilljar.com/claude-with-the-anthropic-api", "free"),
 "claude-code-course": ("course", "Claude Code in Action", "Anthropic Academy", "https://anthropic.skilljar.com/claude-code-in-action", "free"),
 "mcp-course": ("course", "Introduction to Model Context Protocol", "Anthropic Academy", "https://anthropic.skilljar.com/introduction-to-model-context-protocol", "free"),
 "anthropic-courses": ("course", "Anthropic courses on GitHub (API, prompting, tool use)", "Anthropic", "https://github.com/anthropics/courses", "free"),
 "prompt-tutorial": ("course", "Interactive prompt engineering tutorial", "Anthropic", "https://github.com/anthropics/prompt-eng-interactive-tutorial", "free"),
 "prompting-101": ("video", "Prompting 101", "Anthropic, Code w/ Claude", yt("ysPbXH0LpIE"), "free"),
 "agent-tips": ("video", "Tips for building AI agents", "Anthropic", yt("LP5OCa20Zpg"), "free"),
 "cc-30": ("video", "Mastering Claude Code in 30 minutes", "Anthropic", yt("6eBSHbLKuN0"), "free"),
 "dlai-agentic": ("course", "Agentic AI, with Andrew Ng", "DeepLearning.AI", "https://www.deeplearning.ai/courses/agentic-ai", "free"),
 "dlai-mcp": ("course", "MCP: Build Rich-Context AI Apps with Anthropic", "DeepLearning.AI", "https://learn.deeplearning.ai/courses/mcp-build-rich-context-ai-apps-with-anthropic", "free"),
 "dlai-cc": ("course", "Claude Code: A Highly Agentic Coding Assistant", "DeepLearning.AI", "https://www.deeplearning.ai/courses/claude-code-a-highly-agentic-coding-assistant", "free"),
 "dlai-prompt": ("course", "ChatGPT Prompt Engineering for Developers", "DeepLearning.AI", "https://www.deeplearning.ai/courses/chatgpt-prompt-eng", "free"),
 "prompt-docs": ("docs", "Prompt engineering overview", "Claude Platform Docs", "https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview", "free"),
 "cc-docs": ("docs", "Claude Code overview", "Claude Code Docs", "https://code.claude.com/docs/en/overview", "free"),
 "cc-best": ("docs", "Best practices for Claude Code", "Claude Code Docs", "https://code.claude.com/docs/en/best-practices", "free"),
 "mcp-site": ("docs", "What is the Model Context Protocol?", "modelcontextprotocol.io", "https://modelcontextprotocol.io/", "free"),
 "cursor": ("docs", "Cursor documentation", "Cursor", "https://cursor.com/docs", "free"),
 "copilot": ("docs", "GitHub Copilot documentation", "GitHub Docs", "https://docs.github.com/en/copilot", "free"),
 "rm-ai": ("docs", "AI Engineer roadmap", "roadmap.sh", "https://roadmap.sh/ai-engineer", "free"),
 "evals-hamel": ("docs", "Your AI product needs evals", "Hamel Husain", "https://hamel.dev/blog/posts/evals/", "free"),
 "evals-claude": ("docs", "Define success criteria and build evaluations", "Claude Platform Docs", "https://platform.claude.com/docs/en/test-and-evaluate/develop-tests", "free"),
 "dlai-evals": ("course", "Evaluating AI Agents", "DeepLearning.AI", "https://www.deeplearning.ai/courses/evaluating-ai-agents", "free"),
 "langfuse": ("docs", "Langfuse documentation (LLM tracing and evaluation)", "Langfuse", "https://langfuse.com/docs", "free"),
 "fcc-docker": ("video", "Docker tutorial for beginners, full DevOps course", "freeCodeCamp", yt("fqMOX6JJhGo"), "free"),
 "udemy-docker": ("course", "Docker and Kubernetes: The Practical Guide", "Udemy", "https://www.udemy.com/course/docker-kubernetes-the-practical-guide/", "paid"),
 "cf-pages": ("docs", "Cloudflare Pages overview", "Cloudflare Docs", "https://developers.cloudflare.com/pages/", "free"),
 "gh-actions": ("docs", "GitHub Actions documentation", "GitHub Docs", "https://docs.github.com/en/actions", "free"),
 "sre": ("book", "Site Reliability Engineering (free online book)", "Google", "https://sre.google/sre-book/table-of-contents/", "free"),
 "rm-devops": ("docs", "DevOps roadmap", "roadmap.sh", "https://roadmap.sh/devops", "free"),
 "yc-mvp": ("video", "How to Plan an MVP", "Y Combinator, Michael Seibel", yt("1hHMwLxN6EM"), "free"),
 "inspired": ("book", "INSPIRED: How to Create Tech Products Customers Love", "Marty Cagan, SVPG", "https://www.svpg.com/books/inspired-how-to-create-tech-products-customers-love-2nd-edition/", "paid"),
 "spm": ("course", "Software Product Management specialization", "University of Alberta on Coursera", "https://www.coursera.org/specializations/product-management", "paid"),
 "google-pm": ("cert", "Google Project Management Professional Certificate", "Google on Coursera", "https://www.coursera.org/professional-certificates/google-project-management", "paid"),
}

CERTS = [
 ("Anthropic Academy course certificates", "Anthropic", "Everyone. Completion certificates for Claude API, Claude Code and MCP courses.", "https://anthropic.skilljar.com/", "Course certificate", "free", "both"),
 ("AWS Certified AI Practitioner (AIF-C01)", "Amazon Web Services", "Domain track. Foundational AI and generative AI concepts on AWS.", "https://aws.amazon.com/certification/certified-ai-practitioner/", "Proctored exam", "paid", "B"),
 ("AWS Certified Cloud Practitioner (CLF-C02)", "Amazon Web Services", "Domain track. Cloud basics, pricing, security model.", "https://aws.amazon.com/certification/certified-cloud-practitioner/", "Proctored exam", "paid", "B"),
 ("Microsoft Certified: Azure AI Fundamentals", "Microsoft", "Either track, for teams working on Azure.", "https://learn.microsoft.com/en-us/credentials/certifications/azure-ai-fundamentals/", "Proctored exam", "paid", "both"),
 ("Google Cloud Generative AI Leader", "Google Cloud", "Either track. Business-level generative AI strategy and adoption.", "https://cloud.google.com/learn/certification/generative-ai-leader", "Proctored exam", "paid", "both"),
 ("Professional Scrum Product Owner I (PSPO I)", "Scrum.org", "Software track. Product ownership and backlog value.", "https://www.scrum.org/assessments/professional-scrum-product-owner-i-certification", "Online assessment", "paid", "A"),
 ("Certified Scrum Product Owner (CSPO)", "Scrum Alliance", "Alternative to PSPO I, course-based.", "https://www.scrumalliance.org/get-certified/product-owner-track/certified-scrum-product-owner", "Course + certificate", "paid", "A"),
 ("Entry Certificate in Business Analysis (ECBA)", "IIBA", "Software track. Requirements and business analysis fundamentals.", "https://www.iiba.org/business-analysis-certifications/ecba/", "Proctored exam", "paid", "A"),
 ("PMI Certified Professional in Managing AI (PMI-CPMAI)", "Project Management Institute", "Either track, for people who will lead AI delivery.", "https://www.pmi.org/certifications/ai-project-management-cpmai", "Proctored exam", "paid", "both"),
 ("GitHub certifications (Foundations, Copilot)", "GitHub", "Domain track. Version control and AI-assisted coding.", "https://resources.github.com/learn/certifications/", "Proctored exam", "paid", "B"),
 ("Databricks Certified Generative AI Engineer Associate", "Databricks", "Software track, advanced. Building LLM applications on a data platform.", "https://www.databricks.com/learn/certification/genai-engineer-associate", "Proctored exam", "paid", "A"),
]

CONCEPTS = [
 ("Technology", [
  ("How the web works", "Client, server, DNS, HTTP request and response, status codes.", "B"),
  ("APIs and JSON", "Call a REST API, read the docs, handle auth headers and errors.", "B"),
  ("Data and SQL", "Tables, keys, joins; write a SELECT with a WHERE and a JOIN.", "B"),
  ("Files and formats", "CSV, JSON, PDF, spreadsheets; what is structured vs unstructured.", "both"),
  ("Identity and access", "Authentication vs authorization, SSO, OAuth, API keys, least privilege.", "both"),
  ("Data protection", "PII, data residency, retention, what may leave the client's boundary.", "both"),
  ("Systems of record", "What ERP, CRM, PLM, QMS, HRIS and ticketing systems hold and who owns them.", "A"),
 ]),
 ("AI and LLMs", [
  ("Tokens, context and cost", "Why long prompts cost more and how context windows limit a task.", "both"),
  ("Prompting", "Roles, instructions, examples, structured output, and asking the model to reason.", "both"),
  ("Hallucination and grounding", "Why models invent facts and how retrieval and citations reduce it.", "both"),
  ("Embeddings and RAG", "Search over your own documents and feed the results to the model.", "both"),
  ("Tool use and agents", "The model calls functions, reads results and decides the next step.", "both"),
  ("MCP", "A standard way to connect models to tools and data sources.", "both"),
  ("Evaluation", "A test set with expected answers, a pass rate, and failure review.", "both"),
  ("Model choice", "Frontier API vs smaller or self-hosted models, by accuracy, cost, latency and data rules.", "A"),
 ]),
 ("Development", [
  ("Reading code", "Follow a function, find where data comes from, explain it in plain words.", "B"),
  ("Python or TypeScript basics", "Variables, functions, loops, packages, running a script.", "B"),
  ("Git and GitHub", "Clone, branch, commit, pull request, review.", "B"),
  ("AI-assisted coding", "Use Claude Code, Cursor or Copilot to plan, write, test and explain code.", "both"),
  ("Testing and debugging", "Reproduce a bug, read an error, write a small test.", "B"),
  ("Environments and secrets", "Local, test, production; keep keys out of code.", "B"),
 ]),
 ("Deployment", [
  ("Hosting options", "Static pages, serverless functions, containers, managed platforms.", "B"),
  ("Containers", "What a Docker image is and why it makes deployment repeatable.", "B"),
  ("CI/CD", "Automatic test and deploy on every change.", "both"),
  ("Logging and monitoring", "Traces, errors, latency, cost per request, alerting.", "both"),
  ("Security review basics", "Prompt injection, data leakage, access scope, audit trail.", "both"),
 ]),
 ("Product ownership", [
  ("Outcomes over outputs", "Define success as a business measure, not a feature list.", "A"),
  ("POC vs pilot vs production", "What each proves, who uses it, and what it must survive.", "both"),
  ("User stories and acceptance criteria", "Write who, what, why, and how we know it is done.", "A"),
  ("Prioritization", "Value vs effort, quick wins first, say no clearly.", "A"),
  ("Backlog and scope control", "Keep a visible list; trade scope, not quality or dates.", "A"),
 ]),
 ("Client requirements", [
  ("Discovery interviews", "Ask about the last real case, not opinions about the future.", "A"),
  ("Process mapping", "Draw steps, roles, systems, handoffs and exceptions as a swimlane.", "both"),
  ("Shadowing", "Watch real work end to end; note copy-paste, waiting and workarounds.", "both"),
  ("Stakeholder mapping", "Sponsor, owner, users, IT, security, compliance; RACI.", "A"),
  ("Writing a one-page brief", "Problem, users, data, constraints, success measure, open questions.", "both"),
  ("Change and adoption", "Why people resist, and how to bring the process owner along.", "A"),
 ]),
 ("Market and business analysis", [
  ("Industry value chain", "How the client makes money and where cost and delay sit.", "A"),
  ("Business case", "Volume x time saved x loaded cost, plus quality and risk effects.", "A"),
  ("Build, buy or configure", "When an existing product beats a custom build.", "both"),
  ("Vendor and competitor scan", "Who else solves this, and how the client would compare options.", "A"),
  ("Business model canvas", "Customers, value, channels, cost and revenue on one page.", "A"),
 ]),
]

MODULES = [
 dict(n=1, wk="Week 1", title="The FDE role and the AI landscape", track="both", hours="18-24 h",
      goal="Understand what a forward deployed engineer does, why companies hire them, and how the program runs.",
      topics=["The FDE loop: embed, discover, design, build, evaluate, demo, hand over", "FDE vs consultant vs solutions engineer vs product engineer", "Where AI projects fail: pilots that never reach production", "Ways of working: pairs, weekly rhythm, using AI as a tutor"],
      lab="Pair up (one software, one domain background). Interview each other on a process you know well and write a one-paragraph problem statement.",
      out="A half page in your journal on the FDE loop applied to your own work.",
      res=["fde-playbook", "agentic-ng", "effective-agents", "genai-everyone"]),
 dict(n=2, wk="Weeks 1-2", title="LLM foundations and AI fluency", track="both", hours="24-30 h",
      goal="Explain how LLMs work, where they fail, and how to use them well in daily work.",
      topics=["Tokens, context windows, temperature, cost", "Prompting patterns and structured output", "Hallucination, grounding and citations", "RAG, tools and agents at a conceptual level", "Responsible use: data, privacy, bias, human review"],
      lab="Take one messy real document (policy, contract, SOP). Use an LLM to summarize, extract fields into JSON and answer 10 questions. Record where it was wrong and why.",
      out="A prompt log with 10 tested prompts and a short note on failure patterns.",
      res=["karpathy-intro", "karpathy-use", "3b1b-brief", "karpathy-deep", "3b1b-transformers", "ibm-rag", "ai-fluency", "ai-everyone", "google-genai"]),
 dict(n=3, wk="Weeks 2-4", title="Building blocks: code, APIs, data and Git", track="B", hours="30-42 h",
      goal="Read and change code, call APIs, query data and work in Git, with an AI coding assistant beside you.",
      topics=["How the web works", "Python basics", "Calling REST APIs, JSON, auth", "SQL queries and joins", "Git, GitHub and pull requests", "Using Claude Code or Cursor to explain and change code"],
      lab="Write a small script that pulls records from a public API, stores them in SQLite and answers three questions with SQL. Commit it to GitHub through a pull request.",
      out="A working repository with a README a colleague can run.",
      res=["mdn-web", "fcc-intro", "mosh-python", "fcc-python", "dlai-python", "fcc-apis", "fcc-sql", "cs50sql", "fcc-git", "gh-hello", "udemy-git", "fireship-web", "missing", "cs50x"],
      note="Software-background learners take a short skills check and skip what they can already do."),
 dict(n=4, wk="Weeks 3-4", title="Domain, business and market analysis", track="A", hours="24-30 h",
      goal="Understand how a client's business works, where value sits, and how to size an opportunity.",
      topics=["Industry value chains and systems of record", "Business model and value proposition canvases", "Market and competitor scan", "Business case: volume, time, cost, risk", "Build, buy or configure"],
      lab="Pick an industry. Map its value chain, list five processes where AI could help, and size the top one with a simple business case.",
      out="A two-page industry brief with a sized opportunity.",
      res=["yc-ideas", "bmc", "vpc", "market-research", "babok", "udemy-ba", "rm-pm", "google-data"],
      note="Domain-background learners take a short check and focus on the business case part."),
 dict(n=5, wk="Weeks 5-6", title="Discovery and requirements capture", track="both", hours="30-36 h",
      goal="Run a discovery that finds the real problem, the real process and the real constraints.",
      topics=["Interview technique: the last real case, not opinions", "Shadowing and evidence from documents and system logs", "Process mapping with swimlanes and BPMN basics", "Stakeholders, RACI and the process owner", "Writing the one-page brief and acceptance criteria", "Change and adoption from day one"],
      lab="Role-play discovery with a mentor playing the client. Capture the process, draw the map, and write the brief with open questions.",
      out="Discovery notes, a process map and a one-page brief, reviewed by the mock client.",
      res=["yc-users", "momtest", "cdh", "bpmn", "stories", "raci", "adkar", "udemy-pm"]),
 dict(n=6, wk="Weeks 6-7", title="Solution design and options", track="both", hours="24-30 h",
      goal="Turn a brief into two or three solution options and recommend one with honest trade-offs.",
      topics=["Option framing: assistive, semi-automated, automated", "Architecture sketches with the C4 model", "Data flow, integrations and where data may go", "Security: prompt injection, data leakage, access scope", "Model choice, cost and latency estimates", "Low-code vs custom build"],
      lab="For your brief, design three options. Draw a context and container diagram for the recommended one, list risks and give a cost estimate per month.",
      out="A solution options paper with a recommendation and a one-page architecture.",
      res=["c4", "12factor", "owasp-llm", "context-eng", "openai-agents", "effective-agents", "n8n"]),
 dict(n=7, wk="Weeks 7-9", title="Building the POC with LLMs", track="both", hours="42-54 h",
      goal="Build a working proof of concept on realistic data, fast, with AI coding assistants.",
      topics=["Prompt design and structured output in code", "Tool use and function calling", "RAG over client documents", "Agents and when not to use them", "MCP servers and connectors", "Working with Claude Code, Cursor or Copilot: plan, build, test, explain"],
      lab="Build the POC for your brief: a small app or workflow that reads the data, uses an LLM with tools or retrieval, and produces the agreed output.",
      out="A running POC in a repository, with a README and a two-minute screen recording.",
      res=["claude-api", "claude-code-course", "mcp-course", "prompting-101", "agent-tips", "cc-30", "dlai-agentic", "dlai-mcp", "dlai-cc", "dlai-prompt", "anthropic-courses", "prompt-tutorial", "prompt-docs", "cc-docs", "cc-best", "mcp-site", "cursor", "copilot", "rm-ai"]),
 dict(n=8, wk="Weeks 8-9", title="From demo to dependable: agentic system design and the FDE portfolio", track="both", hours="30-36 h",
      goal="Turn a working demo into a system a client can trust, and build the portfolio and interview skills that prove you can do it.",
      topics=["Where AI belongs: deterministic code, model judgment or human approval", "Designing for the unhappy path: schemas, validation, retries, fallbacks", "Agentic system design from a vague ask to production", "Integrating with existing systems; shadow mode to production", "Example portfolio projects and a 30-day build plan", "Preparing for FDE interviews: take-homes, live Python, case studies"],
      lab="Map one real workflow step by step into code, model and human; harden your POC for its top five failure modes; then run a mock agentic design interview in pairs.",
      out="A step-by-step operating map, a failure-mode list with how each is handled, and a one-page portfolio write-up of your POC.",
      res=["fde-playbook", "effective-agents", "context-eng", "openai-agents", "owasp-llm", "dlai-agentic", "evals-hamel"]),
 dict(n=9, wk="Weeks 9-10", title="Evaluate, deploy and operate", track="both", hours="30-36 h",
      goal="Prove the POC works on more than the demo case, put it online safely and know how it behaves.",
      topics=["Building an evaluation set from real cases", "Pass rates, error analysis, LLM-as-judge and its limits", "Human review gates and audit trail", "Deploying: static pages, serverless, containers", "CI/CD, secrets, logging, tracing and cost tracking"],
      lab="Create 30+ test cases, measure the POC, fix the top failure, deploy it behind access control and add basic tracing.",
      out="An evaluation report (before and after), a deployed URL and a short runbook.",
      res=["evals-hamel", "evals-claude", "dlai-evals", "langfuse", "fcc-docker", "udemy-docker", "cf-pages", "gh-actions", "sre", "rm-devops"]),
 dict(n=10, wk="Week 10", title="Product ownership, demo and hand-over", track="both", hours="18-24 h",
      goal="Show the value clearly, agree next steps and leave something the client can own.",
      topics=["Demo craft: start from the client's problem, show real data, show limits", "From POC to pilot: what changes and what it costs", "Roadmap, backlog and success measures", "Hand-over pack: runbook, owner, support model"],
      lab="Give a ten-minute demo to a mock steering group. Answer hard questions on accuracy, cost, security and adoption.",
      out="Demo recording, a pilot proposal and a hand-over pack.",
      res=["yc-mvp", "inspired", "spm", "google-pm", "rm-pm"]),
 dict(n=11, wk="Weeks 11-12", title="Final project: one client, one POC, end to end", track="both", hours="60-75 h",
      goal="Run the full FDE loop on an assigned use case with a mentor playing the client.",
      topics=["Discovery with the mock client", "Options paper and recommendation", "POC build with evaluation", "Deployment with access control", "Final demo and hand-over"],
      lab="Pick one of the assessment use cases below. Pairs work together; each person presents a part of the final demo.",
      out="Everything in the project checklist, scored against the rubric.",
      res=[]),
]

CASES = [
 dict(t="Invoice exception handling", sector="Cross-industry", ind="Finance operations", lvl="Core",
      client="Accounts payable lead at a mid-size distributor. 3,000 supplier invoices a month; about 15% fail matching against purchase orders.",
      pain="Clerks chase buyers by email, re-key data and miss early-payment discounts.",
      data="50 sample invoice PDFs, a purchase order export (CSV), an email thread sample, the AP policy (PDF).",
      deliver=["Process map of the exception path", "Extraction of invoice fields into JSON with a match check", "Drafted exception summary and suggested resolution for a clerk to approve", "Evaluation on 30+ invoices: extraction accuracy and correct routing"],
      skills="Document AI, rules plus LLM, human approval, business case"),
 dict(t="Support ticket triage and reply drafting", sector="Cross-industry", ind="Customer service", lvl="Core",
      client="Head of support at a software company. 1,200 tickets a week across email and chat.",
      pain="Tickets sit unassigned; agents answer the same questions from scratch.",
      data="500 anonymized tickets with categories, a help-center export, an SLA policy.",
      deliver=["Category and priority classifier with confidence", "Reply drafts grounded in help articles, with citations", "Routing rules and an escalation path", "Evaluation: classification accuracy, groundedness of replies"],
      skills="Classification, RAG, citations, evaluation design"),
 dict(t="Contract clause review", sector="Cross-industry", ind="Legal and procurement", lvl="Stretch",
      client="Procurement manager who reviews 40 supplier contracts a month against a clause playbook.",
      pain="Reviews take hours; risky clauses are missed when the team is busy.",
      data="20 sample contracts (PDF), a clause playbook with preferred and fallback language.",
      deliver=["Clause extraction and comparison against the playbook", "Risk flags with the exact contract text quoted", "A review summary a lawyer approves before it is sent", "Evaluation: recall of risky clauses on a labeled set"],
      skills="Long documents, quoting evidence, high-stakes review gates"),
 dict(t="Maintenance work order assistant", sector="Manufacturing", ind="Manufacturing", lvl="Core",
      client="Maintenance planner at a plant with 80 machines and paper-heavy work orders.",
      pain="Technicians search manuals and old work orders to find fixes; downtime grows.",
      data="Equipment list, 300 historical work orders (CSV), three machine manuals (PDF).",
      deliver=["Search across manuals and past fixes for a reported fault", "Drafted work order with parts and steps, approved by the planner", "A simple dashboard of repeat faults", "Evaluation: usefulness rated by a mentor on 20 fault reports"],
      skills="RAG over manuals, structured drafts, operations data"),
 dict(t="HR policy assistant and onboarding checklist", sector="Cross-industry", ind="Human resources", lvl="Starter",
      client="HR business partner fielding the same questions from 400 employees.",
      pain="Policy questions take time; new hires miss onboarding steps.",
      data="Employee handbook (PDF), leave and travel policies, an onboarding checklist (spreadsheet).",
      deliver=["Policy Q and A with citations and a 'not sure, ask HR' fallback", "A personalized onboarding checklist from a role and start date", "Access rules: what the assistant must never answer", "Evaluation: 40 questions with expected answers"],
      skills="Grounded Q and A, refusal behavior, privacy"),
 dict(t="Sales call notes to CRM updates", sector="Cross-industry", ind="Sales", lvl="Starter",
      client="Sales operations manager whose CRM is always out of date.",
      pain="Reps do not log calls; forecasts are unreliable.",
      data="20 call transcripts, the CRM field list, an opportunity stage definition.",
      deliver=["Extraction of next steps, stage, risks and contacts into CRM fields", "A follow-up email draft for the rep to send", "Change preview the rep approves before anything is written", "Evaluation: field-level accuracy on 20 transcripts"],
      skills="Extraction to a schema, write-back with approval, adoption"),
 dict(t="Quality deviation intake and triage", sector="Life sciences and regulated", ind="Regulated industries (life sciences, food, aerospace)", lvl="Stretch",
      client="Quality manager at a regulated manufacturer handling 100 deviations a month.",
      pain="Intake is inconsistent; investigations start late; audit trail is weak.",
      data="60 anonymized deviation reports, the deviation SOP, a risk classification matrix.",
      deliver=["Structured intake from free-text reports", "Risk classification with the reasoning shown, capped at human approval", "Investigation starter pack: similar past cases and suggested questions", "Audit log of every AI suggestion and every human decision", "Evaluation: agreement with quality specialists on 40 cases"],
      skills="Regulated workflows, audit trail, human-in-the-loop, validation thinking"),
 dict(t="Device complaint intake and reportability flag", sector="MedTech", ind="Quality and regulatory", lvl="Core",
      client="Complaint handling lead at a medical device maker. Complaints arrive as emails and call notes in many formats.",
      pain="Handlers retype device, lot, event and patient details by hand and must judge quickly whether an event may be reportable.",
      data="50 synthetic complaint emails written with an LLM, using public device event reports from the FDA MAUDE database as a style reference.",
      deliver=["Extraction of complaint fields into the complaint record format", "A possible-reportability flag with the reason shown", "A complaint specialist confirms every field and makes the reportability decision", "Evaluation: field accuracy on 40 labeled emails and recall on potentially reportable ones"],
      skills="Extraction, regulated review gate, recall over precision"),
 dict(t="Requirements to verification trace checker", sector="MedTech", ind="R&D and design controls", lvl="Core",
      client="Design engineering lead preparing the design history file for a new device.",
      pain="The trace matrix between design inputs and verification tests is built by hand, and gaps surface late in design reviews.",
      data="A synthetic list of 60 design inputs and 70 verification test summaries for a simple device such as a home blood pressure monitor.",
      deliver=["Proposed links between each design input and its verification tests", "A gap list: inputs with no test, tests with no input", "The design engineer accepts or rejects every proposed link", "Evaluation: precision and recall against a hand-built trace matrix"],
      skills="Matching, traceability, human acceptance of every link"),
 dict(t="Clinical evaluation literature screening", sector="MedTech", ind="Clinical affairs", lvl="Stretch",
      client="Clinical affairs reviewer updating a clinical evaluation report under EU MDR.",
      pain="Hundreds of abstracts are screened by hand, each needing an include or exclude decision and a reason.",
      data="200 public PubMed abstracts for one device type, with 100 labeled include or exclude and a reason.",
      deliver=["Include or exclude suggestion with a reason for each abstract", "A screening log in the format the report needs", "A clinical reviewer confirms every decision", "Evaluation: agreement with reviewer labels and number of relevant papers missed"],
      skills="Classification with reasons, audit trail, high-recall screening"),
 dict(t="Supplier corrective action request drafting", sector="MedTech", ind="Supply chain and manufacturing", lvl="Starter",
      client="Supplier quality engineer handling rejected components from incoming inspection.",
      pain="Each corrective action request is written by hand from inspection records and drawings, taking hours per case.",
      data="20 synthetic incoming inspection nonconformance records and a synthetic supplier quality agreement.",
      deliver=["A drafted request with the defect, the requirement cited and the containment asked for", "The engineer edits and approves before it is sent", "Evaluation: reviewer score on 20 drafts and edit time per draft"],
      skills="Drafting from records, citing requirements, approval before sending"),
]

RUBRIC = [
 ("Discovery", "Asked mostly about features or opinions; process map has gaps.", "Captured the real process and pain from the last real cases; map is complete.", "Found the root problem and the hidden constraint; the client recognizes the map as their work."),
 ("Problem framing and value", "Success is a feature list.", "Success is a measurable outcome with a baseline.", "Business case is sized, credible and agreed by the process owner."),
 ("Solution options", "One option, no trade-offs.", "Two or three options with clear pros, cons and costs.", "Recommendation is defensible on accuracy, cost, risk and adoption; knows when not to use AI."),
 ("Build quality", "Works only on the demo case.", "Works on realistic data; code is readable and runs from the README.", "Clean, small, testable; another person can extend it in a day."),
 ("Evaluation and safety", "No test set.", "30+ cases, a pass rate and the top failures explained.", "Evaluation drives changes; human review and access limits match the risk."),
 ("Deployment and operations", "Runs only on a laptop.", "Deployed behind access control with secrets handled properly.", "Tracing, cost tracking and a runbook; someone else could operate it."),
 ("Communication", "Demo is a tour of features.", "Demo starts from the client problem and shows real results.", "Handles hard questions calmly; states limits honestly; next step is agreed."),
]


# Five FDE abilities; each module row in the program map names the abilities it builds and how it is assessed.
ABILITIES = [
 ("A1", "Understand the end-to-end process", "and spot where automation, AI or software would help"),
 ("A2", "Turn problems into requirements", "a clear brief, acceptance criteria and a business case"),
 ("A3", "Design the solution", "pick suitable technology and sketch the architecture"),
 ("A4", "Build and prove a POC", "working software on realistic data, measured on real cases"),
 ("A5", "Present, get approval, hand over", "demo to the client, agree next steps, move toward delivery"),
]
MAP = {
 1: (["A1"], "Tutor step 01: the FDE loop applied to your project"),
 2: (["A3"], "Week 2 knowledge check; AI Fluency certificate"),
 3: (["A4"], "Week 4 skills check (domain track)"),
 4: (["A1", "A2"], "Week 4 industry brief (software track); rubric: problem framing"),
 5: (["A1", "A2"], "Week 6 discovery role-play; rubric: discovery"),
 6: (["A3"], "Options review with a mentor; rubric: solution options"),
 7: (["A4"], "POC repository and recording; rubric: build quality"),
 8: (["A3", "A4"], "Failure-mode list and portfolio write-up; rubric: evaluation and safety"),
 9: (["A4"], "Week 10 POC demo with evaluation results; rubric: deployment"),
 10: (["A5"], "Mock steering demo; rubric: communication"),
 11: (["A1", "A2", "A3", "A4", "A5"], "Week 12 final review panel, full rubric"),
}

def abilities_html():
    return '<ol class="abil">' + "".join(f'<li><span class="ab">{k}</span><b>{t}</b><span>{d}</span></li>' for k, t, d in ABILITIES) + "</ol>"

def map_html():
    rows = ['<tr data-track="both"><td class="mn-cell">--</td><th scope="row">Before week 1: the basics and machine setup</th><td>Before week 1</td><td></td>'
            '<td>A GitHub learning journal with a first commit</td><td>Tutor steps A and B</td><td><a href="learn/basics.html">Basics</a> / <a href="learn/m00.html">Setup</a></td></tr>']
    for m in MODULES:
        ab, how = MAP[m["n"]]
        chips = "".join(f'<span class="ab">{a}</span>' for a in ab)
        tr = "" if m["track"] == "both" else " " + chip(m["track"])
        rows.append(f'<tr data-track="{m["track"]}"><td class="mn-cell">{m["n"]:02d}</td><th scope="row">{escape(m["title"])}{tr}</th><td>{m["wk"]}<br><small>{m["hours"]}</small></td>'
                    f'<td class="abs">{chips}</td><td>{m["out"]}</td><td>{how}</td><td><a href="learn/m{m["n"]:02d}.html">Lessons</a></td></tr>')
    return ('<div class="tablewrap"><table class="pmap"><thead><tr><th>#</th><th>Module</th><th>When</th><th>Builds</th><th>You hand in</th><th>Assessed by</th><th></th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div>')

def case_filter_html():
    secs = []
    for c in CASES:
        if c["sector"] not in secs:
            secs.append(c["sector"])
    btns = '<button data-sector="all" aria-pressed="true">All</button>' + "".join(f'<button data-sector="{escape(x)}" aria-pressed="false">{escape(x)}</button>' for x in secs)
    return f'<div class="rfilter" role="group" aria-label="Filter use cases by industry"><span>Industry:</span>{btns}</div>'

# AI stack: six layers, top first. fde: "build" (FDE builds here), "choose" (FDE selects and buys), "" (FDE only feels its cost).
STACK = [
 ("Observability", "watch, evaluate, govern", "Records every step the system takes, scores the quality of its answers, catches problems before users do, and keeps the audit trail a regulator or an unhappy customer will ask for.", "Small layer, big consequences.", "LangSmith, Langfuse, Braintrust, Arize, Datadog, OpenTelemetry", "build"),
 ("Agent", "decide, call tools, act", "The logic around the model: routing, tools and their permissions, memory, retrieval, approvals and the loop that turns a model into something that does real work.", "Where the client's solution actually lives.", "Claude Agent SDK, OpenAI Agents SDK, Google ADK, LangGraph, Microsoft Agent Framework, MCP", "build"),
 ("Model", "weights and inference", "The models themselves, plus the serving that turns them into answers at a price per token.", "Changes fastest and gets cheaper fastest.", "Anthropic, OpenAI, Google, Meta, Mistral, DeepSeek, Qwen; served by them or by clouds and hosts", "choose"),
 ("Compute", "who runs the machines", "Buys the chips, builds the data centers and rents capacity by the hour, or runs it privately.", "Where most of the money is spent.", "AWS, Microsoft Azure, Google Cloud, Oracle Cloud, CoreWeave, your own data center", ""),
 ("Silicon", "who makes the chips", "Designs and manufactures the processors, memory and networking that everything else runs on.", "The hardest layer to enter.", "NVIDIA, AMD, TSMC, Samsung, SK Hynix, Micron; in-house chips such as Google TPU and AWS Trainium", ""),
 ("Energy", "power, grid, cooling", "Electricity, transmission and cooling for data centers.", "Now a real limit on how fast the rest can grow.", "Utilities and grid operators, power generators", ""),
]

def stack_html():
    rows = []
    for name, sub, desc, punch, who, fde in STACK:
        tag = {"build": '<span class="sk-tag sk-build">FDE builds here</span>', "choose": '<span class="sk-tag sk-choose">FDE chooses here</span>'}.get(fde, "")
        rows.append(f'<li class="sk-row sk-{name.lower()}{" sk-fde" if fde == "build" else ""}"><div class="sk-name"><b>{name}</b><span>{sub}</span>{tag}</div>'
                    f'<p class="sk-desc">{desc} <b>{punch}</b></p><p class="sk-who">{who}</p></li>')
    flow = learn.diagram_html({"type": "flow", "title": "What the FDE does, step by step", "caption": "The FDE does not train models or run data centers. They pick the right model and build, secure, measure and hand over the layers on top.", "steps": [
        {"label": "Find the real job", "note": "The process, the bottleneck, the measure"},
        {"label": "Choose a suitable model", "note": "Model layer: right size for each step"},
        {"label": "Build the agent layer", "note": "Code, tools, data access, human approval"},
        {"label": "Secure it", "note": "Least privilege, PII, injection, audit"},
        {"label": "Keep cost down", "note": "Smaller models, caching, batching"},
        {"label": "Observe and evaluate", "note": "Traces, evals, alerts, drift"},
        {"label": "Hand over to maintain", "note": "Runbook, owner, support model"}]})
    goals = "".join(f'<li><b>{g}</b><span>{d}</span></li>' for g, d in [
        ("Suitable", "The right kind of AI for this job, or no AI where rules do better"),
        ("Secure", "Client data protected, access limited, every action traceable"),
        ("Least cost", "Smallest model and fewest calls that still meet the measure"),
        ("Maintainable", "Someone else can run, fix and change it after you leave"),
        ("Does the job", "Measured against the outcome it was set up to deliver")])
    return f'<ol class="stack">{"".join(rows)}</ol>{flow}<div class="goal-box"><p class="eyebrow">What a good solution looks like</p><ul class="goals">{goals}</ul></div>'

# ---------- render ----------
TYPE_LABEL = {"video": "Video", "course": "Course", "docs": "Guide", "book": "Book", "cert": "Certificate"}
TRACK_LABEL = {"A": "Software background", "B": "Domain or business background", "both": "Both tracks"}

def chip(track):
    return f'<span class="trk t-{track}">{"Both tracks" if track == "both" else ("Track A" if track == "A" else "Track B")}</span>'

def res_item(key):
    t, title, src, url, cost = R[key]
    return (f'<li class="res" data-type="{t}" data-cost="{cost}"><span class="rt">{TYPE_LABEL[t]}</span>'
            f'<a href="{escape(url)}" target="_blank" rel="noopener">{escape(title)}</a>'
            f'<span class="rs">{escape(src)}</span>{"<span class=\"cost c-paid\">Paid</span>" if cost == "paid" else ""}</li>')

def open_link(m):
    f = ROOT / "content" / f'm{m["n"]:02d}.json'
    return f'<a class="open" href="learn/m{m["n"]:02d}.html">Open the training material</a>' if f.exists() else ""

def material_html():
    mods = learn.load_modules()
    label = lambda m: "Start here / set up first" if m["module"] == 0 else f'Module {m["module"]:02d}'
    items = "".join(f'<li><a href="learn/{m["file"]}.html"><span>{label(m)} / {len(m["lessons"])} lessons</span><b>{escape(m["title"])}</b></a></li>' for m in mods)
    start = '<li><a href="learn/basics.html"><span>Start here / before module 01</span><b>The basics: what is what</b></a></li>'
    return f'<ul class="mlist" role="list" style="list-style:none;padding:0">{start}{items}</ul>'

def module_html(m):
    res = "".join(res_item(k) for k in m["res"])
    note = f'<p class="note">{m["note"]}</p>' if m.get("note") else ""
    res_block = f'<div class="mres"><h4>Learn from</h4><ul class="reslist">{res}</ul></div>' if res else ""
    return f'''<article class="module" id="m{m["n"]}" data-track="{m["track"]}">
  <header><span class="mn">{m["n"]:02d}</span><div><p class="wk">{m["wk"]} / {m["hours"]}</p><h3>{m["title"]}</h3></div>{chip(m["track"])}</header>
  <p class="goal">{m["goal"]}</p>{note}
  <div class="mgrid">
    <div><h4>What we cover</h4><ul class="dots">{"".join(f"<li>{t}</li>" for t in m["topics"])}</ul></div>
    <div><h4>Hands-on lab</h4><p>{m["lab"]}</p><h4>You hand in</h4><p>{m["out"]}</p></div>
  </div>
  {res_block}
  {open_link(m)}
</article>'''

def concepts_html():
    out = []
    i = 0
    for area, items in CONCEPTS:
        lis = []
        for name, desc, track in items:
            i += 1
            lis.append(f'<li data-track="{track}"><label><input type="checkbox" id="c{i}" data-concept="c{i}"><span><b>{name}</b> {desc}</span></label>{chip(track)}</li>')
        out.append(f'<section class="carea"><h3>{area}</h3><ul class="clist">{"".join(lis)}</ul></section>')
    return "".join(out), i

def cases_html():
    out = []
    for i, c in enumerate(CASES, 1):
        out.append(f'''<article class="case" data-sector="{escape(c["sector"])}">
  <header><span class="lvl l-{c["lvl"].lower()}">{c["lvl"]}</span><h3>{i}. {c["t"]}</h3><p class="ind">{c["ind"]}</p></header>
  <dl><div><dt>Client</dt><dd>{c["client"]}</dd></div><div><dt>Pain</dt><dd>{c["pain"]}</dd></div><div><dt>Data you get</dt><dd>{c["data"]}</dd></div></dl>
  <h4>Deliver</h4><ul class="dots">{"".join(f"<li>{d}</li>" for d in c["deliver"])}</ul>
  <p class="skills"><b>Tests:</b> {c["skills"]}</p>
</article>''')
    return "".join(out)

def rubric_html():
    rows = "".join(f'<tr><th scope="row">{d}</th><td>{a}</td><td>{b}</td><td>{c}</td></tr>' for d, a, b, c in RUBRIC)
    return f'<div class="tablewrap"><table class="rubric"><thead><tr><th>Dimension</th><th>Not yet</th><th>Practitioner</th><th>FDE-ready</th></tr></thead><tbody>{rows}</tbody></table></div>'

def certs_html():
    rows = "".join(f'<tr data-track="{tr}"><td><a href="{escape(u)}" target="_blank" rel="noopener">{escape(n)}</a></td><td>{escape(iss)}</td><td>{escape(who)}</td><td>{fmt}</td><td>{chip(tr)}</td></tr>' for n, iss, who, u, fmt, cost, tr in CERTS)
    return f'<div class="tablewrap"><table class="certs"><thead><tr><th>Certification</th><th>Issuer</th><th>Who it is for</th><th>Format</th><th>Track</th></tr></thead><tbody>{rows}</tbody></table></div>'

def timeline_html():
    weeks = list(range(1, 13))
    spans = [(1, 1, 1, "both"), (2, 1, 2, "both"), (3, 2, 4, "B"), (4, 3, 4, "A"), (5, 5, 6, "both"), (6, 6, 7, "both"), (7, 7, 9, "both"), (8, 8, 9, "both"), (9, 9, 10, "both"), (10, 10, 10, "both"), (11, 11, 12, "both")]
    head = "".join(f'<span class="tw">W{w}</span>' for w in weeks)
    bars = "".join(f'<a class="tbar t-{tr}" href="learn/m{n:02d}.html" style="grid-column:{a + 1} / {b + 2}">{n:02d} {escape(MODULES[n - 1]["title"].split(":")[0])}</a>' for n, a, b, tr in spans)
    return f'<div class="tl-wrap"><div class="tl"><span class="tlab"></span>{head}{bars}</div></div>'

def how_week_html():
    return learn.diagram_html({"type": "swimlane", "title": "Who does what, day by day", "caption": "Mock clients join in discovery, demo and final project weeks. Everything a learner hands in is committed to their GitHub journal, so progress is visible to the mentor.",
        "lanes": ["Learner", "Pair", "Mentor", "Mock client", "Reviewer"],
        "steps": [{"lane": 0, "label": "Mon: self-study, videos, reading"}, {"lane": 2, "label": "Tue: live session, worked example"},
                  {"lane": 1, "label": "Wed: build the week's hand-in"}, {"lane": 2, "label": "Wed-Thu: office hours, unblock"},
                  {"lane": 3, "label": "Thu: answers questions as client"}, {"lane": 0, "label": "Thu: commit evidence to journal"},
                  {"lane": 1, "label": "Fri: show and tell to the group"}, {"lane": 4, "label": "Fri: score on rubric, feedback"}]})

def how_tools_html():
    return learn.diagram_html({"type": "flow", "title": "The tools you will use, stage by stage", "caption": "Learners pick one tool per stage to start; the program does not depend on any single vendor.",
        "steps": [{"label": "Think and draft", "note": "Claude, ChatGPT or Gemini"}, {"label": "Build", "note": "Claude Code, Cursor or Copilot; Python; Git"},
                  {"label": "Connect", "note": "APIs, MCP servers, n8n"}, {"label": "Evaluate", "note": "A test set; tracing with Langfuse"},
                  {"label": "Deploy", "note": "Cloudflare, AWS, Azure or Google Cloud"}, {"label": "Show", "note": "Diagrams, a recording, a live demo"}]})

JOURNEY = [
 ("1", "Start here", "Get the words and the tools right.",
  "Read the basics (what a model, an API, a harness and context are) and set up GitHub, VS Code and an AI coding assistant on your machine.",
  "About a week", [("The basics", "learn/basics.html"), ("Set up your machine", "learn/m00.html")]),
 ("2", "Modules", "Learn the FDE skills, one module at a time.",
  "Eleven modules from the FDE role to the final project. Each lesson has a diagram, a plain explanation, a worked example and practice.",
  "12 weeks", [("Open module 01", "learn/m01.html")]),
 ("3", "Practice", "Build one real project and prove each step.",
  "Pick your industry and a project, then work through 13 steps. Your evidence is saved to your GitHub journal, so your mentor sees real progress.",
  "Alongside the modules", [("Open your learning path", "tldr.html")]),
 ("4", "Crash course", "Go deeper on any topic, whenever you need to.",
  "431 checked videos, articles, courses and papers across systems, programming, data, cloud, security, AI and business. Start with the must-dos.",
  "As you need it", [("Open the crash course", "crash-course.html")]),
]

def journey_html():
    cards = []
    for num, title, line, desc, when, links in JOURNEY:
        btns = "".join(f'<a class="open" href="{h}">{escape(t)}</a>' for t, h in links)
        cards.append(f'<li class="jr"><span class="jr-n">{num}</span><div><h3>{title}</h3><p class="jr-line">{line}</p><p>{desc}</p>'
                     f'<p class="jr-when">{when}</p><div class="jr-go">{btns}</div></div></li>')
    return '<ol class="journey">' + "".join(cards) + "</ol>"

# Four stages of the 12 weeks: what you learn, what you build, how it is checked.
PHASES = [
 ("Foundations", "Weeks 1 to 4", [1, 2, 3], "The FDE role, how LLMs work, and enough code, APIs, data and Git to build.",
  "Your learning journal, a prompt log and a small working script.", "Week 2 knowledge check and week 4 skills check."),
 ("Understand the client", "Weeks 3 to 6", [4, 5], "How the business makes money, discovery interviews, process maps and requirements.",
  "A sized business case, a process map and a one-page brief.", "Week 6 discovery role-play with a mock client."),
 ("Design and build", "Weeks 6 to 9", [6, 7, 8], "Solution options, security and cost, building the POC, and making it dependable.",
  "An options paper, a working POC and a list of how it handles failures.", "Options review and the POC recording."),
 ("Prove and hand over", "Weeks 9 to 12", [9, 10, 11], "Evaluation, deployment, demo craft and hand-over, then the final project.",
  "An evaluation report, a live URL, a demo, a hand-over pack and your final project.", "Week 10 POC demo and the week 12 final review panel."),
]

def phases_html():
    by_n = {m["n"]: m for m in MODULES}
    out = []
    for i, (name, weeks, nums, learn_, build_, prove_) in enumerate(PHASES, 1):
        mods = []
        for n in nums:
            m = by_n[n]
            ab, how = MAP[n]
            chips = "".join(f'<span class="ab">{a}</span>' for a in ab)
            tr = "" if m["track"] == "both" else " " + chip(m["track"])
            mods.append(f'<li class="pm" data-track="{m["track"]}"><a href="learn/m{n:02d}.html"><span class="pm-n">{n:02d}</span>'
                        f'<b>{escape(m["title"])}</b></a><p class="pm-when">{m["wk"]} / {m["hours"]}{tr}</p><p class="pm-abs">{chips}</p>'
                        f'<p><span class="pm-k">You hand in</span>{m["out"]}</p><p><span class="pm-k">Checked by</span>{how}</p></li>')
        out.append(f'<section class="phase"><header><p class="eyebrow">Stage {i} / {weeks}</p><h3>{name}</h3></header>'
                   f'<dl class="lbp"><div><dt>Learn</dt><dd>{learn_}</dd></div><div><dt>Build</dt><dd>{build_}</dd></div><div><dt>Prove</dt><dd>{prove_}</dd></div></dl>'
                   f'<ol class="pms">{"".join(mods)}</ol></section>')
    return "".join(out)

def certs_cards_html():
    items = "".join(f'<li data-track="{tr}"><a href="{escape(u)}" target="_blank" rel="noopener">{escape(n)}</a><span>{escape(iss)} / {fmt}</span><p>{escape(who)}</p></li>'
                    for n, iss, who, u, fmt, cost, tr in CERTS)
    return f'<ul class="certcards">{items}</ul>'

def page():
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>FDE Training Program</title>
<meta name="description" content="A 12-week program that adds forward deployed engineering skills to engineers and domain experts: understand the process, write requirements, design the solution, build a POC and get it approved.">
<script src="theme.js"></script>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Familjen+Grotesk:wght@500;600;700&family=Atkinson+Hyperlegible:wght@400;700&family=IBM+Plex+Mono:wght@500&display=swap">
<link rel="stylesheet" href="style.css"></head>
<body>
<a class="skip" href="#main">Skip to content</a>
{topbar("", (), "", "index")}
<div class="page">
<main id="main">
<header class="hero">
  <p class="kicker">Training program / 12 weeks / 24 to 32 hours a week</p>
  <h1>Add forward deployed engineering skills to the expertise you already have.</h1>
  <p class="lede">For engineers and domain experts in R&amp;D, quality and regulatory, clinical, supply chain, manufacturing, program management, software and digital teams. You already know the work and the customer. This program adds the skills to turn that knowledge into AI and software solutions a client approves.</p>
  <div class="cp-hero"><p class="cp-h">Your progress</p><div data-progress></div><p class="t-note">Counted from the checks you pass: the basics quick check, the machine setup check and the 12 module tests. Saved in this browser.</p></div>
  <h2 class="abil-h">What you will be able to do</h2>
  {abilities_html()}
</header>

<section id="journey" class="sec">
  <h2>Your path through the program</h2>
  <p class="intro">Four parts, in this order. Start here once, work through the modules, practise on one real project as you go, and use the crash course whenever you want more depth.</p>
  {journey_html()}
</section>

<section id="map" class="sec">
  <h2>The 12 weeks: learn, build, prove</h2>
  <p class="intro">The 12 weeks in four stages. For each stage: what you learn, what you build, and how it is checked. Open any module to start its lessons.</p>
  {phases_html()}
</section>

<section id="stack" class="sec">
  <h2>Where an FDE fits in the AI stack</h2>
  <p class="intro">AI runs on six layers. Most of the money goes into the bottom layers; most of what makes one company's AI different from another's is built in the top two. That is where the FDE works: choosing a model, then building the agent and observability layers so the client gets AI that fits, is safe, costs as little as possible, can be maintained and does what it was set up to do.</p>
  {stack_html()}
</section>

<section id="role" class="sec">
  <h2>How an FDE works with a client</h2>
  <p class="intro">Every engagement, and every module in this program, follows the same loop: from "how does this work actually happen" to "a running solution the owner trusts".</p>
  <ol class="loop">
    <li><b>Embed</b><span>Join the client team, meet the process owner and the people doing the work.</span></li>
    <li><b>Discover</b><span>Interview, shadow, read documents and data; map the real process.</span></li>
    <li><b>Frame</b><span>Write the problem, the success measure and the business case.</span></li>
    <li><b>Design</b><span>Lay out two or three options and recommend one.</span></li>
    <li><b>Build</b><span>Ship a POC on realistic data with AI coding assistants.</span></li>
    <li><b>Evaluate</b><span>Test on real cases; fix what fails; set human review.</span></li>
    <li><b>Demo and hand over</b><span>Show the value, agree the next step, leave a runbook.</span></li>
  </ol>
</section>

<section id="tracks" class="sec">
  <h2>Who this program is for</h2>
  <p class="intro">Anyone who wants to use today's AI well: effectively, securely and at the lowest cost. That takes two things. You learn how the underlying pieces work (models, data, APIs, networks, security), and you learn how to read an industry so you know where AI really helps. Everyone starts from one of two places.</p>
  <div class="tracks">
    <div class="track t-A"><p class="tk">Track A</p><h3>Software and digital background</h3><p>You can build. The program adds domain and business analysis, discovery, product ownership and communication. Fast-track Module 3 after a skills check.</p></div>
    <div class="track t-B"><p class="tk">Track B</p><h3>Domain background</h3><p>R&amp;D, quality, regulatory, clinical, supply chain, manufacturing or operations. You know the work. The program adds code basics, APIs, data, AI-assisted building and deployment. Fast-track Module 4 after a skills check.</p></div>
  </div>
  <p class="intro">Learners work in mixed pairs, one from each track, so they teach each other and finish the final project together.</p>
</section>



<section id="assess" class="sec">
  <h2>How your progress is checked</h2>
  <p class="intro">Three layers of evidence, so a learner, a mentor and a manager can all see the same progress.</p>
  <div class="assess">
    <div><h3>1. Every step: the GitHub journal</h3><p>In <a href="tldr.html">the tutor</a>, each of the 13 steps saves evidence to the learner's own GitHub repository and must pass defined checks. A manager opens one link to see what is done.</p></div>
    <div><h3>2. Checkpoints with a mentor</h3><ol>
      <li><b>Week 2:</b> knowledge check on LLM concepts and a prompt log review</li>
      <li><b>Week 4:</b> track skills check: a small coding task (domain track) or an industry brief (software track)</li>
      <li><b>Week 6:</b> recorded discovery role-play with a mock client</li>
      <li><b>Week 10:</b> POC demo with evaluation results</li>
      <li><b>Week 12:</b> final review panel: demo, questions, hand-over pack</li></ol></div>
    <div><h3>3. Rubric and graduation</h3><p>The panel scores seven dimensions as not yet, practitioner or FDE-ready. <b>To graduate:</b> FDE-ready in discovery, build quality, evaluation and safety, and communication, and at least practitioner in the rest.</p></div>
  </div>
  <details class="rub"><summary>See the full rubric</summary>{rubric_html()}</details>
</section>

<section id="cases" class="sec">
  <h2>Choose a project to practice on</h2>
  <p class="intro">Pick a project from the industry you know or want to work in. You build it in the final two weeks, from discovery to demo. Filter by industry below, or find 86 more ideas in <a href="tldr.html">your path</a>.</p>
  {case_filter_html()}
  <div class="cases">{cases_html()}</div>
  <div class="capstone"><h3>Every project hands in</h3><ul class="dots">
    <li>Discovery notes and a process map reviewed by the mock client</li><li>One-page brief with the success measure and a sized business case</li><li>Options paper with a recommendation</li><li>Working POC in a repository with a README</li><li>Evaluation set of 30 or more cases with results and the top failures explained</li><li>Deployed URL behind access control</li><li>Ten-minute demo and a hand-over pack: runbook, owner, next step</li></ul></div>
</section>

<section id="certs" class="sec">
  <h2>Optional certifications</h2>
  <p class="intro">Optional, and never a substitute for the final project. Pick one or two that match your track and the platforms your clients use.</p>
  {certs_cards_html()}
</section>

<section id="how" class="sec">
  <h2>How each week runs</h2>
  <p class="intro">Every week follows the same rhythm, so learners always know what is expected and when. Read each lane left to right: it shows who does what across the week.</p>
  {how_week_html()}
  <div class="assess">
    <div><h3>How we teach</h3><ul class="dots">
      <li><b>Learn by doing:</b> every week ends with something handed in and committed</li>
      <li><b>Real material:</b> messy documents, realistic data, real constraints</li>
      <li><b>AI as tutor and tool:</b> use it to explain, draft and code, then show your own reasoning</li>
      <li><b>Evidence over opinion:</b> every claim backed by an interview, a document or data</li>
      <li><b>Feedback every week</b> from a mentor and from peers</li></ul></div>
    <div><h3>Who supports you</h3><ul class="dots">
      <li><b>Program lead:</b> owns cohorts, the plan and graduation decisions</li>
      <li><b>Mentors:</b> experienced engineers and consultants, one per four to six learners</li>
      <li><b>Mock clients:</b> domain experts who play the client in discovery, demos and the final project</li>
      <li><b>Reviewers:</b> score hand-ins and the final project against the rubric</li></ul></div>
  </div>
  {how_tools_html()}
</section>

</main></div>
<script src="app.js" defer></script>
<script src="progress.js" defer></script>
</body></html>
'''

def main():
    OUT.mkdir(exist_ok=True)
    mods = learn.build()
    tldr.build()
    crash.build()
    faq, vec = ROOT / "content" / "faq.json", OUT / "faq-vec.json"
    if faq.exists() and (not vec.exists() or vec.stat().st_mtime < faq.stat().st_mtime):
        import subprocess
        r = subprocess.run(["node", str(ROOT / "tools" / "needle_embed.js")], capture_output=True, text=True)
        print(r.stdout.strip() or r.stderr.strip())
    print("lesson pages:", ", ".join(m["file"] for m in mods))
    html = page()
    head, body = html.split('<div class="page">', 1)
    body = body.replace('href="learn/', 'target="_blank" rel="noopener" href="learn/')
    (OUT / "index.html").write_text(head + '<div class="page">' + body, encoding="ascii")
    print("built", OUT / "index.html", "resources:", len(R), "modules:", len(MODULES), "cases:", len(CASES))

if __name__ == "__main__":
    main()
