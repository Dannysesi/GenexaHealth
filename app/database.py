import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import json

class WarfarinDatabase:
    def __init__(self):
        self.genomics_df = None
        self.clinical_df = None
        self.lifestyle_df = None
        self.outcomes_df = None
        self.merged_df = None
        self.load_data()
    
    def load_data(self):
        """Load data from CSV files"""
        try:
            self.genomics_df = pd.read_csv('app/data/genomics.csv')
            self.clinical_df = pd.read_csv('app/data/clinical.csv')
            self.lifestyle_df = pd.read_csv('app/data/lifestyle.csv')
            
            # Read outcomes and rename the problematic column
            self.outcomes_df = pd.read_csv('app/data/outcomes.csv')
            self.outcomes_df = self.outcomes_df.rename(
                columns={'Time_in_Therapeutic_Range_%': 'Time_in_Therapeutic_Range_Pct'}
            )
            
            # Create merged view for complex queries
            self.merged_df = self.merge_all_data()
            print("✅ Data loaded successfully")
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            raise e
    
    def merge_all_data(self) -> pd.DataFrame:
        """Merge all data sources into a single DataFrame"""
        df = self.clinical_df.merge(self.genomics_df, on='Patient_ID')
        df = df.merge(self.lifestyle_df, on='Patient_ID')
        df = df.merge(self.outcomes_df, on='Patient_ID')
        return df
    
    def get_patient_by_id(self, patient_id: str) -> Optional[Dict]:
        """Get complete patient record by ID, structured for Pydantic model"""
        patient_data = self.merged_df[self.merged_df['Patient_ID'] == patient_id]
        if patient_data.empty:
            return None
        
        return self._structure_patient_data(patient_data.iloc[0])
    
    def get_all_patients(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Get paginated list of all patients, structured for Pydantic model"""
        patients_data = self.merged_df.iloc[offset:offset+limit]
        return [self._structure_patient_data(row) for _, row in patients_data.iterrows()]
    
    def search_patients(self, 
                       age_min: Optional[int] = None,
                       age_max: Optional[int] = None,
                       genotype: Optional[str] = None,
                       adverse_event: Optional[str] = None) -> List[Dict]:
        """Search patients with filters, structured for Pydantic model"""
        df = self.merged_df.copy()
        
        if age_min is not None:
            df = df[df['Age'] >= age_min]
        if age_max is not None:
            df = df[df['Age'] <= age_max]
        if genotype:
            df = df[df['CYP2C9'] == genotype]
        if adverse_event:
            df = df[df['Adverse_Event'] == adverse_event]
        
        return [self._structure_patient_data(row) for _, row in df.iterrows()]
    
    def _structure_patient_data(self, row) -> Dict:
        """Structure flat row data into nested format for Pydantic model"""
        # Handle NaN values and ensure proper data types
        def clean_value(value, default=None):
            if pd.isna(value):
                return default
            if isinstance(value, (int, float)) and np.isnan(value):
                return default
            return value
        
        # Extract comorbidities with proper boolean conversion
        comorbidities = {
            'Hypertension': bool(clean_value(row.get('Hypertension', 0))),
            'Diabetes': bool(clean_value(row.get('Diabetes', 0))),
            'Chronic_Kidney_Disease': bool(clean_value(row.get('Chronic_Kidney_Disease', 0))),
            'Heart_Failure': bool(clean_value(row.get('Heart_Failure', 0)))
        }
        
        # Extract medications with proper boolean conversion
        medications = {
            'Amiodarone': bool(clean_value(row.get('Amiodarone', 0))),
            'Antibiotics': bool(clean_value(row.get('Antibiotics', 0))),
            'Aspirin': bool(clean_value(row.get('Aspirin', 0))),
            'Statins': bool(clean_value(row.get('Statins', 0)))
        }
        
        # Structure the patient data according to Pydantic model
        structured_data = {
            'Patient_ID': clean_value(row['Patient_ID'], ''),
            'Age': clean_value(row['Age'], 0),
            'Sex': clean_value(row['Sex'], ''),
            'Weight_kg': clean_value(row['Weight_kg'], 0.0),
            'Ethnicity': clean_value(row['Ethnicity'], ''),
            'Genomics': {
                'CYP2C9': clean_value(row['CYP2C9'], ''),
                'VKORC1': clean_value(row['VKORC1'], ''),
                'CYP4F2': clean_value(row['CYP4F2'], '')
            },
            'Lifestyle': {
                'Alcohol_Intake': clean_value(row['Alcohol_Intake'], ''),
                'Smoking_Status': clean_value(row['Smoking_Status'], ''),
                'Diet_VitK_Intake': clean_value(row['Diet_VitK_Intake'], '')
            },
            'Dosing': {
                'Final_Stable_Dose_mg': clean_value(row['Final_Stable_Dose_mg'], 0.0),
                'INR_Stabilization_Days': clean_value(row['INR_Stabilization_Days'], 0),
                'Adverse_Event': clean_value(row['Adverse_Event'], 'None'),
                'Time_in_Therapeutic_Range_Pct': clean_value(row['Time_in_Therapeutic_Range_Pct'], 0.0)
            },
            'Comorbidities': comorbidities,
            'Medications': medications
        }
        
        # Handle Height_cm if it exists (optional field)
        if 'Height_cm' in row:
            structured_data['Height_cm'] = clean_value(row['Height_cm'])
        
        return structured_data

# Global database instance
db = WarfarinDatabase()