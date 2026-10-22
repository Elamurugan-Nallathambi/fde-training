// Needle 3 meaning search in the browser (Apache-2.0, Cactus Compute). Weights come once from the pinned Hugging Face revision,
// are checked against their sha256 and kept in the browser cache; the engine runs off the main thread.
importScripts("needle/needle.js");
var WEIGHTS = "https://huggingface.co/Cactus-Compute/needle3/resolve/9da75122d4ca11aa4a667281c9c8ba38a7eed679/needle3.cact";
var SHA256 = "c9d915eca282ed42d1a09b143b592adb4cc6744ffe2d294adf5cfc5548170c38";
var M = null, dim = 0, out = 0;

async function weights() {
  var cache = await caches.open("fde-needle3");
  var res = await cache.match(WEIGHTS);
  if (!res) {
    res = await fetch(WEIGHTS);
    if (!res.ok) throw new Error("weights download failed: HTTP " + res.status);
    await cache.put(WEIGHTS, res.clone());
  }
  var buf = new Uint8Array(await res.arrayBuffer());
  var hash = Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256", buf)), function (b) { return b.toString(16).padStart(2, "0"); }).join("");
  if (hash !== SHA256) { await cache.delete(WEIGHTS); throw new Error("weights checksum mismatch"); }
  return buf;
}

var ready = (async function () {
  var wasm = await fetch(new URL("needle/needle.wasm", self.location.href).href);
  if (!wasm.ok) throw new Error("engine download failed: HTTP " + wasm.status);
  M = await createNeedle({ wasmBinary: new Uint8Array(await wasm.arrayBuffer()) });
  var cact = await weights();
  var p = M._malloc(cact.length);
  M.HEAPU8.set(cact, p);
  if (M._needle_load(p, BigInt(cact.length)) < 0) throw new Error("needle_load failed");
  if (M.ccall("needle_init", "number", ["string", "string", "string"], ["", "[]", ""]) < 0) throw new Error("needle_init failed");
  dim = M.ccall("needle_embed", "number", ["string", "number", "number"], ["x", 0, 0]);
  out = M._malloc(dim * 4);
})();
ready.then(function () { postMessage({ type: "ready", dim: dim }); }, function (e) { postMessage({ type: "failed", error: String(e && e.message || e) }); });

onmessage = function (e) {
  ready.then(function () {
    var n = M.ccall("needle_embed", "number", ["string", "number", "number"], [String(e.data.text).slice(0, 1500), out, dim]);
    if (n <= 0) return postMessage({ id: e.data.id, error: "needle_embed failed" });
    var vec = Float32Array.from(new Float32Array(M.HEAPU8.buffer, out, n));
    postMessage({ id: e.data.id, vec: vec }, [vec.buffer]);
  }, function (err) { postMessage({ id: e.data.id, error: String(err && err.message || err) }); });
};
