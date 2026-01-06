import os
import grpc
from typing import Optional
from . import company_pb2, company_pb2_grpc


class CompanyClient:
    def __init__(self):
        self.host = os.getenv("COMPANY_SERVICE_HOST", "company-service")
        self.port = os.getenv("COMPANY_SERVICE_GRPC_PORT", "50051")
        self.channel = grpc.insecure_channel(f"{self.host}:{self.port}")
        self.stub = company_pb2_grpc.CompanyServiceStub(self.channel)

    def get_company(self, company_id: str) -> Optional[dict]:
        """Get company by ID via gRPC"""
        try:
            request = company_pb2.GetCompanyRequest(id=company_id)
            response = self.stub.GetCompany(request, timeout=5)
            
            return {
                "id": response.id,
                "userId": response.userId,
                "companyName": response.companyName,
                "street": response.street,
                "streetAdditional": response.streetAdditional,
                "postalCode": response.postalCode,
                "city": response.city,
                "iban": response.iban,
                "bic": response.bic,
                "registrationNumber": response.registrationNumber,
                "vatPayer": response.vatPayer,
                "vatId": response.vatId,
                "additionalInfo": response.additionalInfo,
                "documentLocation": response.documentLocation,
                "reverseCharge": response.reverseCharge,
            }
        except grpc.RpcError as e:
            print(f"gRPC error getting company {company_id}: {e}")
            return None
        except Exception as e:
            print(f"Error getting company {company_id}: {e}")
            return None

    def close(self):
        """Close the gRPC channel"""
        if self.channel:
            self.channel.close()
