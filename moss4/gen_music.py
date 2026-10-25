# -*- coding: utf-8 -*-
"""v4 — trilha com Ace-Step 1.5 turbo (instrumental 20 s)."""
import json, time, shutil, os, urllib.request, uuid

WF = "C:/Users/userx/Documents/projs/game dev/tools/comfy/workflows/ace_turbo_api.json"
OUTDIR = "C:/Users/userx/Documents/projs/game dev/tools/comfy/portable/ComfyUI/output"
DEST = "C:/Users/userx/Documents/projs/COMFYUI/moss4/video"

TAGS = ("Instrumental, warm fingerstyle acoustic guitar, soft ambient folk, intimate cozy morning mood, "
        "slow golden honey light, gentle cinematic commercial bed, organic, warm, tender, 76 bpm, no drums, "
        "no vocals, delicate picked strings, soft pads")

tpl = open(WF, encoding="utf-8").read()
wf_txt = (tpl.replace("__TAGS__", json.dumps(TAGS)[1:-1])
             .replace("__OUTPREFIX__", "moss4/amber_theme"))
body = json.dumps({"prompt": json.loads(wf_txt), "client_id": str(uuid.uuid4())}).encode()
t0 = time.time()
req = urllib.request.Request("http://127.0.0.1:8189/prompt", data=body,
                             headers={"Content-Type": "application/json"})
try:
    with urllib.request.urlopen(req) as r:
        pid = json.load(r)["prompt_id"]
except urllib.error.HTTPError as e:
    print("REJEITADO:", e.read().decode(errors="replace")[:600]); raise SystemExit(1)
print(f"[theme] {pid} aguardando...", flush=True)
h = {}
while time.time() - t0 < 1800:
    time.sleep(5)
    with urllib.request.urlopen(f"http://127.0.0.1:8189/history/{pid}") as r:
        h = json.load(r)
    if pid in h:
        st = h[pid].get("status", {})
        if st.get("completed") or st.get("status_str") == "error":
            break
outs = h.get(pid, {}).get("outputs", {})
auds = []
for o in outs.values():
    for k in ("audio", "audios", "images", "gifs", "videos"):
        for e in o.get(k, []):
            if e.get("type") == "output":
                auds.append(e)
if not auds:
    print("ERRO sem saida:", str(h.get(pid, {}).get("status"))[:300]); raise SystemExit(1)
e0 = auds[0]
os.makedirs(DEST, exist_ok=True)
src = os.path.join(OUTDIR, e0.get("subfolder", ""), e0["filename"])
dst = os.path.join(DEST, "amber_theme" + os.path.splitext(e0["filename"])[1])
shutil.copyfile(src, dst)
print(f"[theme] OK em {time.time()-t0:.0f}s -> {dst}")
