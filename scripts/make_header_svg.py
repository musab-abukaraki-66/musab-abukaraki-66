"""Typed terminal banner: header.svg. Two commands print once, then a cursor blinks."""
from pathlib import Path

from theme import AMBER, BLUE, DIM, FG, GREEN, HANDLE, esc, frame

ROOT = Path(__file__).resolve().parent.parent
W, H = 860, 150
CH = 7.8  # advance of 13px monospace, used to size the typing wipe


def typed(x: float, y: float, segments: list[tuple[str, str]], begin: float, size: int = 13, bold: bool = False) -> tuple[str, str, float]:
    """One line of coloured text revealed left to right. Returns (defs, markup, end_time)."""
    text = "".join(s for s, _ in segments)
    width = len(text) * (size * 0.6)
    dur = max(0.4, len(text) * 0.035)
    cid = f"t{int(begin * 100)}"
    defs = (
        f'<clipPath id="{cid}"><rect x="{x}" y="{y - size - 2}" width="0" height="{size + 8}">'
        f'<animate attributeName="width" from="0" to="{width + 4:.0f}" dur="{dur:.2f}s" begin="{begin}s" fill="freeze"/></rect></clipPath>'
    )
    spans = "".join(f'<tspan fill="{c}">{esc(s)}</tspan>' for s, c in segments)
    weight = ' font-weight="700"' if bold else ""
    markup = f'<text x="{x}" y="{y}" font-size="{size}"{weight} xml:space="preserve" clip-path="url(#{cid})">{spans}</text>'
    return defs, markup, begin + dur


def main() -> None:
    prompt = [(HANDLE, GREEN), (" ~ $ ", DIM)]
    lines = [
        (62, prompt + [("whoami", FG)], 13, False, 0.3),
        (92, [("Musab AbuKaraki", BLUE), ("  /  Data Science & AI graduate", FG)], 17, True, 1.0),
        (124, prompt + [("echo $FOCUS", FG)], 13, False, 2.4),
        (146, [("Official public data -> reconciled models -> decisions.", AMBER)], 13, False, 3.2),
    ]
    defs, body, end = "", [], 0.0
    for y, segs, size, bold, t in lines:
        d, m, end = typed(24, y, segs, t, size, bold)
        defs, body = defs + d, body + [m]
    cx = 24 + len("Official public data -> reconciled models -> decisions.") * 13 * 0.6 + 6
    body.append(
        f'<rect x="{cx:.0f}" y="134" width="8" height="15" fill="{GREEN}" opacity="0">'
        f'<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;0.01;0.5;0.51;1" dur="1.1s" begin="{end:.2f}s" repeatCount="indefinite"/></rect>'
    )
    (ROOT / "header.svg").write_text(frame(W, H + 14, f"{HANDLE} - whoami", "\n".join(body), defs=defs), encoding="utf-8")
    print("wrote header.svg")


if __name__ == "__main__":
    main()
