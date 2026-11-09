# Experimentos práticos v25–v37 (out–nov/2026)

← [Home](Home.md) · Anterior: [Receita MOSS](pipeline-moss.md)

Registro completo das técnicas testadas, validadas e rejeitadas em 13 versões de reels de dança e diálogo, todas na RTX 3070 8GB.

---

## Arquiteturas testadas

### 1. Root + Bridge (v25, rejeitada)
Raízes independentes + pontes de motion latent dos dois lados. **Falha**: raízes alinham a personagem (via ref) mas o layout da cena varia por geração (diff 41-58 entre primeiros frames). As pontes "morphaam" o fundo entre layouts → mudança de cena visível.

### 2. Cadeia de extensões MCtx (v25-v27, validada para talking heads)
1 raiz + N extends com pins MCtx de 39f. **Funciona perfeitamente para talking heads** (movimento sutil, câmera fixa): 30s+ contínuos sem corte. **Limitação para dança rápida**: o pin fornece continuidade *latent* mas não *pixel-perfect* — em movimentos corporais grandes há micro-salto de 1-2% na posição visível como corte (v36-v37 confirmaram: diffs 44-67 nas junções vs 2-5 normal).

### 3. Takes independentes + crossfade (v32, v34, parcial)
4×124f com crossfade 0,25s na batida. Reduz cortes mas não elimina — ainda visível. Fórmula do crossfade encadeado: `setpts factor = sd/ds` (alvo/origem, NÃO origem/alvo).

### 4. Take único longo (não resolvido)
243f (10s) funciona a 480×864 mas motion cai com Sharper a 1.5. 362f (15s) OOM em qualquer resolução testada. **Única forma de zero cortes garantido**: 1 take = 1 difusão contínua.

---

## TTS Chatterbox pt-BR (v28-v29)

- **Modelo**: `ChatterboxMultilingualTTS` (pip `chatterbox-tts`), `language_id="pt"`, `audio_prompt_path` = ref de voz de 9s
- **Licença**: MIT ✅
- **Sem param de velocidade** — pacing por contagem de palavras + `cfg_weight` menor (mais lento)
- **Taxa de fala real do H3**: ~2,05 palavras/s com pausas (calibrar roteiro por contagem, não por "achismo")
- **QA da voz**: o sample H3 que ensina o clone também precisa passar por whisper — sample gaguejado → clone gaguejado
- **Forced audio na cadeia**: trilha-mestre TTS fatiada por take na grade do latent; a região pinada contém o mesmo PCM → pin segura bit-exact
- **Pausas naturais**: segmento TTS mais curto que o take vira silêncio forçado com boca fechada (sem murmulho)

---

## Pika H3 Flex (v32+)

- **O que é**: LoRA oficial da Pika (1,9GB BF16) sobre o H3 base — único pós-treinamento com pesos abertos
- **Stack**: `ref2va int8 + pika_flex_ref2va_comfy_bf16 (1.0) + Sharper (0.8) + Perfect Hands (0.3)` — 6 steps
- **VRAM**: mesma da base (~10min/124f@480×864 com anti-crash protocol)
- **Licença**: MiniMax H3 Community License (mesma da base)
- **Calibração crítica**: Sharper Video LoRA a 1.5 **mata o movimento** (motion 0,7 = quase estático). A 0.8 mantém dança e melhora nitidez. Não usar nafasp nem turbo junto (Pika já é o pós-treino completo).

---

## LoRAs anti-borrão de mãos (v35)

| LoRA | ID Civitai | Strength | Efeito |
|---|---|---|---|
| Sharper Video (saliacoel) | 3427546 | 0.8 (máx 1.5) | Aumenta nitidez em movimento; 1.5 mata o motion |
| Perfect Hands (Polyhedron) | 3278036 | 0.3 (overtrained) | Melhora dedos especificamente; peso baixo por design |
| Cinematic V2 | 2890588 | ~0.85 | Reduz look plástico; download falhou (403), multi-ref é mais impactante |

