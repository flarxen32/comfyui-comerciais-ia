# -*- coding: utf-8 -*-
"""v4 — cadeia completa de renders ÂMBAR (todos os takes Wan a 704p nativo, decode tiled):
hero fp16 20st + 3 Turbo 4st + 4 doadores de áudio H3@4st."""
import json, time, shutil, os, subprocess, urllib.request, uuid

TOOLS = "C:/Users/userx/Documents/projs/game dev/tools/comfy"
INPUT = TOOLS + "/portable/ComfyUI/input"
OUTDIR = TOOLS + "/portable/ComfyUI/output"
BASE = "C:/Users/userx/Documents/projs/COMFYUI"
DEST = BASE + "/moss4/video"
WFS = {"h3": TOOLS + "/workflows/minimax_h3_i2v_api.json",
       "wan": TOOLS + "/workflows/wan22_i2v_api.json",
       "turbo": TOOLS + "/workflows/wan22_turbo_gguf_api.json"}
GGUF = "Wan2_2-TI2V-5B-Turbo-Q5_K_M.gguf"

VID = {
 "comb": ("Macro of glowing golden honeycomb cells, thick honey slowly overflowing from one cell and "
          "dripping down in a slow thick thread, warm backlight shifting subtly richer, everything else "
          "still. Camera: locked tripod macro."),
 "jar": ("Static close-up of a hexagonal glass honey jar glowing golden in warm backlight, the label "
         "reading ÂMBAR sharp and legible, a single bead of honey sliding slowly down the glass, the warm "
         "light breathing gently. Camera: locked tripod."),
 "dipper": ("A thick golden ribbon of honey drizzles from a wooden dipper into a small glass bowl in "
            "extreme slow motion, the ribbon folding and stacking elegantly, warm directional light glowing "
            "through the translucent honey, dark warm background with soft bokeh. Camera: locked tripod macro."),
 "bread": ("Golden honey drips from a wooden dipper onto rustic sourdough bread slices, morning window "
           "light with soft steam, the honey pooling and spreading slowly on the crumb. Camera: very slow "
           "dolly-in."),
}
AUD = {
 "comb": ("Macro of honeycomb with honey dripping. Ambient audio: a soft apiary hum, distant birds, and a "
          "slow warm fingerstyle acoustic guitar theme beginning gently."),
 "jar": ("Static close-up of a glowing honey jar. Ambient audio: quiet warm room tone, a soft viscous "
         "honey drip, and the fingerstyle guitar theme continuing tenderly."),
 "dipper": ("Honey drizzling from a dipper in slow motion. Ambient audio: slow thick honey drips and "
            "pours, and the fingerstyle guitar theme swelling warmly with light percussion."),
 "bread": ("Honey dripping on bread in morning light. Ambient audio: morning kitchen ambience, soft "
           "drips, and the fingerstyle guitar theme resolving with a warm final chord."),
}

TAKES = [
    ("s4v4_dipper", "wan",    "s4_dipper", (1280, 704), 20, 7201, "dipper"),
    ("s4v4_comb",   "turbo",  "s4_comb",   (1280, 704), 4,  7202, "comb"),
    ("s4v4_jar",    "turbo",  "s4_jar",    (1280, 704), 4,  7203, "jar"),
    ("s4v4_bread",  "turbo",  "s4_bread",  (1280, 704), 4,  7204, "bread"),
    ("aud_comb",   "h3", "s4_comb",   (832, 480), 4, 7301, "comb", True),
    ("aud_jar",    "h3", "s4_jar",    (832, 480), 4, 7302, "jar", True),
    ("aud_dipper", "h3", "s4_dipper", (832, 480), 4, 7303, "dipper", True),
    ("aud_bread",  "h3", "s4_bread",  (832, 480), 4, 7304, "bread", True),
]

client = str(uuid.uuid4())
os.makedirs(DEST, exist_ok=True)

for t in TAKES:
    name, engine, still, (w, h), steps, seed, key = t[0], t[1], t[2], t[3], t[4], t[5], t[6]
    is_aud = len(t) > 7 and t[7]
    prompt = AUD[key] if is_aud else VID[key]
    src = f"{BASE}/moss4/stills/{still}.png"
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
                 .replace("__OUTPREFIX__", "moss4/" + name))
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
        if time.time() - t0 > 4800:
            print(f"[{name}] TIMEOUT", flush=True); break
    outs = hh.get(pid, {}).get("outputs", {})
    vids = []
    for o in outs.values():
        for k in ("videos", "gifs", "images"):
            for e in o.get(k, []):
                if e.get("type") == "output":
                    vids.append(e)
    if not vids:
        print(f"[{name}] ERRO: {str(hh[pid].get('status'))[:300]}", flush=True); continue
    e0 = vids[0]
    dst = f"{DEST}/{name}" + os.path.splitext(e0["filename"])[1]
    shutil.copyfile(os.path.join(OUTDIR, e0.get("subfolder", ""), e0["filename"]), dst)
    print(f"[{name}] OK em {time.time()-t0:.0f}s -> {dst}", flush=True)
print("cadeia v4 concluida")
