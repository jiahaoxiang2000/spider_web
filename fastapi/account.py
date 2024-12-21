from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, Column, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class AccountDB(Base):
    __tablename__ = "accounts"

    username = Column(String, primary_key=True)
    password = Column(String, nullable=False)
    token = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, server_default="1")
    is_online = Column(Boolean, default=False, server_default="0")


class Account(BaseModel):
    username: str
    password: str
    token: Optional[str] = None
    is_active: bool = True
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
            return False
        account = AccountDB(username=username, password=password)
        self.session.add(account)
        self.session.commit()
        return True

    def delete_account(self, username: str) -> bool:
        account = (
            self.session.query(AccountDB).filter(AccountDB.username == username).first()
        )
        if account:
            self.session.delete(account)
            self.session.commit()
            return True
        return False

    def toggle_account(self, username: str) -> bool:
        account = (
            self.session.query(AccountDB).filter(AccountDB.username == username).first()
        )
        if account:
            account.is_active = not account.is_active  # type: ignore
            self.session.commit()
            return True
        return False

    def get_accounts(self) -> List[Account]:
        accounts = self.session.query(AccountDB).all()
        if not accounts:
            return []
        return [
            Account.from_orm(acc) for acc in accounts
        ]  # Using the new from_orm method

    def set_online_status(self, username: str, status: bool) -> bool:
        account = (
            self.session.query(AccountDB).filter(AccountDB.username == username).first()
        )
        if account:
            account.is_online = status  # type: ignore
            self.session.commit()
            return True
        return False
