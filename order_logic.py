import math
import time

def calculate_daily_orders(project_data, current_price, target_etf):
    turn = float(project_data.get("turn", 0.0))
    splits = int(project_data.get("splits", 40))
    total_budget = float(project_data.get("total_budget", 10000.0))
    total_spent = float(project_data.get("total_spent", 0.0))
    db_avg_price = float(project_data.get("avg_price", 0.0))
    db_shares = float(project_data.get("total_shares", 0.0))

    if turn >= splits:
        daily_buy_budget = 0.0
    else:
        remaining_budget = total_budget - total_spent
        daily_buy_budget = remaining_budget / (splits - turn)

    buy1_price = db_avg_price if db_avg_price > 0 else current_price
    buy1_qty = math.floor((daily_buy_budget * 0.5) / buy1_price) if buy1_price > 0 else 0
    if buy1_qty == 0 and daily_buy_budget > 0 and buy1_price > 0:
        buy1_qty = 1

    buy2_price = current_price * 1.10
    buy2_qty = math.floor((daily_buy_budget * 0.5) / buy2_price) if buy2_price > 0 else 0
    if buy2_qty == 0 and daily_buy_budget > 0 and buy2_price > 0:
        buy2_qty = 1

    sell_price = db_avg_price * 1.10
    sell_qty = db_shares

    return {
        "buy1": {"qty": buy1_qty, "price": buy1_price},
        "buy2": {"qty": buy2_qty, "price": buy2_price},
        "sell": {"qty": sell_qty, "price": sell_price}
    }

def execute_orders(api, target_etf, orders):
    success_orders = 0
    fail_orders = 0
    messages = []
    
    buy1_qty = orders["buy1"]["qty"]
    buy1_price = orders["buy1"]["price"]
    buy2_qty = orders["buy2"]["qty"]
    buy2_price = orders["buy2"]["price"]
    sell_qty = orders["sell"]["qty"]
    sell_price = orders["sell"]["price"]

    if buy1_qty > 0:
        success, res = api.place_order(target_etf, buy1_qty, buy1_price, order_type="34")
        if success:
            success_orders += 1
            messages.append(f"✅ 매수 1순위(평단 LOC) 성공: {buy1_qty}주 @ ${buy1_price:.2f}")
        else:
            fail_orders += 1
            messages.append(f"❌ 매수 1순위: {res}")
        time.sleep(1.0)
        
    if buy2_qty > 0:
        success, res = api.place_order(target_etf, buy2_qty, buy2_price, order_type="34")
        if success:
            success_orders += 1
            messages.append(f"✅ 매수 2순위(고가 LOC) 성공: {buy2_qty}주 @ ${buy2_price:.2f}")
        else:
            fail_orders += 1
            messages.append(f"❌ 매수 2순위: {res}")
        time.sleep(1.0)
        
    if sell_qty > 0:
        success, res = api.place_order(target_etf, -sell_qty, sell_price, order_type="00")
        if success:
            success_orders += 1
            messages.append(f"✅ 익절 매도 성공: {sell_qty}주 @ ${sell_price:.2f}")
        else:
            fail_orders += 1
            messages.append(f"❌ 익절 매도: {res}")
            
    return success_orders, fail_orders, messages
