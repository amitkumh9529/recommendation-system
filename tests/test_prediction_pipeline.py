import pytest


def test_prediction_pipeline_import():
    from src.pipeline.prediction_pipeline import PredictionPipeline
    pipeline = PredictionPipeline()
    assert pipeline is not None
