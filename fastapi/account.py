from pydantic import BaseModel
from typing import List, Optional
import json
from pathlib import Path

class Account(BaseModel):
    username: str
    password: str
    is_active: bool = True
    is_online: bool = False  # Add online status field

class AccountManager:
    def __init__(self):
        self.accounts_file = Path("accounts.json")
        self.accounts: List[Account] = []
        self.load_accounts()

    def load_accounts(self):
        if self.accounts_file.exists():
            data = json.loads(self.accounts_file.read_text())
            self.accounts = [Account(**account) for account in data]

    def save_accounts(self):
        data = [account.dict() for account in self.accounts]
        self.accounts_file.write_text(json.dumps(data, indent=2))

    def add_account(self, username: str, password: str) -> bool:
        if any(acc.username == username for acc in self.accounts):
            return False
        self.accounts.append(Account(username=username, password=password))
        self.save_accounts()
        return True

    def delete_account(self, username: str) -> bool:
        for i, account in enumerate(self.accounts):
            if account.username == username:
                self.accounts.pop(i)
                self.save_accounts()
                return True
        return False

    def toggle_account(self, username: str) -> bool:
        for account in self.accounts:
            if account.username == username:
                account.is_active = not account.is_active
                self.save_accounts()
                return True
        return False

    def get_accounts(self) -> List[Account]:
        return self.accounts

    def set_online_status(self, username: str, status: bool) -> bool:
        for account in self.accounts:
            if account.username == username:
                account.is_online = status
                self.save_accounts()
                return True
        return False
