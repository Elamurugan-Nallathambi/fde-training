// Starts "Connect with Cloudflare": one-time state cookie, then Cloudflare's consent page.
import { configured, redirectUri, back, setCookie, AUTH_URL } from "../../../lib/cf.js";

export async function onRequestGet({ request, env }) {
  if (!configured(env)) return back(request, "cf_error=not_configured");
  const state = Array.from(crypto.getRandomValues(new Uint8Array(16)), (b) => b.toString(16).padStart(2, "0")).join("");
  const url = new URL(AUTH_URL);
  url.searchParams.set("response_type", "code");
  url.searchParams.set("client_id", env.CF_OAUTH_CLIENT_ID);
  url.searchParams.set("redirect_uri", redirectUri(request));
  url.searchParams.set("scope", env.CF_OAUTH_SCOPES);
  url.searchParams.set("state", state);
  const headers = new Headers({ Location: url.toString(), "Cache-Control": "no-store" });
  headers.append("Set-Cookie", setCookie("cf_state", state, 600));
  return new Response(null, { status: 302, headers });
}
