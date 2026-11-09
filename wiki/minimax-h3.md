# MiniMax H3 — o modelo

← [Home](Home.md) · Anterior: [Conceito](video-infinito.md) · Próximo: [Nós de vídeo longo](nos-de-video-longo.md)

## O que é

Modelo aberto (open-weight) multimodal de geração vídeo+áudio. Gera **vídeo e áudio na mesma passada**: diálogo com lip-sync, efeitos sonoros e música juntos, seguindo o prompt. Suporta sequências multi-shot, texto legível dentro da cena e áudio estéreo nativo. É o modelo dominante nos vídeos de "vídeo longo low VRAM" da pesquisa (8 dos 20 resultados).

## Stack de modelos (tamanhos em disco)

| Arquivo | Tamanho | Observação |
|---|---|---|
| Difusão H3 (INT8 ou FP8) | ~21 GB | ver regra de quantização abaixo |
| Text encoder Qwen3-VL-32B (NVFP4) | 15.7 GB | versão AWQ também existe |
| VAE vídeo (FP16) | ~5.8 GB (2 VAEs juntos) | |
| VAE áudio (FP32) | ↑ | separado do de vídeo |
| **Total típico** | **~42.5 GB** | (Skill Destiny) |

Variações usadas nos vídeos:
- `minimax_h3_fused_refdelta_r1024_turbo8_mystic07_int8_convrot` — **fused INT8 turbo** (AmberNova; a base dos workflows 6GB)
- Pruned INT8 (Skill Destiny) · FP8 E4M3FN (Tensor Alchemist, GPUs Ada/Blackwell)
- Encoder alternativo: Qwen3-VL **GGUF INT8 "web version"** (CG Pixel) e **INT4** (Tensor Alchemist / workflow de inpainting)

## Regra de quantização (Tensor Alchemist)

| Componente | GPU Ada Lovelace (RTX 40xx) ou Blackwell (50xx) | GPU mais antiga |
|---|---|---|
| Difusão | **FP8** (tensor cores aceleram) | **INT8** |
| Encoder | **NVFP4** só se Blackwell; senão INT4 | INT4 (ou GGUF) |

Pasta: difusor em `models/diffusion_models`, encoder em `models/text_encoders`, VAEs em `models/VAE`. ComfyUI **atualizado** é obrigatório (suporte H3 chegou num update recente; aparecem 3 templates oficiais MiniMax após atualizar). Python 3.12; CUDA compatível com a geração da GPU.

## Offloading

Com 8GB VRAM + **32GB de RAM** (mínimo citado), o gerenciamento dinâmico de memória do ComfyUI faz streaming dos pesos — o Tensor Alchemist monitorou e **não houve swap significativo em SSD** durante a geração. Lento, mas seguro. Workflows low-VRAM (Skill Destiny) reservam ~0.9GB de VRAM para o resto do sistema (não clica OOM com browser aberto).

## Settings que importam

### Sigma Shift (nó próprio do H3)
- **shift video = 12** e **shift audio = 3** são os defaults do modelo — 12 é o sweet spot de movimento (mais que isso = movimento caótico com morphing); audio não se mexe.

### Duração é "pedido", não resultado
- O H3 trabalha na **grade de 24 fps**; um nó de math faz snap para CIMA: 5s → 124 frames (= 5.17s); 2s → 56 frames (= 2.33s). Qualquer valor intermediário arredonda para o próximo comprimento alcançável.

### Steps / sampler
- Sampler **euler + scheduler simple** (escolha do LoRAtech após horas de teste) ou **res_multistep + simple** (Tensor Alchemist, CG Pixel).
- Steps: 20 = sweet spot de qualidade (Skill Destiny); 12–14 para teste; **8** com fused turbo (CG Pixel); **4** com turbo LoRA (LoRAtech — perde qualidade em movimento rápido). CFG 1.

