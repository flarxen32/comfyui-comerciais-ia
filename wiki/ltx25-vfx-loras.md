# LTX-2.5 VFX LoRAs — VFX grátis em 2–4 min (12 GB VRAM)

← [Home](Home.md) · Veja também: [MiniMax H3](minimax-h3.md) · [Modelos alternativos](modelos-alternativos.md) · [Pegadinhas](pegadinhas.md)

> Fonte: vídeo **"No Seedance 2.5 Needed: Free AI VFX in 2 to 4 Minutes"** (the_frizzy1, 2026-11-07, 12:57) — https://youtu.be/y2dJfFNS8QY
> Dissecado em 2026-11-08: transcrição completa + README/downloads/notas do workflow oficial + model cards das 15 LoRAs no Hugging Face + quadros da seção de custos.

## TL;DR

A Lightricks lançou **15 LoRAs "Creative Lab" para LTX-2.5-22b** que fazem **VFX video-to-video de graça, local**: remover pessoas, dia→noite, simulação de água, matte sem green screen, deblur, colorização, restauro de arquivo, gray-blockout→render etc. O the_frizzy1 empacotou tudo num **workflow único** (só nós core do ComfyUI 0.44+, zero custom nodes) que roda em **RTX 3060 12 GB** com **2–4 min por clipe de 4 s**. É a alternativa gratuita ao que o Seedance 2.5 cobra **~US$ 0,39/segundo**. Regra geral do IC-LoRA: o clipe original entra como **referência congelada** (VAE-encode 1×) e o prompt segue o formato **"Reference shows X. Edited shows Y. TRIGGER ..."**.

## Stack de modelos (Lightricks/LTX-2.5 — gated, aceitar termos logado no HF)

| Arquivo | Pasta | Tamanho | Obs |
|---|---|---|---|
| `ltx-2.5-22b-distilled-transformer-nvfp4.safetensors` | `diffusion_models/` | 18.7 GB | a versão do workflow 12 GB; 8 steps fixos, CFG 1 |
| `ltx-2.5-22b-distilled-transformer-comfy-int8-convrot.safetensors` | `diffusion_models/` | ~int8 | alternativa ComfyUI-only |
| `gemma4-12b-with-proj-ltx-2.5-comfy-int8-convrot.safetensors` | `text_encoders/` | 15.4 GB | text encoder Gemma 4 12B + projections |
| `ltx-2.5-video-vae-bf16.safetensors` | `vae/` | 1.5 GB | |
| `ltx-2.5-audio-vae-bf16.safetensors` | `vae/` | 0.4 GB | gera/mantém áudio |
| `ltx-2.5-latent-spatial-upscaler-x2-bf16-1.0.safetensors` | `latent_upscale_models/` | 1.0 GB | só T2V/I2V; tamanho snap múltiplo de 64 |
| Pose: `ltx-2.3-22b-ic-lora-union-control-ref0.5` + `sdpose_wholebody_fp16` + `rt_detr_v4-x-hgnet` | `loras/`, `checkpoints/`, `diffusion_models/` | 0.7+1.9+0.1 GB | IC-LoRA Union 2.3 roda no 2.5 |

