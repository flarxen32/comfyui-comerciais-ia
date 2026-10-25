# -*- coding: utf-8 -*-
"""Stills v5 — AMARGO chocolate 70% cacau (MOSS-Image SFT, 1600x900)."""
import json, time, shutil, sys, os, urllib.request, uuid

WF = "C:/Users/userx/Documents/projs/game dev/tools/comfy/workflows/moss_image_t2i_api.json"
OUTDIR = "C:/Users/userx/Documents/projs/game dev/tools/comfy/portable/ComfyUI/output"
DEST = "C:/Users/userx/Documents/projs/COMFYUI/moss5/stills"
NEG = "nsfw, worst quality, bad anatomy, watermark, jpeg artifact"

endcard_layout = {
    "summary": {"meta": ["poster"], "canvas": "single",
                "caption": "A minimalist dark chocolate poster on a deep brown-black background with a broken chocolate bar in the center and the brand name AMARGO in large cream uppercase letters."},
    "items": [
        {"label": "text", "caption": "Huge cream uppercase serif word with generous letter spacing, centered near the top.",
         "text": "AMARGO", "bbox": [-400, -360, -280, 360]},
        {"label": "object", "caption": "A dark chocolate bar with a clean snap broken into two pieces, cocoa powder dust around it, centered, soft studio light.",
         "bbox": [-60, -150, 220, 150]},
        {"label": "text", "caption": "Small cream uppercase tracking-wide line under the chocolate.",
         "text": "CHOCOLATE 70% CACAU", "bbox": [260, -260, 300, 260]},
        {"label": "text", "caption": "Small italic cream tagline centered near the bottom.",
         "text": "O lado selvagem do doce.", "bbox": [340, -390, 395, 390]},
    ],
    "bbox_coord_space": "abs_centralized", "bbox_format": "yxyx",
}

STILLS = [
    dict(name="s5_beans", seed=5101,
         prompt=("Extreme macro photograph of a ripe cocoa pod split open revealing white cocoa beans inside, "
                 "a few loose beans and dried cocoa leaves on dark rustic wood, warm dramatic side light, "
                 "deep brown and ivory palette, shallow depth of field, commercial food cinematography, "
                 "photorealistic, ultra detailed")),
    dict(name="s5_pour", seed=5202,
         prompt=("Macro photograph of thick melted dark chocolate pouring in a slow glossy ribbon onto a "
                 "dark stone surface, the chocolate folding and pooling with a rich satin sheen, dramatic "
                 "warm side light with deep shadows, dark moody patisserie background with soft bokeh, "
                 "commercial food advertising, photorealistic, ultra sharp")),
    dict(name="s5_bar", seed=5303,
         prompt=("Studio product photograph of a dark chocolate bar standing upright at a slight angle, the "
                 "chocolate surface embossed with the word \"AMARGO\" in elegant uppercase letters and a "
                 "smaller embossed line \"70% CACAU\" below, fine cocoa dust at the base, single warm key "
                 "light from the left with deep shadow falloff, dark charcoal-brown background, artisanal "
                 "chocolate advertising packshot, photorealistic, ultra sharp")),
    dict(name="s5_truffle", seed=5404,
         prompt=("Warm photograph of artisanal chocolate truffles dusted with dark cocoa powder on rough "
                 "grey stone, one truffle cut open showing a silky dark ganache center, soft window light "
                 "with gentle steam of cocoa in the air, shallow depth of field, artisanal patisserie mood, "
                 "commercial food photography, photorealistic")),
    dict(name="s5_endcard", seed=5505, prompt=json.dumps(endcard_layout, ensure_ascii=False)),
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
                 .replace("__OUTPREFIX__", "moss5/" + s["name"]))
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
