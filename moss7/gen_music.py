# -*- coding: utf-8 -*-
"""v7 — tema choro + jingle CANAVIAL."""
import json, time, shutil, os, urllib.request, uuid

WF = "C:/Users/userx/Documents/projs/game dev/tools/comfy/workflows/ace_turbo_api.json"
OUTDIR = "C:/Users/userx/Documents/projs/game dev/tools/comfy/portable/ComfyUI/output"
DEST = "C:/Users/userx/Documents/projs/COMFYUI/moss7/video"

TRACKS = [
 dict(out="canavial_theme",
      tags=("Instrumental, brazilian choro with cavaquinho, pandeiro light percussion and warm accordion, "
            "rustic countryside joy, golden hour mood, elegant commercial bed, 88 bpm, no vocals"),
      lyrics="", lang="en", key="G major", bpm=88, seed=71),
 dict(out="canavial_jingle",
      tags=("Catchy brazilian samba jingle, warm male vocals, joyful, short hook, ad commercial music, "
            "studio quality, concise, 98 bpm"),
      lyrics=("[Hook]\nCanavial, canavial\nA aguardente da terra\nCanavial, canavial\nEnvelhecida devagar"),
      lang="pt", key="G major", bpm=98, seed=72),
]
client = str(uuid.uuid4())
os.makedirs(DEST, exist_ok=True)
for t in TRACKS:
    tpl = open(WF, encoding="utf-8").read()
    wf_txt = (tpl.replace("__TAGS__", json.dumps(t["tags"])[1:-1])
                 .replace('"lyrics": ""', '"lyrics": ' + json.dumps(t["lyrics"], ensure_ascii=False))
                 .replace('"seed": 71', f'"seed": {t["seed"]}')
                 .replace('"bpm": 76', f'"bpm": {t["bpm"]}')
                 .replace('"language": "en"', f'"language": "{t["lang"]}"')
                 .replace('"keyscale": "E major"', f'"keyscale": "{t["key"]}"')
                 .replace("__OUTPREFIX__", "moss7/" + t["out"]))
    body = json.dumps({"prompt": json.loads(wf_txt), "client_id": client}).encode()
    req = urllib.request.Request("http://127.0.0.1:8189/prompt", data=body, headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req) as r: pid = json.load(r)["prompt_id"]
    print(f"[{t['out']}] aguardando...", flush=True)
    h = {}; t0 = time.time()
    while time.time()-t0 < 900:
        time.sleep(5)
        with urllib.request.urlopen(f"http://127.0.0.1:8189/history/{pid}") as r: h = json.load(r)
        if pid in h:
            st = h[pid].get("status",{})
            if st.get("completed") or st.get("status_str")=="error": break
    outs = h.get(pid,{}).get("outputs",{})
    auds = [e for o in outs.values() for k in ("audio","audios") for e in o.get(k,[]) if e.get("type")=="output"]
    if not auds:
        print(f"[{t['out']}] ERRO"); continue
    e0 = auds[0]
    shutil.copyfile(os.path.join(OUTDIR, e0.get("subfolder",""), e0["filename"]),
                    os.path.join(DEST, t["out"] + os.path.splitext(e0["filename"])[1]))
    print(f"[{t['out']}] OK {time.time()-t0:.0f}s", flush=True)
