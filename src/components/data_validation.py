# src/components/data_validation.py
import os, sys
import pandas as pd
from src.logger import logger
from src.exception import RecommendationException
from src.entity.config_entity import DataValidationConfig
from src.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact
from src.utils.main_utils import save_yaml

class DataValidation:
    def __init__(self, config: DataValidationConfig, ingestion_artifact: DataIngestionArtifact):
        self.config = config
        self.ingestion_artifact = ingestion_artifact

    def validate_schema(self, df: pd.DataFrame) -> dict:
        report = {}
        missing = [c for c in self.config.required_columns if c not in df.columns]
        report["missing_columns"] = missing
        report["schema_valid"] = len(missing) == 0
        report["total_rows"] = len(df)
        report["null_counts"] = df.isnull().sum().to_dict()
        report["duplicate_rows"] = int(df.duplicated().sum())
        return report

    def initiate_data_validation(self) -> DataValidationArtifact:
        try:
            logger.info(">>> Starting Data Validation <<<")
            # Load data (adjust path for MovieLens structure)
            ratings_path = os.path.join(self.ingestion_artifact.raw_file_path, "ml-1m", "ratings.dat")
            df = pd.read_csv(ratings_path, sep="::", engine="python",
                             names=["user_id", "item_id", "rating", "timestamp"])
            report = self.validate_schema(df)
            save_yaml(self.config.report_file_path, report)

            status = report["schema_valid"] and report["total_rows"] > 1000
            artifact = DataValidationArtifact(
                validation_status=status,
                report_file_path=self.config.report_file_path,
                message="Validation passed" if status else "Validation failed"
            )
            logger.info(f"Data Validation Artifact: {artifact}")
            return artifact
        except Exception as e:
            raise RecommendationException(e, sys)