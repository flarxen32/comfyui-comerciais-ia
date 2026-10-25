# -*- coding: utf-8 -*-
"""v13 — takes de produto Wan 2.2 5B Turbo: A/B gêmeos (mesma seed, ± LoRA chuva) + pour.
A/B honesto: mesmo prompt, mesma seed, mesma imagem; única variável = beauty_of_rain @0.7."""
import json, time, shutil, sys, os, urllib.request, uuid

WF_PLAIN = "C:/Users/userx/Documents/projs/game dev/tools/comfy/workflows/wan22_turbo_gguf_api.json"
WF_LORA  = "C:/Users/userx/Documents/projs/game dev/tools/comfy/workflows/wan22_turbo_gguf_lora_api.json"
GGUF = "Wan2_2-TI2V-5B-Turbo-Q5_K_M.gguf"
OUTDIR = "C:/Users/userx/Documents/projs/game dev/tools/comfy/portable/ComfyUI/output"
INPUT  = "C:/Users/userx/Documents/projs/game dev/tools/comfy/portable/ComfyUI/input"
DEST   = "C:/Users/userx/Documents/projs/COMFYUI/moss13/video"
STILLS = "C:/Users/userx/Documents/projs/COMFYUI/moss13/stills"
LOG    = "C:/Users/userx/Documents/projs/COMFYUI/moss13/chain.log"

RAIN_PROMPT = ("Vertical cinematic product shot: a premium clear glass mineral water bottle with a deep "
               "blue-green label reading NASCENTE stands on a wet dark stone ledge during steady light rain, "
               "raindrops falling and hitting the bottle and the stone, each drop splashing into tiny bright "
               "droplets that bounce with real gravity at natural speed, water beads rolling slowly down the "
               "cold glass, cold condensation, soft city lights bokeh in the dark background, slow camera "
               "push-in, photorealistic luxury water commercial")

POUR_PROMPT = ("Vertical dynamic product shot: crystal clear mineral water pours from a glass bottle into a "
               "tall glass, the stream hits the surface at natural speed and splashes with real gravity, "
               "droplets bounce up sharp and bright, a second bottle with a deep blue-green label reading "
               "NASCENTE stands behind in soft focus on wet dark stone, fine mist of water in the air, soft "
               "rim light, photorealistic luxury water commercial")

TAKES = [
 dict(name="prod_rain_plain", img="prod_bottle.png", seed=15001, tpl=WF_PLAIN, prompt=RAIN_PROMPT),
 dict(name="prod_rain_lora",  img="prod_bottle.png", seed=15001, tpl=WF_LORA,  prompt=RAIN_PROMPT,
      lora="beauty_of_rain_wan2_2_ti2v_5B.safetensors", lstr=0.7),
 dict(name="prod_pour_lora",  img="prod_pour.png",   seed=15002, tpl=WF_LORA,  prompt=POUR_PROMPT,
      lora="beauty_of_rain_wan2_2_ti2v_5B.safetensors", lstr=0.7),
]

def log(msg):
    print(msg, flush=True)
    with open(LOG, "a", encoding="utf-8") as f: f.write(msg + "\n")

tpl_plain = open(WF_PLAIN, encoding="utf-8").read()
tpl_lora  = open(WF_LORA,  encoding="utf-8").read()
os.makedirs(DEST, exist_ok=True)
for t in TAKES:
    shutil.copyfile(os.path.join(STILLS, t["img"]), os.path.join(INPUT, t["img"]))
    tpl = tpl_lora if "lora" in t else tpl_plain
    s = (tpl.replace("__PROMPT__", json.dumps(t["prompt"])[1:-1])
            .replace("__UNETGGUF__", GGUF)
            .replace("__WIDTH__", "1088").replace("__HEIGHT__", "1920")
            .replace("__LENGTH__", "121").replace("__STEPS__", "4")
            .replace("__CFG__", "1.0").replace("__SAMPLER__", "euler")
            .replace("__SEED__", str(t["seed"]))
            .replace("__IMAGE__", t["img"])
            .replace("__OUTPREFIX__", "moss13/" + t["name"]))
    if "lora" in t:
        s = s.replace("__LORANAME__", t["lora"]).replace("__LORASTRENGTH__", str(t["lstr"]))
    assert "__" not in s.replace("__meta__", ""), f"placeholder sobrando em {t['name']}"
    body = json.dumps({"prompt": json.loads(s), "client_id": str(uuid.uuid4())}).encode("utf-8")
    t0 = time.time()
    req = urllib.request.Request("http://127.0.0.1:8189/prompt", data=body, headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req) as r: pid = json.load(r)["prompt_id"]
    hh = {}
    while True:
        time.sleep(10)
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:8189/history/{pid}", timeout=30) as r: h = json.load(r)
        except Exception:
            continue
        if pid in h:
            hh = h[pid]
            st = hh.get("status", {})
            if st.get("completed") or st.get("status_str") == "error": break
        if time.time()-t0 > 3600: log(f"[{t['name']}] TIMEOUT"); break
    vids = [v for o in hh.get("outputs", {}).values()
            for v in (o.get("gifs") or o.get("videos") or o.get("images") or [])]
    if not vids:
        log(f"[{t['name']}] ERRO: {str(hh.get('status'))[:300]}"); continue
    v = vids[0]
    src = os.path.join(OUTDIR, v.get("subfolder",""), v["filename"])
    shutil.copyfile(src, os.path.join(DEST, t["name"] + ".mp4"))
    log(f"[{t['name']}] OK {time.time()-t0:.0f}s")
log("produto concluido")
