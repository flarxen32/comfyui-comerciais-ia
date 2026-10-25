# -*- coding: utf-8 -*-
"""Stills v8 — MATTA açaí, dois formatos (1600x900 e 900x1600)."""
import json, time, shutil, sys, os, urllib.request, uuid

WF = "C:/Users/userx/Documents/projs/game dev/tools/comfy/workflows/moss_image_t2i_api.json"
OUTDIR = "C:/Users/userx/Documents/projs/game dev/tools/comfy/portable/ComfyUI/output"
DEST = "C:/Users/userx/Documents/projs/COMFYUI/moss8/stills"
NEG = "nsfw, worst quality, bad anatomy, watermark, jpeg artifact"

def endcard(w, h):
    if w > h:
        return {"summary": {"meta": ["poster"], "canvas": "single", "caption": "A minimalist açaí poster on a deep purple-black background with a full açaí bowl in the center and the brand name MATTA in large cream uppercase letters."},
                "items": [
                 {"label": "text", "caption": "Huge cream uppercase word with generous letter spacing, centered near the top.", "text": "MATTA", "bbox": [-400, -360, -280, 360]},
                 {"label": "object", "caption": "A ceramic bowl of thick deep-purple açaí topped with granola, banana slices and a few açaí berries, centered, soft studio light.", "bbox": [-60, -170, 220, 170]},
                 {"label": "text", "caption": "Small cream uppercase tracking-wide line under the bowl.", "text": "AÇAÍ DE VERDADE · 100% NATURAL", "bbox": [260, -330, 300, 330]},
                 {"label": "text", "caption": "Small italic cream tagline centered near the bottom.", "text": "A força da mata na tigela.", "bbox": [340, -400, 395, 400]}],
                "bbox_coord_space": "abs_centralized", "bbox_format": "yxyx"}
    return {"summary": {"meta": ["poster"], "canvas": "single", "caption": "A minimalist açaí poster on a deep purple-black background with a full açaí bowl in the center and the brand name MATTA in large cream uppercase letters."},
            "items": [
             {"label": "text", "caption": "Huge cream uppercase word with generous letter spacing, centered in the upper third.", "text": "MATTA", "bbox": [-660, -360, -520, 360]},
             {"label": "object", "caption": "A ceramic bowl of thick deep-purple açaí topped with granola and banana slices, centered in the middle, soft studio light.", "bbox": [-260, -200, 420, 200]},
             {"label": "text", "caption": "Small cream uppercase tracking-wide line under the bowl.", "text": "AÇAÍ DE VERDADE · 100% NATURAL", "bbox": [520, -400, 580, 400]},
             {"label": "text", "caption": "Small italic cream tagline near the bottom.", "text": "A força da mata na tigela.", "bbox": [660, -400, 730, 400]}],
            "bbox_coord_space": "abs_centralized", "bbox_format": "yxyx"}

BASE = {
 "berries": ("Macro photograph of deep purple açaí berries filling a woven basket, a few berries tumbling "
             "out, glossy skins catching warm morning jungle light, blurred green canopy behind, shallow "
             "depth of field, deep purple and green palette, commercial food cinematography, photorealistic, "
             "ultra detailed"),
 "pour": ("Macro photograph of thick deep-purple açaí being poured from a blender jug into a ceramic bowl "
          "in a slow heavy ribbon, the creamy texture folding glossy and dense, granola and banana slices "
          "waiting beside, warm natural window light, dark wooden counter, commercial food advertising, "
          "photorealistic, ultra sharp"),
 "bowl": ("Overhead photograph of a finished açaí bowl on dark wood, thick purple açaí topped with crunchy "
          "granola, banana slices and a drizzle of honey, a spoon resting on the rim, soft morning light, "
          "shallow depth of field, artisanal café mood, commercial food photography, photorealistic"),
 "spoon": ("Close-up photograph of a wooden spoon lifting a curl of thick purple açaí with a slow glossy "
           "drip falling back into the bowl, granola crumbs suspended, warm side light, dark moody "
           "background with soft bokeh, commercial food cinematography, photorealistic, ultra sharp"),
}
STILLS = []
for i, (k, p) in enumerate(BASE.items()):
    STILLS.append(dict(name=f"s8_{k}", seed=8100+i, prompt=p, w=1600, h=900))
    STILLS.append(dict(name=f"s8_{k}_v", seed=8100+i, prompt=p, w=900, h=1600))
STILLS.append(dict(name="s8_endcard_h", seed=8190, prompt=json.dumps(endcard(1600,900), ensure_ascii=False), w=1600, h=900))
STILLS.append(dict(name="s8_endcard_v", seed=8191, prompt=json.dumps(endcard(900,1600), ensure_ascii=False), w=900, h=1600))

tpl = open(WF, encoding="utf-8").read()
client = str(uuid.uuid4())
sel = sys.argv[1:] or [s["name"] for s in STILLS]
os.makedirs(DEST, exist_ok=True)
for s in [x for x in STILLS if x["name"] in sel]:
    wf_txt = (tpl.replace("__PROMPT__", json.dumps(s["prompt"], ensure_ascii=False)[1:-1])
                 .replace("__NEGATIVE__", json.dumps(NEG)[1:-1])
                 .replace("__WIDTH__", str(s["w"])).replace("__HEIGHT__", str(s["h"]))
                 .replace("__SEED__", str(s["seed"]))
                 .replace("__OUTPREFIX__", "moss8/" + s["name"]))
    body = json.dumps({"prompt": json.loads(wf_txt), "client_id": client}).encode("utf-8")
    t0 = time.time()
    req = urllib.request.Request("http://127.0.0.1:8189/prompt", data=body, headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req) as r: pid = json.load(r)["prompt_id"]
    while True:
        time.sleep(5)
        with urllib.request.urlopen(f"http://127.0.0.1:8189/history/{pid}") as r: h = json.load(r)
        if pid in h:
            st = h[pid].get("status", {})
            if st.get("completed") or st.get("status_str") == "error": break
        if time.time()-t0 > 900: print(f"[{s['name']}] TIMEOUT"); break
    outs = h.get(pid, {}).get("outputs", {})
    imgs = [i for o in outs.values() for i in o.get("images", [])]
    if not imgs:
        print(f"[{s['name']}] ERRO: {str(h.get(pid,{}).get('status'))[:200]}"); continue
    img = imgs[0]
    shutil.copyfile(os.path.join(OUTDIR, img.get("subfolder",""), img["filename"]), os.path.join(DEST, s["name"]+".png"))
    print(f"[{s['name']}] OK {s['w']}x{s['h']} {time.time()-t0:.0f}s", flush=True)
print("concluido")
