# Copyright © 2026 Mythara Labs LLC. All rights reserved.

"""
Simple PNG export using inline SVG rendering.
Creates placeholder PNGs with text labels (for layout mockups).
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Paths
SVG_DIR = Path(__file__).parent / "assets" / "glyphs"
PNG_DIR = Path(__file__).parent / "assets" / "glyphs_png"

# Sizes and colors
SIZES = [32, 64, 128, 256]
COLORS = {
    "dark": (10, 10, 10, 255),       # Near-black
    "light": (250, 250, 250, 255),   # Near-white
    "brand": (59, 130, 246, 255)     # Blue accent
}

# Glyph names
GLYPHS = [
    "ssip_audit",
    "engine_subscription_monthly",
    "engine_subscription_annual",
    "enterprise_license",
    "custom_clause_dev",
    "training_onboarding",
    "voip_bot_license"
]


def create_png_placeholder(name: str, size: int, color: tuple, output_path: Path):
    """Create a simple PNG placeholder with the glyph icon representation."""
    
    # Create image with transparent background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Icon representations (simple geometric shapes)
    margin = size // 8
    
    if "audit" in name:
        # Shield shape
        draw.polygon([
            (size//2, margin),
            (size-margin, size//3),
            (size-margin, 2*size//3),
            (size//2, size-margin),
            (margin, 2*size//3),
            (margin, size//3)
        ], fill=color)
        # Checkmark
        draw.line((size//3, size//2, size//2, 2*size//3), fill=(0,0,0,0), width=size//20)
        draw.line((size//2, 2*size//3, 3*size//4, size//3), fill=(0,0,0,0), width=size//20)
    
    elif "monthly" in name:
        # Calendar
        draw.rectangle((margin, margin+size//8, size-margin, size-margin), outline=color, width=size//20)
        draw.line((margin, margin+size//4, size-margin, margin+size//4), fill=color, width=size//20)
        # Hex emblem
        cx, cy = size//2, 3*size//5
        r = size//8
        draw.regular_polygon((cx, cy, r), 6, fill=color)
    
    elif "annual" in name:
        # Calendar with laurel
        draw.rectangle((margin, margin+size//8, size-margin, size-margin), outline=color, width=size//20)
        draw.line((margin, margin+size//4, size-margin, margin+size//4), fill=color, width=size//20)
        # Circle (laurel ring)
        draw.ellipse((size//3, size//3, 2*size//3, 2*size//3), outline=color, width=size//20)
    
    elif "enterprise" in name:
        # Shield with crown
        draw.polygon([
            (size//2, margin),
            (size-margin, size//3),
            (size-margin, 3*size//4),
            (size//2, size-margin-size//8),
            (margin, 3*size//4),
            (margin, size//3)
        ], fill=color)
        # Crown
        draw.polygon([
            (size//3, margin+size//6),
            (size//2, margin+size//12),
            (2*size//3, margin+size//6),
            (2*size//3, margin+size//4),
            (size//3, margin+size//4)
        ], fill=(255,215,0,255))
    
    elif "custom" in name or "clause" in name:
        # Gear
        cx, cy = 2*size//3, size//3
        r = size//6
        draw.ellipse((cx-r, cy-r, cx+r, cy+r), outline=color, width=size//20)
        # Quill pen
        draw.line((margin, 3*size//4, size//2, 2*size//3), fill=color, width=size//15)
    
    elif "training" in name or "onboarding" in name:
        # Graduation cap
        draw.polygon([
            (margin, size//2),
            (size//2, size//3),
            (size-margin, size//2),
            (size//2, 2*size//3)
        ], fill=color)
        # Tassel
        draw.line((size-margin, size//2, size-margin, 3*size//4), fill=color, width=size//30)
        draw.ellipse((size-margin-size//30, 3*size//4, size-margin+size//30, 3*size//4+size//15), fill=color)
    
    elif "voip" in name:
        # Phone handset (simplified)
        draw.arc((margin, margin, size//2, size//2), 45, 225, fill=color, width=size//15)
        # Voice waves
        draw.arc((size//2, size//3, 3*size//4, 2*size//3), 270, 90, fill=color, width=size//25)
        draw.arc((3*size//5, size//4, 5*size//6, 3*size//4), 270, 90, fill=color, width=size//25)
    
    else:
        # Default: circle
        draw.ellipse((margin, margin, size-margin, size-margin), fill=color)
    
    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, 'PNG')


def export_all_glyphs():
    """Export all glyphs as PNG placeholders."""
    
    print("🎨 Exporting PNG glyphs (simple geometric versions)...\n")
    
    total = len(GLYPHS) * len(COLORS) * len(SIZES)
    current = 0
    
    for glyph_name in GLYPHS:
        for color_name, color_value in COLORS.items():
            for size in SIZES:
                output_path = PNG_DIR / color_name / str(size) / f"{glyph_name}.png"
                
                try:
                    create_png_placeholder(glyph_name, size, color_value, output_path)
                    current += 1
                    print(f"✓ [{current}/{total}] {glyph_name} @ {size}px ({color_name})")
                except Exception as e:
                    print(f"✗ Failed: {glyph_name} @ {size}px ({color_name}) - {e}")
    
    print(f"\n🎉 Exported {current}/{total} PNG files to {PNG_DIR}")
    print("\nDirectory structure:")
    print(f"  {PNG_DIR}/")
    print(f"    dark/     (near-black - for light backgrounds)")
    print(f"    light/    (near-white - for dark backgrounds)")
    print(f"    brand/    (blue accent - for highlights)")
    for size in SIZES:
        print(f"      {size}/")
    
    print("\nNote: These are simplified geometric versions for layout mockups.")
    print("For production, use the SVG files directly (scalable & precise).")


if __name__ == "__main__":
    export_all_glyphs()
