# -*- coding: utf-8 -*-
"""Benchmark de VAE decode: Turbo Q5 + VAEDecodeTiled (2 configs), 25 frames."""
import json, time, os, subprocess, urllib.request, uuid

TOOLS = "C:/Users/userx/Documents/projs/game dev/tools/comfy"
INPUT = TOOLS + "/portable/ComfyUI/input"
GGUF = "Wan2_2-TI2V-5B-Turbo-Q5_K_M.gguf"

BASE_WF = {
 "37": {"class_type": "UnetLoaderGGUF", "inputs": {"unet_name": GGUF}},
 "38": {"class_type": "CLIPLoader", "inputs": {"clip_name": "umt5_xxl_fp8_e4m3fn_scaled.safetensors", "type": "wan", "device": "default"}},
 "39": {"class_type": "VAELoader", "inputs": {"vae_name": "wan2.2_vae.safetensors"}},
 "56": {"class_type": "LoadImage", "inputs": {"image": "dt_frame.png"}},
 "55": {"class_type": "Wan22ImageToVideoLatent", "inputs": {"vae": ["39",0], "width": 1280, "height": 704, "length": 25, "batch_size": 1, "start_image": ["56",0]}},
 "7": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["38",0], "text": "locked tripod macro, espresso pouring, crema swirling"}},
 "6": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["38",0], "text": "static, worst quality"}},
 "48": {"class_type": "ModelSamplingSD3", "inputs": {"model": ["37",0], "shift": 8}},
 "3": {"class_type": "KSampler", "inputs": {"model": ["48",0], "positive": ["7",0], "negative": ["6",0], "latent_image": ["55",0], "seed": 99, "steps": 4, "cfg": 1.0, "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0}},
 "57": {"class_type": "CreateVideo", "inputs": {"images": ["8",0], "fps": 24}},
 "58": {"class_type": "SaveVideo", "inputs": {"video": ["57",0], "filename_prefix": "moss4/dt", "format": "auto"}},
}

CONFIGS = {
 "A_defaults": {"class_type": "VAEDecodeTiled", "inputs": {"samples": ["3",0], "vae": ["39",0], "tile_size": 512, "overlap": 64, "temporal_size": 64, "temporal_overlap": 8}},
 "B_bigtiles": {"class_type": "VAEDecodeTiled", "inputs": {"samples": ["3",0], "vae": ["39",0], "tile_size": 640, "overlap": 64, "temporal_size": 32, "temporal_overlap": 8}},
}

subprocess.run(["ffmpeg","-y","-v","error","-i","C:/Users/userx/Documents/projs/COMFYUI/moss2/stills/s2_pour.png",
                "-vf","scale=1280:704:force_original_aspect_ratio=increase,crop=1280:704",
                os.path.join(INPUT,"dt_frame.png")], check=True)

for name, dec in CONFIGS.items():
    wf = dict(BASE_WF); wf["8"] = dec
    wf["58"]["inputs"]["filename_prefix"] = "moss4/dt_" + name
    body = json.dumps({"prompt": wf, "client_id": str(uuid.uuid4())}).encode()
    req = urllib.request.Request("http://127.0.0.1:8189/prompt", data=body, headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req) as r: pid = json.load(r)["prompt_id"]
    t0 = time.time(); h = {}
    while time.time()-t0 < 2400:
        time.sleep(5)
        with urllib.request.urlopen(f"http://127.0.0.1:8189/history/{pid}") as r: h = json.load(r)
        if pid in h:
            st = h[pid].get("status",{})
            if st.get("completed") or st.get("status_str")=="error": break
    print(f"[{name}] total {time.time()-t0:.0f}s (25 frames) status={h.get(pid,{}).get('status',{}).get('status_str')}", flush=True)
