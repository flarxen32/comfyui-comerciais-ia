#!/usr/bin/env bash
# Montagem do comercial SERRA v2 — 20,0s @ 1280x720, cortes limpos, grade quente.
# Hero (pour) = Wan 704p; cherry/beans/cup = H3@8st 480p upscaled; end card = MOSS+UltraSharp zoom.
set -euo pipefail
cd "$(dirname "$0")"
V=video; S=stills
GRADE="eq=contrast=1.04:saturation=1.07,unsharp=5:5:0.4,noise=alls=2.5:allf=t"
ENC="-c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -r 24"

# 1) end card: zoom lento 4 s a partir do 1440p upscalado (crisp), sai 1280x720
ffmpeg -y -v error -loop 1 -framerate 24 -t 4 -i "$S"/s2_endcard_up*_.png -vf "scale=2560:1440,zoompan=z='1+0.06*on/96':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=2560x1440:fps=24,scale=1280:720:flags=lanczos,$GRADE,format=yuv420p" $ENC -an "$V"/seg_endcard.mp4

# 2) segmentos de vídeo normalizados (1280x720, grade)
ffmpeg -y -v error -i "$V"/s2v2_h3_cherry.mp4 -t 4.1 -vf "scale=1280:720:flags=lanczos,$GRADE" $ENC -an "$V"/seg_cherry.mp4
ffmpeg -y -v error -i "$V"/s2v2_h3_beans.mp4  -t 4.1 -vf "scale=1280:720:flags=lanczos,$GRADE" $ENC -an "$V"/seg_beans.mp4
ffmpeg -y -v error -i "$V"/ab_wan20.mp4      -t 4.6 -vf "scale=1280:720:flags=lanczos,$GRADE" $ENC -an "$V"/seg_pour.mp4
ffmpeg -y -v error -i "$V"/s2v2_h3_cup.mp4   -t 3.2 -vf "scale=1280:720:flags=lanczos,$GRADE" $ENC -an "$V"/seg_cup.mp4

# 3) faixa de áudio: doadores H3 (pour doa trilha pro take Wan), cortes com micro-crossfade
ffmpeg -y -v error -i "$V"/s2v2_h3_cherry.mp4 -i "$V"/s2v2_h3_beans.mp4 -i "$V"/ab_h3_8st.mp4 -i "$V"/s2v2_h3_cup.mp4 -i "$V"/seg_endcard.mp4 \
  -filter_complex "[0:a]atrim=0:4.1,asetpts=N/SR/TB[a0];[1:a]atrim=0:4.1,asetpts=N/SR/TB[a1];[2:a]atrim=0:4.6,asetpts=N/SR/TB[a2];[3:a]atrim=0:3.2,asetpts=N/SR/TB[a3];[a0][a1]acrossfade=d=0.35:c1=tri:c2=tri[ab];[ab][a2]acrossfade=d=0.35:c1=tri:c2=tri[ac];[ac][a3]acrossfade=d=0.35:c1=tri:c2=tri[ad];[ad]apad=pad_dur=4.2,atrim=0:20,afade=t=in:st=0:d=0.4,afade=t=out:st=18.6:d=1.3[aout]" \
  -map "[aout]" -c:a aac -b:a 192k "$V"/audio_track.m4a

# 4) concat vídeo + fades + mux
printf "file 'seg_cherry.mp4'\nfile 'seg_beans.mp4'\nfile 'seg_pour.mp4'\nfile 'seg_cup.mp4'\nfile 'seg_endcard.mp4'\n" > "$V"/list_v2.txt
ffmpeg -y -v error -f concat -safe 0 -i "$V"/list_v2.txt -i "$V"/audio_track.m4a \
  -vf "fade=t=in:st=0:d=0.5,fade=t=out:st=19.2:d=0.8" \
  -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -c:a copy -movflags +faststart -t 20 "$V"/serra_commercial.mp4

ffprobe -v error -show_entries format=duration,size -of default=noprint_wrappers=1 "$V"/serra_commercial.mp4
echo "OK: $V/serra_commercial.mp4"
