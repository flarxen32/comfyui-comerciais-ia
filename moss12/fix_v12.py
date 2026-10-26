# -*- coding: utf-8 -*-
"""Fix v12: still Téo c/ barra INTEGRA + takes teo_talk e prod_snap regenerados."""
import json, time, shutil, os, subprocess, urllib.request, uuid

TOOLS = "C:/Users/userx/Documents/projs/game dev/tools/comfy"
INPUT = TOOLS + "/portable/ComfyUI/input"
OUTDIR = TOOLS + "/portable/ComfyUI/output"
BASE = "C:/Users/userx/Documents/projs/COMFYUI"
WFS = {"moss": TOOLS + "/workflows/moss_image_t2i_api.json",
       "h3r": TOOLS + "/workflows/h3_i2v_realism_api.json",
       "h3": TOOLS + "/workflows/minimax_h3_i2v_api.json"}
NEG = "nsfw, worst quality, bad anatomy, watermark, jpeg artifact, extra fingers, deformed hands"

def post(wf_txt, out, timeout=1800):
    body = json.dumps({"prompt": json.loads(wf_txt), "client_id": str(uuid.uuid4())}).encode()
    req = urllib.request.Request("http://127.0.0.1:8189/prompt", data=body, headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req) as r: pid = json.load(r)["prompt_id"]
    t0 = time.time(); h = {}
    while time.time()-t0 < timeout:
        time.sleep(8)
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:8189/history/{pid}") as r: h = json.load(r)
        except Exception: continue
        if pid in h:
            st = h[pid].get("status",{})
            if st.get("completed") or st.get("status_str")=="error": break
    outs = h.get(pid,{}).get("outputs",{})
    media = [e for o in outs.values() for k in ("videos","gifs","images") for e in o.get(k,[]) if e.get("type")=="output"]
    if not media:
        print(f"[{out}] ERRO", flush=True); return
    e0 = media[0]
    sub = "stills" if e0["filename"].endswith(".png") and "char" in out else "video"
    dst_dir = f"{BASE}/moss12/{sub}"
    shutil.copyfile(os.path.join(OUTDIR, e0.get("subfolder",""), e0["filename"]),
                    os.path.join(dst_dir, out + os.path.splitext(e0["filename"])[1]))
    print(f"[{out}] OK {time.time()-t0:.0f}s", flush=True)

# 1) still Téo c/ barra inteira
tpl = open(WFS["moss"], encoding="utf-8").read()
p_teo = ("Vertical phone-selfie style photograph of a young Brazilian man with a curly top undercut and "
         "round glasses, relaxed easygoing smile, wearing a mustard corduroy shirt, holding a completely "
         "intact milk chocolate bar wrapped halfway in craft paper, soft afternoon light in a cozy living "
         "room with plants, authentic UGC selfie aesthetic, photorealistic, sharp face")
wf = (tpl.replace("__PROMPT__", json.dumps(p_teo)[1:-1])
         .replace("__NEGATIVE__", json.dumps(NEG)[1:-1])
         .replace("__WIDTH__","900").replace("__HEIGHT__","1600")
         .replace("__SEED__","12702").replace("__OUTPREFIX__","moss12/char_teo2"))
post(wf, "char_teo2", 900)

# 2) teo_talk regenerado (barra inteira, imóvel)
subprocess.run(["ffmpeg","-y","-v","error","-i",f"{BASE}/moss12/stills/char_teo2.png",
                "-vf","scale=576:1024:force_original_aspect_ratio=increase,crop=576:1024",
                os.path.join(INPUT,"teo_talk2_576x1024.png")], check=True)
p = ("The person from the image, holding the completely intact chocolate bar, looks straight into the "
     "camera speaking Brazilian Portuguese with accurate lip sync, saying: Teste rápido: ouve esse snap? "
     "Isso é chocolate de verdade. QUEBRA. He speaks softly and casually, relaxed tone. The chocolate bar "
     "in his hands stays completely still, identical and intact in every frame — no pieces moving, "
     "shifting or changing on the bar. Natural small head movements and blinks, slight handheld "
     "phone-camera feel. His face stays sharp and consistent. Camera: front-facing phone camera, almost "
     "static. Ambient audio: his calm clear voice, soft room ambience.")
tpl = open(WFS["h3r"], encoding="utf-8").read()
wf = (tpl.replace("__IMAGE__", "teo_talk2_576x1024.png")
         .replace("__PROMPT__", json.dumps(p)[1:-1])
         .replace("__WIDTH__","576").replace("__HEIGHT__","1024")
         .replace("__LENGTH__","243").replace("__STEPS__","8")
         .replace("__SEED__","12703").replace("__OUTPREFIX__","moss12/teo_talk2"))
post(wf, "teo_talk2", 1800)

# 3) prod_snap simplificado: UM quadro, cai, aterrissa e FICA
subprocess.run(["ffmpeg","-y","-v","error","-i",f"{BASE}/moss12/stills/prod_snap.png",
                "-vf","scale=576:1024:force_original_aspect_ratio=increase,crop=576:1024",
                os.path.join(INPUT,"prod_snap2_576x1024.png")], check=True)
p2 = ("One single chocolate square snaps off the standing bar embossed with QUEBRA, falls quickly with "
      "real gravity and lands on the dark slate, settling into its final resting position where it "
      "stays completely still and visible until the end of the shot. Only a couple of tiny crumbs. "
      "Nothing floats, nothing disappears, nothing changes position after landing. The standing bar "
      "remains in place unchanged. Camera: locked tripod close-up. Ambient audio: a crisp chocolate "
      "snap, one piece landing on stone.")
tpl = open(WFS["h3"], encoding="utf-8").read()
wf = (tpl.replace("__IMAGE__", "prod_snap2_576x1024.png")
         .replace("__PROMPT__", json.dumps(p2)[1:-1])
         .replace("__WIDTH__","576").replace("__HEIGHT__","1024")
         .replace("__LENGTH__","121").replace("__STEPS__","8")
         .replace("__SEED__","12704").replace("__OUTPREFIX__","moss12/prod_snap2"))
post(wf, "prod_snap2", 900)
print("fix concluido")
