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

    def get_by_id(self, invoice_id: UUID, user_id: str = None) -> Optional[Invoice]:
        query = self.db.query(Invoice).filter(Invoice.id == invoice_id)
        if user_id:
            query = query.filter(Invoice.user_id == user_id)
        return query.first()

    def get_all(self, user_id: str = None) -> List[Invoice]:
        query = self.db.query(Invoice)
        if user_id:
            query = query.filter(Invoice.user_id == user_id)
        return query.order_by(Invoice.issue_date.desc()).all()

    def update(self, invoice: Invoice) -> Invoice:
        self.db.commit()
        self.db.refresh(invoice)
        return invoice

    def delete(self, invoice_id: UUID, user_id: str = None) -> bool:
        query = self.db.query(Invoice).filter(Invoice.id == invoice_id)
        if user_id:
            query = query.filter(Invoice.user_id == user_id)
        invoice = query.first()
        if invoice:
            self.db.delete(invoice)
            self.db.commit()
            return True
        return False

    def get_next_invoice_number(self) -> str:
        count = self.db.query(Invoice).count()
        return f"INV-{count + 1:06d}"

