# -*- coding: utf-8 -*-
"""v5 — duas trilhas: instrumental (principal) + jingle cantado PT (alternativa)."""
import json, time, shutil, os, urllib.request, uuid

WF = "C:/Users/userx/Documents/projs/game dev/tools/comfy/workflows/ace_turbo_api.json"
OUTDIR = "C:/Users/userx/Documents/projs/game dev/tools/comfy/portable/ComfyUI/output"
DEST = "C:/Users/userx/Documents/projs/COMFYUI/moss5/video"

TRACKS = [
 dict(out="amargo_theme", tags=("Instrumental, warm fingerstyle acoustic guitar with soft cello pad, dark "
        "chocolate mood, slow sensual samba groove, cinematic commercial bed, organic, intimate, 82 bpm, "
        "no drums, no vocals"),
      lyrics="", lang="en", key="D minor", bpm=82, seed=81),
 dict(out="amargo_jingle", tags=("Catchy brazilian samba-pop jingle, warm female vocals, playful, short "
        "hook, ad commercial music, studio quality, concise, 96 bpm"),
      lyrics=("[Hook]\nAmargo, amargo\nSetenta por cento de cacau\nAmargo, amargo\nO lado selvagem do doce"),
      lang="pt", key="D minor", bpm=96, seed=82),
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
                 .replace("__OUTPREFIX__", "moss5/" + t["out"]))
    body = json.dumps({"prompt": json.loads(wf_txt), "client_id": client}).encode()
    t0 = time.time()
    req = urllib.request.Request("http://127.0.0.1:8189/prompt", data=body,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            pid = json.load(r)["prompt_id"]
    except urllib.error.HTTPError as e:
        print(f"[{t['out']}] REJEITADO: {e.read().decode(errors='replace')[:400]}"); continue
    print(f"[{t['out']}] {pid} aguardando...", flush=True)
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
    auds = [e for o in outs.values() for k in ("audio","audios") for e in o.get(k,[]) if e.get("type")=="output"]
    if not auds:
        print(f"[{t['out']}] ERRO: {str(h.get(pid,{}).get('status'))[:300]}"); continue
    e0 = auds[0]
    dst = os.path.join(DEST, t["out"] + os.path.splitext(e0["filename"])[1])
    shutil.copyfile(os.path.join(OUTDIR, e0.get("subfolder",""), e0["filename"]), dst)
    print(f"[{t['out']}] OK em {time.time()-t0:.0f}s -> {dst}", flush=True)
print("trilhas concluidas")
