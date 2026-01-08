import uuid
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, Enum, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class InvoiceStatus(str, PyEnum):
    ISSUED = "ISSUED"
    PAID = "PAID"
    CANCELLED = "CANCELLED"


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    company_id = Column(UUID(as_uuid=True), nullable=False)
    partner_id = Column(UUID(as_uuid=True), nullable=False)
    invoice_number = Column(String, unique=False, nullable=False)
    issue_date = Column(DateTime, nullable=False)
    service_date = Column(DateTime, nullable=False)
    due_date = Column(DateTime, nullable=False)
    notes = Column(Text, nullable=True)
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.ISSUED, nullable=False)
    company_name = Column(String, nullable=True)  # Snapshot for list display
    partner_name = Column(String, nullable=True)  # Snapshot for list display
    total = Column(Numeric(10, 2), nullable=True)  # Snapshot for list display

    lines = relationship("InvoiceLine", back_populates="invoice", cascade="all, delete-orphan")


class InvoiceLine(Base):
    __tablename__ = "invoice_lines"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), nullable=False)
    amount = Column(Integer, nullable=False)

    invoice = relationship("Invoice", back_populates="lines")

