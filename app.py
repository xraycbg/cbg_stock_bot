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
# 아이폰 & 모바일 최적화 커스텀 프리미엄 CSS
# ------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&family=Noto+Sans+KR:wght@400;600;700;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', 'Noto Sans KR', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background: radial-gradient(circle at 50% -20%, #1e1b4b 0%, #0f172a 70%, #090d16 100%);
        color: #f8fafc;
    }
    
    /* Streamlit 상단 헤더 영역 투명화 */
    header[data-testid="stHeader"], [data-testid="stHeader"] {
        background-color: transparent !important;
        z-index: 1 !important;
    }
    
    /* 패딩 및 컨테이너 여백 최적화 (아이폰 노치 대응) */
    .block-container {
        padding-top: 4rem !important;
        padding-bottom: 3rem !important;
        max-width: 1050px;
    }
    
    /* 모바일 반응형 조절 (iPhone 사파리/크롬 상단 잘림 방지) */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 0.8rem !important;
            padding-right: 0.8rem !important;
            padding-top: 4.2rem !important;
        }
        .title-gradient {
            font-size: 1.55rem !important;
            margin-top: 0.3rem !important;
        }
        .card {
            padding: 16px 14px !important;
            border-radius: 16px !important;
            margin-bottom: 14px !important;
        }

        [data-testid="stMetricValue"] {
            font-size: 1.2rem !important;
        }
        [data-testid="stMetricLabel"] {
            font-size: 0.78rem !important;
        }
        div.stButton > button {
            width: 100% !important;
            border-radius: 12px !important;
            padding: 12px 14px !important;
            font-size: 0.95rem !important;
        }
    }
    
    /* 글래스모피즘 카드 디자인 */
    .card {
        background: rgba(30, 41, 59, 0.65);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 22px 24px;
        margin-bottom: 18px;
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.3);
    }
    
    .card-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #94a3b8;
        margin-bottom: 14px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    
    /* 타이틀 그라데이션 */
    .title-gradient {
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.1rem;
        margin-bottom: 4px;
        letter-spacing: -0.5px;
    }
    
    /* 티커 뱃지 */
    .badge-ticker {
        background: linear-gradient(135deg, #0284c7 0%, #4f46e5 100%);
        color: #ffffff;
        padding: 4px 14px;
        border-radius: 20px;
        font-weight: 800;
        font-size: 0.85rem;
        display: inline-block;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3);
        margin-bottom: 8px;
    }
    
    /* 주문 아이템 모바일 카드 디자인 */
    .order-card {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 14px 16px;
        margin-bottom: 10px;
    }
    
    .order-type-buy {
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 700;
        display: inline-block;
    }
    
    .order-type-sell {
        background: rgba(239, 68, 68, 0.15);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.3);
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 700;
        display: inline-block;
    }
    
    /* 회차 프로그레스 바 */
    .progress-bar-bg {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        height: 8px;
        width: 100%;
        overflow: hidden;
        margin-top: 8px;
        margin-bottom: 12px;
    }
    
    .progress-bar-fill {
        background: linear-gradient(90deg, #38bdf8 0%, #818cf8 100%);
        height: 100%;
        border-radius: 10px;
    }
    
    /* 경고 & 성공 박스 */
    .warning-box {
        background-color: rgba(245, 158, 11, 0.12);
        border-left: 4px solid #f59e0b;
        color: #fef3c7;
        padding: 14px 16px;
        border-radius: 12px;
        margin-bottom: 16px;
        font-size: 0.9rem;
    }
    
    .success-box {
        background-color: rgba(16, 185, 129, 0.12);
        border-left: 4px solid #10b981;
        color: #d1fae5;
        padding: 14px 16px;
        border-radius: 12px;
        margin-bottom: 16px;
        font-size: 0.9rem;
    }
    
    /* 버튼 호버 및 마이크로 애니메이션 */
    div.stButton > button {
        border-radius: 12px !important;
        font-weight: 700 !important;
        transition: all 0.2s ease !important;
    }
    
    div.stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(56, 189, 248, 0.25);
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
# 고유 ID 기반 다중 프로젝트 정규화 함수
# ------------------------------------------
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
            "name": f"{old_target} 1차 프로젝트",
            "target_etf": old_target,
            "total_budget": float(s.get("total_budget", 10000.0)),
            "splits": int(s.get("splits", 40)),
            "turn": int(s.get("turn", 0)),
            "avg_price": float(s.get("avg_price", 0.0)),
            "total_shares": float(s.get("total_shares", 0.0)),
            "total_spent": float(s.get("total_spent", 0.0)),
            "status": s.get("status", "BUYING"),
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
                "status": p.get("status", "BUYING"),
                "created_at": p.get("created_at", time.strftime("%Y-%m-%d %H:%M:%S")),
                "history": p.get("history", [])
            }
            
        s["projects"] = new_projects
        if s.get("active_project_id") not in new_projects:
            s["active_project_id"] = list(new_projects.keys())[0] if new_projects else None
            
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

