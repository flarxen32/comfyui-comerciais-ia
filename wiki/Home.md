# 📚 Wiki — Vídeo infinito & low VRAM no ComfyUI

> Conhecimento consolidado da pesquisa de 2026-10-28 sobre os resultados do YouTube para **"vídeo infinito low vram comfyui"** (20 resultados, 12 vídeos dissecados com transcrição completa) + aplicação prática ao pipeline MOSS/H3.
>
> **Atualizado 2026-11-03** com experimentos práticos v25–v37: MCtx chaining, Pika H3 Flex, motion transfer, TTS Chatterbox, anti-borrão, multi-reference, protocolo anti-crash GPU.
> **Atualizado 2026-11-08** com [LTX-2.5 VFX LoRAs](ltx25-vfx-loras.md): 15 LoRAs da Lightricks p/ VFX v2v grátis (clean plate, day→night, água, matte, deblur, colorize, restauro, blockout→render), workflow 1-nó p/ 12 GB.

## TL;DR

O "vídeo infinito" no ComfyUI em 2026 não é um modelo que gera minutos de uma vez — é **[segmentação encadeada](video-infinito.md)**: cada shot é uma geração normal (5–10s) e um nó orquestrador passa o contexto (últimos frames + motion + áudio nativo) do shot anterior para o próximo. Como cada segmento roda sozinho, **o comprimento deixa de ser problema de VRAM** — roda até em 6GB. O ecossistema dominante é o **[MiniMax H3](minimax-h3.md)**; alternativas: LongCat, WAN 2.2 AIO, LTX 2/2.3.

## Índice

| Página | Conteúdo |
|---|---|
| [Conceito: vídeo infinito](video-infinito.md) | Como funciona o encadeamento de shots e por que a duração deixa de ser problema de VRAM |
| [LTX-2.5 VFX LoRAs](ltx25-vfx-loras.md) | **Novo**: 15 LoRAs Lightricks p/ VFX v2v grátis (remove, relight, água, matte, restore, blockout→render); workflow 1-nó, 3060 12 GB, 2–4 min/clipe |
| [MiniMax H3](minimax-h3.md) | O modelo: stack, quantizações, settings (sigma shift, frame grid), prompt, Ref2VA, artefatos |
| [Nós de vídeo longo](nos-de-video-longo.md) | Motion Director (LoRAtech) · RealRebelAI LongVideos OPTIMIZED · from the beat vs fixed · LongCat extend |
| [Técnicas low-VRAM](tecnicas-low-vram.md) | Catálogo completo: quantização, offloading, flags, atenções, chunk FF, self-lift, turbo LoRAs, 2 passadas |
| [Consistência de personagem](consistencia-de-personagem.md) | Character sheet, R2V vs I2V, memory string, regras de prompt, inpainting p/ correção |
| [Upscale final](upscale-final.md) | RTX Video Super Resolution · DLSS 5 · por que NÃO usar upscaler interno |
| [Modelos alternativos](modelos-alternativos.md) | LongCat · WAN 2.2 AIO · LTX 2 / 2.3 · Wan SCAIL2 |
| [Benchmarks e limites](benchmarks.md) | Hardware × saída × tempo; tamanhos de modelo em disco |
| [Pegadinhas e limitações](pegadinhas.md) | Os erros/armadilhas que os vídeos citam + nossas cicatrizes v25-v37 |
| [Experimentos v25–v37](experimentos-v25-v37.md) | **Novo**: MCtx chaining, Pika Flex, TTS, anti-borrão, multi-ref, protocolo anti-crash, QA automatizado, o que NÃO funciona |
| [Receita p/ pipeline MOSS](pipeline-moss.md) | Aplicação passo a passo ao nosso pipeline de comerciais H3 |
| [Fontes e metodologia](fontes.md) | Todos os vídeos (links, canais, stats), workflows, e como a pesquisa foi feita |

## Mapa rápido de decisão

- **Quer vídeo longo com diálogo/lip-sync?** → H3 + [nó de vídeo longo](nos-de-video-longo.md) + `from the beat`
- **Personagem/influenciador tem que ser o mesmo do início ao fim?** → [reference-to-video + character sheet](consistencia-de-personagem.md) + [multi-ref char+ambiente](experimentos-v25-v37.md)
- **Dança com movimento de viral?** → [Motion transfer R2V + Pika Flex](experimentos-v25-v37.md) + Sharper 0.8 + Perfect Hands 0.3
- **Zero cortes em 15s?** → take único 362f (1 difusão contínua); [MCtx chaining tem micro-saltos em dança](experimentos-v25-v37.md)
- **Voz de estúdio PT-BR?** → [Chatterbox TTS + forced audio](experimentos-v25-v37.md) (MIT, clonagem de timbre)
- **GPU trava/crasha?** → [Protocolo anti-crash](experimentos-v25-v37.md): 1 take + free_vram + cooldown 60s
- **Pouca VRAM?** → [fused INT8 + subgrafo de atenções](tecnicas-low-vram.md); veja [limites por GPU](benchmarks.md)
- **Precisa de 2K/4K no final?** → [RTX VSR ou DLSS 5](upscale-final.md), nunca upscaler interno
- **Sem áudio nativo no orçamento?** → [LongCat ou WAN 2.2 AIO](modelos-alternativos.md)
- **Mãos borradas?** → [lightx2v turbo é a causa](experimentos-v25-v37.md); usar Pika Flex + Sharper 0.8
- **VFX num take pronto (remover pessoa, dia→noite, água, matte, restauro)?** → [LTX-2.5 VFX LoRAs](ltx25-vfx-loras.md) video-to-video, grátis, 2–4 min/clipe
