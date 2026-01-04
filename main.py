from fastapi import FastAPI
from config import engine
from models.database import Base
from api.routes import router

app = FastAPI(
    title="Invoice Service",
    description="Microservice for invoice management",
    version="1.0.0"
)

# Create tables on startup
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(router)


@app.get("/health")
def health_check():
    return {"status": "healthy"}

