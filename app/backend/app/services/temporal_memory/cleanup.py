"""
Scheduler for cleaning up old temporal storage assets
"""
import asyncio
from core.logger import logger
from services.temporal_memory.storage import clean_old_assets


def scheduled_cleanup():
    """Run the cleanup task periodically"""
    logger.info("Running scheduled cleanup of temporal storage assets")
    clean_old_assets()
    logger.info("Temporal storage cleanup completed")