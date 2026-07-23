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
    page_title="무한매수 4.0 Pro 대시보드",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ------------------------------------------
# 🎨 Next-Gen Pro Glassmorphism 디자인 시스템
# ------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800;900&family=Noto+Sans+KR:wght@400;600;700;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', 'Noto Sans KR', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background-color: #080c14;
        color: #f8fafc;
    }
    
    header[data-testid="stHeader"], [data-testid="stHeader"] {
        background-color: transparent !important;
        z-index: 1 !important;
    }
    
    .block-container {
        padding-top: 2.2rem !important;
        padding-bottom: 5rem !important;
        max-width: 620px;
        margin: 0 auto;
    }
    
    @media (max-width: 768px) {
        .block-container {
            padding-left: 0.8rem !important;
            padding-right: 0.8rem !important;
            padding-top: 2.5rem !important;
        }
    }

    /* 📊 상단 종합 계좌 브리핑 Card */
    .summary-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.85) 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(16px);
        border-radius: 22px;
        padding: 16px 20px;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
    }

    .summary-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 12px;
    }

    .summary-item {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 14px;
        padding: 10px 14px;
    }

    .summary-label {
        font-size: 0.73rem;
        font-weight: 700;
        color: #94a3b8;
        margin-bottom: 4px;
    }

    .summary-val {
        font-size: 1.15rem;
        font-weight: 800;
        color: #ffffff;
    }

    /* 📋 Pro 프로젝트 대시보드 카드 */
    .pro-card {
        background: linear-gradient(145deg, #111827 0%, #0f172a 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 22px;
        padding: 18px 20px;
        margin-bottom: 0px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
    }

    .pro-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
    }

    .pro-card-title {
        font-size: 1.3rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.3px;
    }

    .ticker-badge {
        background: rgba(99, 102, 241, 0.2);
        color: #a5b4fc;
        font-size: 0.75rem;
        font-weight: 800;
        padding: 3px 10px;
        border-radius: 8px;
        border: 1px solid rgba(99, 102, 241, 0.3);
    }

    .status-badge-active {
        background: rgba(16, 185, 129, 0.2);
        color: #34d399;
        font-size: 0.75rem;
        font-weight: 800;
        padding: 3px 10px;
        border-radius: 20px;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }

    .pro-metrics-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 6px;
        background: rgba(15, 23, 42, 0.65);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 14px;
        padding: 10px 8px;
        margin-top: 12px;
        margin-bottom: 12px;
        text-align: center;
    }

    .metric-label {
        font-size: 0.7rem;
        color: #64748b;
        font-weight: 700;
        margin-bottom: 2px;
    }

    .metric-value {
        font-size: 0.92rem;
        font-weight: 800;
        color: #f1f5f9;
    }

    .pnl-pill-green {
        background: rgba(16, 185, 129, 0.2);
        color: #34d399;
        font-size: 0.78rem;
        font-weight: 800;
        padding: 2px 6px;
        border-radius: 6px;
        display: inline-block;
    }

    .pnl-pill-red {
        background: rgba(239, 68, 68, 0.2);
        color: #f87171;
        font-size: 0.78rem;
        font-weight: 800;
        padding: 2px 6px;
        border-radius: 6px;
        display: inline-block;
    }

    /* 회차 프로그레스 바 */
    .roop-progress-bg {
        background: #1e263d;
        height: 7px;
        border-radius: 6px;
        width: 100%;
        overflow: hidden;
        margin-top: 6px;
    }

    .roop-progress-fill {
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%);
        height: 100%;
        border-radius: 6px;
    }

    .guide-box {
        background: rgba(30, 41, 59, 0.5);
        border-left: 3px solid #ef4444;
        border-radius: 10px;
        padding: 8px 12px;
        font-size: 0.78rem;
        color: #cbd5e1;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 10px;
    }

    /* ------------------------------------------
       목록 카드(list-card-touch) 전용 100% 픽셀-밀착 클릭 레이어
       ------------------------------------------ */
    div[data-testid="stVerticalBlock"] > div[data-testid="stElementContainer"]:has(div.list-card-touch) {
        position: relative !important;
        margin-bottom: 0px !important;
    }

    div[data-testid="stVerticalBlock"] > div[data-testid="stElementContainer"]:has(div.list-card-touch) + div[data-testid="stElementContainer"] {
        position: relative !important;
        margin-top: -248px !important; /* Pro 카드 높이에 밀착 */
        margin-bottom: 20px !important;
        width: 100% !important;
        height: 232px !important;
        z-index: 99 !important;
        border: none !important;
        background: transparent !important;
        pointer-events: auto !important;
    }

    div[data-testid="stVerticalBlock"] > div[data-testid="stElementContainer"]:has(div.list-card-touch) + div[data-testid="stElementContainer"] div[data-testid="stButton"] {
        width: 100% !important;
        height: 232px !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    div[data-testid="stVerticalBlock"] > div[data-testid="stElementContainer"]:has(div.list-card-touch) + div[data-testid="stElementContainer"] button {
        width: 100% !important;
        height: 232px !important;
        opacity: 0.001 !important;
        background: transparent !important;
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
        cursor: pointer !important;
        pointer-events: auto !important;
        touch-action: manipulation !important;
        padding: 0 !important;
        margin: 0 !important;
        display: block !important;
    }

    /* 오늘의 주문 2열 카드 (레드 / 블루) */
    .buy-box {
        background: #251217;
        border: 1px solid rgba(239, 68, 68, 0.25);
        border-radius: 18px;
        padding: 16px;
        margin-bottom: 12px;
        min-height: 130px;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
    }
    
    .sell-box {
        background: #121933;
        border: 1px solid rgba(99, 102, 241, 0.25);
        border-radius: 18px;
        padding: 16px;
        margin-bottom: 12px;
        min-height: 130px;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
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

    div.stButton > button {
        border-radius: 14px !important;
        font-weight: 700 !important;
    }

    button[kind="primary"] p {
        font-size: 1.15rem !important;
        font-weight: 900 !important;
    }
</style>
""", unsafe_allow_html=True)

# 환경 변수 로드
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

# 🔒 보안 비밀번호 인증 (세션 기반)
env_pwd = os.getenv("APP_PASSWORD")
if env_pwd and state.get("app_password") != env_pwd:
    state["app_password"] = env_pwd
    db.update_state(state, sha)

APP_PASSWORD = state.get("app_password") or env_pwd or "0000"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown('<h2 style="font-weight:800; color:#38bdf8; text-align:center; margin-top:2rem;">🔒 무한매수 4.0 Pro 인증</h2>', unsafe_allow_html=True)
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
# 🔝 상단 Header Bar (Pro 타이틀 & + 새 프로젝트)
# ==========================================
hdr_col1, hdr_col2 = st.columns([2.5, 2.5])

with hdr_col1:
    env_badge = "🧪 모의투자" if api.env == "mock" else "🚀 실전투자"
    st.markdown(f'''
    <div>
        <span style="font-size: 1.4rem; font-weight:900; color:#ffffff;">📈 무한매수 4.0 Pro</span>
        <span style="font-size:0.75rem; font-weight:800; background:rgba(99,102,241,0.25); color:#a5b4fc; padding:2px 8px; border-radius:12px; margin-left:6px;">{env_badge}</span>
    </div>
    ''', unsafe_allow_html=True)

with hdr_col2:
    if st.button("➕ 새 프로젝트", key="top_new_cycle_btn", use_container_width=True):
        st.session_state.view_mode = "CREATE"
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

projects_dict = state.get("projects", {})

# ==========================================
# 📊 상단 스마트 계좌 브리핑 (Executive Summary)
# ==========================================
try:
    _, usd_cash_val, krw_cash_val, _ = api.get_balance()
except Exception:
    usd_cash_val = 0.0
    krw_cash_val = 0.0

active_proj_count = len(projects_dict)
total_allocated_budget = sum(float(p.get("total_budget", 10000.0)) for p in projects_dict.values())
total_spent_budget = sum(float(p.get("total_spent", 0.0)) for p in projects_dict.values())

summary_html = f'''
<div class="summary-card">
    <div class="summary-grid" style="grid-template-columns: repeat(2, 1fr);">
        <div class="summary-item">
            <div class="summary-label">💵 외화 예수금</div>
            <div class="summary-val">${usd_cash_val:,.2f}</div>
        </div>
        <div class="summary-item">
            <div class="summary-label">₩ 원화 예수금</div>
            <div class="summary-val">{krw_cash_val:,.0f} 원</div>
        </div>
    </div>
</div>
'''
st.markdown(summary_html, unsafe_allow_html=True)

# ==========================================
# ➕ 새 프로젝트 생성 화면
# ==========================================
if st.session_state.view_mode == "CREATE" or not projects_dict:
    st.markdown("### 🚀 새 프로젝트 생성")
    
    new_p_ticker = st.selectbox("🎯 매매 종목 선택", ["SOXL", "TQQQ"], key="create_p_ticker")
    existing_count = sum(1 for p in projects_dict.values() if p.get("target_etf") == new_p_ticker)
    recommended_name = f"{new_p_ticker} {existing_count + 1}차"

    with st.form("create_proj_form"):
        new_p_name = st.text_input("프로젝트 이름", value=recommended_name, placeholder=f"예: {recommended_name}")
        new_p_budget = st.number_input("💰 총 투자 예산 ($USD)", min_value=100.0, value=10000.0, step=500.0)
        new_p_splits = st.number_input("⏳ 분할 회차 (Splits)", min_value=10, max_value=60, value=40)
        
        create_submit = st.form_submit_button("✨ 새 프로젝트 생성 및 매매 시작", type="primary", use_container_width=True)
        
        if create_submit:
            final_name = new_p_name.strip() if new_p_name.strip() else recommended_name
            new_id = f"proj_{int(time.time())}"
            if "projects" not in state or not isinstance(state.get("projects"), dict):
                state["projects"] = {}
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
            _, sha = db.update_state(state, sha)
            st.session_state.view_mode = "DETAIL"
            st.success(f"🎉 [{final_name}] 프로젝트가 생성되었습니다!")
            st.rerun()

    if projects_dict:
        if st.button("❌ 취소 및 목록으로 돌아가기"):
            st.session_state.view_mode = "LIST"
            st.rerun()
            
    st.stop()


# ==========================================
# 📋 VIEW MODE 1: 프로젝트 목록 (Pro Card LIST)
# ==========================================
if st.session_state.view_mode == "LIST":
    st.markdown('''
    <div style="text-align:right; margin-bottom:14px;">
        <span style="font-weight:600; color:#64748b; font-size:0.85rem;">총 {0}개 운용 중</span>
    </div>
    '''.format(len(projects_dict)), unsafe_allow_html=True)
    
    p_items = list(projects_dict.values())
    for p in p_items:
        p_id = p["id"]
        ticker = p.get("target_etf", "TQQQ")
        turn_cnt = int(p.get('turn', 0))
        splits_cnt = int(p.get('splits', 40))
        prog_pct = min(100, int((turn_cnt / splits_cnt) * 100)) if splits_cnt > 0 else 0
        
        db_shares = float(p.get("total_shares", 0.0))
        db_avg_price = float(p.get("avg_price", 0.0))
        total_spent = float(p.get("total_spent", 0.0))
        total_budget = float(p.get("total_budget", 10000.0))
        
        # 현재가 조회 (오류 시 평단 또는 0)
        try:
            curr_price = api.get_current_price(ticker)
        except Exception:
            curr_price = 0.0
            
        display_curr = curr_price if curr_price > 0 else db_avg_price
        
        # 수익률 계산
        if db_avg_price > 0 and display_curr > 0:
            pnl_pct = ((display_curr - db_avg_price) / db_avg_price) * 100
            pnl_html = f'<span class="pnl-pill-green">+{pnl_pct:.2f}%</span>' if pnl_pct >= 0 else f'<span class="pnl-pill-red">{pnl_pct:.2f}%</span>'
        else:
            pnl_html = '<span style="color:#64748b; font-size:0.8rem; font-weight:700;">0.00%</span>'

        # 오늘 2분할 LOC 매수가이드 계산
        rem_budget = max(0.0, total_budget - total_spent)
        daily_budget = rem_budget / (splits_cnt - turn_cnt) if turn_cnt < splits_cnt else 0.0
        
        card_b1_price = db_avg_price if db_avg_price > 0 else display_curr
        card_b1_qty = math.floor((daily_budget * 0.5) / card_b1_price) if card_b1_price > 0 else 0
        if card_b1_qty == 0 and daily_budget > 0 and card_b1_price > 0:
            card_b1_qty = 1
            
        card_b2_price = display_curr * 1.10 if display_curr > 0 else card_b1_price * 1.10
        card_b2_qty = math.floor((daily_budget * 0.5) / card_b2_price) if card_b2_price > 0 else 0
        if card_b2_qty == 0 and daily_budget > 0 and card_b2_price > 0:
            card_b2_qty = 1

        excg_tag = "AMEX" if ticker == "SOXL" else "NASD"

        card_html = f"""<div class="pro-card list-card-touch">
<div class="pro-card-header">
<div>
<span class="ticker-badge">{ticker} · {excg_tag}</span>
<span class="pro-card-title" style="margin-left:8px;">{p['name']}</span>
</div>
<span class="status-badge-active">진행중</span>
</div>

<div class="pro-metrics-grid">
<div>
<div class="metric-label">현재가</div>
<div class="metric-value">${display_curr:.2f}</div>
</div>
<div>
<div class="metric-label">평균매수가</div>
<div class="metric-value">${db_avg_price:.2f}</div>
</div>
<div>
<div class="metric-label">손익률</div>
<div>{pnl_html}</div>
</div>
<div>
<div class="metric-label">보유수량</div>
<div class="metric-value">{db_shares:g}주</div>
</div>
</div>

<div style="display:flex; justify-content:space-between; font-size:0.8rem; font-weight:700; color:#94a3b8;">
<span>회차 진행률 ({turn_cnt}/{splits_cnt}회)</span>
<span style="color:#ffffff;">${total_spent:,.0f} / ${total_budget:,.0f}</span>
</div>
<div class="roop-progress-bg">
<div class="roop-progress-fill" style="width: {prog_pct}%;"></div>
</div>

<div class="guide-box">
<div>🔴 <b>LOC 매수가이드</b>: 1순위 ${card_b1_price:.2f} ({card_b1_qty}주) | 2순위 ${card_b2_price:.2f} ({card_b2_qty}주)</div>
<div style="color:#818cf8; font-weight:800;">상세보기 →</div>
</div>
</div>"""
        st.markdown(card_html, unsafe_allow_html=True)

        if st.button(" ", key=f"overlay_click_{p_id}", use_container_width=True):
            state["active_project_id"] = p_id
            db.update_state(state, sha)
            st.session_state.view_mode = "DETAIL"
            st.rerun()

    st.stop()

# ==========================================
# 🔍 VIEW MODE 2: 360도 Pro 세부 대시보드 (DETAIL)
# ==========================================
active_id = state.get("active_project_id")
if not active_id or active_id not in projects_dict:
    st.session_state.view_mode = "LIST"
    st.rerun()

project_data = projects_dict[active_id]
target_etf = project_data["target_etf"]

if st.button("← 목록", key="back_btn"):
    st.session_state.view_mode = "LIST"
    st.rerun()

dash_tab, set_tab = st.tabs(["📊 대시보드", "⚙️ 설정"])

with set_tab:
    st.markdown("<br>", unsafe_allow_html=True)
    rn_col1, rn_col2 = st.columns([4, 1])
    with rn_col1:
        new_name_val = st.text_input("새 프로젝트 이름", value=project_data["name"], label_visibility="collapsed")
    with rn_col2:
        if st.button("💾 저장", use_container_width=True):
            if new_name_val.strip() and new_name_val.strip() != project_data["name"]:
                state["projects"][active_id]["name"] = new_name_val.strip()
                db.update_state(state, sha)
                st.rerun()
    
    st.markdown("---")
    with st.popover("🗑️ 프로젝트 삭제"):
        st.markdown("<div style='font-size:0.95rem; font-weight:700; margin-bottom:12px;'>정말 이 프로젝트를 영구적으로 삭제하시겠습니까?</div>", unsafe_allow_html=True)
        d_col1, d_col2, d_col3 = st.columns([1, 2, 1])
        with d_col2:
            if st.button("✅ 확인", use_container_width=True):
                del state["projects"][active_id]
                rem = list(state["projects"].keys())
                state["active_project_id"] = rem[0] if rem else None
                db.update_state(state, sha)
                st.session_state.view_mode = "CREATE" if not rem else "LIST"
                st.rerun()

with dash_tab:
    # 시세 및 잔고 API 조회
    with st.spinner(f"[{project_data['name']}] 실시간 시세 및 계좌 잔고 로딩 중..."):
        try:
            current_price = api.get_current_price(target_etf)
        except Exception as e:
            current_price = 0.0
        
        try:
            holdings, usd_cash, krw_cash, account_summary = api.get_balance()
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
            krw_cash = 0.0
            holdings = []

    db_shares = float(project_data.get("total_shares", 0.0))
    db_avg_price = float(project_data.get("avg_price", 0.0))

    turn_cnt = int(project_data.get('turn', 0))
    splits_cnt = int(project_data.get('splits', 40))
    prog_pct = min(100, int((turn_cnt / splits_cnt) * 100)) if splits_cnt > 0 else 0

    display_curr = current_price if current_price > 0 else db_avg_price
    if db_avg_price > 0 and display_curr > 0:
        detail_pnl_pct = ((display_curr - db_avg_price) / db_avg_price) * 100
        detail_pnl_html = f'<span class="pnl-pill-green">+{detail_pnl_pct:.2f}%</span>' if detail_pnl_pct >= 0 else f'<span class="pnl-pill-red">{detail_pnl_pct:.2f}%</span>'
    else:
        detail_pnl_html = '<span style="color:#64748b; font-size:0.85rem; font-weight:700;">0.00%</span>'

    detail_card_html = f"""<div class="pro-card">
<div class="pro-card-header">
<div>
<span class="ticker-badge">{target_etf} 대시보드</span>
<span class="pro-card-title" style="margin-left:8px;">{project_data['name']}</span>
</div>
<span class="status-badge-active">진행중</span>
</div>

<div class="pro-metrics-grid">
<div>
<div class="metric-label">현재가</div>
<div class="metric-value">${display_curr:.2f}</div>
</div>
<div>
<div class="metric-label">평균매수가</div>
<div class="metric-value">${db_avg_price:.2f}</div>
</div>
<div>
<div class="metric-label">실시간손익</div>
<div>{detail_pnl_html}</div>
</div>
<div>
<div class="metric-label">보유수량</div>
<div class="metric-value">{db_shares:g}주</div>
</div>
</div>

<div style="display:flex; justify-content:space-between; font-size:0.85rem; font-weight:700; color:#94a3b8;">
<span>회차 진행률 ({turn_cnt} / {splits_cnt}회)</span>
<span style="color:#ffffff;">{prog_pct}% 완료</span>
</div>
<div class="roop-progress-bg">
<div class="roop-progress-fill" style="width: {prog_pct}%;"></div>
</div>
</div>"""
    st.markdown(detail_card_html, unsafe_allow_html=True)


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
        buy1_qty = 1

    buy2_price = current_price * 1.10
    buy2_qty = math.floor((daily_buy_budget * 0.5) / buy2_price) if buy2_price > 0 else 0
    if buy2_qty == 0 and daily_buy_budget > 0 and buy2_price > 0:
        buy2_qty = 1

    sell_price = db_avg_price * 1.10
    sell_qty = db_shares

    # 오늘의 주문 2열 카드
    st.markdown('<div style="font-size:1.05rem; font-weight:800; color:#ffffff; margin-top:16px; margin-bottom:12px;">오늘의 주문</div>', unsafe_allow_html=True)

    ord_col1, ord_col2 = st.columns(2)

    with ord_col1:
        buy_html = f"""<div class="buy-box">
<div class="box-title-buy">매수 · LOC 2분할</div>
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
<span class="tag-red">고가</span>
</div>
</div>"""
        st.markdown(buy_html, unsafe_allow_html=True)

    with ord_col2:
        sell_html = f"""<div class="sell-box">
<div class="box-title-sell">매도 · LOC / 지정가</div>
<div class="order-row">
<div>
<span class="price-bold">${sell_price:.2f}</span>
<span class="qty-text"> × {sell_qty:g}주</span>
</div>
<span class="tag-purple">+10% 익절</span>
</div>
</div>"""
        st.markdown(sell_html, unsafe_allow_html=True)

    # 오늘의 주문 전송 섹션

    approve_buy1 = True if buy1_qty > 0 else False
    approve_buy2 = True if buy2_qty > 0 else False
    approve_sell = True if sell_qty > 0 else False

    if st.button("오늘의 주문 전송", type="primary", use_container_width=True):
        # 페이지 로드 시 호출된 잔고조회 API 등과 주문 전송 API가 겹쳐 
        # '초당 거래건수 초과(TPS)' 에러가 발생하는 것을 방지하기 위해 잠시 대기
        time.sleep(1.0)
    
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
                messages.append(f"❌ 매수 1순위: {res}")
            time.sleep(1.0)
            
        if approve_buy2 and buy2_qty > 0:
            success, res = api.place_order(target_etf, buy2_qty, buy2_price, order_type="34")
            if success:
                success_orders += 1
                messages.append(f"✅ 매수 2순위(고가 LOC) 성공: {buy2_qty}주 @ ${buy2_price:.2f}")
            else:
                fail_orders += 1
                messages.append(f"❌ 매수 2순위: {res}")
            time.sleep(1.0)
            
        if approve_sell and sell_qty > 0:
            success, res = api.place_order(target_etf, -sell_qty, sell_price, order_type="00")
            if success:
                success_orders += 1
                messages.append(f"✅ 익절 매도 성공: {sell_qty}주 @ ${sell_price:.2f}")
            else:
                fail_orders += 1
                messages.append(f"❌ 익절 매도: {res}")

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

    # 계좌 잔고 및 DB 동기화 센터
    with st.expander("🏦 계좌 잔고 및 실제 주식 수량 DB 동기화"):
        sync_html = f'''
        <div class="summary-grid" style="grid-template-columns: repeat(3, 1fr); margin-bottom: 15px;">
            <div class="summary-item">
                <div class="summary-label">💵 사용 가능 예수금</div>
                <div class="summary-val" style="font-size:1.0rem;">${usd_cash:,.2f}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">📦 실제 {target_etf} 수량</div>
                <div class="summary-val" style="font-size:1.0rem;">{actual_shares} 주</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">🎯 실제 {target_etf} 평단</div>
                <div class="summary-val" style="font-size:1.0rem;">${actual_avg_price:.2f}</div>
            </div>
        </div>
        '''
        st.markdown(sync_html, unsafe_allow_html=True)
    
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





