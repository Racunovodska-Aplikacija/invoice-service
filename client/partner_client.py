import os
import grpc
from typing import Optional
from . import partner_pb2, partner_pb2_grpc


class PartnerClient:
    def __init__(self):
        self.host = os.getenv("PARTNER_SERVICE_HOST", "partner-service")
        self.port = os.getenv("PARTNER_SERVICE_GRPC_PORT", "50051")
        self.channel = grpc.insecure_channel(f"{self.host}:{self.port}")
        self.stub = partner_pb2_grpc.PartnerServiceStub(self.channel)

    def get_partner(self, partner_id: str) -> Optional[dict]:
        """Get partner by ID via gRPC"""
        try:
            request = partner_pb2.GetPartnerRequest(id=partner_id)
            response = self.stub.GetPartner(request, timeout=5)
            
            return {
                "id": response.id,
                "userId": response.userId,
                "naziv": response.naziv,
                "ulica": response.ulica,
                "kraj": response.kraj,
                "postnaSt": response.postnaSt,
                "poljubenNaslov": response.poljubenNaslov,
                "ddvZavezanec": response.ddvZavezanec,
                "davcnaSt": response.davcnaSt,
                "rokPlacila": response.rokPlacila,
                "telefon": response.telefon,
                "ePosta": response.ePosta,
                "spletnastran": response.spletnastran,
                "opombe": response.opombe,
                "eRacunNaslov": response.eRacunNaslov,
                "eRacunId": response.eRacunId,
            }
        except grpc.RpcError as e:
            print(f"gRPC error getting partner {partner_id}: {e}")
            return None
        except Exception as e:
            print(f"Error getting partner {partner_id}: {e}")
            return None

    def close(self):
        """Close the gRPC channel"""
        if self.channel:
            self.channel.close()
