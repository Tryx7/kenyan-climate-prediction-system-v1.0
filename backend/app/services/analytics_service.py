from datetime import datetime, timedelta
from typing import Dict, List
import logging

from app.services.database import get_db_pool

logger = logging.getLogger(__name__)

class AnalyticsService:
    """Service for analytics and dashboard data"""

    async def get_dashboard_summary(self) -> Dict:
        """Get main dashboard summary"""
        pool = await get_db_pool()

        async with pool.acquire() as conn:
            # Total predictions made
            pred_count = await conn.fetchval("SELECT COUNT(*) FROM predictions")

            # Active alerts
            alert_count = await conn.fetchval(
                "SELECT COUNT(*) FROM climate_alerts WHERE is_active = true"
            )

            # Popular locations
            popular = await conn.fetch(
                """SELECT location, COUNT(*) as searches 
                   FROM search_logs 
                   WHERE created_at > NOW() - INTERVAL '30 days'
                   GROUP BY location 
                   ORDER BY searches DESC 
                   LIMIT 5"""
            )

            # Model performance
            model_perf = await conn.fetch(
                """SELECT model_name, AVG(metric_value) as avg_score
                   FROM model_performance
                   WHERE training_date > NOW() - INTERVAL '30 days'
                   GROUP BY model_name"""
            )

        return {
            "total_predictions": pred_count or 0,
            "active_alerts": alert_count or 0,
            "popular_locations": [dict(row) for row in popular] if popular else [],
            "model_performance": {row["model_name"]: round(float(row["avg_score"]), 3) 
                                 for row in model_perf} if model_perf else {},
            "system_status": "operational",
            "last_updated": datetime.utcnow().isoformat()
        }

    async def get_prediction_trends(self, days: int = 30) -> Dict:
        """Get prediction accuracy trends"""
        pool = await get_db_pool()
        since = datetime.utcnow() - timedelta(days=days)

        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """SELECT DATE(created_at) as date, 
                          prediction_type,
                          AVG(accuracy) as avg_accuracy,
                          COUNT(*) as count
                   FROM predictions
                   WHERE created_at > $1 AND accuracy IS NOT NULL
                   GROUP BY DATE(created_at), prediction_type
                   ORDER BY date""",
                since
            )

        trends = {}
        for row in rows:
            date_str = row["date"].isoformat()
            if date_str not in trends:
                trends[date_str] = {}
            trends[date_str][row["prediction_type"]] = {
                "accuracy": round(float(row["avg_accuracy"]), 3),
                "count": row["count"]
            }

        return {
            "period_days": days,
            "trends": trends,
            "summary": self._calculate_trend_summary(trends)
        }

    def _calculate_trend_summary(self, trends: Dict) -> Dict:
        """Calculate trend summary"""
        if not trends:
            return {"message": "No data available"}

        all_accuracies = []
        for date_data in trends.values():
            for pred_type, data in date_data.items():
                all_accuracies.append(data["accuracy"])

        if not all_accuracies:
            return {"message": "No accuracy data available"}

        import numpy as np
        return {
            "average_accuracy": round(np.mean(all_accuracies), 3),
            "trend_direction": "improving" if all_accuracies[-1] > all_accuracies[0] else "stable",
            "total_predictions": sum(
                sum(d["count"] for d in date_data.values())
                for date_data in trends.values()
            )
        }

    async def get_popular_locations(self, limit: int = 10) -> Dict:
        """Get most searched locations"""
        pool = await get_db_pool()

        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """SELECT location, COUNT(*) as searches,
                          COUNT(DISTINCT DATE(created_at)) as active_days
                   FROM search_logs
                   WHERE created_at > NOW() - INTERVAL '30 days'
                   GROUP BY location
                   ORDER BY searches DESC
                   LIMIT $1""",
                limit
            )

        return {
            "period": "last_30_days",
            "locations": [
                {
                    "name": row["location"],
                    "searches": row["searches"],
                    "active_days": row["active_days"]
                }
                for row in rows
            ]
        }

    async def get_enso_trends(self, years: int = 20) -> Dict:
        """Get ENSO trend analysis"""
        from app.services.enso_service import ENSOService
        enso = ENSOService()
        history = await enso.get_historical_data(years=years)

        data = history.get("data", [])
        if not data:
            return {"message": "No ENSO data available"}

        # Calculate trends
        import numpy as np
        oni_values = [d["oni"] for d in data]

        return {
            "period_years": years,
            "average_oni": round(np.mean(oni_values), 2),
            "max_oni": round(max(oni_values), 2),
            "min_oni": round(min(oni_values), 2),
            "std_oni": round(np.std(oni_values), 2),
            "phase_distribution": history.get("phase_distribution", {}),
            "trend": "warming" if np.mean(oni_values[-36:]) > np.mean(oni_values[:36]) else "stable",
            "strongest_el_nino": max(data, key=lambda x: x["oni"]),
            "strongest_la_nina": min(data, key=lambda x: x["oni"])
        }
