from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config import get_db
from models.schemas import InvoiceCreate, InvoiceResponse, InvoiceListResponse, StatusUpdate
from service.invoice_service import InvoiceService

router = APIRouter(prefix="/invoices", tags=["invoices"])


def get_service(db: Session = Depends(get_db)) -> InvoiceService:
    return InvoiceService(db)


@router.post("", response_model=InvoiceResponse, status_code=201)
def create_invoice(data: InvoiceCreate, service: InvoiceService = Depends(get_service)):
    return service.create_invoice_response(data)


@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(invoice_id: UUID, service: InvoiceService = Depends(get_service)):
    invoice = service.get_invoice_response(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


@router.get("", response_model=List[InvoiceListResponse])
def list_invoices(service: InvoiceService = Depends(get_service)):
    return service.list_invoice_responses()


@router.patch("/{invoice_id}/status", response_model=InvoiceResponse)
def update_invoice_status(
    invoice_id: UUID,
    status_update: StatusUpdate,
    service: InvoiceService = Depends(get_service)
):
    invoice = service.update_status(invoice_id, status_update)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return service.get_invoice_response(invoice_id)

