import streamlit as st
import pandas as pd
import os
import math
import time
from dotenv import load_dotenv
from github_db import GitHubDB
from kis_api import KISApi

# 페이지 기본 설정
st.set_page_config(
    page_title="루프 4.0 무한매수법 봇",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS
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
    
    .title-gradient {
        background: linear-gradient(to right, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.2rem;
        margin-bottom: 5px;
    }
    
    .warning-box {
        background-color: rgba(245, 158, 11, 0.1);
        border-left: 5px solid #f59e0b;
        color: #fef3c7;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    
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

# DB 및 API 초기화
if "github_db" not in st.session_state:
    st.session_state.github_db = GitHubDB()
if "kis_api" not in st.session_state:
    st.session_state.kis_api = KISApi()

db = st.session_state.github_db
api = st.session_state.kis_api

raw_state, sha = db.get_state()

# ------------------------------------------
# 다중 프로젝트 마이그레이션 & 정규화 함수
# ------------------------------------------
def normalize_state(s):
    if not isinstance(s, dict):
        s = {}
    
    # 깃허브 DB가 단일 프로젝트 구조(구 버전)일 경우 다중 프로젝트 구조로 변환
    if "projects" not in s:
        old_target = s.get("target_etf", "TQQQ")
        if old_target not in ["TQQQ", "SOXL"]:
            old_target = "TQQQ"
        
        legacy_proj = {
            "target_etf": old_target,
            "total_budget": float(s.get("total_budget", 10000.0)),
            "splits": int(s.get("splits", 40)),
            "turn": int(s.get("turn", 0)),
            "avg_price": float(s.get("avg_price", 0.0)),
            "total_shares": float(s.get("total_shares", 0.0)),
            "total_spent": float(s.get("total_spent", 0.0)),
            "status": s.get("status", "BUYING"),
            "history": s.get("history", [])
        }
        
        other_target = "SOXL" if old_target == "TQQQ" else "TQQQ"
        other_proj = {
            "target_etf": other_target,
            "total_budget": 10000.0,
            "splits": 40,
            "turn": 0,
            "avg_price": 0.0,
            "total_shares": 0.0,
            "total_spent": 0.0,
            "status": "BUYING",
            "history": []
        }
        
        s = {
            "active_project": old_target,
            "projects": {
                old_target: legacy_proj,
                other_target: other_proj
            },
            "app_password": s.get("app_password", "0000")
        }
    else:
        # TQQQ / SOXL 필수 존재 보장
        if "TQQQ" not in s["projects"]:
            s["projects"]["TQQQ"] = {
                "target_etf": "TQQQ", "total_budget": 10000.0, "splits": 40,
                "turn": 0, "avg_price": 0.0, "total_shares": 0.0, "total_spent": 0.0,
                "status": "BUYING", "history": []
            }
        if "SOXL" not in s["projects"]:
            s["projects"]["SOXL"] = {
                "target_etf": "SOXL", "total_budget": 10000.0, "splits": 40,
                "turn": 0, "avg_price": 0.0, "total_shares": 0.0, "total_spent": 0.0,
                "status": "BUYING", "history": []
            }
        if s.get("active_project") not in ["TQQQ", "SOXL"]:
            s["active_project"] = "TQQQ"
            
    return s

state = normalize_state(raw_state)

# ==========================================
# 🔒 보안 비밀번호 인증 & 자동 동기화
# ==========================================
env_pwd = os.getenv("APP_PASSWORD")
if env_pwd and state.get("app_password") != env_pwd:
    state["app_password"] = env_pwd
    db.update_state(state, sha)

APP_PASSWORD = state.get("app_password") or env_pwd or "0000"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown('<div class="title-gradient">🔒 루프 4.0 봇 인증</div>', unsafe_allow_html=True)
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

# 타이틀 표시
st.markdown('<div class="title-gradient">📈 루프 무한매수법 V4.0 자동매매</div>', unsafe_allow_html=True)
st.markdown('<p style="color: #94a3b8; margin-bottom: 20px;">라오어 무한매수법 4.0 전용 프로젝트 관리 및 한국투자증권 자동 예약주문 대시보드</p>', unsafe_allow_html=True)

# ==========================================
# 사이드바 설정 (프로젝트 선택 & 생성)
# ==========================================
with st.sidebar:
    st.markdown("### ⚙️ 시스템 & 프로젝트 설정")
    
    # 1. 투자 환경 선택
    env_option = st.selectbox(
        "실행 환경 선택",
        ["모의투자 (Mock)", "실전투자 (Real)"],
        index=0 if os.getenv("KIS_ENVIRONMENT", "mock") == "mock" else 1
    )
    new_env = "real" if "Real" in env_option else "mock"
    if api.env != new_env:
        os.environ["KIS_ENVIRONMENT"] = new_env
        st.session_state.kis_api = KISApi()
        api = st.session_state.kis_api
        st.success(f"환경이 {env_option}로 변경되었습니다.")
        
    st.markdown("---")
    st.markdown("### 📂 활성 프로젝트 선택")
    
    active_proj_key = state.get("active_project", "TQQQ")
    selected_active = st.selectbox(
        "현재 조회/매매할 프로젝트",
        ["TQQQ", "SOXL"],
        index=0 if active_proj_key == "TQQQ" else 1
    )
    
    if selected_active != active_proj_key:
        state["active_project"] = selected_active
        db.update_state(state, sha)
        st.success(f"활성 프로젝트가 {selected_active}(으)로 변경되었습니다.")
        st.rerun()

    st.markdown("---")
    with st.expander("➕ 새 V4.0 프로젝트 생성 / 초기화"):
        st.write("새 무한매수 4.0 프로젝트를 시작하거나 예산을 재설정합니다.")
        new_proj_ticker = st.selectbox("종목 선택 (TQQQ / SOXL)", ["TQQQ", "SOXL"], key="new_proj_ticker")
        new_proj_budget = st.number_input("총 투자 예산 ($USD)", min_value=100.0, value=10000.0, step=500.0, key="new_proj_budget")
        new_proj_splits = st.number_input("분할 회차 (Splits)", min_value=10, max_value=60, value=40, key="new_proj_splits")
        
        if st.button("🚀 프로젝트 시작 및 깃허브 DB 적용", type="primary"):
            state["projects"][new_proj_ticker] = {
                "target_etf": new_proj_ticker,
                "total_budget": float(new_proj_budget),
                "splits": int(new_proj_splits),
                "turn": 0,
                "avg_price": 0.0,
                "total_shares": 0.0,
                "total_spent": 0.0,
                "status": "BUYING",
                "history": []
            }
            state["active_project"] = new_proj_ticker
            success, new_sha = db.update_state(state, sha)
            if success:
                st.success(f"🎉 {new_proj_ticker} 프로젝트가 성공적으로 생성을 완료하고 시작되었습니다!")
                time.sleep(1)
                st.rerun()

    st.markdown("---")
    st.markdown("### 💾 GitHub DB 연결 상태")
    st.text(f"Repo: {db.repo}")
    st.text(f"Path: {db.file_path}")
    if st.button("🔄 GitHub DB 다시 불러오기"):
        st.cache_data.clear()
        st.rerun()

# ==========================================
# 활성 프로젝트 데이터 및 API 조회
# ==========================================
active_key = state.get("active_project", "TQQQ")
project_data = state["projects"][active_key]
target_etf = project_data["target_etf"]

with st.spinner(f"{target_etf} 프로젝트 및 계좌 잔고 로딩 중..."):
    # 실시간 시세 조회
    try:
        current_price = api.get_current_price(target_etf)
    except Exception as e:
        current_price = 0.0
        st.sidebar.error(f"시세 조회 실패: {e}")
        
    # 잔고 및 예수금 조회
    try:
        holdings, usd_cash, account_summary = api.get_balance()
        target_holding = None
        for hold in holdings:
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
db_shares = float(project_data.get("total_shares", 0.0))
db_avg_price = float(project_data.get("avg_price", 0.0))

is_synced = (db_shares == actual_shares) and (abs(db_avg_price - actual_avg_price) < 0.01)

if is_synced:
    st.markdown(f'<div class="success-box">✅ <b>일치 완료:</b> [{target_etf} 프로젝트] DB와 실제 한국투자증권 계좌 잔고가 일치합니다.</div>', unsafe_allow_html=True)
else:
    st.markdown(f'''
    <div class="warning-box">
        ⚠️ <b>상태 불일치 감지:</b> [{target_etf} 프로젝트] DB와 실제 한투 계좌 정보가 다릅니다.<br>
        • DB: {db_shares}주 (평단 ${db_avg_price:.2f}) | • 실제 계좌: {actual_shares}주 (평단 ${actual_avg_price:.2f})
    </div>
    ''', unsafe_allow_html=True)
    
    if st.button(f"🛠️ DB를 실제 한투 계좌 기준({target_etf})으로 동기화"):
        project_data["total_shares"] = actual_shares
        project_data["avg_price"] = actual_avg_price
        project_data["total_spent"] = actual_shares * actual_avg_price
        if actual_shares == 0:
            project_data["turn"] = 0
            project_data["status"] = "BUYING"
            
        state["projects"][target_etf] = project_data
        success, new_sha = db.update_state(state, sha)
        if success:
            st.success("동기화가 완료되었습니다! 페이지를 새로고침합니다.")
            time.sleep(1)
            st.rerun()

# ==========================================
# 2. 프로젝트 및 계좌 대시보드
# ==========================================
col1, col2 = st.columns(2)

with col1:
    st.markdown(f'<div class="card"><div class="card-title">📁 [{target_etf}] 루프 V4.0 프로젝트 상태</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("진행 회차 (T)", f"{project_data.get('turn', 0)} / {project_data.get('splits', 40)} 회")
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
    with st.expander("💼 계좌 전체 보유 종목 보기"):
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

# 실시간 시세 및 손익 표시
st.markdown('<div class="card"><div class="card-title">📊 실시간 시장 시세 및 평가 손익</div>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
c1.metric(f"{target_etf} 현재가", f"${current_price:.2f}")

total_spent = float(project_data.get("total_spent", 0.0))
valuation = actual_shares * current_price
profit_usd = valuation - total_spent
profit_rt = (profit_usd / total_spent * 100) if total_spent > 0 else 0.0

c2.metric("총 매입금액", f"${total_spent:.2f}")
c3.metric("평가금액", f"${valuation:.2f}")
c4.metric("평가손익 (수익률)", f"${profit_usd:.2f} ({profit_rt:.2f}%)", 
          delta=f"{profit_rt:.2f}%" if profit_usd >= 0 else f"{profit_rt:.2f}%")
st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 3. 무한매수법 V4.0 매매 가이드라인
# ==========================================
st.markdown(f'<div class="card"><div class="card-title">📝 [{target_etf}] 루프 V4.0 오늘의 매매 가이드라인</div>', unsafe_allow_html=True)

turn = int(project_data.get("turn", 0))
splits = int(project_data.get("splits", 40))
total_budget = float(project_data.get("total_budget", 10000.0))

if turn >= splits:
    st.warning("⚠️ 이미 40회차 매수를 완료하였습니다. 추가 예수금을 투입하여 연장하거나 리버스를 고려해 주세요.")
    daily_buy_budget = 0.0
else:
    remaining_budget = total_budget - total_spent
    daily_buy_budget = remaining_budget / (splits - turn)

st.write(f"👉 **총 예산**: **${total_budget:,.2f}** | **오늘의 1회 매수 설정 금액**: **${daily_buy_budget:.2f}** (남은 예산 ${remaining_budget:.2f}의 1/{splits - turn})")

# 매수/매도 주문 계산
buy1_price = db_avg_price if db_avg_price > 0 else current_price
buy1_qty = math.floor((daily_buy_budget * 0.5) / buy1_price) if buy1_price > 0 else 0

buy2_price = current_price * 1.10
buy2_qty = math.floor((daily_buy_budget * 0.5) / buy2_price) if buy2_price > 0 else 0

sell_price = db_avg_price * 1.10
sell_qty = db_shares

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

st.table(pd.DataFrame(order_data))
st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 4. 1-클릭 주문 승인 및 한투 API 전송
# ==========================================
st.markdown('<div class="card"><div class="card-title">⚡ 주문 검토 및 최종 승인</div>', unsafe_allow_html=True)
st.write("주문할 내역을 선택하고 승인 버튼을 누르면 한국투자증권으로 예약 주문이 즉시 전송됩니다.")

col_b1, col_b2, col_s = st.columns(3)
with col_b1:
    approve_buy1 = st.checkbox("주문 1 승인 (평단 LOC 매수)", value=True if buy1_qty > 0 else False, disabled=buy1_qty == 0)
with col_b2:
    approve_buy2 = st.checkbox("주문 2 승인 (고가 LOC 매수)", value=True if buy2_qty > 0 else False, disabled=buy2_qty == 0)
with col_s:
    approve_sell = st.checkbox("주문 3 승인 (익절 지정가 매도)", value=True if sell_qty > 0 else False, disabled=sell_qty == 0)

if st.button(f"🚀 [{target_etf}] 주문들을 한국투자증권으로 전송 및 승인", type="primary"):
    success_orders = 0
    fail_orders = 0
    messages = []
    
    if approve_buy1 and buy1_qty > 0:
        success, res = api.place_order(target_etf, buy1_qty, buy1_price, order_type="34")
        if success:
            success_orders += 1
            messages.append(f"✅ 매수 1순위(평단 LOC) 성공: {buy1_qty}주 @ ${buy1_price:.2f} (접수번호: {res.get('ODNO', 'N/A')})")
        else:
            fail_orders += 1
            messages.append(f"❌ 매수 1순위 실패: {res}")
            
    if approve_buy2 and buy2_qty > 0:
        success, res = api.place_order(target_etf, buy2_qty, buy2_price, order_type="34")
        if success:
            success_orders += 1
            messages.append(f"✅ 매수 2순위(고가 LOC) 성공: {buy2_qty}주 @ ${buy2_price:.2f} (접수번호: {res.get('ODNO', 'N/A')})")
        else:
            fail_orders += 1
            messages.append(f"❌ 매수 2순위 실패: {res}")
            
    if approve_sell and sell_qty > 0:
        success, res = api.place_order(target_etf, -sell_qty, sell_price, order_type="00")
        if success:
            success_orders += 1
            messages.append(f"✅ 익절 지정가 매도 주문 성공: {sell_qty}주 @ ${sell_price:.2f} (접수번호: {res.get('ODNO', 'N/A')})")
        else:
            fail_orders += 1
            messages.append(f"❌ 익절 매도 실패: {res}")

    for msg in messages:
        st.write(msg)
        
    if success_orders > 0 and fail_orders == 0:
        st.success(f"🎉 모든 주문이 성공적으로 접수되었습니다! [{target_etf}] 회차 정보를 업데이트합니다.")
        if approve_buy1 or approve_buy2:
            project_data["turn"] = turn + 1
            
        log_entry = {
            "date": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            "env": api.env,
            "target": target_etf,
            "turn_before": turn,
            "turn_after": project_data["turn"],
            "orders": order_data
        }
        project_data.setdefault("history", []).append(log_entry)
        state["projects"][target_etf] = project_data
        
        db_success, new_sha = db.update_state(state, sha)
        if db_success:
            st.success("💾 깃허브 DB 업데이트 완료! 3초 후 페이지가 갱신됩니다.")
            time.sleep(3)
            st.rerun()
    elif fail_orders > 0:
        st.error("일부 주문이 실패하였습니다. 계좌 또는 API 설정을 확인해 주세요.")

st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 5. 수동 상태 조절 (비상용)
# ==========================================
with st.expander(f"🛠️ [{target_etf}] 프로젝트 수동 상태 조정 (비상용)"):
    st.write("깃허브 DB의 프로젝트 파라미터를 강제 변경합니다.")
    
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        edit_turn = st.number_input("회차 (T) 수정", min_value=0, max_value=splits, value=turn)
        edit_budget = st.number_input("총 예산 (USD) 수정", min_value=0.0, value=total_budget)
    with col_s2:
        edit_shares = st.number_input("보유 수량 수정", min_value=0.0, value=db_shares)
        edit_avg_price = st.number_input("평균 매수가 수정", min_value=0.0, value=db_avg_price)
    with col_s3:
        edit_splits = st.number_input("최대 분할수 (Splits)", min_value=1, value=splits)
        edit_status = st.selectbox("진행 모드", ["BUYING", "REVERSE", "FINISHED"], index=["BUYING", "REVERSE", "FINISHED"].index(project_data.get("status", "BUYING")))

    if st.button(f"💾 [{target_etf}] 수동 변경사항 깃허브 DB 저장"):
        project_data["turn"] = int(edit_turn)
        project_data["total_budget"] = edit_budget
        project_data["total_shares"] = edit_shares
        project_data["avg_price"] = edit_avg_price
        project_data["splits"] = int(edit_splits)
        project_data["status"] = edit_status
        project_data["total_spent"] = edit_shares * edit_avg_price
        
        state["projects"][target_etf] = project_data
        success, new_sha = db.update_state(state, sha)
        if success:
            st.success("수동 변경사항이 정상 적용되었습니다.")
            time.sleep(1)
            st.rerun()
