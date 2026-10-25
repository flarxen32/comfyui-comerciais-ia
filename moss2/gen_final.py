# -*- coding: utf-8 -*-
"""Takes finais do comercial SERRA v2.
Uso: python gen_final.py [engine] [take ...]
  engine: wan (1280x704) | h3 (832x480)  — default wan
Takes: cherry, beans, pour, cup (+ audio_h3 para trilha ambiente via H3@4st)"""
import json, time, shutil, sys, os, subprocess, urllib.request, uuid

TOOLS = "C:/Users/userx/Documents/projs/game dev/tools/comfy"
WFS = {"h3": TOOLS + "/workflows/minimax_h3_i2v_api.json",
       "wan": TOOLS + "/workflows/wan22_i2v_api.json"}
INPUT = TOOLS + "/portable/ComfyUI/input"
OUTDIR = TOOLS + "/portable/ComfyUI/output"
DEST = "C:/Users/userx/Documents/projs/COMFYUI/moss2/video"
STILLS = "C:/Users/userx/Documents/projs/COMFYUI/moss2/stills"

SHOTS = {
 "cherry": ("Static macro shot of ripe red coffee cherries on a branch with dew droplets, a very gentle "
            "breeze makes the leaves sway almost imperceptibly, golden dawn light slowly brightening through "
            "highland mist, blurred plantation behind. The cherries stay sharp and stable. Camera: locked "
            "tripod, no movement. Ambient audio: highland birdsong, soft wind, distant farm sounds."),
 "beans": ("Roasted coffee beans cascade from above into a handcrafted ceramic bowl, bouncing softly, the "
           "pile growing, a faint dust of grounds in the warm window light. The beans fall with natural "
           "physics, the bowl stays sharp and centered. Camera: locked tripod close-up. Ambient audio: "
           "coffee beans rattling into ceramic, quiet room tone."),
 "pour": ("Espresso pours from a bottomless portafilter into a small ceramic cup, the golden crema swirls "
          "and settles, delicate steam curls upward, dark café background with warm bokeh lights. The cup, "
          "portafilter and stream of coffee stay sharp, stable and consistent. Camera: locked tripod macro, "
          "no camera movement. Ambient audio: espresso machine hum, coffee pouring, soft café ambience."),
 "cup": ("Hands in a chunky knit sweater hold a steaming ceramic coffee cup by a bright morning window, the "
         "steam rises slowly through a sunbeam, the fingers shift gently around the warm cup in a small "
         "comforting motion, cozy café mood. The hands stay anatomically consistent. Camera: locked tripod "
         "medium shot. Ambient audio: soft morning ambience, a gentle cup clink, quiet piano notes."),
}

ENGINE = (sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] in ("wan", "h3") else "wan")
sel = [a for a in sys.argv[2:] if a in SHOTS] or list(SHOTS)

RES = {"wan": (1280, 704, 20), "h3": (832, 480, 8)}
w, h, steps = RES[ENGINE]

TAKES = []
for name in sel:
    TAKES.append(dict(name=f"s2v2_{ENGINE}_{name}", engine=ENGINE, still=f"s2_{name}",
                      prompt=SHOTS[name], w=w, h=h, length=121, steps=steps,
                      seed=4100 + list(SHOTS).index(name)))

client = str(uuid.uuid4())
os.makedirs(DEST, exist_ok=True)

for t in TAKES:
    src = f"{STILLS}/{t['still']}.png"
    fname = f"{t['name']}_{t['w']}x{t['h']}.png"
    fpath = os.path.join(INPUT, fname)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src,
                    "-vf", f"scale={t['w']}:{t['h']}:force_original_aspect_ratio=increase,crop={t['w']}:{t['h']}",
                    fpath], check=True)
    tpl = open(WFS[t["engine"]], encoding="utf-8").read()
    wf_txt = (tpl.replace("__IMAGE__", fname)
                 .replace("__PROMPT__", json.dumps(t["prompt"])[1:-1])
                 .replace("__WIDTH__", str(t["w"])).replace("__HEIGHT__", str(t["h"]))
                 .replace("__LENGTH__", str(t["length"])).replace("__STEPS__", str(t["steps"]))
                 .replace("__SEED__", str(t["seed"]))
                 .replace("__OUTPREFIX__", "moss2/" + t["name"]))
    body = json.dumps({"prompt": json.loads(wf_txt), "client_id": client}).encode("utf-8")
    t0 = time.time()
    req = urllib.request.Request("http://127.0.0.1:8189/prompt", data=body,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            pid = json.load(r)["prompt_id"]
    except urllib.error.HTTPError as e:
        print(f"[{t['name']}] REJEITADO: {e.read().decode(errors='replace')[:500]}"); continue
    print(f"[{t['name']}] enfileirado {pid}; aguardando...", flush=True)
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
    src_v = os.path.join(OUTDIR, e0.get("subfolder", ""), e0["filename"])
    dst_v = os.path.join(DEST, t["name"] + os.path.splitext(e0["filename"])[1])
    shutil.copyfile(src_v, dst_v)
    print(f"[{t['name']}] OK em {time.time()-t0:.0f}s -> {dst_v}", flush=True)
print("concluido")
