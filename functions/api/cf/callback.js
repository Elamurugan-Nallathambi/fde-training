// Cloudflare returns here: check state, swap the code for a token, find the granted account, keep both in HttpOnly cookies.
import { configured, redirectUri, back, cookie, setCookie, TOKEN_URL, API } from "../../../lib/cf.js";

export async function onRequestGet({ request, env }) {
  if (!configured(env)) return back(request, "cf_error=not_configured");
  const url = new URL(request.url);
  if (url.searchParams.get("error")) return back(request, "cf_error=" + encodeURIComponent(url.searchParams.get("error")));
  const code = url.searchParams.get("code"), state = url.searchParams.get("state");
  if (!code || !state || state !== cookie(request, "cf_state")) return back(request, "cf_error=bad_state");

  const res = await fetch(TOKEN_URL, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded", Accept: "application/json" },
    body: new URLSearchParams({ grant_type: "authorization_code", code, redirect_uri: redirectUri(request),
      client_id: env.CF_OAUTH_CLIENT_ID, client_secret: env.CF_OAUTH_CLIENT_SECRET }),
  });
  const tok = await res.json().catch(() => ({}));
  if (!tok.access_token) return back(request, "cf_error=" + encodeURIComponent(tok.error || "exchange_failed"));

  const acc = await fetch(API + "/accounts", { headers: { Authorization: "Bearer " + tok.access_token } }).then((r) => r.json()).catch(() => ({}));
  const account = acc && acc.result && acc.result[0];
  if (!account) return back(request, "cf_error=no_account_granted");

  const life = Math.max(300, Math.min(Number(tok.expires_in) || 3600, 86400));
  const headers = new Headers({ Location: new URL("/tldr#cf=connected", request.url).toString(), "Cache-Control": "no-store", "Referrer-Policy": "no-referrer" });
  headers.append("Set-Cookie", setCookie("cf_tok", tok.access_token, life));
  headers.append("Set-Cookie", setCookie("cf_acct", account.id, life));
  headers.append("Set-Cookie", setCookie("cf_name", account.name || "", life));
  headers.append("Set-Cookie", setCookie("cf_state", "", 0));
  return new Response(null, { status: 302, headers });
}