# ==========================================
# 뷰 모드 관리 (LIST: 목록보기 / DETAIL: 세부사항)
# ==========================================
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "LIST"

# 사이드바 설정
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
    st.markdown("### 📂 프로젝트 내비게이션")
    if st.button("📋 전체 프로젝트 목록 보기", use_container_width=True):
        st.session_state.view_mode = "LIST"
        st.rerun()
        
    st.markdown("---")
    st.markdown("### 💾 GitHub DB 상태")
    st.text(f"Repo: {db.repo}")
    st.text(f"Path: {db.file_path}")
    if st.button("🔄 GitHub DB 다시 불러오기"):
        st.cache_data.clear()
        st.rerun()

# 타이틀 헤더
st.markdown('<div class="title-gradient">📈 루프 무한매수법 V4.0</div>', unsafe_allow_html=True)
st.markdown('<p style="color: #94a3b8; margin-bottom: 20px; font-size: 0.95rem;">라오어 무한매수법 4.0 프로젝트 관리 및 한투 자동 예약주문</p>', unsafe_allow_html=True)

projects_dict = state.get("projects", {})

# ==========================================
# 📋 VIEW MODE 1: 프로젝트 목록 화면 (LIST)
# ==========================================
if st.session_state.view_mode == "LIST" or not projects_dict:
    st.markdown("## 📂 내 프로젝트 목록")
    
    # 1. 새 프로젝트 생성 영역
    with st.expander("➕ 새 무한매수 4.0 프로젝트 생성", expanded=True if not projects_dict else False):
        col_sel1, _ = st.columns([2, 2])
        with col_sel1:
            new_p_ticker = st.selectbox("🎯 매매 종목 선택", ["TQQQ", "SOXL"], key="create_p_ticker")
        
        existing_count = sum(1 for p in projects_dict.values() if p.get("target_etf") == new_p_ticker)
        recommended_name = f"{new_p_ticker} {existing_count + 1}차 프로젝트"

        with st.form("create_proj_form"):
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                new_p_name = st.text_input("프로젝트 이름", value=recommended_name, placeholder=f"예: {recommended_name}")
                new_p_budget = st.number_input("💰 총 투자 예산 ($USD)", min_value=100.0, value=10000.0, step=500.0)
            with col_c2:
                new_p_splits = st.number_input("⏳ 분할 회차 (Splits)", min_value=10, max_value=60, value=40)
                st.write("")
                st.write("")
                create_submit = st.form_submit_button("✨ 새 루프 V4.0 프로젝트 시작 및 저장", type="primary", use_container_width=True)
                
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
                    "status": "BUYING",
                    "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "history": []
                }
                state["active_project_id"] = new_id
                db.update_state(state, sha)
                st.session_state.view_mode = "DETAIL"
                st.success(f"🎉 [{final_name}] 프로젝트가 생성되었습니다!")
                time.sleep(1)
                st.rerun()

    # 2. 기존 프로젝트 카드 목록 (모바일 응답형 레이아웃)
    if projects_dict:
        st.markdown("### 📋 보유 프로젝트 카드 목록")
        
        p_items = list(projects_dict.values())
        for i in range(0, len(p_items), 2):
            cols = st.columns(2)
            for j in range(2):
                if i + j < len(p_items):
                    p = p_items[i + j]
                    p_id = p["id"]
                    turn_cnt = int(p.get('turn', 0))
                    splits_cnt = int(p.get('splits', 40))
                    prog_pct = min(100, int((turn_cnt / splits_cnt) * 100)) if splits_cnt > 0 else 0
                    
                    with cols[j]:
                        st.markdown('<div class="card">', unsafe_allow_html=True)
                        st.markdown(f'<span class="badge-ticker">{p["target_etf"]}</span>', unsafe_allow_html=True)
                        st.markdown(f'<h3 style="margin-top:2px; margin-bottom: 8px;">{p["name"]}</h3>', unsafe_allow_html=True)
                        
                        # 회차 프로그레스 바
                        st.markdown(f'''
                        <div style="font-size: 0.85rem; color: #94a3b8;">진행 회차: <b>{turn_cnt}</b> / {splits_cnt} 회 ({prog_pct}%)</div>
                        <div class="progress-bar-bg"><div class="progress-bar-fill" style="width: {prog_pct}%;"></div></div>
                        ''', unsafe_allow_html=True)
                        
                        mc1, mc2 = st.columns(2)
                        mc1.metric("총 예산", f"${p.get('total_budget', 0):,.0f}")
                        mc2.metric("DB 평균 매수가", f"${p.get('avg_price', 0):.2f}")
                        
                        st.write(f"⏱️ 생성일: {p.get('created_at', 'N/A')}")
                        
                        b_col1, b_col2 = st.columns([2.2, 1])
                        with b_col1:
                            if st.button(f"🔍 세부사항 & 매매 실행", key=f"btn_detail_{p_id}", type="primary", use_container_width=True):
                                state["active_project_id"] = p_id
                                db.update_state(state, sha)
                                st.session_state.view_mode = "DETAIL"
                                st.rerun()
                        with b_col2:
                            if st.button(f"🗑️ 삭제", key=f"btn_del_{p_id}", use_container_width=True):
                                del state["projects"][p_id]
                                if state.get("active_project_id") == p_id:
                                    rem = list(state["projects"].keys())
                                    state["active_project_id"] = rem[0] if rem else None
                                db.update_state(state, sha)
                                st.success("프로젝트가 삭제되었습니다.")
                                time.sleep(1)
                                st.rerun()

                        with st.expander("✏️ 프로젝트 이름 수정"):
                            with st.form(f"rename_form_{p_id}"):
                                rename_input = st.text_input("새 프로젝트 이름", value=p["name"])
                                rename_btn = st.form_submit_button("💾 이름 저장")
                                if rename_btn:
                                    if rename_input.strip():
                                        state["projects"][p_id]["name"] = rename_input.strip()
                                        db.update_state(state, sha)
                                        st.success("이름이 변경되었습니다!")
                                        time.sleep(1)
                                        st.rerun()

                        st.markdown('</div>', unsafe_allow_html=True)
                        
    st.stop()

