@echo off
REM ============================================================
REM  계약서 관리 시스템 - 로컬 실행 스크립트 (Windows)
REM  더블클릭하거나 명령 프롬프트에서 run.bat 을 실행하세요.
REM ============================================================
setlocal

cd /d "%~dp0"

echo [1/3] Python 확인 중...
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

if not exist ".venv" (
    echo [2/3] 가상환경 생성 및 패키지 설치 중... 처음 한 번만 시간이 걸립니다.
    python -m venv .venv
    call .venv\Scripts\python.exe -m pip install --upgrade pip -q
    call .venv\Scripts\pip.exe install -r requirements.txt -q
) else (
    echo [2/3] 가상환경 확인 완료.
    call .venv\Scripts\pip.exe install -r requirements.txt -q
)

echo [3/3] 서버 실행 중...
echo.
echo   브라우저에서 아래 주소로 접속하세요:
echo      http://localhost:5002
echo.
echo   종료하려면 이 창에서 Ctrl+C 를 누르세요.
echo.

call .venv\Scripts\python.exe app.py

pause
endlocal
