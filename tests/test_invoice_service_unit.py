from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, List
from uuid import UUID, uuid4
from unittest.mock import MagicMock

import pytest

from models.schemas import InvoiceStatus, InvoiceUpdate


@dataclass
class DummyInvoice:
    id: UUID
    user_id: UUID
    company_id: UUID
    partner_id: UUID
    invoice_number: str
    issue_date: datetime
    service_date: datetime
    due_date: datetime
    notes: str | None
    status: InvoiceStatus
    company_name: str | None = None
    partner_name: str | None = None
    total: Decimal | None = None
    lines: List[Any] = None


@pytest.fixture
def svc_and_repo(monkeypatch):
    # Import inside fixture so patches affect the module used by the service.
    import service.invoice_service as invoice_service_module

    mock_repo = MagicMock()
    mock_company_client = MagicMock()
    mock_partner_client = MagicMock()
    mock_product_client = MagicMock()

    monkeypatch.setattr(invoice_service_module, "InvoiceRepository", lambda db: mock_repo)
    monkeypatch.setattr(invoice_service_module, "CompanyClient", lambda: mock_company_client)
    monkeypatch.setattr(invoice_service_module, "PartnerClient", lambda: mock_partner_client)
    monkeypatch.setattr(invoice_service_module, "ProductClient", lambda: mock_product_client)

    svc = invoice_service_module.InvoiceService(db=MagicMock())
    return svc, mock_repo


def test_get_invoice_delegates_to_repo(svc_and_repo):
    svc, repo = svc_and_repo
    invoice_id = uuid4()
    user_id = "user-123"

    expected = object()
    repo.get_by_id.return_value = expected

    assert svc.get_invoice(invoice_id, user_id) is expected
    repo.get_by_id.assert_called_once_with(invoice_id, user_id)


def test_list_invoices_delegates_to_repo(svc_and_repo):
    svc, repo = svc_and_repo
    user_id = "user-123"

    expected = [object(), object()]
    repo.get_all.return_value = expected

    assert svc.list_invoices(user_id) is expected
    repo.get_all.assert_called_once_with(user_id)


def test_delete_invoice_delegates_to_repo(svc_and_repo):
    svc, repo = svc_and_repo
    invoice_id = uuid4()
    user_id = "user-123"

    repo.delete.return_value = True

    assert svc.delete_invoice(invoice_id, user_id) is True
    repo.delete.assert_called_once_with(invoice_id, user_id)


def test_update_invoice_returns_none_if_missing(svc_and_repo):
    svc, repo = svc_and_repo
    invoice_id = uuid4()
    user_id = "user-123"

    repo.get_by_id.return_value = None

    result = svc.update_invoice(invoice_id, InvoiceUpdate(notes="x"), user_id)
    assert result is None
    repo.update.assert_not_called()


def test_update_invoice_updates_fields_and_calls_repo_update(svc_and_repo):
    svc, repo = svc_and_repo
    invoice_id = uuid4()
    user_id = "user-123"
    now = datetime.now(tz=timezone.utc)

    invoice = DummyInvoice(
        id=invoice_id,
        user_id=uuid4(),
        company_id=uuid4(),
        partner_id=uuid4(),
        invoice_number="INV-000001",
        issue_date=now,
        service_date=now,
        due_date=now,
        notes="old",
        status=InvoiceStatus.ISSUED,
        lines=[],
    )

    repo.get_by_id.return_value = invoice
    repo.update.side_effect = lambda inv: inv  # return the same object back

    result = svc.update_invoice(
        invoice_id,
        InvoiceUpdate(notes="new notes", status=InvoiceStatus.PAID),
        user_id,
    )

    assert result is not None
    assert result.notes == "new notes"
    assert result.status == InvoiceStatus.PAID
    repo.update.assert_called_once()

