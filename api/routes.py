from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from config import get_db
from models.schemas import InvoiceCreate, InvoiceResponse, InvoiceListResponse, StatusUpdate
from service.invoice_service import InvoiceService
from client.product_client import ProductClientError, ProductClientNotFound

router = APIRouter(prefix="/invoices", tags=["invoices"])


def get_service(db: Session = Depends(get_db)) -> InvoiceService:
    return InvoiceService(db)


@router.post("", response_model=InvoiceResponse, status_code=201)
def create_invoice(data: InvoiceCreate, service: InvoiceService = Depends(get_service)):
    try:
        return service.create_invoice_response(data)
    except ProductClientNotFound:
        raise HTTPException(status_code=400, detail="Unknown product_id in invoice lines")
    except ProductClientError:
        raise HTTPException(status_code=502, detail="Failed to fetch product data")


@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(invoice_id: UUID, service: InvoiceService = Depends(get_service)):
    try:
        invoice = service.get_invoice_response(invoice_id)
    except ProductClientNotFound:
        raise HTTPException(status_code=502, detail="Product missing while enriching invoice")
    except ProductClientError:
        raise HTTPException(status_code=502, detail="Failed to fetch product data")
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
    try:
        return service.get_invoice_response(invoice_id)
    except ProductClientNotFound:
        raise HTTPException(status_code=502, detail="Product missing while enriching invoice")
    except ProductClientError:
        raise HTTPException(status_code=502, detail="Failed to fetch product data")

