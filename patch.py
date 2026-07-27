import re

with open("app.py", "r") as f:
    content = f.read()

# 1. Update line 636 to get holdings
content = content.replace("_, usd_cash_val, krw_cash_val, _ = get_cached_balance(api, api.env)",
                          "holdings, usd_cash_val, krw_cash_val, _ = get_cached_balance(api, api.env)")

# 2. Extract the DASHBOARD logic to replace the card_html ending and remove the DASHBOARD section
# I will use a regex to find the start of the card_html in the list loop and the end of the file.

pattern = r"(card_html = f\"\"\"<div class=\"pro-card list-card-touch\">.*?)(# ==========================================\n# 🔍 VIEW MODE 2: 360도 Pro 세부 대시보드 \(DETAIL\)\n# ==========================================.*)"
match = re.search(pattern, content, flags=re.DOTALL)
if not match:
    print("Regex match failed")
    exit(1)

list_part = match.group(1)

# Now we construct the new list part
new_card_body = """        card_html = f\"\"\"<div class="pro-card list-card-touch">
<div class="pro-card-header">
<div style="display: flex; flex-direction: column; align-items: flex-start; overflow: hidden; white-space: nowrap; min-width: 0; max-width: 75%;">
<span class="ticker-badge" style="flex-shrink: 0; margin-bottom: 6px;">{ticker} · {excg_tag}</span>
</div>
</div>
\"\"\"
        st.markdown(card_html, unsafe_allow_html=True)
        
        # 제목을 버튼(tertiary)으로 렌더링
        t_col1, t_col2 = st.columns([8, 2])
        with t_col1:
            if st.button(p['name'], key=f"edit_title_{p_id}", type="tertiary", use_container_width=True, help="클릭하여 제목 수정"):
                edit_title_dialog(p_id, p['name'])

        card_html2 = f\"\"\"
<div class="summary-grid" style="grid-template-columns: repeat(2, 1fr); gap: 10px; margin-top: 12px; margin-bottom: 12px; text-align: center;">
<div class="summary-item">
<div class="summary-label">현재가</div>
<div class="summary-val">${display_curr:.2f}</div>
</div>
<div class="summary-item">
<div class="summary-label">실시간 손익</div>
<div class="summary-val">{pnl_html}</div>
</div>
<div class="summary-item">
<div class="summary-label">{ticker} 평단</div>
<div class="summary-val">${db_avg_price:.2f}</div>
</div>
<div class="summary-item">
<div class="summary-label">{ticker} 수량</div>
<div class="summary-val">{db_shares:g}주</div>
</div>
<div class="summary-item">
<div class="summary-label">총 투자 예산</div>
<div class="summary-val">${total_budget:,.0f}</div>
</div>
<div class="summary-item">
<div class="summary-label">소진된 예산</div>
<div class="summary-val">${total_spent:,.0f}</div>
</div>
</div>

<div style="display:flex; justify-content:space-between; font-size:0.85rem; font-weight:700; color:#94a3b8;">
<span>회차 진행률 ({turn_cnt:g}/{splits_cnt}회)</span>
<span style="color:#ffffff;">${total_spent:,.0f} / ${total_budget:,.0f}</span>
</div>
<div class="roop-progress-bg">
<div class="roop-progress-fill" style="width: {prog_pct}%;"></div>
</div>
\"\"\"
        st.markdown(card_html2, unsafe_allow_html=True)

        # 오늘의 주문 2열 카드
        st.markdown('<div style="font-size:1.05rem; font-weight:800; color:#ffffff; margin-top:16px; margin-bottom:12px;">오늘의 주문</div>', unsafe_allow_html=True)

        ord_col1, ord_col2 = st.columns(2)
        with ord_col1:
            buy_html = f\"\"\"<div class="buy-box">
<div class="box-title-buy">매수 · LOC 2분할</div>
<div class="order-row">
<div>
<span class="price-bold">${card_b1_price:.2f}</span>
<span class="qty-text"> × {card_b1_qty}주</span>
</div>
<span class="tag-red">평단</span>
</div>
<div class="order-row">
<div>
<span class="price-bold">${card_b2_price:.2f}</span>
<span class="qty-text"> × {card_b2_qty}주</span>
</div>
<span class="tag-red">고가</span>
</div>
</div>\"\"\"
            st.markdown(buy_html, unsafe_allow_html=True)

        with ord_col2:
            sell_price = db_avg_price * 1.10
            sell_html = f\"\"\"<div class="sell-box">
<div class="box-title-sell">매도 · LOC / 지정가</div>
<div class="order-row">
<div>
<span class="price-bold">${sell_price:.2f}</span>
<span class="qty-text"> × {db_shares:g}주</span>
</div>
<span class="tag-purple">+10% 익절</span>
</div>
</div>\"\"\"
            st.markdown(sell_html, unsafe_allow_html=True)

        approve_buy1 = True if card_b1_qty > 0 else False
        approve_buy2 = True if card_b2_qty > 0 else False
        approve_sell = True if db_shares > 0 else False

        if st.button("오늘의 주문 전송", key=f"send_btn_{p_id}", type="primary", use_container_width=True):
            time.sleep(1.0)
            success_orders = 0
            fail_orders = 0
            messages = []
            order_data_log = [
                {"구분": "절반 매수 (평단가 LOC)", "수량": card_b1_qty, "단가": card_b1_price},
                {"구분": "절반 매수 (고가 LOC)", "수량": card_b2_qty, "단가": card_b2_price}
            ]
            if db_shares > 0:
                order_data_log.append({"구분": "익절 매도", "수량": db_shares, "단가": sell_price})
            
            if approve_buy1 and card_b1_qty > 0:
                success, res = api.place_order(ticker, card_b1_qty, card_b1_price, order_type="34")
                if success:
                    success_orders += 1
                    messages.append(f"✅ 절반 매수 (평단가 LOC) 성공: {card_b1_qty}주 @ ${card_b1_price:.2f}")
                else:
                    fail_orders += 1
                    messages.append(f"❌ 절반 매수 (평단가 LOC): {res}")
                time.sleep(1.0)
                
            if approve_buy2 and card_b2_qty > 0:
                success, res = api.place_order(ticker, card_b2_qty, card_b2_price, order_type="34")
                if success:
                    success_orders += 1
                    messages.append(f"✅ 절반 매수 (고가 LOC) 성공: {card_b2_qty}주 @ ${card_b2_price:.2f}")
                else:
                    fail_orders += 1
                    messages.append(f"❌ 절반 매수 (고가 LOC): {res}")
                time.sleep(1.0)
                
            if approve_sell and db_shares > 0:
                success, res = api.place_order(ticker, -db_shares, sell_price, order_type="00")
                if success:
                    success_orders += 1
                    messages.append(f"✅ 익절 매도 성공: {db_shares}주 @ ${sell_price:.2f}")
                else:
                    fail_orders += 1
                    messages.append(f"❌ 익절 매도: {res}")

            for msg in messages:
                st.write(msg)
            
            if success_orders > 0 and fail_orders == 0:
                st.success(f"🎉 모든 주문이 성공적으로 전송되었습니다!")
                log_entry = {
                    "date": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "env": api.env,
                    "target": ticker,
                    "turn_before": turn_cnt,
                    "turn_after": turn_cnt,
                    "orders": order_data_log
                }
                p.setdefault("history", []).append(log_entry)
                state["projects"][p_id] = p
                db_success, new_sha = db.update_state(state, sha)
                if db_success:
                    st.success("💾 깃허브 DB 업데이트 완료!")
                    time.sleep(2)
                    st.rerun()

        # 계좌 잔고 및 DB 동기화 센터
        st.markdown('<div style="font-size:1.05rem; font-weight:800; color:#ffffff; margin-top:16px; margin-bottom:12px;">실 계좌 정보</div>', unsafe_allow_html=True)
        
        target_holding = None
        for hold in holdings:
            if hold.get("pdno") == ticker or hold.get("pd_no") == ticker:
                target_holding = hold
                break
        actual_shares = float(target_holding.get("allo_qty", target_holding.get("ccld_qty", 0.0))) if target_holding else 0.0
        actual_avg_price = float(target_holding.get("pchs_avg_pric", 0.0)) if target_holding else 0.0

        sync_html = f'''
        <div class="summary-grid" style="grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 15px;">
            <div class="summary-item">
                <div class="summary-label">외화 예수금</div>
                <div class="summary-val" style="font-size:1.0rem;">${usd_cash_val:,.2f}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">원화 예수금</div>
                <div class="summary-val" style="font-size:1.0rem;">{krw_cash_val:,.0f} 원</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">{ticker} 평단</div>
                <div class="summary-val" style="font-size:1.0rem;">${actual_avg_price:.2f}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">{ticker} 수량</div>
                <div class="summary-val" style="font-size:1.0rem;">{actual_shares} 주</div>
            </div>
        </div>
        '''
        st.markdown(sync_html, unsafe_allow_html=True)

        if st.button(f"DB를 실제 계좌 기준({ticker})으로 동기화", key=f"sync_btn_{p_id}", use_container_width=True):
            p["total_shares"] = actual_shares
            p["avg_price"] = actual_avg_price
            p["total_spent"] = actual_shares * actual_avg_price
            
            splits_val = float(p.get("splits", 40.0))
            if splits_val > 0:
                base_daily_budget = p.get("total_budget", 0.0) / splits_val
                if base_daily_budget > 0:
                    p["turn"] = round((p["total_spent"] / base_daily_budget) * 2) / 2
                else:
                    p["turn"] = 0.0
            else:
                p["turn"] = 0.0
            if actual_shares == 0:
                p["turn"] = 0
            
            state["projects"][p_id] = p
            db.update_state(state, sha)
            st.success("동기화 완료!")
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True) # pro-card closing tag
"""

# Replace in content
content = content[:match.start()] + new_card_body

with open("app.py", "w") as f:
    f.write(content)

print("Patch applied successfully.")
