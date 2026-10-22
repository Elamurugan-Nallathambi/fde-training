// Starts GitHub sign-in: sets a one-time state cookie and sends the user to GitHub's consent page.
import { configured, redirectUri, back, SCOPE } from "../../../lib/gh.js";

export async function onRequestGet({ request, env }) {
  if (!configured(env)) return back(request, "gh_error=not_configured");
  const bytes = crypto.getRandomValues(new Uint8Array(16));
  const state = Array.from(bytes, (b) => b.toString(16).padStart(2, "0")).join("");
  const url = new URL("https://github.com/login/oauth/authorize");
  url.searchParams.set("client_id", env.GITHUB_CLIENT_ID);
  url.searchParams.set("redirect_uri", redirectUri(request));
  url.searchParams.set("scope", SCOPE);
  url.searchParams.set("state", state);
  url.searchParams.set("allow_signup", "true");
  return new Response(null, {
    status: 302,
    headers: {
      Location: url.toString(),
      "Set-Cookie": `gh_state=${state}; Path=/api/gh; HttpOnly; Secure; SameSite=Lax; Max-Age=600`,
      "Cache-Control": "no-store",
    },
  });
}
