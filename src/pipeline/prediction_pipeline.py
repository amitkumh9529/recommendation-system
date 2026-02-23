# src/pipeline/prediction_pipeline.py
import sys
import torch
import faiss
import numpy as np
from src.logger import logger
from src.exception import RecommendationException
from src.utils.main_utils import load_object, load_model
from src.components.model_trainer import NeuralCF
from src.constants import MODEL_DIR, FAISS_INDEX_FILE, MODEL_FILE, ENCODER_FILE, TOP_K
import os

class PredictionPipeline:
    _model = None
    _index = None
    _encoders = None

    @classmethod
    def load_artifacts(cls):
        if cls._model is None:
            logger.info("Loading model artifacts for inference...")
            encoders = load_object(os.path.join(MODEL_DIR, ENCODER_FILE))
            cls._encoders = encoders
            model = NeuralCF(encoders["n_users"], encoders["n_items"])
            cls._model = load_model(model, os.path.join(MODEL_DIR, MODEL_FILE))
            cls._index = faiss.read_index(os.path.join(MODEL_DIR, FAISS_INDEX_FILE))
            logger.info("Artifacts loaded successfully.")

    def get_recommendations(self, user_id: int, top_k: int = TOP_K):
        try:
            self.load_artifacts()
            with torch.no_grad():
                user_emb = self._model.user_embed(
                    torch.tensor([user_id])
                ).numpy().astype("float32")

            faiss.normalize_L2(user_emb)
            scores, item_indices = self._index.search(user_emb, top_k)
            item_enc = self._encoders["item_enc"]
            original_item_ids = item_enc.inverse_transform(item_indices[0]).tolist()

            return {
                "user_id": user_id,
                "recommended_item_ids": original_item_ids,
                "scores": scores[0].tolist()
            }
        except Exception as e:
            raise RecommendationException(e, sys)

    def get_similar_items(self, item_id: int, top_k: int = TOP_K):
        try:
            self.load_artifacts()
            item_enc = self._encoders["item_enc"]
            encoded_id = item_enc.transform([item_id])[0]

            with torch.no_grad():
                item_emb = self._model.item_embed(
                    torch.tensor([encoded_id])
                ).numpy().astype("float32")

            faiss.normalize_L2(item_emb)
            scores, similar_indices = self._index.search(item_emb, top_k + 1)
            similar_items = item_enc.inverse_transform(similar_indices[0][1:]).tolist()  # exclude self

            return {"item_id": item_id, "similar_items": similar_items, "scores": scores[0][1:].tolist()}
        except Exception as e:
            raise RecommendationException(e, sys)