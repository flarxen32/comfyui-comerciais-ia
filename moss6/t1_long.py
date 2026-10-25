# -*- coding: utf-8 -*-
"""T1 v6: take longo contínuo — Turbo 1080p, 241 frames (10 s).
Coerência avaliada por QA em frames 2s/5s/8s."""
import json, time, shutil, os, subprocess, urllib.request, uuid

TOOLS = "C:/Users/userx/Documents/projs/game dev/tools/comfy"
INPUT = TOOLS + "/portable/ComfyUI/input"
OUTDIR = TOOLS + "/portable/ComfyUI/output"
BASE = "C:/Users/userx/Documents/projs/COMFYUI"
WF = TOOLS + "/workflows/wan22_turbo_gguf_api.json"
GGUF = "Wan2_2-TI2V-5B-Turbo-Q5_K_M.gguf"

w, h = 1920, 1088
subprocess.run(["ffmpeg","-y","-v","error","-i",f"{BASE}/moss5/stills/s5_pour.png",
                "-vf",f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}",
                os.path.join(INPUT,"t1_long.png")], check=True)
prompt = ("Thick melted dark chocolate pours in a slow glossy ribbon onto a dark stone surface, the "
          "chocolate folding and pooling with a rich satin sheen for ten continuous seconds, the pour "
          "slowing down and settling as the pool grows wider, dramatic warm side light, dark background "
          "with soft bokeh. Camera: locked tripod macro, one continuous shot.")
tpl = open(WF, encoding="utf-8").read()
wf_txt = (tpl.replace("__UNETGGUF__", GGUF).replace("__CFG__","1.0").replace("__SAMPLER__","euler")
             .replace("__IMAGE__", "t1_long.png")
             .replace("__PROMPT__", json.dumps(prompt)[1:-1])
             .replace("__WIDTH__", str(w)).replace("__HEIGHT__", str(h))
             .replace("__LENGTH__","241").replace("__STEPS__","4")
             .replace("__SEED__", "8201").replace("__OUTPREFIX__","moss6/t1_long10s"))
body = json.dumps({"prompt": json.loads(wf_txt), "client_id": str(uuid.uuid4())}).encode()
t0 = time.time()
req = urllib.request.Request("http://127.0.0.1:8189/prompt", data=body, headers={"Content-Type":"application/json"})
with urllib.request.urlopen(req) as r: pid = json.load(r)["prompt_id"]
print(f"[t1_long] {pid} (241f@1080p — pode levar ~45min)", flush=True)
h = {}
while time.time()-t0 < 5400:
    time.sleep(10)
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:8189/history/{pid}") as r: h = json.load(r)
    except Exception: continue
    if pid in h:
        st = h[pid].get("status",{})
        if st.get("completed") or st.get("status_str")=="error": break
outs = h.get(pid,{}).get("outputs",{})
vids = [e for o in outs.values() for k in ("videos","gifs","images") for e in o.get(k,[]) if e.get("type")=="output"]
if vids:
    e0 = vids[0]
    shutil.copyfile(os.path.join(OUTDIR, e0.get("subfolder",""), e0["filename"]), f"{BASE}/moss6/video/t1_long10s.mp4")
    print(f"[t1_long] OK em {time.time()-t0:.0f}s -> {BASE}/moss6/video/t1_long10s.mp4")
else:
    print("[t1_long] ERRO:", str(h.get(pid,{}).get('status'))[:300])
