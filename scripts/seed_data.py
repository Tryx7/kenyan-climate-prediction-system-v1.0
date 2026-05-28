#!/usr/bin/env python3
"""
Seed database with sample data for testing
Usage: python seed_data.py
"""

import asyncio
import asyncpg
import os
from datetime import datetime, timedelta
import random

async def seed_database():
    database_url = os.getenv("DATABASE_URL", "postgresql://climate_user:climate_pass@localhost:5432/kenyan_climate_db")

    print("Connecting to database...")
    conn = await asyncpg.connect(database_url)

    try:
        print("Seeding weather data...")
        locations = [
            ("Nairobi", -1.2921, 36.8219),
            ("Mombasa", -4.0435, 39.6682),
            ("Kisumu", -0.1022, 34.7617),
            ("Nakuru", -0.3031, 36.0663),
            ("Eldoret", 0.5143, 35.2698),
        ]

        for location, lat, lon in locations:
            for i in range(365):
                date = datetime.now() - timedelta(days=i)
                await conn.execute(
                    """INSERT INTO weather_data 
                       (location, latitude, longitude, date, temperature_max, temperature_min, 
                        precipitation, humidity, wind_speed, pressure)
                       VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                       ON CONFLICT (location, date) DO NOTHING""",
                    location, lat, lon, date.date(),
                    random.uniform(20, 32), random.uniform(12, 20),
                    random.exponential(5), random.uniform(40, 90),
                    random.uniform(5, 25), random.uniform(1005, 1025)
                )

        print("Seeding predictions...")
        for location, _, _ in locations:
            for i in range(30):
                date = datetime.now() - timedelta(days=i)
                await conn.execute(
                    """INSERT INTO predictions 
                       (location, prediction_type, prediction_date, predicted_value, 
                        confidence_score, enso_phase, model_version, actual_value, accuracy)
                       VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                       ON CONFLICT DO NOTHING""",
                    location, random.choice(['rainfall', 'drought', 'temperature']),
                    date.date(), random.uniform(0, 200), random.uniform(0.6, 0.9),
                    random.choice(['El Nino', 'La Nina', 'Neutral']), '1.0.0',
                    random.uniform(0, 200), random.uniform(0.7, 0.95)
                )

        print("Seeding search logs...")
        for _ in range(1000):
            location = random.choice([l[0] for l in locations])
            await conn.execute(
                "INSERT INTO search_logs (location, search_query, created_at) VALUES ($1, $2, $3)",
                location, location, datetime.now() - timedelta(days=random.randint(0, 30))
            )

        print("Seeding API logs...")
        endpoints = ['/api/weather/current/', '/api/predictions/rainfall/', '/api/climate/enso/current']
        for _ in range(500):
            await conn.execute(
                """INSERT INTO api_logs (endpoint, method, status_code, response_time_ms, created_at)
                   VALUES ($1, $2, $3, $4, $5)""",
                random.choice(endpoints) + random.choice([l[0] for l in locations]),
                'GET', random.choice([200, 200, 200, 404, 500]),
                random.uniform(50, 500),
                datetime.now() - timedelta(days=random.randint(0, 7))
            )

        print("Database seeded successfully!")

    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(seed_database())
