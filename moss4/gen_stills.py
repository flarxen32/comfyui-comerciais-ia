# -*- coding: utf-8 -*-
"""Stills v4 — ÂMBAR mel silvestre (MOSS-Image SFT, 1600x900).
Uso: python gen_stills.py [nome1 ...]   (sem args = todos)"""
import json, time, shutil, sys, os, urllib.request, uuid

WF = "C:/Users/userx/Documents/projs/game dev/tools/comfy/workflows/moss_image_t2i_api.json"
OUTDIR = "C:/Users/userx/Documents/projs/game dev/tools/comfy/portable/ComfyUI/output"
DEST = "C:/Users/userx/Documents/projs/COMFYUI/moss4/stills"
NEG = "nsfw, worst quality, bad anatomy, watermark, jpeg artifact"

endcard_layout = {
    "summary": {"meta": ["poster"], "canvas": "single",
                "caption": "A minimalist honey poster on a deep warm amber background with a glass honey jar in the center and the brand name ÂMBAR in large cream serif capitals."},
    "items": [
        {"label": "text", "caption": "Huge cream uppercase serif word with an accent on the A, generous letter spacing, centered near the top.",
         "text": "ÂMBAR", "bbox": [-400, -360, -280, 360]},
        {"label": "object", "caption": "A hexagonal glass honey jar glowing golden, centered, soft studio light, a wooden honey dipper resting against it.",
         "bbox": [-60, -110, 220, 110]},
        {"label": "text", "caption": "Small cream uppercase tracking-wide line under the jar.",
         "text": "MEL SILVESTRE · COLHEITA 2026", "bbox": [260, -280, 300, 280]},
        {"label": "text", "caption": "Small italic cream tagline centered near the bottom.",
         "text": "O tempo, engarrafado.", "bbox": [340, -380, 395, 380]},
    ],
    "bbox_coord_space": "abs_centralized", "bbox_format": "yxyx",
}

STILLS = [
    dict(name="s4_comb", seed=4101,
         prompt=("Extreme macro photograph of golden honeycomb cells filled with luminous honey, one cell "
                 "overflowing with a thick slow drip, warm backlit amber glow, a few cells catching the "
                 "light like stained glass, shallow depth of field, deep amber and cream palette, commercial "
                 "food cinematography, photorealistic, ultra detailed")),
    dict(name="s4_dipper", seed=4202,
         prompt=("Macro photograph of a wooden honey dipper held above a small glass bowl, a thick golden "
                 "ribbon of honey drizzling down in a slow elegant fold, warm directional light from the "
                 "left making the honey glow like liquid amber, dark warm background with soft bokeh, "
                 "commercial food advertising, photorealistic, ultra sharp")),
    dict(name="s4_jar", seed=4303,
         prompt=("Studio product photograph of a hexagonal glass honey jar glowing golden in warm backlight, "
                 "the label reading \"ÂMBAR\" in cream uppercase serif letters with a thin line and the "
                 "smaller words \"MEL SILVESTRE\" below, standing on rustic dark wood, soft steam-warm light "
                 "from behind, deep amber background, subtle reflection under the jar, artisanal honey "
                 "advertising packshot, photorealistic, ultra sharp")),
    dict(name="s4_bread", seed=4404,
         prompt=("Warm breakfast photograph of rustic sourdough bread slices on a linen cloth, golden honey "
                 "dripping from a wooden dipper onto the bread in a slow glossy ribbon, morning window light "
                 "with soft steam, blurred kitchen background, shallow depth of field, cozy artisanal mood, "
                 "commercial food photography, photorealistic")),
    dict(name="s4_endcard", seed=4505, prompt=json.dumps(endcard_layout, ensure_ascii=False)),
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
                 .replace("__OUTPREFIX__", "moss4/" + s["name"]))
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
