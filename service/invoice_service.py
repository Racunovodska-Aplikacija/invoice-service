from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from models.database import Invoice, InvoiceLine, InvoiceStatus
from models.schemas import InvoiceCreate, InvoiceLineResponse, InvoiceResponse, InvoiceListResponse, InvoiceUpdate
from repository.invoice_repo import InvoiceRepository
from client.company_client import CompanyClient
from client.partner_client import PartnerClient
from client.product_client import ProductClient


class InvoiceService:
    def __init__(self, db: Session):
        self.repo = InvoiceRepository(db)
        # Initialize gRPC clients (they read host/port from environment variables)
        self.company_client = CompanyClient()
        self.partner_client = PartnerClient()
        self.product_client = ProductClient()

    def create_invoice(self, data: InvoiceCreate, user_id: str) -> Invoice:
        # Fetch company and partner data for snapshots
        company_data = None
        partner_name = None
        try:
            company_data = self.company_client.get_company(str(data.company_id))
        except Exception as e:
            print(f"Error fetching company for snapshot: {e}")
        
        try:
            partner_data = self.partner_client.get_partner(str(data.partner_id))
            if partner_data:
                partner_name = partner_data.get('naziv')
        except Exception as e:
            print(f"Error fetching partner for snapshot: {e}")

        # Calculate total from product data
        total = 0
        product_ids = [str(line.product_id) for line in data.lines]
        if product_ids:
            try:
                products_list = self.product_client.get_products(product_ids)
                products_map = {p['id']: p for p in products_list}
                for line in data.lines:
                    product = products_map.get(str(line.product_id))
                    if product:
                        line_total = line.amount * float(product.get('cost', 0))
                        vat_rate = float(product.get('ddvPercentage', 22))
                        total += line_total * (1 + vat_rate / 100)
            except Exception as e:
                print(f"Error calculating total: {e}")

        # Create invoice lines with only id, invoice_id, product_id, and amount
        lines = []
        for line_data in data.lines:
            lines.append(InvoiceLine(
                product_id=line_data.product_id,
                amount=line_data.amount,
            ))

        invoice = Invoice(
            invoice_number=data.invoice_number,
            user_id=user_id,
            company_id=data.company_id,
            partner_id=data.partner_id,
            issue_date=data.issue_date,
            service_date=data.service_date,
            due_date=data.due_date,
            notes=data.notes,
            status=InvoiceStatus.ISSUED,
            company_name=company_data.get('companyName') if company_data else None,
            partner_name=partner_name,
            total=total if total > 0 else None,
            lines=lines
        )

        created = self.repo.create(invoice)
        return created

    def get_invoice(self, invoice_id: UUID, user_id: str = None) -> Optional[Invoice]:
        return self.repo.get_by_id(invoice_id, user_id)

    def list_invoices(self, user_id: str = None) -> List[Invoice]:
        return self.repo.get_all(user_id)

    def update_invoice(self, invoice_id: UUID, data: InvoiceUpdate, user_id: str) -> Optional[InvoiceResponse]:
        invoice = self.repo.get_by_id(invoice_id, user_id)
        if not invoice:
            return None

        # Update invoice fields
        if data.company_id is not None:
            invoice.company_id = data.company_id
        if data.partner_id is not None:
            invoice.partner_id = data.partner_id
        if data.issue_date is not None:
            invoice.issue_date = data.issue_date
        if data.service_date is not None:
            invoice.service_date = data.service_date
        if data.due_date is not None:
            invoice.due_date = data.due_date
        if data.notes is not None:
            invoice.notes = data.notes
        if data.status is not None:
            invoice.status = data.status

        # Update lines if provided
        if data.lines is not None:
            # Remove existing lines
            invoice.lines = []
            # Add new lines
            for line_data in data.lines:
                invoice.lines.append(InvoiceLine(
                    product_id=line_data.product_id,
                    amount=line_data.amount,
                ))

        updated = self.repo.update(invoice)
        return self._to_invoice_response(updated)

    def delete_invoice(self, invoice_id: UUID, user_id: str) -> bool:
        return self.repo.delete(invoice_id, user_id)

    def create_invoice_response(self, data: InvoiceCreate, user_id: str) -> InvoiceResponse:
        invoice = self.create_invoice(data, user_id)
        return self._to_invoice_response(invoice)

    def get_invoice_response(self, invoice_id: UUID, user_id: str = None) -> Optional[InvoiceResponse]:
        invoice = self.get_invoice(invoice_id, user_id)
        if not invoice:
            return None
        return self._to_invoice_response_with_grpc(invoice)

    def list_invoices_by_user(self, user_id: str) -> List[InvoiceListResponse]:
        invoices = self.list_invoices(user_id)
        return [
            InvoiceListResponse(
                id=inv.id,
                user_id=inv.user_id,
                company_id=inv.company_id,
                partner_id=inv.partner_id,
                invoice_number=inv.invoice_number,
                issue_date=inv.issue_date,
                service_date=inv.service_date,
                due_date=inv.due_date,
                notes=inv.notes,
                status=inv.status,
                company_name=inv.company_name,
                partner_name=inv.partner_name,
                total=float(inv.total) if inv.total else None,
            )
            for inv in invoices
        ]

    def _to_invoice_response(self, invoice: Invoice) -> InvoiceResponse:
        # Build line responses with only the required fields
        line_responses: list[InvoiceLineResponse] = []
        for line in invoice.lines:
            line_responses.append(
                InvoiceLineResponse(
                    id=line.id,
                    invoice_id=line.invoice_id,
                    product_id=line.product_id,
                    amount=line.amount,
                )
            )

        return InvoiceResponse(
            id=invoice.id,
            invoice_number=invoice.invoice_number,
            user_id=invoice.user_id,
            company_id=invoice.company_id,
            partner_id=invoice.partner_id,
            issue_date=invoice.issue_date,
            service_date=invoice.service_date,
            due_date=invoice.due_date,
            notes=invoice.notes,
            status=invoice.status,
            lines=line_responses,
        )

    def _to_invoice_response_with_grpc(self, invoice: Invoice) -> InvoiceResponse:
        # Fetch company data via gRPC
        company_data = None
        try:
            company_data = self.company_client.get_company(str(invoice.company_id))
        except Exception as e:
            print(f"Error fetching company data: {e}")

        # Fetch partner data via gRPC
        partner_data = None
        try:
            partner_data = self.partner_client.get_partner(str(invoice.partner_id))
        except Exception as e:
            print(f"Error fetching partner data: {e}")

        # Collect all product IDs from invoice lines
        product_ids = [str(line.product_id) for line in invoice.lines]
        
        # Fetch products data via gRPC
        products_data = {}
        if product_ids:
            try:
                print(f"Fetching products for IDs: {product_ids}")
                products_list = self.product_client.get_products(product_ids)
                print(f"Received {len(products_list)} products: {products_list}")
                # Create a map of product_id -> product_data for easy lookup
                # Normalize both keys to strings for comparison
                products_data = {str(p['id']): p for p in products_list}
                print(f"Products map keys: {list(products_data.keys())}")
            except Exception as e:
                print(f"Error fetching products data: {e}")

        # Build line responses with product data
        line_responses: list[InvoiceLineResponse] = []
        for line in invoice.lines:
            product_id_str = str(line.product_id)
            product_data = products_data.get(product_id_str)
            print(f"Looking for product {product_id_str}, found: {product_data is not None}")
            line_responses.append(
                InvoiceLineResponse(
                    id=line.id,
                    invoice_id=line.invoice_id,
                    product_id=line.product_id,
                    amount=line.amount,
                    product=product_data,
                )
            )

        return InvoiceResponse(
            id=invoice.id,
            invoice_number=invoice.invoice_number,
            user_id=invoice.user_id,
            company_id=invoice.company_id,
            partner_id=invoice.partner_id,
            issue_date=invoice.issue_date,
            service_date=invoice.service_date,
            due_date=invoice.due_date,
            notes=invoice.notes,
            status=invoice.status,
            lines=line_responses,
            company=company_data,
            partner=partner_data,
        )

