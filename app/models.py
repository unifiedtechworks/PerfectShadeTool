"""Data models for bid information."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from decimal import Decimal

from app.calculations import decimal_to_json


SUPPORTED_DOCUMENT_TYPES = {"Bid Proposal", "Estimate"}
DEFAULT_PREVAILING_WAGE_STATEMENT = (
    "Applicable prevailing wage labor rates are included where required by the project."
)


def normalize_document_type(value: str | None) -> str:
    return value if value in SUPPORTED_DOCUMENT_TYPES else "Bid Proposal"


@dataclass
class PricingLine:
    description: str = ""
    amount: Decimal = Decimal("0.00")

    def to_dict(self) -> dict[str, str]:
        return {
            "description": self.description,
            "amount": decimal_to_json(self.amount),
        }


@dataclass
class BidData:
    document_type: str = "Bid Proposal"
    bid_number: str = ""
    bid_date: str = ""
    valid_through: str = ""
    bid_due: str = ""
    project_name: str = ""
    project_location: str = ""
    prepared_for: str = ""
    contact_information: str = ""
    scope_items: list[str] = field(default_factory=list)
    addenda_acknowledgements: list[str] = field(default_factory=list)
    additional_terms_items: list[str] = field(default_factory=list)
    pricing_lines: list[PricingLine] = field(default_factory=list)
    include_alternate_pricing: bool = False
    alternate_pricing_lines: list[PricingLine] = field(default_factory=list)
    alternate_pricing_total: Decimal = Decimal("0.00")
    tax_rate_percent: Decimal = Decimal("0")
    deposit_percent: Decimal = Decimal("0")
    subtotal: Decimal = Decimal("0.00")
    sales_tax_amount: Decimal = Decimal("0.00")
    total: Decimal = Decimal("0.00")
    required_deposit: Decimal = Decimal("0.00")
    remaining_balance: Decimal = Decimal("0.00")
    lead_time: str = ""
    pricing_valid_days: str = ""
    additional_terms: str = ""
    include_prevailing_wage_statement: bool = False
    prevailing_wage_statement: str = DEFAULT_PREVAILING_WAGE_STATEMENT
    project_notes: str = ""
    authorized_signer: str = ""
    signature_date: str = ""
    create_docx: bool = True
    create_pdf: bool = False
    output_folder: str = ""

    def __post_init__(self) -> None:
        self.document_type = normalize_document_type(self.document_type)

    def to_dict(self) -> dict:
        data = asdict(self)
        data["pricing_lines"] = [line.to_dict() for line in self.pricing_lines]
        data["alternate_pricing_lines"] = [line.to_dict() for line in self.alternate_pricing_lines]
        for key in (
            "alternate_pricing_total",
            "tax_rate_percent",
            "deposit_percent",
            "subtotal",
            "sales_tax_amount",
            "total",
            "required_deposit",
            "remaining_balance",
        ):
            data[key] = decimal_to_json(getattr(self, key))
        return data
