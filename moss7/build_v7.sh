#!/usr/bin/env bash
# Montagem CANAVIAL v7 — kit de mídia: 16:9 + 9:16 + jingle, LUFS -14.
set -euo pipefail
cd "$(dirname "$0")"
V=video; S=stills; T=tts
GRADE="eq=contrast=1.05:saturation=1.07,unsharp=5:5:0.4,noise=alls=2.0:allf=t"
ENC="-c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -r 24"

# 1) end cards com zoom (h e v)
ffmpeg -y -v error -loop 1 -framerate 24 -t 4.0 -i "$S"/s7_endcard_h_up*_.png -vf "scale=2560:1440,zoompan=z='1+0.05*on/96':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=2560x1440:fps=24,scale=1920:1080:flags=lanczos,$GRADE,format=yuv420p" $ENC -an "$V"/seg_endcard_h.mp4
ffmpeg -y -v error -loop 1 -framerate 24 -t 4.0 -i "$S"/s7_endcard_v_up*_.png -vf "scale=1440:2560,zoompan=z='1+0.05*on/96':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1440x2560:fps=24,scale=1080:1920:flags=lanczos,$GRADE,format=yuv420p" $ENC -an "$V"/seg_endcard_v.mp4

# 2) segmentos 16:9 (1920x1080) e 9:16 (1080x1920)
seg() { ffmpeg -y -v error -i "$V"/s7v7_$2.mp4 -t $3 -vf "scale=$4:$5:flags=lanczos,$GRADE" $ENC -an "$V"/seg_$1.mp4; }
seg cane   cane   3.6 1920 1080; seg bottle bottle 3.8 1920 1080
seg pour   pour   4.6 1920 1080; seg glass  glass  4.0 1920 1080
seg cane_v   cane_v   3.6 1080 1920; seg bottle_v bottle_v 3.8 1080 1920
seg pour_v   pour_v   4.6 1080 1920; seg glass_v  glass_v  4.0 1080 1920

# 3) diegético (arco choro)
ffmpeg -y -v error -i "$V"/aud_cane.mp4 -i "$V"/aud_pour.mp4 -i "$V"/aud_bottle.mp4 -i "$V"/aud_glass.mp4 \
  -filter_complex "[0:a]atrim=0:3.6,asetpts=N/SR/TB[a0];[1:a]atrim=0:4.6,asetpts=N/SR/TB[a1];[2:a]atrim=0:3.8,asetpts=N/SR/TB[a2];[3:a]atrim=0:4.0,asetpts=N/SR/TB[a3];[a0][a1]acrossfade=d=0.3:c1=tri:c2=tri[ab];[ab][a2]acrossfade=d=0.3:c1=tri:c2=tri[ac];[ac][a3]acrossfade=d=0.3:c1=tri:c2=tri,apad=pad_dur=4.0,atrim=0:20[diag]" \
  -map "[diag]" "$V"/diag.m4a

# 4) trilha A (choro + VO) e trilha B (jingle), ambas com loudnorm -14 LUFS
ffmpeg -y -v error -i "$V"/diag.m4a -i "$V"/canavial_theme.flac -i "$T"/vo_line1.wav -i "$T"/vo_line2.wav \
  -filter_complex "[1:a]atrim=0:20,volume=0.42[th];[2:a]adelay=7400|7400,volume=1.8[v1];[3:a]adelay=16400|16400,volume=1.8[v2];[0:a][th][v1][v2]amix=inputs=4:duration=first:normalize=0,afade=t=in:st=0:d=0.5,afade=t=out:st=18.4:d=1.5,loudnorm=I=-14:TP=-1.5:LRA=11[aout]" \
  -map "[aout]" -c:a aac -b:a 192k "$V"/audio_theme.m4a
ffmpeg -y -v error -i "$V"/diag.m4a -i "$V"/canavial_jingle.flac \
  -filter_complex "[1:a]atrim=0:20,volume=0.95[j];[0:a]volume=0.35[d];[d][j]amix=inputs=2:duration=first:normalize=0,afade=t=in:st=0:d=0.4,afade=t=out:st=18.5:d=1.4,loudnorm=I=-14:TP=-1.5:LRA=11[aout]" \
  -map "[aout]" -c:a aac -b:a 192k "$V"/audio_jingle.m4a

# 5) concat + fades + mux (h-tema, v-tema, h-jingle)
printf "file 'seg_cane.mp4'\nfile 'seg_pour.mp4'\nfile 'seg_bottle.mp4'\nfile 'seg_glass.mp4'\nfile 'seg_endcard_h.mp4'\n" > "$V"/list_h.txt
printf "file 'seg_cane_v.mp4'\nfile 'seg_pour_v.mp4'\nfile 'seg_bottle_v.mp4'\nfile 'seg_glass_v.mp4'\nfile 'seg_endcard_v.mp4'\n" > "$V"/list_v.txt
ffmpeg -y -v error -f concat -safe 0 -i "$V"/list_h.txt -i "$V"/audio_theme.m4a -vf "fade=t=in:st=0:d=0.5,fade=t=out:st=19.2:d=0.8" -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -c:a copy -movflags +faststart -t 20 "$V"/canavial_h.mp4
ffmpeg -y -v error -f concat -safe 0 -i "$V"/list_v.txt -i "$V"/audio_theme.m4a -vf "fade=t=in:st=0:d=0.5,fade=t=out:st=19.2:d=0.8" -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -c:a copy -movflags +faststart -t 20 "$V"/canavial_v.mp4
ffmpeg -y -v error -f concat -safe 0 -i "$V"/list_h.txt -i "$V"/audio_jingle.m4a -vf "fade=t=in:st=0:d=0.5,fade=t=out:st=19.2:d=0.8" -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -c:a copy -movflags +faststart -t 20 "$V"/canavial_h_jingle.mp4
for f in "$V"/canavial_h.mp4 "$V"/canavial_v.mp4; do ffprobe -v error -show_entries format=duration -of csv=p=0 "$f"; done
echo "OK: kit v7 em $V/"
