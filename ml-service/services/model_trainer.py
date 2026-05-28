import os
import logging
import pickle
from datetime import datetime
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, precision_score, recall_score

from services.data_loader import DataLoader

logger = logging.getLogger(__name__)

class ModelTrainer:
    """Train and evaluate ML models"""

    def __init__(self):
        self.model_path = os.getenv("MODEL_PATH", "./models")
        self.data_loader = DataLoader()
        self.last_training = None
        self.performance_metrics = {}

        os.makedirs(self.model_path, exist_ok=True)

    def train_all_models(self, force: bool = False) -> dict:
        """Train all climate prediction models"""
        import asyncio

        results = {}

        # Generate synthetic training data for demo
        np.random.seed(42)
        n_samples = 5000

        X = np.random.randn(n_samples, 14)

        # Train rainfall model
        logger.info("Training rainfall model...")
        y_rainfall = np.random.exponential(5, n_samples)
        rf_rainfall = RandomForestRegressor(n_estimators=200, max_depth=20, random_state=42, n_jobs=-1)
        rf_rainfall.fit(X, y_rainfall)

        rainfall_score = rf_rainfall.score(X, y_rainfall)
        joblib.dump(rf_rainfall, os.path.join(self.model_path, "rainfall_model.pkl"))
        results['rainfall'] = {'r2_score': float(rainfall_score), 'status': 'trained'}
        logger.info(f"Rainfall model trained. R2: {rainfall_score:.3f}")

        # Train drought model
        logger.info("Training drought model...")
        y_drought = np.random.binomial(1, 0.25, n_samples)
        rf_drought = RandomForestClassifier(n_estimators=200, max_depth=15, random_state=42, n_jobs=-1)
        rf_drought.fit(X, y_drought)

        drought_score = rf_drought.score(X, y_drought)
        joblib.dump(rf_drought, os.path.join(self.model_path, "drought_model.pkl"))
        results['drought'] = {'accuracy': float(drought_score), 'status': 'trained'}
        logger.info(f"Drought model trained. Accuracy: {drought_score:.3f}")

        # Train flood model
        logger.info("Training flood model...")
        y_flood = np.random.binomial(1, 0.15, n_samples)
        rf_flood = RandomForestClassifier(n_estimators=200, max_depth=15, random_state=42, n_jobs=-1)
        rf_flood.fit(X, y_flood)

        flood_score = rf_flood.score(X, y_flood)
        joblib.dump(rf_flood, os.path.join(self.model_path, "flood_model.pkl"))
        results['flood'] = {'accuracy': float(flood_score), 'status': 'trained'}
        logger.info(f"Flood model trained. Accuracy: {flood_score:.3f}")

        # Train temperature model
        logger.info("Training temperature model...")
        y_temp = np.random.normal(22, 4, n_samples)
        gb_temp = GradientBoostingRegressor(n_estimators=150, max_depth=6, random_state=42)
        gb_temp.fit(X, y_temp)

        temp_score = gb_temp.score(X, y_temp)
        joblib.dump(gb_temp, os.path.join(self.model_path, "temperature_model.pkl"))
        results['temperature'] = {'r2_score': float(temp_score), 'status': 'trained'}
        logger.info(f"Temperature model trained. R2: {temp_score:.3f}")

        self.last_training = datetime.utcnow()
        self.performance_metrics = results

        return results

    def get_last_training_time(self) -> str:
        """Get last training timestamp"""
        if self.last_training:
            return self.last_training.isoformat()
        return "Never"

    def get_performance_metrics(self) -> dict:
        """Get current model performance metrics"""
        return {
            "metrics": self.performance_metrics,
            "last_training": self.get_last_training_time()
        }
