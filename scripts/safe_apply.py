#!/usr/bin/env python3
"""Apply a trimmed skill over the real one, with a verified backup and undo.

Usage:
  python3 safe_apply.py apply   <workspace> <target-skill-dir> [--yes]
  python3 safe_apply.py restore <backup-dir> <target-skill-dir> [--yes] [--force]

<workspace> is the folder from the skill-diet workflow that holds
original/<name>/ (snapshot taken before trimming) and trimmed/<name>/.

apply (fail-closed):
  1. Refuses if the target changed since the snapshot (someone edited it while
     you were trimming), if the trimmed copy has audit ERRORs, or if the skill
     name changed.
  2. Without --yes it only prints the plan.
  3. Copies the current target to <workspace>/backups/<UTC time>/ and writes
     manifest.json with SHA-256 of every file before and after.
  4. Mirrors trimmed/<name>/ into the target and verifies every hash.

restore: puts a backup back. Refuses if the target was edited after the apply
(its hashes no longer match the manifest) unless --force.

Exit code: 0 = done (or plan printed), 1 = refused or verification failed,
2 = usage problem.
"""

import datetime
import hashlib
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import skill_audit  # noqa: E402  (same folder)

SKIP_PARTS = {".git", "__pycache__", ".DS_Store"}


def tree_hashes(root):
    """Map relative POSIX path -> SHA-256 for every regular file under root."""
    root = Path(root)
    out = {}
    for p in sorted(root.rglob("*")):
        if any(part in SKIP_PARTS for part in p.relative_to(root).parts):
            continue
        if p.is_symlink():
            raise SystemExit(f"refused: symlink {p} (copying it could escape "
                             "the skill folder)")
        if p.is_file():
            out[p.relative_to(root).as_posix()] = hashlib.sha256(
                p.read_bytes()).hexdigest()
    return out


def diff(a, b):
    added = sorted(set(b) - set(a))
    removed = sorted(set(a) - set(b))
    changed = sorted(k for k in set(a) & set(b) if a[k] != b[k])
    return added, removed, changed


def mirror(src, dst):
    """Make dst contain exactly the files of src (skipping .git etc.)."""
    src, dst = Path(src), Path(dst)
    want = tree_hashes(src)
    have = tree_hashes(dst) if dst.exists() else {}
    for rel in set(have) - set(want):
        (dst / rel).unlink()
    for rel in want:
        target = dst / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src / rel, target)
    # remove directories left empty by deletions
    for d in sorted((p for p in dst.rglob("*") if p.is_dir()),
                    key=lambda p: len(p.parts), reverse=True):
        if not any(d.iterdir()) and not any(part in SKIP_PARTS for part in d.parts):
            d.rmdir()


def find_pair(workspace):
    ws = Path(workspace)
    origs = [p for p in (ws / "original").glob("*") if (p / "SKILL.md").is_file()]
    trims = [p for p in (ws / "trimmed").glob("*") if (p / "SKILL.md").is_file()]
    if len(origs) != 1 or len(trims) != 1:
        raise SystemExit("refused: expected exactly one original/<name>/ and one "
                         f"trimmed/<name>/ under {ws}")
    return origs[0], trims[0]


def cmd_apply(workspace, target, yes):
    target = Path(target).resolve()
    orig, trim = find_pair(workspace)
    problems = []
    if not (target / "SKILL.md").is_file():
        problems.append(f"{target} has no SKILL.md")
    else:
        a, r, c = diff(tree_hashes(orig), tree_hashes(target))
        if a or r or c:
            problems.append("target changed since the snapshot (added "
                            f"{a}, removed {r}, changed {c}); trim again from "
                            "the current version")
    report = skill_audit.audit(trim)
    errors = [f for f in report["findings"] if f["level"] == "ERROR"]
    if errors:
        problems.append("trimmed copy has audit ERRORs: "
                        + "; ".join(f"{f['id']} {f['message']}" for f in errors))
    old_name = skill_audit.audit(orig).get("name")
    if report.get("name") != old_name:
        problems.append(f"skill name changed {old_name!r} -> {report.get('name')!r}")
    if problems:
        print("REFUSED:\n- " + "\n- ".join(problems))
        return 1

    before, after = tree_hashes(target), tree_hashes(trim)
    a, r, c = diff(before, after)
    print(f"Plan: replace {target}\n  add: {a or '-'}\n  remove: {r or '-'}\n"
          f"  change: {c or '-'}")
    if not yes:
        print("Plan only. Re-run with --yes to back up and apply.")
        return 0

    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup = Path(workspace).resolve() / "backups" / stamp
    files = backup / "files"
    shutil.copytree(target, files, ignore=shutil.ignore_patterns(*SKIP_PARTS))
    if tree_hashes(files) != before:
        print("FAILED: backup does not match the target; nothing was applied")
        return 1
    mirror(trim, target)
    applied = tree_hashes(target)
    manifest = {"target": str(target), "created_utc": stamp,
                "before": before, "after": applied}
    (backup / "manifest.json").write_text(json.dumps(manifest, indent=2),
                                          encoding="utf-8")
    if applied != after:
        print(f"FAILED: target does not match trimmed copy after apply. "
              f"Restore with: restore {backup} {target}")
        return 1
    print(f"Applied. Backup: {backup}\nUndo: python3 {Path(__file__).name} "
          f"restore {backup} {target} --yes")
    return 0


def cmd_restore(backup, target, yes, force):
    backup, target = Path(backup).resolve(), Path(target).resolve()
    mpath = backup / "manifest.json"
    if not mpath.is_file() or not (backup / "files").is_dir():
        print(f"REFUSED: {backup} is not a skill-diet backup")
        return 1
    manifest = json.loads(mpath.read_text(encoding="utf-8"))
    if tree_hashes(backup / "files") != manifest["before"]:
        print("REFUSED: backup files do not match their manifest (damaged)")
        return 1
    current = tree_hashes(target) if target.exists() else {}
    if current != manifest["after"] and not force:
        a, r, c = diff(manifest["after"], current)
        print("REFUSED: target was edited after the apply (added "
              f"{a}, removed {r}, changed {c}). Use --force to overwrite.")
        return 1
    print(f"Plan: restore {target} from {backup}")
    if not yes:
        print("Plan only. Re-run with --yes to restore.")
        return 0
    mirror(backup / "files", target)
    if tree_hashes(target) != manifest["before"]:
        print("FAILED: restored target does not match the backup manifest")
        return 1
    print("Restored and verified.")
    return 0


def main(argv):
    yes = "--yes" in argv
    force = "--force" in argv
    args = [a for a in argv if a not in ("--yes", "--force")]
    if len(args) == 3 and args[0] == "apply":
        return cmd_apply(args[1], args[2], yes)
    if len(args) == 3 and args[0] == "restore":
        return cmd_restore(args[1], args[2], yes, force)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
