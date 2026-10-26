#!/usr/bin/env python3
"""Mechanical audit of an Agent Skill folder (standard library only).

Usage:
  python3 skill_audit.py audit <skill-dir> [--json]
  python3 skill_audit.py compare <old-skill-dir> <new-skill-dir> [--json]

`audit` prints measured numbers and rule-based findings. Every finding carries
a checklist ID from references/checklist.md. Findings marked "heuristic" are
candidates for a human/agent to confirm, not verdicts.

Exit code: 0 = no ERROR findings, 1 = at least one ERROR, 2 = usage problem.
"""

import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------- limits ----
# Values come from the Agent Skills spec (agentskills.io/specification),
# Anthropic's skill authoring best practices, and the Claude Code skills docs.
NAME_MAX = 64                 # spec: name 1-64 chars
DESC_MAX = 1024               # spec: description 1-1024 chars
COMPAT_MAX = 500              # spec: compatibility 1-500 chars
CC_LISTING_MAX = 1536         # Claude Code: description + when_to_use cut here
BODY_LINES_MAX = 500          # spec + best practices: keep SKILL.md < 500 lines
BODY_TOKENS_MAX = 5000        # spec: body < 5000 tokens recommended
COMPACTION_KEEP = 5000        # Claude Code keeps first 5,000 tokens on compaction
REF_TOC_LINES = 100           # best practices: TOC for reference files > 100 lines
EMPHASIS_PER_100_LINES = 3    # local heuristic: more than this reads as shouting

PORTABLE_KEYS = {"name", "description", "license", "compatibility",
                 "metadata", "allowed-tools"}
CLAUDE_CODE_KEYS = {"when_to_use", "argument-hint", "arguments",
                    "disable-model-invocation", "user-invocable",
                    "disallowed-tools", "model", "effort", "context", "agent",
                    "background", "hooks", "paths", "shell"}
RESERVED_WORDS = ("anthropic", "claude")

FILLER = [
    r"\bplease note that\b", r"\bit is important to note\b",
    r"\bit'?s worth noting\b", r"\bkeep in mind that\b", r"\bin order to\b",
    r"\bbasically\b", r"\bessentially\b", r"\bsimply\b", r"\bjust\b",
    r"\bas mentioned (above|earlier|before)\b", r"\bfeel free to\b",
    r"\bmake sure to\b", r"\bdon'?t forget to\b", r"\bnote that\b",
    r"念のため", r"なお、", r"ちなみに", r"基本的に", r"いわゆる",
]
HEDGES = [
    r"\bmight\b", r"\bperhaps\b", r"\bpossibly\b", r"\bprobably\b",
    r"\bif possible\b", r"\bwhen appropriate\b", r"\bas needed\b",
    r"\btry to\b", r"\bconsider\b", r"できれば", r"なるべく", r"適宜",
    r"必要に応じて", r"かもしれ",
]
TIME_SENSITIVE = [
    r"\b(before|after|until|since|as of)\s+(jan|feb|mar|apr|may|jun|jul|aug|"
    r"sep|oct|nov|dec)[a-z]*\.?\s+\d{4}\b",
    r"\b(before|after|until|since|as of)\s+\d{4}\b",
    r"\b(currently|recently|nowadays|these days|latest)\b",
    r"\d{4}年\d{1,2}月(以前|以降|まで|時点)", r"現在は", r"最近",
]
FIRST_SECOND_PERSON_DESC = [r"\bI\b", r"\bI'm\b", r"\bI can\b", r"\bmy\b",
                            r"\byou can\b", r"\byour\b", r"\byou\b"]
WORKFLOW_IN_DESC = [r"\bfirst\b.*\bthen\b", r"\bstep\s*\d", r"\b1[.)]\s.*\b2[.)]\s",
                    r"→|->", r"\bafter that\b", r"\bfollowed by\b",
                    r"まず.*次に", r"その後"]
EMPHASIS = re.compile(r"\b(MUST|NEVER|ALWAYS|IMPORTANT|CRITICAL|REQUIRED|"
                      r"DO NOT|DON'T|NO EXCEPTIONS)\b|必ず|絶対に|厳守")
