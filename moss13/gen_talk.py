# -*- coding: utf-8 -*-
"""v13 — takes de fala H3 (243f@8st, 576x1024, áudio diegético com lip sync PT-BR).
Lena: rua na chuva COM LoRA beauty_of_rain @0.6 (template rain). Caio: controle SEM LoRA (template realism)."""
import json, time, shutil, sys, os, urllib.request, uuid

WF_RAIN    = "C:/Users/userx/Documents/projs/game dev/tools/comfy/workflows/h3_i2v_rain_api.json"
WF_REALISM = "C:/Users/userx/Documents/projs/game dev/tools/comfy/workflows/h3_i2v_realism_api.json"
OUTDIR = "C:/Users/userx/Documents/projs/game dev/tools/comfy/portable/ComfyUI/output"
INPUT  = "C:/Users/userx/Documents/projs/game dev/tools/comfy/portable/ComfyUI/input"
DEST   = "C:/Users/userx/Documents/projs/COMFYUI/moss13/video"
STILLS = "C:/Users/userx/Documents/projs/COMFYUI/moss13/stills"
LOG    = "C:/Users/userx/Documents/projs/COMFYUI/moss13/chain.log"

LENA = ("A Brazilian woman around twenty-seven with voluminous curly dark hair in a bright yellow rain jacket "
        "stands on a city street during calm light rain at dusk, holding a clear glass water bottle with a deep "
        "blue-green label near her chest. She looks straight at the camera with a relaxed genuine smile, lifts "
        "the bottle slightly and speaks Brazilian Portuguese with accurate lip sync, saying: Chuva boa, água "
        "melhor. NASCENTE. Pura de verdade. Steady gentle rain falls around her, raindrops sparkle in the city "
        "lights at natural real speed, wet asphalt reflections shimmer. Her face stays sharp, stable and "
        "consistent throughout the video. Camera: subtle slow push-in. Audio: soft steady rain ambience, distant "
        "city traffic hum, her warm calm voice close and clear, a gentle acoustic guitar bed.")

CAIO = ("A Brazilian man around thirty-two with short curly hair and a trimmed beard in a light blue shirt "
        "stands on an apartment terrace just after rain, wet floor with puddles reflecting the fresh evening "
        "sky, holding a clear glass water bottle with a deep blue-green label near his chest. He looks straight "
        "at the camera with a calm confident smile, uncaps the bottle, takes a small refreshing sip and speaks "
        "Brazilian Portuguese with accurate lip sync, saying: Depois da chuva, eu tomo NASCENTE. Do começo ao "
        "fim. Water droplets fall gently from the terrace railing at natural real speed. His face stays sharp, "
        "stable and consistent throughout the video. Camera: subtle slow push-in. Audio: fresh post-rain "
        "ambience with distant thunder rolling away, water dripping softly, his calm warm voice close and "
        "clear, a soft piano bed.")

TAKES = [
 dict(name="lena_talk", img="char_lena.png", seed=13505, tpl=WF_RAIN, prompt=LENA, rainstr=0.6),
 dict(name="caio_talk",  img="char_caio.png",  seed=13606, tpl=WF_REALISM, prompt=CAIO),
]

def log(msg):
    print(msg, flush=True)
    with open(LOG, "a", encoding="utf-8") as f: f.write(msg + "\n")

os.makedirs(DEST, exist_ok=True)
for t in TAKES:
    shutil.copyfile(os.path.join(STILLS, t["img"]), os.path.join(INPUT, t["img"]))
    s = (open(t["tpl"], encoding="utf-8").read()
         .replace("__PROMPT__", json.dumps(t["prompt"])[1:-1])
         .replace("__WIDTH__", "576").replace("__HEIGHT__", "1024")
         .replace("__LENGTH__", "243").replace("__STEPS__", "8")
         .replace("__SEED__", str(t["seed"]))
         .replace("__IMAGE__", t["img"])
         .replace("__OUTPREFIX__", "moss13/" + t["name"]))
    if "rainstr" in t:
        s = s.replace("__RAINSTR__", str(t["rainstr"]))
    assert "__" not in s.replace("__meta__", ""), f"placeholder sobrando em {t['name']}"
    body = json.dumps({"prompt": json.loads(s), "client_id": str(uuid.uuid4())}).encode("utf-8")
    t0 = time.time()
    req = urllib.request.Request("http://127.0.0.1:8189/prompt", data=body, headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req) as r: pid = json.load(r)["prompt_id"]
    hh = {}
    while True:
        time.sleep(15)
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:8189/history/{pid}", timeout=30) as r: h = json.load(r)
        except Exception:
            continue
        if pid in h:
            hh = h[pid]
            st = hh.get("status", {})
            if st.get("completed") or st.get("status_str") == "error": break
        if time.time()-t0 > 5400: log(f"[{t['name']}] TIMEOUT"); break
    vids = [v for o in hh.get("outputs", {}).values()
            for v in (o.get("gifs") or o.get("videos") or o.get("images") or [])]
    if not vids:
        log(f"[{t['name']}] ERRO: {str(hh.get('status'))[:300]}"); continue
    v = vids[0]
    shutil.copyfile(os.path.join(OUTDIR, v.get("subfolder",""), v["filename"]), os.path.join(DEST, t["name"] + ".mp4"))
    log(f"[{t['name']}] OK {time.time()-t0:.0f}s")
log("talks concluidos")
