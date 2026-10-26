# -*- coding: utf-8 -*-
"""Stills v2 — SERRA café de altitude (MOSS-Image SFT, 1600x900 = 1.44MP).
Uso: python gen_stills.py [nome1 ...]   (sem args = todos)"""
import json, time, shutil, sys, os, urllib.request, uuid

WF = "C:/Users/userx/Documents/projs/game dev/tools/comfy/workflows/moss_image_t2i_api.json"
OUTDIR = "C:/Users/userx/Documents/projs/game dev/tools/comfy/portable/ComfyUI/output"
DEST = "C:/Users/userx/Documents/projs/COMFYUI/moss2/stills"
NEG = "nsfw, worst quality, bad anatomy, watermark, jpeg artifact"

endcard_layout = {
    "summary": {"meta": ["poster"], "canvas": "single",
                "caption": "A minimalist specialty coffee poster on a deep espresso-brown background with a ceramic coffee cup in the center and the brand name SERRA in large cream serif capitals."},
    "items": [
        {"label": "text", "caption": "Huge cream uppercase serif word with generous letter spacing, centered near the top.",
         "text": "SERRA", "bbox": [-400, -360, -280, 360]},
        {"label": "object", "caption": "A handcrafted ceramic coffee cup seen slightly from above, centered, with soft studio light and a thin curl of steam.",
         "bbox": [-60, -140, 220, 140]},
        {"label": "text", "caption": "Small cream uppercase tracking-wide line under the cup.",
         "text": "CAFÉ DE ALTITUDE · 1.400 M", "bbox": [260, -260, 300, 260]},
        {"label": "text", "caption": "Small italic cream tagline centered near the bottom.",
         "text": "O sabor de quem colhe cedo.", "bbox": [340, -400, 395, 400]},
    ],
    "bbox_coord_space": "abs_centralized", "bbox_format": "yxyx",
}

STILLS = [
    dict(name="s2_cherry", seed=2101,
         prompt=("Macro photograph of ripe red coffee cherries clustered on a branch, glossy dark green leaves "
                 "with morning dew droplets, soft golden dawn light filtering through highland mist, a blurred "
                 "mountainside plantation in the far background, shallow depth of field, deep green and warm "
                 "amber palette, commercial agricultural cinematography, photorealistic")),
    dict(name="s2_beans", seed=2202,
         prompt=("Close-up photograph of freshly roasted coffee beans cascading in mid-air into a handcrafted "
                 "ceramic bowl, several beans frozen mid-fall, warm side light from a window, rustic dark wooden "
                 "table, rich brown and caramel tones with soft shadows, commercial food photography, "
                 "photorealistic, sharp detail")),
    dict(name="s2_pour", seed=2303,
         prompt=("Macro close-up of espresso pouring from a bottomless portafilter into a small ceramic cup, "
                 "thick golden crema swirling on the surface, delicate steam curling upward, dark moody café "
                 "background with soft bokeh lights, warm tungsten key light from the left, commercial beverage "
                 "cinematography, photorealistic, ultra detailed")),
    dict(name="s2_cup", seed=2404,
         prompt=("Warm lifestyle photograph of hands in a chunky knit sweater wrapping around a steaming ceramic "
                 "coffee cup on a rustic wooden table beside a bright morning window, gentle steam rising through "
                 "a sunbeam, soft golden hour light, shallow depth of field, cozy artisanal café mood, commercial "
                 "advertising photography, photorealistic")),
    dict(name="s2_endcard", seed=2505, prompt=json.dumps(endcard_layout, ensure_ascii=False)),
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
                 .replace("__OUTPREFIX__", "moss2/" + s["name"]))
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
    print(f"[{s['name']}] OK 1600x900 em {time.time()-t0:.0f}s -> {dst}", flush=True)
print("concluido")
