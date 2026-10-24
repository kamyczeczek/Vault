"""Add `disable-model-invocation: true` to every active workspace SKILL.md.

Skills stay registered (usable via /skill:name) but are no longer advertised
in the system prompt, so the model never loads them automatically.
skills/archive/ is skipped (it is excluded from pi's scan by skills/.ignore).
Idempotent: files that already have the flag are left untouched.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "skills"

FLAG = "disable-model-invocation"


def update(skill_md: Path) -> str:
    text = skill_md.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return "skip (no frontmatter)"
    # find closing ---
    close = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            close = i
            break
    if close is None:
        return "skip (unterminated frontmatter)"
    fm = lines[1:close]
    if any(l.lstrip().startswith(FLAG) for l in fm):
        return "already set"
    fm.insert(len(fm), f"{FLAG}: true\n")
    skill_md.write_text("".join([lines[0], *fm, *lines[close:]]), encoding="utf-8")
    return "updated"


def main() -> int:
    updated = skipped = missing = 0
    for skill_md in sorted(ROOT.glob("*/SKILL.md")):
        if "archive" in skill_md.parts:
            continue
        result = update(skill_md)
        if result == "updated":
            updated += 1
        elif result == "already set":
            skipped += 1
        else:
            missing += 1
            print(f"WARN {skill_md}: {result}")
    print(f"updated={updated} already={skipped} warn={missing}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
