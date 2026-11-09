# Benchmarks e limites medidos

← [Home](Home.md) · Anterior: [Modelos alternativos](modelos-alternativos.md) · Próximo: [Pegadinhas](pegadinhas.md)

Números reais citados nos vídeos (não estimativas). Fonte entre parênteses.

## Hardware × saída (MiniMax H3)

| GPU / setup | Resultado | Tempo | Fonte |
|---|---|---|---|
| RTX 3060 **6GB** + 16GB RAM | 40s, 0.6MP, fused INT8, 8 steps | **~107 min** | CG Pixel |
| RTX 3060 6GB | 14s | ~1h | CG Pixel |
| RTX 3060 6GB | luta de 1 min | ~2h | CG Pixel |
| RTX 3060 6GB | 5s @ 0.6MP + self-lift + DLSS → **4K** | 13–38 min | CG Pixel (4K) |
| RTX 5060 laptop **8GB** (INT8) | **15s = 480p (0.4MP) · 10s = 540p · 5s = 720p** — acima disso OOM | — | Tensor Alchemist |
| 8GB genérico (offloading) | 5s H3 | 5–10+ min | Skill Destiny |
| RTX 3050 8GB (LTX2) | 5s HD | ~10 min | Bored Coder |
| 8GB (flags + 2 passadas, LTX 2.3) | 10s 480×832 | **~1 min** (44s + 15s) | CWB LTX 2.3 |
| RTX **5090** + 64GB RAM | 1 segmento de 6s @ 0.8MP | ~1min15s | LoRAtech |
| RTX 5090 + 64GB RAM | 30s **contínuo** (sem segmentar) | **não roda** (não cabe) | LoRAtech |

## Limites de resolução × duração em 8GB (INT8)

- 15s → 0.6MP **OOM**, 0.5MP **OOM**, **0.4MP (864×480) OK**
- 10s → ~540p OK
- 5s → ~720p OK
- Com **FP8 E4M3FN + Sage attention** os tempos melhoram "significativamente" (sem número fechado) — Tensor Alchemist

## Tamanhos em disco

| Stack | Total |
|---|---|
| H3 completo (difusão 21GB + encoder NVFP4 15.7GB + VAEs ~5.8GB) | **~42.5GB** |
| H3 + Ref2VA (modelo extra) | ~63GB (encoder/VAEs compartilhados) |
| LongCat FP8 + distiller + VAE | ~15GB+ |
| WAN 2.2 AIO (tudo num arquivo) | ~22GB |
| LTX 2.3 (Q4_K_M + Gemma3 GGUF 6.14GB + projection 2.31GB) | ~23GB |

## Requisitos mínimos citados

- **H3 low-VRAM:** 6GB VRAM (CG Pixel/AmberNova) com **16GB RAM**; Tensor Alchemist recomenda **32GB RAM** para offloading confortável
- **H3 workflow 4K self-lift + DLSS:** 6GB (CG Pixel) — mas o workflow "Secret Sauce" do CottonByte pede **16GB VRAM + 64GB RAM** (é workflow de velocidade/4K, não de 6GB)
- Setup base: Python **3.12**, CUDA compatível com a geração da GPU, ComfyUI atualizado, PyTorch do site oficial

## Conversões úteis

- H3: 0.4MP ≈ 864×480 · 0.5MP ≈ 960×544 · 0.6MP+ maior (tabela no workflow)
- Duração H3 sofre snap na grade 24fps: 5s→5.17s (124 frames), 2s→2.33s (56 frames)
- WAN AIO: "5s" melhor como **length 81 + FPS 16** que 121 frames
- LongCat: cena ~93 frames @ 15fps ≈ 6s; 413 frames ≈ 27s
