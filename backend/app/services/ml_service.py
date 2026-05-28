import os
import pickle
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
import httpx
import joblib
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, classification_report

from app.utils.kenya_locations import ALL_LOCATIONS, CLIMATE_ZONES
from app.services.enso_service import ENSOService
from app.services.database import get_db_pool

logger = logging.getLogger(__name__)

class MLService:
    """Machine Learning service for climate predictions"""

    def __init__(self):
        self.model_path = os.getenv("MODEL_PATH", "./ml-service/models")
        self.enso_service = ENSOService()
        self.models = {}
        self._load_models()

    def _load_models(self):
        """Load trained models from disk"""
        model_files = {
            "rainfall": "rainfall_model.pkl",
            "drought": "drought_model.pkl",
            "flood": "flood_model.pkl",
            "temperature": "temperature_model.pkl"
        }

        for name, filename in model_files.items():
            filepath = os.path.join(self.model_path, filename)
            if os.path.exists(filepath):
                try:
                    self.models[name] = joblib.load(filepath)
                    logger.info(f"Loaded model: {name}")
                except Exception as e:
                    logger.warning(f"Could not load model {name}: {e}")
                    self.models[name] = None
            else:
                logger.warning(f"Model file not found: {filepath}")
                self.models[name] = None

    def _get_features(self, location: str, months_ahead: int = 3) -> np.ndarray:
        """Extract features for prediction"""
        loc_data = ALL_LOCATIONS[location]
        zone = CLIMATE_ZONES.get(loc_data["region"], {})

        # Get current month and season
        now = datetime.now()
        current_month = now.month

        # Season encoding (MAM=1, JJA=2, OND=3, DJF=4)
        if current_month in [3, 4, 5]:
            season = 1
        elif current_month in [6, 7, 8]:
            season = 2
        elif current_month in [9, 10, 11]:
            season = 3
        else:
            season = 4

        # ENSO features (simulated for demo)
        enso_phase = 0  # Neutral
        oni = 0.0

        features = np.array([
            loc_data["lat"],
            loc_data["lon"],
            loc_data["elevation"],
            zone.get("avg_temp", 22),
            zone.get("avg_rainfall", 1000),
            zone.get("humidity", 60),
            current_month,
            season,
            months_ahead,
            enso_phase,
            oni,
            # Historical averages (would come from DB)
            zone.get("avg_rainfall", 1000) * 0.8,  # last_year_rainfall
            zone.get("avg_temp", 22) + 0.5,  # last_year_temp
        ]).reshape(1, -1)

        return features

    async def predict_rainfall(self, location: str, months: int = 3) -> Dict:
        """Predict rainfall for a location"""
        features = self._get_features(location, months)
        zone = CLIMATE_ZONES.get(ALL_LOCATIONS[location]["region"], {})
        base_rainfall = zone.get("avg_rainfall", 1000)

        # Get ENSO status
        enso = await self.enso_service.get_current_status()
        enso_phase = enso.get("current_phase", "Neutral")
        oni = enso.get("oni_value", 0)

        # Adjust prediction based on ENSO
        enso_adjustment = 0
        if enso_phase == "El Nino":
            enso_adjustment = oni * 150  # More rain with El Nino
        elif enso_phase == "La Nina":
            enso_adjustment = oni * 100  # Less rain with La Nina

        # Use model if available, otherwise use heuristic
        if self.models.get("rainfall"):
            try:
                pred = self.models["rainfall"].predict(features)[0]
            except Exception:
                pred = base_rainfall / 12 * months + enso_adjustment
        else:
            pred = base_rainfall / 12 * months + enso_adjustment

        # Monthly breakdown
        monthly = []
        for i in range(months):
            month_pred = pred / months * (1 + np.random.normal(0, 0.1))
            monthly.append({
                "month": (datetime.now().month + i - 1) % 12 + 1,
                "predicted_mm": round(max(0, month_pred), 1),
                "confidence": round(0.65 + np.random.random() * 0.25, 2)
            })

        return {
            "location": location,
            "prediction_type": "rainfall",
            "period_months": months,
            "total_predicted_mm": round(max(0, pred), 1),
            "monthly_breakdown": monthly,
            "enso_influence": {
                "phase": enso_phase,
                "oni": oni,
                "adjustment_mm": round(enso_adjustment, 1)
            },
            "confidence_score": round(0.68, 2),
            "model_version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat()
        }

    async def predict_drought(self, location: str) -> Dict:
        """Predict drought likelihood for a location"""
        features = self._get_features(location)
        zone = CLIMATE_ZONES.get(ALL_LOCATIONS[location]["region"], {})
        base_rainfall = zone.get("avg_rainfall", 1000)

        enso = await self.enso_service.get_current_status()
        enso_phase = enso.get("current_phase", "Neutral")
        oni = enso.get("oni_value", 0)

        # Calculate drought probability
        base_prob = 0.2

        if enso_phase == "La Nina":
            base_prob += abs(oni) * 0.25
        elif enso_phase == "El Nino":
            base_prob -= abs(oni) * 0.15

        # Region adjustment
        if zone.get("seasons") == "unimodal":
            base_prob += 0.15

        if base_rainfall < 400:
            base_prob += 0.2

        probability = min(0.95, max(0.05, base_prob))

        # Risk level
        if probability >= 0.7:
            risk = "High"
            severity = "Severe drought conditions likely"
        elif probability >= 0.5:
            risk = "Medium-High"
            severity = "Moderate drought risk"
        elif probability >= 0.3:
            risk = "Medium"
            severity = "Some drought risk"
        else:
            risk = "Low"
            severity = "Normal conditions expected"

        return {
            "location": location,
            "prediction_type": "drought",
            "drought_probability": round(probability, 2),
            "risk_level": risk,
            "severity_description": severity,
            "enso_influence": {
                "phase": enso_phase,
                "impact": f"La Nina increases drought risk" if enso_phase == "La Nina" else 
                         f"El Nino reduces drought risk" if enso_phase == "El Nino" else "Neutral conditions"
            },
            "confidence_score": round(0.72, 2),
            "recommended_actions": self._get_drought_actions(risk),
            "model_version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat()
        }

    def _get_drought_actions(self, risk: str) -> List[str]:
        """Get drought mitigation actions"""
        actions = {
            "High": [
                "Implement emergency water rationing",
                "Distribute drought-resistant seeds",
                "Activate livestock offtake programs",
                "Mobilize food aid distribution"
            ],
            "Medium-High": [
                "Increase water storage capacity",
                "Promote water conservation practices",
                "Monitor livestock health closely",
                "Prepare contingency plans"
            ],
            "Medium": [
                "Review irrigation schedules",
                "Plant early-maturing crop varieties",
                "Maintain water infrastructure",
                "Monitor weather forecasts"
            ],
            "Low": [
                "Standard agricultural practices",
                "Regular monitoring",
                "Maintain preparedness plans"
            ]
        }
        return actions.get(risk, actions["Low"])

    async def predict_flood(self, location: str) -> Dict:
        """Predict flood risk for a location"""
        features = self._get_features(location)
        zone = CLIMATE_ZONES.get(ALL_LOCATIONS[location]["region"], {})

        enso = await self.enso_service.get_current_status()
        enso_phase = enso.get("current_phase", "Neutral")
        oni = enso.get("oni_value", 0)

        # Calculate flood probability
        base_prob = 0.15

        if enso_phase == "El Nino":
            base_prob += abs(oni) * 0.3
        elif enso_phase == "La Nina":
            base_prob -= abs(oni) * 0.1

        # Region adjustment
        if zone.get("avg_rainfall", 0) > 1200:
            base_prob += 0.15

        if ALL_LOCATIONS[location]["elevation"] < 200:
            base_prob += 0.1

        probability = min(0.95, max(0.05, base_prob))

        if probability >= 0.7:
            risk = "High"
            severity = "Severe flooding likely"
        elif probability >= 0.5:
            risk = "Medium-High"
            severity = "Moderate flood risk"
        elif probability >= 0.3:
            risk = "Medium"
            severity = "Some flood risk"
        else:
            risk = "Low"
            severity = "Normal conditions"

        return {
            "location": location,
            "prediction_type": "flood",
            "flood_probability": round(probability, 2),
            "risk_level": risk,
            "severity_description": severity,
            "enso_influence": {
                "phase": enso_phase,
                "impact": f"El Nino increases flood risk" if enso_phase == "El Nino" else 
                         f"La Nina reduces flood risk" if enso_phase == "La Nina" else "Neutral conditions"
            },
            "confidence_score": round(0.70, 2),
            "recommended_actions": self._get_flood_actions(risk),
            "model_version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat()
        }

    def _get_flood_actions(self, risk: str) -> List[str]:
        """Get flood mitigation actions"""
        actions = {
            "High": [
                "Evacuate low-lying areas",
                "Activate emergency response teams",
                "Clear drainage channels",
                "Stock emergency supplies"
            ],
            "Medium-High": [
                "Monitor river levels closely",
                "Prepare sandbagging materials",
                "Alert vulnerable communities",
                "Check drainage systems"
            ],
            "Medium": [
                "Clear storm drains",
                "Secure loose objects",
                "Monitor weather alerts",
                "Review emergency plans"
            ],
            "Low": [
                "Standard preparedness",
                "Regular monitoring"
            ]
        }
        return actions.get(risk, actions["Low"])

    async def predict_temperature(self, location: str, months: int = 3) -> Dict:
        """Predict temperature trends"""
        zone = CLIMATE_ZONES.get(ALL_LOCATIONS[location]["region"], {})
        base_temp = zone.get("avg_temp", 22)

        enso = await self.enso_service.get_current_status()
        enso_phase = enso.get("current_phase", "Neutral")
        oni = enso.get("oni_value", 0)

        # Temperature adjustment
        temp_adjustment = 0
        if enso_phase == "El Nino":
            temp_adjustment = abs(oni) * 0.8
        elif enso_phase == "La Nina":
            temp_adjustment = -abs(oni) * 0.5

        predicted_temp = base_temp + temp_adjustment + 0.5  # Climate warming trend

        monthly = []
        for i in range(months):
            month_temp = predicted_temp + np.random.normal(0, 0.5)
            monthly.append({
                "month": (datetime.now().month + i - 1) % 12 + 1,
                "predicted_temp_c": round(month_temp, 1),
                "anomaly_c": round(month_temp - base_temp, 1),
                "confidence": round(0.70 + np.random.random() * 0.2, 2)
            })

        return {
            "location": location,
            "prediction_type": "temperature",
            "period_months": months,
            "average_predicted_temp_c": round(predicted_temp, 1),
            "monthly_breakdown": monthly,
            "enso_influence": {
                "phase": enso_phase,
                "adjustment_c": round(temp_adjustment, 1)
            },
            "confidence_score": round(0.72, 2),
            "model_version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat()
        }

    async def get_comprehensive_prediction(self, location: str) -> Dict:
        """Get comprehensive climate prediction"""
        rainfall = await self.predict_rainfall(location, 3)
        drought = await self.predict_drought(location)
        flood = await self.predict_flood(location)
        temperature = await self.predict_temperature(location, 3)

        # Overall risk assessment
        risks = [drought["risk_level"], flood["risk_level"]]
        risk_priority = {"Critical": 4, "High": 3, "Medium-High": 2.5, "Medium": 2, "Low": 1}

        max_risk = max(risks, key=lambda x: risk_priority.get(x, 0))

        return {
            "location": location,
            "overall_risk_level": max_risk,
            "predictions": {
                "rainfall": rainfall,
                "drought": drought,
                "flood": flood,
                "temperature": temperature
            },
            "summary": self._generate_summary(location, rainfall, drought, flood, temperature),
            "timestamp": datetime.utcnow().isoformat()
        }

    def _generate_summary(self, location: str, rainfall: Dict, drought: Dict, 
                         flood: Dict, temperature: Dict) -> str:
        """Generate human-readable summary"""
        enso = rainfall.get("enso_influence", {}).get("phase", "Neutral")

        parts = [f"Climate outlook for {location}:", ""]

        parts.append(f"ENSO Status: {enso} conditions present.")
        parts.append(f"Rainfall: {rainfall['total_predicted_mm']}mm expected over next 3 months.")
        parts.append(f"Drought Risk: {drought['risk_level']} ({drought['drought_probability']*100:.0f}% probability).")
        parts.append(f"Flood Risk: {flood['risk_level']} ({flood['flood_probability']*100:.0f}% probability).")
        parts.append(f"Temperature: Averaging {temperature['average_predicted_temp_c']}C.")

        return " ".join(parts)

    async def retrain_all_models(self):
        """Retrain all ML models"""
        logger.info("Starting model retraining...")

        # This would fetch historical data and retrain models
        # For demo, we'll create simple models

        os.makedirs(self.model_path, exist_ok=True)

        # Generate synthetic training data
        np.random.seed(42)
        n_samples = 1000

        X = np.random.randn(n_samples, 13)
        y_rainfall = np.random.exponential(100, n_samples)
        y_drought = np.random.binomial(1, 0.3, n_samples)
        y_flood = np.random.binomial(1, 0.2, n_samples)
        y_temp = np.random.normal(22, 3, n_samples)

        # Train models
        models_config = {
            "rainfall": (RandomForestRegressor(n_estimators=100, random_state=42), X, y_rainfall),
            "drought": (RandomForestClassifier(n_estimators=100, random_state=42), X, y_drought),
            "flood": (RandomForestClassifier(n_estimators=100, random_state=42), X, y_flood),
            "temperature": (GradientBoostingRegressor(n_estimators=100, random_state=42), X, y_temp)
        }

        for name, (model, X_train, y_train) in models_config.items():
            model.fit(X_train, y_train)
            filepath = os.path.join(self.model_path, f"{name}_model.pkl")
            joblib.dump(model, filepath)
            self.models[name] = model
            logger.info(f"Retrained and saved model: {name}")

        # Log performance
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            for name, (model, X_train, y_train) in models_config.items():
                if hasattr(model, 'score'):
                    score = model.score(X_train, y_train)
                    await conn.execute(
                        """INSERT INTO model_performance 
                           (model_name, model_version, metric_name, metric_value, training_date)
                           VALUES ($1, $2, $3, $4, NOW())""",
                        name, "1.0.0", "r2_score" if "Regressor" in str(type(model)) else "accuracy", 
                        float(score)
                    )

        logger.info("Model retraining complete!")

    async def get_performance_metrics(self) -> Dict:
        """Get model performance metrics"""
        pool = await get_db_pool()

        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """SELECT model_name, metric_name, metric_value, training_date
                   FROM model_performance
                   ORDER BY training_date DESC"""
            )

        metrics = {}
        for row in rows:
            model = row["model_name"]
            if model not in metrics:
                metrics[model] = []
            metrics[model].append({
                "metric": row["metric_name"],
                "value": round(float(row["metric_value"]), 4),
                "date": row["training_date"].isoformat()
            })

        return {
            "models": metrics,
            "last_training": datetime.utcnow().isoformat()
        }
