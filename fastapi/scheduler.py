from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from task_manager import TaskManager

scheduler = AsyncIOScheduler()
task_manager = TaskManager()


async def create_daily_task():
    """Create and start task for previous day at 00:30"""
    # Get yesterday's date
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    # Create task for yesterday
    task = await task_manager.create_task(yesterday)

    # Start the task automatically
    if task:
        await task_manager.start_task(task.id)  # type: ignore


def start_scheduler():
    # Schedule task to run at 00:30 every day
    scheduler.add_job(
        create_daily_task, trigger="cron", hour=9, minute=39, id="daily_task_creation"
    )
    scheduler.start()
