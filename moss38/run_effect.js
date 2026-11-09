// v38 — submete um efeito ao ComfyUI (8189), espera terminar, copia saída e gera comparação lado-a-lado
// Uso: node run_effect.js <effect> [seed=N] [width=W] [height=H]
const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");
const { build, EFFECTS } = require("./wf_gen.js");

const SERVER = "http://127.0.0.1:8189";
const OUTDIR = path.join(__dirname, "out");
const CMPDIR = path.join(__dirname, "compare");
const SRCDIR = path.join(__dirname, "src");
const FIRDIR = path.join(__dirname, "first");
const COMFY_IN = "C:/Users/userx/Documents/projs/game dev/tools/comfy/portable/ComfyUI/input";
const COMFY_OUT = "C:/Users/userx/Documents/projs/game dev/tools/comfy/portable/ComfyUI/output";
const LOG = path.join(__dirname, "run.log");
const log = (m) => { const l = `[${new Date().toISOString().slice(11,19)}] ${m}`; console.log(l); fs.appendFileSync(LOG, l + "\n"); };

async function main() {
  const name = process.argv[2];
  if (!name || !EFFECTS[name]) { console.log("efeitos:", Object.keys(EFFECTS).join(", ")); process.exit(1); }
  const opts = {};
  for (const kv of process.argv.slice(3)) { const [k, v] = kv.split("="); opts[k] = isNaN(+v) ? v : +v; }

  // garante inputs no ComfyUI
  fs.mkdirSync(OUTDIR, { recursive: true }); fs.mkdirSync(CMPDIR, { recursive: true });
  const e = EFFECTS[name];
  for (const f of [e.src]) { const p = path.join(SRCDIR, f); if (fs.existsSync(p) && !fs.existsSync(path.join(COMFY_IN, f))) fs.copyFileSync(p, path.join(COMFY_IN, f)); }
  for (const f of [e.guideImage, e.imageInit]) { if (f) { const p = path.join(FIRDIR, f); if (fs.existsSync(p) && !fs.existsSync(path.join(COMFY_IN, f))) fs.copyFileSync(p, path.join(COMFY_IN, f)); } }

  const wf = build(name, opts);
  const body = JSON.stringify({ prompt: wf, client_id: "v38-runner" });
  log(`SUBMIT ${name} seed=${opts.seed ?? 42}`);
  const t0 = Date.now();
  const resp = await fetch(SERVER + "/prompt", { method: "POST", headers: { "Content-Type": "application/json" }, body });
  const rj = await resp.json();
  if (rj.error) { log(`ERROR submit ${name}: ${JSON.stringify(rj.error).slice(0,300)} | node_errors: ${JSON.stringify(rj.node_errors||{}).slice(0,400)}`); process.exit(2); }
  const pid = rj.prompt_id;

  while (true) {
    await new Promise(r => setTimeout(r, 5000));
    const h = await (await fetch(SERVER + "/history/" + pid)).json();
    const rec = h[pid];
    if (!rec) continue;
    if (rec.status && (rec.status.completed || rec.status.status_str === "error")) {
      const outs = [];
      for (const nid in rec.outputs || {}) { const o = rec.outputs[nid];
        for (const key of ["images", "videos", "gifs", "audio"]) if (o[key]) for (const im of o[key]) outs.push({ ...im, _key: key });
      }
      if (rec.status.status_str === "error") {
        const msgs = Object.values(rec.status.messages || {}).map(m => JSON.stringify(m)).join(" ").slice(0, 500);
        log(`FAIL exec ${name}: ${msgs}`); process.exit(3);
      }
      if (!rec.status.completed) continue;
      let vid = outs.find(o => (o.subfolder + "/" + o.filename).includes("v38/") && /\.(mp4|webm|mov)$/i.test(o.filename));
      if (!vid) vid = outs.find(o => /\.(mp4|webm|mov)$/i.test(o.filename) && o._key !== "audio" && !/^(street|desk|dancer|bw_|skate|rain_|gray_)/i.test(o.filename));
      if (!vid) { log(`DONE sem video ${name}: ${JSON.stringify(outs).slice(0,300)}`); process.exit(4); }
      const src = path.join(COMFY_OUT, vid.subfolder || "", vid.filename);
      const dst = path.join(OUTDIR, name + ".mp4");
      fs.copyFileSync(src, dst);
      const min = ((Date.now() - t0) / 60000).toFixed(1);
      log(`OK ${name} em ${min}min -> ${dst}`);
      // comparação lado a lado (original | efeito)
      const orig = e.imageInit ? path.join(FIRDIR, e.imageInit) : path.join(SRCDIR, e.src);
      try {
        const isImg = /\.png|\.jpe?g$/i.test(orig);
        const pre = isImg ? "-loop 1 -t 5.04" : "";
        const frames = isImg ? "" : "-frames:v 121";
        execSync(`ffmpeg -hide_banner -loglevel error -y ${pre} -i "${orig}" -i "${dst}" -filter_complex "[0:v]scale=480:272:force_original_aspect_ratio=decrease,pad=480:272:(ow-iw)/2:(oh-ih)/2,setsar=1[a];[1:v]scale=480:272:force_original_aspect_ratio=decrease,pad=480:272:(ow-iw)/2:(oh-ih)/2,setsar=1[b];[a][b]hstack=inputs=2" ${frames} -r 24 -c:v libx264 -crf 20 -pix_fmt yuv420p "${path.join(CMPDIR, name + "_compare.mp4")}"`);
        log(`COMPARE ok ${name}`);
      } catch (err) { log(`COMPARE fail ${name}: ${String(err.message).slice(0,150)}`); }
      process.exit(0);
    }
  }
}
main().catch(e => { log("FATAL " + e.message); process.exit(9); });
