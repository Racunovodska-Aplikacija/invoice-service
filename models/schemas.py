from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel


class InvoiceStatus(str, Enum):
    ISSUED = "ISSUED"
    PAID = "PAID"
    CANCELLED = "CANCELLED"


# Invoice Line Schemas
class InvoiceLineBase(BaseModel):
    description: str
    quantity: int
    unit_price: Decimal


class InvoiceLineCreate(InvoiceLineBase):
    pass


class InvoiceLineResponse(InvoiceLineBase):
    id: UUID
    invoice_id: UUID
    line_total: Decimal

    class Config:
        from_attributes = True


# Invoice Schemas
class InvoiceBase(BaseModel):
    customer_id: UUID
    issue_date: datetime
    due_date: datetime


class InvoiceCreate(InvoiceBase):
    lines: List[InvoiceLineCreate]


class InvoiceResponse(InvoiceBase):
    id: UUID
    invoice_number: str
    status: InvoiceStatus
    subtotal: Decimal
    tax_total: Decimal
    total: Decimal
    created_at: datetime
    lines: List[InvoiceLineResponse]

    class Config:
        from_attributes = True


class InvoiceListResponse(BaseModel):
    id: UUID
    invoice_number: str
    customer_id: UUID
    issue_date: datetime
    due_date: datetime
    status: InvoiceStatus
    total: Decimal
    created_at: datetime

    class Config:
        from_attributes = True


class StatusUpdate(BaseModel):
    status: InvoiceStatus

