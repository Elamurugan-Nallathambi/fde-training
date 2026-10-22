// Disconnects Cloudflare by clearing the cookies; the learner can also revoke the app in their Cloudflare profile.
import { setCookie } from "../../../lib/cf.js";

export async function onRequestPost() {
  const headers = new Headers({ "Cache-Control": "no-store" });
  for (const n of ["cf_tok", "cf_acct", "cf_name"]) headers.append("Set-Cookie", setCookie(n, "", 0));
  return Response.json({ ok: true }, { headers });
}
