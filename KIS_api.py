import mojito
import pandas as pd
import datetime
import requests
import json


class BankisAPI:
    """
    한국투자증권 API를 이용하여 증권 데이터를 활용한 Repo입니다.\n
    KIS Developers 에서 API 신청을 한 이후 사용해 주세요.
    """

    def __init__(self, file: str) -> None:
        self.file = file
        self.api_key = None
        self.api_secret = None
        self.acc_no = None
        self.broker = None
        self.URL = "https://openapi.koreainvestment.com:9443"
        self.access_token = None

    def LoadApiCredentials(self):
        '''
        발급받은 API의 key, secret key, 계좌번호, Access Token을 불러오는 함수
        '''
        with open(self.file, 'r') as information:
            information = information.readlines()

            if len(information) == 3:
                self.api_key, self.api_secret, self.acc_no = [
                    inform.rstrip() for inform in information]
            elif len(information) == 4:
                self.api_key, self.api_secret, self.acc_no, self.access_token = [
                    inform.rstrip() for inform in information]

    def AccessCredential(self):
        body_data = {
            "grant_type": "client_credentials",
            "appkey": self.api_key,
            "appsecret": self.api_secret,
        }
        credential_response = requests.post(
            url=f"{self.URL}/oauth2/tokenP",
            headers={"content-type": "application/json"},
            data=json.dumps(body_data)
        )

        self.access_token = f"Bearer {credential_response.json()['access_token']}"
        return self.access_token
