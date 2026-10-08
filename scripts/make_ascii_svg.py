"""Turn an image into a monochrome ASCII SVG that prints row by row (SMIL, plays once).

    python scripts/make_ascii_svg.py                 # built-in monogram + rising-bars emblem
    python scripts/make_ascii_svg.py --photo me.jpg  # your own photo instead

Photos get autocontrast + histogram equalisation first, so a flat-lit face still has
highlights. Background removal is optional: run `pip install rembg` and pass --cutout.
"""
import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

from theme import DIM, FG, GREEN, HANDLE, esc, frame

ROOT = Path(__file__).resolve().parent.parent
RAMP = " .`:-=+*cs#%@"  # dark -> bright on a dark panel: space clears the background
COLS, ROWS = 64, 34
CW, LH = 5.7, 10.6  # char advance / line height in the SVG
W, H = 370, 456
FONT_BOLD = ["C:/Windows/Fonts/ariblk.ttf", "C:/Windows/Fonts/arialbd.ttf", "DejaVuSans-Bold.ttf"]


def load_font(size: int) -> ImageFont.FreeTypeFont:
    for p in FONT_BOLD:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default()


def emblem() -> Image.Image:
    """512x544 greyscale: bold wordmark over a rising bar chart with a trend line."""
    img = Image.new("L", (512, 544), 0)
    d = ImageDraw.Draw(img)
    f = load_font(150)
    layer = Image.new("L", (900, 260), 0)
    ImageDraw.Draw(layer).text((20, 10), "MUSAB", font=f, fill=255)
    word = layer.crop(layer.getbbox())
    word = word.resize((484, int(word.height * 484 / word.width * 1.7)), Image.LANCZOS)  # tall letters survive 1:2 cells
    img.paste(word, (14, 34))
    wm_bottom = 34 + word.height
    d.line((14, wm_bottom + 20, 498, wm_bottom + 20), fill=95, width=4)
    top, base = wm_bottom + 54, 512
    for k in range(1, 5):  # faint gridlines give the chart texture
        y = base - k * (base - top) / 4
        d.line((14, y, 498, y), fill=42, width=2)
    heights = [0.22, 0.30, 0.26, 0.41, 0.36, 0.52, 0.47, 0.63, 0.58, 0.76, 0.71, 0.92]
    n, gap = len(heights), 12
    bw = (484 - gap * (n - 1)) / n
    pts = []
    for i, h in enumerate(heights):
        x = 14 + i * (bw + gap)
        y = base - h * (base - top)
        d.rectangle((x, y, x + bw, base), fill=int(105 + 150 * i / (n - 1)))
        pts.append((x + bw / 2, y - 22))
    d.line(pts, fill=255, width=5, joint="curve")
    for x, y in pts:
        d.ellipse((x - 7, y - 7, x + 7, y + 7), fill=255)
    d.line((14, base + 4, 498, base + 4), fill=170, width=3)
    glow = img.filter(ImageFilter.GaussianBlur(7))
    return Image.fromarray(np.maximum(np.asarray(img), (np.asarray(glow) * 0.5).astype(np.uint8)))

def from_photo(path: str, cutout: bool) -> Image.Image:
    im = Image.open(path).convert("RGB")
    if cutout:
        from rembg import remove  # optional heavy dependency
        im = remove(im)
        bg = Image.new("RGBA", im.size, (0, 0, 0, 255))
        im = Image.alpha_composite(bg, im.convert("RGBA")).convert("RGB")
    g = ImageOps.equalize(ImageOps.autocontrast(im.convert("L"), cutoff=2))
    g = ImageOps.fit(g, (512, 544), method=Image.LANCZOS, centering=(0.5, 0.35))
    return g


def to_rows(img: Image.Image) -> list[str]:
    small = np.asarray(img.resize((COLS, ROWS), Image.BOX), dtype=float) / 255.0
    small = np.clip((small - 0.04) / 0.9, 0, 1) ** 0.85
    idx = (small * (len(RAMP) - 1)).round().astype(int)
    return ["".join(RAMP[i] for i in row) for row in idx]


def build(rows: list[str]) -> str:
    top = 54
    defs, body = "", []
    for i, row in enumerate(rows):
        stripped = row.rstrip()
        lead = len(stripped) - len(stripped.lstrip())
        text = stripped.lstrip()
        if not text:
            continue
        x, y = 10 + lead * CW + (W - 20 - COLS * CW) / 2, top + i * LH
        w = len(text) * CW
        t0 = round(0.35 + i * 0.07, 2)
        defs += (
            f'<clipPath id="r{i}"><rect x="{x:.1f}" y="{y - LH + 2:.1f}" width="0" height="{LH}">'
            f'<animate attributeName="width" from="0" to="{w:.1f}" dur="0.55s" begin="{t0}s" fill="freeze"/></rect></clipPath>'
        )
        body.append(
            f'<text x="{x:.1f}" y="{y:.1f}" font-size="9.4" fill="{FG}" textLength="{w:.1f}" '
            f'lengthAdjust="spacingAndGlyphs" clip-path="url(#r{i})" xml:space="preserve">{esc(text)}</text>'
        )
        body.append(  # block cursor riding the wipe edge, gone when the row is done
            f'<rect x="{x:.1f}" y="{y - LH + 3:.1f}" width="{CW:.1f}" height="{LH - 2}" fill="{GREEN}" opacity="0">'
            f'<animate attributeName="x" from="{x:.1f}" to="{x + w:.1f}" dur="0.55s" begin="{t0}s" fill="freeze"/>'
            f'<animate attributeName="opacity" values="0;0.9;0.9;0" keyTimes="0;0.02;0.97;1" dur="0.55s" begin="{t0}s" fill="freeze"/></rect>'
        )
    prompt = f'<text x="14" y="{H - 16}" font-size="10.5" fill="{DIM}">{HANDLE} ~ $ cat avatar.ascii</text>'
    return frame(W, H, "avatar.ascii", prompt + "\n" + "\n".join(body), defs=defs)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--photo")
    ap.add_argument("--cutout", action="store_true")
    a = ap.parse_args()
    img = from_photo(a.photo, a.cutout) if a.photo else emblem()
    rows = to_rows(img)
    (ROOT / "avatar-ascii.svg").write_text(build(rows), encoding="utf-8")
    print("\n".join(rows))


if __name__ == "__main__":
    main()



