# -*- coding: utf-8 -*-
"""v3 — takes Wan 2.2 TI2V-5B Turbo GGUF (4 steps, CFG 1, 704p).
Uso: python gen_videos.py [take ...]  (sem args = todos)
Inclui ab_turbo4: benchmark do Turbo no MESMO still do SERRA (s2_pour)
para comparação direta com ab_wan20/ab_h3_8st da v2."""
import json, time, shutil, sys, os, subprocess, urllib.request, uuid

TOOLS = "C:/Users/userx/Documents/projs/game dev/tools/comfy"
WF = TOOLS + "/workflows/wan22_turbo_gguf_api.json"
INPUT = TOOLS + "/portable/ComfyUI/input"
OUTDIR = TOOLS + "/portable/ComfyUI/output"
BASE = "C:/Users/userx/Documents/projs/COMFYUI"
GGUF = "Wan2_2-TI2V-5B-Turbo-Q5_K_M.gguf"

SHOTS = {
 "hops": ("Macro of fresh green hop cones in light rain, raindrops falling gently, leaves swaying softly, "
          "soft overcast light slowly brightening. Camera: very slow dolly-in, almost imperceptible."),
 "bottle": ("Static close-up of a matte dark craft beer bottle covered in condensation droplets, one droplet "
            "slides down the label, the faint mist drifts in the dark background. The label reading GAROA "
            "stays sharp, stable and legible. Camera: locked tripod, no movement."),
 "pour": ("Amber IPA pours from a bottle into a tall tilted glass, a cascade of thick creamy foam builds and "
          "swirls, fine bubbles rise through the golden liquid. The bottle, glass and foam stay physically "
          "consistent. Camera: locked tripod macro, no camera movement."),
 "glass": ("A tall glass of amber IPA with thick foam on a rustic wooden table, rain runs down the window "
           "behind creating moving bokeh, condensation glitters on the glass. Camera: very slow dolly-in."),
}

TAKES = [dict(name="ab_turbo4", still=f"{BASE}/moss2/stills/s2_pour", res=(1280, 704),
              prompt=("Static camera macro shot: espresso pours from a bottomless portafilter into a small "
                      "ceramic cup, the golden crema swirls and settles, delicate steam curls upward, dark "
                      "café background with warm bokeh lights. The cup, portafilter and stream of coffee "
                      "stay sharp, stable and consistent. Camera: locked tripod macro, no camera movement."),
              seed=3304, length=121, steps=4, cfg=1.0, sampler="euler")]
for i, (k, v) in enumerate(SHOTS.items()):
    TAKES.append(dict(name=f"s3v3_{k}", still=f"{BASE}/moss3/stills/s3_{k}", res=(1280, 704),
                      prompt=v, seed=5100 + i, length=121, steps=4, cfg=1.0, sampler="euler"))

client = str(uuid.uuid4())
os.makedirs(f"{BASE}/moss3/video", exist_ok=True)
sel = sys.argv[1:] or [t["name"] for t in TAKES]

for t in [x for x in TAKES if x["name"] in sel]:
    w, h = t["res"]
    fname = f"{t['name']}_{w}x{h}.png"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", t["still"] + ".png",
                    "-vf", f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}",
                    os.path.join(INPUT, fname)], check=True)
    tpl = open(WF, encoding="utf-8").read()
    wf_txt = (tpl.replace("__UNETGGUF__", GGUF).replace("__IMAGE__", fname)
                 .replace("__PROMPT__", json.dumps(t["prompt"])[1:-1])
                 .replace("__WIDTH__", str(w)).replace("__HEIGHT__", str(h))
                 .replace("__LENGTH__", str(t["length"])).replace("__STEPS__", str(t["steps"]))
                 .replace("__CFG__", str(t["cfg"])).replace("__SAMPLER__", t["sampler"])
                 .replace("__SEED__", str(t["seed"]))
                 .replace("__OUTPREFIX__", "moss3/" + t["name"]))
    body = json.dumps({"prompt": json.loads(wf_txt), "client_id": client}).encode("utf-8")
    t0 = time.time()
    req = urllib.request.Request("http://127.0.0.1:8189/prompt", data=body,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            pid = json.load(r)["prompt_id"]
    except urllib.error.HTTPError as e:
        print(f"[{t['name']}] REJEITADO: {e.read().decode(errors='replace')[:500]}"); continue
    print(f"[{t['name']}] turbo 4st enfileirado {pid}; aguardando...", flush=True)
    hh = {}
    while True:
        time.sleep(6)
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:8189/history/{pid}") as r:
                hh = json.load(r)
        except Exception:
            continue
        if pid in hh:
            st = hh[pid].get("status", {})
            if st.get("completed") or st.get("status_str") == "error":
                break
        if time.time() - t0 > 3600:
            print(f"[{t['name']}] TIMEOUT"); break
    outs = hh.get(pid, {}).get("outputs", {})
    vids = []
    for o in outs.values():
        for k in ("videos", "gifs", "images"):
            for e in o.get(k, []):
                if e.get("type") == "output":
                    vids.append(e)
    if not vids:
        print(f"[{t['name']}] ERRO sem saida: {str(hh[pid].get('status'))[:400]}"); continue
    e0 = vids[0]
    dst = f"{BASE}/moss3/video/{t['name']}" + os.path.splitext(e0["filename"])[1]
    shutil.copyfile(os.path.join(OUTDIR, e0.get("subfolder", ""), e0["filename"]), dst)
    print(f"[{t['name']}] OK em {time.time()-t0:.0f}s -> {dst}", flush=True)
print("concluido")
