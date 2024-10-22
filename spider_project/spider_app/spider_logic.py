import requests
import pandas as pd
from datetime import datetime
from .models import Spider


class SpiderLogic:
    def __init__(self, spider_data):
        self.username = spider_data["username"]
        self.password = spider_data["password"]
        self.date = spider_data["date"]
        self.country_code = self.get_country_code(spider_data["country_code"])
        self.token = ""
        self.page_number = spider_data["page_number"]

    def get_country_code(self, country):
        country_codes = {
            "Brazil": "0055",
            "India": "0091",
            "Indonesia": "0062",
            "Philippines": "0063",
            "Pakistan": "0092",
        }
        return country_codes.get(country, "")

    def get_token(self):
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
            else:
                raise Exception("Failed to login")
        else:
            raise Exception("Failed to get check code")

    def fetch_data(self):
        timestamp = int(datetime.utcnow().timestamp())
        query = f"_t={timestamp}&day={self.date}&countryCode={self.country_code}&column=createtime&order=desc&gatewayDr=000&pageNo={self.page_number}&pageSize=100"
        url = f"https://web.antgst.com/antgst/sms/otpPremium/channel/sendRecordList?{query}"
        response = requests.get(url, headers={"X-Access-Token": self.token})
        if response.status_code == 200:
            data = response.json()
            records = data["result"]["records"]
            self.store_data_csv(records)
        else:
            raise Exception("Failed to fetch data")

    def store_data_csv(self, data):
        df = pd.DataFrame(data)
        df.to_csv(
            f"data_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv", index=False
        )

    def start(self):
        self.get_token()
        self.fetch_data()

    @staticmethod
    def status():
        return "Spider is running"
