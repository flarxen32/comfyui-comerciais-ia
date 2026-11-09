# Upscale final: RTX VSR e DLSS 5

← [Home](Home.md) · Anterior: [Consistência](consistencia-de-personagem.md) · Próximo: [Modelos alternativos](modelos-alternativos.md)

Regra unânime da pesquisa: **gererar em resolução baixa (0.4–0.6MP) e upscalar no final com tensor cores da NVIDIA** — não com upscaler de difusão dentro do workflow.

## Por que não upscaler interno

O vídeo de LTX 2.3 mediu: o upscaler embutido no workflow levou o pico de VRAM de 8GB para **~14GB** (rodou, mas lentamente). O caminho tensor-core custa 3–4GB e ~30s.

## RTX Video Super Resolution (nó "ComfyUI NVIDIA RTX Nodes")

- Quality **ultra**, multiplicador **2×** → 2K a partir de 960×544 (AmberNova).
- 3–4GB de VRAM, ~30 segundos (LTX 2.3).
- Sem flicker nem artefatos de AI; texturas/pele/arquitetura nítidas.
- **Pegadinha:** o FPS do vídeo de entrada tem que bater com o FPS do nó video combine, senão o tempo desincroniza (Tensor Alchemist).
- Workflows prontos: AmberNova (no JSON do Gumroad), Tensor Alchemist (https://drive.google.com/file/d/1iiCJtD4mTDUG9x0zWjdBjExAc5X-zsi4).
- No nó do RealRebelAI o método aparece como opção "RTX" junto de "model" e "Lanczos".

## DLSS 5 (nó ComfyUI-RH-DLSS5)

**Repo:** https://github.com/RH-RunningHub/ComfyUI-RH-DLSS5

- Mais rápido e confiável que upscaler de modelo; **corrige junto** highlights estourados e imagem lavada do H3 (CottonByte).
- Vai até 8K, mas **é progressivo**: não pule direto para 8K a partir de uma base fraca — 2K é o ponto estável, 4K aceitável (CG Pixel).
- Setup local: criar pasta de modelo DLSS5 com os 3 arquivos + DLLs (zip disponível no Drive do CG Pixel: https://drive.google.com/file/d/1i4234NhKVBMjiVeXVYjsh1z0cgqHmbnu/view).
- Tem socket de imagem e de vídeo (serve para upscaling de imagem única também).
- Combina com [Self-Lift](tecnicas-low-vram.md#8-self-lift-progressive-sampling-a-novidade-de-out2026): self-lift gera, DLSS 5 finaliza em 2K/4K.

## Interpolação de frames (menção)

Existe workflow de interpolação pós-geração (Tensor Alchemist: https://drive.google.com/file/d/1dhiZCk7P9ro4JnH9j0KKP8u2W9wn-1YQ), mas o veredito é que **remove o feel cinematográfico** — usar só em clips selecionados. FPS do H3 fica em 24; interpolar fora do workflow principal.

## Nó de comparação

`video compare slider` (AmberNova) para validar raw vs upscale lado a lado antes de exportar.
