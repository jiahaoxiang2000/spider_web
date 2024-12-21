import aiohttp
from typing import List, Optional, Dict
from utils.logger_config import get_logger

logger = get_logger(__name__)


class Auth:
    def __init__(self):
        # In a real application, this would be connected to a database
        self.user_authorities = {}  # username: authority_level
        self.add_url = "https://web.antgst.com/antgst/;/sys/user/addSysUserRole"
        # the add_url is POST request, the data is like this:
        # {
        #   "roleId": "743e6e95d9a4001e46a78c3606dcb15b",
        #   "userIdList": [
        #        "e888946e0213c9a4685bd94e7f1563ae"
        #     ]
        # }
        self.delete_url = "https://web.antgst.com/antgst/;/sys/user/deleteUserRole"
        # the delete_url is DELETE request, the prams is like this:
        # ?roleId=743e6e95d9a4001e46a78c3606dcb15b&userId=e888946e0213c9a4685bd94e7f1563ae
        self.query_user_id_url = (
            "https://web.antgst.com/antgst/;/sys/user/getUserListByName"
        )
        # the query_user_id_url is GET request, the prams is like this:
        # userName=SS678

    async def upgrade_authority(self, username: str) -> bool:
        try:
            self.user_authorities[username] = "admin"
            users = await self.get_user_by_name(username)
            # log username and users[0]["id"] on INFO level
            if users:
                logger.info(f"upgrade_authority: {username} {users[0]['id']}")
            else:
                logger.error(f"upgrade_authority: {username} - user not found")
            return True
        except Exception:
            return False

    async def downgrade_authority(self, username: str) -> bool:
        try:
            self.user_authorities[username] = "user"
            return True
        except Exception:
            return False

    def get_authority(self, username: str) -> str:
        return self.user_authorities.get(username, "user")

    async def add_user_role(self, role_id: str, user_ids: List[str]) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                data = {"roleId": role_id, "userIdList": user_ids}
                async with session.post(self.add_url, json=data) as response:
                    return response.status == 200
        except Exception:
            return False

    async def delete_user_role(self, role_id: str, user_id: str) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                params = {"roleId": role_id, "userId": user_id}
                async with session.delete(
                    f"{self.delete_url}", params=params
                ) as response:
                    return response.status == 200
        except Exception:
            return False

    async def get_user_by_name(self, username: str) -> Optional[Dict]:
        try:
            async with aiohttp.ClientSession() as session:
                params = {"userName": username}
                async with session.get(
                    self.query_user_id_url, params=params
                ) as response:
                    logger.info(f"get_user_by_name: {await response.json()}")
                    if response.status == 200:
                        return await response.json()
                    return None
        except Exception:
            return None
