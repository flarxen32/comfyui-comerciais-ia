#!/usr/bin/env bash
# Montagem do comercial RAIZ v6 — 20,0s @ 1920x1080, 48fps via RIFE.
# Master A: bossa + diegético + LOCUÇÃO PT-BR (Piper). Master B: jingle v1 + diegético.
set -euo pipefail
cd "$(dirname "$0")"
V=video; S=stills; T=tts
GRADE="eq=contrast=1.05:saturation=1.05,unsharp=5:5:0.4,noise=alls=2.0:allf=t"
ENC="-c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -r 24"

# 1) end card zoom 4,0 s
ffmpeg -y -v error -loop 1 -framerate 24 -t 4.0 -i "$S"/s6_endcard_up*_.png -vf "scale=2560:1440,zoompan=z='1+0.05*on/96':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=2560x1440:fps=24,scale=1920:1080:flags=lanczos,$GRADE,format=yuv420p" $ENC -an "$V"/seg_endcard.mp4

# 2) segmentos 1080p
ffmpeg -y -v error -i "$V"/s6v6_grapes.mp4 -t 3.4 -vf "scale=1920:1080:flags=lanczos,$GRADE" $ENC -an "$V"/seg_grapes.mp4
ffmpeg -y -v error -i "$V"/s6v6_cellar.mp4 -t 3.6 -vf "scale=1920:1080:flags=lanczos,$GRADE" $ENC -an "$V"/seg_cellar.mp4
ffmpeg -y -v error -i "$V"/s6v6_pour.mp4   -t 4.6 -vf "scale=1920:1080:flags=lanczos,$GRADE" $ENC -an "$V"/seg_pour.mp4
ffmpeg -y -v error -i "$V"/s6v6_swirl.mp4  -t 4.4 -vf "scale=1920:1080:flags=lanczos,$GRADE" $ENC -an "$V"/seg_swirl.mp4

# 3) diegético (arco bossa)
ffmpeg -y -v error -i "$V"/aud_grapes.mp4 -i "$V"/aud_cellar.mp4 -i "$V"/aud_pour.mp4 -i "$V"/aud_swirl.mp4 \
  -filter_complex "[0:a]atrim=0:3.4,asetpts=N/SR/TB[a0];[1:a]atrim=0:3.6,asetpts=N/SR/TB[a1];[2:a]atrim=0:4.6,asetpts=N/SR/TB[a2];[3:a]atrim=0:4.4,asetpts=N/SR/TB[a3];[a0][a1]acrossfade=d=0.3:c1=tri:c2=tri[ab];[ab][a2]acrossfade=d=0.3:c1=tri:c2=tri[ac];[ac][a3]acrossfade=d=0.3:c1=tri:c2=tri,apad=pad_dur=4.0,atrim=0:20[diag]" \
  -map "[diag]" "$V"/diag.m4a

# 4) Master A — bossa + locução Piper (falas posicionadas)
ffmpeg -y -v error -i "$V"/diag.m4a -i "$V"/raiz_theme.flac -i "$T"/vo_line1.wav -i "$T"/vo_line2.wav \
  -filter_complex "[1:a]atrim=0:20,volume=0.45[theme];[2:a]adelay=7200|7200,volume=1.9[vo1];[3:a]adelay=16600|16600,volume=1.9[vo2];[0:a][theme][vo1][vo2]amix=inputs=4:duration=first:normalize=0,afade=t=in:st=0:d=0.5,afade=t=out:st=18.4:d=1.5[aout]" \
  -map "[aout]" -c:a aac -b:a 192k "$V"/audio_theme.m4a

# 5) Master B — jingle v1 + diegético
ffmpeg -y -v error -i "$V"/diag.m4a -i "$V"/raiz_jingle_v1.flac \
  -filter_complex "[1:a]atrim=0:20,volume=0.95[j];[0:a]volume=0.35[d];[d][j]amix=inputs=2:duration=first:normalize=0,afade=t=in:st=0:d=0.4,afade=t=out:st=18.5:d=1.4[aout]" \
  -map "[aout]" -c:a aac -b:a 192k "$V"/audio_jingle.m4a

# 6) concat + fades + mux
printf "file 'seg_grapes.mp4'\nfile 'seg_cellar.mp4'\nfile 'seg_pour.mp4'\nfile 'seg_swirl.mp4'\nfile 'seg_endcard.mp4'\n" > "$V"/list_v6.txt
for M in theme jingle; do
  ffmpeg -y -v error -f concat -safe 0 -i "$V"/list_v6.txt -i "$V"/audio_$M.m4a \
    -vf "fade=t=in:st=0:d=0.5,fade=t=out:st=19.2:d=0.8" \
    -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -c:a copy -movflags +faststart -t 20 "$V"/raiz_commercial_$M.mp4
done
ffprobe -v error -show_entries format=duration -of csv=p=0 "$V"/raiz_commercial_theme.mp4
echo "OK: masters RAIZ em $V/"
