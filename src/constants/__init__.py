# src/constants/__init__.py  — LOCAL machine version
import os

ARTIFACT_DIR = "artifacts"
DATA_DIR     = "data"
MODEL_DIR    = "models"

DATASET_URL   = "https://files.grouplens.org/datasets/movielens/ml-1m.zip"
RAW_DATA_FILE = "ratings.dat"

# ✅ Must match Kaggle training exactly
EMBED_DIM     = 64
HIDDEN_LAYERS = [128, 64, 32]
DROPOUT_RATE  = 0.2
LEARNING_RATE = 1e-3
BATCH_SIZE    = 2048
EPOCHS        = 15
TOP_K         = 10

NEG_SAMPLE_RATIO   = 4
MIN_NDCG_THRESHOLD = 0.32
EVAL_USERS         = 300

FAISS_INDEX_FILE = "item_index.faiss"
MODEL_FILE       = "model.pt"
ENCODER_FILE     = "encoders.pkl"

MLFLOW_TRACKING_URI = "file:///mlruns"
EXPERIMENT_NAME     = "NeuralCF_embed64"

TMDB_API_KEY    = os.getenv("TMDB_API_KEY", "")
TMDB_BASE_URL   = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"