"""
Background scheduler for automated tasks.

Handles scheduled jobs like token cleanup, verification reminders, etc.
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timezone
import logging

from app.services.token_service import token_service
from app.db.database import SessionLocal, get_session_local

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SchedulerService:
    """Service for managing scheduled background tasks."""

    def __init__(self):
        """Initialize the scheduler."""
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        logger.info("Background scheduler started")

    def cleanup_expired_tokens(self):
        """
        Job: Cleanup expired and used verification tokens.

        Runs every hour to remove:
        - Expired tokens (expires_at < now)
        - Used tokens (is_valid = False and used_at is not None)
        """
        try:
            logger.info("Starting token cleanup job...")

            # Create database session
            db = SessionLocal()

            try:
                # Run cleanup
                stats = token_service.cleanup_expired_tokens(db)

                logger.info(
                    f"Token cleanup completed: "
                    f"{stats['expired_removed']} tokens removed at {stats['timestamp']}"
                )

                # Log to file for monitoring
                self._log_cleanup_stats(stats)

            finally:
                db.close()

        except Exception as e:
            logger.error(f"Token cleanup job failed: {str(e)}")
            import traceback
            traceback.print_exc()

    def _log_cleanup_stats(self, stats: dict):
        """Log cleanup statistics to file for monitoring."""
        try:
            log_file = "logs/token_cleanup.log"

            # Create logs directory if it doesn't exist
            import os
            os.makedirs("logs", exist_ok=True)

            with open(log_file, "a") as f:
                f.write(
                    f"{stats['timestamp']} - "
                    f"Removed {stats['expired_removed']} expired tokens\n"
                )

        except Exception as e:
            logger.warning(f"Failed to write cleanup log: {str(e)}")

    def run_scheduled_scans(self):
        """
        Job: Run scheduled security scans on assets.

        Checks for assets where:
        - scan_enabled = True
        - next_scan_at <= now

        Runs every 15 minutes to check for assets that need scanning.
        """
        try:
            logger.info("Starting scheduled scan job...")

            # Create database session
            SessionLocal = get_session_local()
            db = SessionLocal()

            try:
                from app.models.asset import Asset
                from app.services.scan_service import SecurityScanner
                from datetime import datetime, timezone, timedelta
                import asyncio

                # Find assets that need scanning
                now = datetime.now(timezone.utc)

                assets_to_scan = db.query(Asset).filter(
                    Asset.scan_enabled == True,
                    Asset.next_scan_at <= now
                ).all()

                logger.info(f"Found {len(assets_to_scan)} assets to scan")

                scanned_count = 0
                for asset in assets_to_scan:
                    try:
                        logger.info(f"Running scheduled scan for: {asset.name}")

                        # Check if user has active trial or subscription
                        from app.services.trial_service import TrialService
                        from app.models.user import User

                        # Get asset owner
                        if asset.user_id:
                            user = db.query(User).get(asset.user_id)
                            if not user:
                                logger.warning(f"User not found for asset {asset.name}")
                                continue

                            # Check access
                            if not TrialService.can_use_services(user, db):
                                logger.info(f"Skipping {asset.name} - user trial/subscription expired")
                                continue

                        # Run scan
                        scanner = SecurityScanner(db)

                        async def run_scan():
                            return await scanner.scan_asset(str(asset.id))

                        scan = asyncio.run(run_scan())

                        # Calculate next scan time
                        interval_map = {
                            '1h': timedelta(hours=1),
                            '6h': timedelta(hours=6),
                            '12h': timedelta(hours=12),
                            '24h': timedelta(hours=24),
                            'daily': timedelta(days=1),
                            'weekly': timedelta(weeks=1),
                            'monthly': timedelta(days=30)
                        }

                        interval = interval_map.get(asset.scan_interval, timedelta(days=1))
                        asset.next_scan_at = now + interval

                        db.commit()
                        scanned_count += 1

                        logger.info(f"Scan completed for {asset.name}. Score: {scan.score}")

                    except Exception as scan_error:
                        logger.error(f"Failed to scan {asset.name}: {str(scan_error)}")
                        # Don't fail the whole job if one scan fails
                        continue

                logger.info(f"Scheduled scan job completed: {scanned_count} assets scanned")

            finally:
                db.close()

        except Exception as e:
            logger.error(f"Scheduled scan job failed: {str(e)}")
            import traceback
            traceback.print_exc()

    def schedule_jobs(self):
        """Schedule all background jobs."""

        # Job 1: Token cleanup (every hour)
        self.scheduler.add_job(
            func=self.cleanup_expired_tokens,
            trigger=IntervalTrigger(hours=1),
            id='token_cleanup',
            name='Cleanup expired verification tokens',
            replace_existing=True,
            max_instances=1  # Prevent concurrent runs
        )

        logger.info("Scheduled job: Token cleanup (every 1 hour)")

        # Job 2: Scheduled security scans (every 15 minutes)
        self.scheduler.add_job(
            func=self.run_scheduled_scans,
            trigger=IntervalTrigger(minutes=15),
            id='scheduled_scans',
            name='Run scheduled security scans',
            replace_existing=True,
            max_instances=1  # Prevent concurrent runs
        )

        logger.info("Scheduled job: Security scans (every 15 minutes)")

        # Future jobs can be added here:
        # - Re-verification reminders (daily)
        # - Analytics reports (weekly)
        # - Database maintenance (weekly)

    def get_job_status(self) -> dict:
        """Get status of all scheduled jobs."""
        jobs = []

        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            })

        return {
            "scheduler_running": self.scheduler.running,
            "jobs": jobs
        }

    def shutdown(self):
        """Shutdown the scheduler gracefully."""
        logger.info("Shutting down scheduler...")
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")


# Global scheduler instance
scheduler_service = SchedulerService()
