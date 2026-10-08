"""Hand-authored neofetch-style card: info-card.svg. STATIC=1 emits a frozen frame for previews."""
import os
from pathlib import Path

from theme import AMBER, BLUE, DIM, FG, GREEN, HANDLE, MUTED, PINK, esc, frame

ROOT = Path(__file__).resolve().parent.parent
W, H = 490, 456
STATIC = os.environ.get("STATIC") == "1"

# (key, value) rows; None = spacer; ("#", text) = section heading; (">", text) = highlight line
ROWS = [
    ("Role", "Data Science & AI graduate"),
    ("Focus", "BI, analytics engineering, automation"),
    ("Stack", "Power BI / PBIP, DAX, Python, SQL"),
    ("Also", "TypeScript, Next.js, Supabase"),
    ("Method", "source-traced, reconciled, reproducible"),
    None,
    ("#", "highlights"),
    (">", "6.64M contract actions -> 187 MB Power BI model"),
    (">", "3,107 hospitals drawn as SVG inside DAX"),
    (">", "10 quarters of Jordanian unemployment, traced"),
    (">", "96.78% mAP@0.5 aerial car detection (YOLOv8)"),
    (">", "Orbit: realtime PM app, live on Vercel"),
    None,
    ("#", "contact"),
    ("Mail", "musababukaraki1@gmail.com"),
    ("Web", "linkedin.com/in/musababukaraki"),
]
SWATCH = ["#ff7b72", "#e3b341", "#39d353", "#58a6ff", "#bc8cff", "#f778ba", "#8b949e", "#c9d1d9"]


def main() -> None:
    x0, y = 28, 70
    lh = 19.5
    out = [f'<text x="{x0}" y="{y}" font-size="14" font-weight="700" fill="{GREEN}">{HANDLE}</text>']
    y += 8
    out.append(f'<text x="{x0}" y="{y + 10}" font-size="11" fill="{MUTED}">{"-" * 34}</text>')
    y += 10 + lh
    n = 0
    for row in ROWS:
        if row is None:
            y += lh * 0.55
            continue
        k, v = row
        delay = 0.25 + n * 0.11
        anim = "" if STATIC else f' class="ln" style="animation-delay:{delay:.2f}s"'
        if k == "#":
            out.append(f'<text x="{x0}" y="{y:.1f}" font-size="12" fill="{AMBER}"{anim}>[ {esc(v)} ]</text>')
        elif k == ">":
            out.append(
                f'<text x="{x0}" y="{y:.1f}" font-size="12" fill="{FG}"{anim}>'
                f'<tspan fill="{PINK}">&gt;</tspan> {esc(v)}</text>'
            )
        else:
            out.append(
                f'<text x="{x0}" y="{y:.1f}" font-size="12" fill="{FG}"{anim} xml:space="preserve">'
                f'<tspan fill="{BLUE}" font-weight="700">{esc(k.ljust(8))}</tspan>{esc(v)}</text>'
            )
        y += lh
        n += 1
    sy = H - 38
    sw = "".join(f'<rect x="{x0 + i * 26}" y="{sy}" width="22" height="14" rx="3" fill="{c}"/>' for i, c in enumerate(SWATCH))
    anim_css = (
        ".ln { animation: slide .5s ease-out both; }"
        "@keyframes slide { from { opacity: 0; transform: translateX(-10px); } to { opacity: 1; transform: none; } }"
        ".cur { animation: blink 1.1s steps(1) infinite; } @keyframes blink { 50% { opacity: 0; } }"
    )
    cursor = f'<rect class="cur" x="{x0 + len(HANDLE + " ~ $ ") * 6.6:.0f}" y="{sy - 24}" width="7" height="13" fill="{GREEN}"/>'
    out.append(sw)
    out.append(f'<text x="{x0}" y="{sy - 14}" font-size="11" fill="{DIM}">{HANDLE} ~ $</text>')
    out.append(cursor)
    (ROOT / "info-card.svg").write_text(frame(W, H, "neofetch", "\n".join(out), style=anim_css), encoding="utf-8")
    print("wrote info-card.svg")


if __name__ == "__main__":
    main()
