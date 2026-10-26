#!/bin/bash
# Concatena os 4 takes do comercial FLOW no video final (com corte seco T2->T3).
# Uso: bash build_final.sh
set -e
OUT="/c/Users/userx/Documents/projs/game dev/tools/comfy/portable/ComfyUI/output"
DST="/c/Users/userx/Documents/projs/COMFYUI/comercial"
cd "$DST"

# copia takes do output do ComfyUI (nomes: flow_takeN_00001.mp4)
for n in 1 2 3 4; do
  f=$(ls "$OUT"/flow_take${n}_00001_.mp4 2>/dev/null | head -1)
  [ -z "$f" ] && { echo "take $n nao encontrado"; exit 1; }
  cp -f "$f" take${n}.mp4
done

# concat com re-encode leve (evita glitch de timestamp de audio entre takes)
printf "file 'take1.mp4'\nfile 'take2.mp4'\nfile 'take3.mp4'\nfile 'take4.mp4'\n" > list.txt
ffmpeg -y -v error -f concat -safe 0 -i list.txt -c:v libx264 -crf 19 -pix_fmt yuv420p -c:a aac -b:a 160k flow_commercial.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 flow_commercial.mp4
echo "OK -> $DST/flow_commercial.mp4"
