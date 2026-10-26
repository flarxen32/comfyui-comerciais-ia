# -*- coding: utf-8 -*-
"""v8 — tema + jingle MATTA (açaí)."""
import json, time, shutil, os, urllib.request, uuid

WF = "C:/Users/userx/Documents/projs/game dev/tools/comfy/workflows/ace_turbo_api.json"
OUTDIR = "C:/Users/userx/Documents/projs/game dev/tools/comfy/portable/ComfyUI/output"
DEST = "C:/Users/userx/Documents/projs/COMFYUI/moss8/video"

TRACKS = [
 dict(out="matta_theme",
      tags=("Instrumental, brazilian acoustic afro-samba, warm nylon guitar with soft berimbau-like "
            "percussion and deep hand drums, jungle morning freshness, energetic but smooth, cinematic "
            "commercial bed, 90 bpm, no vocals"),
      lyrics="", lang="en", key="E minor", bpm=90, seed=91),
 dict(out="matta_jingle",
      tags=("Catchy brazilian afro-pop jingle, warm male vocals, joyful, short hook, ad commercial music, "
            "studio quality, concise, 100 bpm"),
      lyrics=("[Hook]\nMatta, matta\nAçaí de verdade\nMatta, matta\nA força da mata na tigela"),
      lang="pt", key="E minor", bpm=100, seed=92),
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
                 .replace("__OUTPREFIX__", "moss8/" + t["out"]))
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
print("trilhas concluidas")
