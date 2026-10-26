# -*- coding: utf-8 -*-
"""Stills v6 — RAIZ vinho tinto (MOSS-Image SFT, 1600x900)."""
import json, time, shutil, sys, os, urllib.request, uuid

WF = "C:/Users/userx/Documents/projs/game dev/tools/comfy/workflows/moss_image_t2i_api.json"
OUTDIR = "C:/Users/userx/Documents/projs/game dev/tools/comfy/portable/ComfyUI/output"
DEST = "C:/Users/userx/Documents/projs/COMFYUI/moss6/stills"
NEG = "nsfw, worst quality, bad anatomy, watermark, jpeg artifact"

endcard_layout = {
    "summary": {"meta": ["poster"], "canvas": "single",
                "caption": "A minimalist red wine poster on a deep burgundy-black background with a crystal glass of red wine in the center and the brand name RAIZ in large cream serif capitals."},
    "items": [
        {"label": "text", "caption": "Huge cream uppercase serif word with generous letter spacing, centered near the top.",
         "text": "RAIZ", "bbox": [-400, -320, -280, 320]},
        {"label": "object", "caption": "A crystal glass of deep ruby red wine catching a soft warm light, centered, subtle wine legs on the glass.",
         "bbox": [-60, -110, 220, 110]},
        {"label": "text", "caption": "Small cream uppercase tracking-wide line under the glass.",
         "text": "VINHO TINTO · RESERVA", "bbox": [260, -250, 300, 250]},
        {"label": "text", "caption": "Small italic cream tagline centered near the bottom.",
         "text": "O tinto que desce devagar.", "bbox": [340, -390, 395, 390]},
    ],
    "bbox_coord_space": "abs_centralized", "bbox_format": "yxyx",
}

STILLS = [
    dict(name="s6_grapes", seed=6101,
         prompt=("Macro photograph of ripe dark purple wine grapes on the vine at golden hour, dew droplets "
                 "on the skins, sunlit vineyard rows blurred in the background, warm amber backlight through "
                 "the grapes, shallow depth of field, deep purple and gold palette, commercial agricultural "
                 "cinematography, photorealistic, ultra detailed")),
    dict(name="s6_pour", seed=6202,
         prompt=("Macro photograph of red wine pouring from a bottle into a crystal glass, deep ruby liquid "
                 "with a thin elegant stream, soft splash settling, wine legs forming on the glass walls, "
                 "dark moody cellar background with warm candlelight bokeh, dramatic chiaroscuro lighting, "
                 "commercial beverage cinematography, photorealistic, ultra sharp")),
    dict(name="s6_cellar", seed=6303,
         prompt=("Atmospheric photograph of old oak wine barrels in a dim cellar, dust particles floating in "
                 "a single beam of warm light from a small window, one open barrel in the foreground with a "
                 "tasting glass on top, deep browns and amber tones, cinematic mood, commercial photography, "
                 "photorealistic")),
    dict(name="s6_swirl", seed=6404,
         prompt=("Close-up photograph of a hand gently tilting a crystal glass of red wine showing the wine "
                 "legs sliding slowly down the glass, deep ruby color glowing in warm side light, dark "
                 "elegant background with soft bokeh, luxury wine advertising, photorealistic, ultra sharp")),
    dict(name="s6_endcard", seed=6505, prompt=json.dumps(endcard_layout, ensure_ascii=False)),
]
for s in STILLS:
    s.update(w=1600, h=900)

tpl = open(WF, encoding="utf-8").read()
client = str(uuid.uuid4())
sel = sys.argv[1:] or [s["name"] for s in STILLS]
os.makedirs(DEST, exist_ok=True)

for s in [x for x in STILLS if x["name"] in sel]:
    wf_txt = (tpl.replace("__PROMPT__", json.dumps(s["prompt"], ensure_ascii=False)[1:-1])
                 .replace("__NEGATIVE__", json.dumps(NEG)[1:-1])
                 .replace("__WIDTH__", str(s["w"])).replace("__HEIGHT__", str(s["h"]))
                 .replace("__SEED__", str(s["seed"]))
                 .replace("__OUTPREFIX__", "moss6/" + s["name"]))
    body = json.dumps({"prompt": json.loads(wf_txt), "client_id": client}).encode("utf-8")
    t0 = time.time()
    req = urllib.request.Request("http://127.0.0.1:8189/prompt", data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        pid = json.load(r)["prompt_id"]
    print(f"[{s['name']}] enfileirado {pid}; aguardando...", flush=True)
    while True:
        time.sleep(5)
        with urllib.request.urlopen(f"http://127.0.0.1:8189/history/{pid}") as r:
            h = json.load(r)
        if pid in h:
            st = h[pid].get("status", {})
            if st.get("completed") or st.get("status_str") == "error":
                break
        if time.time() - t0 > 1800:
            print(f"[{s['name']}] TIMEOUT"); break
    outs = h.get(pid, {}).get("outputs", {})
    imgs = [i for o in outs.values() for i in o.get("images", [])]
    if not imgs:
        print(f"[{s['name']}] ERRO: {str(h.get(pid, {}).get('status'))[:300]}"); continue
    img = imgs[0]
    shutil.copyfile(os.path.join(OUTDIR, img.get("subfolder", ""), img["filename"]),
                    os.path.join(DEST, s["name"] + ".png"))
    print(f"[{s['name']}] OK 1600x900 em {time.time()-t0:.0f}s", flush=True)
print("concluido")
