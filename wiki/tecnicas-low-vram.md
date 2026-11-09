# Técnicas low-VRAM — catálogo consolidado

← [Home](Home.md) · Anterior: [Nós de vídeo longo](nos-de-video-longo.md) · Próximo: [Consistência](consistencia-de-personagem.md)

Tudo o que os vídeos da pesquisa usam para caber vídeo de modelo grande em GPU pequena, em ordem de impacto:

## 1. Segmentação encadeada (a técnica-mestra)

Ver [Conceito: vídeo infinito](video-infinito.md). Resolve a **duração**: o pico de VRAM é o de um shot, não do vídeo todo.

## 2. Quantização do modelo de difusão

| Formato | Quando | Fonte |
|---|---|---|
| **FP8** (E4M3FN) | RTX 40xx (Ada) ou 50xx (Blackwell) — tensor cores aceleram de verdade | Tensor Alchemist |
| **INT8** | GPUs mais antigas; é o formato dos workflows 6GB ("fused INT8 turbo") | CG Pixel, AmberNova |
| Fused (difusor+delta+turbo num arquivo) | sempre que disponível — menos arquivos/carregamento | AmberNova (`minimax_h3_fused_refdelta_r1024_turbo8_mystic07_int8_convrot`) |

Encoder: **NVFP4** só em Blackwell; **INT4** no resto; **GGUF INT8 web** também funciona (Qwen3-VL).

## 3. Offloading / gerenciamento dinâmico de VRAM

- ComfyUI faz streaming dos pesos entre RAM e VRAM. Precisa de **32GB de RAM** (mínimo citado); monitorado sem swap significativo de SSD.
- `--reserve-vram` para deixar headroom (workflow Skill Destiny reserva ~0.9GB; no vídeo de LTX 2.3 usaram `--reserve-vram 24` numa GPU de 32GB para simular 8GB).

## 4. Flags de inicialização do ComfyUI (LTX 2.3)

```
python main.py --lowvram --reserve-vram 1.0 --cache-lru 10 --preview-method taesd
```
- `taesd` → `none` se ainda der OOM (preview pesa memória)
- `--cache-lru 10` → cache pequeno; **é o que permite a geração em 2 passadas** (a 2ª continua de onde a 1ª parou, não recomeça)
- Portable: editar o `.bat` e acrescentar após `main.py`

## 5. Chunk feed-forward

Quebra o trabalho da rede em micro-batches → menos pico de VRAM. Presente em quase todos os workflows H3 (LoRAtech, AmberNova, CG Pixel) e LTX. Nos workflows prontos, **não mexer nos valores**.

## 6. Nós de atenção (o trio dos workflows 6GB)

| Nó | O que faz |
|---|---|
| **H3 SLA attention** (sparse local attention) | atenção esparsa/local — a maior economia dos workflows 6GB |
| **Low VRAM attention** | derruba o pico durante a atenção |
| **ComfyUI Kitchen Attention** | cozinha/otimiza a atenção (patch geral) |
| Sage attention | acelera FP8 (Tensor Alchemist viu ganho claro de tempo) |
| SigSpectral (nó Self-Lift) | mede por frame e corrige só as cabeças desbalanceadas → velocidade |

Na prática o subgrafo vem pronto: **SLA + low VRAM + Kitchen/chunk** (workflow CG Pixel/AmberNova/RealRebelAI).

## 7. Menos steps: turbo LoRAs e distillers

| Modelo | Solução | Custo |
|---|---|---|
| H3 | 4-step turbo LoRA (25→4 steps) | degrada movimento rápido |
| H3 fused turbo | 8 steps nativo | artefato "pele queimada" → LoRA anti-burn 0.5 |
| LongCat | LoRA distiller alpha (50→12 steps) + scheduler "longcat distiller" | — |
| LTX 2.3 | modelo distilled 1.1 Q4_K_M (sem LoRA extra) | — |

## 8. Self-Lift Progressive Sampling ⭐ (a novidade de out/2026)

**O quê:** em vez de rodar todos os denoise steps na resolução final, começa em resolução baixa (estabelece composição/contorno/movimento), **levanta a resolução do latent num ponto escolhido** e termina os steps finais em resolução cheia.
**Ganho:** resolução final alta sem pagar resolução alta o tempo todo — 4K em RTX 3060 6GB em ~13 min (CG Pixel). Sem treino adicional.
**Onde:** plugin **Yusu MiniMax H3 Unified** (https://github.com/yusu-02/ComfyUI-Yusu-MiniMaxH3-Unified) + presets (qualidade/equilíbrio/aceleração). Parâmetro "transition step" controla quando acontece o lift; latent upscaler interno faz o aumento.
**Trade-off:** perde detalhes pequenos vs single-pass; movimento largo/rápido desmorona (CottonByte).

## 9. Geração em 2 passadas com cache (LTX 2.3)

Pass 1 = primeiros 6 steps (testar sozinho, com pass 2 e upscaler em bypass) → Pass 2 = +2 steps **continuando do cache**. Medido: pass 1 = 44s/pico 8.1GB; pass 2 = 15s; total ~1min para 10s de vídeo em 8GB.

## 10. Upscale por tensor cores no final

RTX Video Super Resolution ou DLSS 5 em vez de upscaler interno — ver página dedicada: [Upscale final](upscale-final.md). (3–4GB de VRAM, ~30s, vs pico de 14GB do upscaler interno.)

## 11. Micro-otimizações citadas

- **Cache do encoder** (H3): mesmo prompt + novo seed = não recodifica texto (Skill Destiny).
- Resolução digitada em texto puro em vez de nó custom de resolução (cada nó a mais gasta VRAM — LTX 2.3).
- Reduzir preview durante teste; limpar cache entre renders; renderizar em partes e stitch (LongCat).
- Liberar memória vazada entre gerações / reiniciar sessão do ComfyUI em sessões longas (LoRAtech).
