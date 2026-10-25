# -*- coding: utf-8 -*-
"""Stills v13 — NASCENTE água mineral + influenciadores Lena e Caio (tema: água/chuva)."""
import json, time, shutil, sys, os, urllib.request, uuid

WF = "C:/Users/userx/Documents/projs/game dev/tools/comfy/workflows/moss_image_t2i_api.json"
OUTDIR = "C:/Users/userx/Documents/projs/game dev/tools/comfy/portable/ComfyUI/output"
DEST = "C:/Users/userx/Documents/projs/COMFYUI/moss13/stills"
NEG = "nsfw, worst quality, bad anatomy, watermark, jpeg artifact, extra fingers, deformed hands"

STILLS = [
 dict(name="char_lena", seed=13101, w=900, h=1600,
      prompt=("Vertical phone-selfie style photograph of a Brazilian woman around twenty-seven with voluminous "
              "curly dark hair, radiant relaxed smile, wearing a bright yellow rain jacket, standing on a city "
              "street during light rain at dusk, small raindrops visible in the air and on her shoulders, holding "
              "a clear glass water bottle with a deep blue-green label at chest level, wet asphalt reflections "
              "and soft city bokeh behind her, authentic UGC selfie aesthetic, photorealistic, sharp face")),
 dict(name="char_caio", seed=13202, w=900, h=1600,
      prompt=("Vertical phone-selfie style photograph of a Brazilian man around thirty-two with short curly hair "
              "and a trimmed beard, calm confident smile, wearing a light blue shirt, standing on an apartment "
              "terrace just after rain with a wet floor full of puddles reflecting the sky, holding a clear glass "
              "water bottle with a deep blue-green label at chest level, fresh evening light, authentic UGC "
              "selfie aesthetic, photorealistic, sharp face")),
 dict(name="prod_bottle", seed=13303, w=1088, h=1920,
      prompt=("Vertical product photograph of a premium clear glass mineral water bottle with a minimal deep "
              "blue-green label reading \"NASCENTE\" in clean white capital letters with the smaller words "
              "\"ÁGUA MINERAL\" below, dense cold condensation droplets on the glass, standing on a wet dark "
              "stone ledge with fine rain falling around it, tiny splashes where raindrops hit the stone, soft "
              "city lights bokeh in the dark background, luxury water commercial, photorealistic, ultra sharp")),
 dict(name="prod_pour", seed=13404, w=1088, h=1920,
      prompt=("Vertical dynamic product photograph of crystal clear mineral water being poured from a glass "
              "bottle into a tall glass, water hitting the surface at natural speed and splashing with real "
              "gravity, droplets bouncing up sharp and bright, a second bottle with a deep blue-green label "
              "reading \"NASCENTE\" standing behind in soft focus, dark stone background with soft rim light, "
              "luxury water commercial, photorealistic, ultra sharp")),
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
                 .replace("__OUTPREFIX__", "moss13/" + s["name"]))
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