# ==========================================
# 🔍 VIEW MODE 2: 프로젝트 세부사항 및 매매 대시보드 (DETAIL)
# ==========================================
active_id = state.get("active_project_id")
if not active_id or active_id not in projects_dict:
    st.session_state.view_mode = "LIST"
    st.rerun()

project_data = projects_dict[active_id]
target_etf = project_data["target_etf"]

# 모바일 대응 상단 내비게이션
if st.button("← 📂 프로젝트 목록으로 돌아가기", key="back_to_list_btn"):
    st.session_state.view_mode = "LIST"
    st.rerun()

st.markdown(f'<span class="badge-ticker">{target_etf}</span>', unsafe_allow_html=True)
st.markdown(f'<h2 style="margin-top: 2px; margin-bottom: 12px;">{project_data["name"]}</h2>', unsafe_allow_html=True)

with st.expander(f"✏️ 프로젝트 이름 수정"):
    with st.form("detail_rename_form"):
        detail_name_val = st.text_input("프로젝트 이름", value=project_data["name"])
        detail_rename_btn = st.form_submit_button("💾 변경사항 저장")
        if detail_rename_btn:
            if detail_name_val.strip():
                state["projects"][active_id]["name"] = detail_name_val.strip()
                db.update_state(state, sha)
                st.success("프로젝트 이름이 변경되었습니다!")
                time.sleep(1)
                st.rerun()

# 시세 및 잔고 API 조회
with st.spinner(f"[{project_data['name']}] 계좌 잔고 로딩 중..."):
    try:
        current_price = api.get_current_price(target_etf)
    except Exception as e:
        current_price = 0.0
        st.sidebar.error(f"시세 조회 실패: {e}")
        
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

