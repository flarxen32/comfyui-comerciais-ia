# -*- coding: utf-8 -*-
"""v13 QA — transcreve a fala do reel/take com faster-whisper (small, int8, CPU).
Uso: python qa_whisper.py <video.mp4>"""
import sys, subprocess, os, tempfile

P = "C:/Users/userx/Documents/projs/game dev/tools/comfy/portable/python_embeded/python.exe"
vid = sys.argv[1]
wav = os.path.join(tempfile.gettempdir(), "qa_v13.wav")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", vid, "-vn", "-ac", "1", "-ar", "16000", wav], check=True)
code = (
    "from faster_whisper import WhisperModel;import sys\n"
    "m=WhisperModel('small', device='cpu', compute_type='int8')\n"
    f"segs,info=m.transcribe(r'{wav}', language='pt')\n"
    "print(' '.join(s.text.strip() for s in segs))\n"
)
r = subprocess.run([P, "-c", code], capture_output=True, text=True, encoding="utf-8")
print("FALA:", r.stdout.strip())
if r.returncode != 0: print("ERR:", r.stderr[-400:])
