from fastapi import APIRouter
from pydantic import BaseModel
from src.logger import logger

router = APIRouter()


class FeedbackRequest(BaseModel):
    user_id: int
    item_id: int
    clicked: bool
    rating:  float = None


@router.post("/feedback")
def log_feedback(feedback: FeedbackRequest):
    logger.info(f"Feedback received: {feedback}")
    # TODO: persist to PostgreSQL / Redis for retraining
    return {"status": "ok", "message": "Feedback logged"}
