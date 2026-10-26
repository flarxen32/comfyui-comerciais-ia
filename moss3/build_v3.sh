#!/usr/bin/env bash
# Montagem do comercial GAROA v3 — 20,0s @ 1280x720 (24fps master; 48fps via RIFE depois).
# hero (pour) = Wan fp16 20st 704p; hops/bottle/glass = H3@8st; end card = MOSS + UltraSharp zoom.
set -euo pipefail
cd "$(dirname "$0")"
V=video; S=stills
GRADE="eq=contrast=1.05:saturation=1.06,unsharp=5:5:0.4,noise=alls=2.2:allf=t"
ENC="-c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -r 24"

# 1) end card zoom 3,8 s a partir do 1440p UltraSharp
ffmpeg -y -v error -loop 1 -framerate 24 -t 3.8 -i "$S"/s3_endcard_up*_.png -vf "scale=2560:1440,zoompan=z='1+0.05*on/91':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=2560x1440:fps=24,scale=1280:720:flags=lanczos,$GRADE,format=yuv420p" $ENC -an "$V"/seg_endcard.mp4

# 2) segmentos 1280x720 com grade
ffmpeg -y -v error -i "$V"/s3v3_hops.mp4   -t 4.4 -vf "scale=1280:720:flags=lanczos,$GRADE" $ENC -an "$V"/seg_hops.mp4
ffmpeg -y -v error -i "$V"/s3v3_bottle.mp4 -t 3.8 -vf "scale=1280:720:flags=lanczos,$GRADE" $ENC -an "$V"/seg_bottle.mp4
ffmpeg -y -v error -i "$V"/s3v3_pour.mp4   -t 4.6 -vf "scale=1280:720:flags=lanczos,$GRADE" $ENC -an "$V"/seg_pour.mp4
ffmpeg -y -v error -i "$V"/s3v3_glass.mp4  -t 3.4 -vf "scale=1280:720:flags=lanczos,$GRADE" $ENC -an "$V"/seg_glass.mp4

# 3) áudio: doadores H3 (mesma duração dos segmentos, micro-crossfade, fades)
ffmpeg -y -v error -i "$V"/aud_h3_hops.mp4 -i "$V"/aud_h3_bottle.mp4 -i "$V"/aud_h3_pour.mp4 -i "$V"/aud_h3_glass.mp4 -i "$V"/seg_endcard.mp4 \
  -filter_complex "[0:a]atrim=0:4.4,asetpts=N/SR/TB[a0];[1:a]atrim=0:3.8,asetpts=N/SR/TB[a1];[2:a]atrim=0:4.6,asetpts=N/SR/TB[a2];[3:a]atrim=0:3.4,asetpts=N/SR/TB[a3];[a0][a1]acrossfade=d=0.3:c1=tri:c2=tri[ab];[ab][a2]acrossfade=d=0.3:c1=tri:c2=tri[ac];[ac][a3]acrossfade=d=0.3:c1=tri:c2=tri[ad];[ad]apad=pad_dur=4.1,atrim=0:20,afade=t=in:st=0:d=0.4,afade=t=out:st=18.6:d=1.3[aout]" \
  -map "[aout]" -c:a aac -b:a 192k "$V"/audio_track.m4a

# 4) concat + fades + mux
printf "file 'seg_hops.mp4'\nfile 'seg_bottle.mp4'\nfile 'seg_pour.mp4'\nfile 'seg_glass.mp4'\nfile 'seg_endcard.mp4'\n" > "$V"/list_v3.txt
ffmpeg -y -v error -f concat -safe 0 -i "$V"/list_v3.txt -i "$V"/audio_track.m4a \
  -vf "fade=t=in:st=0:d=0.5,fade=t=out:st=19.2:d=0.8" \
  -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -c:a copy -movflags +faststart -t 20 "$V"/garoa_commercial.mp4

ffprobe -v error -show_entries format=duration -of csv=p=0 "$V"/garoa_commercial.mp4
echo "OK: $V/garoa_commercial.mp4"
