from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from models.database import Invoice, InvoiceLine, InvoiceStatus


class InvoiceRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, invoice: Invoice) -> Invoice:
        self.db.add(invoice)
        self.db.commit()
        self.db.refresh(invoice)
        return invoice

    def get_by_id(self, invoice_id: UUID) -> Optional[Invoice]:
        return self.db.query(Invoice).filter(Invoice.id == invoice_id).first()

    def get_all(self) -> List[Invoice]:
        return self.db.query(Invoice).order_by(Invoice.created_at.desc()).all()

    def update_status(self, invoice_id: UUID, status: InvoiceStatus) -> Optional[Invoice]:
        invoice = self.get_by_id(invoice_id)
        if invoice:
            invoice.status = status
            self.db.commit()
            self.db.refresh(invoice)
        return invoice

    def get_next_invoice_number(self) -> str:
        count = self.db.query(Invoice).count()
        return f"INV-{count + 1:06d}"

