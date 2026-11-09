# Conceito: vídeo infinito

← [Home](Home.md) · Próximo: [MiniMax H3](minimax-h3.md)

## A ideia central

Nenhum vídeo da pesquisa gera minutos de uma vez. Nem uma RTX 5090 com 64GB de RAM segura uma geração contínua de 30s do H3 (afirmação do LoRAtech, que roda esse hardware). O que existe é **segmentação encadeada**:

1. Um **nó orquestrador** (ver [Nós de vídeo longo](nos-de-video-longo.md)) mantém uma timeline de "shots"/"prompt groups".
2. Cada shot tem **prompt próprio + duração própria** (5–10s tipicamente).
3. Ao rodar, os shots são gerados **em ordem**, e o nó passa o **contexto do shot anterior para o próximo**:
   - os **últimos frames** gerados (âncora visual),
   - o **motion** (continuidade de movimento),
   - o **áudio** (no H3, o som continua entre os cortes — vídeo+áudio são gerados juntos).
4. Cada segmento é uma geração normal e independente → **a GPU nunca segura o vídeo inteiro na memória** → empilhar 10, 20 shots não aumenta o pico de VRAM. Comprimento deixa de ser problema de hardware.

## Por que funciona tão bem no H3

O MiniMax H3 gera **vídeo e áudio nativamente na mesma passada** (diálogo com lip-sync, efeitos, música). Quando os shots são encadeados, o áudio transita junto — um diálogo de 40s soa como uma gravação única, com os cortes caindo nas batidas das falas (modo [`from the beat`](nos-de-video-longo.md)).

## Os dois ecossistemas

| | MiniMax H3 | Alternativos (LongCat, WAN 2.2, LTX) |
|---|---|---|
| Áudio nativo com lip-sync | ✅ sim | ❌ não (LTX2 tem áudio, sem a mesma qualidade de diálogo) |
| Nó de encadeamento pronto | ✅ Motion Director / LongVideos OPTIMIZED | LongCat: cadeia manual de nós "extend" |
| Consistência entre shots | alta com character sheet (R2V) | moderada (overlap de frames) |
| Custo | modelo 21GB em disco (INT8/FP8) | LongCat FP8 15GB · WAN AIO 22GB · LTX ~23GB |
| Veredito dos revisores | "toda geração é aproveitável" | LTX: "precisa gerar muito p/ achar uma boa" |

## O que "infinito" significa na prática

- **LoRAtech**: "stack 10 shots, 20 shots, quantos quiser prompting" — infinito de verdade.
- **CG Pixel**: 40s é o número que ele usa no título; gerou até 1 min de luta (com drift de personagem após ~13s sem âncora — ver [Consistência](consistencia-de-personagem.md)).
- **LongCat**: "sem limite real" — copia e cola o grupo extend quantas vezes quiser.
- Na prática o limite é **tempo** (40s em RTX 3060 6GB ≈ 107 min) e **deriva de personagem**, não VRAM.

## Páginas relacionadas

- [Nós de vídeo longo](nos-de-video-longo.md) — os orquestradores concretos
- [Técnicas low-VRAM](tecnicas-low-vram.md) — o que segura o pico de memória dentro de cada shot
- [Benchmarks](benchmarks.md) — números reais por GPU
