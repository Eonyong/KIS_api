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
        self.LoadApiCredentials()
        

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
        '''
        Access Token을 발급 받는 함수
        '''
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

    def AccountLink(self):
        '''
        API를 활용하여 계좌와 연결하는 함수
        '''
        self.broker = mojito.KoreaInvestment(
            api_key=self.api_key,
            api_secret=self.api_secret,
            acc_no=self.acc_no
        )
        return self.broker

    def WeeklyIPO(self):
        """매주 상장하는 기업 데이터 도출"""
        today = datetime.datetime.now()
        weekly = today + datetime.timedelta(days=6)

        ipo = requests.get(
            url=f"{self.URL}/uapi/domestic-stock/v1/ksdinfo/pub-offer",
            headers={
                "content-type": "application/json",
                "authorization": self.access_token,
                "appkey": self.api_key,
                "appsecret": self.api_secret,
                "tr_id": "HHKDB669108C0",
                "custtype": "P"
            },
            params={
                "F_DT": today.strftime("%Y%m%d"),
                "T_DT": weekly.strftime("%Y%m%d"),
            })

        ipo_companies = ipo.json()["output1"]

        print(f"이번주에 상장하는 기업은 __총 {len(ipo_companies)}개__ 입니다.")
        for company in ipo_companies:
            print(f"""
상장 기업은 __{company["isin_name"]}__이고
청약 시작일은 {company["record_date"][:4]}년 {company["record_date"][4:6]}월 {company["record_date"][6:]}일 이고
쳥약 진행일은 {company["subscr_dt"]}동안 진행이 됩니다.
청약 환불일은 {company["refund_dt"]}
주관사는 __{company["lead_mgr"]}__입니다.
청약 확정 금액은 __{company["fix_subscr_pri"].strip()}원__ 입니다.
            """)

    def MakeExcel(self):
        '''국내에 상장되어 있는 주식 및 ETF 가격 리스트를 CSV로 출력하는 Code'''

        output = self.broker.fetch_symbols()
        output.to_csv("symbols.csv", index=False)  # index를 제외하고 CSV로 저장

        data = []
        for idx, row in output.iterrows():
            try:
                if row["단축코드"].isnumeric() and row["단축코드"] > '0':
                    value = self.broker.fetch_price(row["단축코드"])['output']
                    data.append([row["단축코드"], row["한글명"], value["stck_prpr"]])
            except:
                continue

        data_df = pd.DataFrame(data, columns=["단축코드", "한글명", "가격"])
        data_df.to_csv("stock_price_list.csv", index=False)
