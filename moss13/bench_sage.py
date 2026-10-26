# -*- coding: utf-8 -*-
"""Benchmark SageAttention — renderiza o take prod_rain_lora idêntico (seed 15001) e cronometra.
Uso: python bench_sage.py <outprefix>"""
import json, time, sys, os, urllib.request, uuid

WF_LORA = "C:/Users/userx/Documents/projs/game dev/tools/comfy/workflows/wan22_turbo_gguf_lora_api.json"
INPUT = "C:/Users/userx/Documents/projs/game dev/tools/comfy/portable/ComfyUI/input"
OUT = "C:/Users/userx/Documents/projs/game dev/tools/comfy/portable/ComfyUI/output"
prefix = sys.argv[1]

PROMPT = ("Vertical cinematic product shot: a premium clear glass mineral water bottle with a deep "
          "blue-green label reading NASCENTE stands on a wet dark stone ledge during steady light rain, "
          "raindrops falling and hitting the bottle and the stone, each drop splashing into tiny bright "
          "droplets that bounce with real gravity at natural speed, water beads rolling slowly down the "
          "cold glass, cold condensation, soft city lights bokeh in the dark background, slow camera "
          "push-in, photorealistic luxury water commercial")

s = (open(WF_LORA, encoding="utf-8").read()
     .replace("__PROMPT__", json.dumps(PROMPT)[1:-1])
     .replace("__UNETGGUF__", "Wan2_2-TI2V-5B-Turbo-Q5_K_M.gguf")
     .replace("__WIDTH__", "1088").replace("__HEIGHT__", "1920")
     .replace("__LENGTH__", "121").replace("__STEPS__", "4")
     .replace("__CFG__", "1.0").replace("__SAMPLER__", "euler")
     .replace("__SEED__", "15001").replace("__IMAGE__", "prod_bottle.png")
     .replace("__OUTPREFIX__", "moss13/" + prefix)
     .replace("__LORANAME__", "beauty_of_rain_wan2_2_ti2v_5B.safetensors")
     .replace("__LORASTRENGTH__", "0.7"))
body = json.dumps({"prompt": json.loads(s), "client_id": str(uuid.uuid4())}).encode("utf-8")
t0 = time.time()
req = urllib.request.Request("http://127.0.0.1:8189/prompt", data=body, headers={"Content-Type":"application/json"})
with urllib.request.urlopen(req) as r: pid = json.load(r)["prompt_id"]
while True:
    time.sleep(5)
    with urllib.request.urlopen(f"http://127.0.0.1:8189/history/{pid}") as r: h = json.load(r)
    if pid in h and (h[pid].get("status", {}).get("completed") or h[pid].get("status", {}).get("status_str") == "error"):
        break
    if time.time()-t0 > 2400: print("TIMEOUT"); break
hh = h.get(pid, {})
ok = any(o.get("images") for o in hh.get("outputs", {}).values())
print(f"{prefix}: {'OK' if ok else 'ERRO'} em {time.time()-t0:.0f}s")
