#!/usr/bin/env python3
"""اعتبارسنج ساختار بسته — Structural validator only.

بررسی می‌کند: وجود SKILL.md، فرانت‌متر (name/description/version)، طول description،
لینک‌های محلی، نبود فایل یتیم (هر md باید از SKILL.md لینک شده باشد)، و ساختار evalها
(حداقل ۵ کیس، id یکتا، prompt/acceptance غیرخالی). کیفیت ادبی، نحو، وزن یا قافیه را
اثبات نمی‌کند؛ برای تقطیع از scan_meter.py و تست‌ها استفاده کنید.
"""
from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
MAX_DESC = 1024
errors: list[str] = []


def check_frontmatter(skill_dir: Path, text: str) -> None:
    name = skill_dir.name
    if not text.startswith("---\n"):
        errors.append(f"Missing frontmatter: {name}")
        return
    parts = text.split("---", 2)
    if len(parts) < 3:
        errors.append(f"Unclosed frontmatter: {name}")
        return
    fm = parts[1]
    m = re.search(r"(?m)^name:\s*([a-z0-9-]+)\s*$", fm)
    if not m or m.group(1) != name:
        errors.append(f"name missing/mismatch: {name}")
    desc = re.search(r"(?m)^description:\s*(.+)$", fm)
    if not desc or not desc.group(1).strip():
        errors.append(f"description missing: {name}")
    elif len(desc.group(1).strip()) > MAX_DESC:
        errors.append(f"description too long (>{MAX_DESC}): {name}")
    if not re.search(r"(?m)^\s*version:\s*", fm):
        errors.append(f"version missing in metadata: {name}")


def check_links(skill_dir: Path) -> set[str]:
    linked: set[str] = set()
    for md in skill_dir.rglob("*.md"):
        body = md.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", body):
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            rel = target.split("#", 1)[0]
            if not rel:
                continue
            local = (md.parent / rel).resolve()
            if not local.exists():
                errors.append(f"Broken link: {md.relative_to(ROOT)} -> {target}")
            if md.name == "SKILL.md":
                linked.add((skill_dir / rel).resolve().as_posix())
    return linked


def check_orphans(skill_dir: Path, linked: set[str]) -> None:
    for md in skill_dir.rglob("*.md"):
        if md.name == "SKILL.md":
            continue
        if md.resolve().as_posix() not in linked:
            errors.append(f"Orphan file (not linked from SKILL.md): {md.relative_to(ROOT)}")


def check_evals(skill_dir: Path) -> None:
    name = skill_dir.name
    path = skill_dir / "evals/evals.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        errors.append(f"Invalid eval file {name}: {e}")
        return
    cases = data.get("cases", [])
    if len(cases) < 5:
        errors.append(f"Need at least five evals: {name}")
    seen: set[str] = set()
    for c in cases:
        cid = c.get("id")
        if not cid or not c.get("prompt") or not c.get("acceptance"):
            errors.append(f"Malformed eval (id/prompt/acceptance): {name} {cid}")
            continue
        if cid in seen:
            errors.append(f"Duplicate eval id: {name} {cid}")
        seen.add(cid)
        acc = c.get("acceptance")
        if not isinstance(acc, list) or not all(isinstance(a, str) and a.strip() for a in acc):
            errors.append(f"acceptance must be non-empty strings: {name} {cid}")


def main() -> int:
    skills_dir = ROOT / "skills"
    if not skills_dir.is_dir():
        print("VALIDATION FAILED")
        print("ERROR: missing skills/ directory")
        return 1
    for d in sorted(skills_dir.iterdir()):
        if not d.is_dir():
            continue
        p = d / "SKILL.md"
        if not p.exists():
            errors.append(f"Missing SKILL.md: {d.name}")
            continue
        text = p.read_text(encoding="utf-8")
        check_frontmatter(d, text)
        linked = check_links(d)
        check_orphans(d, linked)
        check_evals(d)

    if errors:
        print("VALIDATION FAILED")
        for e in errors:
            print("ERROR:", e)
        return 1
    print("STRUCTURE OK")
    print("Checked: frontmatter, description length, local links, orphan files, eval structure.")
    print("This does not validate literary quality, grammar, meter or rhyme.")
    return 0


if __name__ == "__main__":
    sys.exit(main())