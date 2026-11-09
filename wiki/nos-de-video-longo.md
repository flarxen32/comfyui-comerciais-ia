# Nós de vídeo longo (os orquestradores)

← [Home](Home.md) · Anterior: [MiniMax H3](minimax-h3.md) · Próximo: [Técnicas low-VRAM](tecnicas-low-vram.md)

São os nós que implementam a [segmentação encadeada](video-infinito.md). Três protagonistas na pesquisa:

---

## 1. RealRebelAI — MiniMax-H3-LongVideos_OPTIMIZED ⭐

**Repo:** https://github.com/RealRebelAI/MiniMax-H3-LongVideos_OPTIMIZED
**Quem usa:** CG Pixel (vídeo dos 40s em 6GB). Autor (RealRebelAI) mantém um canal com workflows low-VRAM para cada modelo.

- Instalação: `git clone` dentro de `ComfyUI/custom_nodes/` + restart.
- Entradas: modelo, clip (encoder), VAE vídeo + áudio, prompt, first image opcional, negative prompt, CFG, shift vídeo/áudio (defaults).
- **Parâmetros de duração:**
  - `shot_seconds` — segundos por segmento (ex.: 10)
  - `shot_length` — modo: **`from the beat`** (o nó analisa o prompt — falas/voice-over/ações — e calcula a duração real de cada shot; ex.: 4 segmentos de "10s" viram um vídeo final de 14s cortado nas batidas) ou **`fixed`** (todos os shots com a duração exata definida).
- **Upscale integrado** (opcional): métodos **RTX / model / Lanczos**, com fator (ex.: 2×).
- Subgrafo de otimização que acompanha: **ComfyUI Kitchen Attention + low VRAM attention (pico) + H3 SLA attention**.
- Prompt: parágrafos simples, **1 parágrafo = 1 segmento**; sem necessidade de descrição elaborada de estilo/ambiente; ChatGPT/Claude escrevem bem.

**Workflows prontos:**
- CG Pixel (grátis): https://drive.google.com/file/d/15FYXmjzvUv_NZRS2YqlZfWnVy_Oqc1Ue/view
- Artigo no Civitai: https://civitai.com/articles/35705

**Números (RTX 3060 6GB + 16GB RAM):** 14s ≈ 1h · 40s ≈ 107 min · luta de 1 min ≈ 2h · 0.6MP é o teto prático (por tempo).

---

## 2. LoRAtech — MiniMax H3 Motion Director

**Instalação:** pelo ComfyUI Manager (buscar "Motion Director") ou GitHub (link na descrição do vídeo). Workflow grátis no Discord do canal: https://discord.gg/2bqQXKxsxg
**Vídeo:** https://youtu.be/6oz0ms9GRY8 (118k views — o vídeo-síntese da técnica)

Interface "Open Director" com suite completa:

- **Timeline de prompt groups**: botão verde adiciona shots; cada um com prompt + segundos (defaults 6/5). Sem imagem por shot: o shot herda os últimos frames do anterior automaticamente. Dá para anexar imagem de origem em shots específicos (troca de roupa/cenário).
- **Selective run**: marcar só os shots ruins → regenera somente eles (não refaz a linha inteira).
- **Mode**: text-to-video / image-to-video / reference-to-video (+ outros) — deve casar com o model switch do workflow (1 = first/last frame = T2V/I2V; 2 = R2V; 3 = "fast" — qualidade ruim).
- **Saída**: aspect ratio, resolução em megapixels (0.7–0.9), FPS 24 (não mexer; interpolar fora).
- **Pós-processamento embutido**: segunda passada de sampling em denoise baixo (~dobra o tempo), upscale (método à escolha, ~dobra o tempo), deblur, **face refine (ruim — deixar off)**, live preview, aba Results com os segmentos em resolução cheia + som conforme ficam prontos.
- Acompanha: 3 loaders + model switch, 4-step turbo LoRA, nós de video/audio shift, **chunk feed-forward** e nó de atenção H3 pré-configurados.

**Benchmarks do vídeo:** ~1min15s por segmento de 6s @ 0.8MP na RTX 5090.

**Extra:** LoRAtech mostrou um monitor de recursos (não lançado) com botão *free up RAM* que devolve ~5GB de memória vazada entre gerações — vale saber que o leak existe em sessões longas do ComfyUI.

---

## 3. AmberNova — painel de controle do vídeo longo (H3)

**Workflow grátis:** https://ambernovastudio.gumroad.com/l/afdlbt
**Vídeo:** https://youtu.be/iprgDi1Eq98 (40s + 2K em 6GB)

Painel numerado usado no vídeo (o "H3 long videos node" com a aceleração embutida):

1. Aspect ratio (horizontal)
2. Resolução em megapixels — **0.5 = 960×544** nativo (equilíbrio VRAM/qualidade)
3. Modo de timing — `from the beat` (dinâmico, segue as falas) vs `fixed` (uniforme: 5s / 15s / 30s)
4. Duração por shot (no modo fixed)
5. Seed (reprodutibilidade)
6. **Character memory string** — nome, idade, traços de rosto e roupa → consistência entre shots (ver [Consistência](consistencia-de-personagem.md))

- Subgrafo de aceleração: **H3 SLA attention (sparse local) + chunk feed forward + low VRAM attention** → micro-batches → 40s contínuo sem OOM em 6GB.
- Finalização com [RTX Video Super Resolution → 2K](upscale-final.md).

---

## 4. LongCat — mecanismo "extend image" (alternativo)

Não é um nó único: é um **grupo de nós "extend" que se copia e encadeia** (output do grupo anterior → input do próximo). "Sem limite real" — o vídeo do ComfyUI Workflow Blog encadeia até ~30s e diz que 4/10/30 min é só copiar/colar e adicionar prompts. Detalhes em [Modelos alternativos](modelos-alternativos.md#longcat).

---

## Choosing: qual orquestrador?

| Situação | Escolha |
|---|---|
| Diálogo com cortes nas falas (comerciais MOSS) | RealRebelAI com `from the beat` (ou Motion Director) |
| Controle fino por shot + regenerar só o que falhou | Motion Director (selective run) |
| 6GB / tempo longo disponível | RealRebelAI + fused INT8 (workflow CG Pixel/AmberNova) |
| Sem H3 / sem áudio nativo | LongCat extend chain |
