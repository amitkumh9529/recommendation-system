# api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from api.routes import recommend, feedback
from src.pipeline.prediction_pipeline import PredictionPipeline
from src.logger import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up API - loading model artifacts...")
    PredictionPipeline.load_artifacts()
    yield
    logger.info("Shutting down API...")

app = FastAPI(title="Deep Learning Recommendation System", version="1.0.0", lifespan=lifespan)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(recommend.router, prefix="/api/v1", tags=["Recommendations"])
app.include_router(feedback.router, prefix="/api/v1", tags=["Feedback"])

@app.get("/health")
def health(): return {"status": "ok"}