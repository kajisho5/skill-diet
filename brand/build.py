#!/usr/bin/env python3
"""Build the skill-diet wordmark and icon SVGs.

Letters are Inter Display Bold (SIL Open Font License 1.1) converted to
outlines, so the SVGs render the same everywhere without the font installed.
Needs fontTools (pip install fonttools) and the Inter Display Bold font file;
the outputs are committed, so this only runs when the logo changes.
"""
import sys
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

FONT = "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
OUT = Path(__file__).resolve().parent
GREEN = "#16A34A"
GREEN_DARK = "#4ADE80"

font = TTFont(sys.argv[1] if len(sys.argv) > 1 else FONT)
gs = font.getGlyphSet()
cmap = font.getBestCmap()
upm = font["head"].unitsPerEm
asc = font["hhea"].ascent


def run(text, x, y, size, squeeze=1.0, tracking=0.0):
    """Return (path_d, advance) for text with baseline at y."""
    s = size / upm
    pen = SVGPathPen(gs)
    for ch in text:
        g = cmap[ord(ch)]
        tp = TransformPen(pen, (s * squeeze, 0, 0, -s, x, y))
        gs[g].draw(tp)
        x += gs[g].width * s * squeeze + tracking * size
    return pen.getCommands(), x


def wordmark(fg, accent, name):
    size, base = 64, 62
    d1, x = run("skill", 0, base, size, tracking=-0.02)
    d2, x2 = run("-", x + 2, base, size)
    # "diet" is the same letters squeezed to 74% width: the word slims down
    d3, x3 = run("diet", x2 + 2, base, size, squeeze=0.74, tracking=-0.01)
    w = round(x3 + 4)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} 80" '
           f'width="{w}" height="80" role="img" aria-label="skill-diet">'
           f'<path fill="{fg}" d="{d1}"/><path fill="{accent}" d="{d2}"/>'
           f'<path fill="{accent}" d="{d3}"/></svg>\n')
    (OUT / name).write_text(svg, encoding="utf-8")


def icon(bg, page, belt, name):
    # A SKILL.md page whose sides pinch in at a belt: a document on a diet.
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="256" height="256" role="img" aria-label="skill-diet icon">
<rect width="256" height="256" rx="56" fill="{bg}"/>
<path fill="{page}" d="M72 44h84l32 32v52c0 4-14 6-14 20v40c0 9-7 16-16 16H88c-9 0-16-7-16-16v-40c0-14-14-16-14-20V60c0-9 7-16 14-16z"/>
<path fill="{bg}" opacity=".18" d="M156 44v24c0 4 4 8 8 8h24z"/>
<rect x="94" y="88" width="68" height="9" rx="4.5" fill="{bg}" opacity=".55"/>
<rect x="94" y="106" width="48" height="9" rx="4.5" fill="{bg}" opacity=".55"/>
<rect x="48" y="128" width="160" height="22" rx="11" fill="{belt}"/>
<rect x="120" y="124" width="22" height="30" rx="6" fill="none" stroke="{page}" stroke-width="6"/>
<rect x="94" y="168" width="58" height="9" rx="4.5" fill="{bg}" opacity=".55"/>
<rect x="94" y="186" width="40" height="9" rx="4.5" fill="{bg}" opacity=".55"/>
</svg>
'''
    (OUT / name).write_text(svg, encoding="utf-8")


wordmark("#0B0F14", GREEN, "wordmark-black.svg")
wordmark("#F5F7FA", GREEN_DARK, "wordmark-white.svg")
icon("#0B0F14", "#F5F7FA", GREEN_DARK, "icon-dark.svg")
icon("#F5F7FA", "#0B0F14", GREEN, "icon.svg")
print("wrote", *sorted(p.name for p in OUT.glob("*.svg")))
