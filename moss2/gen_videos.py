# -*- coding: utf-8 -*-
"""Matriz A/B v2 — compara engines no shot hero (s2_pour).
Uso: python gen_videos.py [take ...]   (sem args = todos)
Engines: h3 (MiniMax H3 i2v, 832x480) · wan (Wan 2.2 TI2V-5B, 1280x704)"""
import json, time, shutil, sys, os, subprocess, urllib.request, uuid

TOOLS = "C:/Users/userx/Documents/projs/game dev/tools/comfy"
WF_H3 = TOOLS + "/workflows/minimax_h3_i2v_api.json"
WF_WAN = TOOLS + "/workflows/wan22_i2v_api.json"
INPUT = TOOLS + "/portable/ComfyUI/input"
OUTDIR = TOOLS + "/portable/ComfyUI/output"
DEST = "C:/Users/userx/Documents/projs/COMFYUI/moss2/video"
STILLS = "C:/Users/userx/Documents/projs/COMFYUI/moss2/stills"

POUR_PROMPT = ("Static camera macro shot: espresso pours from a bottomless portafilter into a small ceramic "
               "cup, the golden crema swirls and settles, delicate steam curls upward, dark café background "
               "with warm bokeh lights. The cup, portafilter and stream of coffee stay sharp, stable and "
               "consistent. Camera: locked tripod macro, no camera movement. Ambient audio: espresso machine "
               "hum, coffee pouring, soft café ambience.")

TAKES = [
    dict(name="ab_h3_4st", engine="h3", still="s2_pour", prompt=POUR_PROMPT,
         w=832, h=480, length=121, steps=4, seed=3301),
    dict(name="ab_h3_8st", engine="h3", still="s2_pour", prompt=POUR_PROMPT,
         w=832, h=480, length=121, steps=8, seed=3302),
    dict(name="ab_wan20", engine="wan", still="s2_pour", prompt=POUR_PROMPT,
         w=1280, h=704, length=121, steps=20, seed=3303),
]

client = str(uuid.uuid4())
os.makedirs(DEST, exist_ok=True)
sel = sys.argv[1:] or [t["name"] for t in TAKES]

for t in [x for x in TAKES if x["name"] in sel]:
    # 1) frame de partida no res exato do engine
    src = f"{STILLS}/{t['still']}.png"
    fname = f"{t['name']}_{t['w']}x{t['h']}.png"
    fpath = os.path.join(INPUT, fname)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src,
                    "-vf", f"scale={t['w']}:{t['h']}:force_original_aspect_ratio=increase,crop={t['w']}:{t['h']}",
                    fpath], check=True)
    # 2) workflow
    wf_file = WF_H3 if t["engine"] == "h3" else WF_WAN
    tpl = open(wf_file, encoding="utf-8").read()
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
    print(f"[{t['name']}] {t['engine']} {t['steps']}st {t['w']}x{t['h']} enfileirado {pid}; aguardando...", flush=True)
    h = {}
    while True:
        time.sleep(6)
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:8189/history/{pid}") as r:
                h = json.load(r)
        except Exception:
            continue
        if pid in h:
            st = h[pid].get("status", {})
            if st.get("completed") or st.get("status_str") == "error":
                break
        if time.time() - t0 > 3600:
            print(f"[{t['name']}] TIMEOUT 60min"); break
    outs = h.get(pid, {}).get("outputs", {})
    vids = []
    for o in outs.values():
        for k in ("videos", "gifs", "images"):
            for e in o.get(k, []):
                if e.get("type") == "output":
                    vids.append(e)
    if not vids:
        print(f"[{t['name']}] ERRO sem saida: {str(h[pid].get('status'))[:400]}"); continue
    e0 = vids[0]
    src_v = os.path.join(OUTDIR, e0.get("subfolder", ""), e0["filename"])
    dst_v = os.path.join(DEST, t["name"] + os.path.splitext(e0["filename"])[1])
    shutil.copyfile(src_v, dst_v)
    print(f"[{t['name']}] OK em {time.time()-t0:.0f}s -> {dst_v}", flush=True)
print("concluido")