LoRAs VFX: **0,2–1,7 GB cada**, baixar só as que usar (todas em `loras/`). Total das 15 ≈ 14 GB. Workflow: [Thefrizzy1/The_frizzy1-Workflows · ltx/ltx-2.5-ultimate-12gb](https://github.com/Thefrizzy1/The_frizzy1-Workflows/tree/main/workflows/ltx/ltx-2.5-ultimate-12gb) (v3.1.1).

## Os 11 modos do workflow (1 dropdown MODE)

T2V · I2V (first frame) · First+last frame · Pose control (IC-LoRA Union) · **VFX: video to video** (picker de LoRA) · **VFX: Layout to Render** · **VFX: Ingredients** · I2V + Cinemagraph · I2V + Slow motion. VFX v2v e Pose devolvem o **áudio original** do clipe.

## As 15 LoRAs — tipos de vídeo, settings e veredito

### Grupo "Reference shows / Edited shows" (VFX v2v)

| LoRA | O que faz | Strength | Prompt (formato) | Veredito do vídeo |
|---|---|---|---|---|
| **Clean Plate** | remove pessoas e reconstrói o fundo vazio (sem máscara) | **1.2** + nomear a pessoa ("no man with a blue cap and glasses"), sentada; 1.0 p/ quem passa andando | descrever a CENA VAZIA; nomear objetos persistentes no positivo E negativo ("no bicycle anywhere") | ✅ 3:32 no 3060; removeu 2 pessoas que passam; luta quando a pessoa domina o quadro |
| **Day To Night** | dia→noite, acende lâmpadas, janelas azuis | 1.0 com gente em movimento; 1.3 = noite mais escura mas gente "borra" | descrever a cena noturna | ✅ o mais confiável; ~2:30 |
| **Water Simulation** | adiciona água realista (chuva, inundação, rio, poça) | 1.0; 1.25–1.45 = drama máximo (risco de drift); ≥1.5 deforma rostos | **"ADD WATER"** + "Reference shows seco. Edited shows mesma cena com água. ADD WATER <descrição>" | ⚠️ hit-and-miss: em 960×512 pintou o sofá de teal; **em 1280×704 (MP 0.9) inundou o chão direito** (6 min); noutro clipe só chão molhado |
| **Deblur** | reconstrói de blur (é um "palpite", não recupera real) | 1.0 (1.3 não muda) | "Reference shows... Edited shows... DEBLUR" | ✅ surpreendeu; **não confiar em rosto/detalhe** |
| **Decompression** | melhora clipe comprimido | 1.0 | "...ENHANCE QUALITY" | ⚠️ **inventa texto** — não usar em screen recordings |
| **Colorization** | P&B→cor | **1.3** (em 1.0 a cor volta lavada/desbotada; card oficial diz 1.0 e 0.8–0.9 se sangrar) | "Reference shows P&B. Edited shows cores naturais. COLORIZE <descrição vívida>" | ✅ em 1.3 a camisa azul volta e fica |
| **Restore** | restaura arquivo danificado (fita, broadcast, scratch, flicker; coloriza junto) | **1.0 é um switch** (0.7 desliga, 1.4 altera cor) | sem trigger; prompt rico de época/lugar/luz; negativo lista o que não inventar | (não testada no vídeo; card: tiled 960×544 mesmo em FullHD, janelas de 97f, emenda com últimos 17f restaurados) |
| **Refine Details** | afina detalhe | 1.0 | descrever a cena | ❌ "dificilmente visível" p/ o autor |
| **SDR To HDR** | SDR 8-bit → HDR 16-bit (EXR ACEScg + HLG 10-bit) | **fixo 1.0** | **sem prompt** (embedding fixo pré-computado) | (não testada; card: força 1.0 fixa, keyframe 0.95, frame 8k+1, sem áudio) |
| **Pixel Spatial Upscaler x2** | upscale 2× | 1.0 | descrever a cena | ⚠️ bom em draft, **mudou o rosto** em footage real |
| **Alpha Gen** | matte branco/preto sem green screen | 1.0 | **deixar o prompt VAZIO** | ✅ manteve fios de cabelo e saia (3:30); corta o foreground INTEIRO (levou cadeira+microfone); máx 145f/1920×1088; composição: `out = rgb·alpha + bg·(1−alpha)` |

### Modos próprios (não são o formato reference/edited)

| Modo | Como funciona | Veredito |
|---|---|---|
| **Layout to Render** | blockout cinza (Blender/playblast) → render final; **first frame = o look** (gere com qualquer image model a partir do 1º frame do clay; NUNCA usar o frame cinza). 2 estágios: 960×544×8 steps → 1920×1088×3 steps. Prompt curto do shot final, **não escrever "clay/3D/Unreal"**; frames cortam p/ 8k+1 (72→65 é normal) | ✅ viral; virou rua neon chuvosa seguindo blocos+câmera; **sem first frame = clay cinza de volta** (1º frame ~40s + vídeo ~3:30). Seedance fez o mesmo SEM first frame |
| **Ingredients** | reference sheet (painéis: close de rosto + turnaround por personagem, props, location) como **vídeo estático de referência ≥121 frames** — NÃO é first frame; bucket 768×448×121f@24 | ❌ 9 de 9 runs copiou o grid do sheet; força maior não corrigiu |
| **Cinemagraph** | foto → loop com só 1 elemento animado; trigger **`CINEMAGRAPH_MOTION,`** no início; explicitar "Only the X moves; everything else frozen", câmera travada, "seamless natural loop" | ⚠️ funcionou em cachoeira, na mesa "continuou se movendo"; é p/ cenário sem pessoas |
| **Slow motion** | foto → slow-mo até 40×; speed é **valor numérico** (1.0 → 0.025), não palavra; **não escrever "slow motion" no prompt** | ✅ usar **0.2**; 0.05 não ficou mais lento |

## Settings que importam

- **Megapixels**: 0.5 ≈ 960×512 (padrão dos testes); **0.9 = 1280×704** (o que consertou a água, ainda cabe em 12 GB). OOM → baixar MP primeiro, depois encurtar clipe.
- **Frames**: sempre **8k+1** (1, 9, 17 … 121 …); dimensões múltiplas de 32 (layout/upscaler pedem 64). 24 fps.
- **Distilled**: 8 steps, CFG 1, sigma fixo. Re-roll = trocar seed (encoder cacheia o prompt).
- **VFX LoRA strength**: default 1.0; exceções nas tabelas acima (Clean Plate 1.2, Colorization 1.3). >1 não ajudou em cinemagraph/slow-mo/ingredients; água >1 escureceu a sala.

## Benchmarks medidos (RTX 3060 12 GB · 32 GB RAM · 960×512 · 4 s)

| Modo | Wall | VRAM pico | RAM pico |
|---|---|---|---|
| T2V | 1:43 | 11.6 GB | 18.9 GB |
| I2V first frame | 2:00 | 11.3 GB | 19.1 GB |
| First+last | 2:32 | 11.3 GB | 19.3 GB |
| Pose (IC-LoRA Union) | 3:44 | 11.7 GB | 20.6 GB |
| Clean Plate 1.2 | 3:27 | 11.7 GB | 19.8 GB |
| Layout to Render | 3:30 | 11.7 GB | 20.1 GB |
| Ingredients | 4:09 | 11.6 GB | 19.4 GB |
| Cinemagraph / Slow-mo | 1:49 | 11.6 GB | ~20 GB |

**12 GB vs 24 GB (RTX PRO 4000)**: maior clipe 1280×784·4s vs **1920×1088·10s**; Clean Plate desk 3:32@960×544 vs 17:22@1920×1088; RAM pico ~20 GB vs ~53 GB. Em 12 GB os efeitos são os mesmos, só menores — upscale externo na 2ª passada.

## Onde o grátis para (vs Seedance 2.5 no OpenArt)

- Custos medidos: **US$ 1,56/try** (549 credits), **US$ 0,39/s**, plano Plus US$ 29/mês = 12.000 credits; 5 testes do autor = 2.745 credits ≈ **US$ 7,78**.
- Seedance: até 1080p e 30 s, e faz o que **não existe LoRA** p/ LTX-2.5: trocar fundo por cenário neon, "kraken", cabeça em fogo (essas viram embeddings p/ MiniMax H3 — ver [minimax-h3.md]).
- LTX-2.5 grátis: máx prático ~10 s em 24 GB, 4 s em 12 GB, 960–1280 de largura.

## Viabilidade na NOSSA máquina (RTX 3070 8 GB · 32 GB RAM)

Abaixo de 12 GB "vai ser muito difícil" (palavras do autor) — mas nossa RAM de 32 GB é o mesmo cenário dele, e o gerenciamento de memória do ComfyUI faz streaming dos pesos (o NVFP4 de 18.7 GB + Gemma 15.4 GB não precisa caber na VRAM). Estratégia: clipe curto (2–4 s), MP 0.5 ou menos, LoRAs pequenas primeiro (Clean Plate/Day-to-Night são só 0.33 GB). Alternativa: transformer **comfy-int8-convrot**. Se OOM no decode da VAE: clipe mais curto / tiled decode. Risco maior é tempo, não viabilidade — o H3 já rodou em 8 GB aqui ([benchmarks](benchmarks.md)).

## Aplicação ao pipeline MOSS / comerciais

- **Clean Plate + Alpha Gen** = pré-produção de composição: plate limpo + matte do influenciador → trocar fundo mantendo a luz (o Alpha Gen corta o foreground inteiro; separar pessoa/cadeira ainda precisa de roto ou máscara).
- **Day To Night / Water** = variação de comercial a partir do MESMO take master (2–3 min por variação, grátis).
- **Layout to Render** = animatic 3D barato → look final; casa com a ideia de storyboard→render do pipeline H3.
- **Restore** = recuperar footage velho de cliente sem tooling de restauro.
- Áudio original preservado nos modos VFX v2v → não quebra o forced audio/lip-sync do pipeline.

## Fontes

- Vídeo: https://youtu.be/y2dJfFNS8QY (transcrição `en` integral; seção de custos lida por quadros)
- Workflow: https://github.com/Thefrizzy1/The_frizzy1-Workflows/tree/main/workflows/ltx/ltx-2.5-ultimate-12gb
- Modelo base + LoRAs: https://huggingface.co/Lightricks/LTX-2.5 e `Lightricks/LTX-2.5-22b-{IC-}LoRA-*` (15 repos, set–out/2026; gated — "Agree and access" por página, logado)
- Vídeos relacionados do canal: LTX 2.5 no 3060 vs MacBook Air M5 (HeHY6N5hH_M) · "LTX 2.5 Is the New Low-VRAM King (Beats MiniMax H3)" (TlV72fg9skw) · Long AI videos free (dSzM3ovKBko)
