# -*- coding: utf-8 -*-
"""QA visual local: Qwen3.5-9B (encoder do MOSS) como VLM via TextGenerate.
Uso: python qa_vlm.py <imagem.png> <pergunta>
Escreve a resposta em stdout."""
import json, time, sys, os, shutil, urllib.request, uuid

WF = "C:/Users/userx/Documents/projs/game dev/tools/comfy/workflows/qa_vlm_api.json"
INPUT = "C:/Users/userx/Documents/projs/game dev/tools/comfy/portable/ComfyUI/input"

img, prompt = sys.argv[1], sys.argv[2]
fname = "qa_" + os.path.basename(img).replace(" ", "_")
shutil.copyfile(img, os.path.join(INPUT, fname))

tpl = open(WF, encoding="utf-8").read()
wf_txt = (tpl.replace("__IMAGE__", fname)
             .replace("__PROMPT__", json.dumps(prompt, ensure_ascii=False)[1:-1]))
body = json.dumps({"prompt": json.loads(wf_txt), "client_id": str(uuid.uuid4())}).encode("utf-8")
t0 = time.time()
req = urllib.request.Request("http://127.0.0.1:8189/prompt", data=body,
                             headers={"Content-Type": "application/json"})
try:
    with urllib.request.urlopen(req) as r:
        pid = json.load(r)["prompt_id"]
except urllib.error.HTTPError as e:
    print("REJEITADO:", e.read().decode(errors="replace")[:600]); sys.exit(1)
print(f"[qa] {pid} aguardando...", file=sys.stderr)
h = {}
while time.time() - t0 < 900:
    time.sleep(4)
    with urllib.request.urlopen(f"http://127.0.0.1:8189/history/{pid}") as r:
        h = json.load(r)
    if pid in h and (h[pid].get("status", {}).get("completed") or h[pid].get("status", {}).get("status_str") == "error"):
        break
outs = h.get(pid, {}).get("outputs", {})
print("RAW:", json.dumps(outs)[:400], file=sys.stderr)
txt = ""
for o in outs.values():
    for k in ("text", "STRING", "string", "results"):
        if k in o:
            v = o[k]
            txt = v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)
            break
if not txt:
    # fallback: varre qualquer valor string nos outputs
    for o in outs.values():
        for v in o.values():
            if isinstance(v, str):
                txt = v; break
print(f"[qa] {time.time()-t0:.0f}s")
print(txt if txt else "(sem texto — ver RAW acima)")