CAPS_WORD = re.compile(r"\b[A-Z]{4,}\b")
LINK = re.compile(r"\[[^\]]*\]\(([^)\s#]+)(?:#[^)]*)?\)")
BARE_PATH = re.compile(r"(?<![\w/.-])((?:references|scripts|assets|reference|"
                       r"docs|examples|agents)/[\w./-]+)")


# ------------------------------------------------------------ helpers -------
def est_tokens(text):
    """Rough token estimate. ASCII ~4 chars/token, other scripts ~1 char/token.

    This is an estimate for comparing versions, not an exact count.
    """
    ascii_chars = sum(1 for c in text if ord(c) < 128)
    other = len(text) - ascii_chars
    return round(ascii_chars / 4 + other * 1.0)


def parse_frontmatter(text):
    """Parse the YAML subset used in SKILL.md frontmatter.

    Supports: key: value, quoted values, block scalars (| and >),
    folded multi-line plain scalars, one-level maps (metadata), and lists.
    Returns (dict, body, error_message_or_None, frontmatter_line_count).
    """
    if not text.startswith("---"):
        return {}, text, "frontmatter must start on line 1 with ---", 0
    lines = text.split("\n")
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return {}, text, "frontmatter has no closing ---", 0
    fm_lines = lines[1:end]
    body = "\n".join(lines[end + 1:])
    data, err = {}, None
    i = 0
    while i < len(fm_lines):
        raw = fm_lines[i]
        if not raw.strip() or raw.lstrip().startswith("#"):
            i += 1
            continue
        if raw.startswith((" ", "\t")):
            err = err or f"unexpected indentation on frontmatter line {i + 2}"
            i += 1
            continue
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", raw)
        if not m:
            err = err or f"cannot parse frontmatter line {i + 2}: {raw!r}"
            i += 1
            continue
        key, val = m.group(1), m.group(2)
        i += 1
        children = []
        while i < len(fm_lines) and (fm_lines[i].startswith((" ", "\t"))
                                     or not fm_lines[i].strip()):
            children.append(fm_lines[i])
            i += 1
        while children and not children[-1].strip():
            children.pop()
        if val in ("|", ">", "|-", ">-", "|+", ">+"):
            parts = [c.strip() for c in children]
            data[key] = ("\n" if val.startswith("|") else " ").join(parts).strip()
        elif val == "" and children and children[0].strip().startswith("- "):
            data[key] = [c.strip()[2:].strip().strip("'\"") for c in children
                         if c.strip().startswith("- ")]
        elif val == "" and children:
            sub = {}
            for c in children:
                cm = re.match(r"^\s+([^:]+):\s*(.*)$", c)
                if cm:
                    sub[cm.group(1).strip()] = cm.group(2).strip().strip("'\"")
            data[key] = sub
        else:
            if val[:1] in ("'", '"'):
                q = val[0]
                joined = " ".join([val] + [c.strip() for c in children])
                if joined.endswith(q) and len(joined) > 1:
                    joined = joined[1:-1]
                    if q == "'":
                        joined = joined.replace("''", "'")
                else:
                    err = err or f"unclosed quote in '{key}'"
                data[key] = joined
            elif val.startswith("[") and val.endswith("]"):
                data[key] = [v.strip().strip("'\"") for v in val[1:-1].split(",")
                             if v.strip()]
            else:
                data[key] = " ".join([val] + [c.strip() for c in children]).strip()
                if ": " in val and not children:
                    err = err or (f"value of '{key}' contains ': ' unquoted; "
                                  "strict YAML parsers may reject it")
    return data, body, err, end + 1


def strip_code(text):
    """Remove fenced code blocks so prose checks ignore code and examples."""
    return re.sub(r"```.*?```", "", text, flags=re.S)


def line_of(body_lines, offset, pattern):
    for n, line in enumerate(body_lines, start=offset):
        if re.search(pattern, line, flags=re.I):
            return n
    return None


def add(findings, fid, level, msg, where=None, kind="rule"):
    findings.append({"id": fid, "level": level, "kind": kind,
                     "where": where, "message": msg})


