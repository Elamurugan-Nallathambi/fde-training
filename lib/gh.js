// GitHub OAuth helpers for the tutor page. Client id and secret come from Pages env: GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET.
export const PAGE = "/tldr";
export const SCOPE = "public_repo";

export function configured(env) {
  return Boolean(env.GITHUB_CLIENT_ID && env.GITHUB_CLIENT_SECRET);
}

export function redirectUri(request) {
  return new URL("/api/gh/callback", request.url).toString();
}

export function back(request, hash) {
  return Response.redirect(new URL(PAGE + "#" + hash, request.url).toString(), 302);
}

export function readCookie(request, name) {
  const raw = request.headers.get("Cookie") || "";
  for (const part of raw.split(";")) {
    const [k, ...v] = part.trim().split("=");
    if (k === name) return v.join("=");
  }
  return "";
}
