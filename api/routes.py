from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
import base64
import json
from config import get_db
from models.schemas import InvoiceCreate, InvoiceResponse, InvoiceListResponse, InvoiceUpdate
from service.invoice_service import InvoiceService

router = APIRouter(prefix="/invoices", tags=["invoices"])


def get_service(db: Session = Depends(get_db)) -> InvoiceService:
    return InvoiceService(db)


def extract_user_id_from_token(request: Request) -> str:
    """Extract userId from JWT token"""
    token = None
    
    # Try Authorization header first
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:]
    # Try cookies
    elif "jwt" in request.cookies:
        token = request.cookies["jwt"]
    
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        # Decode JWT payload (middle part)
        parts = token.split(".")
        if len(parts) != 3:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        payload = base64.urlsafe_b64decode(parts[1] + "===")
        decoded = json.loads(payload)
        user_id = decoded.get("userId")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="UserId not found in token")
        
        return user_id
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.get("", response_model=List[InvoiceListResponse])
def get_invoices(request: Request, service: InvoiceService = Depends(get_service)):
    """Get all invoices for the authenticated user"""
    user_id = extract_user_id_from_token(request)
    return service.list_invoices_by_user(user_id)


@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(invoice_id: UUID, request: Request, service: InvoiceService = Depends(get_service)):
    """Get a specific invoice by ID"""
    user_id = extract_user_id_from_token(request)
    invoice = service.get_invoice_response(invoice_id, user_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


@router.post("", response_model=InvoiceResponse, status_code=201)
def add_invoice(data: InvoiceCreate, request: Request, service: InvoiceService = Depends(get_service)):
    """Create a new invoice"""
    user_id = extract_user_id_from_token(request)
    return service.create_invoice_response(data, user_id)


@router.put("/{invoice_id}", response_model=InvoiceResponse)
def update_invoice(
    invoice_id: UUID,
    data: InvoiceUpdate,
    request: Request,
    service: InvoiceService = Depends(get_service)
):
    """Update an existing invoice"""
    user_id = extract_user_id_from_token(request)
    invoice = service.update_invoice(invoice_id, data, user_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


@router.delete("/{invoice_id}", status_code=204)
def delete_invoice(invoice_id: UUID, request: Request, service: InvoiceService = Depends(get_service)):
    """Delete an invoice"""
    user_id = extract_user_id_from_token(request)
    success = service.delete_invoice(invoice_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Invoice not found")

