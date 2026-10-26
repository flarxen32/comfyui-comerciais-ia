# -*- coding: utf-8 -*-
"""Enfileira os 4 takes do comercial FLOW no ComfyUI (porta 8189).
Tecnica validada na skill gen-video: takes de 243f@8st com ancoras first/last
compartilhadas (first do take N = last do take anterior), submissao em lote
para a fila encadear com pagecache quente apos o job R2V."""
import json, urllib.request, uuid

BASE = "C:/Users/userx/Documents/projs/game dev/tools/comfy/workflows/minimax_h3_i2v_fl_api.json"
CHAR = ("A stylish Brazilian grandmother in her early seventies, short silver-white hair, "
        "gold-rimmed sunglasses, blue denim jacket over a white t-shirt, relaxed blue jeans "
        "and crisp white sneakers")
STREET = "on a quiet Brazilian suburban street with small colorful houses in warm morning light"
PLAZA = "on a small sunny neighborhood plaza with palm trees and a bench in golden morning light"
CONSIST = "Her face stays sharp, stable and consistent throughout the video."

takes = [
    dict(out="flow_take1", first="flowA.png", last="flowB.png", seed=1111,
         prompt=(f"{CHAR} {STREET}. She finishes tying the laces of her white sneakers sitting on the front "
                 "step of the yellow house, then stands up, stretches her back with a confident smile and "
                 f"puts her hands on her hips looking straight at the camera. {CONSIST} Camera: slow gentle "
                 "push-in from wide to medium. Ambient sound: morning birds, a distant rooster, and a soft "
                 "uplifting amapiano piano melody starting.")),
    dict(out="flow_take2", first="flowB.png", last="flowC.png", seed=2222,
         prompt=(f"{CHAR} {STREET}. She starts walking briskly down the sidewalk with light dance steps, "
                 "swinging her arms in rhythm and bobbing her head to the beat, greeting a neighbor who "
                 "waves back, ending mid-stride with one foot planted forward and a cheerful expression. "
                 f"{CONSIST} Camera: smooth tracking shot alongside her at steady walking pace. Audio: the "
                 "upbeat amapiano beat grows with deep bass and shakers, her footsteps landing in rhythm.")),
    dict(out="flow_take3", first="flowC2.png", last="flowD.png", seed=3333,
         prompt=(f"{CHAR} {PLAZA}. She dances joyfully with full amapiano energy - body rolls, hip swings "
                 "and wave-like arm movements - building up to a triumphant finish with both arms raised "
                 f"high while neighbors clap around her. {CONSIST} Camera: static wide shot. Audio: uplifting "
                 "amapiano music at full energy with clapping and cheerful voices.")),
    dict(out="flow_take4", first="flowD.png", last="flowE.png", seed=4444,
         prompt=(f"{CHAR} {PLAZA}. She lowers her arms, catches her breath with a proud smile, picks up one "
                 "white sneaker from the bench and holds it up at chest height presenting it to the camera, "
                 "speaking Brazilian Portuguese with accurate lip sync, saying: FLOW. Idade não define o "
                 "ritmo. With the word FLOW written in large bold white capital letters appearing on screen "
                 f"behind her. {CONSIST} Camera: slow push-in to a medium shot. Audio: the amapiano music "
                 "resolves warmly, palm leaves rustling in the morning breeze.")),
]

tpl = open(BASE, encoding="utf-8").read()
client = str(uuid.uuid4())
prompt_ids = []
for t in takes:
    s = (tpl.replace("__PROMPT__", json.dumps(t["prompt"])[1:-1])
            .replace("__WIDTH__", "832").replace("__HEIGHT__", "480")
            .replace("__LENGTH__", "243").replace("__STEPS__", "8")
            .replace("__SEED__", str(t["seed"]))
            .replace("__OUTPREFIX__", t["out"])
            .replace('"image": "sketch_first.png"', f'"image": "{t["first"]}"')
            .replace('"image": "sketch_last.png"', f'"image": "{t["last"]}"'))
    wf = json.loads(s)  # valida
    body = json.dumps({"prompt": wf, "client_id": client}).encode("utf-8")
    req = urllib.request.Request("http://127.0.0.1:8189/prompt", data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        resp = json.load(r)
    pid = resp.get("prompt_id")
    prompt_ids.append((t["out"], pid))
    print(t["out"], "->", pid, resp.get("number", ""))

json.dump(prompt_ids, open("C:/Users/userx/Documents/projs/COMFYUI/comercial/take_ids.json", "w"))
print("enfileirados:", len(prompt_ids))
