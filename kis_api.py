import requests
import json
import os
import time
from dotenv import load_dotenv

# 로컬 환경 변수 로드
load_dotenv()

class KISApi:
    def __init__(self):
        self.env = os.getenv("KIS_ENVIRONMENT", "mock")
        
        # 환경에 맞춰 각기 다른 환경변수 로드
        if self.env == "real":
            self.appkey = os.getenv("REAL_KIS_APPKEY")
            self.appsecret = os.getenv("REAL_KIS_APPSECRET")
            self.cano = os.getenv("REAL_KIS_CANO")
            self.acnt_prdt_cd = os.getenv("REAL_KIS_ACNT_PRDT_CD", "01")
            self.base_url = "https://openapi.koreainvestment.com:9443"
            self.tr_id_buy = "TTTT1002U"
            self.tr_id_sell = "TTTT1006U"
            self.tr_id_balance = "TTTS3012R"
        else:
            self.appkey = os.getenv("MOCK_KIS_APPKEY")
            self.appsecret = os.getenv("MOCK_KIS_APPSECRET")
            self.cano = os.getenv("MOCK_KIS_CANO")
            self.acnt_prdt_cd = os.getenv("MOCK_KIS_ACNT_PRDT_CD", "01")
            self.base_url = "https://openapivts.koreainvestment.com:29443"
            self.tr_id_buy = "VTTT1002U"
            self.tr_id_sell = "VTTT1006U"
            self.tr_id_balance = "VTTS3012R"
            
        self.token_cache_file = f"token_cache_{self.env}.json"

    def get_access_token(self):
        """
        한투 API 인증 토큰을 발급받거나 캐시에서 로드합니다.
        토큰의 유효 기간(24시간)을 확인하여 만료된 경우 자동으로 갱신합니다.
        """
        # 1. 캐시된 토큰 로드 시도
        if os.path.exists(self.token_cache_file):
            try:
                with open(self.token_cache_file, "r") as f:
                    cache = json.load(f)
                    # 만료 시간(현재 시간보다 1시간 전 안전마진) 검사
                    if cache.get("expires_at", 0) > time.time() + 3600:
                        return cache["access_token"]
            except Exception as e:
                print(f"토큰 캐시 로드 오류: {e}")

        # 2. 신규 토큰 발급
        url = f"{self.base_url}/oauth2/tokenP"
        payload = {
            "grant_type": "client_credentials",
            "appkey": self.appkey,
            "appsecret": self.appsecret
        }
        headers = {"content-type": "application/json"}
        
        res = requests.post(url, headers=headers, data=json.dumps(payload))
        if res.status_code == 200:
            data = res.json()
            access_token = data["access_token"]
            # 만료 시점 계산 (만료 시간 - 2시간 차감하여 안전하게 갱신되도록 함)
            expires_in = data.get("expires_in", 86400)
            expires_at = time.time() + expires_in
            
            # 캐시 파일 저장
            with open(self.token_cache_file, "w") as f:
                json.dump({
                    "access_token": access_token,
                    "expires_at": expires_at
                }, f)
                
            print("한투 API 토큰이 새로 발급 및 캐싱되었습니다.")
            return access_token
        else:
            raise Exception(f"토큰 발급 실패: {res.status_code} - {res.text}")

    def get_current_price(self, ticker, exchange="NAS"):
        """
        미국 주식 현재가(시세)를 조회합니다.
        한투 API에서 시세를 제공하지 않거나(모의투자 환경 등) 장외 시간일 경우 실시간 시세를 백업 로드합니다.
        """
        # 1. 한투 API 시세 조회 시도
        try:
            token = self.get_access_token()
            url = f"{self.base_url}/uapi/overseas-price/v1/quotations/price"
            headers = {
                "content-type": "application/json; charset=utf-8",
                "authorization": f"Bearer {token}",
                "appkey": self.appkey,
                "appsecret": self.appsecret,
                "tr_id": "HHDFS00000300"
            }
            params = {
                "AUTH": "",
                "EXCD": exchange,
                "SYMB": ticker
            }
            res = requests.get(url, headers=headers, params=params, timeout=5)
            if res.status_code == 200:
                data = res.json()
                if data.get("rt_cd") == "0" and data.get("output", {}).get("last"):
                    last_val = data["output"]["last"].strip()
                    if last_val:
                        val = float(last_val)
                        if val > 0:
                            return val
        except Exception as e:
            print(f"한투 시세 조회 백업 전환: {e}")

        # 2. 백업 실시간 시세 조회 (Yahoo Finance API)
        try:
            yf_url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
            yf_headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
            yf_res = requests.get(yf_url, headers=yf_headers, timeout=5)
            if yf_res.status_code == 200:
                chart_data = yf_res.json()
                meta = chart_data["chart"]["result"][0]["meta"]
                price = meta.get("regularMarketPrice") or meta.get("previousClose")
                if price and float(price) > 0:
                    return float(price)
        except Exception as e:
            print(f"Yahoo Finance 시세 조회 실패: {e}")

        return 0.0


    def get_balance(self):
        """
        해외주식 잔고 및 예수금 정보를 조회합니다.
        반환값: (보유 종목 리스트, 외화 예수금(달러), 요약 딕셔너리)
        """
        token = self.get_access_token()
        url = f"{self.base_url}/uapi/overseas-stock/v1/trading/inquire-balance"
        
        headers = {
            "content-type": "application/json",
            "authorization": f"Bearer {token}",
            "appkey": self.appkey,
            "appsecret": self.appsecret,
            "tr_id": self.tr_id_balance
        }
        
        # 해외주식 잔고 조회의 필수 쿼리 매개변수
        params = {
            "CANO": self.cano,
            "ACNT_PRDT_CD": self.acnt_prdt_cd,
            "OVRS_EXCG_CD": "NASD",  # 미국 나스닥 기준 (TQQQ 등)
            "TR_CRCY_CD": "USD",     # 외화 기준 조회
            "CTX_AREA_FK200": "",
            "CTX_AREA_NK200": ""
        }
        
        res = requests.get(url, headers=headers, params=params)
        if res.status_code == 200:
            data = res.json()
            if data.get("rt_cd") == "0":
                holdings = data.get("output1", [])
                summary = data.get("output2", {})
                
                # 예수금 파싱 (output2의 frcr_dncl_amt_2 또는 frcr_drwg_psbl_amt)
                usd_cash = float(summary.get("frcr_dncl_amt_2", 0.0))
                if usd_cash == 0.0 and "frcr_drwg_psbl_amt" in summary:
                    usd_cash = float(summary.get("frcr_drwg_psbl_amt", 0.0))
                
                return holdings, usd_cash, summary
            else:
                raise Exception(f"잔고 조회 API 오류: {data.get('msg1')}")
        else:
            raise Exception(f"잔고 조회 HTTP 오류: {res.status_code} - {res.text}")


    def place_order(self, ticker, qty, price, order_type="34", exchange="NASD"):
        """
        미국 주식 매수/매도 주문을 실행합니다.
        - order_type: "00" (지정가), "34" (LOC 주문)
        - tr_id: self.tr_id_buy 또는 self.tr_id_sell
        """
        token = self.get_access_token()
        url = f"{self.base_url}/uapi/overseas-stock/v1/trading/order"
        
        # tr_id 결정 (기본은 매수)
        tr_id = self.tr_id_buy if qty > 0 else self.tr_id_sell
        actual_qty = abs(qty)
        
        headers = {
            "content-type": "application/json",
            "authorization": f"Bearer {token}",
            "appkey": self.appkey,
            "appsecret": self.appsecret,
            "tr_id": tr_id
        }
        
        # 모의투자는 한투 서버 특성상 지정가("00")만 지원되므로 모의투자 시 자동 보정
        actual_order_type = "00" if (self.env == "mock" and order_type == "34") else order_type

        # 가격 소수점 처리 (미국 주식은 $1 이상 종목 소수점 2자리 권장)
        price_str = f"{price:.2f}"
        if actual_order_type == "01": # 시장가의 경우 가격은 0
            price_str = "0"

        payload = {
            "CANO": self.cano,
            "ACNT_PRDT_CD": self.acnt_prdt_cd,
            "OVRS_EXCG_CD": exchange,
            "PDNO": ticker,
            "ORD_DVSN": actual_order_type,
            "ORD_QTY": str(actual_qty),
            "OVRS_ORD_UNPR": price_str,
            "ORD_SVR_DVSN_CD": "0"
        }

        
        res = requests.post(url, headers=headers, data=json.dumps(payload))
        if res.status_code == 200:
            data = res.json()
            if data.get("rt_cd") == "0":
                print(f"주문 성공 - 종목: {ticker}, 수량: {qty}, 가격: {price}, 유형: {order_type}")
                return True, data.get("output", {})
            else:
                msg = data.get("msg1") or data.get("message") or "주문 오류"
                print(f"주문 실패 API 메시지: {msg}")
                return False, msg
        else:
            try:
                err_data = res.json()
                err_msg = err_data.get("msg1") or err_data.get("message") or f"HTTP {res.status_code}"
            except Exception:
                err_msg = f"HTTP Error {res.status_code}"
            print(f"주문 HTTP 통신 에러: {res.status_code} - {res.text}")
            return False, err_msg


if __name__ == "__main__":
    # 로컬 간단 테스트
    try:
        api = KISApi()
        print("토큰 발급 테스트:")
        token = api.get_access_token()
        print("발급완료:", token[:10] + "...")
        
        print("\nTQQQ 현재가 테스트:")
        price = api.get_current_price("TQQQ")
        print("TQQQ 가격:", price)
        
        print("\n잔고 조회 테스트:")
        holdings, cash = api.get_balance()
        print("보유종목:", holdings)
        print("예수금(USD):", cash)
    except Exception as e:
        print("테스트 중 오류:", e)
