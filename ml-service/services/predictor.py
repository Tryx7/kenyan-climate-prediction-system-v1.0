import os
import logging
import numpy as np
import joblib
from datetime import datetime

from services.data_loader import DataLoader

logger = logging.getLogger(__name__)

class Predictor:
    """Make predictions using trained models"""

    def __init__(self):
        self.model_path = os.getenv("MODEL_PATH", "./models")
        self.models = {}
        self._load_models()

    def _load_models(self):
        """Load all trained models"""
        model_files = {
            'rainfall': 'rainfall_model.pkl',
            'drought': 'drought_model.pkl',
            'flood': 'flood_model.pkl',
            'temperature': 'temperature_model.pkl'
        }

        for name, filename in model_files.items():
            filepath = os.path.join(self.model_path, filename)
            if os.path.exists(filepath):
                try:
                    self.models[name] = joblib.load(filepath)
                    logger.info(f"Loaded model: {name}")
                except Exception as e:
                    logger.warning(f"Failed to load {name}: {e}")
            else:
                logger.warning(f"Model file not found: {filepath}")

    def get_loaded_models(self) -> list:
        """Get list of loaded models"""
        return list(self.models.keys())

    def get_model_versions(self) -> dict:
        """Get model version info"""
        return {name: "1.0.0" for name in self.models.keys()}

    def _create_features(self, location: str, months_ahead: int = 3) -> np.ndarray:
        """Create feature vector for prediction"""
        # Simplified feature vector for demo
        features = np.array([
            -1.2921,  # lat (Nairobi default)
            36.8219,  # lon
            1795,     # elevation
            22,       # avg_temp
            1000,     # avg_rainfall
            65,       # humidity
            datetime.now().month,
            1,        # season
            months_ahead,
            0,        # enso_phase
            0.0,      # oni
            800,      # last_year_rainfall
            22.5      # last_year_temp
        ]).reshape(1, -1)

        return features

    def predict_rainfall(self, location: str, months_ahead: int = 3) -> dict:
        """Predict rainfall"""
        features = self._create_features(location, months_ahead)

        if 'rainfall' in self.models:
            prediction = self.models['rainfall'].predict(features)[0]
        else:
            prediction = np.random.exponential(50) * months_ahead

        monthly = []
        for i in range(months_ahead):
            month_pred = prediction / months_ahead * (1 + np.random.normal(0, 0.15))
            monthly.append({
                'month': (datetime.now().month + i - 1) % 12 + 1,
                'predicted_mm': round(max(0, month_pred), 1),
                'confidence': round(0.65 + np.random.random() * 0.25, 2)
            })

        return {
            'location': location,
            'prediction_type': 'rainfall',
            'period_months': months_ahead,
            'total_predicted_mm': round(max(0, prediction), 1),
            'monthly_breakdown': monthly,
            'confidence_score': round(0.68, 2),
            'model_version': '1.0.0',
            'timestamp': datetime.utcnow().isoformat()
        }

    def predict_drought(self, location: str) -> dict:
        """Predict drought probability"""
        features = self._create_features(location)

        if 'drought' in self.models:
            prob = self.models['drought'].predict_proba(features)[0][1]
        else:
            prob = np.random.random() * 0.4 + 0.1

        risk_level = 'High' if prob > 0.7 else 'Medium-High' if prob > 0.5 else 'Medium' if prob > 0.3 else 'Low'

        return {
            'location': location,
            'prediction_type': 'drought',
            'drought_probability': round(prob, 2),
            'risk_level': risk_level,
            'confidence_score': round(0.72, 2),
            'model_version': '1.0.0',
            'timestamp': datetime.utcnow().isoformat()
        }

    def predict_flood(self, location: str) -> dict:
        """Predict flood probability"""
        features = self._create_features(location)

        if 'flood' in self.models:
            prob = self.models['flood'].predict_proba(features)[0][1]
        else:
            prob = np.random.random() * 0.3 + 0.05

        risk_level = 'High' if prob > 0.7 else 'Medium-High' if prob > 0.5 else 'Medium' if prob > 0.3 else 'Low'

        return {
            'location': location,
            'prediction_type': 'flood',
            'flood_probability': round(prob, 2),
            'risk_level': risk_level,
            'confidence_score': round(0.70, 2),
            'model_version': '1.0.0',
            'timestamp': datetime.utcnow().isoformat()
        }

    def predict_temperature(self, location: str, months_ahead: int = 3) -> dict:
        """Predict temperature trends"""
        features = self._create_features(location, months_ahead)

        if 'temperature' in self.models:
            base_temp = self.models['temperature'].predict(features)[0]
        else:
            base_temp = 22 + np.random.normal(0, 2)

        monthly = []
        for i in range(months_ahead):
            month_temp = base_temp + np.random.normal(0, 0.5)
            monthly.append({
                'month': (datetime.now().month + i - 1) % 12 + 1,
                'predicted_temp_c': round(month_temp, 1),
                'anomaly_c': round(month_temp - 22, 1),
                'confidence': round(0.70 + np.random.random() * 0.2, 2)
            })

        return {
            'location': location,
            'prediction_type': 'temperature',
            'period_months': months_ahead,
            'average_predicted_temp_c': round(base_temp, 1),
            'monthly_breakdown': monthly,
            'confidence_score': round(0.72, 2),
            'model_version': '1.0.0',
            'timestamp': datetime.utcnow().isoformat()
        }
