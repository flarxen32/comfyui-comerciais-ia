#!/usr/bin/env bash
# Reels v10 — LUZ: 2 reels verticais de 10 s (char 6,2 + produto 3,8 + overlay marca).
set -euo pipefail
cd "$(dirname "$0")"
V=video
ENC="-c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -r 24"
GRADE="eq=contrast=1.03:saturation=1.04,noise=alls=3.0:allf=t"

reel() { # $1=nome $2=take_char $3=take_prod
  ffmpeg -y -v error -i "$V"/$2.mp4 -t 6.2 -vf "scale=1080:1920:flags=lanczos,$GRADE" $ENC -an "$V"/segA_$1.mp4
  ffmpeg -y -v error -i "$V"/$3.mp4 -t 3.8 -vf "scale=1080:1920:flags=lanczos,eq=contrast=1.04:saturation=1.06,noise=alls=2.0:allf=t" $ENC -an "$V"/segB_$1.mp4
  printf "file 'segA_$1.mp4'\nfile 'segB_$1.mp4'\n" > "$V"/list_$1.txt
  ffmpeg -y -v error -f concat -safe 0 -i "$V"/list_$1.txt -c copy "$V"/body_$1.mp4
  ffmpeg -y -v error -i "$V"/$2.mp4 -i "$V"/luz_theme.flac \
    -filter_complex "[0:a]atrim=0:10,asetpts=N/SR/TB[vo];[1:a]atrim=0:10,volume=0.28[th];[vo][th]amix=inputs=2:duration=first:normalize=0,afade=t=out:st=9.0:d=0.9,loudnorm=I=-14:TP=-1.5:LRA=11[aout]" \
    -map "[aout]" -c:a aac -b:a 192k "$V"/aud_$1.m4a
  VF=$(tr -d '\n' < overlay.flt)
  ffmpeg -y -v error -i "$V"/body_$1.mp4 -i "$V"/aud_$1.m4a \
    -vf "$VF" \
    -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -c:a copy -movflags +faststart -t 10 "$V"/reel_$1.mp4
  rm -f "$V"/segA_$1.mp4 "$V"/segB_$1.mp4 "$V"/body_$1.mp4 "$V"/list_$1.txt "$V"/aud_$1.m4a
  echo "OK: $V/reel_$1.mp4"
}

reel bia  t1_bia_talk prod_drop
reel duda duda_talk   prod_bottle
