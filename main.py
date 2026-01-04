from fastapi import FastAPI
from api.routes import router

app = FastAPI(
    title="Invoice Service",
    description="Microservice for invoice management",
    version="1.0.0"
)

# Include routers
app.include_router(router)


@app.get("/health")
def health_check():
    return {"status": "healthy"}

