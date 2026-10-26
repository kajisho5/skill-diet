#!/usr/bin/env python3
"""Build dist/skill-diet.skill (a zip with the skill folder at its root) and
print the version from SKILL.md frontmatter (metadata.version).

Only the files an installed skill needs go in: SKILL.md, LICENSE,
references/ and scripts/. README, tests and CI files stay out.
"""
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NAME = "skill-diet"
INCLUDE = ["SKILL.md", "LICENSE", "references", "scripts"]


def version():
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    m = re.search(r'^\s+version:\s*"?([0-9]+\.[0-9]+\.[0-9]+)"?\s*$', text, re.M)
    if not m:
        sys.exit("metadata.version not found in SKILL.md")
    return m.group(1)


def build():
    out = ROOT / "dist" / f"{NAME}.skill"
    out.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for item in INCLUDE:
            p = ROOT / item
            files = [p] if p.is_file() else sorted(x for x in p.rglob("*") if x.is_file())
            for f in files:
                if "__pycache__" in f.parts:
                    continue
                z.write(f, f"{NAME}/{f.relative_to(ROOT).as_posix()}")
    return out


if __name__ == "__main__":
    if sys.argv[1:] == ["--version"]:
        print(version())
    else:
        print(build())
