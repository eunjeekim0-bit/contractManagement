#!/usr/bin/env bash
# ============================================================
#  계약서 관리 목업 - 라이브 프리뷰 개발 서버 (macOS / Linux)
#  터미널에서 ./serve.sh 로 실행하세요.
#  브라우저가 열리고, 파일 저장 시 자동 새로고침됩니다.
#  추가 설치 없이 Python 만 있으면 됩니다.
# ============================================================
set -e
cd "$(dirname "$0")"

if command -v python3 >/dev/null 2>&1; then
    PY=python3
elif command -v python >/dev/null 2>&1; then
    PY=python
else
    echo "[오류] Python 이 설치되어 있지 않습니다. https://www.python.org/downloads/ 에서 설치하세요."
    exit 1
fi

exec "$PY" dev_server.py
