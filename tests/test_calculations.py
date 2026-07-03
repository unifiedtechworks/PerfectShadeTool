"""Tests for proposal money parsing and base-total calculations."""

from decimal import Decimal

import pytest

from app.calculations import calculate_totals, parse_money


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("1000", Decimal("1000.00")),
        ("1000.50", Decimal("1000.50")),
        ("$1,000.50", Decimal("1000.50")),
    ],
)
def test_parse_money_accepts_supported_formats(value: str, expected: Decimal) -> None:
    assert parse_money(value) == expected


@pytest.mark.parametrize("value", ["", "one thousand", "12.345", "$1,2x0.00"])
def test_parse_money_rejects_invalid_values(value: str) -> None:
    with pytest.raises(ValueError):
        parse_money(value)


def test_calculate_totals_keeps_tax_outside_proposal_total() -> None:
    totals = calculate_totals(
        [Decimal("1000.00"), Decimal("250.50")],
        tax_rate_percent=Decimal("8.6"),
        deposit_percent=Decimal("20"),
    )

    assert totals.subtotal == Decimal("1250.50")
    assert totals.sales_tax_amount == Decimal("0.00")
    assert totals.total == Decimal("1250.50")
    assert totals.required_deposit == Decimal("250.10")
    assert totals.remaining_balance == Decimal("1000.40")