**Causa raiz do borrão**: o lightx2v ref2v turbo LoRA borra mãos em movimento rápido (confirmado em [HF discussion #33](https://huggingface.co/lightx2v/Minimax-h3-Turbo/discussions/33)).

---

## Multi-reference char + ambiente (v37)

O H3 aceita até 9 `ref_images`. Passando:
- `ref_image_0` = personagem (MOSS still com corpo inteiro)
- `ref_image_1` = **ambiente** (MOSS still SEM pessoa, com prompt de iluminação específica)

O modelo tem referência visual do cenário (não só texto) → fundo cola com a personagem. Prompts devem descrever como a luz afeta **ambos**: *"the warm amber lighting illuminates both the woman and the concrete walls behind her, creating matching shadows and color temperature"*.

Técnicas complementares da pesquisa ([Reddit](https://www.reddit.com/r/StableDiffusion/comments/1w8daml), [RunDiffusion](https://www.rundiffusion.com/minimax-h3-prompt-guide)):
- Equirectangular panoramas como referência de ambiente
- Imagens de personagem com fundo transparente
- Múltiplas referências de cena (até 9)

---

## Motion transfer R2V ref_video (v31+)

### O que funciona
- `MiniMaxH3ReferenceToVideo` com `ref_videos.ref_video_0` (via `GetVideoComponents`)
- Vídeo de referência a 480×864 (mesma resolução do take), 24fps
- Fontes: virais do YouTube baixados via yt-dlp, janelas de 5-10s com mais fluxo de movimento
- Score anti-borrão: `mediana(fluxo) / (1 + pico/mediana × 0,12)` — movimento forte com pico controlado

### Limitações de VRAM
| Config | Status |
|---|---|
| 576×1024 × 243f | OOM (com ou sem compiler) |
| 480×864 × 243f | Funciona (85min/take, motion fraco com Sharper 1.5) |
| 480×864 × 124f | **Config recomendada** (~10min com Pika 6-step) |
| 416×744 × 243f | OOM (apps desktop devoram VRAM de dia) |
| 352×640 × 362f | **Não testado** — teoricamente cabe (0.54× pixels de 480×864) |

### Sincronização para comparativo lado a lado
O R2V usa o trecho do viral como ref_video → a IA copia o movimento na **mesma timeline**. Dois `<video>` tags no HTML lado a lado = sincronia por construção.

---

## Protocolo anti-crash GPU (v33+, validado)

```python
# 1 take por vez
free_vram()  # POST /free {"unload_models": true, "free_memory": true}
time.sleep(60)  # cooldown
```

Sem isso: GPU driver crash (WDDM lost, "aimdo memory compile error") a cada 2-3 takes. Com isso: 10/10 renders sem crash. A 3070 aguenta 100% GPU por horas se descarregar modelos entre jobs.

**Causas de crash identificadas**:
- `--disable-comfy-compiler` desativa malloc-graph mas CUDA OOM aparece (memória não gerenciada)
- Apps desktop (Edge, Epic, Copilot) comem 2-4GB VRAM durante o dia
- `aimdo memory compile error` = malloc-graph do comfy-aimdo falha sob pressão de RAM

---

## QA automatizado

| Check | Ferramenta | Threshold |
|---|---|---|
| Motion (presença de movimento) | mediana diff frames | > 1.5 (dança) |
| Fundo estável | diff faixa superior | < 40 (talking) / < 40 (dança, relaxado) |
| Palavras extras (TTS) | whisper Δpalavras | ≤ +1 (fala forçada) |
| Nitidez | Laplaciano variance | comparar entre versões |
| Integridade pós-crash | ffprobe moov atom | duração > 0 |
| Cortes visíveis | diff frames picos | > 20 = investigar |

**QA invertido para dança**: take precisa SE MOVER (mediana > 1.5); talking head era ~0.3.

---

## Ferramentas e downloads

| Ferramenta | Fonte | Uso |
|---|---|---|
| treg CLI | [treg.to](https://treg.to) | YouTube search (~$0.001/hit), catálogo 4000+ tools |
| yt-dlp | sistema | Download de virais (`--extractor-args "youtube:player_client=tv,web_embedded,web_safari"`) |
| Whisper (faster-whisper) | venv hermes | QA de fala (small/int8 CPU) |
| Chatterbox TTS | venv ttsvenv | Voz pt-BR (MIT, clonagem de timbre) |
| MOSS-Image | ComfyUI native | Stills de personagens e ambientes |
| Ace-Step 1.5 Turbo | ComfyUI | Música de fundo |
| RIFE v4.26 | ComfyUI native | 48fps interpolation |

---

## Resumo do que NÃO funciona

1. ❌ Raízes independentes + pontes (layout de cena varia, ponte morpha)
2. ❌ 243f+ com Sharper a 1.5 (motion morre)
3. ❌ 362f a 480×864 (OOM)
4. ❌ Piper TTS para feminina (só faber=male PT-BR)
5. ❌ lightx2v ref2v turbo (borra mãos)
6. ❌ Detail Slider degrada fala (garbage fonético)
7. ❌ Crossfades eliminam a percepção de corte (só disfarçam)
8. ❌ MCtx chaining para dança rápida (micro-salto visível nas junções)
