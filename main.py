from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import initialize_database
from api.routes import router

app = FastAPI(
    title="Invoice Service",
    description="Microservice for invoice management",
    version="1.0.0"
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


@app.get("/health")
def health_check():
    return {"status": "healthy"}

