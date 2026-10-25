# -*- coding: utf-8 -*-
"""Stills v3 — GAROA cerveja artesanal IPA (MOSS-Image SFT, 1600x900).
Uso: python gen_stills.py [nome1 ...]   (sem args = todos)"""
import json, time, shutil, sys, os, urllib.request, uuid

WF = "C:/Users/userx/Documents/projs/game dev/tools/comfy/workflows/moss_image_t2i_api.json"
OUTDIR = "C:/Users/userx/Documents/projs/game dev/tools/comfy/portable/ComfyUI/output"
DEST = "C:/Users/userx/Documents/projs/COMFYUI/moss3/stills"
NEG = "nsfw, worst quality, bad anatomy, watermark, jpeg artifact"

endcard_layout = {
    "summary": {"meta": ["poster"], "canvas": "single",
                "caption": "A minimalist craft beer poster on a deep charcoal-blue rain-soaked background with a amber beer glass in the center and the brand name GAROA in large cream uppercase letters."},
    "items": [
        {"label": "text", "caption": "Huge cream uppercase condensed word with generous letter spacing, centered near the top.",
         "text": "GAROA", "bbox": [-400, -360, -280, 360]},
        {"label": "object", "caption": "A tall glass of amber IPA with a thick foam head, centered, soft studio light, fine condensation droplets.",
         "bbox": [-60, -150, 220, 150]},
        {"label": "text", "caption": "Small cream uppercase tracking-wide line under the glass.",
         "text": "IPA DA SERRA · LUPULO DA CHUVA", "bbox": [260, -290, 300, 290]},
        {"label": "text", "caption": "Small italic cream tagline centered near the bottom.",
         "text": "Amarga que nem saudade.", "bbox": [340, -380, 395, 380]},
    ],
    "bbox_coord_space": "abs_centralized", "bbox_format": "yxyx",
}

STILLS = [
    dict(name="s3_hops", seed=3101,
         prompt=("Macro photograph of fresh green hop cones on the vine covered in fine rain droplets, "
                 "lupulin glands glistening, soft overcast mountain light, blurred rainy hop field in the "
                 "background, shallow depth of field, deep green and silver-grey palette, commercial "
                 "agricultural cinematography, photorealistic")),
    dict(name="s3_bottle", seed=3202,
         prompt=("Studio product photograph of a matte dark 355ml craft beer bottle covered in fine "
                 "condensation droplets, the label reading \"GAROA\" in cream uppercase letters with a thin "
                 "line and the smaller words \"IPA DA SERRA\" below, standing on wet dark slate, single soft "
                 "key light from the left with deep shadow falloff, dark charcoal-blue background, subtle "
                 "reflection under the bottle, craft beer advertising packshot, photorealistic, ultra sharp")),
    dict(name="s3_pour", seed=3303,
         prompt=("Macro close-up of amber IPA beer pouring from a bottle into a tall tilted glass, a cascade "
                 "of thick creamy foam building and swirling, fine bubbles rising through the golden liquid, "
                 "dark moody brewery background with warm bokeh lights, warm tungsten key light, commercial "
                 "beverage cinematography, photorealistic, ultra detailed")),
    dict(name="s3_glass", seed=3404,
         prompt=("Warm photograph of a tall glass of amber IPA with a thick foam head standing on a rustic "
                 "wooden table, a rain-streaked window with soft grey-blue evening light behind, gentle "
                 "bokeh raindrops, condensation on the glass, cozy craft brewery mood, shallow depth of "
                 "field, commercial advertising photography, photorealistic")),
    dict(name="s3_endcard", seed=3505, prompt=json.dumps(endcard_layout, ensure_ascii=False)),
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
                 .replace("__OUTPREFIX__", "moss3/" + s["name"]))
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
        print(f"[{s['name']}] ERRO: {str(h[pid].get('status'))[:300]}"); continue
    img = imgs[0]
    shutil.copyfile(os.path.join(OUTDIR, img.get("subfolder", ""), img["filename"]),
                    os.path.join(DEST, s["name"] + ".png"))
    print(f"[{s['name']}] OK 1600x900 em {time.time()-t0:.0f}s", flush=True)
print("concluido")
