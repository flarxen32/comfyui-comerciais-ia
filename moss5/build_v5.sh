#!/usr/bin/env bash
# Montagem do comercial AMARGO v5 — 20,0s @ 1920x1080 (1080p nativo), 48fps via RIFE.
# Duas trilhas: master instrumental (tema Ace + diegético) e master jingle (cantado PT).
set -euo pipefail
cd "$(dirname "$0")"
V=video; S=stills
GRADE="eq=contrast=1.05:saturation=1.06,unsharp=5:5:0.4,noise=alls=2.0:allf=t"
ENC="-c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -r 24"

# 1) end card zoom 3,8 s (fonte 2560x1440 UltraSharp) → 1920x1080
ffmpeg -y -v error -loop 1 -framerate 24 -t 3.8 -i "$S"/s5_endcard_up*_.png -vf "scale=2560:1440,zoompan=z='1+0.05*on/91':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=2560x1440:fps=24,scale=1920:1080:flags=lanczos,$GRADE,format=yuv420p" $ENC -an "$V"/seg_endcard.mp4

# 2) segmentos 1080p (fontes 1920x1088 → crop/scale 1920x1080)
ffmpeg -y -v error -i "$V"/s5v5_beans.mp4   -t 4.0 -vf "scale=1920:1080:flags=lanczos,$GRADE" $ENC -an "$V"/seg_beans.mp4
ffmpeg -y -v error -i "$V"/s5v5_bar.mp4     -t 4.2 -vf "scale=1920:1080:flags=lanczos,$GRADE" $ENC -an "$V"/seg_bar.mp4
ffmpeg -y -v error -i "$V"/s5v5_pour.mp4    -t 4.6 -vf "scale=1920:1080:flags=lanczos,$GRADE" $ENC -an "$V"/seg_pour.mp4
ffmpeg -y -v error -i "$V"/s5v5_truffle.mp4 -t 3.4 -vf "scale=1920:1080:flags=lanczos,$GRADE" $ENC -an "$V"/seg_truffle.mp4

# 3) faixa diegética (doadores H3, arco samba+cello)
ffmpeg -y -v error -i "$V"/aud_beans.mp4 -i "$V"/aud_bar.mp4 -i "$V"/aud_pour.mp4 -i "$V"/aud_truffle.mp4 \
  -filter_complex "[0:a]atrim=0:4.0,asetpts=N/SR/TB[a0];[1:a]atrim=0:4.2,asetpts=N/SR/TB[a1];[2:a]atrim=0:4.6,asetpts=N/SR/TB[a2];[3:a]atrim=0:3.4,asetpts=N/SR/TB[a3];[a0][a1]acrossfade=d=0.3:c1=tri:c2=tri[ab];[ab][a2]acrossfade=d=0.3:c1=tri:c2=tri[ac];[ac][a3]acrossfade=d=0.3:c1=tri:c2=tri,apad=pad_dur=4.0,atrim=0:20[diag]" \
  -map "[diag]" "$V"/diag.m4a

# 4) master A — instrumental: diag + tema Ace a 0.5
ffmpeg -y -v error -i "$V"/diag.m4a -i "$V"/amargo_theme.flac -filter_complex "[1:a]atrim=0:20,volume=0.5[t];[0:a][t]amix=inputs=2:duration=first:normalize=0,afade=t=in:st=0:d=0.5,afade=t=out:st=18.4:d=1.5[aout]" -map "[aout]" -c:a aac -b:a 192k "$V"/audio_theme.m4a
# 5) master B — jingle: diag 0.35 + jingle 0.95
ffmpeg -y -v error -i "$V"/diag.m4a -i "$V"/amargo_jingle.flac -filter_complex "[1:a]atrim=0:20,volume=0.95[t];[0:a]volume=0.35[d];[d][t]amix=inputs=2:duration=first:normalize=0,afade=t=in:st=0:d=0.4,afade=t=out:st=18.5:d=1.4[aout]" -map "[aout]" -c:a aac -b:a 192k "$V"/audio_jingle.m4a

# 6) concat vídeo + fades + mux (dois masters)
printf "file 'seg_beans.mp4'\nfile 'seg_bar.mp4'\nfile 'seg_pour.mp4'\nfile 'seg_truffle.mp4'\nfile 'seg_endcard.mp4'\n" > "$V"/list_v5.txt
for M in theme jingle; do
  ffmpeg -y -v error -f concat -safe 0 -i "$V"/list_v5.txt -i "$V"/audio_$M.m4a \
    -vf "fade=t=in:st=0:d=0.5,fade=t=out:st=19.2:d=0.8" \
    -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -c:a copy -movflags +faststart -t 20 "$V"/amargo_commercial_$M.mp4
done
ffprobe -v error -show_entries format=duration -of csv=p=0 "$V"/amargo_commercial_theme.mp4
echo "OK: masters 1080p em $V/"
