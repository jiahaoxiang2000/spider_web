from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from task_manager import TaskManager
from pytz import timezone

hong_kong_tz = timezone("Asia/Hong_Kong")
scheduler = AsyncIOScheduler(timezone=hong_kong_tz)
task_manager = TaskManager()


async def create_daily_task():
    """Create and start task for previous day at 00:30 Hong Kong time"""
    # Get yesterday's date in Hong Kong time
    yesterday = (datetime.now(hong_kong_tz) - timedelta(days=1)).strftime("%Y-%m-%d")

    # Create task for yesterday
    task = await task_manager.create_task(yesterday)

    # Start the task automatically
    if task:
        await task_manager.start_task(task.id)  # type: ignore


def start_scheduler():
    # Schedule task to run at 00:30 Hong Kong time every day
    scheduler.add_job(
        create_daily_task, trigger="cron", hour=4, minute=0, id="daily_task_creation"
    )
    scheduler.start()
