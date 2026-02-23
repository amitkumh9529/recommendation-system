from pydantic import BaseModel
from typing import List, Optional


class RecommendationResponse(BaseModel):
    user_id:               int
    recommended_item_ids:  List[int]
    scores:                List[float]


class SimilarItemsResponse(BaseModel):
    item_id:       int
    similar_items: List[int]
    scores:        List[float]


class FeedbackRequest(BaseModel):
    user_id: int
    item_id: int
    clicked: bool
    rating:  Optional[float] = None
