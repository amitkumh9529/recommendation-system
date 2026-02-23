# src/components/model_pusher.py
import os, sys, shutil
import torch
import faiss
import numpy as np
from src.logger import logger
from src.exception import RecommendationException
from src.entity.config_entity import ModelPusherConfig
from src.entity.artifact_entity import (
    ModelEvaluationArtifact, DataTransformationArtifact,
    ModelTrainerArtifact, ModelPusherArtifact
)
from src.utils.main_utils import load_object, load_model
from src.components.model_trainer import NeuralCF
from src.constants import EMBED_DIM, HIDDEN_LAYERS, DROPOUT_RATE

class ModelPusher:
    def __init__(self, config: ModelPusherConfig,
                 eval_artifact: ModelEvaluationArtifact,
                 trans_artifact: DataTransformationArtifact,
                 trainer_artifact: ModelTrainerArtifact):
        self.config           = config
        self.eval_artifact    = eval_artifact
        self.trans_artifact   = trans_artifact
        self.trainer_artifact = trainer_artifact

    def build_faiss_index(self, model, n_items):
        all_items = torch.arange(n_items)
        with torch.no_grad():
            item_embeddings = model.item_embed(all_items).numpy().astype("float32")
        faiss.normalize_L2(item_embeddings)
        index = faiss.IndexFlatIP(EMBED_DIM)
        index.add(item_embeddings)
        faiss.write_index(index, self.config.faiss_index_path)
        logger.info(f"FAISS index built with {n_items} items.")

    def initiate_model_pusher(self) -> ModelPusherArtifact:
        try:
            logger.info(">>> Starting Model Pusher <<<")
            if not self.eval_artifact.is_model_accepted:
                logger.warning("Model not accepted. Skipping push.")
                return ModelPusherArtifact(
                    model_pushed=False, production_model_path="", faiss_index_path=""
                )

            os.makedirs(self.config.production_model_dir, exist_ok=True)
            encoders = load_object(self.trans_artifact.encoder_path)
            n_users, n_items = encoders["n_users"], encoders["n_items"]

            model = NeuralCF(n_users, n_items, EMBED_DIM, HIDDEN_LAYERS, DROPOUT_RATE)
            model = load_model(model, self.trainer_artifact.model_path)

            self.build_faiss_index(model, n_items)
            shutil.copy(self.trainer_artifact.model_path,   self.config.final_model_path)
            shutil.copy(self.trans_artifact.encoder_path,   self.config.final_encoder_path)

            logger.info(f"Model pushed to: {self.config.production_model_dir}")
            return ModelPusherArtifact(
                model_pushed=True,
                production_model_path=self.config.final_model_path,
                faiss_index_path=self.config.faiss_index_path
            )
        except Exception as e:
            raise RecommendationException(e, sys)