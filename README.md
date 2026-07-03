# Perfect Shade Bid Generator

Perfect Shade Bid Generator is a local-only Windows desktop application for creating bid proposals for Perfect Shade LLC. It uses PySide6 for the desktop interface and creates local JSON and Word DOCX files without requiring cloud services or Microsoft Word.

PDF export is not implemented and remains disabled in the application.

## Features

- PySide6 desktop interface with Project, Scope of Work, Pricing, Terms & Notes, and Output tabs
- Dynamic scope items and main pricing rows
- Optional alternate pricing table kept separate from the base proposal total
- Optional addenda acknowledgement
- Additional terms and exclusions rendered as proposal bullets
- Optional prevailing wage statement
- Constant Measurement Readiness section
- Constant Craftsmanship Warranty section
- Constant Company Qualifications section
- Constant maximum-retainage language
- Decimal-based subtotal, total, deposit, and balance calculations
- Local JSON export with safe filenames and duplicate-name suffixes
- DOCX generation with `docxtpl` and the bundled proposal template
- Friendly validation dialogs for required or invalid proposal data
- Disabled PDF option indicating that PDF export is not implemented

## Setup

Python 3.10 or later is recommended. From the repository root:

```bat
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

## Run

```bat
python -m app.main
```

## Tests

```bat
python -m pytest
```

## Output

Selecting **Create Bid** always writes proposal data as JSON to the selected output folder:

```text
YYYY-MM-DD - Project Name - Perfect Shade Bid.json
```

When **Create DOCX** is selected, the app also renders the bundled template and writes:

```text
YYYY-MM-DD - Project Name - Perfect Shade Bid.docx
```

Existing files are not overwritten. The application appends ` (2)`, ` (3)`, and so on to create a unique filename. The default output location is the repository's local `output` folder, and another local folder can be selected in the UI.

DOCX generation uses the local template at:

```text
templates/perfect_shade_bid_template.docx
```
