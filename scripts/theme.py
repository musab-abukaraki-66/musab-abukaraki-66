"""Shared look for every generated SVG: one palette, one font stack, one terminal frame."""
from xml.sax.saxutils import escape

USER = "musab-abukaraki-66"
HANDLE = "musab@github"

BG = "#0d1117"
PANEL = "#010409"
BORDER = "#30363d"
FG = "#c9d1d9"
DIM = "#8b949e"
MUTED = "#484f58"
GREEN = "#39d353"
BLUE = "#58a6ff"
AMBER = "#e3b341"
PINK = "#f778ba"
RED = "#ff7b72"

FONT = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"


def esc(s: str) -> str:
    return escape(s, {'"': "&quot;"})


def frame(width: int, height: int, title: str, body: str, defs: str = "", style: str = "") -> str:
    """Terminal window: rounded dark panel, title bar with three dots, centred title."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{esc(title)}">
  <title>{esc(title)}</title>
  <defs>{defs}</defs>
  <style>
    text {{ font-family: {FONT}; }}
    {style}
    @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
  </style>
  <rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>
  <path d="M0.5 36 V10.5 a10 10 0 0 1 10 -10 H{width - 10.5} a10 10 0 0 1 10 10 V36 Z" fill="{PANEL}"/>
  <line x1="0.5" y1="36" x2="{width - 0.5}" y2="36" stroke="{BORDER}"/>
  <circle cx="20" cy="18" r="5.5" fill="#ff5f56"/>
  <circle cx="38" cy="18" r="5.5" fill="#ffbd2e"/>
  <circle cx="56" cy="18" r="5.5" fill="#27c93f"/>
  <text x="{width / 2}" y="22" font-size="12" fill="{DIM}" text-anchor="middle">{esc(title)}</text>
{body}
</svg>
"""
