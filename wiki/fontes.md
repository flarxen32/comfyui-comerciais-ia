# Fontes e metodologia

← [Home](Home.md) · Anterior: [Receita MOSS](pipeline-moss.md)

Pesquisa realizada em **2026-10-28** a partir de: `https://www.youtube.com/results?search_query=video+infiniti+low+vram+comfyui` (20 resultados). 12 vídeos dissecados com transcrição completa; descrições com links de workflows coletadas.

## Vídeos principais (com transcrição analisada)

| # | Vídeo | Canal | Stats | Link |
|---|---|---|---|---|
| 1 | MiniMax H3 Can Make Infinite Length Videos Now (Low VRAM) | LoRAtech – ComfyUI Hub | 118k · 19:39 · 1mês | https://youtu.be/6oz0ms9GRY8 |
| 2 | Make Long AI Videos on a Low-VRAM GPU (ComfyUI Workflow) | AmberNova Studio | 27k · 5:43 · 12d | https://youtu.be/iprgDi1Eq98 |
| 3 | MiniMax H3 40-Second Video on 6GB VRAM | CG Pixel | 27k · 10:01 · 1mês | https://youtu.be/85XQ_xcWX7U |
| 4 | MiniMax H3's Secret Sauce: Faster 4K, Less VRAM | CottonByte AI | 22k · 7:27 · 12d | https://youtu.be/t02ttse7Qhw |
| 5 | MiniMax H3 ComfyUI Workflow (8GB, High Quality) | Skill Destiny | 27k · 9:52 · 2m | https://youtu.be/VNi9QTSHxEU |
| 6 | MiniMax H3 FP8 & INT8 on 8GB VRAM | Tensor Alchemist | 35k · 10:29 · 2m | https://youtu.be/jZsBMdjV4z0 |
| 7 | Generate 4K AI Videos on a 6GB GPU? (SelfLift + DLSS5) | CG Pixel | 20k · 9:04 · 3d | https://youtu.be/sJbhZjAzkE0 |
| 8 | ComfyUI LongCat: Very Long Video (Low VRAM) | ComfyUI Workflow Blog | 24k · 8:35 · 11m | https://youtu.be/peoQXfY-KU0 |
| 9 | WAN 2.2 Low VRAM: High+Low Noise in One File (6GB) | ComfyUI Workflow Blog | 53k · 14:45 · 1a | https://youtu.be/rBAI32tl_hI |
| 10 | ComfyUI LTX 2.3 v1.1: The 8GB Workflow (OOM Fix) | ComfyUI Workflow Blog | 23k · 9:10 · 5m | https://youtu.be/CIpY4nt-F1E |
| 11 | Fast LTX 2 I2V Low VRAM (áudio, 8GB) | Bored Coder | 33k · 2:32 · 9m | https://youtu.be/ub-1pBrAd9U |
| 12 | MiniMax H3 Video Inpainting on 8GB (SAM 3.1) | Tensor Alchemist | 8.8k · 10:29 · 2m | https://youtu.be/58ydJUg5aR8 |

