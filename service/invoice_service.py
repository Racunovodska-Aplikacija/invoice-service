from decimal import Decimal
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from models.database import Invoice, InvoiceLine, InvoiceStatus
from models.schemas import InvoiceCreate, StatusUpdate
from repository.invoice_repo import InvoiceRepository


TAX_RATE = Decimal("0.22")  # 22% tax


class InvoiceService:
    def __init__(self, db: Session):
        self.repo = InvoiceRepository(db)

    def create_invoice(self, data: InvoiceCreate) -> Invoice:
        # Calculate totals
        subtotal = Decimal("0")
        lines = []
        for line_data in data.lines:
            line_total = line_data.quantity * line_data.unit_price
            subtotal += line_total
            lines.append(InvoiceLine(
                description=line_data.description,
                quantity=line_data.quantity,
                unit_price=line_data.unit_price,
                line_total=line_total
            ))

        tax_total = subtotal * TAX_RATE
        total = subtotal + tax_total

        invoice = Invoice(
            invoice_number=self.repo.get_next_invoice_number(),
            customer_id=data.customer_id,
            issue_date=data.issue_date,
            due_date=data.due_date,
            status=InvoiceStatus.ISSUED,
            subtotal=subtotal,
            tax_total=tax_total,
            total=total,
            lines=lines
        )

        return self.repo.create(invoice)

    def get_invoice(self, invoice_id: UUID) -> Optional[Invoice]:
        return self.repo.get_by_id(invoice_id)

    def list_invoices(self) -> List[Invoice]:
        return self.repo.get_all()

    def update_status(self, invoice_id: UUID, status_update: StatusUpdate) -> Optional[Invoice]:
        return self.repo.update_status(invoice_id, status_update.status)

