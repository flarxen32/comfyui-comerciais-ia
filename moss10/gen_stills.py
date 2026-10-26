# -*- coding: utf-8 -*-
"""Stills v10 — LUZ sérum + personagens Bia e Duda (retratos UGC verticais 900x1600 + produto)."""
import json, time, shutil, sys, os, urllib.request, uuid

WF = "C:/Users/userx/Documents/projs/game dev/tools/comfy/workflows/moss_image_t2i_api.json"
OUTDIR = "C:/Users/userx/Documents/projs/game dev/tools/comfy/portable/ComfyUI/output"
DEST = "C:/Users/userx/Documents/projs/COMFYUI/moss10/stills"
NEG = "nsfw, worst quality, bad anatomy, watermark, jpeg artifact, extra fingers, deformed hands"

STILLS = [
 dict(name="char_bia", seed=10101, w=900, h=1600,
      prompt=("Vertical phone-selfie style photograph of a Brazilian woman in her mid-twenties, warm "
              "light-brown skin, long dark wavy hair loosely tied, minimal natural makeup, calm confident "
              "smile, wearing a soft cream knit top, holding a small amber glass serum bottle with the "
              "label \"LUZ\" near her cheek, soft natural bathroom light from a window, authentic UGC "
              "selfie aesthetic slightly imperfect, photorealistic, sharp face")),
 dict(name="char_duda", seed=10202, w=900, h=1600,
      prompt=("Vertical phone-selfie style photograph of a young Brazilian woman with voluminous curly "
              "caramel hair and freckles, big expressive joyful smile, wearing a colorful tie-dye t-shirt, "
              "holding up a small amber glass serum bottle labeled \"LUZ\" toward the camera, bright "
              "bedroom daylight, energetic best-friend energy, authentic UGC selfie aesthetic, "
              "photorealistic, sharp face")),
 dict(name="prod_bottle", seed=10303, w=900, h=1600,
      prompt=("Vertical product photograph of a small amber glass serum bottle with a dropper cap, the "
              "minimal label reading \"LUZ\" in white elegant uppercase letters with a thin line and the "
              "smaller words \"SÉRUM FACIAL\" below, standing on a marble bathroom shelf, soft morning "
              "light from the side, warm neutral background, water droplets of condensation, authentic "
              "skincare commercial, photorealistic, ultra sharp")),
 dict(name="prod_drop", seed=10404, w=900, h=1600,
      prompt=("Vertical extreme macro photograph of a golden viscous serum drop stretching slowly from a "
              "glass dropper, thick honey-like consistency glowing in warm backlight, fine suspended "
              "bubbles inside the dense liquid, soft bathroom bokeh background, skincare commercial "
              "cinematography, photorealistic, ultra detailed")),
 dict(name="prod_smear", seed=10505, w=900, h=1600,
      prompt=("Vertical macro photograph of a smooth swirl of pearly golden face cream texture on a clear "
              "glass surface, thick glossy peaks and folds, warm side light catching the ridges, minimal "
              "skincare aesthetic, commercial texture shot, photorealistic, ultra sharp")),
]

tpl = open(WF, encoding="utf-8").read()
client = str(uuid.uuid4())
sel = sys.argv[1:] or [s["name"] for s in STILLS]
os.makedirs(DEST, exist_ok=True)
for s in [x for x in STILLS if x["name"] in sel]:
    wf_txt = (tpl.replace("__PROMPT__", json.dumps(s["prompt"], ensure_ascii=False)[1:-1])
                 .replace("__NEGATIVE__", json.dumps(NEG)[1:-1])
                 .replace("__WIDTH__", str(s["w"])).replace("__HEIGHT__", str(s["h"]))
                 .replace("__SEED__", str(s["seed"]))
                 .replace("__OUTPREFIX__", "moss10/" + s["name"]))
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
