# Receita para o pipeline MOSS (H3)

← [Home](Home.md) · Anterior: [Pegadinhas](pegadinhas.md) · Próximo: [Fontes](fontes.md)

Aplicação do conhecimento da pesquisa ao nosso pipeline de comerciais (que já gera 30s com diálogo H3 nativo e lip-sync, sem TTS externo). Objetivo: passar de 30s para vídeos longos/"infinitos" mantendo o influenciador consistente e sem estourar VRAM.

## Passo a passo recomendado

1. **Instalar o nó orquestrador**
   `git clone https://github.com/RealRebelAI/MiniMax-H3-LongVideos_OPTIMIZED` em `custom_nodes/` (+ restart). Alternativa com UI mais rica: Motion Director via ComfyUI Manager (workflow no Discord do LoRAtech).

2. **Modelo fused INT8 turbo**
   Baixar `minimax_h3_fused_refdelta_r1024_turbo8_mystic07_int8_convrot` (difusor) + encoder Qwen3-VL (NVFP4 se Blackwell, senão INT4 ou GGUF INT8 web) + VAE vídeo FP16 + VAE áudio FP32. Encoder e VAEs já temos do fluxo atual do H3.

3. **Subgrafo de otimização** (já vem nos workflows prontos)
   H3 SLA attention + low VRAM attention + Kitchen attention + chunk feed-forward. Não mexer nos valores.

4. **Timing de diálogo: `from the beat`**
   Os cortes seguem as falas do prompt — casam perfeitamente com o nosso formato de diálogo H3 nativo. `fixed` só se precisarmos de shots uniformes.

5. **Consistência do influenciador (crítico)**
   - Gerar **character sheet** do influenciador (vários ângulos/expressões — já temos as fotos-base dos 26 influenciadores).
   - Usar **reference-to-video com o sheet ancorado em TODOS os shots** (não só no primeiro).
   - Preencher **character memory string** (nome, idade, traços de rosto/roupa).
   - Se precisar amarrar a voz: Ref2VA com áudio de referência (casting de voz).

6. **Prompt longo (formato AmberNova)**
   - Parágrafo 1 = âncora visual (produto/marca, ambiente, luz, personagem, estilo).
   - 1 parágrafo por shot; **nunca terminar shot com o personagem de costas/saindo**.
   - Diálogo entre **aspas duplas** → lip-sync nativo automático.

7. **Resolução e upscale**
   - Gerar em 0.5–0.6MP (960×544 ~ 1080×608) e finalizar com **RTX Video Super Resolution (ultra, 2×)** ou **DLSS 5** para 2K/4K. Nunca upscaler interno.
   - FPS 24 fixo na geração; conferir FPS do nó de upscale.

8. **Fluxo de trabalho operacional**
   - Testar shot isolado primeiro (selective run do Motion Director / rodar 1 segmento).
   - Regenerar só shots ruins, não a linha inteira.
   - Entre lotes: reiniciar/liberar memória do ComfyUI (leak em sessão longa).
   - Re-rolls: manter o prompt e trocar só o seed (cache do encoder).

## Metas realistas por hardware

- 6GB: 40s em ~1h45 (ok para entregáveis overnight) — [Benchmarks](benchmarks.md)
- 8GB: shots de 5s a 720p, ou mais tempo em 480p
- 4K final via self-lift + DLSS 5 em ~13–38 min por vídeo (CG Pixel provou em 3060)

## Checklist de qualidade (evita os erros catalogados)

- [ ] Character sheet em todos os shots (R2V)
- [ ] Nenhum shot termina com personagem de costas/saindo do quadro
- [ ] Diálogo entre aspas duplas
- [ ] Megapixel ≥ 0.5 (rostos pequenos desestruturam abaixo disso)
- [ ] Shots com movimento rápido sem turbo 4-step
- [ ] Upscale final via RTX VSR/DLSS, não interno
- [ ] FPS do upscale = FPS da geração

## Pipeline v25+ (motion transfer de dança)

Para reels de dança com movimento copiado de virais (v31+):

1. **Pesquisa de viral**: treg CLI → YouTube search → baixar com yt-dlp
2. **Janelas anti-borrão**: score = `mediana(fluxo) / (1 + pico/mediana × 0,12)`
3. **Personagem + ambiente**: 2 stills MOSS (char com corpo inteiro + env sem pessoa)
4. **Refs**: trechos do viral a 480×864 24fps (mesma resolução do take)
5. **Stack**: ref2va int8 + Pika Flex (1.0) + Sharper (0.8) + Perfect Hands (0.3), 6 steps
6. **Render**: 124f takes, 1 por vez + `free_vram()` + cooldown 60s (anti-crash)
7. **QA**: motion > 1.5 (mediana diff frames), fundo estável
8. **Post**: RIFE 48fps + grade + fades
9. **Deploy**: HTML com dois `<video>` tags lado a lado (flex-direction: row)

**Para zero cortes**: usar take único (1 difusão contínua). MCtx chaining tem micro-saltos visíveis em dança rápida.

**Para TTS (v28+)**: Chatterbox Multilingual pt-BR (MIT), clonar voz de sample H3 limpo, roteiro calibrado a 2,05 palavras/s, forced audio na cadeia (trilha-mestre fatiada por take na grade do latent).
