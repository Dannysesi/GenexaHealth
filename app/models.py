from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Union
from enum import Enum

class AdverseEvent(str, Enum):
    NONE = "None"
    BLEEDING = "Bleeding"
    CLOTTING = "Clotting"

class PatientBase(BaseModel):
    Patient_ID: str = Field(..., description="Unique patient identifier")
    Age: int = Field(..., ge=18, le=100, description="Patient age")
    Sex: str = Field(..., description="Patient gender")
    Weight_kg: float = Field(..., ge=30, le=200, description="Weight in kg")
    Ethnicity: str = Field(..., description="Ethnic background")
    Height_cm: Optional[int] = Field(None, description="Height in cm")  # Make optional

class GenomicsData(BaseModel):
    CYP2C9: str = Field(..., description="CYP2C9 genotype")
    VKORC1: str = Field(..., description="VKORC1 genotype")
    CYP4F2: str = Field(..., description="CYP4F2 genotype")

class LifestyleData(BaseModel):
    Alcohol_Intake: Optional[str] = Field(None, description="Alcohol consumption level")
    Smoking_Status: str = Field(..., description="Smoking status")
    Diet_VitK_Intake: str = Field(..., description="Vitamin K intake level")

class DosingOutcome(BaseModel):
    Final_Stable_Dose_mg: float = Field(..., description="Final stable warfarin dose")
    INR_Stabilization_Days: int = Field(..., description="Days to INR stabilization")
    Adverse_Event: Optional[str] = Field(None, description="Type of adverse event")  # Make optional
    Time_in_Therapeutic_Range_Pct: float = Field(..., description="Percentage time in therapeutic range")

class PatientResponse(PatientBase):
    Genomics: GenomicsData
    Lifestyle: LifestyleData
    Dosing: DosingOutcome
    Comorbidities: Dict[str, bool]
    Medications: Dict[str, bool]

class DosingRecommendation(BaseModel):
    patient_id: str
    recommended_dose: float
    confidence_score: float
    factors: Dict[str, float]
    warnings: List[str]

class PatientSearch(BaseModel):
    age_min: Optional[int] = None
    age_max: Optional[int] = None
    genotype: Optional[str] = None
    adverse_event: Optional[str] = None