# -------------------------------------------------------------- audit -------
def audit(skill_dir):
    root = Path(skill_dir).resolve()
    findings = []
    md = root / "SKILL.md"
    if not md.is_file():
        add(findings, "F1", "ERROR", "SKILL.md not found")
        return {"skill_dir": str(root), "findings": findings, "stats": {}}
    raw = md.read_text(encoding="utf-8", errors="replace")
    if raw.startswith("﻿"):
        add(findings, "F1", "WARN", "file starts with a byte-order mark; "
            "frontmatter may not be recognised", "SKILL.md:1")
        raw = raw[1:]
    raw = raw.replace("\r\n", "\n")
    fm, body, err, fm_len = parse_frontmatter(raw)
    if err:
        add(findings, "F1", "ERROR", err, "SKILL.md")

    # ---- frontmatter keys
    keys = set(fm)
    cc_only = sorted(keys & CLAUDE_CODE_KEYS)
    unknown = sorted(keys - PORTABLE_KEYS - CLAUDE_CODE_KEYS)
    if cc_only:
        add(findings, "P1", "WARN", "Claude Code-only keys "
            f"{cc_only}: claude.ai upload and the Skills API reject these")
    if unknown:
        add(findings, "F2", "WARN", f"unknown keys {unknown}: Claude Code "
            "ignores them silently; other products reject them")

    # ---- name
    name = fm.get("name")
    if not isinstance(name, str) or not name.strip():
        add(findings, "F3", "ERROR", "missing 'name' (required by the spec)")
    else:
        if len(name) > NAME_MAX:
            add(findings, "F3", "ERROR", f"name is {len(name)} chars (max {NAME_MAX})")
        if not re.fullmatch(r"[a-z0-9-]+", name):
            add(findings, "F3", "ERROR", f"name {name!r}: lowercase a-z, 0-9 "
                "and hyphens only")
        if name.startswith("-") or name.endswith("-") or "--" in name:
            add(findings, "F3", "ERROR", f"name {name!r}: no leading/trailing "
                "or doubled hyphens")
        if any(w in name.lower() for w in RESERVED_WORDS):
            add(findings, "F3", "ERROR", f"name {name!r} contains a reserved "
                "word (anthropic/claude)")
        if name != root.name:
            add(findings, "F4", "WARN", f"name {name!r} differs from folder "
                f"{root.name!r} (spec: must match)")

    # ---- description
    desc = fm.get("description")
    when = fm.get("when_to_use") if isinstance(fm.get("when_to_use"), str) else ""
    if not isinstance(desc, str) or not desc.strip():
        add(findings, "D1", "ERROR", "missing or empty 'description'")
        desc = ""
    else:
        if len(desc) > DESC_MAX:
            add(findings, "D1", "ERROR", f"description is {len(desc)} chars "
                f"(max {DESC_MAX})")
        if "<" in desc or ">" in desc:
            add(findings, "D1", "ERROR", "description contains < or > "
                "(rejected by upload validators; XML tags not allowed)")
        combined = len(desc) + (len(when) + 1 if when else 0)
        if combined > CC_LISTING_MAX:
            add(findings, "D2", "WARN", f"description+when_to_use is {combined}"
                f" chars; Claude Code cuts the listing at {CC_LISTING_MAX}")
        for p in FIRST_SECOND_PERSON_DESC:
            if re.search(p, desc):
                add(findings, "D3", "WARN", "description uses first/second "
                    f"person ({p.strip(chr(92) + 'b')}); write in third person",
                    kind="heuristic")
                break
        if not re.search(r"\b(use (it |this )?(when|for|whenever)|when the user|"
                         r"triggers?|if the user)\b|使う|使用|とき|場合", desc, re.I):
            add(findings, "D4", "WARN", "description has no visible 'when to "
                "use' trigger phrase", kind="heuristic")
        for p in WORKFLOW_IN_DESC:
            if re.search(p, desc, re.I):
                add(findings, "D5", "INFO", "description may summarise the "
                    "procedure (agents may follow it instead of the body)",
                    kind="heuristic")
                break

    comp = fm.get("compatibility")
    if isinstance(comp, str) and len(comp) > COMPAT_MAX:
        add(findings, "F5", "ERROR", f"compatibility is {len(comp)} chars "
            f"(max {COMPAT_MAX})")

    # ---- body size
    body_lines = body.split("\n")
    first_body_line = fm_len + 1
    tokens = est_tokens(body)
    words = len(re.findall(r"[A-Za-z0-9_'-]+", body))
    cjk = len(re.findall(r"[぀-ヿ㐀-鿿]", body))
    if len(body_lines) > BODY_LINES_MAX:
        add(findings, "L1", "WARN", f"body is {len(body_lines)} lines "
            f"(guideline < {BODY_LINES_MAX})")
    if tokens > BODY_TOKENS_MAX:
        add(findings, "L2", "WARN", f"body is ~{tokens} tokens (spec "
            f"recommends < {BODY_TOKENS_MAX})")
        acc, cut_line = 0, None
        for n, line in enumerate(body_lines, start=first_body_line):
            acc += est_tokens(line + "\n")
            if acc > COMPACTION_KEEP:
                cut_line = n
                break
        if cut_line:
            add(findings, "L3", "INFO", "after context compaction Claude Code "
                f"keeps only the first {COMPACTION_KEEP} tokens; content from "
                f"about line {cut_line} on can be lost", f"SKILL.md:{cut_line}")

    prose = strip_code(body)

    # ---- emphasis density
    emph_hits = []
    for n, line in enumerate(body_lines, start=first_body_line):
        if line.strip().startswith("```"):
            continue
        k = len(EMPHASIS.findall(re.sub(r"`[^`]*`", "", line)))
        if k:
            emph_hits.append((n, k))
    emph_total = sum(k for _, k in emph_hits)
    caps_total = len(CAPS_WORD.findall(prose))
    bold_total = len(re.findall(r"\*\*[^*\n]+\*\*", prose))
    per100 = emph_total / max(len(body_lines), 1) * 100
    if per100 > EMPHASIS_PER_100_LINES:
        where = ", ".join(f"SKILL.md:{n}" for n, _ in emph_hits[:8])
        add(findings, "E1", "WARN", f"{emph_total} emphasis markers "
            f"(MUST/NEVER/ALWAYS/IMPORTANT…), {per100:.1f} per 100 lines; "
            "keep emphasis for rules that were observed to be broken",
            where, kind="heuristic")

    # ---- filler / hedges / time-sensitive (prose lines only)
    in_code = set()
    fence = False
    for n, line in enumerate(body_lines, start=first_body_line):
        if line.strip().startswith("```"):
            fence = not fence
            in_code.add(n)
        elif fence:
            in_code.add(n)

    def scan_prose(patterns, fid, label, level="INFO"):
        hits = []
        for n, line in enumerate(body_lines, start=first_body_line):
            if n in in_code:
                continue
            if any(re.search(p, line, re.I) for p in patterns):
                hits.append(n)
        if hits:
            where = ", ".join(f"SKILL.md:{n}" for n in hits[:10])
            more = f" (+{len(hits) - 10} more)" if len(hits) > 10 else ""
            add(findings, fid, level, f"{len(hits)} lines with {label}{more}",
                where, kind="heuristic")
        return len(hits)

    filler_n = scan_prose(FILLER, "C2", "filler phrases")
    hedge_n = scan_prose(HEDGES, "C3", "hedging words")
    scan_prose(TIME_SENSITIVE, "C6", "time-sensitive wording", "WARN")

    # ---- duplicated lines / near-duplicate paragraphs
    seen = {}
    dups = []
    for n, line in enumerate(body_lines, start=first_body_line):
        if n in in_code:
            continue
        norm = re.sub(r"[\W_]+", " ", line.lower()).strip()
        if len(norm) < 25:
            continue
        if norm in seen:
            dups.append((seen[norm], n))
        else:
            seen[norm] = n
    if dups:
        where = ", ".join(f"SKILL.md:{a}={b}" for a, b in dups[:8])
        add(findings, "C4", "WARN", f"{len(dups)} repeated lines", where)

    paras = [p for p in re.split(r"\n\s*\n", prose) if len(p.split()) >= 12]

    def shingles(p):
        w = re.findall(r"\w+", p.lower())
        return {" ".join(w[i:i + 4]) for i in range(max(len(w) - 3, 1))}

    near = []
    sh = [shingles(p) for p in paras]
    for a in range(len(paras)):
        for b in range(a + 1, len(paras)):
            if not sh[a] or not sh[b]:
                continue
            j = len(sh[a] & sh[b]) / len(sh[a] | sh[b])
            if j >= 0.5:
                near.append((a, b, round(j, 2)))
    if near:
        def first_line(p):
            first = p.strip().split("\n")[0]
            ln = line_of(body_lines, first_body_line, re.escape(first[:40]))
            return f"SKILL.md:{ln}" if ln else "?"
        where = ", ".join(f"{first_line(paras[a])}~{first_line(paras[b])}"
                          f"({j})" for a, b, j in near[:6])
        add(findings, "C5", "WARN", f"{len(near)} near-duplicate paragraph "
            "pairs (≥50% shared 4-word runs)", where, kind="heuristic")

    # ---- references
    def clean(r):
        return r.rstrip(".,;:)`'\"")

    no_inline_code = re.sub(r"`[^`\n]*`", "", prose)
    link_refs = {clean(r) for r in LINK.findall(no_inline_code) if "://" not in r}
    bare_refs = {clean(r) for r in BARE_PATH.findall(body)}
    refs = link_refs | bare_refs | {clean(r) for r in LINK.findall(body)
                                    if "://" not in r}
    broken_links, broken_bare, ref_files, outside = [], [], [], []
    for r in sorted(refs):
        if "\\" in r:
            add(findings, "R4", "WARN", f"backslash path {r!r}; use /")
            continue
        if r.startswith(("/", "mailto:")):
            continue  # site paths or absolute paths: not skill files
        p = (root / r)
        try:
            p.resolve().relative_to(root)
        except ValueError:
            outside.append(r)
            continue
        if not p.exists():
            (broken_links if r in link_refs else broken_bare).append(r)
        elif p.is_file():
            ref_files.append(p)
    if broken_links:
        add(findings, "R1", "ERROR", f"markdown links to missing files: "
            f"{broken_links}")
    if outside:
        add(findings, "R1", "WARN", f"links pointing outside the skill folder: "
            f"{outside} (they break once the skill is installed on its own)")
    if broken_bare:
        add(findings, "R1", "INFO", f"paths not found inside this skill: "
            f"{broken_bare} (fine if they point to another skill or the "
            "user's files)", kind="heuristic")
    if re.search(r"\b[\w-]+\\[\w.-]+\.(md|py|sh|js)\b", body):
        add(findings, "R4", "WARN", "Windows-style backslash path in body")

    all_files = [p for p in root.rglob("*") if p.is_file()
                 and not {"__pycache__", ".git", ".github", "dist"} & set(p.parts)
                 and p.name != "SKILL.md"]
    text_files = [p for p in all_files if p.suffix.lower() in
                  (".md", ".txt", ".rst")]
    ref_set = {p.resolve() for p in ref_files}
    def mentioned(p, rel):
        stem_mod = rel.rsplit(".", 1)[0].replace("/", ".")
        return (p.resolve() in ref_set or any(rel in r for r in refs)
                or p.name in body or stem_mod in body)

    for p in text_files:
        rel = p.relative_to(root).as_posix()
        if rel.split("/")[0] in ("evals", "tests") or p.name.upper().startswith(
                ("LICENSE", "README", "CHANGELOG", "NOTICE")):
            continue
        txt = p.read_text(encoding="utf-8", errors="replace")
        n_lines = txt.count("\n") + 1
        head = "\n".join(txt.split("\n")[:40])
        if n_lines > REF_TOC_LINES and not re.search(
                r"^#+\s*(contents|table of contents|目次)", head, re.I | re.M):
            add(findings, "R3", "INFO", f"{rel} has {n_lines} lines and no "
                "table of contents near the top")
        nested = [x for x in set(LINK.findall(txt)) if "://" not in x
                  and (p.parent / x).suffix == ".md" and (p.parent / x).exists()]
        if nested:
            add(findings, "R2", "WARN", f"{rel} links on to {sorted(nested)}; "
                "keep references one level deep from SKILL.md")
        if not mentioned(p, rel):
            add(findings, "R5", "INFO", f"{rel} is never mentioned in "
                "SKILL.md, so the agent will not know to read it")
    for p in all_files:
        if p.suffix.lower() in (".py", ".sh", ".js", ".ts") \
                and p.name != "__init__.py":
            rel = p.relative_to(root).as_posix()
            if rel.split("/")[0] in ("evals", "tests"):
                continue
            if not mentioned(p, rel):
                add(findings, "R5", "INFO", f"script {rel} is never "
                    "mentioned in SKILL.md")

    nested_skill = [p.relative_to(root).as_posix() for p in root.rglob("SKILL.md")
                    if p.resolve() != md.resolve()
                    and "__pycache__" not in p.parts
                    and p.relative_to(root).parts[0] != "evals"]
    if nested_skill:
        add(findings, "P2", "ERROR", f"extra SKILL.md files {nested_skill}: "
            "claude.ai and the Skills API accept exactly one")

    headings = len(re.findall(r"^#{1,6}\s", prose, re.M))
    stats = {
        "description_chars": len(desc),
        "when_to_use_chars": len(when),
        "body_lines": len(body_lines),
        "body_words_latin": words,
        "body_cjk_chars": cjk,
        "body_tokens_est": tokens,
        "headings": headings,
        "code_blocks": body.count("```") // 2,
        "emphasis_markers": emph_total,
        "all_caps_words": caps_total,
        "bold_spans": bold_total,
        "filler_lines": filler_n,
        "hedge_lines": hedge_n,
        "supporting_files": len(all_files),
        "supporting_tokens_est": sum(est_tokens(p.read_text("utf-8", "replace"))
                                     for p in text_files),
    }
    order = {"ERROR": 0, "WARN": 1, "INFO": 2}
    findings.sort(key=lambda f: (order[f["level"]], f["id"]))
    return {"skill_dir": str(root), "name": name if isinstance(name, str) else None,
            "frontmatter_keys": sorted(keys), "stats": stats,
            "findings": findings}


