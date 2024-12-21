import aiohttp
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, Column, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import time
from utils.logger_config import get_logger

logger = get_logger(__name__)

Base = declarative_base()


class AccountDB(Base):
    __tablename__ = "accounts"

    username = Column(String, primary_key=True)
    password = Column(String, nullable=False)
    token = Column(String, nullable=True)
    is_online = Column(Boolean, default=False, server_default="0")


class Account(BaseModel):
    username: str
    password: str
    token: Optional[str] = None
    is_online: bool = False

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm(cls, obj):
        return cls.parse_obj(obj.__dict__)


class AccountManager:
    def __init__(self):
        self.engine = create_engine("sqlite:///spider.db")
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

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

    async def set_online_status(self, username: str, status: bool) -> bool:
        account = (
            self.session.query(AccountDB).filter(AccountDB.username == username).first()
        )
        if account:
            if status and not account.is_online:  # type: ignore
                logger.info(f"Attempting to login account: {username}")
                login_success = await self.login(account)
                if not login_success:
                    logger.error(f"Failed to login account: {username}")
                    return False
            else:
                # If going offline, try to logout first
                if not status and account.is_online:  # type: ignore
                    logout_success = await self.logout(account)
                    if not logout_success:
                        logger.error(f"Failed to logout account: {username}")
                        return False
                else:
                    account.is_online = status  # type: ignore
                    self.session.commit()
                logger.info(f"Set account {username} online status to: {status}")
            return True
        logger.warning(f"Failed to set online status: {username} not found")
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
