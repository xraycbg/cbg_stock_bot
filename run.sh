#!/bin/bash
# cbg_stock_bot 실행 스크립트

echo "========================================="
      echo "📈 무한매수법 V4.0 봇 구동 시작"
echo "========================================="

# requirements.txt에 명시된 라이브러리 자동 설치
echo "1. 파이썬 라이브러리 검사 및 설치 중..."
pip install -r requirements.txt

# Streamlit 실행
echo "2. Streamlit 대시보드 서버 실행 중..."
streamlit run app.py
