# src/pipeline/training_pipeline.py
import sys
from src.logger import logger
from src.exception import RecommendationException
from src.components.data_ingestion import DataIngestion
from src.components.data_validation import DataValidation
from src.components.data_transformation import DataTransformation
from src.components.model_trainer import ModelTrainer
from src.components.model_evaluation import ModelEvaluation
from src.components.model_pusher import ModelPusher
from src.entity.config_entity import (DataIngestionConfig, DataValidationConfig,
    DataTransformationConfig, ModelTrainerConfig, ModelEvaluationConfig, ModelPusherConfig)

class TrainingPipeline:
    def __init__(self):
        self.data_ingestion_config = DataIngestionConfig()
        self.data_validation_config = DataValidationConfig()
        self.data_transformation_config = DataTransformationConfig()
        self.model_trainer_config = ModelTrainerConfig()
        self.model_evaluation_config = ModelEvaluationConfig()
        self.model_pusher_config = ModelPusherConfig()

    def run_pipeline(self):
        try:
            logger.info("=" * 60)
            logger.info("    TRAINING PIPELINE STARTED")
            logger.info("=" * 60)

            # Stage 1: Data Ingestion
            data_ingestion = DataIngestion(self.data_ingestion_config)
            ingestion_artifact = data_ingestion.initiate_data_ingestion()

            # Stage 2: Data Validation
            data_validation = DataValidation(self.data_validation_config, ingestion_artifact)
            validation_artifact = data_validation.initiate_data_validation()

            # Stage 3: Data Transformation
            data_transformation = DataTransformation(self.data_transformation_config, validation_artifact)
            transformation_artifact = data_transformation.initiate_data_transformation()

            # Stage 4: Model Training
            model_trainer = ModelTrainer(self.model_trainer_config, transformation_artifact)
            trainer_artifact = model_trainer.initiate_model_training()

            # Stage 5: Model Evaluation
            model_evaluation = ModelEvaluation(self.model_evaluation_config, transformation_artifact, trainer_artifact)
            evaluation_artifact = model_evaluation.initiate_model_evaluation()

            # Stage 6: Model Pusher
            model_pusher = ModelPusher(self.model_pusher_config, evaluation_artifact, transformation_artifact, trainer_artifact)
            pusher_artifact = model_pusher.initiate_model_pusher()

            logger.info("=" * 60)
            logger.info("    TRAINING PIPELINE COMPLETED SUCCESSFULLY")
            logger.info("=" * 60)
            return pusher_artifact

        except Exception as e:
            raise RecommendationException(e, sys)