// Cloudflare OAuth helpers. Pages env: CF_OAUTH_CLIENT_ID, CF_OAUTH_CLIENT_SECRET, CF_OAUTH_SCOPES (space separated, as chosen on the OAuth client), optional CF_AI_MODEL.
// The learner's token lives only in HttpOnly cookies on /api/cf, so page scripts never see it.
export const AUTH_URL = "https://dash.cloudflare.com/oauth2/auth";
export const TOKEN_URL = "https://dash.cloudflare.com/oauth2/token";
export const API = "https://api.cloudflare.com/client/v4";
export const DEFAULT_MODEL = "@cf/meta/llama-3.2-3b-instruct";
export const PAGE = "/tldr";

export function configured(env) {
  return Boolean(env.CF_OAUTH_CLIENT_ID && env.CF_OAUTH_CLIENT_SECRET && env.CF_OAUTH_SCOPES);
}

export function redirectUri(request) {
  return new URL("/api/cf/callback", request.url).toString();
}

export function back(request, hash) {
  return Response.redirect(new URL(PAGE + "#" + hash, request.url).toString(), 302);
}

export function cookie(request, name) {
  for (const part of (request.headers.get("Cookie") || "").split(";")) {
    const [k, ...v] = part.trim().split("=");
    if (k === name) return decodeURIComponent(v.join("="));
  }
  return "";
}

export function setCookie(name, value, maxAge) {
  return `${name}=${encodeURIComponent(value)}; Path=/api/cf; HttpOnly; Secure; SameSite=Lax; Max-Age=${maxAge}`;
}
