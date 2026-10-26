#!/usr/bin/env bash
# Montagem do comercial ÂMBAR v4 — 20,0s @ 1280x720, todos os takes 704p nativos.
# Trilha: doadores H3 (diegético) + tema Ace-Step (música) mixados. Master 24fps; 48fps via RIFE depois.
set -euo pipefail
cd "$(dirname "$0")"
V=video; S=stills
GRADE="eq=contrast=1.04:saturation=1.08,unsharp=5:5:0.4,noise=alls=2.2:allf=t"
ENC="-c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -r 24"

# 1) end card zoom 3,8 s a partir do 1440p UltraSharp
ffmpeg -y -v error -loop 1 -framerate 24 -t 3.8 -i "$S"/s4_endcard_up*_.png -vf "scale=2560:1440,zoompan=z='1+0.05*on/91':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=2560x1440:fps=24,scale=1280:720:flags=lanczos,$GRADE,format=yuv420p" $ENC -an "$V"/seg_endcard.mp4

# 2) segmentos 720p (fontes 1280x704 nativas)
ffmpeg -y -v error -i "$V"/s4v4_comb.mp4   -t 4.2 -vf "scale=1280:720:flags=lanczos,$GRADE" $ENC -an "$V"/seg_comb.mp4
ffmpeg -y -v error -i "$V"/s4v4_jar.mp4    -t 3.6 -vf "scale=1280:720:flags=lanczos,$GRADE" $ENC -an "$V"/seg_jar.mp4
ffmpeg -y -v error -i "$V"/s4v4_dipper.mp4 -t 4.8 -vf "scale=1280:720:flags=lanczos,$GRADE" $ENC -an "$V"/seg_dipper.mp4
ffmpeg -y -v error -i "$V"/s4v4_bread.mp4  -t 3.6 -vf "scale=1280:720:flags=lanczos,$GRADE" $ENC -an "$V"/seg_bread.mp4

# 3) áudio: diegético (doadores H3) + tema Ace-Step mixado por baixo
ffmpeg -y -v error -i "$V"/aud_comb.mp4 -i "$V"/aud_jar.mp4 -i "$V"/aud_dipper.mp4 -i "$V"/aud_bread.mp4 -i "$V"/amber_theme.flac \
  -filter_complex "[0:a]atrim=0:4.2,asetpts=N/SR/TB[a0];[1:a]atrim=0:3.6,asetpts=N/SR/TB[a1];[2:a]atrim=0:4.8,asetpts=N/SR/TB[a2];[3:a]atrim=0:3.6,asetpts=N/SR/TB[a3];[a0][a1]acrossfade=d=0.3:c1=tri:c2=tri[ab];[ab][a2]acrossfade=d=0.3:c1=tri:c2=tri[ac];[ac][a3]acrossfade=d=0.3:c1=tri:c2=tri,apad=pad_dur=4.1,atrim=0:20[diag];[4:a]atrim=0:20,volume=0.55[theme];[diag][theme]amix=inputs=2:duration=first:normalize=0,afade=t=in:st=0:d=0.5,afade=t=out:st=18.4:d=1.5[aout]" \
  -map "[aout]" -c:a aac -b:a 192k "$V"/audio_track.m4a

# 4) concat + fades + mux
printf "file 'seg_comb.mp4'\nfile 'seg_jar.mp4'\nfile 'seg_dipper.mp4'\nfile 'seg_bread.mp4'\nfile 'seg_endcard.mp4'\n" > "$V"/list_v4.txt
ffmpeg -y -v error -f concat -safe 0 -i "$V"/list_v4.txt -i "$V"/audio_track.m4a \
  -vf "fade=t=in:st=0:d=0.5,fade=t=out:st=19.2:d=0.8" \
  -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -c:a copy -movflags +faststart -t 20 "$V"/ambar_commercial.mp4

ffprobe -v error -show_entries format=duration -of csv=p=0 "$V"/ambar_commercial.mp4
echo "OK: $V/ambar_commercial.mp4"
