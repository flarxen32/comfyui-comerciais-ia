# -*- coding: utf-8 -*-
"""Stills v11 — SOSSEGO vela + influenciadores Rafa e Clara (calmos)."""
import json, time, shutil, sys, os, urllib.request, uuid

WF = "C:/Users/userx/Documents/projs/game dev/tools/comfy/workflows/moss_image_t2i_api.json"
OUTDIR = "C:/Users/userx/Documents/projs/game dev/tools/comfy/portable/ComfyUI/output"
DEST = "C:/Users/userx/Documents/projs/COMFYUI/moss11/stills"
NEG = "nsfw, worst quality, bad anatomy, watermark, jpeg artifact, extra fingers, deformed hands"

STILLS = [
 dict(name="char_rafa", seed=11101, w=900, h=1600,
      prompt=("Vertical phone-selfie style photograph of a Brazilian man around thirty, short dark beard, "
              "athletic but relaxed, warm calm smile, wearing a gray linen shirt, holding a lit frosted "
              "glass jar candle at chest level, soft warm evening light on a balcony, authentic UGC "
              "selfie aesthetic, photorealistic, sharp face")),
 dict(name="char_clara", seed=11202, w=900, h=1600,
      prompt=("Vertical phone-selfie style photograph of a young Brazilian woman with straight shoulder-"
              "length brown hair and round glasses, gentle serene smile, wearing a soft oversized beige "
              "cardigan, sitting cozy on a bed holding a lit frosted jar candle near her face, warm dim "
              "bedroom candlelight, authentic UGC selfie aesthetic, photorealistic, sharp face")),
 dict(name="prod_jar", seed=11303, w=900, h=1600,
      prompt=("Vertical product photograph of a frosted glass jar candle with a minimal craft label "
              "reading \"SOSSEGO\" in dark green lowercase letters with a thin line and the smaller words "
              "\"VELA AROMÁTICA\" below, the candle lit with a warm steady flame, standing on a wooden "
              "tray with dried lavender, soft warm evening light, artisanal candle commercial, "
              "photorealistic, ultra sharp")),
 dict(name="prod_flame", seed=11404, w=900, h=1600,
      prompt=("Vertical extreme macro photograph of a candle flame burning steady at a cotton wick inside "
              "a frosted glass jar, the warm orange glow reflecting on the frosted glass, melted cream "
              "wax pool around the wick, deep warm bokeh background, cozy candle commercial macro, "
              "photorealistic, ultra detailed")),
 dict(name="prod_smoke", seed=11505, w=900, h=1600,
      prompt=("Vertical macro photograph of a thin elegant ribbon of white smoke rising from a just-"
              "extinguished candle wick, curling gracefully against a dark warm background with soft "
              "amber bokeh, minimalist and serene mood, artisanal candle commercial, photorealistic")),
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
                 .replace("__OUTPREFIX__", "moss11/" + s["name"]))
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
