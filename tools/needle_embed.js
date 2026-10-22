// Embeds the chat's prepared questions with Needle 3 (same engine and pinned weights as the browser) into public/faq-vec.json.
// Vectors are centred on their mean and normalised, so the browser only needs a dot product. Usage: node tools/needle_embed.js [--test]
const fs = require("fs");
const path = require("path");
const os = require("os");
const crypto = require("crypto");

const ROOT = path.join(__dirname, "..");
const WEIGHTS_URL = "https://huggingface.co/Cactus-Compute/needle3/resolve/9da75122d4ca11aa4a667281c9c8ba38a7eed679/needle3.cact";
const WEIGHTS_SHA256 = "c9d915eca282ed42d1a09b143b592adb4cc6744ffe2d294adf5cfc5548170c38";
const CACHE = path.join(os.homedir(), ".cache", "antp-needle3", "needle3-" + WEIGHTS_SHA256.slice(0, 12) + ".cact");

async function weights() {
  if (fs.existsSync(CACHE) && crypto.createHash("sha256").update(fs.readFileSync(CACHE)).digest("hex") === WEIGHTS_SHA256) return fs.readFileSync(CACHE);
  const res = await fetch(WEIGHTS_URL);
  if (!res.ok) throw new Error("weights download failed: HTTP " + res.status);
  const buf = Buffer.from(await res.arrayBuffer());
  if (crypto.createHash("sha256").update(buf).digest("hex") !== WEIGHTS_SHA256) throw new Error("weights sha256 mismatch");
  fs.mkdirSync(path.dirname(CACHE), { recursive: true });
  fs.writeFileSync(CACHE, buf);
  return buf;
}

async function embedder() {
  const createNeedle = require(path.join(ROOT, "public", "needle", "needle.js"));
  const M = await createNeedle();
  const cact = await weights();
  const p = M._malloc(cact.length);
  M.HEAPU8.set(cact, p);
  if (M._needle_load(p, BigInt(cact.length)) < 0) throw new Error("needle_load failed");
  if (M.ccall("needle_init", "number", ["string", "string", "string"], ["", "[]", ""]) < 0) throw new Error("needle_init failed");
  const dim = M.ccall("needle_embed", "number", ["string", "number", "number"], ["x", 0, 0]);
  const out = M._malloc(dim * 4);
  return {
    dim,
    embed(text) {
      const n = M.ccall("needle_embed", "number", ["string", "number", "number"], [String(text).slice(0, 1500), out, dim]);
      if (n <= 0) throw new Error("needle_embed failed");
      return Float32Array.from(new Float32Array(M.HEAPU8.buffer, out, n));
    },
  };
}

function centre(vecs) {
  const dim = vecs[0].length, mean = new Float32Array(dim);
  vecs.forEach((v) => v.forEach((x, i) => (mean[i] += x / vecs.length)));
  const norm = (v) => { const c = v.map((x, i) => x - mean[i]); const l = Math.hypot(...c) || 1; return c.map((x) => x / l); };
  return { mean, norm };
}

async function main() {
  const e = await embedder();
  const faq = JSON.parse(fs.readFileSync(path.join(ROOT, "content", "faq.json"), "utf8")).answers;
  const raw = faq.map((f) => e.embed(f.q + " " + (f.keywords || []).join(" ")));
  const { mean, norm } = centre(raw);
  const vecs = raw.map((v) => Array.from(norm(v), (x) => Math.round(x * 1000) / 1000));
  if (process.argv.includes("--test")) {
    const probes = [["what is a harness", null], ["how many times can I retake the module test", null], ["where do I begin", null], ["what does rag mean", null], ["best pizza recipe", null]];
    for (const [q] of probes) {
      const v = norm(e.embed(q));
      const scored = vecs.map((u, i) => ({ i, s: u.reduce((a, x, k) => a + x * v[k], 0) })).sort((a, b) => b.s - a.s).slice(0, 2);
      console.log(q.padEnd(48), scored.map((x) => faq[x.i].id + " " + x.s.toFixed(3)).join(" | "));
    }
    return;
  }
  const out = { model: "needle3-3.0.1", dim: e.dim, mean: Array.from(mean, (x) => Math.round(x * 100000) / 100000), ids: faq.map((f) => f.id), vecs };
  fs.writeFileSync(path.join(ROOT, "public", "faq-vec.json"), JSON.stringify(out));
  console.log("embedded", faq.length, "answers, dim", e.dim);
}

if (require.main === module) main().catch((err) => { console.error(err.message); process.exit(1); });
module.exports = { embedder, WEIGHTS_URL, WEIGHTS_SHA256 };
