import asyncio
from database import TaskDB, SessionLocal, AccountDB
from datetime import datetime
import os
from utils.logger_config import get_logger
import csv
import aiohttp
import time
from typing import Optional

logger = get_logger(__name__)


# Make spider_sleep_time global and mutable
class SpiderConfig:
    sleep_time = 180


spider_config = SpiderConfig()


async def spider_task(task_id: int):
    """
    Spider task that runs in the background
    Args:
        task_id: The ID of the task to run
    """
    session = SessionLocal()
    try:
        task = session.query(TaskDB).get(task_id)
        if not task:
            logger.error(f"Task {task_id} not found")
            return

        base_url = "https://web.antgst.com/antgst/sms/otpPremium/channel/sendRecordList"

        while not task.stop_flag and task.current_page < task.total_page:
            # Get an available account
            account = (
                session.query(AccountDB)
                .filter(AccountDB.is_active == True, AccountDB.is_online == True)
                .first()
            )
            if not account:
                logger.error("No available account")
                await asyncio.sleep(60)
                continue

            try:
                # Prepare request parameters
                timestamp = int(time.time() * 1000)
                params = {
                    "_t": timestamp,
                    "day": task.date,
                    "countryCode": "0055",
                    "column": "createTime",
                    "order": "desc",
                    "field": "id,,userName,countryName,operator,smsFrom,smsTo,message,sendResult,gatewayDr,gatewayRealDr,intervalTime,smsCount,smsFee,currency,sendDrStatus,resendDrTimes,sendTime,updateTime,gatewayName,gatewayResult,validateResult,action",
                    "pageNo": task.current_page,
                    "pageSize": 3000,
                }
                headers = {"X-Access-Token": str(account.token)}

                async with aiohttp.ClientSession() as client:
                    async with client.get(
                        base_url, params=params, headers=headers
                    ) as response:

                        if response.status == 200:
                            data = await response.json()

                            # Write data to CSV file
                            with open(task.data_file_path, "a", newline="") as f:
                                writer = csv.writer(f)
                                for record in data.get("result", {}).get("records", []):
                                    writer.writerow(
                                        [
                                            record.get("id"),
                                            record.get("userName"),
                                            record.get("countryName"),
                                            record.get("operator"),
                                            record.get("smsFrom"),
                                            record.get("smsTo"),
                                            record.get("message"),
                                            record.get("sendResult"),
                                            record.get("sendTime"),
                                        ]
                                    )

                            # Update task progress
                            task.current_page += 1
                            task.total_page = data.get("result", {}).get("pages", 0)
                            session.commit()
                            logger.info(
                                f"Task {task_id} completed page {task.current_page}"
                            )
                        else:
                            setattr(account, "is_online", False)
                            session.commit()
                            logger.error(
                                f"Request failed with status {response.status}"
                            )
                            break

                await asyncio.sleep(
                    spider_config.sleep_time
                )  # Use the configurable sleep time

            except Exception as e:
                logger.error(f"Error in spider task: {str(e)}")
                await asyncio.sleep(5)  # Wait before retrying on error

        # Mark task as done if completed
        if task.current_page >= task.total_page:
            task.done = True
            session.commit()

    except Exception as e:
        logger.error(f"Fatal error in spider task: {str(e)}")
    finally:
        session.close()


class TaskManager:
    def __init__(self):
        self.session = SessionLocal()
        self.output_dir = "output"
        os.makedirs(self.output_dir, exist_ok=True)

    async def create_task(self, date: str):
        task = TaskDB(
            date=date,
            stop_flag=True,
            done=False,
            created_at=datetime.now(),
            data_file_path=os.path.join(
                self.output_dir,
                f"data_{date}_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv",
            ),
        )
        # create the task result null file
        with open(str(task.data_file_path), "w") as f:
            f.write("")

        self.session.add(task)
        self.session.commit()
        return task

    def get_tasks(self):
        return self.session.query(TaskDB).order_by(TaskDB.created_at.desc()).all()

    async def start_task(self, task_id: int):
        task = self.session.query(TaskDB).get(task_id)
        if task:
            task.stop_flag = False
            self.session.commit()
            # use the asyncio.ensure_future to run the task in the background
            # the task is the spider task
            asyncio.ensure_future(spider_task(task_id))

            return True
        return False

    async def stop_task(self, task_id: int):
        task = self.session.query(TaskDB).get(task_id)
        if task:
            task.stop_flag = True
            self.session.commit()
            return True
        return False

    async def update_progress(self, task_id: int, current_page: int):
        task = self.session.query(TaskDB).get(task_id)
        if task:
            task.current_page = current_page
            if current_page >= task.total_page:
                task.done = True
            self.session.commit()
            return True
        return False

    @staticmethod
    async def update_sleep_time(sleep_time: int):
        """Update the spider sleep time"""
        if sleep_time > 0:
            spider_config.sleep_time = sleep_time
            return True
        return False

    def get_spider_sleep_time(self):
        """Get the current spider sleep time"""
        return spider_config.sleep_time
