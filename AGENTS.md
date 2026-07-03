# Perfect Shade Tool Repository Instructions

## Project identity

- This repository is **Perfect Shade Tool**, not UnifiedInvoice.
- Repository: `https://github.com/unifiedtechworks/PerfectShadeTool.git`
- Do not use UnifiedInvoice task numbers, packages, paths, conventions, or baseline rules.
- The application is a local-only Windows desktop bid proposal generator for Perfect Shade LLC.

## Technology and structure

- Python with PySide6 desktop UI.
- JSON persistence/export.
- DOCX generation with `docxtpl` and `templates/perfect_shade_bid_template.docx`.
- Primary source files live under `app/`.
- Generated proposals belong under `output/`.

## Development rules

- Keep the application local-only.
- Do not add cloud services, databases, authentication, networking, or web application features.
- Do not implement or enable PDF export unless a task explicitly requests it.
- Do not rewrite the application architecture.
- Preserve JSON and DOCX generation behavior.
- Treat the DOCX template as a core application asset.
- Keep user-facing proposal language professional and concise.
- Preserve the constant measurement readiness, craftsmanship warranty, company qualifications, and retainage sections unless a task explicitly requests changes.
- Preserve support for dynamic scope rows, main pricing rows, additional terms/exclusions rows, optional addenda acknowledgement, optional prevailing wage language, and optional alternate pricing.

## Verification

- Run `python -m compileall app` for source validation.
- Run `python -m app.main` when interactive application verification is appropriate.
- When changing the DOCX template or document-generation behavior, generate a test DOCX and verify its rendered output before considering the work complete.

## Scope discipline

- Make focused changes and avoid unrelated cleanup.
- Do not modify application functionality during repository-initialization tasks unless explicitly requested.
