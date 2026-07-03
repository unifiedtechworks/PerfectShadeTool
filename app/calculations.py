"""Money parsing, calculation, and formatting helpers."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import re


MONEY_QUANT = Decimal("0.01")


@dataclass(frozen=True)
class BidTotals:
    subtotal: Decimal
    sales_tax_amount: Decimal
    total: Decimal
    required_deposit: Decimal
    remaining_balance: Decimal


def quantize_money(value: Decimal) -> Decimal:
    """Round money consistently to two decimal places."""
    return value.quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


def parse_money(value: str) -> Decimal:
    """Parse money strings like 1000, 1000.50, or $1,000.50."""
    cleaned = str(value).strip()
    if not cleaned:
        raise ValueError("Amount is required.")

    cleaned = cleaned.replace("$", "").replace(",", "")
    if not re.fullmatch(r"-?\d+(\.\d{1,2})?", cleaned):
        raise ValueError(f"Invalid amount: {value}")

    try:
        return quantize_money(Decimal(cleaned))
    except InvalidOperation as exc:
        raise ValueError(f"Invalid amount: {value}") from exc


def parse_percent(value: str, field_name: str) -> Decimal:
    """Parse a percentage field into Decimal."""
    cleaned = str(value).strip().replace("%", "")
    if not cleaned:
        cleaned = "0"
    try:
        return Decimal(cleaned)
    except InvalidOperation as exc:
        raise ValueError(f"{field_name} must be a valid number.") from exc


def calculate_totals(
    pricing_amounts: list[Decimal], tax_rate_percent: Decimal, deposit_percent: Decimal
) -> BidTotals:
    """Calculate bid totals using Decimal arithmetic.

    ``tax_rate_percent`` is retained for backward compatibility with older saved data,
    but sales tax is not included in proposal totals.
    """
    subtotal = quantize_money(sum(pricing_amounts, Decimal("0")))
    sales_tax_amount = Decimal("0.00")
    total = subtotal
    required_deposit = quantize_money(total * (deposit_percent / Decimal("100")))
    remaining_balance = quantize_money(total - required_deposit)
    return BidTotals(
        subtotal=subtotal,
        sales_tax_amount=sales_tax_amount,
        total=total,
        required_deposit=required_deposit,
        remaining_balance=remaining_balance,
    )


def format_currency(value: Decimal) -> str:
    """Format Decimal money as dollars with two decimals."""
    return f"${quantize_money(value):,.2f}"


def decimal_to_json(value: Decimal) -> str:
    """Convert Decimal to a JSON-friendly fixed-point string."""
    return f"{quantize_money(value):.2f}"
