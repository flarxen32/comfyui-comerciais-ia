#!/usr/bin/env bash
# passada 2: roda apenas efeitos sem compare/*.mp4
set -u
cd /c/Users/userx/Documents/projs/COMFYUI/moss38
ALL=(day2night clean_plate water deblur decompression colorization restore refine upscale2x alpha_gen layout2render cinemagraph slowmo ingredients sdr2hdr)
for e in "${ALL[@]}"; do
  [ -f "compare/${e}_compare.mp4" ] && continue
  echo "[$(date +%H:%M:%S)] === PASS2 $e ===" >> run.log
  node run_effect.js "$e"
  sleep 15
done
echo "[$(date +%H:%M:%S)] === PASS2 COMPLETA ===" >> run.log
