#!/usr/bin/env bash
SRC="C:/Users/userx/Documents/projs/COMFYUI"
STG="C:/Users/userx/Documents/projs/COMFYUI_ghpages"
rm -rf "$STG"; mkdir -p "$STG"
(cd "$SRC" && tar --exclude=.git --exclude=tts --exclude='__pycache__' --exclude='*.log' -cf - .) | (cd "$STG" && tar -xf -)
echo "[$(date +%H:%M:%S)] copiado: $(du -sh "$STG" | cut -f1)"
cd "$STG"
T=$(find . -name "*.mp4" | wc -l); N=0
find . -name "*.mp4" | while read f; do
  N=$((N+1))
  tmp="${f%.mp4}._tmp.mp4"
  if ffmpeg -y -v error -i "$f" -vf "scale='min(1280,iw)':'min(1280,ih)':force_original_aspect_ratio=decrease:force_divisible_by=2" -c:v libx264 -preset fast -crf 26 -pix_fmt yuv420p -c:a aac -b:a 96k -movflags +faststart "$tmp"; then mv "$tmp" "$f"; else rm -f "$tmp"; echo "ERRO encode: $f"; fi
  [ $((N % 20)) -eq 0 ] && echo "[$(date +%H:%M:%S)] $N/$T videos"
done
echo "[$(date +%H:%M:%S)] encode ok: $(du -sh "$STG" | cut -f1)"
git init -q -b gh-pages .
git config user.name flarxen32
git config user.email "flarxen32@users.noreply.github.com"
git add -A
git commit -q -m "site: paginas do projeto com midia 720p" || echo "commit falhou"
git -c credential.helper= push -f "${GH_URL:-https://flarxen32:${GH_TOKEN}@github.com}"/flarxen32/comfyui-comerciais-ia.git" gh-pages:gh-pages 2>&1 | tail -2
echo "FIM: push gh-pages"
