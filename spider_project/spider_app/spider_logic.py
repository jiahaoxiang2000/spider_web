import requests
import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SpiderLogic:
    def __init__(self, spider_data):
        self.username = spider_data.get("username", "yindu529")
        self.password = spider_data.get("password", "yindu529")
        self.target_username = spider_data.get("target_username", "admin")
        self.original_role_id = ""
        self.token = ""
        self.login()

    def __del__(self):
        # self.logout()
        pass

    def get_country_code(self, country):
        country_codes = {
            "Brazil": "0055",
            "India": "0091",
            "Indonesia": "0062",
            "Philippines": "0063",
            "Pakistan": "0092",
        }
        return country_codes.get(country, "")

    def login(self):
        timestamp = int(datetime.utcnow().timestamp())
        url = f"https://web.antgst.com/antgst/sys/getCheckCode?_t={timestamp}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            code = data["result"]["code"]
            key = data["result"]["key"]
            login_data = {
                "username": self.username,
                "password": self.password,
                "captcha": code,
                "checkKey": key,
                "remember_me": True,
            }
            login_response = requests.post(
                "https://web.antgst.com/antgst/sys/login", json=login_data
            )
            if login_response.status_code == 200:
                self.token = login_response.json()["result"]["token"]
                logger.info(f"login user: {self.username}, token: {self.token}")
            else:
                raise Exception("Failed to login")
        else:
            raise Exception("Failed to get check code")

    def logout(self):
        logout_url = "https://web.antgst.com/antgst/sys/logout"
        headers = {"X-Access-Token": self.token}
        response = requests.get(logout_url, headers=headers)
        if response.status_code != 200:
            logger.error(f"Logout failed for user: {self.username}")
            print("Logout failed")
        logger.info(f"Logout user: {self.username}")
        self.token = ""

    def fetch_data(self):
        timestamp = int(datetime.utcnow().timestamp())
        query = f"_t={timestamp}&day={self.date}&countryCode={self.country_code}&column=createtime&order=desc&gatewayDr=000&pageNo={self.page_number}&pageSize=100"
        url = f"https://web.antgst.com/antgst/sms/otpPremium/channel/sendRecordList?{query}"
        headers = {"X-Access-Token": self.token}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            records = data["result"]["records"]
            return records
        else:
            raise Exception("Failed to fetch data")
        return []

    def store_data_csv(self, data):
        df = pd.DataFrame(data)
        df.to_csv(
            f"data_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv", index=False
        )

    def spider_data(self, date="", country_code="", page_number=1):
        self.date = date
        self.country_code = self.get_country_code(country_code)
        self.page_number = page_number
        return self.fetch_data()

    def get_total_page(self, date="", country=""):
        self.date = date
        self.country_code = self.get_country_code(country)
        self.page_number = 1
        self.fetch_data()

        timestamp = int(datetime.utcnow().timestamp())
        query = f"_t={timestamp}&day={self.date}&countryCode={self.country_code}&column=createtime&order=desc&gatewayDr=000&pageNo={self.page_number}&pageSize=100"
        url = f"https://web.antgst.com/antgst/sms/otpPremium/channel/sendRecordList?{query}"
        headers = {"X-Access-Token": self.token}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            pages = data["result"]["pages"]
            return pages
        else:
            raise Exception("Failed to fetch data")

    def get_user_id(self, username):
        url = f"https://web.antgst.com/antgst/sys/user/getUserListByName?userName={username}"
        headers = {"X-Access-Token": self.token}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data[0]["id"]
        else:
            raise Exception("Failed to get user ID")

    def get_role_id(self, user_id):
        url = f"https://web.antgst.com/antgst/sys/user/queryUserRole?userid={user_id}"
        headers = {"X-Access-Token": self.token}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data["result"][0]
        else:
            raise Exception("Failed to get role ID")

    def delete_user_role(self, user_id, role_id):
        url = "https://web.antgst.com/antgst/sys/user/deleteUserRole"
        headers = {"X-Access-Token": self.token}
        params = {"roleId": role_id, "userId": user_id}
        response = requests.delete(url, headers=headers, params=params)
        if response.status_code == 200 and response.json().get("success"):
            return True
        else:
            raise Exception("Failed to delete user role")

    def add_user_role(self, user_id, role_id):
        url = "https://web.antgst.com/antgst/sys/user/addSysUserRole"
        headers = {"X-Access-Token": self.token, "Content-Type": "application/json"}
        data = {"roleId": role_id, "userIdList": [user_id]}
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200 and response.json().get("success"):
            return True
        else:
            raise Exception("Failed to add user role")

    def change_user_role(self, target_username):
        """
        Changes the role of the current user to match the role of the target user. NOTE: this role id change only works on one user-id account. not support for multiple user-id account.

        This method retrieves the current user's role and the target user's role,
        logs the change, deletes the current user's role, and assigns the target
        user's role to the current user.

        Args:
            target_username (str): The username of the target user whose role will be assigned to the current user.

        Returns:
            None


        """
        user_id = self.get_user_id(self.username)
        current_role_id = self.get_role_id(user_id)
        self.original_role_id = current_role_id  # Store original role ID
        target_id = self.get_user_id(target_username)
        target_role_id = self.get_role_id(target_id)
        logger.info(
            f"Changing role of user {self.username} to {target_username}, old role: {current_role_id}, new role: {target_role_id}"
        )

        # Delete current role
        self.delete_user_role(user_id, current_role_id)

        # Add new role
        self.add_user_role(user_id, target_role_id)

    def revert_normal_role(self):
        normal_role_id = "082678e5d9270824353a223a6727e009"
        user_id = self.get_user_id(self.username)
        user_role_id = self.get_role_id(user_id)
        logger.info(
            f"Reverting role of user {self.username} to normal, old role: {user_role_id}, new role: {normal_role_id}"
        )

        # Delete new role
        self.delete_user_role(user_id, user_role_id)

        # Reassign original role
        self.add_user_role(user_id, normal_role_id)

    @staticmethod
    def status():
        return "Spider is running"
