# -*- coding: utf-8 -*-
"""Gera stills comerciais com MOSS-Image SFT (ComfyUI 8189, workflow nativo).
Uso: python gen_stills.py [nome1 nome2 ...]   (sem args = todos)
Copies finais em COMFYUI/moss/stills/<nome>.png
"""
import json, time, shutil, sys, os, urllib.request, uuid

WF = "C:/Users/userx/Documents/projs/game dev/tools/comfy/workflows/moss_image_t2i_api.json"
OUTDIR = "C:/Users/userx/Documents/projs/game dev/tools/comfy/portable/ComfyUI/output"
DEST = "C:/Users/userx/Documents/projs/COMFYUI/moss/stills"
NEG = "nsfw, worst quality, bad anatomy, watermark, jpeg artifact"

endcard_layout = {
    "summary": {"meta": ["poster"], "canvas": "single",
                "caption": "A minimalist luxury fragrance poster on a deep charcoal background with a clear glass perfume bottle in the center and the brand name MOSS in large white serif capitals."},
    "items": [
        {"label": "text", "caption": "Huge white uppercase serif word with generous letter spacing, centered near the top.",
         "text": "MOSS", "bbox": [-350, -320, -210, 320]},
        {"label": "object", "caption": "A rectangular clear glass perfume bottle with a matte deep-green cap, small and centered, lit by soft studio light.",
         "bbox": [-80, -75, 250, 75]},
        {"label": "text", "caption": "Small white uppercase tracking-wide line under the bottle.",
         "text": "EAU DE PARFUM", "bbox": [280, -170, 315, 170]},
        {"label": "text", "caption": "Small italic white tagline centered near the bottom.",
         "text": "Onde a floresta mora em você.", "bbox": [335, -390, 370, 390]},
    ],
    "bbox_coord_space": "abs_centralized", "bbox_format": "yxyx",
}

poster_layout = {
    "summary": {"meta": ["poster"], "canvas": "single",
                "caption": "A minimalist travel poster on cream paper with a flat deep-green mountain range, layered mist, and the title MATA at the top."},
    "items": [
        {"label": "text", "caption": "Large dark-green uppercase serif title centered at the top.",
         "text": "MATA", "bbox": [-440, -300, -330, 300]},
        {"label": "object", "caption": "Flat deep-green mountain silhouettes with two lighter mist layers in the lower two thirds.",
         "bbox": [-160, -400, 340, 400]},
        {"label": "text", "caption": "Small dark-green uppercase tracking-wide line near the bottom.",
         "text": "TRILHAS DA FLORESTA", "bbox": [390, -360, 430, 360]},
    ],
    "bbox_coord_space": "abs_centralized", "bbox_format": "yxyx",
}

STILLS = [
    dict(name="spot_open", w=1344, h=768, seed=101,
         prompt=("Cinematic macro photograph of a rectangular clear glass perfume bottle nestled on a "
                 "moss-covered granite boulder in a temperate rainforest, deep emerald moss and tiny ferns "
                 "framing the bottle, fine mist drifting through volumetric god rays falling from the canopy, "
                 "the bottle label reading \"MOSS\" in small white uppercase serif letters, dew droplets "
                 "beading on the glass, dark emerald and charcoal palette with one warm amber rim light from "
                 "behind, shallow depth of field, 100mm macro lens, luxury fragrance commercial still, "
                 "photorealistic")),
    dict(name="spot_pack", w=1344, h=768, seed=202,
         prompt=("Studio product photograph of a rectangular clear glass perfume bottle with a matte "
                 "deep-green cap standing on wet black slate, a collar of live moss wrapping the base of the "
                 "bottle, single large softbox key light from upper left with deep shadow falloff, fine water "
                 "droplets on the slate, dark charcoal seamless background, the bottle label reading \"MOSS\" "
                 "in white uppercase serif letters above a thin line and the smaller words \"EAU DE PARFUM\", "
                 "soft reflection under the bottle, luxury fragrance advertising packshot, photorealistic, "
                 "ultra sharp")),
    dict(name="endcard", w=1344, h=768, seed=303, prompt=json.dumps(endcard_layout, ensure_ascii=False)),
    dict(name="show_fragrance", w=1024, h=1024, seed=404,
         prompt=("Premium fragrance advertising photograph: a transparent rectangular glass bottle with a "
                 "charcoal cap standing on a rough grey stone, one dark green moss cushion growing at its "
                 "base, pale grey seamless backdrop, strong directional soft light, the title \"MOSS\" in "
                 "black uppercase serif letters on the backdrop wall behind the bottle with a thin vermilion "
                 "underline leading toward the bottle cap, minimalist luxury campaign, photorealistic, sharp "
                 "focus")),
    dict(name="show_poster", w=1024, h=1024, seed=505, prompt=json.dumps(poster_layout, ensure_ascii=False)),
    dict(name="show_window", w=1024, h=1280, seed=606,
         prompt=("Evening street photograph of an elegant bookshop window display, one large illustrated "
                 "travel poster standing on a wooden easel behind the glass, the poster showing a flat green "
                 "mountain landscape under a cream sky with the readable title \"FLORESTA\" in dark green "
                 "capitals at its top, warm interior lamps and a small red stool beside the easel, faint "
                 "reflections of city lights on the glass, deep forest green and warm cream palette, "
                 "cinematic, photorealistic")),
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
                 .replace("__OUTPREFIX__", "moss/" + s["name"]))
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
            print(f"[{s['name']}] TIMEOUT 30min"); break
    outs = h.get(pid, {}).get("outputs", {})
    imgs = [i for o in outs.values() for i in o.get("images", [])]
    if not imgs:
        print(f"[{s['name']}] ERRO sem saida: {str(h[pid].get('status'))[:300]}"); continue
    img = imgs[0]
    src = os.path.join(OUTDIR, img.get("subfolder", ""), img["filename"])
    dst = os.path.join(DEST, s["name"] + ".png")
    shutil.copyfile(src, dst)
    print(f"[{s['name']}] OK {s['w']}x{s['h']} em {time.time()-t0:.0f}s -> {dst}", flush=True)
print("concluido")
