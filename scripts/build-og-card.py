#!/usr/bin/env python3
"""Build the site's default Open Graph card (1200x630 PNG).

Editorial style matching the site CSS — paper background, burnt-sienna
accent rule, serif title, sans display eyebrow + footer. Output:
`assets/og-default.png` (1200x630, sRGB).

Run:
    python3 scripts/build-og-card.py

The card is committed to the repo so deployment doesn't depend on this
running. Re-run any time the title or accent color changes.
"""

from __future__ import annotations
import pathlib
from PIL import Image, ImageDraw, ImageFont

# Site palette — keep in sync with assets/css/style.css
BG = (251, 250, 247)        # --c-bg
INK = (26, 22, 20)           # --c-ink
INK_SOFT = (74, 70, 64)      # --c-ink-soft
INK_MUTED = (118, 113, 106)  # --c-ink-muted
ACCENT = (138, 51, 36)       # --c-accent
RULE = (227, 221, 210)       # --c-rule

W, H = 1200, 630


def find_font(candidates: list[str], size: int) -> ImageFont.FreeTypeFont:
    """Return the first usable system font from a candidate list."""
    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size)
        except OSError:
            continue
    return ImageFont.load_default(size=size)  # type: ignore[arg-type]


SERIF_CANDIDATES = [
    # macOS
    "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
    "/System/Library/Fonts/Times.ttc",
    # Linux
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
]
SANS_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
]


def main() -> int:
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Vertical accent rule on the left, matching .featured-card aesthetic
    draw.rectangle([(64, 64), (68, H - 64)], fill=ACCENT)

    # Eyebrow — small uppercase tracking
    eyebrow_font = find_font(SANS_CANDIDATES, 22)
    draw.text(
        (110, 90),
        "REPORTS",
        font=eyebrow_font,
        fill=ACCENT,
        spacing=6,
    )

    # Title — large serif
    title_font = find_font(SERIF_CANDIDATES, 84)
    draw.text(
        (110, 140),
        "Long-form technical",
        font=title_font,
        fill=INK,
    )
    draw.text(
        (110, 240),
        "reports on AI models,",
        font=title_font,
        fill=INK,
    )
    draw.text(
        (110, 340),
        "systems, and tooling.",
        font=title_font,
        fill=INK,
    )

    # Hairline separator above footer
    draw.line(
        [(110, H - 110), (W - 110, H - 110)],
        fill=RULE,
        width=1,
    )

    # Footer — sans, ink-soft
    footer_font = find_font(SANS_CANDIDATES, 26)
    draw.text(
        (110, H - 88),
        "1011-a.github.io/reports",
        font=footer_font,
        fill=INK_SOFT,
    )

    # Right-aligned note on the footer
    note = "Primary-source-cited · MIT"
    note_w = draw.textlength(note, font=footer_font)
    draw.text(
        (W - 110 - note_w, H - 88),
        note,
        font=footer_font,
        fill=INK_MUTED,
    )

    out = pathlib.Path("assets/og-default.png")
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "PNG", optimize=True)
    size_kb = out.stat().st_size / 1024
    print(f"wrote {out} ({size_kb:.0f} KB, {W}x{H})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
