# Modelos alternativos (fora do MiniMax H3)

← [Home](Home.md) · Anterior: [Upscale final](upscale-final.md) · Próximo: [Benchmarks](benchmarks.md)

Alternativas que apareceram na pesquisa para vídeo longo / low VRAM sem o stack H3:

## LongCat

**Vídeo:** https://youtu.be/peoQXfY-KU0 (ComfyUI Workflow Blog, 24k views) · **Post:** https://aistudynow.com/comfyui-longcat-workflow-make-very-long-video-on-low-vram/

Modelo aberto da ByteDance feito **para vídeos de minutos**: T2V, I2V e **continuação** no mesmo modelo.

- **Modelos (HuggingFace):** BF16 27GB (GPU forte) ou **FP8 15GB (low VRAM)** + **LoRA distiller alpha** (50 → **12 steps**) + VAE v2.1. Encoder BF16 na lista da página.
- Requer wrapper atualizado (kijai) → aparece o scheduler **"longcat distiller"**.
- Settings do teste: flash attention 2, 12 steps, **overlap 13** (fusão entre segmentos), 640×604, CFG 1, **15fps**.
- **Mecanismo de infinito:** grupo "extend image" — copiar/colar e encadear output→input quantas vezes quiser ("sem limite real"). Cada cena ~93 frames (~6s) em **~1 min** em GPU fraca; teste encadeou até 413 frames ≈ 27s com luz/cor/rosto consistentes.
- Sem áudio nativo com lip-sync (diferença-chave vs H3).

## WAN 2.2 AIO

**Vídeo:** https://youtu.be/rBAI32tl_hI (ComfyUI Workflow Blog, 53k views)

**WAN 2.2 I2V / T2V rapid AIO** — **um único arquivo FP8 de ~22GB** no checkpoint loader: difusor + high/low noise juntos, sem nó de CLIP, sem VAE separada. Roda com **8GB VRAM + 16GB RAM** (relato de usuário). Só precisa do `clip_vision_h.safetensors` para I2V.

Versões no HuggingFace:

| Versão | Avaliação do vídeo |
|---|---|
| base | motion básico, nada especial |
| V2 | melhor motion, shift de cor no início |
| V3 | 720p, mix SkyReels, prompt match melhor, shift de cor no início |
| **V4** | **motion dramático e estável, sem shift de cor** |
| **V5** | **mais balanceado/suave — só I2V** |

- Settings: scheduler beta, length 81; resolução testou até 1024×1024.
- **Dica de ouro:** para "5 segundos" use **length 81 + FPS 16** (motion mais suave que 121 frames — que deixou o movimento esquisito).
- Qualidade ~ FP16 dual-noise, porém muito mais rápido/leve.

## LTX 2

**Vídeo:** https://youtu.be/ub-1pBrAd9U (Bored Coder, 33k views)
- Workflow simples de I2V com **áudio** em 8GB; RTX 3050: **5s HD em ~10 min**; 121 frames @ 24fps. Prompting fácil (tips dentro do workflow). Links na descrição.

## LTX 2.3 v1.1 (workflow 8GB com OOM fix)

**Vídeo:** https://youtu.be/CIpY4nt-F1E (ComfyUI Workflow Blog, 23k views)

A "aula de flags" da pesquisa — aplicável a qualquer modelo:
- Flags: `--lowvram --reserve-vram 1.0 --cache-lru 10 --preview-method taesd` (ver [Técnicas](tecnicas-low-vram.md#4-flags-de-inicialização-do-comfyui-ltx-23))
- Modelos: **distilled 1.1 Q4_K_M** (sem LoRA extra) + **Gemma 3 GGUF** (6.14GB!) + text projection 2.31GB ≈ 23GB total
- Patches: Sage + memory-efficient attention + chunk FF
- **LTX NAG node**: negativa muito mais forte ("no bad hands, no weird text")
- Resolução digitada direto (480×832, 10s @ 24fps); geração em 2 passadas com cache
- Medido: pico 8.1GB; 10s de vídeo em ~1 min em 8GB
- Upscale: exportar vídeo → RTX VSR (o upscaler interno picou 14GB)

## LTX low VRAM com GGUF + fix de ruído de áudio

**Vídeo:** https://youtu.be/r7TACD329wY (Veteran AI) — solução completa LTX2 em VRAM baixa com GGUF e correção do ruído no áudio gerado.

## Wan SCAIL2

**Vídeo:** https://youtu.be/51ay-rW8sMI (Prime Giggle Clips) — "testando e é incrível"; baixar os modelos menores se faltar espaço/VRAM; rápido em VRAM baixa.

## Comparativo rápido com H3

| | H3 | LongCat | WAN 2.2 AIO | LTX 2.3 |
|---|---|---|---|---|
| Áudio nativo c/ diálogo | ✅ | ❌ | ❌ | parcial |
| Encadeamento | nós prontos | manual (extend) | ❌ | ❌ |
| Consistência multi-shot | alta (R2V+sheet) | média (overlap) | — | — |
| Veredito dos revisores | "toda geração aproveitável" | bom p/ minutos | melhor custo/benefício sem áudio | rápido, mas "gerar muito p/ achar boa" |