# 싱크 상태 점검
db_shares = float(project_data.get("total_shares", 0.0))
db_avg_price = float(project_data.get("avg_price", 0.0))
is_synced = (db_shares == actual_shares) and (abs(db_avg_price - actual_avg_price) < 0.01)

if is_synced:
    st.markdown(f'<div class="success-box">✅ <b>일치 완료:</b> [{project_data["name"]}] DB 정보와 실제 한국투자증권 계좌 잔고가 일치합니다.</div>', unsafe_allow_html=True)
else:
    st.markdown(f'''
    <div class="warning-box">
        ⚠️ <b>상태 불일치 감지:</b> [{project_data["name"]}] DB 수량({db_shares}주)과 실제 계좌 수량({actual_shares}주)이 다릅니다.
    </div>
    ''', unsafe_allow_html=True)
    
    if st.button(f"🛠️ DB를 실제 계좌 기준({target_etf})으로 동기화"):
        project_data["total_shares"] = actual_shares
        project_data["avg_price"] = actual_avg_price
        project_data["total_spent"] = actual_shares * actual_avg_price
        if actual_shares == 0:
            project_data["turn"] = 0
            project_data["status"] = "BUYING"
            
        state["projects"][active_id] = project_data
        success, new_sha = db.update_state(state, sha)
        if success:
            st.success("동기화 완료!")
            time.sleep(1)
            st.rerun()

# 대시보드 메트릭 카드
col1, col2 = st.columns(2)

