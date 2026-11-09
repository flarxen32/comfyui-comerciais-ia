// v38 — Gerador de workflows API LTX-2.5 VFX (grafo achatado do frizzy v3.1.1)
// Uso: node wf_gen.js <effect>          -> imprime JSON do prompt
//      node wf_gen.js                   -> lista efeitos
const fs = require("fs");
const path = require("path");

const SIGMAS = "1.0, 0.99375, 0.9875, 0.98125, 0.975, 0.909375, 0.725, 0.421875, 0.0";
const NEG_BASE = "pc game, console game, video game, cartoon, childish, ugly";

const EFFECTS = {
  clean_plate: {
    src: "street.mp4", lora: "ltx-2.5-22b-ic-lora-clean-plate-1.0.safetensors", strength: 1.0,
    pos: "An empty clean plate of the exact same location: identical background, environment, structures and lighting as the source video, no people, no pedestrians anywhere in the frame. Static photorealistic footage, natural light, high detail.",
    neg: "person, people, human, figure, pedestrian, ghosting, semi-transparent remnants",
  },
  day2night: {
    src: "street.mp4", lora: "ltx-2.5-22b-ic-lora-day-to-night-0.9.safetensors", strength: 1.0,
    pos: "The same city street transformed to night: dark blue night sky, street lamps glowing warm orange, shop windows lit from inside, car headlights streaking, wet asphalt reflections. Photorealistic night scene, moody cinematic light.",
    neg: "",
  },
  water: {
    src: "street.mp4", lora: "ltx-2.5-22b-ic-lora-water-simulation-0.9.safetensors", strength: 1.0,
    pos: "Reference shows a dry city street with pedestrians crossing. Edited shows the same scene with water added. ADD WATER a flooded street, knee-deep murky river water flowing over the crossing, splashes around walking feet, reflections of the buildings in the water.",
    neg: "",
  },
  deblur: {
    src: "street_blur.mp4", lora: "ltx-2.5-22b-ic-lora-deblur-0.9.safetensors", strength: 1.0,
    pos: "Reference shows a blurred city street scene. Edited shows the same scene with sharp focus restored. DEBLUR crisp architectural details, sharp text on signs, defined silhouettes of pedestrians.",
    neg: "",
  },
  decompression: {
    src: "desk_crushed.mp4", lora: "ltx-2.5-22b-ic-lora-decompression-0.9.safetensors", strength: 1.0,
    pos: "Reference shows a heavily compressed low-quality office desk scene with blocky artifacts. Edited shows the same scene restored. ENHANCE QUALITY clean smooth gradients, no compression blocks, sharp facial details, crisp text on the monitor.",
    neg: "blocky artifacts, banding, pixelation",
  },
  colorization: {
    src: "bw_train_gray.mp4", lora: "ltx-2.5-22b-ic-lora-colorization-0.9.safetensors", strength: 1.3,
    pos: "Reference shows a grayscale scene of a steam train arriving at a station platform in 1896 with passengers. Edited shows the same scene with natural colors restored. COLORIZE the steam locomotive deep black with warm smoke, stone platform in warm browns, passengers in muted period colors, soft morning light.",
    neg: "",
  },
  restore: {
    src: "bw_arch_gray.mp4", lora: "ltx-2.5-22b-ic-lora-restore-1.0.safetensors", strength: 1.0,
    pos: "Archive footage of a busy New York street in the 1900s restored: horse-drawn carriages, crowds in hats and dark coats, brick buildings, cobblestone road. Natural colour, sharp photographic detail, crisp faces and clothing texture, natural grain, high resolution footage.",
    neg: "shipping containers, logos, signage, lettering, modern vehicles, graffiti, modern buildings, blurry, soft, plastic, smeared detail, oversharpened halos, warped faces",
  },
  refine: {
    src: "desk.mp4", lora: "ltx-2.5-22b-ic-lora-refine-details-1.0.safetensors", strength: 1.0,
    pos: "A crisp, sharp home office scene with a man talking at his desk: detailed skin texture, fabric weave on the chair, clear monitor content, refined small details everywhere. Photoreal, high detail.",
    neg: "",
  },
  upscale2x: {
    src: "street_small.mp4", lora: "ltx-2.5-22b-ic-lora-pixel-spatial-upscaler-x2-1.0.safetensors", strength: 1.0,
    pos: "A busy city street with pedestrians crossing, upscaled: sharp details, crisp signage text, defined faces, photorealistic.",
    neg: "",
  },
  alpha_gen: {
    src: "dancer.mp4", lora: "ltx-2.5-22b-ic-lora-alpha-gen-0.9.safetensors", strength: 1.0,
    pos: "", neg: "",
  },
  layout2render: {
    src: "gray_blocks.mp4", guideImage: "neon_look.png", lora: "ltx-2.5-22b-ic-lora-layout-to-render-1.0.safetensors", strength: 1.0,
    pos: "A rainy neon-lit city street at night seen from this angle: glowing signs in pink and blue reflecting on wet asphalt, distant light haze, cinematic depth. Photoreal, real wet stone and glass materials.",
    neg: "clay, gray, 3D, unreal",
  },
  ingredients: {
    src: "street.mp4", guideImage: "ingredients_sheet.png", initBypass: true, lora: "ltx-2.5-22b-ic-lora-ingredients-0.9.safetensors", strength: 1.0,
    pos: "Reference sheet: a female dancer in a flowing dress (face close-up and full body) and a city street location. Generated video: the dancer spins gracefully, dress flowing, on the city street. Consistent character with the reference sheet.",
    neg: "worst quality, inconsistent motion, blurry, jittery, distorted",
  },
  cinemagraph: {
    src: "rain_win.mp4", imageInit: "cinemagraph_src.png", lora: "ltx-2.5-22b-lora-cinemagraph-0.9.safetensors", strength: 1.1,
    pos: "CINEMAGRAPH_MOTION, tripod locked-off static camera, zero camera movement. Only the rain streaks sliding down the glass and the shimmering bokeh lights move; everything else frozen perfectly still. Seamless natural loop.",
    neg: "camera movement, pan, tilt, zoom, parallax, whole image moving",
  },
  slowmo: {
    src: "skate.mp4", imageInit: "slowmo_src.png", frameRate: 120, lora: "ltx-2.5-22b-lora-slow-motion-control-1.0.safetensors", strength: 1.0,
    pos: "A skateboarder mid-air performing a trick above a skatepark ramp, arms out for balance, dust particles suspended in the air.",
    neg: "slow motion, high fps",
  },
  sdr2hdr: {
    src: "rain_win.mp4", lora: "ltx-2.5-22b-ic-lora-sdr-to-hdr-1.0.safetensors", strength: 1.0, pos: "", neg: "",
  },
};

