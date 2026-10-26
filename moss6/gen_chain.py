# -*- coding: utf-8 -*-
"""v6 — cadeia RAIZ: 4 takes Turbo 1080p + 4 doadores H3@4st."""
import json, time, shutil, os, subprocess, urllib.request, uuid

TOOLS = "C:/Users/userx/Documents/projs/game dev/tools/comfy"
INPUT = TOOLS + "/portable/ComfyUI/input"
OUTDIR = TOOLS + "/portable/ComfyUI/output"
BASE = "C:/Users/userx/Documents/projs/COMFYUI"
DEST = BASE + "/moss6/video"
WFS = {"h3": TOOLS + "/workflows/minimax_h3_i2v_api.json",
       "turbo": TOOLS + "/workflows/wan22_turbo_gguf_api.json"}
GGUF = "Wan2_2-TI2V-5B-Turbo-Q5_K_M.gguf"

VID = {
 "grapes": ("Macro of ripe dark wine grapes on the vine at golden hour, dew droplets glistening, a very "
            "gentle breeze moves the leaves, warm backlight slowly shifting. Camera: locked tripod macro."),
 "cellar": ("Dim cellar with old oak wine barrels, dust particles drifting through a single warm beam of "
            "light, a tasting glass resting on the nearest barrel. Camera: very slow dolly-in."),
 "pour": ("Red wine pours from a bottle into a crystal glass in one continuous elegant stream, deep ruby "
          "liquid with wine legs forming on the glass, soft splash settling, candlelight bokeh in the dark "
          "background. Camera: locked tripod macro."),
 "swirl": ("A crystal glass of red wine tilts gently showing wine legs sliding slowly down the glass, the "
           "ruby color glowing in warm side light. Camera: locked tripod close-up."),
}
AUD = {
 "grapes": ("Macro of wine grapes at golden hour. Ambient audio: soft vineyard birdsong, gentle breeze, and "
            "an intimate bossa nova guitar beginning quietly."),
 "cellar": ("Dim wine cellar with barrels. Ambient audio: deep cellar silence, a distant echo drip, and the "
            "bossa nova guitar with soft brush drums continuing."),
 "pour": ("Red wine pouring into a glass. Ambient audio: rich liquid pour, a soft glass resonance, and the "
          "bossa nova guitar swelling warmly."),
 "swirl": ("Wine legs sliding down a glass. Ambient audio: a gentle glass chime, quiet room tone, and the "
           "bossa nova guitar resolving with a warm final chord."),
}

TAKES = [
    ("s6v6_pour",    "turbo", "s6_pour",    (1920, 1088), 4, 10201, "pour"),
    ("s6v6_grapes",  "turbo", "s6_grapes",  (1920, 1088), 4, 10202, "grapes"),
    ("s6v6_cellar",  "turbo", "s6_cellar",  (1920, 1088), 4, 10203, "cellar"),
    ("s6v6_swirl",   "turbo", "s6_swirl",   (1920, 1088), 4, 10204, "swirl"),
    ("aud_grapes", "h3", "s6_grapes", (832, 480), 4, 10301, "grapes", True),
    ("aud_cellar",  "h3", "s6_cellar", (832, 480), 4, 10302, "cellar", True),
    ("aud_pour",    "h3", "s6_pour",   (832, 480), 4, 10303, "pour", True),
    ("aud_swirl",   "h3", "s6_swirl",  (832, 480), 4, 10304, "swirl", True),
]

client = str(uuid.uuid4())
os.makedirs(DEST, exist_ok=True)
for t in TAKES:
    name, engine, still, (w, h), steps, seed, key = t[0], t[1], t[2], t[3], t[4], t[5], t[6]
    is_aud = len(t) > 7 and t[7]
    prompt = AUD[key] if is_aud else VID[key]
    src = f"{BASE}/moss6/stills/{still}.png"
    fname = f"{name}_{w}x{h}.png"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src,
                    "-vf", f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}",
                    os.path.join(INPUT, fname)], check=True)
    tpl = open(WFS[engine], encoding="utf-8").read()
    wf_txt = (tpl.replace("__UNETGGUF__", GGUF).replace("__CFG__", "1.0").replace("__SAMPLER__", "euler")
                 .replace("__IMAGE__", fname)
                 .replace("__PROMPT__", json.dumps(prompt, ensure_ascii=False)[1:-1])
                 .replace("__WIDTH__", str(w)).replace("__HEIGHT__", str(h))
                 .replace("__LENGTH__", "121").replace("__STEPS__", str(steps))
                 .replace("__SEED__", str(seed))
                 .replace("__OUTPREFIX__", "moss6/" + name))
    body = json.dumps({"prompt": json.loads(wf_txt), "client_id": client}).encode("utf-8")
    t0 = time.time()
    req = urllib.request.Request("http://127.0.0.1:8189/prompt", data=body,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            pid = json.load(r)["prompt_id"]
    except urllib.error.HTTPError as e:
        print(f"[{name}] REJEITADO: {e.read().decode(errors='replace')[:400]}", flush=True); continue
    print(f"[{name}] {engine}@{steps}st enfileirado {pid}", flush=True)
    hh = {}
    while True:
        time.sleep(6)
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:8189/history/{pid}") as r:
                hh = json.load(r)
        except Exception:
            continue
        if pid in hh:
            st = hh[pid].get("status", {})
            if st.get("completed") or st.get("status_str") == "error":
                break
        if time.time() - t0 > 1500:
            print(f"[{name}] TIMEOUT", flush=True); break
    outs = hh.get(pid, {}).get("outputs", {})
    vids = [e for o in outs.values() for k in ("videos", "gifs", "images") for e in o.get(k, []) if e.get("type") == "output"]
    if not vids:
        print(f"[{name}] ERRO: {str(hh.get(pid, {}).get('status'))[:300]}", flush=True); continue
    e0 = vids[0]
    dst = f"{DEST}/{name}" + os.path.splitext(e0["filename"])[1]
    shutil.copyfile(os.path.join(OUTDIR, e0.get("subfolder", ""), e0["filename"]), dst)
    print(f"[{name}] OK em {time.time()-t0:.0f}s -> {dst}", flush=True)
print("cadeia v6 concluida")
