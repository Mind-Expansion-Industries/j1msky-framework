#!/usr/bin/env python3
"""Generate a simple icon for the app"""

try:
    from PIL import Image, ImageDraw
    
    # Create 64x64 icon
    img = Image.new('RGBA', (64, 64), (26, 26, 46, 255))  # Dark blue background
    draw = ImageDraw.Draw(img)
    
    # Draw thermometer-like shape
    # Bulb at bottom
    draw.ellipse([20, 44, 44, 60], fill=(0, 212, 255, 255))  # Cyan bulb
    
    # Stem
    draw.rectangle([28, 12, 36, 48], fill=(0, 212, 255, 255))
    
    # Temperature lines
    draw.line([(18, 16), (24, 16)], fill=(255, 255, 255, 200), width=2)
    draw.line([(18, 24), (24, 24)], fill=(255, 255, 255, 200), width=2)
    draw.line([(18, 32), (24, 32)], fill=(255, 255, 255, 200), width=2)
    
    img.save('/home/m1ndb0t/Desktop/J1MSKY/apps/thermal-wallpaper-studio/assets/icon.png')
    print("✅ Icon created")
    
except ImportError:
    # Create a simple SVG instead
    svg = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="64" height="64" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
  <rect width="64" height="64" fill="#1a1a2e"/>
  <circle cx="32" cy="52" r="10" fill="#00d4ff"/>
  <rect x="28" y="12" width="8" height="40" fill="#00d4ff"/>
  <line x1="18" y1="20" x2="24" y2="20" stroke="white" stroke-width="2"/>
  <line x1="18" y1="28" x2="24" y2="28" stroke="white" stroke-width="2"/>
  <line x1="18" y1="36" x2="24" y2="36" stroke="white" stroke-width="2"/>
</svg>'''
    
    with open('/home/m1ndb0t/Desktop/J1MSKY/apps/thermal-wallpaper-studio/assets/icon.svg', 'w') as f:
        f.write(svg)
    print("✅ SVG icon created")
