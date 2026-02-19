#!/usr/bin/env python3
"""
Generate AI wallpaper using Replicate API and set it as desktop background
Usage: python3 generate_wallpaper.py "your prompt here" [--model openai/gpt-image-1.5]
"""

import argparse
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

def check_replicate_token():
    """Check if API token is set"""
    token = os.environ.get('REPLICATE_API_TOKEN')
    if not token:
        print("❌ REPLICATE_API_TOKEN not set!")
        print("   Run: export REPLICATE_API_TOKEN=REPLICATE_API_TOKEN_PLACEHOLDER")
        return False
    return True

def install_replicate():
    """Install replicate package if needed"""
    try:
        import replicate
        return True
    except ImportError:
        print("📦 Installing replicate package...")
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', 'replicate', '--break-system-packages'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ replicate installed")
            return True
        else:
            print(f"❌ Failed to install: {result.stderr}")
            return False

def generate_image(prompt, model="openai/gpt-image-1.5", quality="high"):
    """Generate image using Replicate"""
    try:
        import replicate
        
        print(f"🎨 Generating image with {model}...")
        print(f"   Prompt: {prompt}")
        
        input_params = {
            "prompt": prompt,
            "quality": quality
        }
        
        output = replicate.run(
            model,
            input=input_params
        )
        
        return output
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        return None

def download_image(url, output_path):
    """Download image from URL"""
    import urllib.request
    
    try:
        print(f"📥 Downloading...")
        urllib.request.urlretrieve(url, output_path)
        print(f"✅ Saved to: {output_path}")
        return True
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return False

def set_labwc_wallpaper(image_path):
    """Set wallpaper on Labwc (Wayland) desktop"""
    try:
        # Method 1: pcmanfm
        env = os.environ.copy()
        env['DISPLAY'] = ':0'
        env['XDG_RUNTIME_DIR'] = '/run/user/1000'
        
        result = subprocess.run(
            ['pcmanfm', '--set-wallpaper', str(image_path)],
            capture_output=True,
            text=True,
            env=env
        )
        
        if result.returncode == 0:
            print(f"🖼️  Wallpaper set!")
            return True
        else:
            # Method 2: Direct pcmanfm call
            result = subprocess.run(
                ['pcmanfm', '-w', str(image_path)],
                capture_output=True,
                text=True,
                env=env
            )
            if result.returncode == 0:
                print(f"🖼️  Wallpaper set!")
                return True
                
        print(f"⚠️  Could not set wallpaper automatically")
        print(f"   Image saved to: {image_path}")
        print(f"   Set manually: pcmanfm --set-wallpaper {image_path}")
        return False
        
    except Exception as e:
        print(f"⚠️  Wallpaper setting failed: {e}")
        print(f"   Image saved to: {image_path}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Generate AI wallpaper')
    parser.add_argument('prompt', nargs='?', 
                       default="cyberpunk Raspberry Pi setup, glowing circuits, neon blue and purple, dark background, high detail, 4k wallpaper",
                       help='Image generation prompt')
    parser.add_argument('--model', default='openai/gpt-image-1.5',
                       help='Replicate model to use')
    parser.add_argument('--quality', default='high',
                       help='Image quality (high/medium/low)')
    parser.add_argument('--output-dir', default='/home/m1ndb0t/Pictures/Wallpapers',
                       help='Output directory')
    parser.add_argument('--no-set', action='store_true',
                       help='Generate but don\'t set as wallpaper')
    args = parser.parse_args()
    
    # Check token
    if not check_replicate_token():
        sys.exit(1)
    
    # Install replicate if needed
    if not install_replicate():
        sys.exit(1)
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate timestamp for filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Generate image
    print("\n" + "="*60)
    print("🎨 AI WALLPAPER GENERATOR")
    print("="*60 + "\n")
    
    output = generate_image(args.prompt, args.model, args.quality)
    
    if not output:
        print("❌ Generation failed")
        sys.exit(1)
    
    # Handle output (could be URL or file object)
    if isinstance(output, list) and len(output) > 0:
        # Get URL from output object
        if hasattr(output[0], 'url'):
            image_url = output[0].url
        else:
            image_url = str(output[0])
    elif hasattr(output, 'url'):
        image_url = output.url
    else:
        image_url = str(output)
    
    # Download image
    ext = ".webp" if ".webp" in image_url else ".png"
    output_path = output_dir / f"wallpaper_{timestamp}{ext}"
    
    if not download_image(image_url, output_path):
        sys.exit(1)
    
    # Set as wallpaper
    if not args.no_set:
        set_labwc_wallpaper(output_path)
    else:
        print(f"💾 Image saved (not setting as wallpaper)")
        print(f"   Path: {output_path}")
    
    print("\n✨ Done!")
    return output_path

if __name__ == '__main__':
    main()
