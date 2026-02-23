# 🎬 End-to-End Deep Learning Movie Recommendation System

## Tech Stack
- **Model**: Neural Collaborative Filtering (NeuralCF) + FAISS
- **Dataset**: MovieLens 20M
- **Tracking**: MLflow
- **API**: FastAPI
- **Frontend**: React + TailwindCSS
- **Deployment**: Docker + Docker Compose

## Project Structure
```
recommendation-system/
├── src/
│   ├── components/       # ML pipeline components
│   ├── pipeline/         # Train & predict pipelines
│   ├── entity/           # Config & artifact dataclasses
│   ├── config/           # Central configuration
│   ├── constants/        # All constants
│   ├── exception/        # Custom exceptions
│   ├── logger/           # Custom logger
│   └── utils/            # Helper utilities
├── api/                  # FastAPI backend
├── frontend/             # React frontend
├── models/               # Saved model artifacts
├── notebooks/            # EDA & experiments
├── tests/                # Unit & integration tests
├── app.py                # Training entry point
└── run_api.py            # API entry point
```

## Quickstart
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Train the model
python app.py

# 3. Start API
python run_api.py

# 4. Start frontend
cd frontend && npm install && npm start

# 5. Monitor training (MLflow UI)
mlflow ui --port 5000
```

## API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/recommend/{user_id} | Get top-K recommendations |
| GET | /api/v1/similar/{item_id} | Get similar movies |
| POST | /api/v1/feedback | Log user feedback |
| GET | /health | Health check |
