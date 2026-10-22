// Answers a chat question with the learner's own Workers AI, using their Cloudflare token from the cookie.
import { cookie, API, DEFAULT_MODEL } from "../../../lib/cf.js";

const SYSTEM = "You are the help assistant on a training site for forward deployed engineers. Answer in plain, simple English in at most 6 short sentences. Use the page context when it helps. If you are not sure, say so and suggest which part of the course to read. Never invent facts, links or numbers.";

export async function onRequestPost({ request, env }) {
  const tok = cookie(request, "cf_tok"), acct = cookie(request, "cf_acct");
  if (!tok || !acct) return Response.json({ error: "not_connected" }, { status: 401 });
  const body = await request.json().catch(() => ({}));
  const question = String(body.question || "").slice(0, 1000).trim();
  const context = String(body.context || "").slice(0, 4000);
  if (!question) return Response.json({ error: "empty" }, { status: 400 });
  const model = env.CF_AI_MODEL || DEFAULT_MODEL;
  const res = await fetch(`${API}/accounts/${acct}/ai/run/${model}`, {
    method: "POST",
    headers: { Authorization: "Bearer " + tok, "Content-Type": "application/json" },
    body: JSON.stringify({ messages: [{ role: "system", content: SYSTEM }, { role: "user", content: `Page context:\n${context}\n\nQuestion: ${question}` }], max_tokens: 400 }),
  });
  const data = await res.json().catch(() => ({}));
  if (res.status === 401 || res.status === 403) return Response.json({ error: "reconnect" }, { status: 401 });
  if (!data.success) return Response.json({ error: (data.errors && data.errors[0] && data.errors[0].message) || "ai_error" }, { status: 502 });
  return Response.json({ answer: (data.result && data.result.response) || "", model });
}
