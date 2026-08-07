@echo off
REM ============================================================
REM  계약서 관리 목업 - 라이브 프리뷰 개발 서버 (Windows)
REM  더블클릭하면 브라우저가 열리고, 파일 저장 시 자동 새로고침됩니다.
REM  추가 설치 없이 Python 만 있으면 됩니다.
REM ============================================================
setlocal
cd /d "%~dp0"

where python >nul 2>&1
if errorlevel 1 (
    echo.
    echo [오류] Python 이 설치되어 있지 않습니다.
    echo        https://www.python.org/downloads/ 에서 설치 후 다시 실행하세요.
    echo        설치 시 "Add Python to PATH" 옵션을 반드시 체크하세요.
    echo.
    pause
    exit /b 1
)

python dev_server.py

pause
endlocal
