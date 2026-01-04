import os
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

import requests


class ProductClientError(Exception):
    pass


class ProductClientNotFound(ProductClientError):
    pass


@dataclass(frozen=True)
class Product:
    id: UUID
    name: str
    price: Decimal


class ProductClient:
    def __init__(self):
        self.base_url = os.getenv("PRODUCT_SERVICE_URL", "http://localhost:8002").rstrip("/")
        try:
            self.timeout_seconds = float(os.getenv("HTTP_TIMEOUT_SECONDS", "5"))
        except ValueError:
            self.timeout_seconds = 5.0

    def get_product(self, product_id: UUID) -> Product:
        url = f"{self.base_url}/products/{product_id}"
        try:
            resp = requests.get(url, timeout=self.timeout_seconds)
        except requests.RequestException as e:
            raise ProductClientError(str(e)) from e

        if resp.status_code == 404:
            raise ProductClientNotFound()
        if resp.status_code >= 400:
            raise ProductClientError(f"product-service error: {resp.status_code}")

        try:
            data = resp.json()
        except ValueError as e:
            raise ProductClientError("invalid JSON from product-service") from e

        try:
            raw_price = data["price"]
            return Product(
                id=UUID(str(data["id"])),
                name=str(data["name"]),
                price=Decimal(str(raw_price)),
            )
        except Exception as e:
            raise ProductClientError("unexpected product shape from product-service") from e


