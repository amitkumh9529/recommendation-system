# src/components/data_transformation.py
import os, sys
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from src.logger import logger
from src.exception import RecommendationException
from src.entity.config_entity import DataTransformationConfig
from src.entity.artifact_entity import DataValidationArtifact, DataTransformationArtifact
from src.utils.main_utils import save_object
from src.constants import NEG_SAMPLE_RATIO

class DataTransformation:
    def __init__(self, config: DataTransformationConfig, validation_artifact: DataValidationArtifact):
        self.config = config
        self.validation_artifact = validation_artifact

    def initiate_data_transformation(self) -> DataTransformationArtifact:
        try:
            logger.info(">>> Starting Data Transformation <<<")
            if not self.validation_artifact.validation_status:
                raise Exception("Cannot transform: Data validation failed.")

            ratings_path = os.path.join(
                "artifacts/data_ingestion/ingested", "ml-1m", "ratings.dat"
            )
            df = pd.read_csv(
                ratings_path, sep="::", engine="python",
                names=["user_id", "item_id", "rating", "timestamp"]
            )
            logger.info(f"Loaded {len(df):,} ratings")

            user_enc = LabelEncoder()
            item_enc = LabelEncoder()
            df["user"]   = user_enc.fit_transform(df["user_id"])
            df["item"]   = item_enc.fit_transform(df["item_id"])
            df["rating"] = (df["rating"] >= 4).astype(float)

            n_users = df["user"].nunique()
            n_items = df["item"].nunique()
            logger.info(f"Users: {n_users:,} | Items: {n_items:,}")

            logger.info(f"Generating {NEG_SAMPLE_RATIO}x negative samples...")
            interactions = set(zip(df["user"], df["item"]))
            pos_df = df[df["rating"] == 1.0]
            neg_users, neg_items = [], []
            for u in pos_df["user"].unique():
                for _ in range(NEG_SAMPLE_RATIO):
                    neg_item = np.random.randint(0, n_items)
                    while (u, neg_item) in interactions:
                        neg_item = np.random.randint(0, n_items)
                    neg_users.append(u)
                    neg_items.append(neg_item)

            neg_df  = pd.DataFrame({"user": neg_users, "item": neg_items, "rating": 0.0})
            full_df = pd.concat(
                [df[["user", "item", "rating"]], neg_df], ignore_index=True
            ).sample(frac=1, random_state=42).reset_index(drop=True)

            logger.info(f"Total samples: {len(full_df):,}")
            train, test = train_test_split(full_df, test_size=0.2, random_state=42)

            os.makedirs(os.path.dirname(self.config.transformed_train_path), exist_ok=True)
            train.to_csv(self.config.transformed_train_path, index=False)
            test.to_csv(self.config.transformed_test_path,  index=False)

            encoders = {
                "user_enc": user_enc, "item_enc": item_enc,
                "n_users": n_users,   "n_items": n_items
            }
            save_object(self.config.encoder_path, encoders)

            artifact = DataTransformationArtifact(
                transformed_train_path=self.config.transformed_train_path,
                transformed_test_path=self.config.transformed_test_path,
                encoder_path=self.config.encoder_path,
                n_users=n_users, n_items=n_items
            )
            logger.info(f"Data Transformation Artifact: {artifact}")
            return artifact
        except Exception as e:
            raise RecommendationException(e, sys)