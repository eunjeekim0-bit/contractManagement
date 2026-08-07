#!/usr/bin/env bash
# ============================================================
#  계약서 관리 시스템 - 로컬 실행 스크립트 (macOS / Linux)
#  터미널에서  ./run.sh  로 실행하세요.
# ============================================================
set -e

cd "$(dirname "$0")"

# python 명령 결정 (python3 우선)
if command -v python3 >/dev/null 2>&1; then
    PY=python3
elif command -v python >/dev/null 2>&1; then
    PY=python
else
    echo "[오류] Python 이 설치되어 있지 않습니다. https://www.python.org/downloads/ 에서 설치하세요."
    exit 1
fi

echo "[1/3] Python 확인: $($PY --version)"

if [ ! -d ".venv" ]; then
    echo "[2/3] 가상환경 생성 및 패키지 설치 중... 처음 한 번만 시간이 걸립니다."
    "$PY" -m venv .venv
    .venv/bin/python -m pip install --upgrade pip -q
    .venv/bin/pip install -r requirements.txt -q
else
    echo "[2/3] 가상환경 확인 완료."
    .venv/bin/pip install -r requirements.txt -q
fi

echo "[3/3] 서버 실행 중..."
echo ""
echo "  브라우저에서 아래 주소로 접속하세요:"
echo "     http://localhost:5002"
echo ""
echo "  종료하려면 Ctrl+C 를 누르세요."
echo ""

exec .venv/bin/python app.py
