# -*- coding: utf-8 -*-
"""v9 — cadeia SOL: 8 takes com VELOCIDADE por take (fps do CreateVideo) + doadores.
squeeze/glass = 36fps (1,5x real) · swirl = 24fps (herói lento assumido) · carafe = 30fps (1,25x)."""
import json, time, shutil, os, subprocess, urllib.request, uuid

TOOLS = "C:/Users/userx/Documents/projs/game dev/tools/comfy"
INPUT = TOOLS + "/portable/ComfyUI/input"
OUTDIR = TOOLS + "/portable/ComfyUI/output"
BASE = "C:/Users/userx/Documents/projs/COMFYUI"
DEST = BASE + "/moss9/video"
WFS = {"h3": TOOLS + "/workflows/minimax_h3_i2v_api.json",
       "turbo": TOOLS + "/workflows/wan22_turbo_gguf_api.json"}
GGUF = "Wan2_2-TI2V-5B-Turbo-Q5_K_M.gguf"

VID = {
 "squeeze": ("Energetic real-time citrus press: a hand presses a halved orange onto a metal juicer and "
             "juice sprays and trickles down at natural speed, droplets flying and falling with real "
             "gravity, vivid and immediate. Camera: locked tripod close-up."),
 "glass": ("Energetic real-time pour: fresh orange juice pours from a glass carafe into a tall glass at "
           "natural speed, the stream hits the surface and splashes lively, bubbles rise quickly, droplets "
           "bounce with real gravity. Camera: locked tripod."),
 "swirl": ("Cinematic slow-motion macro: an orange slice drops into a tall glass of orange juice, pulp and "
           "fine bubbles swirling gracefully around it, backlit orange glow. Deliberate slow motion. "
           "Camera: locked tripod macro."),
 "carafe": ("A glass carafe of orange juice on a rustic breakfast table beside halved oranges, morning "
            "sunlight moving softly, a slight gleam traveling along the glass. Camera: very slow "
            "dolly-in."),
}
AUD = {
 "squeeze": ("Citrus press in a kitchen. Ambient audio: energetic juice spraying and trickling, a bright "
             "brazilian tropicalia guitar with percussion beginning."),
 "glass": ("Orange juice pouring into a glass. Ambient audio: lively pour with bubbles, and the "
           "tropicalia continuing with groove."),
 "swirl": ("Orange slice dropping into juice in slow motion. Ambient audio: a soft deep bubble, and the "
           "tropicalia holding a warm suspended chord."),
 "carafe": ("Breakfast table with orange juice. Ambient audio: morning birds outside, a gentle carafe "
            "clink, and the tropicalia resolving with a bright final chord."),
}
FPS = {"squeeze": 36, "glass": 36, "swirl": 24, "carafe": 30}

FMTS = {"": (1920, 1088), "_v": (1088, 1920)}
TAKES = []
for key in ("squeeze", "glass", "swirl", "carafe"):
    for sfx, (w, h) in FMTS.items():
        TAKES.append((f"s9v9_{key}{sfx}", "turbo", f"s9_{key}{sfx}", (w, h), 4, 13100 + len(TAKES), key, FPS[key]))
for i, key in enumerate(("squeeze", "glass", "swirl", "carafe")):
    TAKES.append((f"aud_{key}", "h3", f"s9_{key}", (832, 480), 4, 13200 + i, key, None))

client = str(uuid.uuid4())
os.makedirs(DEST, exist_ok=True)
for t in TAKES:
    name, engine, still, (w, h), steps, seed, key, fps = t[0], t[1], t[2], t[3], t[4], t[5], t[6], t[7]
    is_h3 = engine == "h3"
    prompt = AUD[key] if is_h3 else VID[key]
    src = f"{BASE}/moss9/stills/{still}.png"
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
                 .replace("__OUTPREFIX__", "moss9/" + name))
    if fps:
        wf_txt = wf_txt.replace('"fps": 24', f'"fps": {fps}')
    body = json.dumps({"prompt": json.loads(wf_txt), "client_id": client}).encode("utf-8")
    t0 = time.time()
    req = urllib.request.Request("http://127.0.0.1:8189/prompt", data=body,
                                 headers={"Content-Type":"application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            pid = json.load(r)["prompt_id"]
    except urllib.error.HTTPError as e:
        print(f"[{name}] REJEITADO: {e.read().decode(errors='replace')[:400]}", flush=True); continue
    print(f"[{name}] enfileirado (fps={fps})", flush=True)
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
        if time.time() - t0 > 1200:
            print(f"[{name}] TIMEOUT", flush=True); break
    outs = hh.get(pid, {}).get("outputs", {})
    vids = [e for o in outs.values() for k in ("videos", "gifs", "images") for e in o.get(k, []) if e.get("type") == "output"]
    if not vids:
        print(f"[{name}] ERRO: {str(hh.get(pid, {}).get('status'))[:300]}", flush=True); continue
    e0 = vids[0]
    dst = f"{DEST}/{name}" + os.path.splitext(e0["filename"])[1]
    shutil.copyfile(os.path.join(OUTDIR, e0.get("subfolder", ""), e0["filename"]), dst)
    print(f"[{name}] OK em {time.time()-t0:.0f}s -> {dst}", flush=True)
print("cadeia v9 concluida")
