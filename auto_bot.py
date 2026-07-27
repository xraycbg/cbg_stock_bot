import os
import time
import datetime
import schedule
import pandas as pd
from dotenv import load_dotenv

from kis_api import KisOpenApi
from github_db import GithubDB
import order_logic

def run_bot():
    print(f"[{datetime.datetime.now()}] 🤖 자동 스케줄러: 무한매수법 주문 로직 시작")
    
    # 환경변수 및 객체 초기화
    load_dotenv()
    db = GithubDB()
    api = KisOpenApi()
    
    # 1. DB 상태 로드
    state, sha = db.load_state()
    if not state:
        print("DB 로드 실패. 중단합니다.")
        return

    # 2. 계좌 잔고 동기화 (전체 잔고 가져오기)
    success, holdings = api.get_balance()
    if not success:
        print("잔고 조회 실패. 중단합니다.")
        return
        
    projects = state.get("projects", {})
    any_db_updated = False
    
    for p_id, p in projects.items():
        ticker = p.get("target_etf", "")
        if not ticker: continue
        
        print(f"[{ticker}] 프로젝트 진행 상태 업데이트 중...")
        # 3. 잔고를 기반으로 DB 수량/평단가 및 회차(Turn) 최신화
        target_holding = None
        for hold in holdings:
            if hold.get("ovrs_pdno") == ticker or hold.get("pdno") == ticker or hold.get("pd_no") == ticker:
                target_holding = hold
                break
                
        actual_shares = 0.0
        actual_avg_price = 0.0
        
        if target_holding:
            actual_shares = float(target_holding.get("ovrs_cblc_qty", target_holding.get("allo_qty", 0.0)))
            actual_avg_price = float(target_holding.get("pchs_avg_pric", 0.0))
            
        old_shares = float(p.get("total_shares", 0.0))
        old_turn = int(p.get("turn", 0))
        new_turn = old_turn
        
        if actual_shares == 0 and old_shares > 0:
            print(f"[{ticker}] 전량 매도(익절) 감지! 회차를 0으로 초기화합니다.")
            new_turn = 0
            p["total_spent"] = 0.0
            
        elif actual_shares > old_shares and old_turn > 0:
            diff_shares = actual_shares - old_shares
            print(f"[{ticker}] 추가 매수 체결 감지 (+{diff_shares}주). 회차 유지.")
            p["total_spent"] = float(p.get("total_spent", 0.0)) + (diff_shares * actual_avg_price)
            
        elif actual_shares == 0 and old_shares == 0 and old_turn > 0:
            print(f"[{ticker}] 주식은 없는데 회차가 {old_turn}입니다. 강제 초기화 진행.")
            new_turn = 0
            p["total_spent"] = 0.0
            
        p["turn"] = new_turn
        p["total_shares"] = actual_shares
        p["avg_price"] = actual_avg_price
        
        if old_shares != actual_shares or old_turn != new_turn:
            any_db_updated = True
        
        # 4. 오늘의 주문 금액 계산
        current_price = api.get_current_price(ticker)
        if current_price <= 0:
            print(f"[{ticker}] 현재가 조회 실패. 스킵합니다.")
            continue
            
        orders = order_logic.calculate_daily_orders(p, current_price, ticker)
        card_b1_qty = orders["buy1"]["qty"]
        card_b1_price = orders["buy1"]["price"]
        card_b2_qty = orders["buy2"]["qty"]
        card_b2_price = orders["buy2"]["price"]
        db_shares = actual_shares
        sell_price = orders["sell"]["price"]
        
        # 5. 중복 주문 방지 로직 (오늘 성공했던 내역 제외)
        today_str = pd.Timestamp.now().strftime("%Y-%m-%d")
        today_history = [entry for entry in p.get("history", []) if entry.get("date", "").startswith(today_str)]
        
        already_buy1, already_buy2, already_sell = False, False, False
        for entry in today_history:
            for order in entry.get("orders", []):
                if order.get("구분") == "절반 매수 (평단가 LOC)": already_buy1 = True
                elif order.get("구분") == "절반 매수 (고가 LOC)": already_buy2 = True
                elif order.get("구분") == "익절 매도": already_sell = True
                
        approve_buy1 = (card_b1_qty > 0 and not already_buy1)
        approve_buy2 = (card_b2_qty > 0 and not already_buy2)
        approve_sell = (db_shares > 0 and not already_sell)
        
        if not approve_buy1 and not approve_buy2 and not approve_sell:
            print(f"[{ticker}] 오늘 필요한 모든 주문이 이미 접수되었습니다 (추가 주문 없음).")
            continue
            
        # 6. 증권사 서버로 실제 주문 전송
        print(f"[{ticker}] 주문 전송 시작...")
        success_orders = 0
        order_data_log = []
        
        if approve_buy1:
            succ, res = api.place_order(ticker, card_b1_qty, card_b1_price, order_type="34")
            if succ:
                success_orders += 1
                order_data_log.append({"구분": "절반 매수 (평단가 LOC)", "수량": card_b1_qty, "단가": card_b1_price})
                print(f"[{ticker}] 매수1 성공")
            else:
                print(f"[{ticker}] 매수1 실패: {res}")
            time.sleep(1.0)
            
        if approve_buy2:
            succ, res = api.place_order(ticker, card_b2_qty, card_b2_price, order_type="34")
            if succ:
                success_orders += 1
                order_data_log.append({"구분": "절반 매수 (고가 LOC)", "수량": card_b2_qty, "단가": card_b2_price})
                print(f"[{ticker}] 매수2 성공")
            else:
                print(f"[{ticker}] 매수2 실패: {res}")
            time.sleep(1.0)
            
        if approve_sell:
            succ, res = api.place_order(ticker, -db_shares, sell_price, order_type="00")
            if succ:
                success_orders += 1
                order_data_log.append({"구분": "익절 매도", "수량": db_shares, "단가": sell_price})
                print(f"[{ticker}] 매도 성공")
            else:
                print(f"[{ticker}] 매도 실패: {res}")
                
        # 7. 성공한 주문이 있다면 DB History 갱신
        if success_orders > 0:
            log_entry = {
                "date": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
                "env": api.env,
                "target": ticker,
                "turn_before": old_turn,
                "turn_after": new_turn,
                "orders": order_data_log
            }
            p.setdefault("history", []).append(log_entry)
            any_db_updated = True
            print(f"[{ticker}] 성공한 {success_orders}건 DB History 반영 완료.")
            
    # 8. 변경된 상태(계좌 동기화 결과 및 주문 내역)를 깃허브에 최종 저장
    if any_db_updated:
        state["projects"] = projects
        db_succ, _ = db.update_state(state, sha)
        if db_succ:
            print("💾 깃허브 DB 원격 업데이트 완료.")
        else:
            print("🚨 깃허브 DB 원격 업데이트 실패.")
    else:
        print("DB에 갱신할 내용이 없습니다.")

def main():
    print("=" * 50)
    print("🚀 자동매매 스케줄러(auto_bot) 작동 시작")
    print("=" * 50)
    
    # 🌟 미국장 오픈 시간에 맞춰 매일 23:00 (밤 11시) 에 주문 로직 실행 예약
    # (서머타임 등 변경 시 이 시간을 "22:30" 등으로 수정할 수 있습니다.)
    target_time = "23:00"
    schedule.every().day.at(target_time).do(run_bot)
    
    print(f"타이머 등록 완료. 매일 밤 [{target_time}] 에 스스로 주문을 전송합니다.")
    print("서버를 끄지 않는 이상 백그라운드에서 계속 대기합니다...\n")
    
    # 1분에 한 번씩 스케줄이 되었는지 체크하며 무한 대기
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
