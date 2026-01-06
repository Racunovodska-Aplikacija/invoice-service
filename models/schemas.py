from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
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
    product: Optional[Dict[str, Any]] = None  # gRPC product data

    class Config:
        from_attributes = True


# Invoice Schemas
class InvoiceBase(BaseModel):
    company_id: UUID
    partner_id: UUID
    issue_date: datetime
    service_date: datetime
    due_date: datetime
    notes: Optional[str] = None


class InvoiceCreate(BaseModel):
    company_id: UUID
    partner_id: UUID
    invoice_number: str
    issue_date: datetime
    service_date: datetime
    due_date: datetime
    notes: Optional[str] = None
    lines: List[InvoiceLineCreate]


class InvoiceUpdate(BaseModel):
    company_id: Optional[UUID] = None
    partner_id: Optional[UUID] = None
    issue_date: Optional[datetime] = None
    service_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    notes: Optional[str] = None
    status: Optional[InvoiceStatus] = None
    lines: Optional[List[InvoiceLineCreate]] = None


class InvoiceResponse(BaseModel):
    id: UUID
    user_id: UUID
    company_id: UUID
    partner_id: UUID
    invoice_number: str
    issue_date: datetime
    service_date: datetime
    due_date: datetime
    notes: Optional[str]
    status: InvoiceStatus
    lines: List[InvoiceLineResponse]
    company: Optional[Dict[str, Any]] = None  # gRPC company data
    partner: Optional[Dict[str, Any]] = None  # gRPC partner data

    class Config:
        from_attributes = True


class InvoiceListResponse(BaseModel):
    id: UUID
    user_id: UUID
    company_id: UUID
    partner_id: UUID
    invoice_number: str
    issue_date: datetime
    service_date: datetime
    due_date: datetime
    notes: Optional[str]
    status: InvoiceStatus
    company_name: Optional[str] = None
    partner_name: Optional[str] = None
    total: Optional[float] = None

    class Config:
        from_attributes = True


class StatusUpdate(BaseModel):
    status: InvoiceStatus

