from fastapi import APIRouter, Depends, Query, HTTPException
from app.database import db
from app.auth import get_current_active_user, User

router = APIRouter()

@router.get("/", summary="List clinical records")
async def list_clinical(
    limit: int = Query(100, ge=1, le=1000), 
    offset: int = 0,
    current_user: User = Depends(get_current_active_user)
):
    return db.get_table("clinical", limit=limit, offset=offset)

@router.get("/{patient_id}", summary="Get clinical by patient id")
async def clinical_by_patient(
    patient_id: str,
    current_user: User = Depends(get_current_active_user)
):
    rec = db.get_record_by_id("clinical", patient_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Patient not found in clinical data")
    return rec
