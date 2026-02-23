from src.pipeline.training_pipeline import TrainingPipeline
from src.logger import logger

if __name__ == "__main__":
    try:
        pipeline = TrainingPipeline()
        pipeline.run_pipeline()
    except Exception as e:
        logger.exception(f"Training pipeline failed: {e}")
        raise e
