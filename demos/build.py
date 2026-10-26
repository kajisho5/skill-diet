#!/usr/bin/env python3
"""Build docs/demo-light.svg and docs/demo-dark.svg from the csv-tidy example.

Reads examples/csv-tidy/compare.json (output of
`skill_audit.py compare ... --json`), examples/csv-tidy/ledger.md and
examples/csv-tidy/trigger-test.txt, so the README picture always shows the
measured numbers. Standard library only:  python3 demos/build.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EX = ROOT / "examples" / "csv-tidy"
OUT = ROOT / "docs"

THEMES = {
    "light": {"bg": "#FFFFFF", "card": "#F6F8FA", "fg": "#0B0F14", "muted": "#57606A",
              "old": "#D0D7DE", "new": "#16A34A", "warn": "#B45309", "line": "#D8DEE4"},
    "dark": {"bg": "#0D1117", "card": "#161B22", "fg": "#E6EDF3", "muted": "#8B949E",
             "old": "#30363D", "new": "#4ADE80", "warn": "#F59E0B", "line": "#30363D"},
}
FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def data():
    c = json.loads((EX / "compare.json").read_text(encoding="utf-8"))
    rows = {k: (x, y) for k, x, y, _ in c["rows"]}
    ledger = (EX / "ledger.md").read_text(encoding="utf-8")
    inv = len(re.findall(r"^\| I\d+ ", ledger, re.M))
    kept = len([l for l in ledger.splitlines() if re.match(r"^\| I\d+ ", l)
                and l.rstrip().rstrip("|").split("|")[-1].strip()])
    trig = (EX / "trigger-test.txt").read_text(encoding="utf-8")
    old = re.search(r"old\.json \{'total': (\d+), 'passed': (\d+)", trig)
    new = re.search(r"new\.json \{'total': (\d+), 'passed': (\d+)", trig)
    regress = sum(1 for l in trig.splitlines() if " old P new F " in l)
    return rows, (kept, inv), (int(old[2]), int(new[2]), int(old[1]), regress)


def svg(theme):
    t = THEMES[theme]
    rows, (kept, inv), (t_old, t_new, t_total, regress) = data()
    W, H = 880, 476
    bars = [
        ("Body tokens (est.)", *rows["body_tokens_est"]),
        ("Body lines", *rows["body_lines"]),
        ("MUST / NEVER / IMPORTANT", *rows["emphasis_markers"]),
        ("Headings", *rows["headings"]),
        ("Filler + hedge lines", rows["filler_lines"][0] + rows["hedge_lines"][0],
         rows["filler_lines"][1] + rows["hedge_lines"][1]),
    ]
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" '
         f'height="{H}" role="img" aria-label="skill-diet before and after on a sample '
         f'skill: body tokens {rows["body_tokens_est"][0]} to {rows["body_tokens_est"][1]}, '
         f'invariants kept {kept} of {inv}">',
         f'<rect width="{W}" height="{H}" rx="16" fill="{t["bg"]}"/>',
         f'<text x="32" y="48" font-family="{FONT}" font-size="22" font-weight="700" '
         f'fill="{t["fg"]}">csv-tidy (fictional sample skill), before → after</text>',
         f'<text x="32" y="74" font-family="{FONT}" font-size="14" fill="{t["muted"]}">'
         f'Measured with scripts/skill_audit.py compare. Bars are relative to the original.</text>']
    y, x0, bw = 112, 272, 360
    for label, a, b in bars:
        pct = round((b - a) / a * 100) if a else 0
        wb = bw * (b / a) if a else 0
        o.append(f'<text x="32" y="{y + 15}" font-family="{FONT}" font-size="15" '
                 f'fill="{t["fg"]}">{esc(label)}</text>')
        o.append(f'<rect x="{x0}" y="{y}" width="{bw}" height="10" rx="5" fill="{t["old"]}"/>')
        o.append(f'<rect x="{x0}" y="{y + 12}" width="{max(wb, 3):.1f}" height="10" rx="5" '
                 f'fill="{t["new"]}"/>')
        o.append(f'<text x="{x0 + bw + 16}" y="{y + 15}" font-family="{MONO}" font-size="15" '
                 f'fill="{t["fg"]}">{a} → {b}</text>')
        o.append(f'<text x="{W - 32}" y="{y + 15}" text-anchor="end" font-family="{MONO}" '
                 f'font-size="15" font-weight="700" fill="{t["new"]}">{pct:+d}%</text>')
        y += 44
    o.append(f'<line x1="32" x2="{W - 32}" y1="{y + 4}" y2="{y + 4}" stroke="{t["line"]}"/>')
    y += 26
    cards = [
        ("Invariants kept", f"{kept} / {inv}", "numbers, paths, formats, conditions"),
        ("Trigger test", f"{t_old} → {t_new} / {t_total}", f"{regress} regressions"),
        ("Description", f"{rows['description_chars'][0]} → {rows['description_chars'][1]} chars",
         "longer on purpose: added when-to-use"),
    ]
    cw = (W - 64 - 32) / 3
    for i, (head, big, small) in enumerate(cards):
        cx = 32 + i * (cw + 16)
        o.append(f'<rect x="{cx:.1f}" y="{y}" width="{cw:.1f}" height="92" rx="12" '
                 f'fill="{t["card"]}"/>')
        o.append(f'<text x="{cx + 18:.1f}" y="{y + 28}" font-family="{FONT}" font-size="13" '
                 f'fill="{t["muted"]}">{esc(head)}</text>')
        color = t["warn"] if head == "Description" else t["new"]
        o.append(f'<text x="{cx + 18:.1f}" y="{y + 58}" font-family="{FONT}" font-size="22" '
                 f'font-weight="700" fill="{color}">{esc(big)}</text>')
        o.append(f'<text x="{cx + 18:.1f}" y="{y + 78}" font-family="{FONT}" font-size="12" '
                 f'fill="{t["muted"]}">{esc(small)}</text>')
    o.append("</svg>\n")
    return "\n".join(o)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for theme in THEMES:
        path = OUT / f"demo-{theme}.svg"
        path.write_text(svg(theme), encoding="utf-8")
        print("wrote", path.relative_to(ROOT))
