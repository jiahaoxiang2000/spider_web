import aiohttp
from typing import List, Optional, Dict
from utils.logger_config import get_logger

logger = get_logger(__name__)


class Auth:
    def __init__(self):

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
        self.upgrade_user_role_id = "743e6e95d9a4001e46a78c3606dcb15b"
        self.query_user_role_url = (
            "https://web.antgst.com/antgst/;/sys/user/queryUserRole"
        )
        # the query_user_role_url is GET request, the prams is like this:
        # ?userid=e888946e0213c9a4685bd94e7f1563ae

    async def is_super_user(self, user_id: str) -> bool:
        try:
            current_roles = await self.query_user_role(user_id)
            if current_roles and current_roles.get("result"):
                role_ids = current_roles["result"]
                is_super = self.upgrade_user_role_id in role_ids
                logger.info(f"User {user_id} super user status: {is_super}")
                return is_super
            return False
        except Exception as e:
            logger.error(f"Error checking super user status: {str(e)}")
            return False

    async def upgrade_authority(self, username: str) -> bool:
        try:
            users = await self.get_user_by_name(username)
            if not users:
                logger.error(f"upgrade_authority: {username} - user not found")
                return False

            user_id = users[0]["id"]
            logger.info(f"upgrade_authority: {username} {user_id}")

            # Use the new is_super_user method
            if await self.is_super_user(user_id):
                logger.info(f"User {username} is already a super user")
                return True

            # Add the role if user isn't a super user
            success = await self.add_user_role(self.upgrade_user_role_id, [user_id])
            if success:
                logger.info(f"Successfully upgraded authority for user: {username}")
            else:
                logger.error(f"Failed to upgrade authority for user: {username}")
            return success
        except Exception as e:
            logger.error(f"Error in upgrade_authority: {str(e)}")
            return False

    async def downgrade_authority(self, username: str) -> bool:
        try:
            users = await self.get_user_by_name(username)
            # log username and users[0]["id"] on INFO level
            if users:
                logger.info(f"downgrade_authority: {username} {users[0]['id']}")
                if username == users[0]["userName"]:
                    success = await self.delete_user_role(
                        self.upgrade_user_role_id, users[0]["id"]
                    )
                    if success:
                        logger.info(
                            f"Successfully downgraded authority for user: {username}"
                        )
                    else:
                        logger.error(
                            f"Failed to downgrade authority for user: {username}"
                        )
            return True
        except Exception:
            return False

    async def add_user_role(self, role_id: str, user_ids: List[str]) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                data = {"roleId": role_id, "userIdList": user_ids}
                logger.info(
                    f"Adding user role - roleId: {role_id}, userIds: {user_ids}"
                )
                async with session.post(self.add_url, json=data) as response:
                    success = response.status == 200
                    if success:
                        logger.info(
                            f"Successfully added role {role_id} to users {user_ids}"
                        )
                    else:
                        logger.error(
                            f"Failed to add role {role_id} to users {user_ids}"
                        )
                    return success
        except Exception as e:
            logger.error(f"Error adding user role: {str(e)}")
            return False

    async def delete_user_role(self, role_id: str, user_id: str) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                params = {"roleId": role_id, "userId": user_id}
                logger.info(
                    f"Deleting user role - roleId: {role_id}, userId: {user_id}"
                )
                async with session.delete(
                    f"{self.delete_url}", params=params
                ) as response:
                    success = response.status == 200
                    if success:
                        logger.info(
                            f"Successfully deleted role {role_id} from user {user_id}"
                        )
                    else:
                        logger.error(
                            f"Failed to delete role {role_id} from user {user_id}"
                        )
                    return success
        except Exception as e:
            logger.error(f"Error deleting user role: {str(e)}")
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

    async def query_user_role(self, user_id: str) -> Optional[Dict]:
        try:
            async with aiohttp.ClientSession() as session:
                params = {"userid": user_id}
                logger.info(f"Querying user roles for userId: {user_id}")
                async with session.get(
                    self.query_user_role_url, params=params
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"User roles query result: {result}")
                        return result
                    return None
        except Exception as e:
            logger.error(f"Error querying user roles: {str(e)}")
            return None
