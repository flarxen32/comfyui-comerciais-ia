#!/usr/bin/env bash
# Vigia os downloads e dispara a fila de efeitos quando tudo estiver pronto.
set -u
M="/c/Users/userx/Documents/projs/game dev/tools/comfy/portable/ComfyUI/models"
FLAG=/c/Users/userx/yt_dl/v38_started.flag
LOG=/c/Users/userx/yt_dl/watch.log
sz(){ stat -c%s "$1" 2>/dev/null || echo 0; }
while true; do
  if [ -f "$FLAG" ]; then exit 0; fi
  g=$(sz "$M/text_encoders/gemma4-12b-with-proj-ltx-2.5-comfy-int8-convrot.safetensors")
  n=$(sz "$M/diffusion_models/ltx-2.5-22b-distilled-transformer-nvfp4.safetensors")
  loras_done=$(grep -c "MS ALL DONE" /c/Users/userx/yt_dl/dl_ms.log 2>/dev/null || echo 0)
  loras_fail=$(grep -c FAIL /c/Users/userx/yt_dl/dl_ms.log 2>/dev/null || echo 0)
  echo "[$(date +%H:%M:%S)] gemma=$g/15372969374 nvfp4=$n/18721548408 loras_done=$loras_done fail=$loras_fail" >> "$LOG"
  need_loras=$(( loras_done == 1 ? 0 : 1 ))
  # se a fila de loras terminou com falhas mas >=13 ok, segue mesmo assim
  total_ok=$(grep -c "^\[.*\] OK ltx" /c/Users/userx/yt_dl/dl_ms.log 2>/dev/null || echo 0)
  if [ "$g" -ge 15372969374 ] && [ "$n" -ge 18721548408 ] && { [ "$need_loras" -eq 0 ] || [ "$total_ok" -ge 13 ]; }; then
    echo "[$(date +%H:%M:%S)] TUDO PRONTO — disparando fila" >> "$LOG"
    touch "$FLAG"
    cd /c/Users/userx/Documents/projs/COMFYUI/moss38
    nohup bash run_all.sh >> run.log 2>&1 &
    exit 0
  fi
  sleep 60
done