function build(name, opts = {}) {
  const e = EFFECTS[name];
  const W = opts.width || 960, H = opts.height || 544, L = opts.length || 121;
  const fps = e.frameRate || 24;
  const seed = opts.seed ?? 42;
  const n = {};
  const link = (from, slot, to, iname) => [ String(from), slot ];

  n.load_video = { class_type: "LoadVideo", inputs: { file: e.src } };
  n.gvc = { class_type: "GetVideoComponents", inputs: { video: ["load_video", 0] } };
  n.from_batch = { class_type: "ImageFromBatch", inputs: { image: ["gvc", 0], batch_index: 0, length: L } };
  n.scale_video = { class_type: "ImageScale", inputs: { image: ["from_batch", 0], upscale_method: "lanczos", width: W, height: H, crop: "center" } };

  n.unet = { class_type: "UNETLoader", inputs: { unet_name: opts.unet || "ltx-2.5-22b-distilled-transformer-comfy-int8-convrot.safetensors", weight_dtype: "default" } };
  n.vfx_lora = { class_type: "LTXICLoRALoaderModelOnly", inputs: { model: ["unet", 0], lora_name: e.lora, strength_model: e.strength } };
  n.clip = { class_type: "CLIPLoader", inputs: { clip_name: "gemma4-12b-with-proj-ltx-2.5-comfy-int8-convrot.safetensors", type: "ltxv", device: "default" } };
  n.vae = { class_type: "VAELoader", inputs: { vae_name: "ltx-2.5-video-vae-bf16.safetensors" } };
  n.audio_vae = { class_type: "VAELoader", inputs: { vae_name: "ltx-2.5-audio-vae-bf16.safetensors" } };

  n.pos = { class_type: "CLIPTextEncode", inputs: { text: e.pos, clip: ["clip", 0] } };
  n.neg = { class_type: "CLIPTextEncode", inputs: { text: [e.neg, NEG_BASE].filter(Boolean).join(", "), clip: ["clip", 0] } };
  n.cond = { class_type: "LTXVConditioning", inputs: { positive: ["pos", 0], negative: ["neg", 0], frame_rate: fps } };

  n.empty_latent = { class_type: "EmptyLTXVLatentVideo", inputs: { width: W, height: H, length: L, batch_size: 1 } };

  // init latent: vídeo (v2v) ou imagem única (i2v) — ou bypass (ingredients)
  if (e.imageInit) {
    n.load_image = { class_type: "LoadImage", inputs: { image: e.imageInit } };
    n.scale_img = { class_type: "ImageScale", inputs: { image: ["load_image", 0], upscale_method: "lanczos", width: W, height: H, crop: "center" } };
    n.i2v = { class_type: "LTXVImgToVideoInplace", inputs: { vae: ["vae", 0], image: ["scale_img", 0], latent: ["empty_latent", 0], strength: 0.7, bypass: false } };
  } else if (e.initBypass) {
    n.i2v = { class_type: "LTXVImgToVideoInplace", inputs: { vae: ["vae", 0], image: ["scale_video", 0], latent: ["empty_latent", 0], strength: 1.0, bypass: true } };
  } else {
    n.i2v = { class_type: "LTXVImgToVideoInplace", inputs: { vae: ["vae", 0], image: ["scale_video", 0], latent: ["empty_latent", 0], strength: 0.7, bypass: false } };
  }

  // guide: vídeo (default), imagem (layout/ingredients), ou mesma imagem (cinemagraph/slowmo)
  if (e.guideImage) {
    n.load_gimg = { class_type: "LoadImage", inputs: { image: e.guideImage } };
    n.scale_gimg = { class_type: "ImageScale", inputs: { image: ["load_gimg", 0], upscale_method: "lanczos", width: W, height: H, crop: "center" } };
    n.guide = { class_type: "LTXAddVideoICLoRAGuide", inputs: { positive: ["cond", 0], negative: ["cond", 1], vae: ["vae", 0], latent: ["i2v", 0], image: ["scale_gimg", 0], frame_idx: 0, strength: 1.0, latent_downscale_factor: 1, crop: "disabled", use_tiled_encode: false, tile_size: 256, tile_overlap: 64, use_streaming: false, tile_frames: 97 } };
  } else if (e.imageInit) {
    n.guide = { class_type: "LTXAddVideoICLoRAGuide", inputs: { positive: ["cond", 0], negative: ["cond", 1], vae: ["vae", 0], latent: ["i2v", 0], image: ["scale_img", 0], frame_idx: 0, strength: 1.0, latent_downscale_factor: 1, crop: "disabled", use_tiled_encode: false, tile_size: 256, tile_overlap: 64, use_streaming: false, tile_frames: 97 } };
  } else {
    n.guide = { class_type: "LTXAddVideoICLoRAGuide", inputs: { positive: ["cond", 0], negative: ["cond", 1], vae: ["vae", 0], latent: ["i2v", 0], image: ["scale_video", 0], frame_idx: 0, strength: 1.0, latent_downscale_factor: 1, crop: "disabled", use_tiled_encode: false, tile_size: 256, tile_overlap: 64, use_streaming: false, tile_frames: 97 } };
  }

  n.empty_audio = { class_type: "LTXVEmptyLatentAudio", inputs: { frames_number: L, frame_rate: fps, batch_size: 1, audio_vae: ["audio_vae", 0] } };
  n.concat_av = { class_type: "LTXVConcatAVLatent", inputs: { video_latent: ["guide", 2], audio_latent: ["empty_audio", 0] } };

  n.noise = { class_type: "RandomNoise", inputs: { noise_seed: seed } };
  n.guider = { class_type: "CFGGuider", inputs: { model: ["vfx_lora", 0], positive: ["guide", 0], negative: ["guide", 1], cfg: 1.0 } };
  n.sampler_sel = { class_type: "KSamplerSelect", inputs: { sampler_name: "euler_ancestral" } };
  n.sigmas = { class_type: "ManualSigmas", inputs: { sigmas: SIGMAS } };
  n.sampler = { class_type: "SamplerCustomAdvanced", inputs: { noise: ["noise", 0], guider: ["guider", 0], sampler: ["sampler_sel", 0], sigmas: ["sigmas", 0], latent_image: ["concat_av", 0] } };

  n.separate = { class_type: "LTXVSeparateAVLatent", inputs: { av_latent: ["sampler", 0] } };
  n.crop = { class_type: "LTXVCropGuides", inputs: { positive: ["guide", 0], negative: ["guide", 1], latent: ["separate", 0] } };
  n.decode = { class_type: "VAEDecodeTiled", inputs: { samples: ["crop", 2], vae: ["vae", 0], tile_size: 512, overlap: 64, temporal_size: 64, temporal_overlap: 16 } };
  n.create = { class_type: "CreateVideo", inputs: { images: ["decode", 0], fps: fps, bit_depth: "auto", color_space: "sRGB", chroma_subsampling: "auto", codec: "none" } };
  n.save = { class_type: "SaveVideo", inputs: { video: ["create", 0], filename_prefix: "v38/" + name, format: "auto" } };
  return n;
}

if (require.main === module) {
  const a = process.argv[2];
  if (!a) { console.log("efeitos:", Object.keys(EFFECTS).join(", ")); process.exit(0); }
  const opts = {};
  for (const kv of process.argv.slice(3)) { const [k, v] = kv.split("="); opts[k] = isNaN(+v) ? v : +v; }
  console.log(JSON.stringify(build(a, opts), null, 1));
}
module.exports = { build, EFFECTS };
