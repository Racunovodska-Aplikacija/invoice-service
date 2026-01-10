from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from config import initialize_database
from api.routes import router

app = FastAPI(
    title="Invoice Service",
    description="Microservice for invoice management",
    version="1.0.0",
    # Serve docs/OpenAPI under the same /invoices prefix that Kong routes to this service.
    # This avoids needing a separate Ingress rule for /docs and /openapi.json.
    docs_url="/invoices/docs",
    redoc_url="/invoices/redoc",
    openapi_url="/invoices/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    initialize_database()

# Include routers
app.include_router(router)

# Prometheus metrics (cluster-internal scraping; do NOT expose via Kong Ingress)
Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)


@app.get("/health")
def health_check():
    return {"status": "healthy"}

