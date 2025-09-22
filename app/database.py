import pandas as pd
from typing import Optional, Dict, Any, List

class WarfarinDatabase:
    def __init__(self, data_path: str = "data"):
        self.data_path = data_path
        self.genomics_df: Optional[pd.DataFrame] = None
        self.clinical_df: Optional[pd.DataFrame] = None
        self.lifestyle_df: Optional[pd.DataFrame] = None
        self.outcomes_df: Optional[pd.DataFrame] = None
        self._loaded = False

    def load_data(self):
        """Load all CSVs once at startup."""
        if self._loaded:
            return
        self.genomics_df = pd.read_csv(f"app/{self.data_path}/genomics.csv")
        self.clinical_df = pd.read_csv(f"app/{self.data_path}/clinical.csv")
        self.lifestyle_df = pd.read_csv(f"app/{self.data_path}/lifestyle.csv")
        self.outcomes_df = pd.read_csv(f"app/{self.data_path}/outcomes.csv")

        # normalize any weird column names
        if "Time_in_Therapeutic_Range_%" in self.outcomes_df.columns:
            self.outcomes_df = self.outcomes_df.rename(
                columns={"Time_in_Therapeutic_Range_%": "Time_in_Therapeutic_Range_Pct"}
            )
        self._loaded = True

    def _sanitize_df(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Convert DF to JSON-serializable list of dicts."""
        return (
            df.where(pd.notnull(df), None)
            .astype(object)
            .to_dict(orient="records")
        )

    # --- Public Accessors ---
    def get_table(self, table: str, limit: int = 100, offset: int = 0) -> List[Dict]:
        self.load_data()
        df_map = {
            "genomics": self.genomics_df,
            "clinical": self.clinical_df,
            "lifestyle": self.lifestyle_df,
            "outcomes": self.outcomes_df,
        }
        if table not in df_map:
            raise ValueError("Invalid table requested")
        df = df_map[table].iloc[offset : offset + limit]
        return self._sanitize_df(df)

    def get_record_by_id(self, table: str, patient_id: str) -> Optional[Dict]:
        self.load_data()
        df_map = {
            "genomics": self.genomics_df,
            "clinical": self.clinical_df,
            "lifestyle": self.lifestyle_df,
            "outcomes": self.outcomes_df,
        }
        df = df_map[table]
        recs = df[df["Patient_ID"] == patient_id]
        if recs.empty:
            return None
        return self._sanitize_df(recs)[0]

    def get_patient_ids(self) -> List[str]:
        self.load_data()
        return self.clinical_df["Patient_ID"].astype(str).tolist()


# Global DB instance
db = WarfarinDatabase()
