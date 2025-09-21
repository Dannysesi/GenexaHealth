from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from app.database import db
from app.models import PatientResponse, PatientSearch
from app.auth import get_current_active_user, require_role
from app.security import get_current_user_from_bearer

router = APIRouter()

@router.get("/patients", response_model=List[PatientResponse])
async def get_all_patients(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user = Depends(get_current_user_from_bearer)  # Add authentication
):
    """Get paginated list of all patients"""
    patients = db.get_all_patients(limit, offset)
    return patients

@router.get("/patients/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: str,
    current_user = Depends(get_current_user_from_bearer)  # Add authentication
):
    """Get complete patient record by ID"""
    patient = db.get_patient_by_id(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@router.post("/patients/search", response_model=List[PatientResponse])
async def search_patients(
    search: PatientSearch,
    current_user = Depends(get_current_user_from_bearer)  # Add authentication
):
    """Search patients with filters"""
    patients = db.search_patients(
        age_min=search.age_min,
        age_max=search.age_max,
        genotype=search.genotype,
        adverse_event=search.adverse_event
    )
    return patients