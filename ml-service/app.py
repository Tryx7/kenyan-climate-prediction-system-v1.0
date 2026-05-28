from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import os
import logging
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, RandomForestClassifier

from services.data_loader import DataLoader
from services.model_trainer import ModelTrainer
from services.predictor import Predictor

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Kenya Climate ML Service",
    description="Machine learning service for climate predictions",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
data_loader = DataLoader()
model_trainer = ModelTrainer()
predictor = Predictor()

class PredictionRequest(BaseModel):
    location: str
    months_ahead: int = 3
    include_confidence: bool = True

class TrainingRequest(BaseModel):
    model_type: str = "all"
    force_retrain: bool = False

@app.get("/")
async def root():
    return {
        "service": "Kenya Climate ML Service",
        "version": "1.0.0",
        "status": "operational",
        "models_loaded": predictor.get_loaded_models()
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.post("/predict/rainfall")
async def predict_rainfall(request: PredictionRequest):
    """Predict rainfall for a location"""
    try:
        result = predictor.predict_rainfall(request.location, request.months_ahead)
        return result
    except Exception as e:
        logger.error(f"Rainfall prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/drought")
async def predict_drought(request: PredictionRequest):
    """Predict drought probability"""
    try:
        result = predictor.predict_drought(request.location)
        return result
    except Exception as e:
        logger.error(f"Drought prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/flood")
async def predict_flood(request: PredictionRequest):
    """Predict flood probability"""
    try:
        result = predictor.predict_flood(request.location)
        return result
    except Exception as e:
        logger.error(f"Flood prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/temperature")
async def predict_temperature(request: PredictionRequest):
    """Predict temperature trends"""
    try:
        result = predictor.predict_temperature(request.location, request.months_ahead)
        return result
    except Exception as e:
        logger.error(f"Temperature prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/train")
async def train_models(request: TrainingRequest):
    """Trigger model training"""
    try:
        results = model_trainer.train_all_models(force=request.force_retrain)
        return {
            "status": "success",
            "models_trained": results,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Training error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models/status")
async def get_model_status():
    """Get status of all models"""
    return {
        "loaded_models": predictor.get_loaded_models(),
        "last_training": model_trainer.get_last_training_time(),
        "model_versions": predictor.get_model_versions()
    }

@app.get("/models/performance")
async def get_model_performance():
    """Get model performance metrics"""
    return model_trainer.get_performance_metrics()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)
