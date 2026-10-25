# -*- coding: utf-8 -*-
"""Stills v9 — SOL suco de laranja, dois formatos."""
import json, time, shutil, sys, os, urllib.request, uuid

WF = "C:/Users/userx/Documents/projs/game dev/tools/comfy/workflows/moss_image_t2i_api.json"
OUTDIR = "C:/Users/userx/Documents/projs/game dev/tools/comfy/portable/ComfyUI/output"
DEST = "C:/Users/userx/Documents/projs/COMFYUI/moss9/stills"
NEG = "nsfw, worst quality, bad anatomy, watermark, jpeg artifact"

def endcard(w, h):
    if w > h:
        return {"summary": {"meta": ["poster"], "canvas": "single", "caption": "A minimalist orange juice poster on a deep warm orange background with a tall glass of fresh orange juice in the center and the brand name SOL in large cream uppercase letters."},
                "items": [
                 {"label": "text", "caption": "Huge cream uppercase word with generous letter spacing, centered near the top.", "text": "SOL", "bbox": [-400, -300, -280, 300]},
                 {"label": "object", "caption": "A tall glass of vivid orange juice with a fresh orange slice on the rim, centered, bright morning light.", "bbox": [-60, -130, 220, 130]},
                 {"label": "text", "caption": "Small cream uppercase tracking-wide line under the glass.", "text": "LARANJA · 100% NATURAL", "bbox": [260, -260, 300, 260]},
                 {"label": "text", "caption": "Small italic cream tagline centered near the bottom.", "text": "Feito na hora. De verdade.", "bbox": [340, -400, 395, 400]}],
                "bbox_coord_space": "abs_centralized", "bbox_format": "yxyx"}
    return {"summary": {"meta": ["poster"], "canvas": "single", "caption": "A minimalist orange juice poster on a deep warm orange background with a tall glass of fresh orange juice in the center and the brand name SOL in large cream uppercase letters."},
            "items": [
             {"label": "text", "caption": "Huge cream uppercase word with generous letter spacing, centered in the upper third.", "text": "SOL", "bbox": [-660, -300, -520, 300]},
             {"label": "object", "caption": "A tall glass of vivid orange juice with an orange slice on the rim, centered in the middle, bright morning light.", "bbox": [-260, -170, 420, 170]},
             {"label": "text", "caption": "Small cream uppercase tracking-wide line under the glass.", "text": "LARANJA · 100% NATURAL", "bbox": [520, -380, 580, 380]},
             {"label": "text", "caption": "Small italic cream tagline near the bottom.", "text": "Feito na hora. De verdade.", "bbox": [660, -400, 730, 400]}],
            "bbox_coord_space": "abs_centralized", "bbox_format": "yxyx"}

BASE = {
 "squeeze": ("Photograph of a hand pressing a halved orange onto a metal citrus juicer, juice spraying and "
             "trickling down at natural real speed, droplets flying with real gravity, bright morning "
             "kitchen light, blurred background, vivid orange and steel palette, commercial food "
             "photography, photorealistic, ultra sharp"),
 "glass": ("Photograph of fresh orange juice pouring from a glass carafe into a tall glass at natural "
           "speed, lively splash and bubbles in the vivid orange liquid, droplets bouncing off the "
           "surface, bright window light, clean white-marble kitchen, commercial beverage photography, "
           "photorealistic"),
 "swirl": ("Extreme macro photograph of an orange slice dropping into a tall glass of orange juice, pulp "
           "and fine bubbles swirling around the slice, backlit vivid orange glow, dark warm background "
           "with soft bokeh, luxury beverage cinematography, photorealistic, ultra detailed"),
 "carafe": ("Warm photograph of a glass carafe of fresh orange juice on a rustic breakfast table beside "
            "halved oranges and a folded linen napkin, morning sunlight streaming through a window, soft "
            "steam of fresh coffee blurred in the background, cozy bright mood, commercial photography, "
            "photorealistic"),
}
STILLS = []
for i, (k, p) in enumerate(BASE.items()):
    STILLS.append(dict(name=f"s9_{k}", seed=9200+i, prompt=p, w=1600, h=900))
    STILLS.append(dict(name=f"s9_{k}_v", seed=9200+i, prompt=p, w=900, h=1600))
STILLS.append(dict(name="s9_endcard_h", seed=9290, prompt=json.dumps(endcard(1600,900), ensure_ascii=False), w=1600, h=900))
STILLS.append(dict(name="s9_endcard_v", seed=9291, prompt=json.dumps(endcard(900,1600), ensure_ascii=False), w=900, h=1600))

tpl = open(WF, encoding="utf-8").read()
client = str(uuid.uuid4())
sel = sys.argv[1:] or [s["name"] for s in STILLS]
os.makedirs(DEST, exist_ok=True)
for s in [x for x in STILLS if x["name"] in sel]:
    wf_txt = (tpl.replace("__PROMPT__", json.dumps(s["prompt"], ensure_ascii=False)[1:-1])
                 .replace("__NEGATIVE__", json.dumps(NEG)[1:-1])
                 .replace("__WIDTH__", str(s["w"])).replace("__HEIGHT__", str(s["h"]))
                 .replace("__SEED__", str(s["seed"]))
                 .replace("__OUTPREFIX__", "moss9/" + s["name"]))
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
    print(f"[{s['name']}] OK {time.time()-t0:.0f}s", flush=True)
print("concluido")
