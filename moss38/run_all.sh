#!/usr/bin/env bash
# v38 — fila sequencial de todos os efeitos (para a noite toda)
set -u
cd /c/Users/userx/Documents/projs/COMFYUI/moss38
ORDER=(
  day2night
  clean_plate
  water
  deblur
  decompression
  colorization
  restore
  refine
  upscale2x
  alpha_gen
  layout2render
  cinemagraph
  slowmo
  ingredients
  sdr2hdr
)
# smoke primeiro com resolução menor p/ validar execução de ponta a ponta
echo "[$(date +%H:%M:%S)] === SMOKE day2night 640x352 ===" >> run.log
node run_effect.js day2night seed=7 width=640 height=352
check_server() {
  curl -s -m 4 http://127.0.0.1:8189/system_stats > /dev/null || {
    echo "[$(date +%H:%M:%S)] servidor caiu — reiniciando" >> run.log
    cd "/c/Users/userx/Documents/projs/game dev/tools/comfy" && ./comfy.sh start >> /c/Users/userx/Documents/projs/COMFYUI/moss38/run.log 2>&1
    cd /c/Users/userx/Documents/projs/COMFYUI/moss38
    sleep 20
  }
}
for e in "${ORDER[@]}"; do
  echo "[$(date +%H:%M:%S)] === $e ===" >> run.log
  node run_effect.js "$e"
  check_server
  sleep 20   # respiro de VRAM entre jobs (protocolo anti-crash)
done
echo "[$(date +%H:%M:%S)] === FILA COMPLETA ===" >> run.log
