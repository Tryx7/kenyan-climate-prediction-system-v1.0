import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import httpx
import asyncpg

logger = logging.getLogger(__name__)

class DataLoader:
    """Load and prepare data for ML models"""

    def __init__(self):
        self.data_path = os.getenv("DATA_PATH", "./data")
        self.db_url = os.getenv("DATABASE_URL")

    async def load_historical_weather(self, location: str, years: int = 10) -> pd.DataFrame:
        """Load historical weather data from database"""
        if not self.db_url:
            return self._generate_synthetic_data(location, years)

        try:
            conn = await asyncpg.connect(self.db_url)
            rows = await conn.fetch(
                """SELECT * FROM weather_data 
                   WHERE location = $1 AND date > $2
                   ORDER BY date""",
                location, datetime.now() - timedelta(days=years*365)
            )
            await conn.close()

            if rows:
                df = pd.DataFrame([dict(row) for row in rows])
                return df
        except Exception as e:
            logger.warning(f"Database connection failed: {e}")

        return self._generate_synthetic_data(location, years)

    async def load_enso_data(self, years: int = 20) -> pd.DataFrame:
        """Load ENSO historical data"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt",
                    timeout=30.0
                )

            if response.status_code == 200:
                lines = response.text.strip().split('\n')
                data = []
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 3 and parts[0].isdigit():
                        data.append({
                            'year': int(parts[0]),
                            'month': parts[1],
                            'oni': float(parts[2])
                        })
                return pd.DataFrame(data)
        except Exception as e:
            logger.warning(f"NOAA data fetch failed: {e}")

        return self._generate_synthetic_enso(years)

    def _generate_synthetic_data(self, location: str, years: int) -> pd.DataFrame:
        """Generate synthetic weather data for demo"""
        np.random.seed(42)
        n_days = years * 365

        dates = pd.date_range(end=datetime.now(), periods=n_days, freq='D')

        df = pd.DataFrame({
            'date': dates,
            'location': location,
            'temperature_max': np.random.normal(25, 5, n_days),
            'temperature_min': np.random.normal(15, 3, n_days),
            'precipitation': np.random.exponential(3, n_days),
            'humidity': np.random.normal(65, 15, n_days).clip(20, 100),
            'wind_speed': np.random.normal(12, 5, n_days).clip(0, 50),
            'pressure': np.random.normal(1013, 10, n_days)
        })

        return df

    def _generate_synthetic_enso(self, years: int) -> pd.DataFrame:
        """Generate synthetic ENSO data"""
        np.random.seed(42)
        data = []
        current_year = datetime.now().year

        for y in range(current_year - years, current_year + 1):
            for m in range(1, 13):
                oni = np.random.normal(0, 0.8)
                data.append({'year': y, 'month': m, 'oni': oni})

        return pd.DataFrame(data)

    def prepare_features(self, weather_df: pd.DataFrame, enso_df: pd.DataFrame, 
                       location: str) -> tuple:
        """Prepare features for ML models"""
        # Merge weather and ENSO data
        weather_df['year'] = weather_df['date'].dt.year
        weather_df['month'] = weather_df['date'].dt.month

        merged = weather_df.merge(enso_df, on=['year', 'month'], how='left')
        merged['oni'] = merged['oni'].fillna(0)

        # Feature engineering
        merged['temp_range'] = merged['temperature_max'] - merged['temperature_min']
        merged['rainfall_7d'] = merged['precipitation'].rolling(7).sum().fillna(0)
        merged['rainfall_30d'] = merged['precipitation'].rolling(30).sum().fillna(0)
        merged['temp_trend'] = merged['temperature_max'].diff(7).fillna(0)

        # Lag features
        for lag in [1, 7, 30]:
            merged[f'precip_lag_{lag}'] = merged['precipitation'].shift(lag).fillna(0)

        # Season encoding
        merged['season'] = merged['month'].map({
            12: 4, 1: 4, 2: 4,  # DJF
            3: 1, 4: 1, 5: 1,   # MAM
            6: 2, 7: 2, 8: 2,   # JJA
            9: 3, 10: 3, 11: 3  # OND
        })

        # Drop NaN values
        merged = merged.dropna()

        feature_cols = [
            'temperature_max', 'temperature_min', 'humidity', 'wind_speed',
            'pressure', 'oni', 'temp_range', 'rainfall_7d', 'rainfall_30d',
            'temp_trend', 'precip_lag_1', 'precip_lag_7', 'precip_lag_30', 'season'
        ]

        X = merged[feature_cols]
        y_rainfall = merged['precipitation']
        y_drought = (merged['rainfall_30d'] < merged['rainfall_30d'].quantile(0.2)).astype(int)
        y_flood = (merged['rainfall_7d'] > merged['rainfall_7d'].quantile(0.95)).astype(int)
        y_temp = merged['temperature_max']

        return X, y_rainfall, y_drought, y_flood, y_temp
