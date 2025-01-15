from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from task_manager import TaskManager
from pytz import timezone

hong_kong_tz = timezone("Asia/Hong_Kong")
scheduler = AsyncIOScheduler(timezone=hong_kong_tz)
task_manager = TaskManager()


async def create_daily_task():
    """Create and start task for previous day at 04:00 Hong Kong time"""
    # Get yesterday's date in Hong Kong time
    yesterday = (datetime.now(hong_kong_tz) - timedelta(days=1)).strftime("%Y-%m-%d")

    # Create task for yesterday
    task = await task_manager.create_task(yesterday)

    # Start the task automatically
    if task:
        await task_manager.start_task(task.id)  # type: ignore


async def auto_stop_last_task():
    """Stop the last task if it's running at 09:00 Hong Kong time"""
    tasks = task_manager.get_tasks()
    if tasks:
        last_task = tasks[0]
        await task_manager.stop_task(last_task.id)  # type: ignore


def start_scheduler():
    # Schedule task to run at 04:00 Hong Kong time every day
    scheduler.add_job(
        create_daily_task, trigger="cron", hour=4, minute=0, id="daily_task_creation"
    )
    # Schedule task to run at 09:00 Hong Kong time every day
    scheduler.add_job(
        auto_stop_last_task, trigger="cron", hour=9, minute=0, id="auto_stop_last_task"
    )
    scheduler.start()
