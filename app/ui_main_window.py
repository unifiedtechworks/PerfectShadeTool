"""Main PySide6 window for the Perfect Shade Bid Generator."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.calculations import calculate_totals, format_currency, parse_money, parse_percent
from app.document_generator import generate_docx_bid
from app.models import DEFAULT_PREVAILING_WAGE_STATEMENT, BidData, PricingLine
from app.settings import (
    APP_NAME,
    DEFAULT_PRICING_ROWS,
    DEFAULT_SCOPE_ROWS,
    MAX_PRICING_LINES,
    MAX_SCOPE_ITEMS,
    MAX_ADDITIONAL_TERMS,
    MAX_ALTERNATE_PRICING_LINES,
)
from app.storage import save_bid_json


MEASUREMENT_READINESS_TEXT = (
    "Measurement Readiness: Final measurements should not be requested or scheduled until the project area is ready, accessible, and reasonably prepared for accurate measuring. "
    "If there are questions about site readiness, mounting conditions, product requirements, or any other measurement-related requirements, Customer/Contractor should contact Perfect Shade LLC before requesting or scheduling final measurements. "
    "Additional trips, re-measures, or delays caused by incomplete site conditions, inaccessible areas, unclear requirements, construction changes, or other conditions outside Perfect Shade LLC’s control may result in additional charges."
)
SALES_TAX_NOTICE_TEXT = "Applicable sales tax will be added unless a valid tax exemption certificate is provided."
RETAINAGE_TERM_TEXT = "Maximum retainage shall be limited to 5% of the contract amount unless otherwise agreed in writing."
CRAFTSMANSHIP_WARRANTY_TEXT = (
    "Perfect Shade provides a one-year craftsmanship warranty on installation labor. This warranty covers defects in workmanship under normal use and does not cover product defects, misuse, damage by others, changes to surrounding construction, or conditions outside Perfect Shade’s control."
)
COMPANY_QUALIFICATIONS_TEXT = (
    "Perfect Shade LLC is a locally owned and operated window covering company serving commercial, healthcare, municipal, educational, multifamily, and professional facilities throughout Eastern Oregon and Eastern Washington. "
    "We routinely assist with value engineering, product coordination, dependable project execution, and clean professional installation. Our lead installer has more than 15 years of experience installing window coverings throughout the Tri-Cities and surrounding region. "
    "References are available upon request."
)


class MainWindow(QMainWindow):
    """Primary application window with tabbed bid-entry workflow."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(1000, 760)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self._build_project_tab()
        self._build_scope_tab()
        self._build_pricing_tab()
        self._build_terms_tab()
        self._build_output_tab()
        self.update_totals()

    def _build_project_tab(self) -> None:
        tab = QWidget()
        layout = QFormLayout(tab)
        layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

        self.bid_number_edit = QLineEdit()
        self.document_type_combo = QComboBox()
        self.document_type_combo.addItems(["Bid Proposal", "Estimate"])
        self.bid_date_edit = QLineEdit()
        self.valid_through_edit = QLineEdit()
        self.bid_due_edit = QLineEdit()
        self.project_name_edit = QLineEdit()
        self.project_location_edit = QLineEdit()
        self.prepared_for_edit = QLineEdit()
        self.contact_information_edit = QTextEdit()
        self.contact_information_edit.setMinimumHeight(90)

        layout.addRow("Document Type", self.document_type_combo)
        layout.addRow("Bid Number", self.bid_number_edit)
        layout.addRow("Bid Date", self.bid_date_edit)
        layout.addRow("Valid Through", self.valid_through_edit)
        layout.addRow("Bid Due", self.bid_due_edit)
        layout.addRow("Project Name *", self.project_name_edit)
        layout.addRow("Project Location", self.project_location_edit)
        layout.addRow("Architect *", self.prepared_for_edit)
        layout.addRow("Owner", self.contact_information_edit)

        self.tabs.addTab(tab, "Project")

    def _build_scope_tab(self) -> None:
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.scope_table = QTableWidget(0, 1)
        self.scope_table.setHorizontalHeaderLabels(["Scope Item"])
        self.scope_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.scope_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.scope_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.scope_table.verticalHeader().setVisible(False)

        button_layout = QHBoxLayout()
        add_button = QPushButton("Add Scope Item")
        remove_button = QPushButton("Remove Selected Scope Item")
        add_button.clicked.connect(self.add_scope_row)
        remove_button.clicked.connect(self.remove_scope_row)
        button_layout.addWidget(add_button)
        button_layout.addWidget(remove_button)
        button_layout.addStretch()

        layout.addWidget(self.scope_table)
        layout.addLayout(button_layout)

        for _ in range(DEFAULT_SCOPE_ROWS):
            self.add_scope_row()

        self.tabs.addTab(tab, "Scope of Work")

    def _build_pricing_tab(self) -> None:
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.pricing_table = QTableWidget(0, 2)
        self.pricing_table.setHorizontalHeaderLabels(["Description", "Amount"])
        self.pricing_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.pricing_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.pricing_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.pricing_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.pricing_table.verticalHeader().setVisible(False)
        self.pricing_table.itemChanged.connect(self.update_totals)

        button_layout = QHBoxLayout()
        add_button = QPushButton("Add Pricing Line")
        remove_button = QPushButton("Remove Selected Pricing Line")
        add_button.clicked.connect(self.add_pricing_row)
        remove_button.clicked.connect(self.remove_pricing_row)
        button_layout.addWidget(add_button)
        button_layout.addWidget(remove_button)
        button_layout.addStretch()

        totals_box = QGroupBox("Totals")
        totals_layout = QGridLayout(totals_box)
        self.subtotal_value = QLabel("$0.00")
        self.total_value = QLabel("$0.00")
        self.deposit_percent_edit = QLineEdit("0")
        self.required_deposit_value = QLabel("$0.00")
        self.remaining_balance_value = QLabel("$0.00")
        self.deposit_percent_edit.textChanged.connect(self.update_totals)

        totals_layout.addWidget(QLabel("Subtotal"), 0, 0)
        totals_layout.addWidget(self.subtotal_value, 0, 1)
        totals_layout.addWidget(QLabel("Total"), 1, 0)
        totals_layout.addWidget(self.total_value, 1, 1)
        totals_layout.addWidget(QLabel("Deposit %"), 2, 0)
        totals_layout.addWidget(self.deposit_percent_edit, 2, 1)
        totals_layout.addWidget(QLabel("Required Deposit"), 3, 0)
        totals_layout.addWidget(self.required_deposit_value, 3, 1)
        totals_layout.addWidget(QLabel("Remaining Balance"), 4, 0)
        totals_layout.addWidget(self.remaining_balance_value, 4, 1)

        layout.addWidget(self.pricing_table)
        layout.addLayout(button_layout)

        alternate_box = QGroupBox("Alternate Pricing")
        alternate_layout = QVBoxLayout(alternate_box)
        self.include_alternate_pricing_checkbox = QCheckBox("Include Alternate Pricing")
        self.alternate_pricing_table = QTableWidget(0, 2)
        self.alternate_pricing_table.setHorizontalHeaderLabels(["Description", "Amount"])
        self.alternate_pricing_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.alternate_pricing_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.alternate_pricing_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.alternate_pricing_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.alternate_pricing_table.verticalHeader().setVisible(False)
        alternate_buttons = QHBoxLayout()
        add_alternate_button = QPushButton("Add Alternate Price")
        remove_alternate_button = QPushButton("Remove Selected Alternate Price")
        add_alternate_button.clicked.connect(self.add_alternate_pricing_row)
        remove_alternate_button.clicked.connect(self.remove_alternate_pricing_row)
        alternate_buttons.addWidget(add_alternate_button)
        alternate_buttons.addWidget(remove_alternate_button)
        alternate_buttons.addStretch()
        alternate_layout.addWidget(self.include_alternate_pricing_checkbox)
        alternate_layout.addWidget(self.alternate_pricing_table)
        alternate_layout.addLayout(alternate_buttons)
        self.add_alternate_pricing_row()

        layout.addWidget(alternate_box)
        layout.addWidget(totals_box)

        for _ in range(DEFAULT_PRICING_ROWS):
            self.add_pricing_row()

        self.tabs.addTab(tab, "Pricing")

    def _build_terms_tab(self) -> None:
        tab = QWidget()
        outer_layout = QVBoxLayout(tab)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        content = QWidget()
        page_layout = QVBoxLayout(content)

        self.lead_time_edit = QLineEdit()
        self.pricing_valid_days_edit = QLineEdit()
        self.include_prevailing_wage_checkbox = QCheckBox("Include Prevailing Wage Statement")
        self.prevailing_wage_statement_edit = QTextEdit()
        self.prevailing_wage_statement_edit.setPlainText(DEFAULT_PREVAILING_WAGE_STATEMENT)
        self.prevailing_wage_statement_edit.setMinimumHeight(70)
        self.project_notes_edit = QTextEdit()
        self.authorized_signer_edit = QLineEdit()
        self.signature_date_edit = QLineEdit()
        self.project_notes_edit.setMinimumHeight(120)

        addenda_box = QGroupBox("Addenda Acknowledgement")
        addenda_layout = QVBoxLayout(addenda_box)
        self.addenda_table = QTableWidget(0, 1)
        self.addenda_table.setHorizontalHeaderLabels(["Addendum"])
        self.addenda_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.addenda_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.addenda_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.addenda_table.verticalHeader().setVisible(False)

        addenda_buttons = QHBoxLayout()
        add_addendum_button = QPushButton("Add Addendum")
        remove_addendum_button = QPushButton("Remove Selected Addendum")
        add_addendum_button.clicked.connect(self.add_addendum_row)
        remove_addendum_button.clicked.connect(self.remove_addendum_row)
        addenda_buttons.addWidget(add_addendum_button)
        addenda_buttons.addWidget(remove_addendum_button)
        addenda_buttons.addStretch()

        addenda_layout.addWidget(self.addenda_table)
        addenda_layout.addLayout(addenda_buttons)
        self.add_addendum_row()

        page_layout.addWidget(addenda_box)

        core_terms_box = QGroupBox("Core Terms / Deposit / Pricing Valid / Lead Time")
        core_terms_layout = QFormLayout(core_terms_box)
        core_terms_layout.addRow("Pricing Valid For Days", self.pricing_valid_days_edit)
        core_terms_layout.addRow("Estimated Lead Time", self.lead_time_edit)
        retainage_preview = QTextEdit()
        retainage_preview.setPlainText(RETAINAGE_TERM_TEXT)
        retainage_preview.setReadOnly(True)
        retainage_preview.setMinimumHeight(55)
        core_terms_layout.addRow("Retainage", retainage_preview)
        page_layout.addWidget(core_terms_box)

        page_layout.addWidget(self._read_only_preview_group("Sales Tax Notice", SALES_TAX_NOTICE_TEXT))

        prevailing_wage_box = QGroupBox("Prevailing Wage")
        prevailing_wage_layout = QVBoxLayout(prevailing_wage_box)
        prevailing_wage_layout.addWidget(self.include_prevailing_wage_checkbox)
        prevailing_wage_layout.addWidget(self.prevailing_wage_statement_edit)
        page_layout.addWidget(prevailing_wage_box)

        terms_box = QGroupBox("Additional Terms / Exclusions")
        terms_layout = QVBoxLayout(terms_box)
        self.additional_terms_table = QTableWidget(0, 1)
        self.additional_terms_table.setHorizontalHeaderLabels(["Term / Exclusion"])
        self.additional_terms_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.additional_terms_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.additional_terms_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.additional_terms_table.verticalHeader().setVisible(False)
        self.additional_terms_table.verticalHeader().setDefaultSectionSize(32)
        self.additional_terms_table.setMinimumHeight(170)
        term_buttons = QHBoxLayout()
        add_term_button = QPushButton("Add Term / Exclusion")
        remove_term_button = QPushButton("Remove Selected Term / Exclusion")
        add_term_button.clicked.connect(self.add_additional_term_row)
        remove_term_button.clicked.connect(self.remove_additional_term_row)
        term_buttons.addWidget(add_term_button)
        term_buttons.addWidget(remove_term_button)
        term_buttons.addStretch()
        terms_layout.addWidget(self.additional_terms_table)
        terms_layout.addLayout(term_buttons)
        self.add_additional_term_row()
        page_layout.addWidget(terms_box)

        page_layout.addWidget(self._read_only_preview_group("Measurement Readiness", MEASUREMENT_READINESS_TEXT))
        page_layout.addWidget(self._read_only_preview_group("Craftsmanship Warranty", CRAFTSMANSHIP_WARRANTY_TEXT))
        page_layout.addWidget(self._read_only_preview_group("Company Qualifications", COMPANY_QUALIFICATIONS_TEXT))

        notes_box = QGroupBox("Project Notes")
        notes_layout = QVBoxLayout(notes_box)
        notes_layout.addWidget(self.project_notes_edit)
        page_layout.addWidget(notes_box)

        signature_box = QGroupBox("Signature / Authorization")
        signature_layout = QFormLayout(signature_box)
        signature_layout.addRow("Perfect Shade Authorized Signer", self.authorized_signer_edit)
        signature_layout.addRow("Signature Date", self.signature_date_edit)
        page_layout.addWidget(signature_box)

        page_layout.addStretch()
        scroll_area.setWidget(content)
        outer_layout.addWidget(scroll_area)

        self.tabs.addTab(tab, "Terms & Notes")

    def _read_only_preview_group(self, title: str, text: str) -> QGroupBox:
        group = QGroupBox(title)
        layout = QVBoxLayout(group)
        preview = QTextEdit()
        preview.setPlainText(text)
        preview.setReadOnly(True)
        preview.setMinimumHeight(90)
        layout.addWidget(preview)
        return group

    def _build_output_tab(self) -> None:
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.create_docx_checkbox = QCheckBox("Create DOCX")
        self.create_docx_checkbox.setChecked(True)
        self.create_pdf_checkbox = QCheckBox("Create PDF")
        self.create_pdf_checkbox.setEnabled(False)
        self.create_pdf_checkbox.setToolTip("PDF generation will be added in a future task.")

        output_folder_layout = QHBoxLayout()
        self.output_folder_edit = QLineEdit(str(Path.cwd() / "output"))
        browse_button = QPushButton("Select Output Folder")
        browse_button.clicked.connect(self.select_output_folder)
        output_folder_layout.addWidget(self.output_folder_edit)
        output_folder_layout.addWidget(browse_button)

        create_button = QPushButton("Create Bid")
        create_button.clicked.connect(self.create_bid)

        info = QLabel(
            "Create Bid always saves JSON. If Create DOCX is checked, a Word bid proposal is also generated. PDF export is not implemented yet."
        )
        info.setWordWrap(True)

        layout.addWidget(self.create_docx_checkbox)
        layout.addWidget(self.create_pdf_checkbox)
        layout.addWidget(QLabel("Output Folder"))
        layout.addLayout(output_folder_layout)
        layout.addSpacing(20)
        layout.addWidget(info)
        layout.addWidget(create_button, alignment=Qt.AlignLeft)
        layout.addStretch()

        self.tabs.addTab(tab, "Output")

    def add_scope_row(self) -> None:
        if self.scope_table.rowCount() >= MAX_SCOPE_ITEMS:
            self.show_error(f"Scope of work supports up to {MAX_SCOPE_ITEMS} items.")
            return
        row = self.scope_table.rowCount()
        self.scope_table.insertRow(row)
        self.scope_table.setItem(row, 0, QTableWidgetItem(""))

    def remove_scope_row(self) -> None:
        row = self.scope_table.currentRow()
        if row >= 0:
            self.scope_table.removeRow(row)

    def add_addendum_row(self) -> None:
        row = self.addenda_table.rowCount()
        self.addenda_table.insertRow(row)
        self.addenda_table.setItem(row, 0, QTableWidgetItem(""))

    def remove_addendum_row(self) -> None:
        row = self.addenda_table.currentRow()
        if row >= 0:
            self.addenda_table.removeRow(row)

    def add_additional_term_row(self) -> None:
        if self.additional_terms_table.rowCount() >= MAX_ADDITIONAL_TERMS:
            self.show_error(f"Additional terms support up to {MAX_ADDITIONAL_TERMS} items.")
            return
        row = self.additional_terms_table.rowCount()
        self.additional_terms_table.insertRow(row)
        self.additional_terms_table.setItem(row, 0, QTableWidgetItem(""))

    def remove_additional_term_row(self) -> None:
        row = self.additional_terms_table.currentRow()
        if row >= 0:
            self.additional_terms_table.removeRow(row)

    def add_alternate_pricing_row(self) -> None:
        if self.alternate_pricing_table.rowCount() >= MAX_ALTERNATE_PRICING_LINES:
            self.show_error(f"Alternate pricing supports up to {MAX_ALTERNATE_PRICING_LINES} lines.")
            return
        row = self.alternate_pricing_table.rowCount()
        self.alternate_pricing_table.insertRow(row)
        self.alternate_pricing_table.setItem(row, 0, QTableWidgetItem(""))
        self.alternate_pricing_table.setItem(row, 1, QTableWidgetItem(""))

    def remove_alternate_pricing_row(self) -> None:
        row = self.alternate_pricing_table.currentRow()
        if row >= 0:
            self.alternate_pricing_table.removeRow(row)

    def add_pricing_row(self) -> None:
        if self.pricing_table.rowCount() >= MAX_PRICING_LINES:
            self.show_error(f"Pricing supports up to {MAX_PRICING_LINES} lines.")
            return
        row = self.pricing_table.rowCount()
        self.pricing_table.insertRow(row)
        self.pricing_table.setItem(row, 0, QTableWidgetItem(""))
        self.pricing_table.setItem(row, 1, QTableWidgetItem(""))

    def remove_pricing_row(self) -> None:
        row = self.pricing_table.currentRow()
        if row >= 0:
            self.pricing_table.removeRow(row)
            self.update_totals()

    def select_output_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder", self.output_folder_edit.text())
        if folder:
            self.output_folder_edit.setText(folder)

    def table_text(self, table: QTableWidget, row: int, column: int) -> str:
        item = table.item(row, column)
        return item.text().strip() if item else ""

    def collect_scope_items(self) -> list[str]:
        return [
            self.table_text(self.scope_table, row, 0)
            for row in range(self.scope_table.rowCount())
            if self.table_text(self.scope_table, row, 0)
        ]

    def collect_addenda_acknowledgements(self) -> list[str]:
        return [
            self.table_text(self.addenda_table, row, 0)
            for row in range(self.addenda_table.rowCount())
            if self.table_text(self.addenda_table, row, 0)
        ]

    def collect_additional_terms_items(self) -> list[str]:
        return [
            self.table_text(self.additional_terms_table, row, 0)
            for row in range(self.additional_terms_table.rowCount())
            if self.table_text(self.additional_terms_table, row, 0)
        ]

    def collect_pricing_lines(self, require_valid: bool = True) -> list[PricingLine]:
        lines: list[PricingLine] = []
        for row in range(self.pricing_table.rowCount()):
            description = self.table_text(self.pricing_table, row, 0)
            amount_text = self.table_text(self.pricing_table, row, 1)
            if not description and not amount_text:
                continue
            if not amount_text:
                if require_valid:
                    raise ValueError(f"Pricing line {row + 1} needs an amount.")
                continue
            amount = parse_money(amount_text)
            lines.append(PricingLine(description=description, amount=amount))
        return lines

    def collect_alternate_pricing_lines(self, require_valid: bool = True) -> list[PricingLine]:
        lines: list[PricingLine] = []
        for row in range(self.alternate_pricing_table.rowCount()):
            description = self.table_text(self.alternate_pricing_table, row, 0)
            amount_text = self.table_text(self.alternate_pricing_table, row, 1)
            if not description and not amount_text:
                continue
            if not amount_text:
                if require_valid:
                    raise ValueError(f"Alternate pricing line {row + 1} needs an amount.")
                continue
            amount = parse_money(amount_text)
            lines.append(PricingLine(description=description, amount=amount))
        return lines

    def current_totals(self) -> tuple[Decimal, Decimal, object]:
        tax_rate = Decimal("0")
        deposit_percent = parse_percent(self.deposit_percent_edit.text(), "Deposit %")
        pricing_lines = self.collect_pricing_lines(require_valid=False)
        totals = calculate_totals([line.amount for line in pricing_lines], tax_rate, deposit_percent)
        return tax_rate, deposit_percent, totals

    def update_totals(self) -> None:
        try:
            _, _, totals = self.current_totals()
        except ValueError:
            return

        self.subtotal_value.setText(format_currency(totals.subtotal))
        self.total_value.setText(format_currency(totals.total))
        self.required_deposit_value.setText(format_currency(totals.required_deposit))
        self.remaining_balance_value.setText(format_currency(totals.remaining_balance))

    def build_bid_data(self) -> BidData:
        project_name = self.project_name_edit.text().strip()
        prepared_for = self.prepared_for_edit.text().strip()
        if not project_name:
            raise ValueError("Project Name is required.")
        if not prepared_for:
            raise ValueError("Architect is required.")

        tax_rate, deposit_percent, totals = self.current_totals()
        if deposit_percent < 0 or deposit_percent > 100:
            raise ValueError("Deposit % must be between 0 and 100.")

        pricing_lines = self.collect_pricing_lines(require_valid=True)
        if not pricing_lines:
            raise ValueError("At least one pricing line with a valid amount is required.")

        alternate_pricing_lines = self.collect_alternate_pricing_lines(
            require_valid=self.include_alternate_pricing_checkbox.isChecked()
        )
        if self.include_alternate_pricing_checkbox.isChecked() and not alternate_pricing_lines:
            raise ValueError(
                "Include Alternate Pricing is checked, but no valid alternate pricing rows were entered."
            )
        alternate_pricing_total = sum((line.amount for line in alternate_pricing_lines), Decimal("0.00"))

        output_folder = self.output_folder_edit.text().strip()
        if not output_folder:
            raise ValueError("Please select an output folder.")

        return BidData(
            document_type=self.document_type_combo.currentText(),
            bid_number=self.bid_number_edit.text().strip(),
            bid_date=self.bid_date_edit.text().strip(),
            valid_through=self.valid_through_edit.text().strip(),
            bid_due=self.bid_due_edit.text().strip(),
            project_name=project_name,
            project_location=self.project_location_edit.text().strip(),
            prepared_for=prepared_for,
            contact_information=self.contact_information_edit.toPlainText().strip(),
            scope_items=self.collect_scope_items(),
            addenda_acknowledgements=self.collect_addenda_acknowledgements(),
            additional_terms_items=self.collect_additional_terms_items(),
            pricing_lines=pricing_lines,
            include_alternate_pricing=self.include_alternate_pricing_checkbox.isChecked(),
            alternate_pricing_lines=alternate_pricing_lines,
            alternate_pricing_total=alternate_pricing_total,
            tax_rate_percent=tax_rate,
            deposit_percent=deposit_percent,
            subtotal=totals.subtotal,
            sales_tax_amount=totals.sales_tax_amount,
            total=totals.total,
            required_deposit=totals.required_deposit,
            remaining_balance=totals.remaining_balance,
            lead_time=self.lead_time_edit.text().strip(),
            pricing_valid_days=self.pricing_valid_days_edit.text().strip(),
            additional_terms="\n".join(self.collect_additional_terms_items()),
            include_prevailing_wage_statement=self.include_prevailing_wage_checkbox.isChecked(),
            prevailing_wage_statement=self.prevailing_wage_statement_edit.toPlainText().strip()
            or DEFAULT_PREVAILING_WAGE_STATEMENT,
            project_notes=self.project_notes_edit.toPlainText().strip(),
            authorized_signer=self.authorized_signer_edit.text().strip(),
            signature_date=self.signature_date_edit.text().strip(),
            create_docx=self.create_docx_checkbox.isChecked(),
            create_pdf=self.create_pdf_checkbox.isChecked(),
            output_folder=output_folder,
        )

    def create_bid(self) -> None:
        try:
            bid_data = self.build_bid_data()
            created_files = [save_bid_json(bid_data)]
            if bid_data.create_docx:
                created_files.append(generate_docx_bid(bid_data, Path(bid_data.output_folder)))
        except ValueError as exc:
            self.show_error(str(exc))
            return
        except OSError as exc:
            self.show_error(f"Could not save bid files:\n{exc}")
            return
        except Exception as exc:
            self.show_error(f"Could not generate DOCX bid document:\n{exc}")
            return

        files_text = "\n".join(str(path) for path in created_files)
        QMessageBox.information(self, "Bid Saved", f"Bid files saved successfully:\n{files_text}")

    def show_error(self, message: str) -> None:
        QMessageBox.warning(self, "Please Check Bid Details", message)
