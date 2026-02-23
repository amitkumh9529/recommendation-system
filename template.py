import os
import logging
from pathlib import Path

# ─────────────────────────────────────────────
#  Logging setup
# ─────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
#  All project files & folders
# ─────────────────────────────────────────────
project_files = [

    # ── Data directories ──────────────────────
    "data/raw/.gitkeep",
    "data/processed/.gitkeep",
    "data/artifacts/.gitkeep",

    # ── Source: logger ────────────────────────
    "src/__init__.py",
    "src/logger/__init__.py",

    # ── Source: exception ─────────────────────
    "src/exception/__init__.py",

    # ── Source: constants ─────────────────────
    "src/constants/__init__.py",

    # ── Source: entity ────────────────────────
    "src/entity/__init__.py",
    "src/entity/config_entity.py",
    "src/entity/artifact_entity.py",

    # ── Source: config ────────────────────────
    "src/config/__init__.py",
    "src/config/configuration.py",

    # ── Source: utils ─────────────────────────
    "src/utils/__init__.py",
    "src/utils/main_utils.py",
    "src/utils/tmdb_enrichment.py",

    # ── Source: components ────────────────────
    "src/components/__init__.py",
    "src/components/data_ingestion.py",
    "src/components/data_validation.py",
    "src/components/data_transformation.py",
    "src/components/model_trainer.py",
    "src/components/model_evaluation.py",
    "src/components/model_pusher.py",

    # ── Source: pipeline ──────────────────────
    "src/pipeline/__init__.py",
    "src/pipeline/training_pipeline.py",
    "src/pipeline/prediction_pipeline.py",

    # ── Models (saved artifacts) ──────────────
    "models/.gitkeep",

    # ── Notebooks ─────────────────────────────
    "notebooks/experiment.ipynb",

    # ── API: FastAPI backend ───────────────────
    "api/__init__.py",
    "api/main.py",
    "api/routes/__init__.py",
    "api/routes/recommend.py",
    "api/routes/feedback.py",
    "api/schemas/__init__.py",
    "api/schemas/models.py",

    # ── Frontend: React ───────────────────────
    "frontend/public/index.html",
    "frontend/src/App.jsx",
    "frontend/src/index.js",
    "frontend/src/components/MovieCard.jsx",
    "frontend/src/components/SearchBar.jsx",
    "frontend/src/components/RecommendationGrid.jsx",
    "frontend/src/components/Navbar.jsx",
    "frontend/src/pages/Home.jsx",
    "frontend/src/pages/MovieDetail.jsx",
    "frontend/src/services/api.js",
    "frontend/package.json",
    "frontend/.env",

    # ── Tests ─────────────────────────────────
    "tests/__init__.py",
    "tests/test_data_ingestion.py",
    "tests/test_data_transformation.py",
    "tests/test_model_trainer.py",
    "tests/test_prediction_pipeline.py",

    # ── MLflow ────────────────────────────────
    "mlflow/.gitkeep",

    # ── Logs ──────────────────────────────────
    "logs/.gitkeep",

    # ── Root files ────────────────────────────
    "app.py",
    "run_api.py",
    "setup.py",
    "requirements.txt",
    "Dockerfile",
    "docker-compose.yml",
    ".env",
    ".gitignore",
    "README.md",
]

