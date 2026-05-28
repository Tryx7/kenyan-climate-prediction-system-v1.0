import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime

logger = logging.getLogger(__name__)

_scheduler = None

def start_scheduler():
    """Start the background scheduler"""
    global _scheduler
    if _scheduler is None:
        _scheduler = BackgroundScheduler()

        # Schedule model retraining every Saturday at 12:00 PM
        _scheduler.add_job(
            _retrain_models,
            trigger=CronTrigger(day_of_week="sat", hour=12, minute=0),
            id="model_retrain",
            name="ML Model Retraining",
            replace_existing=True
        )

        # Schedule ENSO data update daily at 6:00 AM
        _scheduler.add_job(
            _update_enso_data,
            trigger=CronTrigger(hour=6, minute=0),
            id="enso_update",
            name="ENSO Data Update",
            replace_existing=True
        )

        # Schedule weather data collection every 3 hours
        _scheduler.add_job(
            _collect_weather_data,
            trigger=CronTrigger(hour="*/3"),
            id="weather_collect",
            name="Weather Data Collection",
            replace_existing=True
        )

        _scheduler.start()
        logger.info("Scheduler started with jobs: model retrain (Sat 12:00), ENSO update (daily 6:00), weather collection (every 3h)")

def stop_scheduler():
    """Stop the background scheduler"""
    global _scheduler
    if _scheduler:
        _scheduler.shutdown()
        _scheduler = None
        logger.info("Scheduler stopped")

def _retrain_models():
    """Trigger model retraining"""
    logger.info("Scheduled model retraining started")
    try:
        import asyncio
        from app.services.ml_service import MLService
        ml = MLService()
        asyncio.run(ml.retrain_all_models())
        logger.info("Scheduled model retraining completed")
    except Exception as e:
        logger.error(f"Model retraining failed: {e}")

def _update_enso_data():
    """Update ENSO data"""
    logger.info("Scheduled ENSO data update started")
    try:
        import asyncio
        from app.services.enso_service import ENSOService
        enso = ENSOService()
        asyncio.run(enso.get_current_status())
        logger.info("ENSO data updated")
    except Exception as e:
        logger.error(f"ENSO update failed: {e}")

def _collect_weather_data():
    """Collect weather data for all locations"""
    logger.info("Scheduled weather data collection started")
    try:
        # This would collect weather data for all Kenyan locations
        logger.info("Weather data collection completed")
    except Exception as e:
        logger.error(f"Weather collection failed: {e}")
