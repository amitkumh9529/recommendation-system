# src/components/model_evaluation.py
import os, sys
import torch
import numpy as np
import pandas as pd
from src.logger import logger
from src.exception import RecommendationException
from src.entity.config_entity import ModelEvaluationConfig
from src.entity.artifact_entity import DataTransformationArtifact, ModelTrainerArtifact, ModelEvaluationArtifact
from src.utils.main_utils import load_object, load_model, save_yaml
from src.components.model_trainer import NeuralCF
from src.constants import EVAL_USERS, EMBED_DIM, HIDDEN_LAYERS, DROPOUT_RATE

def ndcg_at_k(actual, predicted, k=10):
    dcg = idcg = 0.0
    for i, p in enumerate(predicted[:k]):
        if p in actual:
            dcg += 1 / np.log2(i + 2)
    for i in range(min(len(actual), k)):
        idcg += 1 / np.log2(i + 2)
    return dcg / idcg if idcg > 0 else 0.0

def hit_rate_at_k(actual, predicted, k=10):
    return int(len(set(predicted[:k]) & set(actual)) > 0)

class ModelEvaluation:
    def __init__(self, config: ModelEvaluationConfig,
                 transformation_artifact: DataTransformationArtifact,
                 trainer_artifact: ModelTrainerArtifact):
        self.config           = config
        self.trans_artifact   = transformation_artifact
        self.trainer_artifact = trainer_artifact

    def initiate_model_evaluation(self) -> ModelEvaluationArtifact:
        try:
            logger.info(">>> Starting Model Evaluation <<<")
            encoders = load_object(self.trans_artifact.encoder_path)
            n_users, n_items = encoders["n_users"], encoders["n_items"]

            # ✅ Must match training architecture exactly
            model = NeuralCF(n_users, n_items, EMBED_DIM, HIDDEN_LAYERS, DROPOUT_RATE)
            model = load_model(model, self.trainer_artifact.model_path)
            model.eval()

            test_df  = pd.read_csv(self.trans_artifact.transformed_test_path)
            test_pos = (
                test_df[test_df["rating"] > 0.5]
                .groupby("user")["item"].apply(list).to_dict()
            )

            ndcg_scores, hit_rates = [], []
            all_items = torch.arange(n_items)

            sample_users = list(test_pos.items())[:EVAL_USERS]
            logger.info(f"Evaluating on {len(sample_users)} users...")

            with torch.no_grad():
                for user_id, actual_items in sample_users:
                    user_tensor = torch.tensor([user_id] * n_items)
                    scores      = model(user_tensor, all_items).numpy()
                    top_k       = np.argsort(scores)[::-1][:self.config.top_k].tolist()
                    ndcg_scores.append(ndcg_at_k(actual_items, top_k, self.config.top_k))
                    hit_rates.append(hit_rate_at_k(actual_items, top_k, self.config.top_k))

            avg_ndcg    = float(np.mean(ndcg_scores))
            avg_hr      = float(np.mean(hit_rates))
            is_accepted = avg_ndcg >= self.config.ndcg_threshold

            report = {
                "NDCG@10": avg_ndcg, "HitRate@10": avg_hr,
                "model_accepted": is_accepted,
                "users_evaluated": len(sample_users)
            }
            save_yaml(self.config.evaluation_report_path, report)
            logger.info(f"NDCG@10={avg_ndcg:.4f} | HitRate@10={avg_hr:.4f} | Accepted={is_accepted}")

            return ModelEvaluationArtifact(
                is_model_accepted=is_accepted,
                ndcg_score=avg_ndcg,
                hit_rate=avg_hr,
                report_path=self.config.evaluation_report_path
            )
        except Exception as e:
            raise RecommendationException(e, sys)