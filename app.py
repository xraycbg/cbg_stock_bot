import streamlit as st
import pandas as pd
import os
import math
import time
import copy
from dotenv import load_dotenv
from github_db import GitHubDB
from kis_api import KISApi

# 페이지 기본 설정 (아이폰 및 모바일 뷰포트 최적화)
st.set_page_config(
    page_title="cbg 무매40 대시보드",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

@st.dialog("프로젝트 삭제")
def confirm_delete_dialog(p_id, p_name):
    st.markdown(f"**{p_name}** 프로젝트를 정말 삭제하시겠습니까?<br><span style='font-size:0.85rem; color:#94a3b8;'>삭제 시 복구할 수 없습니다.</span>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    d_col1, d_col2 = st.columns(2)
    with d_col1:
        if st.button("확인", use_container_width=True, type="primary"):
            state, sha = db.get_state()
            state = copy.deepcopy(state)
            if state and p_id in state["projects"]:
                del state["projects"][p_id]
                success, _ = db.update_state(state, sha)
                if success:
                    st.rerun()
                else:
                    st.error("⚠️ 깃허브 DB 저장 실패")
            else:
                st.rerun()
    with d_col2:
        if st.button("취소", use_container_width=True):
            st.rerun()

@st.dialog("프로젝트 제목 편집")
def edit_title_dialog(p_id, old_name):
    new_name = st.text_input("새 프로젝트 제목", value=old_name)
    d_col1, d_col2 = st.columns(2)
    with d_col1:
        if st.button("저장", use_container_width=True, type="primary"):
            state, sha = db.get_state()
            state = copy.deepcopy(state)
            if state and p_id in state["projects"]:
                state["projects"][p_id]["name"] = new_name.strip()
                success, _ = db.update_state(state, sha)
                if success:
                    st.rerun()
                else:
                    st.error("⚠️ 깃허브 DB 저장 실패")
            else:
                st.rerun()
    with d_col2:
        if st.button("취소", use_container_width=True):
            st.rerun()

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
    
    /* 버튼 글씨 줄바꿈 방지 (어떤 해상도에서도 1줄 유지) */
    .stButton > button, .stButton > button * {
        white-space: nowrap !important;
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
        border-radius: 10px;
        padding: 12px 14px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: flex-start;
        gap: 4px;
    }

    .summary-label {
        font-size: 0.8rem;
        font-weight: 600;
        color: #94a3b8;
    }

    .summary-val {
        font-size: 1.05rem;
        font-weight: 800;
        color: #ffffff;
    }

    /* 📋 Pro 프로젝트 대시보드 카드 */
    .pro-card {
        background: linear-gradient(145deg, #111827 0%, #0f172a 100%);
        border: 1.5px solid #8b5cf6;
        border-radius: 22px;
        padding: 18px 20px;
        margin-bottom: 0px;
        box-shadow: 0 4px 20px rgba(139, 92, 246, 0.25);
    }

    div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"]:first-child .pro-card-marker) {
        background: linear-gradient(145deg, #111827 0%, #0f172a 100%) !important;
        border: 1px solid rgba(139, 92, 246, 0.4) !important;
        border-radius: 22px !important;
        padding: 18px 20px !important;
        margin-bottom: 24px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4) !important;
    }
    
    div[data-testid="stElementContainer"]:has(.pro-card-marker) {
        display: none !important;
    }
    
    div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"]:first-child .pro-card-marker) > div {
        gap: 0.5rem !important;
    }

    .pro-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
    }

    .pro-card-title {
        font-size: 1.15rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.3px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
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
        white-space: nowrap;
        flex-shrink: 0;
    }

    .pro-metrics-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 10px;
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
        margin-bottom: 24px;
    }

    .roop-progress-fill {
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%);
        height: 100%;
        border-radius: 6px;
    }

    .guide-box {
        background: rgba(30, 41, 59, 0.5);
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
        margin-top: -188px !important; /* 상단 60px(삭제버튼 영역) 터치 제외 */
        margin-bottom: 20px !important;
        width: 100% !important;
        height: 172px !important;
        z-index: 99 !important;
        border: none !important;
        background: transparent !important;
        pointer-events: auto !important;
    }
    
    /* 삭제 버튼 컬럼 자체를 우측 정렬 */
    div[data-testid="stHorizontalBlock"]:has(.del-btn-wrapper) > div:last-child > div[data-testid="stVerticalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        justify-content: flex-end !important;
        align-items: center !important;
        width: 100% !important;
    }

    /* 마커 숨김 */
    div[data-testid="stElementContainer"]:has(.del-btn-wrapper) {
        display: none !important;
    }

    /* 삭제 버튼 스타일링 */
    div[data-testid="stHorizontalBlock"]:has(.del-btn-wrapper) button {
        background: rgba(239, 68, 68, 0.15) !important;
        color: #ef4444 !important;
        border: 1px solid rgba(239, 68, 68, 0.3) !important;
        border-radius: 20px !important;
        font-size: 0.75rem !important;
        font-weight: 800 !important;
        padding: 2px 10px !important;
        min-height: 0 !important;
        height: 24px !important;
        line-height: 1 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: none !important;
        margin: 0 !important;
        width: auto !important;
    }
    
    div[data-testid="stHorizontalBlock"]:has(.del-btn-wrapper) button:hover {
        background: rgba(239, 68, 68, 0.25) !important;
        border-color: rgba(239, 68, 68, 0.5) !important;
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
        padding: 12px 16px;
        margin-bottom: 12px;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
    }
    
    .sell-box {
        background: #121933;
        border: 1px solid rgba(99, 102, 241, 0.25);
        border-radius: 18px;
        padding: 12px 16px;
        margin-bottom: 12px;
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
        flex-wrap: wrap;
        row-gap: 4px;
        margin-bottom: 10px;
    }
    
    .order-row:last-child {
        margin-bottom: 0px;
    }
    
    .order-row > div {
        white-space: nowrap;
        display: flex;
        align-items: center;
        gap: 4px;
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
        white-space: nowrap;
        flex-shrink: 0;
    }
    
    .tag-purple {
        background: rgba(139, 92, 246, 0.25);
        color: #c084fc;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 10px;
        white-space: nowrap;
        flex-shrink: 0;
    }

    div.stButton > button {
        border-radius: 14px !important;
        font-weight: 700 !important;
    }

    button[kind="primary"] p {
        font-size: 1.05rem !important;
        font-weight: 900 !important;
    }

    /* 마커 컨테이너 자체를 숨겨서 여백 제거 */
    div[data-testid="stElementContainer"]:has(.title-btn-marker) {
        display: none !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* 클릭 가능한 제목 버튼용 (structural sibling targeting) */
    div[data-testid="stElementContainer"]:has(.title-btn-marker) + div[data-testid="stElementContainer"] button {
        background: transparent !important;
        border: none !important;
        padding: 4px 0 !important;
        box-shadow: none !important;
        display: flex !important;
        width: 100% !important;
        justify-content: flex-start !important;
        margin-top: -4px !important;
        margin-bottom: -6px !important;
    }
    
    div[data-testid="stElementContainer"]:has(.title-btn-marker) + div[data-testid="stElementContainer"] button * {
        text-align: left !important;
        justify-content: flex-start !important;
        font-size: 1.35rem !important;
        font-weight: 800 !important;
        color: #ffffff !important;
        margin: 0 !important;
        width: 100% !important;
        line-height: 1.2 !important;
    }
    
    div[data-testid="stElementContainer"]:has(.title-btn-marker) + div[data-testid="stElementContainer"] button:hover * {
        color: #a5b4fc !important;
    }
</style>
""", unsafe_allow_html=True)

# 환경 변수 로드
from pathlib import Path
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

# DB 및 API 초기화
if "github_db" not in st.session_state:
    st.session_state.github_db = GitHubDB()

db = st.session_state.github_db
api = KISApi() # 항상 최신 로직을 반영하기 위해 세션캐시를 사용하지 않음

@st.cache_data(ttl=300, show_spinner=True)
def get_cached_price(_api, ticker):
    return _api.get_current_price(ticker)

@st.cache_data(ttl=300, show_spinner=True)
def get_cached_balance(_api):
    return _api.get_balance()

def send_telegram_msg(text):
    import requests
    import os
    try:
        cloud_token = st.secrets.get("TELEGRAM_BOT_TOKEN")
        cloud_chat = st.secrets.get("TELEGRAM_CHAT_ID")
    except Exception:
        cloud_token, cloud_chat = None, None
        
    token = os.getenv("TELEGRAM_BOT_TOKEN") or cloud_token
    chat_id = os.getenv("TELEGRAM_CHAT_ID") or cloud_chat
    if token and chat_id:
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
            resp = requests.post(url, json=payload, timeout=5)
            return resp.status_code == 200, resp.text
        except Exception as e:
            return False, str(e)
    return False, "Not configured"

raw_state, sha = db.get_state()
raw_state = copy.deepcopy(raw_state)

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
            "turn": float(s.get("turn", 0.0)),
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
            }
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
                "turn": float(p.get("turn", 0.0)),
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
            
    # 과거 유물(legacy key) 삭제
    if "active_project" in s:
        del s["active_project"]
            
    return s

state = normalize_state(raw_state)

# 🔒 보안 비밀번호 인증 (세션 기반) - 오직 .env 또는 Streamlit Secrets만 사용!
def get_env_pwd():
    try:
        env_file = Path(__file__).parent / ".env"
        if env_file.exists():
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith("APP_PASSWORD="):
                        return line.split("=", 1)[1].strip()
    except Exception:
        pass
    return os.getenv("APP_PASSWORD")

env_pwd = get_env_pwd()

try:
    cloud_pwd = st.secrets.get("APP_PASSWORD")
except Exception:
    cloud_pwd = None

# Streamlit Secrets를 최우선으로, 그 다음 로컬 환경변수, 모두 없으면 기본값 'aaaa'
APP_PASSWORD = cloud_pwd or env_pwd or "aaaa"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown('<h2 style="font-weight:800; color:#38bdf8; text-align:center; margin-top:2rem;">cbg 무매40 인증</h2>', unsafe_allow_html=True)
    with st.form("auth_form"):
        password_input = st.text_input("접속 비밀번호 (PIN)", type="password", placeholder="비밀번호 입력")
        submit_btn = st.form_submit_button("로그인", type="primary", use_container_width=True)
        if submit_btn:
            if password_input.strip() == str(APP_PASSWORD).strip():
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

        
    st.markdown("---")
    st.markdown("### 💾 GitHub DB 상태")
    st.text(f"Repo: {db.repo}")
    st.text(f"Path: {db.file_path}")
    if st.button("🔄 GitHub DB 다시 불러오기"):
        st.cache_data.clear()
        st.session_state.pop("github_db_state", None)
        st.session_state.pop("github_db_sha", None)
        st.rerun()
        
    st.markdown("---")
    st.markdown("### 📲 텔레그램 연동")
    if st.button("🚀 텔레그램 테스트 발송", use_container_width=True):
        active_id = state.get("active_project_id")
        project = state.get("projects", {}).get(active_id, {})
        proj_name = project.get("name", "프로젝트 없음")
        env_str = "🚀 실전투자"
        target = project.get("target_etf", "N/A")
        
        try:
            _, usd, krw, _ = get_cached_balance(api)
        except Exception:
            usd, krw = 0.0, 0.0
        
        msg = f"""🤖 *cbg 무매40 시스템 알림*

🔹 *실행 환경*: {env_str}
🔹 *진행 프로젝트*: {proj_name}
🔹 *타겟 종목*: {target}
🔹 *외화 예수금*: ${usd:,.2f}
🔹 *원화 예수금*: {krw:,.0f} 원

정상적으로 텔레그램 연동이 완료되었습니다! 🎉"""
        
        success, err = send_telegram_msg(msg)
        if success:
            st.success("✅ 텔레그램으로 테스트 메시지를 성공적으로 발송했습니다!")
        elif err == "Not configured":
            st.error("텔레그램 설정이 필요합니다. (.env 확인)")
        else:
            st.error(f"❌ 발송 실패: {err}")
                


# ==========================================
# 🔝 상단 Header Bar (Pro 타이틀)
# ==========================================
st.markdown('''
<div style="margin-bottom: 20px;">
    <span style="font-size: 1.4rem; font-weight:900; color:#ffffff;">cbg 무매40</span>
</div>
''', unsafe_allow_html=True)

projects_dict = state.get("projects", {})

# ==========================================
# 📊 상단 스마트 계좌 브리핑 (Executive Summary)
# ==========================================
if "token_retry_cnt" not in st.session_state:
    st.session_state.token_retry_cnt = 0

try:
    holdings, usd_cash_val, krw_cash_val, _ = get_cached_balance(api)
    st.session_state.token_retry_cnt = 0  # 성공 시 리셋
except Exception:
    if st.session_state.token_retry_cnt < 2:
        st.session_state.token_retry_cnt += 1
        st.warning(f"🔄 증권사 보안 토큰을 발급 중입니다... 3초 후 자동으로 새로고침됩니다. (자동 재시도 {st.session_state.token_retry_cnt}/2)")
        time.sleep(3)
        st.rerun()
    else:
        usd_cash_val = None
        krw_cash_val = None
        st.error("⚠️ 증권사 API 접속이 지연되고 있습니다. 나중에 수동으로 새로고침(Cmd+R)해주세요.")

active_proj_count = len(projects_dict)
total_allocated_budget = sum(float(p.get("total_budget", 10000.0)) for p in projects_dict.values())
total_spent_budget = sum(float(p.get("total_spent", 0.0)) for p in projects_dict.values())

with st.container(border=False):
    st.markdown('<div class="pro-card-marker" style="display:none;"></div>', unsafe_allow_html=True)
    usd_display = f"${usd_cash_val:,.2f}" if usd_cash_val is not None else "⚠️ 조회 실패"
    krw_display = f"{krw_cash_val:,.0f} 원" if krw_cash_val is not None else "⚠️ 조회 실패"
    
    summary_html = f'''
    <div class="summary-grid" style="grid-template-columns: repeat(2, 1fr); margin-bottom: 15px;">
        <div class="summary-item">
            <div class="summary-label">외화 예수금</div>
            <div class="summary-val" style="color: {'#f87171' if usd_cash_val is None else 'inherit'};">{usd_display}</div>
        </div>
        <div class="summary-item">
            <div class="summary-label">원화 예수금</div>
            <div class="summary-val" style="color: {'#f87171' if krw_cash_val is None else 'inherit'};">{krw_display}</div>
        </div>
    </div>
    '''
    st.markdown(summary_html, unsafe_allow_html=True)
    
    b_col1, b_col2, b_col3 = st.columns([1, 4, 1])
    with b_col2:
        if st.button("실 계좌정보 ReLoad", use_container_width=True):
            get_cached_balance.clear() # 잔고 캐시 날리기
            st.session_state.pop("krw_usd_rate", None) # 환율 캐시 날리기
            st.session_state.ticker_price_cache = {} # 현재가 캐시 날리기
            st.rerun() # 화면 즉시 새로고침

# ==========================================
# ➕ 새 프로젝트 생성 화면
# ==========================================
if st.session_state.view_mode == "CREATE" or not projects_dict:
    st.markdown("### 새 프로젝트 생성")
    with st.container(border=True):
        new_p_ticker = st.selectbox("매매 종목 선택", ["SOXL", "TQQQ"], key="create_p_ticker")
        existing_count = sum(1 for p in projects_dict.values() if p.get("target_etf") == new_p_ticker)
        

        if "ticker_price_cache" not in st.session_state:
            st.session_state.ticker_price_cache = {}
        if new_p_ticker not in st.session_state.ticker_price_cache:
            try:
                st.session_state.ticker_price_cache[new_p_ticker] = api.get_current_price(new_p_ticker)
            except:
                st.session_state.ticker_price_cache[new_p_ticker] = 0.0
                
        curr_price = st.session_state.ticker_price_cache.get(new_p_ticker, 0.0)
        
        # 환율 캐싱 로직
        if "krw_usd_rate" not in st.session_state:
            try:
                import requests
                res = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/KRW=X", headers={"User-Agent": "Mozilla/5.0"}, timeout=3)
                rate = res.json()["chart"]["result"][0]["meta"]["regularMarketPrice"]
                st.session_state.krw_usd_rate = float(rate)
            except:
                st.session_state.krw_usd_rate = 1400.0 # 조회 실패 시 기본값
        
        exch_rate = st.session_state.krw_usd_rate

        
        new_p_splits = st.number_input("분할 회차 (Splits)", min_value=10, max_value=60, value=40, step=1)
        min_usd = curr_price * 2 * new_p_splits
        min_krw = min_usd * exch_rate
        min_budget_str = f" (최소 권장: ${min_usd:,.0f} / 약 {min_krw:,.0f}원)" if curr_price > 0 else ""
        
        if "usd_widget" not in st.session_state:
            st.session_state.usd_widget = "10,000"
        if "krw_widget" not in st.session_state:
            st.session_state.krw_widget = "14,000,000"
            
        def format_usd():
            val = st.session_state.usd_widget
            clean_val = ''.join(filter(str.isdigit, val))
            st.session_state.usd_widget = f"{int(clean_val):,}" if clean_val else "0"
            
        def format_krw():
            val = st.session_state.krw_widget
            clean_val = ''.join(filter(str.isdigit, val))
            st.session_state.krw_widget = f"{int(clean_val):,}" if clean_val else "0"
        
        # 입력 폼 밖에서 동적 UI 처리 (st.form 내부에서는 실시간 텍스트 업데이트가 제한됨)
        input_type = st.radio("예산 입력 단위 선택", ["USD (달러)", "KRW (원화)"], horizontal=True)
        if input_type == "USD (달러)":
            st.text_input(f"총 투자 예산 (USD){min_budget_str}", key="usd_widget", on_change=format_usd)
            raw_usd = st.session_state.usd_widget
            new_p_budget_usd = int(''.join(filter(str.isdigit, raw_usd))) if any(c.isdigit() for c in raw_usd) else 0
            st.caption(f"💡 현재 환율(약 {exch_rate:,.1f}원) 기준, **약 {new_p_budget_usd * exch_rate:,.0f}원**이 소모됩니다.")
            final_budget_usd = new_p_budget_usd
        else:
            st.text_input(f"총 투자 예산 (KRW){min_budget_str}", key="krw_widget", on_change=format_krw)
            raw_krw = st.session_state.krw_widget
            new_p_budget_krw = int(''.join(filter(str.isdigit, raw_krw))) if any(c.isdigit() for c in raw_krw) else 0
            converted_usd = round(new_p_budget_krw / exch_rate)
            st.caption(f"💡 현재 환율(약 {exch_rate:,.1f}원) 기준, **약 ${converted_usd:,.0f}**로 설정됩니다.")
            final_budget_usd = converted_usd
            
        import streamlit.components.v1 as components
        components.html("""
        <script>
            setInterval(() => {
                const inputs = window.parent.document.querySelectorAll('input[aria-label^="총 투자 예산"]');
                if (inputs.length > 0) {
                    inputs.forEach(input => {
                        if (!input.dataset.commaListener) {
                            input.dataset.commaListener = 'true';
                            input.addEventListener('input', function(e) {
                                let cursorPosition = this.selectionStart;
                                let oldLength = this.value.length;
                                
                                let val = this.value.replace(/[^0-9]/g, '');
                                if (val) {
                                    let newVal = parseInt(val, 10).toLocaleString('en-US');
                                    if (this.value !== newVal) {
                                        let nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                                        nativeInputValueSetter.call(this, newVal);
                                        this.dispatchEvent(new Event('input', { bubbles: true }));
                                        
                                        let newLength = this.value.length;
                                        cursorPosition = cursorPosition + (newLength - oldLength);
                                        this.setSelectionRange(cursorPosition, cursorPosition);
                                    }
                                } else {
                                    if (this.value !== "") {
                                        let nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                                        nativeInputValueSetter.call(this, "");
                                        this.dispatchEvent(new Event('input', { bubbles: true }));
                                    }
                                }
                            });
                        }
                    });
                }
            }, 300);
        </script>
        """, height=0)
            
        is_budget_valid = (final_budget_usd >= min_usd)
        if not is_budget_valid:
            st.error(f"⚠️ 예산 부족: 최소 권장 예산(${min_usd:,.0f} / 약 {min_krw:,.0f}원) 이상을 입력하셔야 정상적으로 봇이 동작합니다.")
            
        recommended_name = f"{new_p_ticker} {existing_count + 1}차 ({new_p_splits}회차 - ${final_budget_usd:,.0f})"
    
        with st.form("create_proj_form", border=False):
            new_p_name = st.text_input("프로젝트 이름", value=recommended_name, placeholder=f"예: {recommended_name}")
            
            create_submit = st.form_submit_button("새 프로젝트 생성 및 매매 시작", type="primary", use_container_width=True, disabled=not is_budget_valid)
            
            if create_submit:
                # 버튼 비활성화로 막았지만, 2중 안전장치 유지
                if not is_budget_valid:
                    st.stop()
                    
                final_name = new_p_name.strip() if new_p_name.strip() else recommended_name
                new_id = f"proj_{int(time.time())}"
                if "projects" not in state or not isinstance(state.get("projects"), dict):
                    state["projects"] = {}
                state["projects"][new_id] = {
                    "id": new_id,
                    "name": final_name,
                    "target_etf": new_p_ticker,
                    "total_budget": float(final_budget_usd),
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
                success, new_sha = db.update_state(state, sha)
                if success:
                    st.session_state.view_mode = "LIST"
                    st.success(f"🎉 [{final_name}] 프로젝트가 생성되었습니다!")
                    st.rerun()
                else:
                    st.error("⚠️ 깃허브 DB 업데이트에 실패했습니다. 일시적인 서버 오류일 수 있으니 잠시 후 다시 시도해주세요.")

    if projects_dict:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("취소", use_container_width=True):
                st.session_state.view_mode = "LIST"
                st.rerun()
            
    st.stop()


# ==========================================
# 📋 VIEW MODE 1: 프로젝트 목록 (Pro Card LIST)
# ==========================================
if st.session_state.view_mode == "LIST":
    list_hdr_col1, list_hdr_col2 = st.columns([3, 2])
    with list_hdr_col2:
        if st.button("➕ 프로젝트 추가", key="list_add_project_btn", use_container_width=False):
            st.session_state.view_mode = "CREATE"
            st.rerun()
    
    p_items = list(projects_dict.values())
    for p in p_items:
        p_id = p["id"]
        ticker = p.get("target_etf", "TQQQ")
        splits_cnt = int(p.get('splits', 40))
        total_budget = float(p.get("total_budget", 10000.0))
        
        # 실시간 계좌 연동 (자동 동기화)
        target_holding = None
        for hold in holdings:
            if hold.get("ovrs_pdno") == ticker or hold.get("pdno") == ticker or hold.get("pd_no") == ticker:
                target_holding = hold
                break
                
        if target_holding:
            db_shares = float(target_holding.get("ovrs_cblc_qty", target_holding.get("allo_qty", 0.0)))
            db_avg_price = float(target_holding.get("pchs_avg_pric", 0.0))
            total_spent = float(target_holding.get("frcr_pchs_amt1", db_shares * db_avg_price))
        else:
            db_shares = 0.0
            db_avg_price = 0.0
            total_spent = 0.0
        
        # 현재가 조회 (오류 시 평단 또는 0)
        try:
            curr_price = get_cached_price(api, ticker)
        except Exception:
            curr_price = 0.0
        display_curr = curr_price if curr_price > 0 else db_avg_price
        
        # 수익률 계산
        if db_avg_price > 0 and display_curr > 0:
            pnl_pct = ((display_curr - db_avg_price) / db_avg_price) * 100
            if pnl_pct > 0:
                pnl_html = f'<span style="color:#34d399;">+{pnl_pct:.2f}%</span>'
            elif pnl_pct < 0:
                pnl_html = f'<span style="color:#f87171;">{pnl_pct:.2f}%</span>'
            else:
                pnl_html = '0.00%'
        else:
            pnl_html = '0.00%'

        # 일일 예산 고정 (정액 분할 매수)
        daily_budget = total_budget / splits_cnt if splits_cnt > 0 else 0.0
        
        # 실계좌 누적 매수금액 기반 회차 자동 추정
        if daily_budget > 0:
            turn_cnt = round(total_spent / daily_budget, 1)
        else:
            turn_cnt = 0.0
        
        # 주식 매도 후 수량이 0이면 회차 리셋
        if db_shares == 0:
            turn_cnt = 0.0
            
        prog_pct = min(100, int((turn_cnt / splits_cnt) * 100)) if splits_cnt > 0 else 0
        
        card_b1_price = db_avg_price if db_avg_price > 0 else display_curr
        card_b1_qty = math.floor((daily_budget * 0.5) / card_b1_price) if card_b1_price > 0 else 0
        if card_b1_qty == 0 and daily_budget > 0 and card_b1_price > 0:
            card_b1_qty = 1
            
        card_b2_price = display_curr * 1.10 if display_curr > 0 else card_b1_price * 1.10
        card_b2_qty = math.floor((daily_budget * 0.5) / card_b2_price) if card_b2_price > 0 else 0
        if card_b2_qty == 0 and daily_budget > 0 and card_b2_price > 0:
            card_b2_qty = 1

        buy_count = (1 if card_b1_qty > 0 else 0) + (1 if card_b2_qty > 0 else 0)
        sell_count = 1 if db_shares > 0 else 0

        excg_tag = "AMEX" if ticker == "SOXL" else "NASD"

        with st.container(border=False):
            st.markdown('<div class="pro-card-marker" style="display:none;"></div>', unsafe_allow_html=True)
            hdr_col1, hdr_col2 = st.columns([1, 1], vertical_alignment="center")
            with hdr_col1:
                st.markdown(f'<div style="height: 24px; display: flex; align-items: flex-start; transform: translateY(-7px);"><span class="ticker-badge" style="margin:0;">{ticker} · {excg_tag}</span></div>', unsafe_allow_html=True)
            with hdr_col2:
                st.markdown('<div class="del-btn-wrapper" style="display:none;"></div>', unsafe_allow_html=True)
                if st.button("삭제", key=f"del_btn_{p_id}"):
                    confirm_delete_dialog(p_id, p['name'])
        
            # 제목을 버튼으로 렌더링 (CSS 타겟팅을 위한 마커 삽입)
            st.markdown('<div class="title-btn-marker" style="display:none;"></div>', unsafe_allow_html=True)
            if st.button(p['name'], key=f"edit_title_{p_id}", type="tertiary", use_container_width=True, help="클릭하여 제목 수정"):
                edit_title_dialog(p_id, p['name'])

            card_html2 = f"""
    <div class="summary-grid" style="grid-template-columns: repeat(2, 1fr); gap: 10px; margin-top: 4px; margin-bottom: 12px; text-align: center;">
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
    </div>
    <div class="roop-progress-bg">
    <div class="roop-progress-fill" style="width: {prog_pct}%;"></div>
    </div>
    """
            st.markdown(card_html2, unsafe_allow_html=True)

            ord_col1, ord_col2 = st.columns(2)
            with ord_col1:
                buy_html = f"""<div class="buy-box">
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
    </div>"""
                st.markdown(buy_html, unsafe_allow_html=True)

            with ord_col2:
                sell_price = db_avg_price * 1.10
                sell_html = f"""<div class="sell-box">
    <div class="box-title-sell">매도 · LOC / 지정가</div>
    <div class="order-row">
    <div>
    <span class="price-bold">${sell_price:.2f}</span>
    <span class="qty-text"> × {db_shares:g}주</span>
    </div>
    <span class="tag-purple">+10% 익절</span>
    </div>
    </div>"""
                st.markdown(sell_html, unsafe_allow_html=True)

            today_str = pd.Timestamp.now().strftime("%Y-%m-%d")
            
            already_buy1 = False
            already_buy2 = False
            already_sell = False
            
            # 실전투자: 실제 계좌를 조회하여 '취소'되지 않은 주문 내역 확인
            live_orders = api.get_today_live_orders(ticker)
            for order in live_orders:
                oprice = order.get("price", 0.0)
                if order.get("type") == "02": # 매수
                    if abs(oprice - card_b1_price) < 0.01:
                        already_buy1 = True
                    elif abs(oprice - card_b2_price) < 0.01:
                        already_buy2 = True
                elif order.get("type") == "01": # 매도
                    if abs(oprice - sell_price) < 0.01:
                        already_sell = True

            approve_buy1 = True if (card_b1_qty > 0 and not already_buy1) else False
            approve_buy2 = True if (card_b2_qty > 0 and not already_buy2) else False
            approve_sell = True if (db_shares > 0 and not already_sell) else False

            if st.button("주문 전송", key=f"send_btn_{p_id}", type="primary", use_container_width=True):
                time.sleep(1.0)
                success_orders = 0
                fail_orders = 0
                messages = []
                order_data_log = []
                
                # 현재 한국 시간 기준 낮(08시 ~ 22시)이면 예약주문 API 사용
                current_hour = pd.Timestamp.now(tz="Asia/Seoul").hour
                is_daytime_res = (8 <= current_hour < 22)
                res_tag = "[예약] " if is_daytime_res else ""
            
                if not approve_buy1 and not approve_buy2 and not approve_sell:
                    st.info("👍 오늘 필요한 모든 주문이 이미 성공적으로 접수되었습니다! (더 이상 전송할 주문이 없습니다)")
                else:
                    if card_b1_qty > 0:
                        if already_buy1:
                            messages.append(f"⏭️ 절반 매수 (평단가) 스킵  \n[LOC / {card_b1_qty}주]  \n이미 성공하여 스킵 (중복방지)")
                        else:
                            success, res = api.place_order(ticker, card_b1_qty, card_b1_price, order_type="34", is_reservation=is_daytime_res)
                            if success:
                                success_orders += 1
                                messages.append(f"✅ {res_tag}절반 매수 (평단가) 성공  \n[LOC / {card_b1_qty}주 @ ${card_b1_price:.2f}]")
                            else:
                                fail_orders += 1
                                messages.append(f"❌ {res_tag}절반 매수 (평단가) 실패  \n[LOC / {card_b1_qty}주 @ ${card_b1_price:.2f}]  \n{res}")
                            time.sleep(1.0)
                    
                    if card_b2_qty > 0:
                        if already_buy2:
                            messages.append(f"⏭️ 절반 매수 (고가) 스킵  \n[LOC / {card_b2_qty}주]  \n이미 성공하여 스킵 (중복방지)")
                        else:
                            success, res = api.place_order(ticker, card_b2_qty, card_b2_price, order_type="34", is_reservation=is_daytime_res)
                            if success:
                                success_orders += 1
                                messages.append(f"✅ {res_tag}절반 매수 (고가) 성공  \n[LOC / {card_b2_qty}주 @ ${card_b2_price:.2f}]")
                            else:
                                fail_orders += 1
                                messages.append(f"❌ {res_tag}절반 매수 (고가) 실패  \n[LOC / {card_b2_qty}주 @ ${card_b2_price:.2f}]  \n{res}")
                            time.sleep(1.0)
                    
                    if db_shares > 0:
                        if already_sell:
                            messages.append(f"⏭️ 익절 매도 스킵  \n[지정가 / {db_shares}주]  \n이미 성공하여 스킵 (중복방지)")
                        else:
                            success, res = api.place_order(ticker, -db_shares, sell_price, order_type="00", is_reservation=is_daytime_res)
                            if success:
                                success_orders += 1
                                messages.append(f"✅ {res_tag}익절 매도 성공  \n[지정가 / {db_shares:g}주 @ ${sell_price:.2f}]")
                            else:
                                fail_orders += 1
                                messages.append(f"❌ {res_tag}익절 매도 실패  \n[지정가 / {db_shares:g}주 @ ${sell_price:.2f}]  \n{res}")

                    for msg in messages:
                        st.write(msg)
                

            
                if success_orders > 0:
                    if fail_orders == 0:
                        st.success(f"🎉 모든 주문이 성공적으로 전송되었습니다!")
                    else:
                        st.warning(f"⚠️ 일부 주문이 실패했지만, {success_orders}건의 주문 전송에 성공했습니다.")
                        
                # 텔레그램 알림 발송 (전송된 내용이 있을 때만)
                if messages:
                    # 마크다운 포맷을 위해 두 칸 공백 제거 등 텔레그램 용으로 약간 다듬음
                    tele_msgs = [m.replace("  \n", "\n") for m in messages]
                    tele_body = "\n\n".join(tele_msgs)
                    tele_text = f"🤖 *주문 전송 결과 알림*\n\n🔹 *프로젝트*: {p.get('name', '알 수 없는 프로젝트')}\n\n{tele_body}"
                    send_telegram_msg(tele_text)
        



