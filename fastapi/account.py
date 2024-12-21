import aiohttp
from pydantic import BaseModel
from typing import List, Optional
from database import Base, engine, SessionLocal, AccountDB
import time
from utils.logger_config import get_logger
import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = get_logger(__name__)


class Account(BaseModel):
    username: str
    password: str
    token: Optional[str] = None
    is_online: bool = False
    is_active: bool = True

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm(cls, obj):
        return cls.parse_obj(obj.__dict__)


class AccountManager:
    def __init__(self):
        self.engine = engine
        Base.metadata.create_all(self.engine)
        self.session = SessionLocal()
        self.health_check_url = "https://web.antgst.com/antgst/sys/user/isCommonUser"
        self.scheduler = AsyncIOScheduler()
        self.health_check_task = None
        self.loop = asyncio.get_event_loop()
        logger.info("AccountManager initialized, starting health check task...")
        self.start_health_check_task()

    def start_health_check_task(self):
        """Start the periodic health check task"""
        if self.health_check_task is None:

            async def run_periodic():
                logger.info("Starting periodic health check loop")
                while True:
                    logger.debug("Running periodic health check iteration")
                    try:
                        await self.periodic_health_check()
                    except Exception as e:
                        logger.error(f"Error in periodic health check loop: {str(e)}")
                    logger.debug("Sleeping for 10 minutes before next health check")
                    await asyncio.sleep(600)

            self.health_check_task = asyncio.ensure_future(run_periodic())
            logger.info(
                f"Health check task created with ID: {id(self.health_check_task)}"
            )

    async def check_account_health(self, account: AccountDB) -> bool:
        """Check if an account is healthy and online"""
        if not account.is_active is True or account.token is None:
            return False

        headers = {"X-Access-Token": str(account.token)}
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    self.health_check_url, headers=headers
                ) as response:
                    if response.status == 200:
                        if account.is_online is False:
                            account.is_online = True  # type: ignore
                            self.session.commit()
                        return True
            except Exception as e:
                logger.error(f"Health check failed for {account.username}: {str(e)}")

        # If we reach here, either the request failed or returned non-200
        if account.is_active:
            # Try to login again
            login_success = await self.login(account)
            if not login_success:
                account.is_online = False  # type: ignore
                self.session.commit()
            return login_success
        return False

    async def periodic_health_check(self):
        """Run health checks for all active accounts"""
        logger.debug("Starting periodic health check")
        try:
            accounts = (
                self.session.query(AccountDB).filter(AccountDB.is_active == True).all()
            )
            logger.info(f"Found {len(accounts)} active accounts to check")
            for account in accounts:
                logger.info(f"Checking health for account: {account.username}")
                is_healthy = await self.check_account_health(account)
                logger.info(
                    f"Health check for {account.username}: {'healthy' if is_healthy else 'unhealthy'}"
                )
        except Exception as e:
            logger.error(f"Error in periodic health check: {str(e)}")
        finally:
            logger.debug("Completed periodic health check")

    async def cleanup(self):
        """Cleanup method to be called when shutting down"""
        logger.info("Starting cleanup process")
        if self.health_check_task:
            logger.info("Canceling health check task")
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                logger.info("Health check task cancelled successfully")
        logger.info("Cleanup completed")

    def add_account(self, username: str, password: str) -> bool:
        if self.session.query(AccountDB).filter(AccountDB.username == username).first():
            logger.warning(f"Failed to add account: {username} already exists")
            return False
        account = AccountDB(username=username, password=password)
        self.session.add(account)
        self.session.commit()
        logger.info(f"Added new account: {username}")
        return True

    def delete_account(self, username: str) -> bool:
        account = (
            self.session.query(AccountDB).filter(AccountDB.username == username).first()
        )
        if account:
            self.session.delete(account)
            self.session.commit()
            logger.info(f"Deleted account: {username}")
            return True
        logger.warning(f"Failed to delete account: {username} not found")
        return False

    def get_accounts(self) -> List[Account]:
        accounts = self.session.query(AccountDB).all()
        if not accounts:
            logger.debug("No accounts found in database")
            return []
        logger.debug(f"Retrieved {len(accounts)} accounts from database")
        return [Account.from_orm(acc) for acc in accounts]

    async def set_active_status(self, username: str, status: bool) -> bool:
        account = (
            self.session.query(AccountDB).filter(AccountDB.username == username).first()
        )
        if account:
            account.is_active = status  # type: ignore
            self.session.commit()
            logger.info(f"Set account {username} active status to: {status}")
            return True
        logger.warning(f"Failed to set active status: {username} not found")
        return False

    async def login(self, account: AccountDB) -> bool:
        """Internal method to handle login logic with an existing account object"""
        timestamp = int(time.time() * 1000)
        url = f"https://web.antgst.com/antgst/sys/getCheckCode?_t={timestamp}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    code = data["result"]["code"]
                    key = data["result"]["key"]
                    login_data = {
                        "username": account.username,
                        "password": account.password,
                        "captcha": code,
                        "checkKey": key,
                        "remember_me": True,
                    }

                    async with session.post(
                        "https://web.antgst.com/antgst/sys/login", json=login_data
                    ) as login_response:
                        if login_response.status == 200:
                            login_json = await login_response.json()
                            token = login_json["result"]["token"]
                            account.token = token  # type: ignore
                            account.is_online = True  # type: ignore
                            self.session.commit()
                            logger.info(
                                f"login user: {account.username}, token: {token}"
                            )
                            return True
        return False

    async def logout(self, account: AccountDB) -> bool:
        """Logout an account and clear its token"""
        if not account.token:  # type: ignore
            logger.warning(f"No token found for user: {account.username}")
            return False

        logout_url = "https://web.antgst.com/antgst/sys/logout"
        headers = {"X-Access-Token": str(account.token)}  # type: ignore

        async with aiohttp.ClientSession() as session:
            async with session.get(logout_url, headers=headers) as response:
                if response.status != 200:
                    logger.error(f"Logout failed for user: {account.username}")
                    return False

                account.token = None  # type: ignore
                account.is_online = False  # type: ignore
                self.session.commit()
                logger.info(f"Logout user: {account.username}")
                return True
