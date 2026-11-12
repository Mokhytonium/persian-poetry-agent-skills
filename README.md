# Persian Poetry Agent Skills

[![validate](https://github.com/Mokhytonium/persian-poetry-agent-skills/actions/workflows/validate.yml/badge.svg)](https://github.com/Mokhytonium/persian-poetry-agent-skills/actions/workflows/validate.yml)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-educational%20%2F%20personal-blue)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.1.0-green)](CHANGELOG.md)

> Two modular agent skills for **Persian poetry** — classical (ghazal, masnavi, robai, qasida) and modern (free verse, Nimā'i) — covering writing, continuation, revision, criticism, and **verified prosody**. Ships with a deterministic meter scanner, measurable evals, and CI.

دو اسکیل مستقل و ماژولار برای شعر فارسی، به‌همراه ابزار تقطیع قطعی، evalهای سنجش‌پذیر و اعتبارسنجی خودکار.

- [`skills/persian-classical-poet/`](skills/persian-classical-poet/) — غزل، مثنوی، رباعی، دوبیتی، قصیده، قطعه
- [`skills/persian-modern-poet/`](skills/persian-modern-poet/) — شعر نو، سپید، آزاد، نیمایی

## چرا این بسته؟

مدل‌های زبانی در شعر فارسی اغلب وزن را «حدس» می‌زنند و با اطمینان ادعای «کاملاً موزون» می‌کنند. این بسته سه کار می‌کند:

1. **دانش فنی واقعی:** جدول بحور با الگوی هجایی، اختیارات شاعری، حروف قافیه و وزن هر قالب — نه فقط توصیه.
2. **تقطیع قطعی:** اسکریپت [`scan_meter.py`](scripts/scan_meter.py) الگوی کوتاه/بلند را محاسبه و با وزن هدف تطبیق می‌دهد؛ ادعا را به محاسبه بدل می‌کند.
3. **صداقت فنی:** چهار سطح قطعیت («خوش‌آهنگ» ← «وزن محتمل» ← «تقطیع‌شده» ← «تأییدشده»)؛ فقط سطح آخر اجازه‌ی ادعای قطعی می‌دهد.

## ساختار

```text
persian-poetry-agent-skills/
├── README.md · LICENSE · CONTRIBUTING.md · CHANGELOG.md
├── .github/                  # CI + قالب‌های issue/PR
├── docs/ARCHITECTURE.md
├── scripts/
│   ├── scan_meter.py         # تقطیع‌یار فارسی
│   └── validate_package.py   # اعتبارسنج ساختار
├── tests/                    # تست‌های اسکریپت تقطیع
└── skills/
    ├── persian-classical-poet/
    │   ├── SKILL.md          # نقطه‌ی ورود و ارکستراسیون
    │   ├── references/       # عروض، قافیه، قالب‌ها، تصویر، زبان، نقد، …
    │   ├── examples/         # آزمایشگاه بازنویسی (نمونه‌های انجام‌شده)
    │   └── evals/evals.json
    └── persian-modern-poet/
        ├── SKILL.md
        ├── references/       # تصویر، ریتم، زبان، صدا، نقد، …
        ├── examples/
        └── evals/evals.json
```

`SKILL.md` ارکستراتور است؛ `references/` هنگام نیاز بارگذاری می‌شود (progressive disclosure)؛ `examples/` نمونه‌ی انجام‌شده می‌دهد؛ `evals/` آزمون سنجش‌پذیر دارد. دو اسکیل جدا هستند چون قواعد ریتم و سطرشکنی شعر نو با عروض و قافیه‌ی شعر سنتی یکسان نیست.

## نصب

پوشه‌ی **هر اسکیل** را جداگانه در محل skills ابزار خود کپی کنید (پوشه‌ی اصلی ZIP خودش یک skill نیست):

| ابزار | مسیر معمول |
|---|---|
| Claude (Agent Skills) | `~/.claude/skills/<skill-name>/` |
| Qoder | پوشه‌ی skills کاربر یا پروژه |
| سایر ابزارهای سازگار | محل تعریف‌شده‌ی skill در مستندات ابزار |

نمونه:
```bash
cp -r skills/persian-classical-poet ~/.claude/skills/
cp -r skills/persian-modern-poet   ~/.claude/skills/
```

## استفاده

اسکیل با تشخیص درخواست فعال می‌شود. نمونه promptها:

- «یک غزل دو بیتی درباره‌ی باران شبانه در وزن هزج مسدس محذوف با ردیف "شد" بساز.»
- «این مصراع را تقطیع کن و وزنش را بگو: بشنو این نی چون شکایت می‌کند»
- «این شعر نو را بازنویسی کن؛ تصویر مرکزی‌اش را حفظ کن.»
- «آیا این مصراع موزون است؟ بررسی کن.» (اسکیل بدون تقطیع تأیید نمی‌کند)

## ابزار تقطیع

[`scripts/scan_meter.py`](scripts/scan_meter.py) آوانویسیِ هجابندی‌شده را می‌گیرد و الگو را می‌سازد:

```bash
# تقطیع یک مصراع و تطبیق با وزن هدف
python scripts/scan_meter.py \
  --text "بشنو این نی چون شکایت می‌کند" \
  --line "besh-no-vī-ney-chon-she-kā-yat-mī-ko-nad" \
  --meter "رمل مسدس محذوف"

# شناسایی وزن از روی الگو (بدون --meter)
python scripts/scan_meter.py --line "be-sah-rā-ban-ga-ram-sah-rā-ta-vī-nam"

# جدول بحور
python scripts/scan_meter.py --list-meters
```

طرح آوانویسی: واکه‌ی کوتاه `a e o i u`، بلند `ā ī ū`، مرکب `ey ow`؛ جداکننده‌ی هجا `-` یا فاصله. قواعد: `CV=U`، `CVV/CVC=—`، `CVVC/CVCC=—U` (کشیده)، هجای پایانی همیشه بلند. **تشخیص اضافه، همزه و تلفظ صحیح بر عهده‌ی کاربر است**؛ ورودی نادرست = نتیجه‌ی نادرست.

## اعتبارسنجی و تست

```bash
python scripts/validate_package.py        # ساختار، فرانت‌متر، لینک‌ها، فایل یتیم، evalها
python -m unittest discover -s tests -v   # تست‌های اسکریپت تقطیع
```

اعتبارسنج ساختار را می‌سنجد، **نه کیفیت ادبی یا صحت عروض را**. CI روی هر push/PR هر دو را اجرا می‌کند.

## evals

هر اسکیل ۱۰ کیس با متن ورودی (`input`) و معیارهای پذیرش سنجش‌پذیر دارد؛ از جمله تقطیع، تشخیص وزن شکسته، قافیه‌ی آوایی، جداسازی قافیه/ردیف، سطرشکنی، حفظ هسته و صداقت فنی. کیس‌های تقطیع با `scan_meter.py` قابل راستی‌آزمایی‌اند.

## اصول

1. حفظ ایده‌ها و تصاویر موفق متن اولیه، حتی اگر عبارت‌بندی تغییر کند.
2. جداسازی تولید، نقد ادبی و راستی‌آزمایی فنی.
3. عدم ادعای وزن و قافیه بدون بررسی واقعی.
4. آرایه‌ها در خدمت معنا، نه چک‌لیست تزئینی.
5. پرسش‌گری هوشمند؛ فقط اگر پاسخ مسیر اثر را تغییر دهد.
6. هر بیت/بند باید کارکرد تازه‌ای داشته باشد.
7. تشخیص ابهام سازنده از نحو نامفهوم.

## مشارکت

[`CONTRIBUTING.md`](CONTRIBUTING.md) را ببینید. هر نمونه‌ی تقطیع باید با اسکریپت تأیید شود؛ هر فایل منبع باید از `SKILL.md` لینک شود؛ evalها باید معیار سنجش‌پذیر داشته باشند.

## مجوز

[`LICENSE`](LICENSE) — استفاده و بازتوزیع آموزشی و شخصی با ذکر منبع. آثار شاعران دیگر تابع وضعیت حقوقی خودشان‌اند؛ اشاره‌های کوتاه در منابع صرفاً آموزشی‌اند.