# Perfect Shade Bid Generator

Local-only Windows desktop bid generator for Perfect Shade LLC.

The app provides a functional PySide6 UI shell, validates required bid fields, exports bid data to JSON, and can generate a Word DOCX bid proposal from a local template. PDF generation is intentionally left for a future task.

## Features

- Desktop window titled **Perfect Shade Bid Generator**
- Tabs for Project, Scope of Work, Pricing, Terms & Notes, and Output
- Dynamic scope item rows, up to 20 items
- Dynamic pricing rows, up to 50 lines
- Decimal-based subtotal, sales tax, total, deposit, and balance calculations
- Friendly validation dialogs
- Local JSON export with safe filename handling and duplicate filename suffixes
- Word DOCX bid proposal generation using `docxtpl`
- Optional addenda acknowledgements included in JSON and conditionally rendered in DOCX
- Standard Measurement Readiness and Craftsmanship Warranty sections in every DOCX

## Setup

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run

Run from the project root folder, `Perfect Shade Tool`:

```bat
python -m app.main
```

## Output

Clicking **Create Bid** saves a JSON file to the selected output folder using this format:

```text
YYYY-MM-DD - Project Name - Perfect Shade Bid.json
```

If **Create DOCX** is checked, the app also creates:

```text
YYYY-MM-DD - Project Name - Perfect Shade Bid.docx
```

If a file already exists, the app appends ` (2)`, ` (3)`, and so on.

DOCX generation uses the local template at:

```text
templates/perfect_shade_bid_template.docx
```

## Future Tasks

- Add optional PDF export

