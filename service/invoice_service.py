from decimal import Decimal
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from models.database import Invoice, InvoiceLine, InvoiceStatus
from models.schemas import InvoiceCreate, InvoiceLineResponse, InvoiceResponse, InvoiceListResponse, StatusUpdate
from repository.invoice_repo import InvoiceRepository


class InvoiceService:
    def __init__(self, db: Session):
        self.repo = InvoiceRepository(db)

    def create_invoice(self, data: InvoiceCreate) -> Invoice:
        # Totals are provided by the caller; invoice-service does not call external product APIs.
        lines = []
        for line_data in data.lines:
            lines.append(InvoiceLine(
                product_id=line_data.product_id,
                amount=line_data.amount,
                description=line_data.description,
                unit_price=line_data.unit_price,
            ))

        invoice = Invoice(
            invoice_number=self.repo.get_next_invoice_number(),
            partner_id=data.partner_id,
            company_id=data.company_id,
            partner_name=data.partner_name,
            company_name=data.company_name,
            user_id=data.user_id,
            comment=data.comment,
            issue_date=data.issue_date,
            due_date=data.due_date,
            status=InvoiceStatus.ISSUED,
            total=data.total,
            lines=lines
        )

        created = self.repo.create(invoice)
        return created

    def get_invoice(self, invoice_id: UUID) -> Optional[Invoice]:
        return self.repo.get_by_id(invoice_id)

    def list_invoices(self) -> List[Invoice]:
        return self.repo.get_all()

    def update_status(self, invoice_id: UUID, status_update: StatusUpdate) -> Optional[Invoice]:
        return self.repo.update_status(invoice_id, status_update.status)

    def create_invoice_response(self, data: InvoiceCreate) -> InvoiceResponse:
        invoice = self.create_invoice(data)
        return self._to_invoice_response(invoice)

    def get_invoice_response(self, invoice_id: UUID) -> Optional[InvoiceResponse]:
        invoice = self.get_invoice(invoice_id)
        if not invoice:
            return None
        return self._to_invoice_response(invoice)

    def list_invoice_responses(self) -> List[InvoiceListResponse]:
        invoices = self.list_invoices()
        return [
            InvoiceListResponse(
                id=inv.id,
                invoice_number=inv.invoice_number,
                partner_id=inv.partner_id,
                company_id=inv.company_id,
                partner_name=inv.partner_name,
                company_name=inv.company_name,
                user_id=inv.user_id,
                issue_date=inv.issue_date,
                due_date=inv.due_date,
                status=inv.status,
                total=Decimal(str(inv.total)),
                created_at=inv.created_at,
            )
            for inv in invoices
        ]

    def _to_invoice_response(self, invoice: Invoice) -> InvoiceResponse:
        # Build line responses from stored snapshot data (no product-service calls).
        line_responses: list[InvoiceLineResponse] = []
        for line in invoice.lines:
            unit_price = Decimal(str(line.unit_price))
            line_total = Decimal(line.amount) * unit_price
            line_responses.append(
                InvoiceLineResponse(
                    id=line.id,
                    invoice_id=line.invoice_id,
                    product_id=line.product_id,
                    amount=line.amount,
                    description=line.description,
                    unit_price=unit_price,
                    line_total=line_total,
                )
            )

        return InvoiceResponse(
            id=invoice.id,
            invoice_number=invoice.invoice_number,
            partner_id=invoice.partner_id,
            company_id=invoice.company_id,
            partner_name=invoice.partner_name,
            company_name=invoice.company_name,
            user_id=invoice.user_id,
            comment=invoice.comment,
            issue_date=invoice.issue_date,
            due_date=invoice.due_date,
            status=invoice.status,
            total=Decimal(str(invoice.total)),
            created_at=invoice.created_at,
            lines=line_responses,
        )

