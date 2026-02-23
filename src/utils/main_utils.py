# src/utils/main_utils.py
import os, sys, pickle, yaml, torch
import numpy as np
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