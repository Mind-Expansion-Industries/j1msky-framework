#!/usr/bin/env python3
"""
Set any image as desktop wallpaper on Raspberry Pi (Labwc/LXDE)
Usage: python3 set_wallpaper.py /path/to/image.jpg
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

def detect_desktop():
    """Detect which desktop environment is running"""
    # Check for Labwc (Wayland)
    result = subprocess.run(['pgrep', '-x', 'labwc'], capture_output=True)
    if result.returncode == 0:
        return 'labwc'
    
    # Check for LXDE
    result = subprocess.run(['pgrep', '-x', 'lxsession'], capture_output=True)
    if result.returncode == 0:
        return 'lxde'
    
    # Check for Openbox
    result = subprocess.run(['pgrep', '-x', 'openbox'], capture_output=True)
    if result.returncode == 0:
        return 'openbox'
    
    return 'unknown'

def set_wallpaper_labwc(image_path):
    """Set wallpaper on Labwc"""
    env = os.environ.copy()
    env['DISPLAY'] = ':0'
    env['XDG_RUNTIME_DIR'] = '/run/user/1000'
    
    methods = [
        ['pcmanfm', '--set-wallpaper', str(image_path)],
        ['pcmanfm', '-w', str(image_path)],
    ]
    
    for cmd in methods:
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        if result.returncode == 0:
            return True
    
    return False

def set_wallpaper_lxde(image_path):
    """Set wallpaper on LXDE"""
    env = os.environ.copy()
    env['DISPLAY'] = ':0'
    
    result = subprocess.run(
        ['pcmanfm', '--set-wallpaper', str(image_path)],
        capture_output=True,
        text=True,
        env=env
    )
    return result.returncode == 0

def set_wallpaper_openbox(image_path):
    """Set wallpaper on Openbox using feh or nitrogen"""
    env = os.environ.copy()
    env['DISPLAY'] = ':0'
    
    # Try feh
    if subprocess.run(['which', 'feh'], capture_output=True).returncode == 0:
        result = subprocess.run(
            ['feh', '--bg-scale', str(image_path)],
            capture_output=True,
            text=True,
            env=env
        )
        return result.returncode == 0
    
    # Try nitrogen
    if subprocess.run(['which', 'nitrogen'], capture_output=True).returncode == 0:
        result = subprocess.run(
            ['nitrogen', '--set-zoom-fill', str(image_path)],
            capture_output=True,
            text=True,
            env=env
        )
        return result.returncode == 0
    
    return False

def main():
    parser = argparse.ArgumentParser(description='Set desktop wallpaper')
    parser.add_argument('image', help='Path to image file')
    parser.add_argument('--desktop', help='Force desktop type (labwc/lxde/openbox)')
    args = parser.parse_args()
    
    image_path = Path(args.image)
    
    if not image_path.exists():
        print(f"❌ Image not found: {image_path}")
        sys.exit(1)
    
    # Detect or use specified desktop
    desktop = args.desktop or detect_desktop()
    
    print(f"🖼️  Setting wallpaper...")
    print(f"   Desktop: {desktop}")
    print(f"   Image: {image_path}")
    
    # Set wallpaper based on desktop
    if desktop == 'labwc':
        success = set_wallpaper_labwc(image_path)
    elif desktop == 'lxde':
        success = set_wallpaper_lxde(image_path)
    elif desktop == 'openbox':
        success = set_wallpaper_openbox(image_path)
    else:
        # Try all methods
        success = (set_wallpaper_labwc(image_path) or 
                  set_wallpaper_lxde(image_path) or 
                  set_wallpaper_openbox(image_path))
    
    if success:
        print(f"✅ Wallpaper set!")
    else:
        print(f"❌ Failed to set wallpaper")
        print(f"   Try manually: pcmanfm --set-wallpaper {image_path}")
        sys.exit(1)

if __name__ == '__main__':
    main()
