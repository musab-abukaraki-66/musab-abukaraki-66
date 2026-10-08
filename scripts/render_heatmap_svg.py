"""Render data/contributions.json as an animated 53x7 heatmap: contrib-heatmap.svg."""
import json
from datetime import date
from pathlib import Path

from theme import AMBER, BORDER, DIM, FG, GREEN, HANDLE, MUTED, esc, frame

ROOT = Path(__file__).resolve().parent.parent
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#7ee787"]

W, H = 860, 286
STEP, CELL = 14.6, 11.6
LEFT, TOP = 44, 92
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


def sunday_row(d: date) -> int:
    return (d.weekday() + 1) % 7


def main() -> None:
    data = json.loads((ROOT / "data" / "contributions.json").read_text(encoding="utf-8"))
    days, st = data["days"], data["stats"]
    peak = max((d["count"] for d in days), default=0)

    first = date.fromisoformat(days[0]["date"])
    col0 = first.toordinal() - sunday_row(first)

    cells, month_labels, last_month = [], [], None
    for d in days:
        dt = date.fromisoformat(d["date"])
        col, row = (dt.toordinal() - sunday_row(dt) - col0) // 7, sunday_row(dt)
        level = d["level"]
        if level == 4 and peak >= 10 and d["count"] >= peak * 0.9:
            level = 5  # neon top end, only for genuinely standout days
        x, y = LEFT + col * STEP, TOP + row * STEP
        delay = round((col + row) * 0.028, 3)  # diagonal sweep
        tip = f"{d['count']} contribution{'s' if d['count'] != 1 else ''} on {d['date']}"
        cells.append(
            f'<rect class="c" x="{x:.1f}" y="{y:.1f}" width="{CELL}" height="{CELL}" rx="2.5" '
            f'fill="{PALETTE[level]}" style="animation-delay:{delay}s"><title>{esc(tip)}</title></rect>'
        )
        if row == 0 and dt.month != last_month:
            month_labels.append((col, f'<text x="{x:.1f}" y="{TOP - 10}" font-size="10" fill="{DIM}">{MONTHS[dt.month - 1]}</text>'))
            last_month = dt.month

    day_labels = "".join(
        f'<text x="{LEFT - 10}" y="{TOP + r * STEP + 9.6:.1f}" font-size="9" fill="{DIM}" text-anchor="end">{n}</text>'
        for r, n in ((1, "Mon"), (3, "Wed"), (5, "Fri"))
    )

    # legend: Less [] [] [] [] [] [] More
    lx = W - 24 - 6 * 14 - 62
    ly = TOP + 7 * STEP + 24
    legend = f'<text x="{lx}" y="{ly + 9}" font-size="10" fill="{DIM}" text-anchor="end">Less</text>'
    for i, c in enumerate(PALETTE):
        legend += f'<rect x="{lx + 8 + i * 14}" y="{ly}" width="11" height="11" rx="2.5" fill="{c}"/>'
    legend += f'<text x="{lx + 8 + 6 * 14 + 4}" y="{ly + 9}" font-size="10" fill="{DIM}">More</text>'

    bd = st["best_day"]
    bdt = date.fromisoformat(bd["date"]) if bd["date"] else None
    best = f"{bd['count']} on {MONTHS[bdt.month - 1]} {bdt.day}" if bdt and bd["count"] else "n/a"
    foot = (
        f'<text x="24" y="{ly + 9}" font-size="11" fill="{FG}">'
        f'<tspan fill="{GREEN}" font-weight="700">{st["total"]:,}</tspan> contributions in the last year'
        f'<tspan fill="{MUTED}">  |  </tspan>streak <tspan fill="{AMBER}">{st["current_streak"]}d</tspan>'
        f'<tspan fill="{MUTED}">  |  </tspan>longest <tspan fill="{AMBER}">{st["longest_streak"]}d</tspan>'
        f'<tspan fill="{MUTED}">  |  </tspan>best day <tspan fill="{AMBER}">{esc(best)}</tspan>'
        f'<tspan fill="{MUTED}">  |  </tspan>{st["active_days"]} active days</text>'
    )

    prompt = (
        f'<text x="24" y="64" font-size="12" fill="{GREEN}">{HANDLE}</text>'
        f'<text x="{24 + len(HANDLE) * 7.2 + 6:.0f}" y="64" font-size="12" fill="{DIM}">~ $ ./contributions.sh</text>'
    )
    style = (
        ".c { transform-box: fill-box; transform-origin: center; animation: pop .55s cubic-bezier(.2,.9,.3,1.3) both; }"
        "@keyframes pop { from { opacity: 0; transform: translateY(-8px) scale(.3); } to { opacity: 1; transform: none; } }"
    )
    # a partial first column can sit right next to the next month's label; drop the crowded one
    if len(month_labels) > 1 and month_labels[1][0] - month_labels[0][0] < 3:
        month_labels = month_labels[1:]
    body = prompt + "".join(t for _, t in month_labels) + day_labels + "\n  " + "\n  ".join(cells) + "\n" + legend + foot
    out = ROOT / "contrib-heatmap.svg"
    out.write_text(frame(W, H, f"{HANDLE} - contributions", body, style=style), encoding="utf-8")
    print(f"wrote {out.name} ({len(cells)} cells)")


if __name__ == "__main__":
    main()
