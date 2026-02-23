# src/entity/artifact_entity.py
from dataclasses import dataclass

@dataclass
class DataIngestionArtifact:
    raw_file_path: str
    status: bool
    message: str

@dataclass
class DataValidationArtifact:
    validation_status: bool
    report_file_path: str
    message: str

@dataclass
class DataTransformationArtifact:
    transformed_train_path: str
    transformed_test_path: str
    encoder_path: str
    n_users: int
    n_items: int

@dataclass
class ModelTrainerArtifact:
    model_path: str
    train_loss: float
    val_loss: float

@dataclass
class ModelEvaluationArtifact:
    is_model_accepted: bool
    ndcg_score: float
    hit_rate: float
    report_path: str

@dataclass
class ModelPusherArtifact:
    model_pushed: bool
    production_model_path: str
    faiss_index_path: str