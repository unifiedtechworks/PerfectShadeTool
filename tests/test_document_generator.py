"""Tests for data passed to the DOCX template renderer."""

from decimal import Decimal

from app.document_generator import build_render_context
from app.models import BidData, PricingLine


def test_render_context_contains_optional_proposal_sections() -> None:
    bid_data = BidData(
        project_name="Library Shades",
        addenda_acknowledgements=["Addendum 1", "Addendum 2"],
        additional_terms_items=["Electrical work by others", "Existing blocking required"],
        pricing_lines=[PricingLine("Base scope", Decimal("1000.00"))],
        subtotal=Decimal("1000.00"),
        total=Decimal("1000.00"),
        include_prevailing_wage_statement=True,
        prevailing_wage_statement="Applicable prevailing wage rates are included.",
        include_alternate_pricing=True,
        alternate_pricing_lines=[PricingLine("Motorized option", Decimal("275.00"))],
        alternate_pricing_total=Decimal("275.00"),
    )

    context = build_render_context(bid_data)

    assert context["addenda_acknowledgements"] == ["Addendum 1", "Addendum 2"]
    assert context["additional_terms_items"] == [
        "Electrical work by others",
        "Existing blocking required",
    ]
    assert context["bid"]["include_prevailing_wage_statement"] is True
    assert context["bid"]["prevailing_wage_statement"] == (
        "Applicable prevailing wage rates are included."
    )
    assert context["bid"]["include_alternate_pricing"] is True
    assert context["alternate_pricing_lines"] == [
        {"description": "Motorized option", "amount_display": "$275.00"}
    ]


def test_alternate_pricing_stays_separate_from_base_totals_in_context() -> None:
    bid_data = BidData(
        pricing_lines=[PricingLine("Base scope", Decimal("1000.00"))],
        subtotal=Decimal("1000.00"),
        total=Decimal("1000.00"),
        include_alternate_pricing=True,
        alternate_pricing_lines=[PricingLine("Alternate", Decimal("500.00"))],
        alternate_pricing_total=Decimal("500.00"),
    )

    context = build_render_context(bid_data)

    assert context["bid"]["subtotal_display"] == "$1,000.00"
    assert context["bid"]["total_display"] == "$1,000.00"
    assert context["bid"]["alternate_pricing_total_display"] == "$500.00"
