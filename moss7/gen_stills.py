# -*- coding: utf-8 -*-
"""Stills v7 — CANAVIAL cachaça artesanal, em DOIS formatos: 1600x900 e 900x1600."""
import json, time, shutil, sys, os, urllib.request, uuid

WF = "C:/Users/userx/Documents/projs/game dev/tools/comfy/workflows/moss_image_t2i_api.json"
OUTDIR = "C:/Users/userx/Documents/projs/game dev/tools/comfy/portable/ComfyUI/output"
DEST = "C:/Users/userx/Documents/projs/COMFYUI/moss7/stills"
NEG = "nsfw, worst quality, bad anatomy, watermark, jpeg artifact"

def endcard(w, h):
    xh, yh = w // 2, h // 2
    if w > h:  # 16:9
        return {
            "summary": {"meta": ["poster"], "canvas": "single",
                        "caption": "A minimalist artisanal cachaça poster on a deep green-gold background with a bottle and a caipirinha glass in the center and the brand name CANAVIAL in large cream uppercase letters."},
            "items": [
                {"label": "text", "caption": "Huge cream uppercase word with generous letter spacing, centered near the top.",
                 "text": "CANAVIAL", "bbox": [-400, -400, -280, 400]},
                {"label": "object", "caption": "A tall clear cachaça bottle with a craft paper label beside a low glass of caipirinha with crushed ice and lime, centered, soft studio light.",
                 "bbox": [-60, -160, 220, 160]},
                {"label": "text", "caption": "Small cream uppercase tracking-wide line under the bottles.",
                 "text": "CACHAÇA ARTESANAL · ENVELHECIDA", "bbox": [260, -320, 300, 320]},
                {"label": "text", "caption": "Small italic cream tagline centered near the bottom.",
                 "text": "A aguardente da terra.", "bbox": [340, -400, 395, 400]},
            ], "bbox_coord_space": "abs_centralized", "bbox_format": "yxyx"}
    else:  # 9:16
        return {
            "summary": {"meta": ["poster"], "canvas": "single",
                        "caption": "A minimalist artisanal cachaça poster on a deep green-gold background with a bottle and a caipirinha glass in the center and the brand name CANAVIAL in large cream uppercase letters."},
            "items": [
                {"label": "text", "caption": "Huge cream uppercase word with generous letter spacing, centered near the upper third.",
                 "text": "CANAVIAL", "bbox": [-660, -400, -520, 400]},
                {"label": "object", "caption": "A tall clear cachaça bottle with a craft paper label beside a low glass of caipirinha with crushed ice and lime, centered in the middle, soft studio light.",
                 "bbox": [-260, -200, 420, 200]},
                {"label": "text", "caption": "Small cream uppercase tracking-wide line under the bottles.",
                 "text": "CACHAÇA ARTESANAL · ENVELHECIDA", "bbox": [520, -400, 580, 400]},
                {"label": "text", "caption": "Small italic cream tagline near the bottom.",
                 "text": "A aguardente da terra.", "bbox": [660, -400, 730, 400]},
            ], "bbox_coord_space": "abs_centralized", "bbox_format": "yxyx"}

BASE_PROMPTS = {
 "cane": ("Macro photograph of tall sugarcane stalks at dawn, golden light rim-lighting the fibers, dew "
          "droplets on the leaves, a blurred sugarcane field in warm morning haze behind, shallow depth of "
          "field, green and gold palette, commercial agricultural cinematography, photorealistic"),
 "pour": ("Close-up of artisanal cachaça being poured over crushed ice into a short glass with a fresh lime "
          "wedge, the crystal-clear spirit catching warm bar light, tiny bubbles, condensation beginning on "
          "the glass, dark rustic bar background with soft amber bokeh, commercial beverage cinematography, "
          "photorealistic, ultra sharp"),
 "bottle": ("Studio product photograph of a tall clear artisanal cachaça bottle with a craft paper label "
            "reading \"CANAVIAL\" in dark green uppercase letters with a thin line and the smaller words "
            "\"CACHAÇA ARTESANAL\" below, standing on dark wood with a few lime wedges and sugar cane "
            "sticks at the base, soft key light from the left, deep green and amber background, artisanal "
            "spirits advertising packshot, photorealistic, ultra sharp"),
 "glass": ("Warm photograph of a finished caipirinha on a rustic wooden bar top, crushed ice and muddled "
           "lime in a short heavy glass, fine condensation droplets, soft golden bar light with candle "
           "bokeh, blurred stools in the background, cozy boteco mood, commercial advertising photography, "
           "photorealistic"),
}

STILLS = []
for i, (k, p) in enumerate(BASE_PROMPTS.items()):
    STILLS.append(dict(name=f"s7_{k}", seed=7100 + i, prompt=p, w=1600, h=900))
    STILLS.append(dict(name=f"s7_{k}_v", seed=7100 + i, prompt=p, w=900, h=1600))
STILLS.append(dict(name="s7_endcard_h", seed=7190, prompt=json.dumps(endcard(1600, 900), ensure_ascii=False), w=1600, h=900))
STILLS.append(dict(name="s7_endcard_v", seed=7191, prompt=json.dumps(endcard(900, 1600), ensure_ascii=False), w=900, h=1600))

tpl = open(WF, encoding="utf-8").read()
client = str(uuid.uuid4())
sel = sys.argv[1:] or [s["name"] for s in STILLS]
os.makedirs(DEST, exist_ok=True)

for s in [x for x in STILLS if x["name"] in sel]:
    wf_txt = (tpl.replace("__PROMPT__", json.dumps(s["prompt"], ensure_ascii=False)[1:-1])
                 .replace("__NEGATIVE__", json.dumps(NEG)[1:-1])
                 .replace("__WIDTH__", str(s["w"])).replace("__HEIGHT__", str(s["h"]))
                 .replace("__SEED__", str(s["seed"]))
                 .replace("__OUTPREFIX__", "moss7/" + s["name"]))
    body = json.dumps({"prompt": json.loads(wf_txt), "client_id": client}).encode("utf-8")
    t0 = time.time()
    req = urllib.request.Request("http://127.0.0.1:8189/prompt", data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        pid = json.load(r)["prompt_id"]
    print(f"[{s['name']}] {s['w']}x{s['h']} enfileirado; aguardando...", flush=True)
    while True:
        time.sleep(5)
        with urllib.request.urlopen(f"http://127.0.0.1:8189/history/{pid}") as r:
            h = json.load(r)
        if pid in h:
            st = h[pid].get("status", {})
            if st.get("completed") or st.get("status_str") == "error":
                break
        if time.time() - t0 > 900:
            print(f"[{s['name']}] TIMEOUT"); break
    outs = h.get(pid, {}).get("outputs", {})
    imgs = [i for o in outs.values() for i in o.get("images", [])]
    if not imgs:
        print(f"[{s['name']}] ERRO: {str(h.get(pid,{}).get('status'))[:200]}"); continue
    img = imgs[0]
    shutil.copyfile(os.path.join(OUTDIR, img.get("subfolder", ""), img["filename"]),
                    os.path.join(DEST, s["name"] + ".png"))
    print(f"[{s['name']}] OK em {time.time()-t0:.0f}s", flush=True)
print("concluido")
