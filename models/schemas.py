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
    product_id: UUID
    amount: int


class InvoiceLineCreate(InvoiceLineBase):
    pass


class InvoiceLineResponse(BaseModel):
    id: UUID
    invoice_id: UUID
    product_id: UUID
    amount: int
    description: str
    unit_price: Decimal
    line_total: Decimal

    class Config:
        from_attributes = False


# Invoice Schemas
class InvoiceBase(BaseModel):
    partner_id: UUID
    company_id: UUID
    user_id: UUID
    comment: Optional[str] = None
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
        from_attributes = False


class InvoiceListResponse(BaseModel):
    id: UUID
    invoice_number: str
    partner_id: UUID
    company_id: UUID
    user_id: UUID
    issue_date: datetime
    due_date: datetime
    status: InvoiceStatus
    total: Decimal
    created_at: datetime

    class Config:
        from_attributes = False


class StatusUpdate(BaseModel):
    status: InvoiceStatus