### Resolução
- Em **megapixels**, com tabela de conversão no workflow (0.5MP ≈ 960×544; 0.4MP ≈ 864×480). FPS 24 fixo — interpolar depois, fora do workflow.
- Limites medidos em 8GB: [Benchmarks](benchmarks.md).

### Cache do text encoder (economia grande de tempo)
- Rodar de novo com o **mesmo prompt** (trocando só o seed) **não recodifica o texto** — o encoder cacheia. Para re-rolls de seed, mantenha prompt/imagens iguais.

### First/last frame
- I2V aceita first frame e last frame (conectar outro Load Image na entrada `last frame`).
- **First frame é esticado** para o canvas; **last frame é center-crop**.

## Prompt no H3

- Estrutura do Skill Destiny: descrição visual da cena + seção separada iniciada com "Audio:" descrevendo o som.
- **Diálogo entre aspas duplas** → o modelo detecta e faz o lip-sync automaticamente, mantendo ação/câmera em movimento.
- Multi-personagem: **descrever por aparência** ("the man in the yellow shirt"), nunca por nome (o modelo não sabe quem é "Marcus"); personagens visualmente parecidos **fundem-se**.

## Ref2VA (reference-to-video-audio)

Segundo modelo H3 (~+21GB; encoder e VAEs compartilhados):
- até **9 imagens de referência + 3 vídeos + 3 áudios**;
- binding estrutural: "picture one turns to picture two and says ...";
- **áudio de referência condiciona a voz** = casting de voz por personagem;
- ComfyUI já traz o nó. É o modelo usado para [consistência com character sheet](consistencia-de-personagem.md) e no [inpainting](consistencia-de-personagem.md#inpainting-para-correção).

## Artefatos conhecidos do H3 (e correções)

| Artefato | Correção |
|---|---|
| Highlights estourados / imagem lavada | LoRA **de-oiling**; DLSS corrige parte |
| Look "oleoso" de pele | LoRA de-oiling |
| Pele "queimada" em steps baixos | LoRA **anti-burn** (strength 0.5) |
| Rostos distantes desestruturam (planos largos, res. baixa) | medium close-up; subir megapixel |
| Morphing em movimento rápido | reduzir shift; evitar turbo 4-step |
| Faces em orientação "longa"/pequena | subir resolução base |
| **Mãos borradas em movimento rápido** | lightx2v turbo é a causa; usar **Pika Flex** + **Sharper Video 0.8** + **Perfect Hands 0.3** |
| **Fundo sintético que não cola com a personagem** | **Multi-reference**: ref_image_0=personagem + ref_image_1=ambiente (still sem pessoa) |

## Pika H3 Flex (v32+)

LoRA oficial da Pika (1,9GB BF16, `Pika-Labs/Pika-H3-Flex` no HF) sobre o H3 base — **único pós-treinamento com pesos abertos**. 6 steps nativos (não usar turbo nem nafasp junto — o Pika já é o pós-treino completo).

**Stack validado na 3070 8GB (v37):**
```
ref2va int8 + pika_flex_ref2va (1.0) + Sharper Video (0.8) + Perfect Hands (0.3)
→ 6 steps, 480×864, 124f → ~10min/take
```

**Calibração crítica**: Sharper a 1.5 mata o movimento (motion 0,7 = quase estático). A 0.8 mantém dança e afia mãos.

**Multi-reference (v37)**: além do ref_video para motion transfer, passar `ref_image_0` (personagem) + `ref_image_1` (ambiente/sem pessoa). O modelo tem referência visual do cenário → fundo cola com a personagem. Prompts devem descrever como a luz afeta ambos.

## Referências dos vídeos

- Skill Destiny (8GB, detalhes): https://youtu.be/VNi9QTSHxEU
- Tensor Alchemist (FP8/INT8, limites): https://youtu.be/jZsBMdjV4z0
- LoRAtech (settings/euler): https://youtu.be/6oz0ms9GRY8
