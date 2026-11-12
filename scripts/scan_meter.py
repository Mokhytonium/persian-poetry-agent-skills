#!/usr/bin/env python3
"""تقطیع‌یار فارسی — Persian prosody scanner (transliteration-based).

این ابزار «تقطیع واقعی» را از ادعا به محاسبه تبدیل می‌کند: آوانویسیِ
هجابندی‌شده‌ی یک مصراع را می‌گیرد، الگوی کوتاه/بلند می‌سازد و با جدول
بحور رایج تطبیق می‌دهد. جایگزین قضاوت ادبی یا دانش عروضی نیست؛ در
اختلاف تلفظ یا اختیار شاعری، عدم قطعیت را گزارش می‌کند.

طرح آوانویسی (ASCII-friendly):
  واکه‌ی کوتاه:  a  e  o  i  u
  واکه‌ی بلند:   ā ī ū   (یا aa ii uu)
  واکه‌ی مرکب:   ey ow   (بلند محسوب می‌شود: می/کی = mey/key)
  صامت‌ها:       b p t s j ch h kh d z r zh sh gh f q k g l m n v y '
  جداکننده‌ی هجا: -  یا فاصله

قواعد مقدار هجا:
  CV            → کوتاه (U)
  CVV / CVC     → بلند (—)
  CVVC / CVCC   → کشیده (— U)  [در میان مصراع]
  هجای پایانی مصراع همیشه بلند (—) است.

مثال:
  python scripts/scan_meter.py --line "besh-no-vin-ney-chon-she-kā-yat-mi-ko-nad"
  python scripts/scan_meter.py --file poem.txt --meter "رمل مسدس محذوف"
  python scripts/scan_meter.py --list-meters
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SHORT = {"a", "e", "o", "i", "u"}
LONG = {"ā", "ī", "ū", "aa", "ii", "uu"}
DIPHTHONG = {"ey", "ow"}
DIGRAPHS = ("kh", "gh", "zh", "sh", "ch")
SINGLES = set("bptsjhdzrfqkglmnvy'")

U = "U"  # کوتاه
L = "L"  # بلند
S = "S"  # کشیده (— U)

# نام بحر → (ارکان، الگوی هجایی)
METERS: dict[str, tuple[str, str]] = {
    "هزج مسدس محذوف": ("مفاعیلن مفاعیلن فعولن", "U---U---U--"),
    "هزج مثمن سالم": ("مفاعیلن مفاعیلن مفاعیلن مفاعیلن", "U---U---U---U---"),
    "هزج مثمن اخرب مکفوف محذوف": ("مفعول مفاعیل مفاعیل فعولن", "--UU--UU--UU--"),
    "هزج مسدس اخرب مقبوض محذوف": ("مفعول مفاعلن فعولن", "--UU-U-U--"),
    "رمل مسدس محذوف": ("فاعلاتن فاعلاتن فاعلن", "-U---U---U-"),
    "رمل مثمن محذوف": ("فاعلاتن فاعلاتن فاعلاتن فاعلن", "-U---U---U---U-"),
    "مجتث مثمن مخبون محذوف": ("مفاعلن فعلاتن مفاعلن فعلن", "U-U-UU--U-U-UU-"),
    "مضارع مثمن اخرب مکفوف محذوف": ("مفعول فاعلات مفاعیل فاعلن", "--U-U-UU--U-U-"),
    "رجز مثمن سالم": ("مستفعلن مستفعلن مستفعلن مستفعلن", "--U---U---U---U-"),
    "خفیف مسدس مخبون محذوف": ("فعلاتن مفاعلن فعلن", "UU--U-U-UU-"),
}


class ScanError(ValueError):
    """آوانویسی نامعتبر یا هجای غیرممکن."""


def _consonant_at(s: str, i: int) -> int:
    """طول صامت در موقعیت i (دیگراف یا تک‌حرف)؛ ۰ اگر صامت نیست."""
    for d in DIGRAPHS:
        if s.startswith(d, i):
            return len(d)
    if i < len(s) and s[i] in SINGLES:
        return 1
    return 0


def parse_syllable(syl: str) -> str:
    """مقدار یک هجا را برمی‌گرداند: U / L / S."""
    s = syl.strip().lower()
    if not s:
        raise ScanError("هجای خالی")
    i = 0
    i += _consonant_at(s, i)  # onset (اختیاری؛ فارسی خوشه‌ی آغازین ندارد)
    nucleus = None
    for v in sorted(LONG | DIPHTHONG | SHORT, key=len, reverse=True):
        if s.startswith(v, i):
            nucleus = v
            i += len(v)
            break
    if nucleus is None:
        raise ScanError(f"واکه یافت نشد در هجای «{syl}»")
    codas = 0
    while i < len(s):
        n = _consonant_at(s, i)
        if n == 0:
            raise ScanError(f"بخش پایانی نامعتبر در هجای «{syl}»: «{s[i:]}»")
        i += n
        codas += 1
    long_nucleus = nucleus in LONG or nucleus in DIPHTHONG
    if codas > 2 or (long_nucleus and codas == 2):
        raise ScanError(f"هجای ناممکن در فارسی: «{syl}»")
    if not long_nucleus and codas == 0:
        return U
    if (long_nucleus and codas == 0) or (not long_nucleus and codas == 1):
        return L
    return S  # CVVC یا CVCC


def split_syllables(text: str) -> list[str]:
    parts = re.split(r"[\s\-]+", text.strip())
    return [p for p in parts if p]


def scan_line(text: str) -> tuple[list[tuple[str, str]], str]:
    """هجاها را با مقدار نهایی (اعمال قاعده‌ی پایان مصراع) و الگو برمی‌گرداند."""
    syls = split_syllables(text)
    if not syls:
        raise ScanError("مصراع خالی")
    quantities = [parse_syllable(s) for s in syls]
    quantities[-1] = L  # هجای پایانی همیشه بلند
    symbols = []
    pattern = []
    for syl, q in zip(syls, quantities):
        sym = {"U": "U", "L": "—", "S": "— U"}[q]
        symbols.append((syl, sym))
        pattern.append({"U": "U", "L": "-", "S": "-U"}[q])
    return symbols, "".join(pattern)


def match_meters(pattern: str, target: str | None = None) -> list[str]:
    if target is not None:
        if target not in METERS:
            raise ScanError(f"وزن ناشناخته: «{target}» (با --list-meters ببینید)")
        return [target] if METERS[target][1] == pattern else []
    return [name for name, (_, pat) in METERS.items() if pat == pattern]


def first_mismatch(pattern: str, target: str) -> int:
    pat = METERS[target][1]
    for i, (a, b) in enumerate(zip(pattern, pat)):
        if a != b:
            return i
    return min(len(pattern), len(pat))


def format_report(text: str, target: str | None = None, label: str | None = None) -> tuple[str, bool]:
    symbols, pattern = scan_line(text)
    lines = []
    if label:
        lines.append(f"متن: {label}")
    lines.append("تلفظ مبنا: " + " ".join(s for s, _ in symbols))
    lines.append("هجابندی: " + " | ".join(f"{s} ({sym})" for s, sym in symbols))
    lines.append(f"الگو: {pattern}  ({len(pattern)} هجا)")
    ok = True
    if target is not None:
        matches = match_meters(pattern, target)
        arkan = METERS[target][0]
        if matches:
            lines.append(f"تطبیق: ✓ منطبق بر «{target}» — {arkan}")
        else:
            ok = False
            idx = first_mismatch(pattern, target)
            lines.append(f"تطبیق: ✗ ناسازگار با «{target}» — {arkan}")
            lines.append(f"نخستین اختلاف در هجای شماره‌ی {idx + 1}؛ طول الگو: {len(pattern)} در برابر {len(METERS[target][1])}")
            lines.append("نتیجه: اصلاح لازم / نیازمند بررسی (اختیار شاعری را جداگانه بسنج)")
    else:
        matches = match_meters(pattern)
        if matches:
            for m in matches:
                lines.append(f"شناسایی: «{m}» — {METERS[m][0]}")
        else:
            ok = False
            lines.append("شناسایی: با هیچ‌یک از بحور جدول منطبق نیست")
            lines.append("نتیجه: نیازمند بررسی (تلفظ، اختیار شاعری یا وزن خارج از جدول)")
    return "\n".join(lines), ok


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="تقطیع‌یار فارسی (بر پایه‌ی آوانویسی)")
    src = ap.add_mutually_exclusive_group()
    src.add_argument("--line", help="آوانویسی هجابندی‌شده‌ی یک مصراع")
    src.add_argument("--file", help="فایل متنی؛ هر خط غیرخالی یک مصراع (# = توضیح)")
    ap.add_argument("--meter", help="نام وزن هدف برای تطبیق (اختیاری)")
    ap.add_argument("--text", help="متن فارسی مصراع برای نمایش در گزارش (اختیاری)")
    ap.add_argument("--list-meters", action="store_true", help="نمایش جدول بحور")
    args = ap.parse_args(argv)

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    if args.list_meters:
        print("نام بحر | ارکان | الگو")
        for name, (arkan, pat) in METERS.items():
            print(f"{name} | {arkan} | {pat}")
        return 0

    if not args.line and not args.file:
        ap.error("یکی از --line یا --file لازم است (یا --list-meters)")

    if args.line:
        items = [(args.line, args.text)]
    else:
        items = []
        for raw in Path(args.file).read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "|" in line:
                fa, tr = line.split("|", 1)
                items.append((tr.strip(), fa.strip()))
            else:
                items.append((line, None))

    all_ok = True
    for i, (tr, label) in enumerate(items):
        if i:
            print()
        try:
            report, ok = format_report(tr, args.meter, label)
            print(report)
            all_ok = all_ok and ok
        except ScanError as e:
            print(f"خطا: {e}")
            all_ok = False
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())