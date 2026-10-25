# -*- coding: utf-8 -*-
"""v5 — cadeia AMARGO 1080p nativo (1920x1088):
hero fp16 20st + 3 Turbo 4st (bar com dolly = texto em movimento) + 4 doadores H3@4st."""
import json, time, shutil, os, subprocess, urllib.request, uuid

TOOLS = "C:/Users/userx/Documents/projs/game dev/tools/comfy"
INPUT = TOOLS + "/portable/ComfyUI/input"
OUTDIR = TOOLS + "/portable/ComfyUI/output"
BASE = "C:/Users/userx/Documents/projs/COMFYUI"
DEST = BASE + "/moss5/video"
WFS = {"h3": TOOLS + "/workflows/minimax_h3_i2v_api.json",
       "wan": TOOLS + "/workflows/wan22_i2v_api.json",
       "turbo": TOOLS + "/workflows/wan22_turbo_gguf_api.json"}
GGUF = "Wan2_2-TI2V-5B-Turbo-Q5_K_M.gguf"

VID = {
 "beans": ("Macro of a ripe cocoa pod split open with white beans inside, fine dust particles drifting "
           "slowly through the warm side light, everything else still. Camera: locked tripod macro."),
 "bar": ("Slow subtle dolly-in toward a dark chocolate bar embossed with the word AMARGO and the smaller "
         "line 70% CACAU, fine cocoa dust glittering in the warm key light. The embossed letters stay "
         "sharp, stable and legible throughout the move. Camera: very slow smooth dolly-in."),
 "pour": ("Thick melted dark chocolate pours in a slow glossy ribbon onto a dark stone surface, the "
          "chocolate folding and pooling with a rich satin sheen, dramatic warm side light with deep "
          "shadows, dark patisserie background with soft bokeh. Camera: locked tripod macro."),
 "truffle": ("Artisanal chocolate truffles dusted with cocoa powder on rough stone, a faint drift of "
             "cocoa in the air, soft steam curling through the window light. Camera: very slow dolly-in."),
}
AUD = {
 "beans": ("Macro of a split cocoa pod. Ambient audio: quiet rainforest ambience, soft wind, and a slow "
           "warm samba guitar with cello beginning gently."),
 "bar": ("Close-up of an embossed chocolate bar. Ambient audio: a soft deep cello note, quiet room tone, "
         "and the samba guitar with cello continuing tenderly."),
 "pour": ("Melted chocolate pouring in slow motion. Ambient audio: thick slow liquid pours and folds, and "
          "the samba guitar with cello swelling warmly with light percussion."),
 "truffle": ("Cocoa-dusted truffles in window light. Ambient audio: soft morning ambience, a gentle "
             "sprinkle of cocoa, and the samba guitar with cello resolving with a warm final chord."),
}

TAKES = [
    ("s5v5_pour",     "turbo", "s5_pour",     (1920, 1088), 4,  9201, "pour"),
    ("s5v5_beans",    "turbo", "s5_beans",    (1920, 1088), 4,  9202, "beans"),
    ("s5v5_bar",      "turbo", "s5_bar",      (1920, 1088), 4,  9203, "bar"),
    ("s5v5_truffle",  "turbo", "s5_truffle",  (1920, 1088), 4,  9204, "truffle"),
    ("aud_beans",   "h3", "s5_beans",   (832, 480), 4, 9301, "beans", True),
    ("aud_bar",     "h3", "s5_bar",     (832, 480), 4, 9302, "bar", True),
    ("aud_pour",    "h3", "s5_pour",    (832, 480), 4, 9303, "pour", True),
    ("aud_truffle", "h3", "s5_truffle", (832, 480), 4, 9304, "truffle", True),
]

client = str(uuid.uuid4())
os.makedirs(DEST, exist_ok=True)

for t in TAKES:
    name, engine, still, (w, h), steps, seed, key = t[0], t[1], t[2], t[3], t[4], t[5], t[6]
    is_aud = len(t) > 7 and t[7]
    prompt = AUD[key] if is_aud else VID[key]
    src = f"{BASE}/moss5/stills/{still}.png"
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
                 .replace("__OUTPREFIX__", "moss5/" + name))
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
        if time.time() - t0 > 5400:
            print(f"[{name}] TIMEOUT", flush=True); break
    outs = hh.get(pid, {}).get("outputs", {})
    vids = [e for o in outs.values() for k in ("videos", "gifs", "images") for e in o.get(k, []) if e.get("type") == "output"]
    if not vids:
        print(f"[{name}] ERRO: {str(hh.get(pid,{}).get("status"))[:300]}", flush=True); continue
    e0 = vids[0]
    dst = f"{DEST}/{name}" + os.path.splitext(e0["filename"])[1]
    shutil.copyfile(os.path.join(OUTDIR, e0.get("subfolder", ""), e0["filename"]), dst)
    print(f"[{name}] OK em {time.time()-t0:.0f}s -> {dst}", flush=True)
print("cadeia v5 concluida")
