// Tutor feedback on a step or project idea, from Workers AI on the site's own account (free daily allowance).
// The rule checks in the page decide pass or fail; this only writes suggestions.
const MODEL = "@cf/meta/llama-3.1-8b-instruct-fp8-fast";
const SYSTEM = "You are a tutor in a forward deployed engineer training program. Give up to three short, concrete suggestions to improve the learner's work. Only refer to what is written. Do not invent numbers or facts. Do not give a verdict. Reply as a short list, one suggestion per line starting with '- '.";
const FOCUS = {
  step: "The learner wrote this as evidence for one step of their project.",
  idea: "The learner wrote this project idea. Focus on: one clear bottleneck, a countable success measure, available data, a human approval point, and scope small enough for 12 weeks.",
};

export async function onRequestPost({ request, env }) {
  if (!env.AI) return Response.json({ error: "not_configured" }, { status: 503 });
  const body = await request.json().catch(() => ({}));
  const kind = body.kind === "idea" ? "idea" : "step";
  const text = String(body.text || "").slice(0, 3500).trim();
  if (text.length < 20) return Response.json({ error: "too_short" }, { status: 400 });
  try {
    const out = await env.AI.run(MODEL, { messages: [{ role: "system", content: SYSTEM + " " + FOCUS[kind] }, { role: "user", content: text }], max_tokens: 250, temperature: 0.3 });
    return Response.json({ answer: String((out && out.response) || "").trim() });
  } catch (e) {
    const msg = String((e && e.message) || e);
    if (/limit|quota|neuron|429|exceed/i.test(msg)) return Response.json({ error: "limit" }, { status: 429 });
    return Response.json({ error: "ai_error" }, { status: 502 });
  }
}
