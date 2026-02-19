# 🌡️ Thermal Wallpaper Studio

AI wallpaper generator for Raspberry Pi that reacts to your CPU temperature.

## Features

- 🌡️ **Thermal-Reactive**: Automatically generates cold-themed art when cool, hot-themed when warm
- ⚡ **Quick Generate**: Type a prompt and get instant wallpapers  
- 🎲 **I'm Feeling Lucky**: Random prompt generation
- 📊 **Cost Tracking**: Monitor your Replicate API usage
- 🎨 **Beautiful UI**: Dark cyberpunk-themed interface

## Launch

Double-click **Thermal Wallpaper Studio** on your desktop, or run:
```bash
~/Desktop/J1MSKY/apps/thermal-wallpaper-studio/launch.sh
```

## How It Works

| Temperature | Theme | Colors |
|-------------|-------|--------|
| < 60°C | Cold | Icy blues, arctic scenes |
| 60-75°C | Neutral | Balanced nature, sunsets |
| > 75°C | Hot | Fiery reds, lava, intensity |

Auto-generate mode creates new wallpapers when temp crosses thresholds.

## Files

- `src/app.py` - Main application
- `launch.sh` - Launcher script
- `assets/icon.png` - App icon

## Requirements

- Raspberry Pi with desktop
- Replicate API token (already configured)
- `replicate` Python package
