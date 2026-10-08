"""Stats dashboard card from data/contributions.json: stats-card.svg (tiles + weekly bar chart)."""
import json
from datetime import date
from pathlib import Path

from theme import AMBER, BLUE, BORDER, DIM, FG, GREEN, HANDLE, MUTED, PANEL, PINK, esc, frame

ROOT = Path(__file__).resolve().parent.parent
W, H = 490, 456
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
WEEKS = 30


def fmt(d: str | None) -> str:
    if not d:
        return "n/a"
    dt = date.fromisoformat(d)
    return f"{MONTHS[dt.month - 1]} {dt.day}"


def main() -> None:
    data = json.loads((ROOT / "data" / "contributions.json").read_text(encoding="utf-8"))
    days, st = data["days"], data["stats"]

    weeks: list[int] = []
    for i, d in enumerate(days):
        dt = date.fromisoformat(d["date"])
        if not weeks or (dt.weekday() + 1) % 7 == 0:
            weeks.append(0)
        weeks[-1] += d["count"]
    weeks = weeks[-WEEKS:]
    peak = max(weeks) or 1
    avg = st["total"] / 52

    tiles = [
        ("current streak", f"{st['current_streak']}", "days", GREEN),
        ("longest streak", f"{st['longest_streak']}", "days", GREEN),
        ("contributions", f"{st['total']:,}", "last 12 months", BLUE),
        ("active days", f"{st['active_days']}", f"of {len(days)}", BLUE),
        ("best day", f"{st['best_day']['count']}", fmt(st["best_day"]["date"]), AMBER),
        ("weekly average", f"{avg:.1f}", "contributions / week", PINK),
    ]
    tw, th, gx, gy, x0, y0 = 219, 74, 12, 10, 20, 52
    out = []
    for i, (label, value, sub, color) in enumerate(tiles):
        x, y = x0 + (i % 2) * (tw + gx), y0 + (i // 2) * (th + gy)
        out.append(
            f'<g class="t" style="animation-delay:{0.15 + i * 0.1:.2f}s">'
            f'<rect x="{x}" y="{y}" width="{tw}" height="{th}" rx="8" fill="{PANEL}" stroke="{BORDER}"/>'
            f'<text x="{x + 14}" y="{y + 20}" font-size="10" fill="{DIM}">{esc(label)}</text>'
            f'<text x="{x + 14}" y="{y + 50}" font-size="26" font-weight="700" fill="{color}">{esc(value)}</text>'
            f'<text x="{x + 14}" y="{y + 66}" font-size="9" fill="{MUTED}">{esc(sub)}</text></g>'
        )

    cy = y0 + 3 * (th + gy) + 14  # chart section
    out.append(f'<text x="{x0}" y="{cy}" font-size="11" fill="{FG}">contributions / week <tspan fill="{MUTED}">(last {len(weeks)} weeks)</tspan></text>')
    base, area = H - 30, 82
    bw = 450 / len(weeks)
    for i, v in enumerate(weeks):
        h = max(2.5, v / peak * area)
        out.append(
            f'<rect class="b" x="{x0 + i * bw:.1f}" y="{base - h:.1f}" width="{bw - 4:.1f}" height="{h:.1f}" rx="2" '
            f'fill="{GREEN if v else "#21262d"}" style="animation-delay:{0.9 + i * 0.03:.2f}s"><title>{v} contributions</title></rect>'
        )
    out.append(f'<line x1="{x0}" y1="{base + 3}" x2="{W - x0}" y2="{base + 3}" stroke="{BORDER}"/>')
    out.append(f'<text x="{x0}" y="{H - 10}" font-size="9" fill="{MUTED}">{HANDLE} ~ $ stats --live  |  updated {data["fetched"]}</text>')

    style = (
        ".t { animation: up .5s ease-out both; } @keyframes up { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: none; } }"
        ".b { transform-box: fill-box; transform-origin: bottom; animation: grow .6s cubic-bezier(.2,.9,.3,1) both; }"
        "@keyframes grow { from { transform: scaleY(0); } to { transform: scaleY(1); } }"
    )
    (ROOT / "stats-card.svg").write_text(frame(W, H, "stats.live", "\n".join(out), style=style), encoding="utf-8")
    print("wrote stats-card.svg")


if __name__ == "__main__":
    main()
