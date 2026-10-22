// Tells the page whether GitHub sign-in is set up on this deployment.
import { configured } from "../../../lib/gh.js";

export async function onRequestGet({ env }) {
  return Response.json({ configured: configured(env) }, { headers: { "Cache-Control": "no-store" } });
}