# ─────────────────────────────────────────────
#  Starter content for key files
# ─────────────────────────────────────────────
file_content_map = {

    "app.py": '''\
from src.pipeline.training_pipeline import TrainingPipeline
from src.logger import logger

if __name__ == "__main__":
    try:
        pipeline = TrainingPipeline()
        pipeline.run_pipeline()
    except Exception as e:
        logger.exception(f"Training pipeline failed: {e}")
        raise e
''',

    "run_api.py": '''\
import uvicorn

if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
''',

    "setup.py": '''\
from setuptools import setup, find_packages

setup(
    name="recommendation-system",
    version="1.0.0",
    author="Your Name",
    description="End-to-End Deep Learning Movie Recommendation System",
    packages=find_packages(),
    install_requires=[],
)
''',

    "requirements.txt": '''\
# Core ML
torch>=2.0.0
torchvision
numpy
pandas
scikit-learn
faiss-cpu

# API
fastapi
uvicorn[standard]
pydantic

# Tracking
mlflow

# Data
requests
PyYAML
tqdm

# Testing
pytest

# Frontend (install separately via npm)
# react, react-dom, axios, tailwindcss
''',

    ".gitignore": '''\
# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
.env

# Data & Models
data/raw/
data/processed/
models/
artifacts/
logs/
mlflow/

# Node
frontend/node_modules/
frontend/.env

# Jupyter
.ipynb_checkpoints/

# OS
.DS_Store
''',

    "README.md": '''\
# 🎬 End-to-End Deep Learning Movie Recommendation System

## Tech Stack
- **Model**: Neural Collaborative Filtering (NeuralCF) + FAISS
- **Dataset**: MovieLens 20M
- **Tracking**: MLflow
- **API**: FastAPI
- **Frontend**: React + TailwindCSS
- **Deployment**: Docker + Docker Compose

## Project Structure
```
recommendation-system/
├── src/
│   ├── components/       # ML pipeline components
│   ├── pipeline/         # Train & predict pipelines
│   ├── entity/           # Config & artifact dataclasses
│   ├── config/           # Central configuration
│   ├── constants/        # All constants
│   ├── exception/        # Custom exceptions
│   ├── logger/           # Custom logger
│   └── utils/            # Helper utilities
├── api/                  # FastAPI backend
├── frontend/             # React frontend
├── models/               # Saved model artifacts
├── notebooks/            # EDA & experiments
├── tests/                # Unit & integration tests
├── app.py                # Training entry point
└── run_api.py            # API entry point
```

## Quickstart
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Train the model
python app.py

# 3. Start API
python run_api.py

# 4. Start frontend
cd frontend && npm install && npm start

# 5. Monitor training (MLflow UI)
mlflow ui --port 5000
```

## API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/recommend/{user_id} | Get top-K recommendations |
| GET | /api/v1/similar/{item_id} | Get similar movies |
| POST | /api/v1/feedback | Log user feedback |
| GET | /health | Health check |
''',

    "docker-compose.yml": '''\
version: "3.9"

services:
  mlflow:
    image: ghcr.io/mlflow/mlflow:latest
    ports:
      - "5000:5000"
    command: mlflow server --host 0.0.0.0

  api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./models:/app/models
      - ./logs:/app/logs
    depends_on:
      - mlflow
    command: python run_api.py

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - api
''',

    "Dockerfile": '''\
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "run_api.py"]
''',

    "src/constants/__init__.py": '''\
import os

# Directories
ARTIFACT_DIR   = "artifacts"
DATA_DIR       = "data"
MODEL_DIR      = "models"

# Dataset
DATASET_URL    = "https://files.grouplens.org/datasets/movielens/ml-20m.zip"
RAW_DATA_FILE  = "ratings.csv"

# Model hyperparameters
EMBED_DIM      = 128
HIDDEN_LAYERS  = [256, 128, 64, 32]
DROPOUT_RATE   = 0.2
LEARNING_RATE  = 1e-3
BATCH_SIZE     = 4096
EPOCHS         = 30
TOP_K          = 10

# Evaluation threshold
MIN_NDCG_THRESHOLD = 0.35

# Artifact filenames
FAISS_INDEX_FILE = "item_index.faiss"
MODEL_FILE       = "model.pt"
ENCODER_FILE     = "encoders.pkl"

# MLflow
MLFLOW_TRACKING_URI = "http://localhost:5000"
EXPERIMENT_NAME     = "NeuralCF_MovieLens20M"

# TMDb
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"
''',

    "src/logger/__init__.py": '''\
import logging
import os
from datetime import datetime

LOG_FILE      = f"{datetime.now().strftime(\'%Y_%m_%d_%H_%M_%S\')}.log"
LOG_DIR       = os.path.join(os.getcwd(), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE_PATH = os.path.join(LOG_DIR, LOG_FILE)

logging.basicConfig(
    filename=LOG_FILE_PATH,
    format="[ %(asctime)s ] %(lineno)d %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger("RecommendationSystem")

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter(
    "[ %(asctime)s ] %(lineno)d %(name)s - %(levelname)s - %(message)s"
))
logger.addHandler(console_handler)
''',

    "src/exception/__init__.py": '''\
import sys
from src.logger import logger


def error_message_detail(error, error_detail: sys):
    _, _, exc_tb = error_detail.exc_info()
    file_name   = exc_tb.tb_frame.f_code.co_filename
    line_number = exc_tb.tb_lineno
    return (
        f"Error in script: [{file_name}] "
        f"at line [{line_number}]: {str(error)}"
    )


class RecommendationException(Exception):
    def __init__(self, error_message, error_detail: sys):
        super().__init__(error_message)
        self.error_message = error_message_detail(error_message, error_detail)
        logger.error(self.error_message)

    def __str__(self):
        return self.error_message
''',

    "src/entity/config_entity.py": '''\
from dataclasses import dataclass, field
from src.constants import *
import os


@dataclass
class DataIngestionConfig:
    raw_data_dir:     str = os.path.join(ARTIFACT_DIR, "data_ingestion", "raw")
    ingested_data_dir: str = os.path.join(ARTIFACT_DIR, "data_ingestion", "ingested")
    dataset_url:      str = DATASET_URL


@dataclass
class DataValidationConfig:
    report_file_path:  str  = os.path.join(ARTIFACT_DIR, "data_validation", "report.yaml")
    required_columns: list = field(default_factory=lambda: ["user_id", "item_id", "rating"])


@dataclass
class DataTransformationConfig:
    transformed_train_path: str = os.path.join(ARTIFACT_DIR, "data_transformation", "train.csv")
    transformed_test_path:  str = os.path.join(ARTIFACT_DIR, "data_transformation", "test.csv")
    encoder_path:           str = os.path.join(ARTIFACT_DIR, "data_transformation", ENCODER_FILE)


@dataclass
class ModelTrainerConfig:
    model_path:    str   = os.path.join(ARTIFACT_DIR, "model_trainer", MODEL_FILE)
    embed_dim:     int   = EMBED_DIM
    hidden_layers: list  = field(default_factory=lambda: HIDDEN_LAYERS)
    dropout:       float = DROPOUT_RATE
    lr:            float = LEARNING_RATE
    batch_size:    int   = BATCH_SIZE
    epochs:        int   = EPOCHS


@dataclass
class ModelEvaluationConfig:
    evaluation_report_path: str   = os.path.join(ARTIFACT_DIR, "model_evaluation", "report.yaml")
    top_k:                  int   = TOP_K
    ndcg_threshold:         float = MIN_NDCG_THRESHOLD


@dataclass
class ModelPusherConfig:
    production_model_dir: str = MODEL_DIR
    faiss_index_path:     str = os.path.join(MODEL_DIR, FAISS_INDEX_FILE)
    final_model_path:     str = os.path.join(MODEL_DIR, MODEL_FILE)
    final_encoder_path:   str = os.path.join(MODEL_DIR, ENCODER_FILE)
''',

    "src/entity/artifact_entity.py": '''\
from dataclasses import dataclass


@dataclass
class DataIngestionArtifact:
    raw_file_path: str
    status:        bool
    message:       str


@dataclass
class DataValidationArtifact:
    validation_status: bool
    report_file_path:  str
    message:           str


@dataclass
class DataTransformationArtifact:
    transformed_train_path: str
    transformed_test_path:  str
    encoder_path:           str
    n_users:                int
    n_items:                int


@dataclass
class ModelTrainerArtifact:
    model_path:  str
    train_loss:  float
    val_loss:    float


@dataclass
class ModelEvaluationArtifact:
    is_model_accepted: bool
    ndcg_score:        float
    hit_rate:          float
    report_path:       str


@dataclass
class ModelPusherArtifact:
    model_pushed:          bool
    production_model_path: str
    faiss_index_path:      str
''',

    "src/utils/main_utils.py": '''\
import os
import sys
import pickle
import yaml
import torch
from src.logger import logger
from src.exception import RecommendationException


def save_object(file_path: str, obj):
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f:
            pickle.dump(obj, f)
        logger.info(f"Object saved at: {file_path}")
    except Exception as e:
        raise RecommendationException(e, sys)


def load_object(file_path: str):
    try:
        with open(file_path, "rb") as f:
            return pickle.load(f)
    except Exception as e:
        raise RecommendationException(e, sys)


def save_yaml(file_path: str, data: dict):
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            yaml.dump(data, f)
    except Exception as e:
        raise RecommendationException(e, sys)


def save_model(model, path: str):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        torch.save(model.state_dict(), path)
        logger.info(f"Model saved at: {path}")
    except Exception as e:
        raise RecommendationException(e, sys)


def load_model(model, path: str):
    try:
        model.load_state_dict(torch.load(path, map_location="cpu"))
        model.eval()
        return model
    except Exception as e:
        raise RecommendationException(e, sys)
''',

    "src/pipeline/training_pipeline.py": '''\
import sys
from src.logger import logger
from src.exception import RecommendationException
from src.components.data_ingestion import DataIngestion
from src.components.data_validation import DataValidation
from src.components.data_transformation import DataTransformation
from src.components.model_trainer import ModelTrainer
from src.components.model_evaluation import ModelEvaluation
from src.components.model_pusher import ModelPusher
from src.entity.config_entity import (
    DataIngestionConfig, DataValidationConfig, DataTransformationConfig,
    ModelTrainerConfig, ModelEvaluationConfig, ModelPusherConfig
)


class TrainingPipeline:
    def __init__(self):
        self.data_ingestion_config     = DataIngestionConfig()
        self.data_validation_config    = DataValidationConfig()
        self.data_transformation_config = DataTransformationConfig()
        self.model_trainer_config      = ModelTrainerConfig()
        self.model_evaluation_config   = ModelEvaluationConfig()
        self.model_pusher_config       = ModelPusherConfig()

    def run_pipeline(self):
        try:
            logger.info("=" * 60)
            logger.info("       TRAINING PIPELINE STARTED")
            logger.info("=" * 60)

            ingestion_artifact = DataIngestion(self.data_ingestion_config).initiate_data_ingestion()
            validation_artifact = DataValidation(self.data_validation_config, ingestion_artifact).initiate_data_validation()
            transformation_artifact = DataTransformation(self.data_transformation_config, validation_artifact).initiate_data_transformation()
            trainer_artifact = ModelTrainer(self.model_trainer_config, transformation_artifact).initiate_model_training()
            evaluation_artifact = ModelEvaluation(self.model_evaluation_config, transformation_artifact, trainer_artifact).initiate_model_evaluation()
            pusher_artifact = ModelPusher(self.model_pusher_config, evaluation_artifact, transformation_artifact, trainer_artifact).initiate_model_pusher()

            logger.info("=" * 60)
            logger.info("    TRAINING PIPELINE COMPLETED SUCCESSFULLY")
            logger.info("=" * 60)
            return pusher_artifact

        except Exception as e:
            raise RecommendationException(e, sys)
''',

    "src/pipeline/prediction_pipeline.py": '''\
import os
import sys
import torch
import faiss
import numpy as np
from src.logger import logger
from src.exception import RecommendationException
from src.utils.main_utils import load_object, load_model
from src.components.model_trainer import NeuralCF
from src.constants import MODEL_DIR, FAISS_INDEX_FILE, MODEL_FILE, ENCODER_FILE, TOP_K


class PredictionPipeline:
    _model    = None
    _index    = None
    _encoders = None

    @classmethod
    def load_artifacts(cls):
        if cls._model is None:
            logger.info("Loading model artifacts for inference...")
            cls._encoders = load_object(os.path.join(MODEL_DIR, ENCODER_FILE))
            model = NeuralCF(cls._encoders["n_users"], cls._encoders["n_items"])
            cls._model = load_model(model, os.path.join(MODEL_DIR, MODEL_FILE))
            cls._index = faiss.read_index(os.path.join(MODEL_DIR, FAISS_INDEX_FILE))
            logger.info("Artifacts loaded.")

    def get_recommendations(self, user_id: int, top_k: int = TOP_K):
        try:
            self.load_artifacts()
            with torch.no_grad():
                user_emb = self._model.user_embed(torch.tensor([user_id])).numpy().astype("float32")
            faiss.normalize_L2(user_emb)
            scores, indices = self._index.search(user_emb, top_k)
            original_ids = self._encoders["item_enc"].inverse_transform(indices[0]).tolist()
            return {"user_id": user_id, "recommended_item_ids": original_ids, "scores": scores[0].tolist()}
        except Exception as e:
            raise RecommendationException(e, sys)

    def get_similar_items(self, item_id: int, top_k: int = TOP_K):
        try:
            self.load_artifacts()
            encoded_id = self._encoders["item_enc"].transform([item_id])[0]
            with torch.no_grad():
                item_emb = self._model.item_embed(torch.tensor([encoded_id])).numpy().astype("float32")
            faiss.normalize_L2(item_emb)
            scores, indices = self._index.search(item_emb, top_k + 1)
            similar = self._encoders["item_enc"].inverse_transform(indices[0][1:]).tolist()
            return {"item_id": item_id, "similar_items": similar, "scores": scores[0][1:].tolist()}
        except Exception as e:
            raise RecommendationException(e, sys)
''',

    "api/main.py": '''\
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from api.routes import recommend, feedback
from src.pipeline.prediction_pipeline import PredictionPipeline
from src.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("API starting up — loading artifacts...")
    PredictionPipeline.load_artifacts()
    yield
    logger.info("API shutting down.")

app = FastAPI(
    title="Movie Recommendation System API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(recommend.router, prefix="/api/v1", tags=["Recommendations"])
app.include_router(feedback.router,  prefix="/api/v1", tags=["Feedback"])


@app.get("/health")
def health():
    return {"status": "ok"}
''',

    "api/routes/recommend.py": '''\
from fastapi import APIRouter, HTTPException
from src.pipeline.prediction_pipeline import PredictionPipeline
from src.logger import logger

router   = APIRouter()
pipeline = PredictionPipeline()


@router.get("/recommend/{user_id}")
def get_recommendations(user_id: int, top_k: int = 10):
    try:
        logger.info(f"Recommend request: user_id={user_id}, top_k={top_k}")
        return pipeline.get_recommendations(user_id, top_k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/similar/{item_id}")
def get_similar_items(item_id: int, top_k: int = 10):
    try:
        return pipeline.get_similar_items(item_id, top_k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
''',

    "api/routes/feedback.py": '''\
from fastapi import APIRouter
from pydantic import BaseModel
from src.logger import logger

router = APIRouter()


class FeedbackRequest(BaseModel):
    user_id: int
    item_id: int
    clicked: bool
    rating:  float = None


@router.post("/feedback")
def log_feedback(feedback: FeedbackRequest):
    logger.info(f"Feedback received: {feedback}")
    # TODO: persist to PostgreSQL / Redis for retraining
    return {"status": "ok", "message": "Feedback logged"}
''',

    "api/schemas/models.py": '''\
from pydantic import BaseModel
from typing import List, Optional


class RecommendationResponse(BaseModel):
    user_id:               int
    recommended_item_ids:  List[int]
    scores:                List[float]


class SimilarItemsResponse(BaseModel):
    item_id:       int
    similar_items: List[int]
    scores:        List[float]


class FeedbackRequest(BaseModel):
    user_id: int
    item_id: int
    clicked: bool
    rating:  Optional[float] = None
''',

    "tests/test_data_ingestion.py": '''\
import pytest
from src.components.data_ingestion import DataIngestion
from src.entity.config_entity import DataIngestionConfig


def test_data_ingestion_config():
    config = DataIngestionConfig()
    assert config.dataset_url != ""
    assert "ml-20m" in config.dataset_url or "movielens" in config.dataset_url
''',

    "tests/test_prediction_pipeline.py": '''\
import pytest


def test_prediction_pipeline_import():
    from src.pipeline.prediction_pipeline import PredictionPipeline
    pipeline = PredictionPipeline()
    assert pipeline is not None
''',

    "frontend/package.json": '''\
{
  "name": "recommendation-frontend",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "axios": "^1.6.0",
    "react-scripts": "5.0.1"
  },
  "devDependencies": {
    "tailwindcss": "^3.3.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test"
  }
}
''',

    "frontend/src/services/api.js": '''\
import axios from "axios";

const BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000/api/v1";

const api = axios.create({ baseURL: BASE_URL });

export const getRecommendations = (userId, topK = 10) =>
  api.get(`/recommend/${userId}`, { params: { top_k: topK } });

export const getSimilarMovies = (itemId, topK = 10) =>
  api.get(`/similar/${itemId}`, { params: { top_k: topK } });

export const sendFeedback = (userId, itemId, clicked, rating = null) =>
  api.post("/feedback", { user_id: userId, item_id: itemId, clicked, rating });

export default api;
''',
}

