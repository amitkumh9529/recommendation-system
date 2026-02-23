# api/routes/recommend.py
from fastapi import APIRouter, HTTPException
from src.pipeline.prediction_pipeline import PredictionPipeline
from src.logger import logger

router = APIRouter()
pipeline = PredictionPipeline()

@router.get("/recommend/{user_id}")
def get_recommendations(user_id: int, top_k: int = 10):
    try:
        logger.info(f"Recommendation request: user_id={user_id}, top_k={top_k}")
        result = pipeline.get_recommendations(user_id, top_k)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/similar/{item_id}")
def get_similar_items(item_id: int, top_k: int = 10):
    try:
        result = pipeline.get_similar_items(item_id, top_k)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))