def print_audit(r):
    print(f"# Audit: {r['skill_dir']}")
    s = r["stats"]
    if s:
        print("\n## Numbers")
        for k, v in s.items():
            print(f"- {k}: {v}")
    print("\n## Findings")
    if not r["findings"]:
        print("- none")
    for f in r["findings"]:
        tag = " (heuristic: confirm by reading)" if f["kind"] == "heuristic" else ""
        where = f" [{f['where']}]" if f["where"] else ""
        print(f"- {f['level']} {f['id']}{where}: {f['message']}{tag}")


def compare(old_dir, new_dir):
    a, b = audit(old_dir), audit(new_dir)
    rows = []
    for k in a["stats"]:
        x, y = a["stats"].get(k), b["stats"].get(k)
        if isinstance(x, int) and isinstance(y, int):
            pct = f"{(y - x) / x * 100:+.0f}%" if x else "n/a"
            rows.append((k, x, y, pct))
    old_ids = {(f["id"], f["message"]) for f in a["findings"]}
    new_ids = {(f["id"], f["message"]) for f in b["findings"]}
    return {"old": a, "new": b, "rows": rows,
            "fixed": sorted(old_ids - new_ids), "introduced": sorted(new_ids - old_ids),
            "name_changed": a.get("name") != b.get("name")}