with col1:
    st.markdown(f'<div class="card"><div class="card-title">📁 프로젝트 진행 현황</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("진행 회차 (T)", f"{project_data.get('turn', 0)} / {project_data.get('splits', 40)} 회")
    c2.metric("DB 평단가", f"${db_avg_price:.2f}")
    c3.metric("DB 수량", f"{db_shares} 주")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card"><div class="card-title">🏦 한투 계좌 현황 & 예수금</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("예수금 (USD)", f"${usd_cash:,.2f}")
    c2.metric(f"실제 {target_etf} 수량", f"{actual_shares} 주")
    c3.metric(f"실제 {target_etf} 평단", f"${actual_avg_price:.2f}")
    st.markdown('</div>', unsafe_allow_html=True)

if holdings:
    with st.expander("💼 계좌 전체 보유 종목 상세 보기"):
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

# 실시간 시세 및 손익
st.markdown('<div class="card"><div class="card-title">📊 실시간 시장 시세 및 손익</div>', unsafe_allow_html=True)
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

# V4.0 가이드라인 & 주문 계산
st.markdown(f'<div class="card"><div class="card-title">📝 오늘의 매매 가이드라인</div>', unsafe_allow_html=True)

turn = int(project_data.get("turn", 0))
splits = int(project_data.get("splits", 40))
total_budget = float(project_data.get("total_budget", 10000.0))

if turn >= splits:
    st.warning("⚠️ 이미 40회차 매수를 완료하였습니다. 추가 예수금을 투입하여 연장하거나 리버스를 고려해 주세요.")
    daily_buy_budget = 0.0
else:
    remaining_budget = total_budget - total_spent
    daily_buy_budget = remaining_budget / (splits - turn)

st.write(f"👉 **총 예산**: **${total_budget:,.2f}** | **오늘 1회 매수 설정액**: **${daily_buy_budget:.2f}** (남은 예산 ${remaining_budget:.2f}의 1/{splits - turn})")

buy1_price = db_avg_price if db_avg_price > 0 else current_price
buy1_qty = math.floor((daily_buy_budget * 0.5) / buy1_price) if buy1_price > 0 else 0

buy2_price = current_price * 1.10
buy2_qty = math.floor((daily_buy_budget * 0.5) / buy2_price) if buy2_price > 0 else 0

sell_price = db_avg_price * 1.10
sell_qty = db_shares

# 모바일 응답형 주문 카드 출력
st.markdown("#### 🛒 예정 주문 목록")

st.markdown(f'''
<div class="order-card">
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <span class="order-type-buy">📍 매수 1순위 (평단 LOC)</span>
        <span style="font-size:0.85rem; color:#94a3b8;">LOC 매수 (34)</span>
    </div>
    <div style="display:flex; justify-content:space-between; align-items:center; margin-top:4px;">
        <span style="font-size:1.1rem; font-weight:800;">{buy1_qty} 주</span>
        <span style="font-size:1.1rem; font-weight:800; color:#38bdf8;">${buy1_price:.2f}</span>
    </div>
    <div style="font-size:0.8rem; color:#64748b; text-align:right;">예상금액: ${(buy1_qty * buy1_price):,.2f}</div>
</div>

<div class="order-card">
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <span class="order-type-buy">🔥 매수 2순위 (고가 LOC)</span>
        <span style="font-size:0.85rem; color:#94a3b8;">LOC 매수 (34)</span>
    </div>
    <div style="display:flex; justify-content:space-between; align-items:center; margin-top:4px;">
        <span style="font-size:1.1rem; font-weight:800;">{buy2_qty} 주</span>
        <span style="font-size:1.1rem; font-weight:800; color:#38bdf8;">${buy2_price:.2f}</span>
    </div>
    <div style="font-size:0.8rem; color:#64748b; text-align:right;">예상금액: ${(buy2_qty * buy2_price):,.2f}</div>
</div>
''', unsafe_allow_html=True)

if sell_qty > 0:
    st.markdown(f'''
    <div class="order-card">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span class="order-type-sell">💰 매도 (10% 익절 지정가)</span>
            <span style="font-size:0.85rem; color:#94a3b8;">지정가 매도 (00)</span>
        </div>
        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:4px;">
            <span style="font-size:1.1rem; font-weight:800;">{sell_qty} 주</span>
            <span style="font-size:1.1rem; font-weight:800; color:#f87171;">${sell_price:.2f}</span>
        </div>
        <div style="font-size:0.8rem; color:#64748b; text-align:right;">예상금액: ${(sell_qty * sell_price):,.2f}</div>
    </div>
    ''', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# 1-클릭 주문 승인 섹션
st.markdown('<div class="card"><div class="card-title">⚡ 주문 검토 및 승인 전송</div>', unsafe_allow_html=True)
st.write("주문 내역을 체크 후 아래 버튼을 누르면 한국투자증권 계좌로 즉시 예약 주문이 접수됩니다.")

col_b1, col_b2, col_s = st.columns(3)
with col_b1:
    approve_buy1 = st.checkbox("주문 1 승인 (평단 LOC)", value=True if buy1_qty > 0 else False, disabled=buy1_qty == 0)
with col_b2:
    approve_buy2 = st.checkbox("주문 2 승인 (고가 LOC)", value=True if buy2_qty > 0 else False, disabled=buy2_qty == 0)
with col_s:
    approve_sell = st.checkbox("주문 3 승인 (익절 매도)", value=True if sell_qty > 0 else False, disabled=sell_qty == 0)

if st.button(f"🚀 [{project_data['name']}] 주문들을 한국투자증권으로 전송", type="primary", use_container_width=True):
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
        st.success(f"🎉 모든 주문이 접수되었습니다! [{project_data['name']}] 회차를 업데이트합니다.")
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
            st.success("💾 깃허브 DB 업데이트 완료! 3초 후 갱신됩니다.")
            time.sleep(3)
            st.rerun()
    elif fail_orders > 0:
        st.error("일부 주문이 실패하였습니다. 계좌 또는 API 설정을 확인해 주세요.")

st.markdown('</div>', unsafe_allow_html=True)

# 수동 상태 조절
with st.expander(f"🛠️ [{project_data['name']}] 수동 상태 조정 (비상용)"):
    st.write("깃허브 DB 파라미터를 수동 변경합니다.")
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

    if st.button(f"💾 [{project_data['name']}] 수동 변경사항 깃허브 DB 저장"):
        project_data["turn"] = int(edit_turn)
        project_data["total_budget"] = edit_budget
        project_data["total_shares"] = edit_shares
        project_data["avg_price"] = edit_avg_price
        project_data["splits"] = int(edit_splits)
        project_data["status"] = edit_status
        project_data["total_spent"] = edit_shares * edit_avg_price
        
        state["projects"][active_id] = project_data
        success, new_sha = db.update_state(state, sha)
        if success:
            st.success("수동 변경사항이 저장되었습니다.")
            time.sleep(1)
            st.rerun()
