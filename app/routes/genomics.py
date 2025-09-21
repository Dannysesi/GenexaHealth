from fastapi import APIRouter, Depends
from app.database import db
from app.auth import get_current_active_user
from app.security import get_current_user_from_bearer

router = APIRouter()

@router.get("/genomics/stats")
async def get_genomics_stats(
    current_user = Depends(get_current_user_from_bearer)  # Add authentication
):
    """Get statistics about genetic variants"""
    df = db.genomics_df
    stats = {
        "cyp2c9_distribution": df['CYP2C9'].value_counts().to_dict(),
        "vkorc1_distribution": df['VKORC1'].value_counts().to_dict(),
        "cyp4f2_distribution": df['CYP4F2'].value_counts().to_dict(),
        "total_patients": len(df)
    }
    return stats

@router.get("/genomics/patients/{genotype}")
async def get_patients_by_genotype(
    genotype: str,
    current_user = Depends(get_current_user_from_bearer)  # Add authentication
):
    """Get patients with specific genotype"""
    patients = db.merged_df[db.merged_df['CYP2C9'] == genotype]
    return patients.to_dict('records')