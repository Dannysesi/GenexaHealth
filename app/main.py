from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel, OAuthFlowPassword
from fastapi.security import OAuth2
from app.routes import patients, genomics, dosing, auth


# --- FastAPI app ---
app = FastAPI(
    title="GenexaHealth Warfarin API",
    description="API for pharmacogenomic-guided warfarin dosing data",
    version="1.0.0"
)

# --- CORS middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Include routers ---
app.include_router(auth.router, tags=["Authentication"])  # Auth router
app.include_router(patients.router, prefix="/api/v1", tags=["Patients"])
app.include_router(genomics.router, prefix="/api/v1", tags=["Genomics"])
app.include_router(dosing.router, prefix="/api/v1", tags=["Dosing"])

# --- Root & health endpoints ---
@app.get("/")
async def root():
    return {"message": "GenexaHealth Warfarin Dosing API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
