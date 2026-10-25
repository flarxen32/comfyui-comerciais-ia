# -*- coding: utf-8 -*-
"""v13 — trilha NASCENTE via Ace-Step 1.5 turbo (tema instrumental, ~20s, corta p/ bed 10s no build)."""
import json, time, shutil, os, urllib.request, uuid

WF = "C:/Users/userx/Documents/projs/game dev/tools/comfy/workflows/ace_turbo_api.json"
OUTDIR = "C:/Users/userx/Documents/projs/game dev/tools/comfy/portable/ComfyUI/output"
DEST = "C:/Users/userx/Documents/projs/COMFYUI/moss13/video"
LOG  = "C:/Users/userx/Documents/projs/COMFYUI/moss13/chain.log"

TAGS = ("fresh acoustic commercial jingle, clean water, rain drops, gentle piano and acoustic guitar, "
        "brazilian chill, uplifting, minimal, pristine, advertising")
LYRICS = ""

tpl = open(WF, encoding="utf-8").read()
s = (tpl.replace("__TAGS__", json.dumps(TAGS)[1:-1])
        .replace('"lyrics": ""', '"lyrics": ' + json.dumps(LYRICS))
        .replace('"seed": 71', '"seed": 131313')
        .replace("__OUTPREFIX__", "moss13/nascente_theme"))
body = json.dumps({"prompt": json.loads(s), "client_id": str(uuid.uuid4())}).encode("utf-8")
t0 = time.time()
req = urllib.request.Request("http://127.0.0.1:8189/prompt", data=body, headers={"Content-Type":"application/json"})
with urllib.request.urlopen(req) as r: pid = json.load(r)["prompt_id"]
hh = {}
while True:
    time.sleep(5)
    with urllib.request.urlopen(f"http://127.0.0.1:8189/history/{pid}") as r: h = json.load(r)
    if pid in h:
        hh = h[pid]
        st = hh.get("status", {})
        if st.get("completed") or st.get("status_str") == "error": break
    if time.time()-t0 > 1200: print("TIMEOUT"); break
auds = [a for o in hh.get("outputs", {}).values() for a in o.get("audio", [])]
if not auds:
    print("ERRO:", str(hh.get("status"))[:300]); raise SystemExit(1)
a = auds[0]
os.makedirs(DEST, exist_ok=True)
src = os.path.join(OUTDIR, a.get("subfolder",""), a["filename"])
shutil.copyfile(src, os.path.join(DEST, "nascente_theme.flac"))
msg = f"[nascente_theme] OK {time.time()-t0:.0f}s"
print(msg)
with open(LOG, "a", encoding="utf-8") as f: f.write(msg + "\n")
