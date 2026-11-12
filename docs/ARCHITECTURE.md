# معماری

```text
persian-poetry-agent-skills/
├── README.md
├── LICENSE
├── docs/ARCHITECTURE.md
└── skills/
    ├── persian-modern-poet/
    │   ├── SKILL.md
    │   ├── references/
    │   ├── examples/
    │   └── evals/
    └── persian-classical-poet/
        ├── SKILL.md
        ├── references/
        ├── examples/
        └── evals/
```

`SKILL.md` نقطه‌ی ورود و ارکستراسیون است؛ `references/` دانش تخصصیِ بارگذاری‌شونده هنگام نیاز؛ `examples/` آزمایشگاه یادگیری؛ `evals/` آزمون‌های قابل سنجش. بسته کاملاً مارک‌داون است و هیچ کد اجرایی ندارد؛ تقطیع و اعتبارسنجی به‌صورت دستی و طبق دستورالعمل‌های مارک‌داون انجام می‌شود. این تفکیک از بارگذاری همه‌ی جزئیات در هر درخواست جلوگیری می‌کند. دو اسکیل جدا هستند چون قواعد ریتم و سطرشکنی شعر نو با عروض و قافیه‌ی شعر سنتی یکسان نیست.
