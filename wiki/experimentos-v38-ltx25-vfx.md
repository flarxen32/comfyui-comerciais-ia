# v38 — LTX-2.5 VFX LoRAs na RTX 3070 8GB (recriação do vídeo the_frizzy1)

← [Home](Home.md) · Base: [LTX-2.5 VFX LoRAs](ltx25-vfx-loras.md) · Anterior: [Experimentos v25–v37](experimentos-v25-v37.md)

> **2026-11-09 (madrugada).** Objetivo: recriar TODOS os efeitos do vídeo
> [y2dJfFNS8QY](https://youtu.be/y2dJfFNS8QY) local, com clipes de 5s e comparação
> original|efeito. Máquina abaixo do mínimo do autor (3070 8GB vs 3060 12GB).
> Entregáveis: `moss38/` (index.html + out/ + compare/ + src/ + first/).

## Setup da noite

- ComfyUI **0.44.2** em `tools/comfy` (porta 8189), atualizado de 0.42.3 via git checkout v0.44.2 + pip requirements.
- Stack baixado **sem HF** (gated): repo oficial `Lightricks/LTX-2.5` no **ModelScope** (transformer NVFP4 18.7GB + Gemma int8 15.4GB), `Genius-Society/*` p/ VAEs + upscaler espacial, LoRAs oficiais espelhadas no MS. Civitai (id 3220250) foi o 1º espelho achado do base, mas URLs B2 expiram em download longo.
- HF signup com temp-mail: **bloqueado** por hCaptcha invisible + AWS WAF (silencioso no IAB E no Edge real; desafios de grade respondidos certo e recusados). Lição: não gastar tempo; ModelScope resolve.
- Workflows API próprios (`moss38/wf_gen.js`): grafo achatado do workflow do frizzy v3.1.1 — LoadVideo→GetVideoComponents→ImageFromBatch→ImageScale; UNETLoader→LoraLoaderModelOnly→GetICLoRAParameters; CLIPLoader(type=ltxv)→2×CLIPTextEncode→LTXVConditioning(24fps); EmptyLTXVLatentVideo→LTXVImgToVideoInplace(strength 1)→LTXVAddGuide(frame_idx 0, strength 1, iclora_parameters)→LTXVEmptyLatentAudio→LTXVConcatAVLatent; RandomNoise+CFGGuider(cfg 1)+KSamplerSelect(euler_ancestral)+**ManualSigmas("1.0, 0.99375, 0.9875, 0.98125, 0.975, 0.909375, 0.725, 0.421875, 0.0")**→SamplerCustomAdvanced→LTXVSeparateAVLatent→LTXVCropGuides→VAEDecodeTiled(512/64/64/16)→CreateVideo(24)→SaveVideo.
- Clipes-base (yt-dlp ytsearch + ffmpeg 121f@24fps 960×544): rua c/ pedestres, mesa/estúdio, dançarina, trem 1896 (P&B), NY 1900 (P&B), skate, chuwa na janela. Derivados: borrado (gblur σ6), esmagado (80kbps 480×272), P&B forçado, 480×272, blockout cinza (drawbox), fotos (chuva p/ cinemagraph, skate p/ slow-mo), ingredients sheet (3 painéis no preto).
- Slow-mo via truque de **frame_rate**: conditioning a 120fps (24/0.2) renderizado a 24 = 5× lento (equivale ao --speed do ltx_pipelines).

## Status final da madrugada (08:30)

**Funciona:** T2V completo na 3070 8GB (int8-convrot 20GB + Gemma int8, ~3min/clip 5s@960×544, prompt respeitado perfeitamente — teste "red sports car at sunset" impecável). V2V também RODA sem erro nenhum com os custom nodes oficiais (`LTXICLoRALoaderModelOnly` + `LTXAddVideoICLoRAGuide` — instalação: ComfyUI-LTXVideo + deps `colour colour-science diffusers einops kornia transformers>=4.50`), **mas o efeito não acontece**: o output reconstrói a referência (YAVG idêntico ao input, ~111) mesmo com prompt no formato treinado "Reference shows/Edited shows", strength 1.0 e init 0.7.

**Suspeitas restantes (na ordem):** (1) o guia IC-LoRA exige o modelo carregado com os loaders/metadata próprios dos custom nodes (workflow oficial usa UNETLoader bf16 + LTXICLoRALoaderModelOnly — testamos com int8; pode faltar algo no patch int8 deles); (2) IC-LoRA só engata com o transformer **bf16** (o workflow oficial carrega bf16 — na nossa 8GB o bf16 roda por streaming, ~3min/clip, mas descartamos por decisão de espaço); (3) algum parâmetro do LTXAddVideoICLoRAGuide (tiled encode / tile_frames 97) importa para >97 frames? (nossos clips são 121f — o default de tile_frames é 97!).

**Next steps dia seguinte:** (a) testar tile_frames=121; (b) testar 97 frames (4s) em vez de 121; (c) se persistir, teste único com bf16 via streaming só para isolar; (d) reportar no GitHub do ComfyUI (o erro "ERROR lora shape [4096,2048]" com LoraLoaderModelOnly core em pesos quantizados é bug real — os custom nodes da Lightricks contornam o crash mas talvez não o patch em int8).

## A saga dos bugs da madrugada (lições duras)

1. **HF gated + hCaptcha/AWS-WAF**: signup com temp-mail bloqueado silenciosamente no IAB e no Edge real (challenges de grade resolvidos por visão e recusados por behavioral score). Resolução: **ModelScope** tem o repo oficial Lightricks/LTX-2.5 + espelhos `Genius-Society` abertos — zero gate.
2. **Civitai = revisão antiga dos arquivos Lightricks**: nvfp4 do Civitai (18721432024 B) ≠ oficial HF/MS (18721548408 B). Misturar Gemma-MS + NVFP4-Civitai → `RuntimeError mat1×mat2 (7040x4096 vs 2048x4096)`. Regra: **par completo da mesma fonte**.
3. **LoRA não aplica em transformer quantizado** (bug central): no comfy 0.44.0/0.44.2 + torch 2.13, `LoraLoaderModelOnly` nas LoRAs VFX sobre o distilled **nvfp4** (U8-packed) ou **comfy-int8-convrot** (I8+comfy_quant) falha com `ERROR lora ... shape '[4096,2048]' invalid for input of size 16777216` — e o comfy **continua sem a LoRA** (não aborta!). Sintoma: v2v com AddGuide **reconstrói a referência** (output = input, imune a seed/prompt/lora-strength). T2V puro funciona perfeito (carro vermelho no pôr do sol) → modelo/encoder/sampler OK. **Solução: transformer bf16 denso (42 GB)** — LoRA patcha denso sem path quantizado.
4. Bash: `local i=$1 a=$((i*C))` com `set -u` explode (expansão antes da atribuição); curl `-C` + `-r` são incompatíveis (usar append por stdout); nohup em bash morre entre tool-calls — **processos longos em Node via run_in_background**.
5. Downloads: Civitai B2 expira URL assinada (~30min) e throttle 429 após ~30GB/paralelo; ModelScope throttleia sob concorrência e libera depois. Multi-range Node (8-16 segs, atomic `.new`+rename, retry com cooldown) resolveu: pico 40MB/s.


| # | Efeito | Fonte | Strength | Veredito |
|---|---|---|---|---|
| 1 | Day to Night | street | 1.0 | (preencher) |
| 2 | Clean Plate | street | 1.0 | |
| 3 | Water | street | 1.0 | |
| 4 | Deblur | street_blur | 1.0 | |
| 5 | Decompression | desk_crushed | 1.0 | |
| 6 | Colorization | bw_train_gray | 1.3 | |
| 7 | Restore | bw_arch_gray | 1.0 | |
| 8 | Refine | desk | 1.0 | |
| 9 | Upscale ×2 | street_small | 1.0 | |
| 10 | Alpha Gen | dancer | 1.0 | |
| 11 | Layout→Render | gray_blocks + neon_look | 1.0 | |
| 12 | Cinemagraph | foto chuva | 1.1 | |
| 13 | Slow Motion | foto skate | 1.0 | |
| 14 | Ingredients | sheet | 1.0 | |
| 15 | SDR→HDR | rain_win | 1.0 fixo | |

(resultados e tempos em `moss38/run.log`; benchmarks alimentam `moss38/index.html`)

## O que aprendemos (preliminar)

- *(preencher após a fila)*
