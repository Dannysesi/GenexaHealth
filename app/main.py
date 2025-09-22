from fastapi import FastAPI
from app.routes import genomics, clinical, lifestyle, outcomes
from app import auth

app = FastAPI(
    title="Warfarin Data Source API",
    version="1.0.0",
    description="Protected API serving siloed data tables (genomics, clinical, lifestyle, outcomes).",
)

# Authentication router
app.include_router(auth.router, prefix="/api/v1")

# Data routers (protected)
app.include_router(genomics.router, prefix="/api/v1/genomics", tags=["Genomics"])
app.include_router(clinical.router, prefix="/api/v1/clinical", tags=["Clinical"])
app.include_router(lifestyle.router, prefix="/api/v1/lifestyle", tags=["Lifestyle"])
app.include_router(outcomes.router, prefix="/api/v1/outcomes", tags=["Outcomes"])

@app.get("/api/v1/patient_ids", tags=["Patients"])
async def get_patient_ids():
    from app.database import db
    return {"patient_ids": db.get_patient_ids()}


# --- Root & health endpoints ---
@app.get("/")
async def root():
    return {"message": "GenexaHealth Warfarin Dosing API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