def print_compare(c):
    print(f"# Compare\n- old: {c['old']['skill_dir']}\n- new: {c['new']['skill_dir']}")
    if c["name_changed"]:
        print(f"- WARNING: name changed {c['old']['name']!r} -> {c['new']['name']!r}"
              " (breaks /name invocation and references)")
    print("\n| metric | old | new | change |\n|---|---|---|---|")
    for k, x, y, pct in c["rows"]:
        print(f"| {k} | {x} | {y} | {pct} |")
    print("\n## Findings fixed")
    for fid, msg in c["fixed"] or [("-", "none")]:
        print(f"- {fid}: {msg}")
    print("\n## Findings introduced")
    for fid, msg in c["introduced"] or [("-", "none")]:
        print(f"- {fid}: {msg}")


def main(argv):
    as_json = "--json" in argv
    args = [a for a in argv if a != "--json"]
    if len(args) == 2 and args[0] == "audit":
        r = audit(args[1])
        print(json.dumps(r, ensure_ascii=False, indent=2) if as_json else "", end="")
        if not as_json:
            print_audit(r)
        return 1 if any(f["level"] == "ERROR" for f in r["findings"]) else 0
    if len(args) == 3 and args[0] == "compare":
        c = compare(args[1], args[2])
        if as_json:
            print(json.dumps(c, ensure_ascii=False, indent=2))
        else:
            print_compare(c)
        return 1 if any(f["level"] == "ERROR" for f in c["new"]["findings"]) else 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
