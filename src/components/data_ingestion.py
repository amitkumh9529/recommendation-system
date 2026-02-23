# src/components/data_ingestion.py
import os, sys, zipfile, requests
from src.logger import logger
from src.exception import RecommendationException
from src.entity.config_entity import DataIngestionConfig
from src.entity.artifact_entity import DataIngestionArtifact

class DataIngestion:
    def __init__(self, config: DataIngestionConfig):
        self.config = config

    def download_data(self) -> str:
        try:
            os.makedirs(self.config.raw_data_dir, exist_ok=True)
            zip_path = os.path.join(self.config.raw_data_dir, "data.zip")
            logger.info(f"Downloading dataset from {self.config.dataset_url}")
            response = requests.get(self.config.dataset_url, stream=True)
            with open(zip_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            logger.info("Download complete.")
            return zip_path
        except Exception as e:
            raise RecommendationException(e, sys)

    def extract_data(self, zip_path: str) -> str:
        try:
            logger.info("Extracting dataset...")
            with zipfile.ZipFile(zip_path, "r") as z:
                z.extractall(self.config.ingested_data_dir)
            logger.info(f"Extracted to {self.config.ingested_data_dir}")
            return self.config.ingested_data_dir
        except Exception as e:
            raise RecommendationException(e, sys)

    def initiate_data_ingestion(self) -> DataIngestionArtifact:
        try:
            logger.info(">>> Starting Data Ingestion <<<")
            zip_path = self.download_data()
            data_dir = self.extract_data(zip_path)
            artifact = DataIngestionArtifact(
                raw_file_path=data_dir, status=True, message="Data ingestion successful"
            )
            logger.info(f"Data Ingestion Artifact: {artifact}")
            return artifact
        except Exception as e:
            raise RecommendationException(e, sys)
        

        