Transcrições secundárias baixadas (não dissectadas a fundo): LTX GGUF audio fix (https://youtu.be/r7TACD329wY) e Wan SCAIL2 (https://youtu.be/51ay-rW8sMI).

## Demais resultados da busca (menos relevantes p/ vídeo infinito)

- 2000% Faster AI Video Upscaling Maximizing VRAM — AI Artistry Atelier — https://youtu.be/U3tx8_QPZLs
- Upscale video in ComfyUI even with low VRAM! — AIFuzz — https://youtu.be/zK7Dt0qt23k
- Free Local AI Video Upscaler (SeedVR2) — The Local Lab — https://youtu.be/N59GNAck0xE
- Qwen Image 2.1 Edit (GGUF+Turbo) — The Local Lab — https://youtu.be/3WRAd6LdVCU
- Qwen Image 2512 GGUF CPU/Low VRAM — Code Crafters Corner — https://youtu.be/TOoVyvwUiTU

## Links diretos de workflows / nós / modelos (H3)

**Nós:**
- RealRebelAI LongVideos OPTIMIZED: https://github.com/RealRebelAI/MiniMax-H3-LongVideos_OPTIMIZED
- Yusu MiniMax H3 Unified (self-lift): https://github.com/yusu-02/ComfyUI-Yusu-MiniMaxH3-Unified
- DLSS 5: https://github.com/RH-RunningHub/ComfyUI-RH-DLSS5
- RTX Nodes (Video Super Resolution): "ComfyUI NVIDIA RTX Nodes" (Manager)

**Workflows:**
- AmberNova (40s+2K, 6GB): https://ambernovastudio.gumroad.com/l/afdlbt
- CG Pixel 40s (grátis): https://drive.google.com/file/d/15FYXmjzvUv_NZRS2YqlZfWnVy_Oqc1Ue/view · artigo: https://civitai.com/articles/35705
- CG Pixel 4K self-lift+DLSS5: https://drive.google.com/file/d/19cFLGTvPOMIk0eA_1xIsTlaUQwgsQvdz/view · DLLs DLSS5: https://drive.google.com/file/d/1i4234NhKVBMjiVeXVYjsh1z0cgqHmbnu/view · artigo: https://civitai.com/articles/37374
- CottonByte Secret Sauce (RunningHub): https://www.runninghub.ai/post/2110371664328900610
- Skill Destiny 8GB: https://drive.google.com/file/d/1djlB1FMEqhBqiZFBsrqXQ-jJvE5yAXJ2
- Tensor Alchemist T2V: https://drive.google.com/file/d/1KuanMQpappwz5Zmu62hAH179PisfR1Oz · Interpolação: https://drive.google.com/file/d/1dhiZCk7P9ro4JnH9j0KKP8u2W9wn-1YQ · RTX SR: https://drive.google.com/file/d/1iiCJtD4mTDUG9x0zWjdBjExAc5X-zsi4
- Tensor Alchemist inpainting: https://drive.google.com/file/d/1OcTGpraPvqtUn_qpgig8N0QU9s7866Kh
- LoRAtech Motion Director: workflow grátis no Discord https://discord.gg/2bqQXKxsxg
- LongCat: https://aistudynow.com/comfyui-longcat-workflow-make-very-long-video-on-low-vram/

**Modelos H3:**
- Oficiais: https://huggingface.co/Comfy-Org/MiniMax-H3
- Fused INT8 turbo (AmberNova): `minimax_h3_fused_refdelta_r1024_turbo8_mystic07_int8_convrot`
- Encoder INT4: https://huggingface.co/Abiray/MiniMax-H3-GGUF/blob/main/text_encoders/qwen3vl_32b_minimax_h3_int4_convrot.safetensors
- SAM 3.1 (inpainting): https://huggingface.co/Comfy-Org/sam3.1

## Metodologia (como extraímos as transcrições)

- Painel de transcrição do YouTube e endpoint `timedtext` via navegador: **bloqueados** (corpo vazio — proteção anti-bot; painel fica em spinner eterno).
- **yt-dlp funcionou** com:
  ```
  yt-dlp --extractor-args "youtube:player_client=tv,web_embedded,web_safari" --js-runtimes node \
    --skip-download --write-auto-subs --sub-langs "en-orig" --sub-format vtt --sleep-requests 3 -o "<id>" \
    "https://www.youtube.com/watch?v=<id>"
  ```
- Sem cookies (Brave/Edge travam o banco de cookies com o navegador aberto; Chrome não instalado). Legendas `en` traduzidas davam 429; **`en-orig` (idioma original) baixa limpo**.
- VTTs limpos com script Node (dedupe de linhas rolantes + strip de tags inline).
- Transcrições brutas preservadas em `%TEMP%\ytt\*.txt` (14 arquivos; pasta temporária — copiar se quiser arquivar).
