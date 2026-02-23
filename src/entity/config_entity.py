# src/entity/config_entity.py
from dataclasses import dataclass
from src.constants import *
import os

@dataclass
class DataIngestionConfig:
    raw_data_dir: str = os.path.join(ARTIFACT_DIR, "data_ingestion", "raw")
    ingested_data_dir: str = os.path.join(ARTIFACT_DIR, "data_ingestion", "ingested")
    dataset_url: str = DATASET_URL

@dataclass
class DataValidationConfig:
    report_file_path: str = os.path.join(ARTIFACT_DIR, "data_validation", "report.yaml")
    required_columns: list = None
    def __post_init__(self):
        self.required_columns = ["user_id", "item_id", "rating"]

@dataclass
class DataTransformationConfig:
    transformed_train_path: str = os.path.join(ARTIFACT_DIR, "data_transformation", "train.csv")
    transformed_test_path: str = os.path.join(ARTIFACT_DIR, "data_transformation", "test.csv")
    encoder_path: str = os.path.join(ARTIFACT_DIR, "data_transformation", ENCODER_FILE)

@dataclass
class ModelTrainerConfig:
    model_path: str = os.path.join(ARTIFACT_DIR, "model_trainer", MODEL_FILE)
    embed_dim: int = EMBED_DIM
    hidden_layers: list = None
    dropout: float = DROPOUT_RATE
    lr: float = LEARNING_RATE
    batch_size: int = BATCH_SIZE
    epochs: int = EPOCHS
    def __post_init__(self):
        self.hidden_layers = HIDDEN_LAYERS

@dataclass
class ModelEvaluationConfig:
    evaluation_report_path: str = os.path.join(ARTIFACT_DIR, "model_evaluation", "report.yaml")
    top_k: int = TOP_K
    ndcg_threshold: float = MIN_NDCG_THRESHOLD

@dataclass
class ModelPusherConfig:
    production_model_dir: str = MODEL_DIR
    faiss_index_path: str = os.path.join(MODEL_DIR, FAISS_INDEX_FILE)
    final_model_path: str = os.path.join(MODEL_DIR, MODEL_FILE)
    final_encoder_path: str = os.path.join(MODEL_DIR, ENCODER_FILE)