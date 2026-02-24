# src/components/model_trainer.py
import os, sys
import torch
import torch.nn as nn
import pandas as pd
from torch.utils.data import Dataset, DataLoader
import mlflow
import mlflow.pytorch
from src.logger import logger
from src.exception import RecommendationException
from src.entity.config_entity import ModelTrainerConfig
from src.entity.artifact_entity import DataTransformationArtifact, ModelTrainerArtifact
from src.utils.main_utils import save_model
from src.constants import MLFLOW_TRACKING_URI, EXPERIMENT_NAME, EMBED_DIM, HIDDEN_LAYERS, DROPOUT_RATE

class RatingsDataset(Dataset):
    def __init__(self, df):
        self.users   = torch.tensor(df["user"].values,   dtype=torch.long)
        self.items   = torch.tensor(df["item"].values,   dtype=torch.long)
        self.ratings = torch.tensor(df["rating"].values, dtype=torch.float)
    def __len__(self): return len(self.ratings)
    def __getitem__(self, idx): return self.users[idx], self.items[idx], self.ratings[idx]

class NeuralCF(nn.Module):
    def __init__(self, n_users, n_items,
                 embed_dim=EMBED_DIM,
                 hidden_layers=None,
                 dropout=DROPOUT_RATE):
        super().__init__()
        if hidden_layers is None:
            hidden_layers = HIDDEN_LAYERS
        self.user_embed = nn.Embedding(n_users, embed_dim)
        self.item_embed = nn.Embedding(n_items, embed_dim)
        layers, input_dim = [], embed_dim * 2
        for h in hidden_layers:
            layers += [
                nn.Linear(input_dim, h),
                nn.BatchNorm1d(h),
                nn.ReLU(),
                nn.Dropout(dropout)
            ]
            input_dim = h
        layers += [nn.Linear(input_dim, 1), nn.Sigmoid()]
        self.mlp = nn.Sequential(*layers)
        nn.init.normal_(self.user_embed.weight, std=0.01)
        nn.init.normal_(self.item_embed.weight, std=0.01)

    def forward(self, users, items):
        x = torch.cat([self.user_embed(users), self.item_embed(items)], dim=-1)
        return self.mlp(x).squeeze(-1)

class ModelTrainer:
    def __init__(self, config: ModelTrainerConfig, transformation_artifact: DataTransformationArtifact):
        self.config   = config
        self.artifact = transformation_artifact
        self.device   = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def initiate_model_training(self) -> ModelTrainerArtifact:
        try:
            logger.info(">>> Starting Model Training <<<")
            logger.info(f"Device: {self.device}")

            train_df = pd.read_csv(self.artifact.transformed_train_path)
            val_df   = pd.read_csv(self.artifact.transformed_test_path)

            train_loader = DataLoader(RatingsDataset(train_df), batch_size=self.config.batch_size, shuffle=True)
            val_loader   = DataLoader(RatingsDataset(val_df),   batch_size=self.config.batch_size)

            model = NeuralCF(
                self.artifact.n_users, self.artifact.n_items,
                self.config.embed_dim, self.config.hidden_layers, self.config.dropout
            ).to(self.device)

            optimizer = torch.optim.Adam(model.parameters(), lr=self.config.lr, weight_decay=1e-5)
            scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.5)
            criterion = nn.BCELoss()

            mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
            mlflow.set_experiment(EXPERIMENT_NAME)

            best_val_loss = float("inf")
            avg_train = avg_val = 0

            with mlflow.start_run():
                mlflow.log_params({
                    "embed_dim":     self.config.embed_dim,
                    "hidden_layers": str(self.config.hidden_layers),
                    "lr":            self.config.lr,
                    "batch_size":    self.config.batch_size,
                    "epochs":        self.config.epochs,
                })

                for epoch in range(self.config.epochs):
                    model.train()
                    total_loss = 0
                    for users, items, labels in train_loader:
                        users, items, labels = users.to(self.device), items.to(self.device), labels.to(self.device)
                        preds = model(users, items)
                        loss  = criterion(preds, labels)
                        optimizer.zero_grad()
                        loss.backward()
                        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                        optimizer.step()
                        total_loss += loss.item()

                    model.eval()
                    val_loss = 0
                    with torch.no_grad():
                        for users, items, labels in val_loader:
                            users, items, labels = users.to(self.device), items.to(self.device), labels.to(self.device)
                            val_loss += criterion(model(users, items), labels).item()

                    avg_train = total_loss / len(train_loader)
                    avg_val   = val_loss   / len(val_loader)
                    scheduler.step()

                    logger.info(f"Epoch [{epoch+1}/{self.config.epochs}] Train: {avg_train:.4f} | Val: {avg_val:.4f}")
                    mlflow.log_metrics({"train_loss": avg_train, "val_loss": avg_val}, step=epoch)

                    if avg_val < best_val_loss:
                        best_val_loss = avg_val
                        save_model(model, self.config.model_path)
                        logger.info(f"  ✅ Best model saved (epoch {epoch+1})")

                mlflow.pytorch.log_model(model, "model")

            artifact = ModelTrainerArtifact(
                model_path=self.config.model_path,
                train_loss=avg_train,
                val_loss=best_val_loss
            )
            logger.info(f"Model Trainer Artifact: {artifact}")
            return artifact
        except Exception as e:
            raise RecommendationException(e, sys)