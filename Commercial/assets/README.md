# Mythara Glyph Assets

**Copyright © 2025 Herbert Velez Jr. All rights reserved.**

## Directory Structure

```
Commercial/assets/
├── README.md            # This file
└── glyphs/              # Original SVG files (scalable, production-ready)
    ├── ssip_audit.svg
    ├── engine_subscription_monthly.svg
    ├── engine_subscription_annual.svg
    ├── enterprise_license.svg
    ├── custom_clause_dev.svg
    ├── training_onboarding.svg
    └── voip_bot_license.svg
```

> **Note:** PNG exports (`glyphs_png/dark|light|brand/`) are not present on
> disk — they were planned but never generated. SVG is the current source of
> truth. Generate PNGs with `Commercial/export_glyph_pngs_simple.py` if a
> PowerPoint/email fallback is needed.

## Usage

### Web / Markdown (Recommended)
Use SVG files for best quality:
```html
<img src="./assets/glyphs/ssip_audit.svg" width="64" height="64" alt="SSIP Audit" />
```

### PowerPoint / Keynote
Export PNGs first (see below), then choose a color variant:
- **Light backgrounds:** dark variant
- **Dark backgrounds:** light variant
- **Brand highlights:** brand variant

### Email Signatures / HTML Emails
Use PNG files once exported (many email clients don't support SVG):
```html
<img src="https://yourdomain.com/assets/glyphs_png/dark/64/ssip_audit.png" width="64" height="64" alt="SSIP Audit" />
```

## Glyph Reference

| Glyph | File Name | Use Case |
|-------|-----------|----------|
| ![Audit](./glyphs/ssip_audit.svg) | `ssip_audit` | SSIP Compliance Audit |
| ![Monthly](./glyphs/engine_subscription_monthly.svg) | `engine_subscription_monthly` | Monthly Subscription |
| ![Annual](./glyphs/engine_subscription_annual.svg) | `engine_subscription_annual` | Annual Subscription |
| ![Enterprise](./glyphs/enterprise_license.svg) | `enterprise_license` | Enterprise License |
| ![Custom](./glyphs/custom_clause_dev.svg) | `custom_clause_dev` | Custom Clause Development |
| ![Training](./glyphs/training_onboarding.svg) | `training_onboarding` | Training & Onboarding |
| ![VoIP](./glyphs/voip_bot_license.svg) | `voip_bot_license` | VoIP Bot License (planned, not built) |

## Color Variants (when exporting PNGs)

### Dark (#0A0A0A)
Best for: Light backgrounds, documents, white slides
- Near-black color ensures good contrast
- Professional appearance for business materials

### Light (#FAFAFA)
Best for: Dark backgrounds, dark mode websites, black slides
- Near-white color for visibility on dark surfaces
- Modern aesthetic for tech presentations

### Brand (#3B82F6)
Best for: Highlights, CTAs, featured items
- Blue accent matches Mythara brand palette
- Use sparingly for emphasis

## Generating PNGs

```powershell
# From the Commercial/ directory:
# Edit export_glyph_pngs_simple.py
# Modify SIZES = [32, 64, 128, 256] or COLORS dict
# Then run:
py -3.11 export_glyph_pngs_simple.py
```

Output lands in `Commercial/assets/glyphs_png/` (dark/light/brand × 32/64/128/256).

## Technical Specs

### SVG Files
- ViewBox: 256×256
- Stroke: `currentColor` (inherits parent color)
- Fill: `none`
- Stroke-width: 12px
- Style: Mono-line, rounded caps/joins
- Accessibility: `role="img"` and `aria-label` attributes

### PNG Files (once generated)
- Format: PNG with transparency (RGBA)
- Sizes: 32×32, 64×64, 128×128, 256×256
- DPI: 96 (standard web resolution)
- Compression: Optimized for web use

## Notes

- **SVG is preferred** for web, apps, and high-resolution printing
- **PNG is fallback** for systems without SVG support (PowerPoint, email, older browsers)
- For production materials, always use SVG when possible

## License

All glyphs are proprietary assets of Herbert Velez Jr. (Mythara Labs LLC —
formation filing attempted with the Colorado Secretary of State on 2026-09-27 — not confirmed;
entity not yet formed; sole member Herbert Velez Jr.). Do not distribute outside of
Mythara commercial materials.
