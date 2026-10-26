#!/usr/bin/env bash
# Montagem MATTA v8 — kit 16:9 + 9:16 + jingle, LUFS -14, VO única (line2, verificada por whisper).
set -euo pipefail
cd "$(dirname "$0")"
V=video; S=stills; T=tts
GRADE="eq=contrast=1.05:saturation=1.06,unsharp=5:5:0.4,noise=alls=2.0:allf=t"
ENC="-c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -r 24"

# 1) end cards com zoom
ffmpeg -y -v error -loop 1 -framerate 24 -t 4.0 -i "$S"/s8_endcard_h_up*_.png -vf "scale=2560:1440,zoompan=z='1+0.05*on/96':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=2560x1440:fps=24,scale=1920:1080:flags=lanczos,$GRADE,format=yuv420p" $ENC -an "$V"/seg_endcard_h.mp4
ffmpeg -y -v error -loop 1 -framerate 24 -t 4.0 -i "$S"/s8_endcard_v_up*_.png -vf "scale=1440:2560,zoompan=z='1+0.05*on/96':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1440x2560:fps=24,scale=1080:1920:flags=lanczos,$GRADE,format=yuv420p" $ENC -an "$V"/seg_endcard_v.mp4

# 2) segmentos 16:9 e 9:16
seg() { ffmpeg -y -v error -i "$V"/s8v8_$2.mp4 -t $3 -vf "scale=$4:$5:flags=lanczos,$GRADE" $ENC -an "$V"/seg_$1.mp4; }
seg berries berries 3.4 1920 1080; seg pour pour 4.6 1920 1080
seg bowl   bowl   3.8 1920 1080; seg spoon spoon 4.2 1920 1080
seg berries_v berries_v 3.4 1080 1920; seg pour_v pour_v 4.6 1080 1920
seg bowl_v   bowl_v   3.8 1080 1920; seg spoon_v spoon_v 4.2 1080 1920

# 3) diegético (arco afro-samba)
ffmpeg -y -v error -i "$V"/aud_berries.mp4 -i "$V"/aud_pour.mp4 -i "$V"/aud_bowl.mp4 -i "$V"/aud_spoon.mp4 \
  -filter_complex "[0:a]atrim=0:3.4,asetpts=N/SR/TB[a0];[1:a]atrim=0:4.6,asetpts=N/SR/TB[a1];[2:a]atrim=0:3.8,asetpts=N/SR/TB[a2];[3:a]atrim=0:4.2,asetpts=N/SR/TB[a3];[a0][a1]acrossfade=d=0.3:c1=tri:c2=tri[ab];[ab][a2]acrossfade=d=0.3:c1=tri:c2=tri[ac];[ac][a3]acrossfade=d=0.3:c1=tri:c2=tri,apad=pad_dur=4.0,atrim=0:20[diag]" \
  -map "[diag]" "$V"/diag.m4a

# 4) trilha A (afro-samba + VO única) e trilha B (jingle), LUFS -14
ffmpeg -y -v error -i "$V"/diag.m4a -i "$V"/matta_theme.flac -i "$T"/vo_line2.wav \
  -filter_complex "[1:a]atrim=0:20,volume=0.42[th];[2:a]adelay=16200|16200,volume=1.8[vo];[0:a][th][vo]amix=inputs=3:duration=first:normalize=0,afade=t=in:st=0:d=0.5,afade=t=out:st=18.4:d=1.5,loudnorm=I=-14:TP=-1.5:LRA=11[aout]" \
  -map "[aout]" -c:a aac -b:a 192k "$V"/audio_theme.m4a
ffmpeg -y -v error -i "$V"/diag.m4a -i "$V"/matta_jingle.flac \
  -filter_complex "[1:a]atrim=0:20,volume=0.95[j];[0:a]volume=0.35[d];[d][j]amix=inputs=2:duration=first:normalize=0,afade=t=in:st=0:d=0.4,afade=t=out:st=18.5:d=1.4,loudnorm=I=-14:TP=-1.5:LRA=11[aout]" \
  -map "[aout]" -c:a aac -b:a 192k "$V"/audio_jingle.m4a

# 5) concat + fades + mux
printf "file 'seg_berries.mp4'\nfile 'seg_pour.mp4'\nfile 'seg_bowl.mp4'\nfile 'seg_spoon.mp4'\nfile 'seg_endcard_h.mp4'\n" > "$V"/list_h.txt
printf "file 'seg_berries_v.mp4'\nfile 'seg_pour_v.mp4'\nfile 'seg_bowl_v.mp4'\nfile 'seg_spoon_v.mp4'\nfile 'seg_endcard_v.mp4'\n" > "$V"/list_v.txt
ffmpeg -y -v error -f concat -safe 0 -i "$V"/list_h.txt -i "$V"/audio_theme.m4a -vf "fade=t=in:st=0:d=0.5,fade=t=out:st=19.2:d=0.8" -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -c:a copy -movflags +faststart -t 20 "$V"/matta_h.mp4
ffmpeg -y -v error -f concat -safe 0 -i "$V"/list_v.txt -i "$V"/audio_theme.m4a -vf "fade=t=in:st=0:d=0.5,fade=t=out:st=19.2:d=0.8" -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -c:a copy -movflags +faststart -t 20 "$V"/matta_v.mp4
ffmpeg -y -v error -f concat -safe 0 -i "$V"/list_h.txt -i "$V"/audio_jingle.m4a -vf "fade=t=in:st=0:d=0.5,fade=t=out:st=19.2:d=0.8" -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -c:a copy -movflags +faststart -t 20 "$V"/matta_h_jingle.mp4
echo "OK: kit v8 em $V/"
