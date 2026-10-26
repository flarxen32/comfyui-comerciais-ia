# -*- coding: utf-8 -*-
"""v3 — doadores de áudio: H3 i2v @4 steps (rápido) com direção musical no prompt.
Gera vídeo só para roubar a trilha; usa os stills GAROA como first frame.
Uso: python gen_audio.py [shot ...]  (sem args = todos)"""
import json, time, shutil, sys, os, subprocess, urllib.request, uuid

TOOLS = "C:/Users/userx/Documents/projs/game dev/tools/comfy"
WF = TOOLS + "/workflows/minimax_h3_i2v_api.json"
INPUT = TOOLS + "/portable/ComfyUI/input"
OUTDIR = TOOLS + "/portable/ComfyUI/output"
BASE = "C:/Users/userx/Documents/projs/COMFYUI"

AUDIO_PROMPTS = {
 "hops": ("Macro of hop cones in light rain. Ambient audio: soft rain on leaves, gentle wind, distant "
          "thunder, and a slow melancholic indie guitar theme with warm reverb building softly."),
 "bottle": ("Static close-up of a cold beer bottle with condensation, one droplet sliding down. Ambient "
            "audio: quiet room tone, a soft fizz, a single low piano note, and the slow melancholic indie "
            "guitar theme continuing."),
 "pour": ("Amber beer pouring into a glass with building foam. Ambient audio: satisfying beer pour and "
          "fizzing foam, and the indie guitar theme swelling with light percussion."),
 "glass": ("A glass of beer by a rain-streaked window. Ambient audio: rain against glass, a soft glass "
           "clink, and the indie guitar theme resolving warmly with a final chord."),
}

client = str(uuid.uuid4())
os.makedirs(f"{BASE}/moss3/video", exist_ok=True)
sel = sys.argv[1:] or list(AUDIO_PROMPTS)

for name in sel:
    src = f"{BASE}/moss3/stills/s3_{name}.png"
    fname = f"aud_{name}_832x480.png"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src,
                    "-vf", "scale=832:480:force_original_aspect_ratio=increase,crop=832:480",
                    os.path.join(INPUT, fname)], check=True)
    tpl = open(WF, encoding="utf-8").read()
    wf_txt = (tpl.replace("__IMAGE__", fname)
                 .replace("__PROMPT__", json.dumps(AUDIO_PROMPTS[name])[1:-1])
                 .replace("__WIDTH__", "832").replace("__HEIGHT__", "480")
                 .replace("__LENGTH__", "121").replace("__STEPS__", "4")
                 .replace("__SEED__", str(6100 + list(AUDIO_PROMPTS).index(name)))
                 .replace("__OUTPREFIX__", "moss3/aud_" + name))
    body = json.dumps({"prompt": json.loads(wf_txt), "client_id": client}).encode("utf-8")
    t0 = time.time()
    req = urllib.request.Request("http://127.0.0.1:8189/prompt", data=body,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            pid = json.load(r)["prompt_id"]
    except urllib.error.HTTPError as e:
        print(f"[aud_{name}] REJEITADO: {e.read().decode(errors='replace')[:400]}"); continue
    print(f"[aud_{name}] h3@4st enfileirado {pid}; aguardando...", flush=True)
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
        if time.time() - t0 > 1800:
            print(f"[aud_{name}] TIMEOUT"); break
    outs = hh.get(pid, {}).get("outputs", {})
    vids = []
    for o in outs.values():
        for k in ("videos", "gifs", "images"):
            for e in o.get(k, []):
                if e.get("type") == "output":
                    vids.append(e)
    if not vids:
        print(f"[aud_{name}] ERRO sem saida: {str(hh[pid].get('status'))[:300]}"); continue
    e0 = vids[0]
    dst = f"{BASE}/moss3/video/aud_{name}" + os.path.splitext(e0["filename"])[1]
    shutil.copyfile(os.path.join(OUTDIR, e0.get("subfolder", ""), e0["filename"]), dst)
    print(f"[aud_{name}] OK em {time.time()-t0:.0f}s -> {dst}", flush=True)
print("concluido")
