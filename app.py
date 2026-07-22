import streamlit as st
import pandas as pd
import os
import math
from dotenv import load_dotenv
from github_db import GitHubDB
from kis_api import KISApi

# 페이지 기본 설정
st.set_page_config(
    page_title="무한매수법 4.0 봇",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS 적용 (프리미엄 디자인)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #f1f5f9;
    }
    
    /* 카드 디자인 */
    .card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    }
    
    .card-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #94a3b8;
        margin-bottom: 12px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* 그라데이션 타이틀 */
    .title-gradient {
        background: linear-gradient(to right, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.2rem;
        margin-bottom: 5px;
    }
    
    /* 경고창 스타일 */
    .warning-box {
        background-color: rgba(245, 158, 11, 0.1);
        border-left: 5px solid #f59e0b;
        color: #fef3c7;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    
    /* 일치 성공창 스타일 */
    .success-box {
        background-color: rgba(16, 185, 129, 0.1);
        border-left: 5px solid #10b981;
        color: #d1fae5;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# 환경 변수 로드 (수정사항 즉시 반영)
load_dotenv(override=True)


# 세션 상태 DB 초기화
if "github_db" not in st.session_state:
    st.session_state.github_db = GitHubDB()

db = st.session_state.github_db

# 깃허브 DB에서 상태 정보 조회
state, sha = db.get_state()

# ==========================================
# 🔒 보안 비밀번호 인증 & 자동 동기화 레이어
# ==========================================
# Mac 로컬 .env 에 APP_PASSWORD가 설정된 경우 GitHub DB로 자동 동기화
env_pwd = os.getenv("APP_PASSWORD")
if env_pwd and state.get("app_password") != env_pwd:
    state["app_password"] = env_pwd
    db.update_state(state, sha)

# 최신 비밀번호 결정 (GitHub DB -> .env -> 기본값 7777)
APP_PASSWORD = state.get("app_password") or env_pwd or "7777"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown('<div class="title-gradient">🔒 무한매수법 봇 인증</div>', unsafe_allow_html=True)
    st.markdown('<p style="color: #94a3b8;">계좌 정보 및 매매 승인을 위해 비밀번호를 입력해주세요.</p>', unsafe_allow_html=True)
    
    with st.form("auth_form"):
        password_input = st.text_input("접속 비밀번호 (PIN)", type="password", placeholder="비밀번호 입력")
        submit_btn = st.form_submit_button("🔓 로그인")
        
        if submit_btn:
            if password_input == APP_PASSWORD:
                st.session_state.authenticated = True
                st.success("인증 성공! 대시보드로 이동합니다.")
                st.rerun()
            else:
                st.error("❌ 비밀번호가 올바르지 않습니다.")
    st.stop()

if "kis_api" not in st.session_state:
    st.session_state.kis_api = KISApi()

api = st.session_state.kis_api


# 타이틀 표시
st.markdown('<div class="title-gradient">📈 무한매수법 V4.0 반자동 매매</div>', unsafe_allow_html=True)
st.markdown('<p style="color: #94a3b8; margin-bottom: 30px;">한국투자증권 API와 GitHub DB를 연동한 분할매매 제어 대시보드</p>', unsafe_allow_html=True)

# ==========================================
# 사이드바 설정
# ==========================================
with st.sidebar:
    st.markdown("### ⚙️ 시스템 설정")
    
    # 투자 환경 설정
    env_option = st.selectbox(
        "실행 환경 선택",
        ["모의투자 (Mock)", "실전투자 (Real)"],
        index=0 if os.getenv("KIS_ENVIRONMENT", "mock") == "mock" else 1
    )
    
    # 환경 변수 동적 수정 적용
    new_env = "real" if "Real" in env_option else "mock"
    if api.env != new_env:
        os.environ["KIS_ENVIRONMENT"] = new_env
        st.session_state.kis_api = KISApi()
        api = st.session_state.kis_api
        st.success(f"환경이 {env_option}로 변경되었습니다.")
    
    st.markdown("---")
    st.markdown("### 🎯 매매 대상 종목 선택")
    current_target = state.get("target_etf", "TQQQ")
    etf_list = ["TQQQ", "SOXL", "BULZ", "TECL", "UPRO", "LABU", "TSLL", "NVDL"]
    selected_etf = st.selectbox(
        "대상 ETF 선택",
        etf_list,
        index=etf_list.index(current_target) if current_target in etf_list else 0
    )
    if selected_etf != current_target:
        state["target_etf"] = selected_etf
        # 종목 변경 시 수량/평단가 자동 동기화 준비
        success, new_sha = db.update_state(state, sha)
        if success:
            st.success(f"매매 종목이 {selected_etf}(으)로 변경되었습니다!")
            st.rerun()

    st.markdown("---")
    st.markdown("### 💾 GitHub DB 연결 상태")

    st.text(f"Repo: {db.repo}")
    st.text(f"Path: {db.file_path}")
    
    if st.button("🔄 GitHub DB 다시 불러오기"):
        st.cache_data.clear()
        st.rerun()


# ==========================================
# 데이터 로드 (GitHub DB 및 KIS API)
# ==========================================
with st.spinner("GitHub DB 및 계좌 정보 불러오는 중..."):
    # 1. GitHub에서 상태 로드
    state, sha = db.get_state()
    target_etf = state.get("target_etf", "TQQQ")
    
    # 2. 한투 API에서 실시간 가격 조회
    try:
        current_price = api.get_current_price(target_etf)
    except Exception as e:
        current_price = 0.0
        st.sidebar.error(f"실시간 가격 조회 실패: {e}")
        
    # 3. 한투 API에서 실제 잔고 및 예수금 조회
    try:
        holdings, usd_cash, account_summary = api.get_balance()
        
        # 특정 종목 잔고 추출
        target_holding = None
        for hold in holdings:
            # KIS API에서 종목코드는 pdno 또는 pd_no에 있음
            if hold.get("pdno") == target_etf or hold.get("pd_no") == target_etf:
                target_holding = hold
                break
                
        actual_shares = float(target_holding.get("allo_qty", target_holding.get("ccld_qty", 0.0))) if target_holding else 0.0
        actual_avg_price = float(target_holding.get("pchs_avg_pric", 0.0)) if target_holding else 0.0
    except Exception as e:
        actual_shares = 0.0
        actual_avg_price = 0.0
        usd_cash = 0.0
        holdings = []
        account_summary = {}
        st.sidebar.error(f"계좌 잔고 조회 실패: {e}")

# ==========================================
# 1. 상태 비교 및 싱크 알림
# ==========================================
db_shares = state.get("total_shares", 0.0)
db_avg_price = state.get("avg_price", 0.0)

is_synced = (db_shares == actual_shares) and (abs(db_avg_price - actual_avg_price) < 0.01)

if is_synced:
    st.markdown(f'<div class="success-box">✅ <b>일치 완료:</b> 깃허브 DB와 실제 한국투자증권 계좌의 <b>{target_etf}</b> 잔고 정보가 완벽히 일치합니다.</div>', unsafe_allow_html=True)
else:
    st.markdown(f'''
    <div class="warning-box">
        ⚠️ <b>상태 불일치 감지:</b> 깃허브 DB와 실제 한투 계좌의 <b>{target_etf}</b> 정보가 다릅니다.<br>
        • DB: {db_shares}주 (평단 ${db_avg_price:.2f}) | • 실제 계좌: {actual_shares}주 (평단 ${actual_avg_price:.2f})
    </div>
    ''', unsafe_allow_html=True)
    
    # 싱크 버튼 제공
    if st.button(f"🛠️ 깃허브 DB를 실제 계좌 기준({target_etf})으로 동기화"):
        state["total_shares"] = actual_shares
        state["avg_price"] = actual_avg_price
        state["total_spent"] = actual_shares * actual_avg_price
        # 수량이 0인 경우 회차 리셋
        if actual_shares == 0:
            state["turn"] = 0
            state["status"] = "BUYING"
            
        success, new_sha = db.update_state(state, sha)
        if success:
            st.success("동기화가 완료되었습니다! 페이지를 새로고침합니다.")
            time.sleep(1)
            st.rerun()

# ==========================================
# 2. 계좌 현황 대시보드
# ==========================================
col1, col2 = st.columns(2)

with col1:
    st.markdown(f'<div class="card"><div class="card-title">💾 깃허브 DB 상태 ({target_etf})</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("현재 회차 (T)", f"{state.get('turn', 0)} / {state.get('splits', 40)} 회")
    c2.metric("DB 평균 매수가", f"${db_avg_price:.2f}")
    c3.metric("DB 보유 수량", f"{db_shares} 주")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card"><div class="card-title">🏦 한국투자증권 계좌 현황 & 예수금</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("사용 가능 예수금 (USD)", f"${usd_cash:,.2f}")
    c2.metric(f"실제 {target_etf} 수량", f"{actual_shares} 주")
    c3.metric(f"실제 {target_etf} 평단가", f"${actual_avg_price:.2f}")
    st.markdown('</div>', unsafe_allow_html=True)

if holdings:
    with st.expander("💼 계좌 내 전체 보유 종목 상세보기"):
        h_list = []
        for item in holdings:
            h_list.append({
                "종목코드": item.get("pdno", item.get("pd_no", "")),
                "종목명": item.get("prdt_name", item.get("ovrs_item_name", item.get("pdno", ""))),
                "보유수량": f"{float(item.get('allo_qty', item.get('ccld_qty', 0))):g} 주",
                "매입평단가": f"${float(item.get('pchs_avg_pric', 0)):.2f}",
                "평가금액": f"${float(item.get('ovrs_stck_evlu_amt', 0)):,.2f}"
            })
        st.table(pd.DataFrame(h_list))



# 실시간 시세 메트릭 표시
st.markdown('<div class="card"><div class="card-title">📊 실시간 시장 시세</div>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
c1.metric(f"{target_etf} 현재가", f"${current_price:.2f}")

# 평가 손익 계산
total_spent = state.get("total_spent", 0.0)
valuation = actual_shares * current_price
profit_usd = valuation - total_spent
profit_rt = (profit_usd / total_spent * 100) if total_spent > 0 else 0.0

c2.metric("총 매입금액", f"${total_spent:.2f}")
c3.metric("평가금액", f"${valuation:.2f}")
c4.metric("평가손익 (수익률)", f"${profit_usd:.2f} ({profit_rt:.2f}%)", 
          delta=f"{profit_rt:.2f}%" if profit_usd >= 0 else f"{profit_rt:.2f}%")
st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 3. 오늘 예정된 매매 주문 계산
# ==========================================
st.markdown('<div class="card"><div class="card-title">📝 무한매수법 V4.0 오늘의 매매 가이드라인</div>', unsafe_allow_html=True)

turn = state.get("turn", 0)
splits = state.get("splits", 40)
total_budget = state.get("total_budget", 10000.0)

if turn >= splits:
    st.warning("⚠️ 이미 40회차 매수를 완료하였습니다. 추가 예수금을 투입하여 연장하거나, 50% 강제 손절 후 리셋(리버스 모드 진입)을 고려해 주세요.")
    daily_buy_budget = 0.0
else:
    # V4.0 1회 매수금 = (전체 예산 - 현재까지 쓴 금액) / (전체 분할수 - 현재 회차)
    remaining_budget = total_budget - total_spent
    daily_buy_budget = remaining_budget / (splits - turn)

st.write(f"👉 **오늘의 1회 매수 설정 금액**: **${daily_buy_budget:.2f}** (남은 예산 ${remaining_budget:.2f}의 1/{splits - turn} 분량)")

# 매수 주문 가격 및 수량 계산
# 주문 1: 평단가 LOC 매수 (0.5회분)
buy1_price = db_avg_price if db_avg_price > 0 else current_price
buy1_qty = math.floor((daily_buy_budget * 0.5) / buy1_price) if buy1_price > 0 else 0

# 주문 2: 현재가 + 10% LOC 매수 (0.5회분 - 무조건 1회 체결을 보장하기 위함)
buy2_price = current_price * 1.10
buy2_qty = math.floor((daily_buy_budget * 0.5) / buy2_price) if buy2_price > 0 else 0

# 주문 3: 익절 지정가 매도 (+10%)
sell_price = db_avg_price * 1.10
sell_qty = db_shares

# 표로 표시하기 위한 데이터프레임 빌드
order_data = [
    {
        "구분": "매수 1순위 (평단 LOC)",
        "종목": target_etf,
        "수량": f"{buy1_qty} 주",
        "설정단가": f"${buy1_price:.2f}",
        "예상금액": f"${(buy1_qty * buy1_price):.2f}",
        "주문타입": "LOC 매수 (34)"
    },
    {
        "구분": "매수 2순위 (고가 LOC)",
        "종목": target_etf,
        "수량": f"{buy2_qty} 주",
        "설정단가": f"${buy2_price:.2f}",
        "예상금액": f"${(buy2_qty * buy2_price):.2f}",
        "주문타입": "LOC 매수 (34)"
    }
]

if sell_qty > 0:
    order_data.append({
        "구분": "매도 (익절 지정가)",
        "종목": target_etf,
        "수량": f"{sell_qty} 주",
        "설정단가": f"${sell_price:.2f}",
        "예상금액": f"${(sell_qty * sell_price):.2f}",
        "주문타입": "지정가 매도 (00)"
    })

df = pd.DataFrame(order_data)
st.table(df)
st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 4. 주문 승인 및 실행 기능
# ==========================================
st.markdown('<div class="card"><div class="card-title">⚡ 주문 검토 및 최종 승인</div>', unsafe_allow_html=True)

st.write("주문할 내역을 선택하고 승인 버튼을 누르면 한국투자증권에 예약 주문이 실제로 접수됩니다.")

col_b1, col_b2, col_s = st.columns(3)

with col_b1:
    approve_buy1 = st.checkbox("주문 1 승인 (평단 LOC 매수)", value=True if buy1_qty > 0 else False, disabled=buy1_qty == 0)
with col_b2:
    approve_buy2 = st.checkbox("주문 2 승인 (고가 LOC 매수)", value=True if buy2_qty > 0 else False, disabled=buy2_qty == 0)
with col_s:
    approve_sell = st.checkbox("주문 3 승인 (익절 지정가 매도)", value=True if sell_qty > 0 else False, disabled=sell_qty == 0)

if st.button("🚀 위 체크된 주문들을 한국투자증권으로 전송 및 승인", type="primary"):
    success_orders = 0
    fail_orders = 0
    messages = []
    
    # 주문 1 실행
    if approve_buy1 and buy1_qty > 0:
        success, res = api.place_order(target_etf, buy1_qty, buy1_price, order_type="34")
        if success:
            success_orders += 1
            messages.append(f"✅ 매수 1순위(평단 LOC) 성공: {buy1_qty}주 @ ${buy1_price:.2f} (접수번호: {res.get('ODNO', 'N/A')})")
        else:
            fail_orders += 1
            messages.append(f"❌ 매수 1순위 실패: {res}")
            
    # 주문 2 실행
    if approve_buy2 and buy2_qty > 0:
        success, res = api.place_order(target_etf, buy2_qty, buy2_price, order_type="34")
        if success:
            success_orders += 1
            messages.append(f"✅ 매수 2순위(고가 LOC) 성공: {buy2_qty}주 @ ${buy2_price:.2f} (접수번호: {res.get('ODNO', 'N/A')})")
        else:
            fail_orders += 1
            messages.append(f"❌ 매수 2순위 실패: {res}")
            
    # 주문 3 실행
    if approve_sell and sell_qty > 0:
        success, res = api.place_order(target_etf, -sell_qty, sell_price, order_type="00")
        if success:
            success_orders += 1
            messages.append(f"✅ 익절 지정가 매도 주문 성공: {sell_qty}주 @ ${sell_price:.2f} (접수번호: {res.get('ODNO', 'N/A')})")
        else:
            fail_orders += 1
            messages.append(f"❌ 익절 매도 실패: {res}")

    # 결과 분석 및 DB 업데이트
    for msg in messages:
        st.write(msg)
        
    if success_orders > 0 and fail_orders == 0:
        st.success("🎉 모든 주문이 성공적으로 들어갔습니다! 깃허브 DB 회차 정보를 업데이트합니다.")
        
        # 매수 주문이 승인된 경우에만 회차(T)를 1 증가시킵니다.
        if approve_buy1 or approve_buy2:
            state["turn"] = turn + 1
            
        # 주문 로그를 기록합니다.
        log_entry = {
            "date": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            "env": api.env,
            "turn_before": turn,
            "turn_after": state["turn"],
            "orders": order_data
        }
        state.setdefault("history", []).append(log_entry)
        
        # 깃허브에 상태 저장
        db_success, new_sha = db.update_state(state, sha)
        if db_success:
            st.success("💾 깃허브 DB 업데이트 완료! 3초 후 페이지가 갱신됩니다.")
            time.sleep(3)
            st.rerun()
    elif fail_orders > 0:
        st.error("일부 주문이 실패하였습니다. 한투 계좌 또는 API 설정을 점검해 주세요. DB 상태는 변경되지 않았습니다.")

st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 5. 수동 상태 조절 (비상용 개발자 모드)
# ==========================================
with st.expander("🛠️ 수동 상태 조정 및 디버깅 (비상용)"):
    st.write("깃허브 DB의 무한매수 진행 수치를 수동으로 강제 변경하고 저장할 수 있습니다.")
    
    col_s1, col_s2, col_s3 = st.columns(3)
    
    with col_s1:
        edit_turn = st.number_input("회차 (T) 수정", min_value=0, max_value=splits, value=turn)
        edit_budget = st.number_input("총 예산 (USD) 수정", min_value=0.0, value=total_budget)
    with col_s2:
        edit_shares = st.number_input("보유 수량 수정", min_value=0.0, value=db_shares)
        edit_avg_price = st.number_input("평균 매수가 수정", min_value=0.0, value=db_avg_price)
    with col_s3:
        edit_splits = st.number_input("최대 분할수 (Splits)", min_value=1, value=splits)
        edit_status = st.selectbox("진행 모드", ["BUYING", "REVERSE", "FINISHED"], index=["BUYING", "REVERSE", "FINISHED"].index(state.get("status", "BUYING")))

    if st.button("💾 변경사항을 깃허브 DB에 강제 덮어쓰기"):
        state["turn"] = int(edit_turn)
        state["total_budget"] = edit_budget
        state["total_shares"] = edit_shares
        state["avg_price"] = edit_avg_price
        state["splits"] = int(edit_splits)
        state["status"] = edit_status
        state["total_spent"] = edit_shares * edit_avg_price
        
        success, new_sha = db.update_state(state, sha)
        if success:
            st.success("성공적으로 수동 변경사항이 적용되었습니다! 리프레시합니다.")
            time.sleep(1)
            st.rerun()
