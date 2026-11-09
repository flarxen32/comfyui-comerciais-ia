# Consistência de personagem em vídeos longos

← [Home](Home.md) · Anterior: [Técnicas low-VRAM](tecnicas-low-vram.md) · Próximo: [Upscale final](upscale-final.md)

O maior risco do encadeamento de shots **não é VRAM — é o personagem deriva**. O que a pesquisa ensina:

## I2V vs Reference-to-Video (o teste do LoRAtech)

| | Image-to-video (first/last frame) | Reference-to-video (R2V / Ref2VA) |
|---|---|---|
| Como ancora | só o primeiro shot | **character sheet em TODOS os shots** |
| Consistência de rosto | deriva quando o personagem vira/sai do quadro | **muito melhor, inclusive no último shot** |
| Custo | mesmo modelo | +21GB de modelo (encoder/VAEs compartilhados) |

Veredito do vídeo: para personagem consistente do início ao fim → **R2V com character sheet ancorado em cada shot**. I2V serve para shots genéricos sem personagem recorrente.

Detalhe técnico: no R2V, **a imagem de referência NÃO vira o primeiro frame** do segmento — por isso dá para ancorar todos os shots com a mesma imagem sem "pular".

## Character memory string (AmberNova)

Campo do painel de vídeo longo: nome do personagem, idade, traços-chave de rosto e roupa. Mantém consistência entre todos os shots do pipeline. Complementar (não substitui) o character sheet.

## Character sheet / action sheet (LoRAtech)

- **Character sheet**: imagem com o personagem em vários ângulos/expressões — ancora a aparência via R2V.
- **Action sheet**: acrescenta as ações que o personagem vai fazer — melhora a continuidade de movimento entre shots.

## Regras de prompt para vídeos longos (AmberNova)

1. **Parágrafo 1 = âncora visual**: estilo de câmera, ambiente, iluminação, detalhes do personagem, estilo de filme, atmosfera — vale para o vídeo todo.
2. Cada parágrafo seguinte (separado por quebra de linha) = **1 shot**.
3. **NUNCA termine um shot com o personagem virando de costas ou saindo do quadro** — quebra a âncora visual do shot seguinte (que usa os últimos frames).
4. **Diálogo entre aspas duplas** → lip-sync automático; ação e câmera continuam se movendo.
5. Multi-personagem: descreva **por aparência**, nunca por nome; torne-os visualmente distintos (dois parecidos se fundem).

## Deriva após ~13s (CG Pixel)

Mesmo com o nó de vídeo longo, o teste de 1 min de luta mostrou o personagem mudando após ~13s e "voltando" depois. Correções citadas:
- ajustar o prompt dos shots críticos;
- trocar o seed e rodar de novo;
- subir o megapixel (artefatos de rosto pioram em resolução baixa).

## Inpainting para correção (Tensor Alchemist)

**SAM 3.1 + prompt inpainting + Ref2VA**: rastreia objeto(s) por texto num vídeo em movimento, gera máscara limpa, regenera **só a região** (troca de roupa, edição de cenário, troca de objeto: besouro → carrinho vermelho) e compõe de volta no footage original. Roda em 8GB.
- Workflow: https://drive.google.com/file/d/1OcTGpraPvqtUn_qpgig8N0QU9s7866Kh
- Modelo SAM: https://huggingface.co/Comfy-Org/sam3.1 · Guia: https://docs.comfy.org/tutorials/utility/video-segment-sam3

## Casting de voz por personagem (Ref2VA)

O Ref2VA aceita **3 clipes de áudio de referência** — o áudio condiciona como a pessoa soa. É o "mais próximo de casting de voz" (Skill Destiny). Com até 9 imagens + 3 vídeos + 3 áudios: `picture one turns to picture two and says "..."`.
