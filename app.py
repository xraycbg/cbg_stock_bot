import streamlit as st
import pandas as pd
import os
import math
import time
from dotenv import load_dotenv
from github_db import GitHubDB
from kis_api import KISApi

# 페이지 기본 설정 (아이폰 및 모바일 뷰포트 최적화)
st.set_page_config(
    page_title="루프 4.0 무한매수법 봇",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ------------------------------------------
# 루프(Roop) 앱 100% 동일 픽셀-퍼펙트 커스텀 CSS
# ------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&family=Noto+Sans+KR:wght@400;600;700;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', 'Noto Sans KR', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* 루프 앱 배경색: 깊은 밤하늘색/다크 네이비 */
    .stApp {
        background-color: #0b0f19;
        color: #f8fafc;
    }
    
    /* Streamlit 상단 투명화 & 노치 공간 확보 */
    header[data-testid="stHeader"], [data-testid="stHeader"] {
        background-color: transparent !important;
        z-index: 1 !important;
    }
    
    .block-container {
        padding-top: 3.2rem !important;
        padding-bottom: 5rem !important;
        max-width: 580px; /* 모바일 카드 앱에 최적화된 너비 */
        margin: 0 auto;
    }
    
    @media (max-width: 768px) {
        .block-container {
            padding-left: 0.9rem !important;
            padding-right: 0.9rem !important;
            padding-top: 3.5rem !important;
        }
    }
    
    /* 탭 컨트롤러 (무한매수 / VR) */
    .segmented-control {
        background: #141b2d;
        border-radius: 14px;
        padding: 4px;
        display: flex;
        gap: 4px;
        width: fit-content;
    }
    
    .segmented-btn-active {
        background: #252e48;
        color: #ffffff;
        font-weight: 700;
        padding: 8px 20px;
        border-radius: 10px;
        font-size: 0.9rem;
    }
    
    .segmented-btn-inactive {
        color: #64748b;
        font-weight: 600;
        padding: 8px 20px;
        border-radius: 10px;
        font-size: 0.9rem;
    }
    
    /* 새 사이클 퍼플 버튼 */
    .btn-new-cycle {
        background: #4f46e5;
        color: #ffffff;
        border-radius: 20px;
        padding: 8px 16px;
        font-weight: 700;
        font-size: 0.85rem;
        border: none;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
    }
    
    /* 루프 앱 카드 스타일 */
    .roop-card {
        background: #131929;
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 16px;
    }
    
    .roop-card-title {
        font-size: 1.3rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 2px;
    }
    
    .roop-card-sub {
        font-size: 0.85rem;
        color: #64748b;
        font-weight: 600;
        margin-bottom: 16px;
    }
    
    .badge-status {
        background: rgba(16, 185, 129, 0.15);
        color: #10b981;
        font-size: 0.8rem;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 20px;
        float: right;
    }
    
    /* 회차 프로그레스 바 (보라색) */
    .roop-progress-bg {
        background: #1e263d;
        height: 6px;
        border-radius: 6px;
        width: 100%;
        overflow: hidden;
        margin-top: 8px;
    }
    
    .roop-progress-fill {
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%);
        height: 100%;
        border-radius: 6px;
    }
    
    /* 오늘의 주문 2열 카드 (레드 / 블루) */
    .buy-box {
        background: #251217;
        border: 1px solid rgba(239, 68, 68, 0.2);
        border-radius: 18px;
        padding: 16px;
        margin-bottom: 12px;
    }
    
    .sell-box {
        background: #121933;
        border: 1px solid rgba(99, 102, 241, 0.25);
        border-radius: 18px;
        padding: 16px;
        margin-bottom: 12px;
    }
    
    .box-title-buy {
        color: #ef4444;
        font-size: 0.85rem;
        font-weight: 800;
        margin-bottom: 12px;
    }
    
    .box-title-sell {
        color: #818cf8;
        font-size: 0.85rem;
        font-weight: 800;
        margin-bottom: 12px;
    }
    
    .order-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
    }
    
    .price-bold {
        font-size: 1.15rem;
        font-weight: 800;
        color: #ffffff;
    }
    
    .qty-text {
        font-size: 0.9rem;
        color: #94a3b8;
        font-weight: 600;
    }
    
    .tag-red {
        background: rgba(239, 68, 68, 0.25);
        color: #f87171;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 10px;
    }
    
    .tag-purple {
        background: rgba(139, 92, 246, 0.25);
        color: #c084fc;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 10px;
    }
    
    /* 하단 탭 바 스타일 */
    .bottom-nav {
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: #141b2d;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 30px;
        padding: 6px 16px;
        display: flex;
        gap: 16px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
        z-index: 9999;
    }
    
    /* 버튼 둥근 스타일 */
    div.stButton > button {
        border-radius: 14px !important;
        font-weight: 700 !important;
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

# 고유 ID 기반 프로젝트 정규화
def normalize_state(s):
    if not isinstance(s, dict):
        s = {}
    
    if "projects" not in s:
        old_target = s.get("target_etf", "TQQQ")
        if old_target not in ["TQQQ", "SOXL"]:
            old_target = "TQQQ"
            
        p_id = f"proj_{int(time.time())}"
        legacy_proj = {
            "id": p_id,
            "name": f"{old_target} 1차",
            "target_etf": old_target,
            "total_budget": float(s.get("total_budget", 10000.0)),
            "splits": int(s.get("splits", 40)),
            "turn": int(s.get("turn", 0)),
            "avg_price": float(s.get("avg_price", 0.0)),
            "total_shares": float(s.get("total_shares", 0.0)),
            "total_spent": float(s.get("total_spent", 0.0)),
            "status": "진행중",
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "history": s.get("history", [])
        }
        
        s = {
            "active_project_id": p_id,
            "projects": {
                p_id: legacy_proj
            },
            "app_password": s.get("app_password", "0000")
        }
    else:
        new_projects = {}
        old_projects = s.get("projects", {})
        for k, p in old_projects.items():
            if not isinstance(p, dict):
                continue
            p_id = p.get("id", k if k.startswith("proj_") else f"proj_{k}_{int(time.time())}")
            p_name = p.get("name", f"{p.get('target_etf', 'TQQQ')} 프로젝트")
            
            new_projects[p_id] = {
                "id": p_id,
                "name": p_name,
                "target_etf": p.get("target_etf", "TQQQ"),
                "total_budget": float(p.get("total_budget", 10000.0)),
                "splits": int(p.get("splits", 40)),
                "turn": int(p.get("turn", 0)),
                "avg_price": float(p.get("avg_price", 0.0)),
                "total_shares": float(p.get("total_shares", 0.0)),
                "total_spent": float(p.get("total_spent", 0.0)),
                "status": "진행중",
                "created_at": p.get("created_at", time.strftime("%Y-%m-%d %H:%M:%S")),
                "history": p.get("history", [])
            }
            
        s["projects"] = new_projects
        if s.get("active_project_id") not in new_projects:
            s["active_project_id"] = list(new_projects.keys())[0] if new_projects else None
            
    return s

state = normalize_state(raw_state)

# 🔒 보안 비밀번호 인증
env_pwd = os.getenv("APP_PASSWORD")
if env_pwd and state.get("app_password") != env_pwd:
    state["app_password"] = env_pwd
    db.update_state(state, sha)

APP_PASSWORD = state.get("app_password") or env_pwd or "0000"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown('<h2 style="font-weight:800; color:#38bdf8;">🔒 루프 4.0 봇 인증</h2>', unsafe_allow_html=True)
    with st.form("auth_form"):
        password_input = st.text_input("접속 비밀번호 (PIN)", type="password", placeholder="비밀번호 입력")
        submit_btn = st.form_submit_button("🔓 로그인", type="primary", use_container_width=True)
        if submit_btn:
            if password_input == APP_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ 비밀번호가 올바르지 않습니다.")
    st.stop()

# 뷰 모드 관리
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "LIST"

# 사이드바 (설정용)
with st.sidebar:
    st.markdown("### ⚙️ 시스템 설정")
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
    st.markdown("### 💾 GitHub DB 상태")
    st.text(f"Repo: {db.repo}")
    st.text(f"Path: {db.file_path}")
    if st.button("🔄 GitHub DB 다시 불러오기"):
        st.cache_data.clear()
        st.rerun()

# ==========================================
# 루프 앱 상단 헤더 Bar (앱 제목 & + 새 사이클)
# ==========================================
hdr_col1, hdr_col2 = st.columns([3.2, 1.8])

with hdr_col1:
    st.markdown('<div class="title-gradient" style="font-size: 1.45rem !important; font-weight:800; margin:0; line-height: 1.4;">📈 무한매수 v4.0</div>', unsafe_allow_html=True)


with hdr_col2:
    if st.button("➕ 새 사이클", key="top_new_cycle_btn", use_container_width=True):
        st.session_state.view_mode = "CREATE"
        st.rerun()


st.markdown("<br>", unsafe_allow_html=True)

projects_dict = state.get("projects", {})

# ==========================================
# ➕ 새 사이클 생성 화면
# ==========================================
if st.session_state.view_mode == "CREATE" or not projects_dict:
    st.markdown('<div class="roop-card">', unsafe_allow_html=True)
    st.markdown("### 🚀 새 사이클 (프로젝트) 생성")
    
    new_p_ticker = st.selectbox("🎯 매매 종목 선택", ["SOXL", "TQQQ"], key="create_p_ticker")
    existing_count = sum(1 for p in projects_dict.values() if p.get("target_etf") == new_p_ticker)
    recommended_name = f"{new_p_ticker} {existing_count + 1}차"

    with st.form("create_proj_form"):
        new_p_name = st.text_input("프로젝트 이름", value=recommended_name, placeholder=f"예: {recommended_name}")
        new_p_budget = st.number_input("💰 총 투자 예산 ($USD)", min_value=100.0, value=10000.0, step=500.0)
        new_p_splits = st.number_input("⏳ 분할 회차 (Splits)", min_value=10, max_value=60, value=40)
        
        create_submit = st.form_submit_button("✨ 새 사이클 생성 및 매매 시작", type="primary", use_container_width=True)
        
        if create_submit:
            final_name = new_p_name.strip() if new_p_name.strip() else recommended_name
            new_id = f"proj_{int(time.time())}"
            state["projects"][new_id] = {
                "id": new_id,
                "name": final_name,
                "target_etf": new_p_ticker,
                "total_budget": float(new_p_budget),
                "splits": int(new_p_splits),
                "turn": 0,
                "avg_price": 0.0,
                "total_shares": 0.0,
                "total_spent": 0.0,
                "status": "진행중",
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "history": []
            }
            state["active_project_id"] = new_id
            db.update_state(state, sha)
            st.session_state.view_mode = "DETAIL"
            st.success(f"🎉 [{final_name}] 사이클이 생성되었습니다!")
            time.sleep(1)
            st.rerun()

    if projects_dict:
        if st.button("❌ 취소 및 목록으로 돌아가기"):
            st.session_state.view_mode = "LIST"
            st.rerun()
            
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# 📋 VIEW MODE 1: 프로젝트 목록 (LIST)
# ==========================================
if st.session_state.view_mode == "LIST":
    st.markdown('''
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
        <span style="font-weight:700; color:#94a3b8; font-size:0.9rem;">내 사이클 목록</span>
        <span style="font-weight:600; color:#64748b; font-size:0.85rem;">⇅ 정렬</span>
    </div>
    ''', unsafe_allow_html=True)
    
    p_items = list(projects_dict.values())
    for p in p_items:
        p_id = p["id"]
        turn_cnt = int(p.get('turn', 0))
        splits_cnt = int(p.get('splits', 40))
        prog_pct = min(100, int((turn_cnt / splits_cnt) * 100)) if splits_cnt > 0 else 0
        
        card_html = f"""<div class="roop-card">
<span class="badge-status">진행중</span>
<div class="roop-card-title">{p['name']}</div>
<div class="roop-card-sub">{p['target_etf']} · V4.0 · 전반전</div>
<div style="display:flex; justify-content:space-between; font-size:0.85rem; font-weight:700; margin-top:8px;">
<span style="color:#64748b;">회차 진행률</span>
<span style="color:#ffffff;">{turn_cnt}.0 / {splits_cnt}</span>
</div>
<div class="roop-progress-bg">
<div class="roop-progress-fill" style="width: {prog_pct}%;"></div>
</div>
</div>"""
        st.markdown(card_html, unsafe_allow_html=True)

        
        btn_c1, btn_c2, btn_c3 = st.columns([2.5, 1, 1])
        with btn_c1:
            if st.button(f"🔍 세부 매매 & 주문", key=f"btn_detail_{p_id}", type="primary", use_container_width=True):
                state["active_project_id"] = p_id
                db.update_state(state, sha)
                st.session_state.view_mode = "DETAIL"
                st.rerun()
        with btn_c2:
            if st.button(f"✏️ 이름", key=f"btn_ren_{p_id}", use_container_width=True):
                st.session_state[f"show_ren_{p_id}"] = not st.session_state.get(f"show_ren_{p_id}", False)
        with btn_c3:
            if st.button(f"🗑️ 삭제", key=f"btn_del_{p_id}", use_container_width=True):
                del state["projects"][p_id]
                if state.get("active_project_id") == p_id:
                    rem = list(state["projects"].keys())
                    state["active_project_id"] = rem[0] if rem else None
                db.update_state(state, sha)
                st.success("삭제되었습니다.")
                time.sleep(1)
                st.rerun()
                
        if st.session_state.get(f"show_ren_{p_id}", False):
            with st.form(f"rename_form_{p_id}"):
                rename_input = st.text_input("새 이름", value=p["name"])
                if st.form_submit_button("💾 이름 저장"):
                    if rename_input.strip():
                        state["projects"][p_id]["name"] = rename_input.strip()
                        db.update_state(state, sha)
                        st.session_state[f"show_ren_{p_id}"] = False
                        st.rerun()

    st.stop()

# ==========================================
# 🔍 VIEW MODE 2: 루프 앱 1:1 세부 주문 화면 (DETAIL)
# ==========================================
active_id = state.get("active_project_id")
if not active_id or active_id not in projects_dict:
    st.session_state.view_mode = "LIST"
    st.rerun()

project_data = projects_dict[active_id]
target_etf = project_data["target_etf"]

if st.button("← 목록으로 돌아가기", key="back_btn"):
    st.session_state.view_mode = "LIST"
    st.rerun()

# 1:1 루프 앱 카드
turn_cnt = int(project_data.get('turn', 0))
splits_cnt = int(project_data.get('splits', 40))
prog_pct = min(100, int((turn_cnt / splits_cnt) * 100)) if splits_cnt > 0 else 0

detail_card_html = f"""<div class="roop-card">
<span class="badge-status">진행중</span>
<div class="roop-card-title">{project_data['name']}</div>
<div class="roop-card-sub">{target_etf} · V4.0 · 전반전</div>
<div style="display:flex; justify-content:space-between; font-size:0.85rem; font-weight:700;">
<span style="color:#64748b;">회차 진행률</span>
<span style="color:#ffffff;">{turn_cnt}.0 / {splits_cnt}</span>
</div>
<div class="roop-progress-bg">
<div class="roop-progress-fill" style="width: {prog_pct}%;"></div>
</div>
</div>"""
st.markdown(detail_card_html, unsafe_allow_html=True)

# 시세 및 잔고 API 조회
with st.spinner(f"[{project_data['name']}] 시세 및 계좌 잔고 로딩 중..."):
    try:
        current_price = api.get_current_price(target_etf)
    except Exception as e:
        current_price = 0.0
        
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

db_shares = float(project_data.get("total_shares", 0.0))
db_avg_price = float(project_data.get("avg_price", 0.0))

# V4.0 주문 계산
turn = int(project_data.get("turn", 0))
splits = int(project_data.get("splits", 40))
total_budget = float(project_data.get("total_budget", 10000.0))
total_spent = float(project_data.get("total_spent", 0.0))

if turn >= splits:
    daily_buy_budget = 0.0
else:
    remaining_budget = total_budget - total_spent
    daily_buy_budget = remaining_budget / (splits - turn)

buy1_price = db_avg_price if db_avg_price > 0 else current_price
buy1_qty = math.floor((daily_buy_budget * 0.5) / buy1_price) if buy1_price > 0 else 0
if buy1_qty == 0 and daily_buy_budget > 0 and buy1_price > 0:
    buy1_qty = 1  # 0.5회 매수금이 1주 가격보다 적을 경우 무한매수법 V4.0 규칙에 따라 최소 1주 매수

buy2_price = current_price * 1.10
buy2_qty = math.floor((daily_buy_budget * 0.5) / buy2_price) if buy2_price > 0 else 0
if buy2_qty == 0 and daily_buy_budget > 0 and buy2_price > 0:
    buy2_qty = 1  # 0.5회 매수금이 1주 가격보다 적을 경우 무한매수법 V4.0 규칙에 따라 최소 1주 매수

sell_price = db_avg_price * 1.10
sell_qty = db_shares


# ==========================================
# 🎯 루프 앱 1:1 디자인 "오늘의 주문" 2열 카드
# ==========================================
st.markdown('<div style="font-size:1.05rem; font-weight:800; color:#ffffff; margin-bottom:12px;">오늘의 주문</div>', unsafe_allow_html=True)

ord_col1, ord_col2 = st.columns(2)

with ord_col1:
    buy_html = f"""<div class="buy-box">
<div class="box-title-buy">매수 · LOC</div>
<div class="order-row">
<div>
<span class="price-bold">${buy1_price:.2f}</span>
<span class="qty-text"> × {buy1_qty}주</span>
</div>
<span class="tag-red">평단</span>
</div>
<div class="order-row">
<div>
<span class="price-bold">${buy2_price:.2f}</span>
<span class="qty-text"> × {buy2_qty}주</span>
</div>
<span class="tag-red">8.0%</span>
</div>
</div>"""
    st.markdown(buy_html, unsafe_allow_html=True)

with ord_col2:
    sell_html = f"""<div class="sell-box">
<div class="box-title-sell">매도 · LOC · 지정가</div>
<div class="order-row">
<div>
<span class="price-bold">${sell_price:.2f}</span>
<span class="qty-text"> × {sell_qty:g}주</span>
</div>
<span class="tag-purple">지정가</span>
</div>
</div>"""
    st.markdown(sell_html, unsafe_allow_html=True)


# 한국투자증권 예약주문 승인 섹션
st.markdown("---")
st.markdown("### ⚡ 한국투자증권 자동 주문 전송")

col_b1, col_b2, col_s = st.columns(3)
with col_b1:
    approve_buy1 = st.checkbox("주문 1 승인 (평단 LOC)", value=True if buy1_qty > 0 else False, disabled=buy1_qty == 0)
with col_b2:
    approve_buy2 = st.checkbox("주문 2 승인 (고가 LOC)", value=True if buy2_qty > 0 else False, disabled=buy2_qty == 0)
with col_s:
    approve_sell = st.checkbox("주문 3 승인 (익절 매도)", value=True if sell_qty > 0 else False, disabled=sell_qty == 0)

if st.button(f"🚀 [{project_data['name']}] 주문들을 한국투자증권으로 즉시 전송", type="primary", use_container_width=True):
    success_orders = 0
    fail_orders = 0
    messages = []
    
    order_data_log = [
        {"구분": "매수 1순위 (평단 LOC)", "수량": buy1_qty, "단가": buy1_price},
        {"구분": "매수 2순위 (고가 LOC)", "수량": buy2_qty, "단가": buy2_price}
    ]
    if sell_qty > 0:
        order_data_log.append({"구분": "익절 매도", "수량": sell_qty, "단가": sell_price})
        
    if approve_buy1 and buy1_qty > 0:
        success, res = api.place_order(target_etf, buy1_qty, buy1_price, order_type="34")
        if success:
            success_orders += 1
            messages.append(f"✅ 매수 1순위(평단 LOC) 성공: {buy1_qty}주 @ ${buy1_price:.2f}")
        else:
            fail_orders += 1
            messages.append(f"❌ 매수 1순위 실패: {res}")
            
    if approve_buy2 and buy2_qty > 0:
        success, res = api.place_order(target_etf, buy2_qty, buy2_price, order_type="34")
        if success:
            success_orders += 1
            messages.append(f"✅ 매수 2순위(고가 LOC) 성공: {buy2_qty}주 @ ${buy2_price:.2f}")
        else:
            fail_orders += 1
            messages.append(f"❌ 매수 2순위 실패: {res}")
            
    if approve_sell and sell_qty > 0:
        success, res = api.place_order(target_etf, -sell_qty, sell_price, order_type="00")
        if success:
            success_orders += 1
            messages.append(f"✅ 익절 매도 성공: {sell_qty}주 @ ${sell_price:.2f}")
        else:
            fail_orders += 1
            messages.append(f"❌ 익절 매도 실패: {res}")

    for msg in messages:
        st.write(msg)
        
    if success_orders > 0 and fail_orders == 0:
        st.success(f"🎉 모든 주문이 성공적으로 전송되었습니다!")
        if approve_buy1 or approve_buy2:
            project_data["turn"] = turn + 1
            
        log_entry = {
            "date": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            "env": api.env,
            "target": target_etf,
            "turn_before": turn,
            "turn_after": project_data["turn"],
            "orders": order_data_log
        }
        project_data.setdefault("history", []).append(log_entry)
        state["projects"][active_id] = project_data
        
        db_success, new_sha = db.update_state(state, sha)
        if db_success:
            st.success("💾 깃허브 DB 업데이트 완료!")
            time.sleep(2)
            st.rerun()

# 잔고 및 현황 요약
with st.expander("🏦 계좌 잔고 및 손익 상태 상세보기"):
    c1, c2, c3 = st.columns(3)
    c1.metric("사용 가능 예수금 (USD)", f"${usd_cash:,.2f}")
    c2.metric(f"실제 {target_etf} 수량", f"{actual_shares} 주")
    c3.metric(f"실제 {target_etf} 평단", f"${actual_avg_price:.2f}")
    
    if st.button(f"🛠️ DB를 실제 계좌 기준({target_etf})으로 동기화"):
        project_data["total_shares"] = actual_shares
        project_data["avg_price"] = actual_avg_price
        project_data["total_spent"] = actual_shares * actual_avg_price
        if actual_shares == 0:
            project_data["turn"] = 0
            
        state["projects"][active_id] = project_data
        db.update_state(state, sha)
        st.success("동기화 완료!")
        st.rerun()
