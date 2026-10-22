// Tells the page whether Cloudflare sign-in is set up here and whether this learner is connected.
import { configured, cookie } from "../../../lib/cf.js";

export async function onRequestGet({ request, env }) {
  const connected = Boolean(cookie(request, "cf_tok") && cookie(request, "cf_acct"));
  return Response.json({ configured: configured(env), connected, account: connected ? cookie(request, "cf_name") : "" }, { headers: { "Cache-Control": "no-store" } });
}
