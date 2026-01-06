import os
import grpc
from typing import List, Optional
from . import product_pb2, product_pb2_grpc


class ProductClient:
    def __init__(self):
        self.host = os.getenv("COMPANY_SERVICE_HOST", "company-service")
        self.port = os.getenv("COMPANY_SERVICE_GRPC_PORT", "50051")
        self.channel = grpc.insecure_channel(f"{self.host}:{self.port}")
        self.stub = product_pb2_grpc.ProductServiceStub(self.channel)

    def get_products(self, product_ids: List[str]) -> List[dict]:
        """Get multiple products by IDs via gRPC"""
        try:
            request = product_pb2.GetProductsRequest(ids=product_ids)
            response = self.stub.GetProducts(request, timeout=5)
            
            products = []
            for product in response.products:
                products.append({
                    "id": product.id,
                    "companyId": product.companyId,
                    "name": product.name,
                    "cost": product.cost,
                    "measuringUnit": product.measuringUnit,
                    "ddvPercentage": product.ddvPercentage,
                })
            return products
        except grpc.RpcError as e:
            print(f"gRPC error getting products: {e}")
            return []
        except Exception as e:
            print(f"Error getting products: {e}")
            return []

    def close(self):
        """Close the gRPC channel"""
        if self.channel:
            self.channel.close()

        try:
            raw_price = data["cost"]
            raw_ddv = data.get("ddvPercentage", "22")
            measuring_unit = data.get("measuringUnit", "")
            return Product(
                id=UUID(str(data["id"])),
                name=str(data["name"]),
                price=Decimal(str(raw_price)),
                measuring_unit=str(measuring_unit),
                ddv_percentage=Decimal(str(raw_ddv)),
            )
        except Exception as e:
            raise ProductClientError("unexpected product shape from product-service") from e


