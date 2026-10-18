# Copyright © 2026 Mythara Labs LLC. All rights reserved.

"""
Export Mythara glyphs as PNGs at multiple sizes and color variants.

Generates:
- 32x32, 64x64, 128x128, 256x256 PNGs
- Color variants: dark (#0A0A0A), light (#FAFAFA), brand accent (#3B82F6)
"""

import os
import re
from pathlib import Path

# Try multiple SVG renderers
try:
    from cairosvg import svg2png
    RENDERER = "cairosvg"
except ImportError:
    try:
        from svglib.svglib import svg2rlg
        from reportlab.graphics import renderPM
        RENDERER = "svglib"
    except ImportError:
        RENDERER = None
        print("⚠️  No SVG renderer found. Install cairosvg or svglib:")
        print("   py -3.11 -m pip install cairosvg")
        print("   OR")
        print("   py -3.11 -m pip install svglib reportlab")

# Paths
SVG_DIR = Path(__file__).parent / "assets" / "glyphs"
PNG_DIR = Path(__file__).parent / "assets" / "glyphs_png"

# Sizes to generate
SIZES = [32, 64, 128, 256]

# Color variants (replace currentColor in SVG)
COLORS = {
    "dark": "#0A0A0A",      # Near-black for light backgrounds
    "light": "#FAFAFA",     # Near-white for dark backgrounds
    "brand": "#3B82F6"      # Blue accent (brand color)
}


def replace_color(svg_content: str, color: str) -> str:
    """Replace currentColor with specific color."""
    return svg_content.replace('stroke="currentColor"', f'stroke="{color}"')


def export_png_cairosvg(svg_path: Path, output_path: Path, size: int, color: str):
    """Export PNG using cairosvg."""
    from cairosvg import svg2png
    
    # Read and modify SVG
    svg_content = svg_path.read_text()
    svg_content = replace_color(svg_content, color)
    
    # Export
    svg2png(
        bytestring=svg_content.encode('utf-8'),
        write_to=str(output_path),
        output_width=size,
        output_height=size
    )


def export_png_svglib(svg_path: Path, output_path: Path, size: int, color: str):
    """Export PNG using svglib."""
    from svglib.svglib import svg2rlg
    from reportlab.graphics import renderPM
    
    # Read and modify SVG
    svg_content = svg_path.read_text()
    svg_content = replace_color(svg_content, color)
    
    # Save temp modified SVG
    temp_svg = svg_path.parent / f"temp_{svg_path.name}"
    temp_svg.write_text(svg_content)
    
    # Convert
    drawing = svg2rlg(str(temp_svg))
    if drawing:
        scale = size / 256  # Original viewBox is 256x256
        drawing.width = size
        drawing.height = size
        drawing.scale(scale, scale)
        renderPM.drawToFile(drawing, str(output_path), fmt="PNG")
    
    # Cleanup
    temp_svg.unlink()


def export_all_glyphs():
    """Export all glyphs as PNGs."""
    
    if not RENDERER:
        print("❌ Cannot export PNGs without SVG renderer")
        return
    
    print(f"🎨 Using {RENDERER} to export PNGs...\n")
    
    # Create output directories
    for color_name in COLORS.keys():
        for size in SIZES:
            dir_path = PNG_DIR / color_name / str(size)
            dir_path.mkdir(parents=True, exist_ok=True)
    
    # Find all SVG files
    svg_files = list(SVG_DIR.glob("*.svg"))
    
    if not svg_files:
        print(f"❌ No SVG files found in {SVG_DIR}")
        return
    
    total = len(svg_files) * len(COLORS) * len(SIZES)
    current = 0
    
    # Export each glyph
    for svg_path in svg_files:
        glyph_name = svg_path.stem
        
        for color_name, color_value in COLORS.items():
            for size in SIZES:
                output_path = PNG_DIR / color_name / str(size) / f"{glyph_name}.png"
                
                try:
                    if RENDERER == "cairosvg":
                        export_png_cairosvg(svg_path, output_path, size, color_value)
                    elif RENDERER == "svglib":
                        export_png_svglib(svg_path, output_path, size, color_value)
                    
                    current += 1
                    print(f"✓ [{current}/{total}] {glyph_name} @ {size}px ({color_name})")
                
                except Exception as e:
                    print(f"✗ Failed: {glyph_name} @ {size}px ({color_name}) - {e}")
    
    print(f"\n🎉 Exported {current}/{total} PNG files to {PNG_DIR}")
    print("\nDirectory structure:")
    print(f"  {PNG_DIR}/")
    print(f"    dark/     (#{COLORS['dark']} - for light backgrounds)")
    print(f"    light/    (#{COLORS['light']} - for dark backgrounds)")
    print(f"    brand/    (#{COLORS['brand']} - accent color)")
    for size in SIZES:
        print(f"      {size}/")


if __name__ == "__main__":
    export_all_glyphs()
