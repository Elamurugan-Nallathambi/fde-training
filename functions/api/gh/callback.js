// GitHub sends the user back here; check state, swap the code for a token, hand the token to the page in the URL fragment.
import { configured, redirectUri, back, readCookie, PAGE } from "../../../lib/gh.js";

export async function onRequestGet({ request, env }) {
  if (!configured(env)) return back(request, "gh_error=not_configured");
  const url = new URL(request.url);
  const code = url.searchParams.get("code");
  const state = url.searchParams.get("state");
  if (url.searchParams.get("error")) return back(request, "gh_error=" + encodeURIComponent(url.searchParams.get("error")));
  if (!code || !state || state !== readCookie(request, "gh_state")) return back(request, "gh_error=bad_state");

  const res = await fetch("https://github.com/login/oauth/access_token", {
    method: "POST",
    headers: { Accept: "application/json", "Content-Type": "application/json", "User-Agent": "fde-training-tutor" },
    body: JSON.stringify({
      client_id: env.GITHUB_CLIENT_ID,
      client_secret: env.GITHUB_CLIENT_SECRET,
      code,
      redirect_uri: redirectUri(request),
    }),
  });
  const data = await res.json().catch(() => ({}));
  if (!data.access_token) return back(request, "gh_error=" + encodeURIComponent(data.error || "exchange_failed"));

  const target = new URL(PAGE + "#gh=" + encodeURIComponent(data.access_token), request.url).toString();
  return new Response(null, {
    status: 302,
    headers: {
      Location: target,
      "Set-Cookie": "gh_state=; Path=/api/gh; HttpOnly; Secure; SameSite=Lax; Max-Age=0",
      "Cache-Control": "no-store",
      "Referrer-Policy": "no-referrer",
    },
  });
}
