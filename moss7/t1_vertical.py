# -*- coding: utf-8 -*-
"""T1 v7: Turbo em vertical nativa 1088x1920 (9:16) — 121f."""
import json, time, shutil, os, subprocess, urllib.request, uuid

TOOLS = "C:/Users/userx/Documents/projs/game dev/tools/comfy"
INPUT = TOOLS + "/portable/ComfyUI/input"
OUTDIR = TOOLS + "/portable/ComfyUI/output"
BASE = "C:/Users/userx/Documents/projs/COMFYUI"
WF = TOOLS + "/workflows/wan22_turbo_gguf_api.json"
GGUF = "Wan2_2-TI2V-5B-Turbo-Q5_K_M.gguf"

w, h = 1088, 1920
subprocess.run(["ffmpeg","-y","-v","error","-i",f"{BASE}/moss5/stills/s5_pour.png",
                "-vf",f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}",
                os.path.join(INPUT,"t1_vert.png")], check=True)
prompt = ("Thick melted dark chocolate pours in a slow glossy ribbon onto a dark stone surface, folding "
          "and pooling with satin sheen, warm side light, dark background with soft bokeh. Camera: locked "
          "tripod macro, vertical composition.")
tpl = open(WF, encoding="utf-8").read()
wf_txt = (tpl.replace("__UNETGGUF__", GGUF).replace("__CFG__","1.0").replace("__SAMPLER__","euler")
             .replace("__IMAGE__", "t1_vert.png")
             .replace("__PROMPT__", json.dumps(prompt)[1:-1])
             .replace("__WIDTH__", str(w)).replace("__HEIGHT__", str(h))
             .replace("__LENGTH__","121").replace("__STEPS__","4")
             .replace("__SEED__", "8301").replace("__OUTPREFIX__","moss7/t1_vertical"))
body = json.dumps({"prompt": json.loads(wf_txt), "client_id": str(uuid.uuid4())}).encode()
t0 = time.time()
req = urllib.request.Request("http://127.0.0.1:8189/prompt", data=body, headers={"Content-Type":"application/json"})
with urllib.request.urlopen(req) as r: pid = json.load(r)["prompt_id"]
print(f"[t1_vert] {pid} (1088x1920)", flush=True)
hh = {}
while time.time()-t0 < 1500:
    time.sleep(6)
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:8189/history/{pid}") as r: hh = json.load(r)
    except Exception: continue
    if pid in hh:
        st = hh[pid].get("status",{})
        if st.get("completed") or st.get("status_str")=="error": break
outs = hh.get(pid,{}).get("outputs",{})
vids = [e for o in outs.values() for k in ("videos","gifs","images") for e in o.get(k,[]) if e.get("type")=="output"]
if vids:
    e0 = vids[0]
    shutil.copyfile(os.path.join(OUTDIR, e0.get("subfolder",""), e0["filename"]), f"{BASE}/moss7/video/t1_vertical.mp4")
    print(f"[t1_vert] OK em {time.time()-t0:.0f}s")
else:
    print("[t1_vert] ERRO:", str(hh.get(pid,{}).get('status'))[:300])
