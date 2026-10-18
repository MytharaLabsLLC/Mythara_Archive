# Copyright © 2026 Mythara Labs LLC. All rights reserved.

"""
Export Mythara SVG glyphs to PNG at multiple sizes and color variants.

- Inputs: Commercial/assets/glyphs/*.svg (stroke="currentColor")
- Outputs: Commercial/assets/glyphs/png/{size}/{variant}/{name}.png

Variants (editable):
- dark:   #0A0A0A  (for light backgrounds)
- light:  #F3F4F6  (for dark backgrounds)
- accent: #2B6CB0  (brand accent blue)

Requires: cairosvg
"""

import os
from pathlib import Path
import re

try:
    import cairosvg
except ImportError:
    raise SystemExit("cairosvg not installed. Run: pip install cairosvg")

ROOT = Path(__file__).resolve().parents[1]
SVG_DIR = ROOT / "assets" / "glyphs"
OUT_DIR = SVG_DIR / "png"

SIZES = [32, 64, 128, 256]
VARIANTS = {
    "dark": "#0A0A0A",
    "light": "#F3F4F6",
    "accent": "#2B6CB0",
}

# Explicit order for pricing glyphs
GLYPHS = [
    "ssip_audit.svg",
    "engine_subscription_monthly.svg",
    "engine_subscription_annual.svg",
    "enterprise_license.svg",
    "custom_clause_dev.svg",
    "training_onboarding.svg",
    "voip_bot_license.svg",
]


def recolor_svg(svg_text: str, color_hex: str) -> str:
    """Replace currentColor stroke/fill with specific color for export."""
    # Ensure we don't change non-color values
    txt = svg_text
    # If stroke uses currentColor, replace
    txt = txt.replace('stroke="currentColor"', f'stroke="{color_hex}"')
    # Some tools might inherit via CSS; inject a fallback style on root
    if "<svg" in txt and "style=" not in txt.split("\n", 1)[0]:
        txt = txt.replace('<svg ', f'<svg style="color:{color_hex}" ', 1)
    return txt


def export_all():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for name in GLYPHS:
        svg_path = SVG_DIR / name
        if not svg_path.exists():
            print(f"⚠️ Missing SVG: {name}")
            continue

        svg_text = svg_path.read_text(encoding="utf-8")

        base = name.replace('.svg', '')
        for size in SIZES:
            for variant, color in VARIANTS.items():
                target_dir = OUT_DIR / str(size) / variant
                target_dir.mkdir(parents=True, exist_ok=True)
                out_path = target_dir / f"{base}.png"

                colored_svg = recolor_svg(svg_text, color)
                cairosvg.svg2png(bytestring=colored_svg.encode("utf-8"),
                                  write_to=str(out_path),
                                  output_width=size,
                                  output_height=size)
                print(f"✅ {out_path.relative_to(ROOT)}")


if __name__ == "__main__":
    export_all()
