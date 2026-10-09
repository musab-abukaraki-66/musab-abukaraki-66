"""Wide neofetch-style story card: info-card.svg. Two columns: who, and highlights."""
from pathlib import Path

from theme import AMBER, BLUE, DIM, FG, GREEN, HANDLE, MUTED, PINK, esc, frame

ROOT = Path(__file__).resolve().parent.parent
W, H = 860, 322

LEFT = [
    ("Role", "Data Science & AI graduate"),
    ("Base", "Amman, Jordan"),
    ("Focus", "BI, analytics engineering, automation"),
    ("Stack", "Power BI / PBIP, DAX, Python, SQL"),
    ("Also", "TypeScript, Next.js, Supabase"),
    ("Method", "source-traced, reconciled, reproducible"),
    ("Mail", "musababukaraki1@gmail.com"),
    ("Site", "musab-abukaraki.vercel.app"),
    ("LinkedIn", "linkedin.com/in/musababukaraki"),
]
RIGHT = [
    "6.64M federal contract actions -> 187 MB Power BI model",
    "3,107 hospitals drawn as SVG inside DAX, no custom visuals",
    "10 quarters of Jordanian unemployment, traced to source",
    "96.78% mAP@0.5 aerial car detection (YOLOv8s)",
    "Orbit: realtime project management, live on Vercel",
]
SWATCH = ["#ff7b72", "#e3b341", "#39d353", "#58a6ff", "#bc8cff", "#f778ba", "#8b949e", "#c9d1d9"]


def main() -> None:
    lh, y0 = 22, 86
    out = [
        f'<text x="28" y="62" font-size="14" font-weight="700" fill="{GREEN}">{HANDLE}</text>'
        f'<text x="28" y="72" font-size="11" fill="{MUTED}">{"-" * 12}</text>',
        f'<text x="400" y="62" font-size="12" fill="{AMBER}">[ highlights ]</text>',
        f'<line x1="386" y1="52" x2="386" y2="{H - 50}" stroke="#21262d"/>',
    ]
    for i, (k, v) in enumerate(LEFT):
        y = y0 + 10 + i * lh
        out.append(
            f'<text class="ln" style="animation-delay:{0.2 + i * 0.1:.1f}s" x="28" y="{y}" font-size="12" fill="{FG}" xml:space="preserve">'
            f'<tspan fill="{BLUE}" font-weight="700">{esc(k.ljust(9))}</tspan>{esc(v)}</text>'
        )
    for i, v in enumerate(RIGHT):
        y = y0 + 10 + i * lh * 1.2
        out.append(
            f'<text class="ln" style="animation-delay:{0.4 + i * 0.12:.2f}s" x="400" y="{y}" font-size="12" fill="{FG}">'
            f'<tspan fill="{PINK}">&gt;</tspan> {esc(v)}</text>'
        )
    sy = H - 34
    out.append("".join(f'<rect x="{28 + i * 26}" y="{sy}" width="22" height="14" rx="3" fill="{c}"/>' for i, c in enumerate(SWATCH)))
    out.append(f'<text x="400" y="{sy + 11}" font-size="11" fill="{DIM}">{HANDLE} ~ $</text>')
    out.append(f'<rect class="cur" x="{400 + len(HANDLE + " ~ $ ") * 6.6:.0f}" y="{sy}" width="7" height="13" fill="{GREEN}"/>')
    style = (
        ".ln { animation: slide .5s ease-out both; } @keyframes slide { from { opacity: 0; transform: translateX(-10px); } to { opacity: 1; transform: none; } }"
        ".cur { animation: blink 1.1s steps(1) infinite; } @keyframes blink { 50% { opacity: 0; } }"
    )
    (ROOT / "info-card.svg").write_text(frame(W, H, "neofetch", "\n".join(out), style=style), encoding="utf-8")
    print("wrote info-card.svg")


if __name__ == "__main__":
    main()
