# Pegadinhas e limitações

← [Home](Home.md) · Anterior: [Benchmarks](benchmarks.md) · Próximo: [Receita MOSS](pipeline-moss.md)

As armadilhas que os vídeos da pesquisa citam explicitamente — coleção de cicatrizes alheias:

1. **Drift de personagem após ~13s** sem âncora em todos os shots (CG Pixel). Fix: [R2V + character sheet em cada shot](consistencia-de-personagem.md); ajustar prompt do shot crítico; trocar seed.

2. **Nunca terminar um shot com o personagem de costas ou saindo do quadro** — o shot seguinte usa os últimos frames como âncora e "perde" o personagem (AmberNova).

3. **Duração pedida ≠ duração entregue** no H3: snap para cima na grade de 24fps (5s vira 5.17s). Trate o campo como pedido (Skill Destiny).

4. **Turbo/4-step degrada movimento rápido** com qualidade visível; steps práticos: 8 (fused turbo) a 20 (padrão). CFG 1 (LoRAtech, CG Pixel, Skill Destiny).

5. **Rostos distantes / planos largos desestruturam** em resolução baixa (540p–) — preferir medium close-up ou subir megapixel (Tensor Alchemist, CG Pixel).

6. **Movimento largo/rápido quebra no self-lift / 3-pass** — o Secret Sauce é para movimento moderado; slow-motion ok (CottonByte).

7. **Artefatos estéticos do H3**: highlights estourados, look oleoso, pele queimada em steps baixos → LoRAs **de-oiling** e **anti-burn (0.5)** (CottonByte, CG Pixel 4K).

8. **Face refine do Motion Director fica ruim** — deixar off (LoRAtech). Upscale interno do nó dobra o tempo; o upscaler embutido do workflow LTX pica 14GB de VRAM.

9. **Leak de RAM/VRAM em sessões longas do ComfyUI** — gerações vão ficando mais lentas até reiniciar o processo (LoRAtech tem monitor experimental com botão de liberar; sem ele: reiniciar entre lotes).

10. **Setup**: ComfyUI desatualizado = nós H3 não aparecem; Python > 3.12 pode quebrar; NVFP4 só roda em Blackwell; GGUF na pasta errada = workflow não carrega; **FPS do vídeo tem que bater com o nó video combine** no upscale RTX ou o tempo desincroniza.

11. **Encoder recodifica ao mudar o prompt** (lento) — mas com **mesmo prompt + novo seed ele cacheia**. Para re-rolls, não mexa no texto (Skill Destiny).

12. **Interpolação de frames remove o feel cinematográfico** — usar só em clips selecionados, nunca no vídeo todo (Tensor Alchemist).

13. **First frame é esticado** para o canvas, **last frame é center-crop** — preparar as imagens de acordo (Skill Destiny).

14. **Character semelhantes se fundem**; nome próprio no prompt não significa nada — descrever por aparência (Skill Destiny).

15. **"Fast" model do H3 (3ª opção no Motion Director) tem qualidade ruim** — evitar (LoRAtech).

16. **Por que chain-extend degrada (e como os vídeos "sem degradação" resolvem)** — cada extensão latent reinterpreta o latent anterior: cores do fundo deslocam, rosto ganha contraste/escurece; a deriva acumula a cada extensão. Shot estático é o pior caso (o modelo redesenha o mesmo fundo toda vez); shot com movimento degrada menos. Soluções vistas (OBVPM/Shannon, GiJxlWOooyo): (a) gerar o clip inteiro de uma vez em baixa resolução (0.2MP) e refinar/upscale em janelas de 5s com overlap 1.3s (MultiDiffusion temporal); (b) **root+bridge**: clips ímpares são raízes frescas e os pares são pontes com motion context dos dois lados — a derida nunca acumula mais de uma ponte.

17. **Regras da PONTE (bridge) latent-to-latent** — (i) prompt da ponte deve ser CURTO: "single continuous shot, no cuts, she says: …" — prompt detalhado faz o modelo seguir o prompt e hard-cortar em vez de continuar; (ii) dar TEMPO: ponte pede ~12s para entregar ~9.5s (a geração engole os frames pinados dos vizinhos); sem tempo ela hard-cuta no fim; (iii) seed da ponte pode variar (tentar algumas); (iv) raízes alinham fundo com MESMA seed + MESMA duração + MESMA imagem-referência (mesmo ruído inicial).

18. **Chroma 4:2:0 cria offset de 2 frames nas juntas** de concatenação — emendar clips em formato 4:2:0 gera seams visíveis; sair em 4:4:4 ou 4:2:2 (H3 Studio/XOY2RwrOgYo). O H3Assemble do OBVPM corta pelo sidecar latent e não sofre disso, mas concat ffmpeg direto sim.

19. **Janela de contexto (22f default) precisa cair num frame LIMPO** — onde você pega a janela importa mais que qualquer outra coisa: frame em sombra/motion blur/chicoteada de câmera dá nada útil ao modelo e o clip seguinte desvia. Escolher momento parado, bem iluminado (H3 Studio auto-scaneia por exposição+estabilidade).

20. **MCtx chaining NÃO é pixel-perfect para dança rápida (v36-v37)** — o pin fornece continuidade *latent* mas o modelo regenera os pixels da junção. Em talking heads (movimento sutil) a micro-diferença é invisível. Em dança com movimentos corporais grandes, há um salto de 1-2% na posição visível como corte (diffs 44-67 vs 2-5 normal). **Única forma de zero cortes garantido**: take único (1 difusão contínua).

21. **lightx2v ref2v turbo LoRA borra mãos em movimento rápido** (v32-v35, confirmado em [HF discussion #33](https://huggingface.co/lightx2v/Minimax-h3-Turbo/discussions/33)). Fix: usar Pika H3 Flex LoRA no lugar + Sharper Video (0.8, não 1.5!) + Perfect Hands (0.3, overtrained).

22. **Sharper Video LoRA a 1.5 MATA o movimento** (v35: motion caiu de 6.5 para 0.68). A 0.8 mantém dança e afia mãos. Calibração obrigatória.

23. **Detail Slider degrada FALA** (v27: garbage fonético no início de todo take). Não usar em conjunto com TTS/forced audio.

24. **apps desktop (Edge, Epic, Copilot) comem 2-4GB VRAM durante o dia** — renders pesados de madrugada ou taskkill antes. Sem isso: OOM em takes que passam tranquilamente de madrugada.

25. **Windows case-insensitive**: prefixo `story_teoF` colide com `story_teof` → assemble grava _00002 e o post lê _00001 velho. Sempre usar nomes únicos por versão.

26. **MP4 0KB = crash durante o save** (moov atom missing). Validar integridade (ffprobe) de todos os takes antes de montar; runners zumbis podem sobrescrever arquivo bom com truncado.

27. **`--disable-comfy-compiler` desativa malloc-graph mas expõe CUDA OOM** — sem o compiler o gerenciamento de memória do aimdo fica inativo e alocações grandes estouram. A 8GB, sempre usar compiler ON (default) + protocolo anti-crash (free_vram + cooldown).