# ─────────────────────────────────────────────
#  File & folder creation logic
# ─────────────────────────────────────────────
def create_project():
    logger.info("Starting project structure creation...")
    created_files = 0
    created_dirs  = 0

    for file_path_str in project_files:
        file_path = Path(file_path_str)
        directory = file_path.parent

        # Create parent directories
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"  📁 Created directory : {directory}")
            created_dirs += 1

        # Create file if it doesn't exist
        if not file_path.exists():
            content = file_content_map.get(file_path_str, "")
            file_path.write_text(content, encoding="utf-8")
            label = "📝" if content else "📄"
            logger.info(f"  {label} Created file      : {file_path}")
            created_files += 1
        else:
            logger.info(f"  ⏭️  Already exists    : {file_path}")

    logger.info("")
    logger.info("=" * 55)
    logger.info("  ✅  Project structure created successfully!")
    logger.info(f"      Directories created : {created_dirs}")
    logger.info(f"      Files created       : {created_files}")
    logger.info("=" * 55)
    logger.info("")
    logger.info("  Next steps:")
    logger.info("    1.  pip install -r requirements.txt")
    logger.info("    2.  python app.py          # train the model")
    logger.info("    3.  python run_api.py      # start the API")
    logger.info("    4.  cd frontend && npm install && npm start")
    logger.info("    5.  mlflow ui --port 5000  # monitor training")
    logger.info("=" * 55)


if __name__ == "__main__":
    create_project()