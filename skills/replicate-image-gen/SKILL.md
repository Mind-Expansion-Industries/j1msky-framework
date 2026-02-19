---
name: replicate-image-gen
description: Generate AI images using Replicate API (GPT Image 1.5, Flux, etc.) and set them as desktop wallpapers. Use when creating custom wallpapers, generating artwork, or automating image generation tasks on Raspberry Pi.
---

# Replicate Image Generation

Generate AI images and set them as desktop backgrounds using Replicate's API.

## Quick Start

```bash
# Generate a wallpaper
python3 scripts/generate_wallpaper.py "cyberpunk city at night, neon lights, rain"

# Generate with specific style
python3 scripts/generate_wallpaper.py "retro wave sunset, palm trees, purple sky" --style digital-art
```

## Environment Setup

API token must be set:
```bash
export REPLICATE_API_TOKEN=REPLICATE_API_TOKEN_PLACEHOLDER
```

Add to `~/.bashrc` to persist:
```bash
echo 'export REPLICATE_API_TOKEN=REPLICATE_API_TOKEN_PLACEHOLDER' >> ~/.bashrc
```

## Available Models

| Model | Best For | Cost |
|-------|----------|------|
| `openai/gpt-image-1.5` | Photorealistic, detailed | Higher |
| `black-forest-labs/flux-schnell` | Fast generation | Lower |
| `black-forest-labs/flux-dev` | High quality art | Medium |
| `stability-ai/stable-diffusion-3` | General purpose | Medium |

## Scripts

- `generate_wallpaper.py` — Generate and auto-set wallpaper
- `batch_generate.py` — Generate multiple images
- `set_wallpaper.py` — Set any image as wallpaper (Labwc/LXDE)

## Labwc Wallpaper

Labwc uses `pcmanfm` for desktop wallpapers:
```bash
# Set wallpaper
pcmanfm --set-wallpaper /path/to/image.jpg

# Or modify directly
export DISPLAY=:0
pcmanfm -w /path/to/image.jpg
```
