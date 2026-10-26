# -*- coding: utf-8 -*-
"""v8 — cadeia MATTA (Turbo 1080p, 2 formatos) + doadores H3. Engine 14B descartado p/ kit (90min/take)."""
import json, time, shutil, os, subprocess, urllib.request, uuid

TOOLS = "C:/Users/userx/Documents/projs/game dev/tools/comfy"
INPUT = TOOLS + "/portable/ComfyUI/input"
OUTDIR = TOOLS + "/portable/ComfyUI/output"
BASE = "C:/Users/userx/Documents/projs/COMFYUI"
DEST = BASE + "/moss8/video"
WFS = {"h3": TOOLS + "/workflows/minimax_h3_i2v_api.json",
       "turbo": TOOLS + "/workflows/wan22_turbo_gguf_api.json"}
GGUF = "Wan2_2-TI2V-5B-Turbo-Q5_K_M.gguf"

VID = {
 "berries": ("Macro of deep purple açaí berries in a woven basket, a gentle breeze, warm jungle morning "
             "light slowly brightening, a berry rolling slightly. Camera: locked tripod macro."),
 "pour": ("Thick deep-purple açaí pours from a blender jug into a ceramic bowl in a slow heavy ribbon, the "
          "creamy texture folding glossy and dense. Camera: locked tripod macro."),
 "bowl": ("Overhead of a finished açaí bowl topped with granola and banana slices, a spoon settling in, "
          "soft morning light shifting. Camera: very slow dolly-in."),
 "spoon": ("A wooden spoon lifts a curl of thick purple açaí with a slow glossy drip falling back into "
           "the bowl, granola crumbs suspended. Camera: locked tripod close-up."),
}
AUD = {
 "berries": ("Macro of açaí berries. Ambient audio: soft jungle birdsong, wind in leaves, and a brazilian "
             "acoustic afro-samba with nylon guitar beginning."),
 "pour": ("Thick açaí pouring into a bowl. Ambient audio: heavy creamy pour, and the afro-samba continuing "
          "with warm hand drums."),
 "bowl": ("Açaí bowl overhead. Ambient audio: morning café ambience, a soft spoon clink, and the afro-samba "
          "swelling smoothly."),
 "spoon": ("Spoon lifting açaí. Ambient audio: a slow glossy drip, quiet room tone, and the afro-samba "
           "resolving with a warm final chord."),
}

FMTS = {"": (1920, 1088), "_v": (1088, 1920)}
TAKES = []
for key in ("berries", "pour", "bowl", "spoon"):
    for sfx, (w, h) in FMTS.items():
        TAKES.append((f"s8v8_{key}{sfx}", "turbo", f"s8_{key}{sfx}", (w, h), 4, 12100 + len(TAKES), key))
for i, key in enumerate(("berries", "pour", "bowl", "spoon")):
    TAKES.append((f"aud_{key}", "h3", f"s8_{key}", (832, 480), 4, 12200 + i, key, True))

client = str(uuid.uuid4())
os.makedirs(DEST, exist_ok=True)
for t in TAKES:
    name, engine, still, (w, h), steps, seed, key = t[0], t[1], t[2], t[3], t[4], t[5], t[6]
    is_aud = len(t) > 7 and t[7]
    prompt = AUD[key] if is_aud else VID[key]
    src = f"{BASE}/moss8/stills/{still}.png"
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
                 .replace("__OUTPREFIX__", "moss8/" + name))
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
print("cadeia v8 concluida")
