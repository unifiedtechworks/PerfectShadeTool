"""DOCX bid generation using docxtpl templates."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

from docxtpl import DocxTemplate

from app.calculations import format_currency
from app.models import BidData, normalize_document_type
from app.storage import sanitize_filename_part, unique_path


TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "templates" / "perfect_shade_bid_template.docx"


def build_docx_output_path(output_folder: Path, project_name: str) -> Path:
    """Build a unique DOCX output path using the standard bid filename format."""
    safe_project_name = sanitize_filename_part(project_name)
    filename = f"{date.today().isoformat()} - {safe_project_name} - Perfect Shade Bid.docx"
    return unique_path(output_folder / filename)


def build_render_context(bid_data: BidData) -> dict[str, Any]:
    """Build the docxtpl render context from BidData."""
    pricing_lines = [
        {
            "description": line.description,
            "amount_display": format_currency(line.amount),
        }
        for line in bid_data.pricing_lines
    ]
    alternate_pricing_lines = [
        {
            "description": line.description,
            "amount_display": format_currency(line.amount),
        }
        for line in bid_data.alternate_pricing_lines
    ]

    bid = {
        "document_type": normalize_document_type(bid_data.document_type),
        "document_type_display": normalize_document_type(bid_data.document_type).upper(),
        "bid_number": bid_data.bid_number,
        "bid_date": bid_data.bid_date,
        "valid_through": bid_data.valid_through,
        "bid_due": bid_data.bid_due,
        "project_name": bid_data.project_name,
        "project_location": bid_data.project_location,
        "prepared_for": bid_data.prepared_for,
        "contact_information": bid_data.contact_information,
        "tax_rate_percent": str(bid_data.tax_rate_percent),
        "deposit_percent": str(bid_data.deposit_percent),
        "subtotal_display": format_currency(bid_data.subtotal),
        "sales_tax_amount_display": format_currency(bid_data.sales_tax_amount),
        "total_display": format_currency(bid_data.total),
        "required_deposit_display": format_currency(bid_data.required_deposit),
        "remaining_balance_display": format_currency(bid_data.remaining_balance),
        "lead_time": bid_data.lead_time,
        "pricing_valid_days": bid_data.pricing_valid_days,
        "additional_terms": bid_data.additional_terms,
        "include_prevailing_wage_statement": bid_data.include_prevailing_wage_statement,
        "prevailing_wage_statement": bid_data.prevailing_wage_statement,
        "include_alternate_pricing": bid_data.include_alternate_pricing,
        "alternate_pricing_total_display": format_currency(bid_data.alternate_pricing_total),
        "project_notes": bid_data.project_notes,
        "authorized_signer": bid_data.authorized_signer,
        "signature_date": bid_data.signature_date,
    }

    return {
        "bid": bid,
        "scope_items": bid_data.scope_items,
        "addenda_acknowledgements": bid_data.addenda_acknowledgements,
        "additional_terms_items": bid_data.additional_terms_items,
        "pricing_lines": pricing_lines,
        "alternate_pricing_lines": alternate_pricing_lines,
    }


def generate_docx_bid(bid_data: BidData, output_folder: Path) -> Path:
    """Render and save a DOCX bid proposal, returning the created path."""
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(f"DOCX template was not found: {TEMPLATE_PATH}")

    output_folder = Path(output_folder).expanduser()
    output_folder.mkdir(parents=True, exist_ok=True)

    template = DocxTemplate(str(TEMPLATE_PATH))
    template.render(build_render_context(bid_data))

    output_path = build_docx_output_path(output_folder, bid_data.project_name)
    template.save(output_path)
    return output_path
