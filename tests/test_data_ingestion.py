import pytest
from src.components.data_ingestion import DataIngestion
from src.entity.config_entity import DataIngestionConfig


def test_data_ingestion_config():
    config = DataIngestionConfig()
    assert config.dataset_url != ""
    assert "ml-20m" in config.dataset_url or "movielens" in config.dataset_url
