from fastapi import APIRouter, HTTPException, Depends
from app.database import db
from app.models import DosingRecommendation
from app.auth import get_current_active_user
import numpy as np
from app.security import get_current_user_from_bearer

router = APIRouter()

@router.get("/dosing/recommendation/{patient_id}", response_model=DosingRecommendation)
async def get_dosing_recommendation(
    patient_id: str,
    current_user = Depends(get_current_user_from_bearer)  # Add authentication
):
    """Get warfarin dosing recommendation for a patient"""
    patient = db.get_patient_by_id(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Simple dosing algorithm
    recommendation = calculate_dose_recommendation(patient)
    return recommendation

def calculate_dose_recommendation(patient: dict) -> DosingRecommendation:
    """Calculate warfarin dose recommendation based on patient data"""
    base_dose = 5.0
    
    # Genetic adjustments - access nested genomics data
    cyp2c9_factors = {"*1/*1": 1.0, "*1/*2": 0.8, "*1/*3": 0.6,
                     "*2/*2": 0.5, "*2/*3": 0.4, "*3/*3": 0.3}
    vkorc1_factors = {"G/G": 1.0, "A/G": 0.7, "A/A": 0.5}
    
    # Get genetic data from nested structure
    cyp2c9_genotype = patient['Genomics']['CYP2C9']
    vkorc1_genotype = patient['Genomics']['VKORC1']
    
    dose = base_dose
    dose *= cyp2c9_factors.get(cyp2c9_genotype, 1.0)
    dose *= vkorc1_factors.get(vkorc1_genotype, 1.0)
    
    # Clinical adjustments
    if patient['Age'] > 75:
        dose *= 0.8
    if patient['Weight_kg'] < 60:
        dose *= 0.9
    
    # Check for amiodarone use in medications
    on_amiodarone = patient['Medications'].get('Amiodarone', False)
    if on_amiodarone:
        dose *= 0.7
    
    factors = {
        "genetic_impact": 0.6,
        "age_impact": 0.2 if patient['Age'] > 75 else 0.0,
        "weight_impact": 0.1 if patient['Weight_kg'] < 60 else 0.0,
        "amiodarone_impact": 0.3 if on_amiodarone else 0.0
    }
    
    warnings = []
    if cyp2c9_genotype in ["*2/*3", "*3/*3"]:
        warnings.append("Poor metabolizer - monitor closely for bleeding")
    if patient['Age'] > 80:
        warnings.append("Elderly patient - increased bleeding risk")
    if on_amiodarone:
        warnings.append("Amiodarone use detected - significant dose reduction needed")
    
    # Calculate confidence score based on data completeness
    confidence_score = 0.85
    if patient['Genomics']['CYP2C9'] is None or patient['Genomics']['VKORC1'] is None:
        confidence_score = 0.6
        warnings.append("Incomplete genetic data - recommendation less reliable")
    
    return DosingRecommendation(
        patient_id=patient['Patient_ID'],
        recommended_dose=round(dose, 1),
        confidence_score=confidence_score,
        factors=factors,
        warnings=warnings
    )