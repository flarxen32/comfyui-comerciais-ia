# -*- coding: utf-8 -*-
"""v3 — cadeia completa de renders GAROA (fila encadeada, pagecache quente):
1) 3 takes H3@8st (hops, bottle, glass) · 2) hero Wan fp16 20st (pour) · 3) 4 doadores de áudio H3@4st"""
import json, time, shutil, os, subprocess, sys, urllib.request, uuid

TOOLS = "C:/Users/userx/Documents/projs/game dev/tools/comfy"
INPUT = TOOLS + "/portable/ComfyUI/input"
OUTDIR = TOOLS + "/portable/ComfyUI/output"
BASE = "C:/Users/userx/Documents/projs/COMFYUI"
DEST = BASE + "/moss3/video"
WFS = {"h3": TOOLS + "/workflows/minimax_h3_i2v_api.json",
       "wan": TOOLS + "/workflows/wan22_i2v_api.json"}

VID_PROMPTS = {
 "hops": ("Macro of fresh green hop cones in light rain, raindrops falling gently, leaves swaying softly, "
          "soft overcast light slowly brightening. The hop cones stay sharp and stable. Camera: very slow "
          "dolly-in, almost imperceptible. Ambient audio: soft rain on leaves, gentle wind, distant thunder, "
          "and a slow melancholic indie guitar theme with warm reverb building softly."),
 "bottle": ("Static close-up of a matte dark craft beer bottle covered in condensation droplets, one droplet "
            "slides slowly down the label, faint mist drifts in the dark background. The label reading GAROA "
            "stays sharp, stable and legible. Camera: locked tripod, no movement. Ambient audio: quiet room "
            "tone, a soft fizz, a single low piano note, and the slow melancholic indie guitar theme continuing."),
 "pour": ("Amber IPA pours from a bottle into a tall tilted glass, a cascade of thick creamy foam builds and "
          "swirls, fine bubbles rise through the golden liquid. The bottle, glass and foam stay physically "
          "consistent. Camera: locked tripod macro, no camera movement."),
 "glass": ("A tall glass of amber IPA with thick foam on a rustic wooden table, rain runs down the window "
           "behind creating moving bokeh, condensation glitters on the glass. Camera: very slow dolly-in. "
           "Ambient audio: rain against glass, a soft glass clink, and the indie guitar theme resolving "
           "warmly with a final chord."),
}
AUD_PROMPTS = {k: v for k, v in VID_PROMPTS.items() if k != "pour"}
AUD_PROMPTS["pour"] = VID_PROMPTS["pour"] + (" Ambient audio: satisfying beer pour and fizzing foam, and the "
                                             "indie guitar theme swelling with light percussion.")

TAKES = [
    # (name, engine, still, res, steps, seed) — steps: h3=8, wan=20
    ("s3v3_hops",   "h3",  "s3_hops",   (832, 480),   8, 5101),
    ("s3v3_bottle", "h3",  "s3_bottle", (832, 480),   8, 5102),
    ("s3v3_glass",  "h3",  "s3_glass",  (832, 480),   8, 5103),
    ("s3v3_pour",   "wan", "s3_pour",   (1280, 704), 20, 5104),
    ("aud_h3_hops",   "h3", "s3_hops",   (832, 480), 4, 6101),
    ("aud_h3_bottle", "h3", "s3_bottle", (832, 480), 4, 6102),
    ("aud_h3_pour",   "h3", "s3_pour",   (832, 480), 4, 6103),
    ("aud_h3_glass",  "h3", "s3_glass",  (832, 480), 4, 6104),
]

client = str(uuid.uuid4())
os.makedirs(DEST, exist_ok=True)

def run(t):
    name, engine, still, (w, h), steps, seed = t
    use_audio_prompt = name.startswith("aud_")
    prompt = (AUD_PROMPTS if use_audio_prompt else VID_PROMPTS)[still.split("_")[1] if False else
              {"s3_hops": "hops", "s3_bottle": "bottle", "s3_pour": "pour", "s3_glass": "glass"}[still]]
    src = f"{BASE}/moss3/stills/{still}.png"
    fname = f"{name}_{w}x{h}.png"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src,
                    "-vf", f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}",
                    os.path.join(INPUT, fname)], check=True)
    tpl = open(WFS[engine], encoding="utf-8").read()
    cfg = "5.0" if engine == "wan" else ""
    wf_txt = (tpl.replace("__IMAGE__", fname)
                 .replace("__PROMPT__", json.dumps(prompt)[1:-1])
                 .replace("__WIDTH__", str(w)).replace("__HEIGHT__", str(h))
                 .replace("__LENGTH__", "121").replace("__STEPS__", str(steps))
                 .replace("__SEED__", str(seed))
                 .replace("__OUTPREFIX__", "moss3/" + name))
    body = json.dumps({"prompt": json.loads(wf_txt), "client_id": client}).encode("utf-8")
    t0 = time.time()
    req = urllib.request.Request("http://127.0.0.1:8189/prompt", data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        pid = json.load(r)["prompt_id"]
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
        if time.time() - t0 > 4200:
            print(f"[{name}] TIMEOUT"); return
    outs = hh.get(pid, {}).get("outputs", {})
    vids = []
    for o in outs.values():
        for k in ("videos", "gifs", "images"):
            for e in o.get(k, []):
                if e.get("type") == "output":
                    vids.append(e)
    if not vids:
        print(f"[{name}] ERRO: {str(hh[pid].get('status'))[:300]}"); return
    e0 = vids[0]
    dst = f"{DEST}/{name}" + os.path.splitext(e0["filename"])[1]
    shutil.copyfile(os.path.join(OUTDIR, e0.get("subfolder", ""), e0["filename"]), dst)
    print(f"[{name}] OK em {time.time()-t0:.0f}s -> {dst}", flush=True)

for t in TAKES:
    try:
        run(t)
    except Exception as ex:
        print(f"[{t[0]}] FALHOU: {ex}", flush=True)
print("cadeia concluida")
