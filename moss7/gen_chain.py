# -*- coding: utf-8 -*-
"""v7 — cadeia CANAVIAL: 4 shots × 2 formatos (1080p horizontal + vertical nativa) + doadores H3."""
import json, time, shutil, os, subprocess, urllib.request, uuid

TOOLS = "C:/Users/userx/Documents/projs/game dev/tools/comfy"
INPUT = TOOLS + "/portable/ComfyUI/input"
OUTDIR = TOOLS + "/portable/ComfyUI/output"
BASE = "C:/Users/userx/Documents/projs/COMFYUI"
DEST = BASE + "/moss7/video"
WFS = {"h3": TOOLS + "/workflows/minimax_h3_i2v_api.json",
       "turbo": TOOLS + "/workflows/wan22_turbo_gguf_api.json"}
GGUF = "Wan2_2-TI2V-5B-Turbo-Q5_K_M.gguf"

VID = {
 "cane": ("Macro of tall sugarcane stalks at dawn, dew droplets glistening, a very gentle breeze moving "
          "the leaves, golden rim light slowly brightening. Camera: locked tripod macro."),
 "pour": ("Artisanal cachaça pours over crushed ice into a short glass with a lime wedge, tiny bubbles "
          "rising, condensation forming on the glass, warm bar light with amber bokeh. Camera: locked "
          "tripod close-up."),
 "bottle": ("Static close-up of a tall clear artisanal cachaça bottle, the craft paper label reading "
            "CANAVIAL and CACHAÇA ARTESANAL sharp and legible, a soft glint of light traveling along the "
            "glass, lime wedges and sugarcane sticks at the base. Camera: locked tripod."),
 "glass": ("A finished caipirinha on a rustic wooden bar top, crushed ice and muddled lime, condensation "
           "droplets growing, candle bokeh flickering softly in the background. Camera: very slow dolly-in."),
}
AUD = {
 "cane": ("Macro of sugarcane at dawn. Ambient audio: morning birdsong, wind through leaves, and a joyful "
          "brazilian choro with cavaquinho beginning."),
 "pour": ("Cachaça pouring over ice. Ambient audio: liquid pour, ice cracking softly, and the choro with "
          "pandeiro continuing."),
 "bottle": ("Close-up of a cachaça bottle. Ambient audio: quiet bar room tone, a soft glass glint chime, "
            "and the choro swelling warmly."),
 "glass": ("A caipirinha on a bar top. Ambient audio: bar murmur, ice settling, and the choro resolving "
           "with a warm final chord."),
}

FMTS = {"": (1920, 1088), "_v": (1088, 1920)}
TAKES = []
for key in ("cane", "pour", "bottle", "glass"):
    for sfx, (w, h) in FMTS.items():
        TAKES.append((f"s7v7_{key}{sfx}", "turbo", f"s7_{key}{sfx}", (w, h), 4, 11100 + len(TAKES), key))
for i, key in enumerate(("cane", "pour", "bottle", "glass")):
    TAKES.append((f"aud_{key}", "h3", f"s7_{key}", (832, 480), 4, 11200 + i, key, True))

client = str(uuid.uuid4())
os.makedirs(DEST, exist_ok=True)
for t in TAKES:
    name, engine, still, (w, h), steps, seed, key = t[0], t[1], t[2], t[3], t[4], t[5], t[6]
    is_aud = len(t) > 7 and t[7]
    prompt = AUD[key] if is_aud else VID[key]
    src = f"{BASE}/moss7/stills/{still}.png"
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
                 .replace("__OUTPREFIX__", "moss7/" + name))
    body = json.dumps({"prompt": json.loads(wf_txt), "client_id": client}).encode("utf-8")
    t0 = time.time()
    req = urllib.request.Request("http://127.0.0.1:8189/prompt", data=body,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            pid = json.load(r)["prompt_id"]
    except urllib.error.HTTPError as e:
        print(f"[{name}] REJEITADO: {e.read().decode(errors='replace')[:400]}", flush=True); continue
    print(f"[{name}] enfileirado {pid}", flush=True)
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
print("cadeia v7 concluida")
