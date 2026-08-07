# 계약서 관리 시스템

계약서 조회(Hub), 의무조항 관리, Dashboard 를 제공하는 사내 웹 애플리케이션입니다.
Flask 기반이며, 데이터는 `data/` 폴더의 JSON 파일을 사용합니다.

---

## 로컬에서 실행하기

### 가장 쉬운 방법 (실행 스크립트)

**Windows**

`run.bat` 파일을 더블클릭하거나, 명령 프롬프트에서 실행합니다.

```
run.bat
```

**macOS / Linux**

터미널에서 실행합니다.

```bash
./run.sh
```

스크립트가 자동으로 가상환경(`.venv`)을 만들고, 필요한 패키지를 설치한 뒤 서버를 실행합니다.
(처음 한 번만 설치에 시간이 조금 걸립니다.)

실행되면 브라우저에서 접속하세요:

👉 **http://localhost:5002**

종료하려면 실행 중인 창에서 `Ctrl + C` 를 누릅니다.

---

### 직접 실행하기 (수동 설정)

Python 3.9 이상이 필요합니다.

```bash
# 1. 가상환경 생성
python -m venv .venv

# 2. 가상환경 활성화
#    Windows:
.venv\Scripts\activate
#    macOS / Linux:
source .venv/bin/activate

# 3. 패키지 설치
pip install -r requirements.txt

# 4. 서버 실행
python app.py
```

접속: **http://localhost:5002**

---

## 화면 구성

| 메뉴 | 경로 | 설명 |
|------|------|------|
| 계약서 Hub | `/` | 계약서 검색 및 목록 조회 |
| 의무조항 관리 | `/obligations` | 정량/정성 의무조항 조회 및 상태 관리 |
| Dashboard | `/dashboard` | 유효 계약, 만료 예정, 기한 초과 의무 현황 |
| Q&A AI Agent | (외부) | `app.py` 의 `AGENT_URL` 에 주소 설정 시 활성화 |

---

## 프로젝트 구조

```
contractManagement/
├── app.py              # Flask 서버 (라우트 및 API)
├── requirements.txt    # Python 패키지 목록
├── run.bat             # Windows 실행 스크립트
├── run.sh              # macOS/Linux 실행 스크립트
├── data/               # 데이터 (JSON)
│   ├── contracts.json
│   ├── obligations.json
│   └── org.json
└── templates/          # HTML 템플릿
    ├── base.html
    ├── index.html
    ├── detail.html
    ├── obligations.html
    └── dashboard.html
```

---

## 참고 사항

- 포트를 변경하려면 `app.py` 마지막 줄의 `port=5002` 를 수정하세요.
- 의무조항 상태 변경 시 `data/obligations.json` 파일이 직접 수정됩니다.
- 개발용 서버(Flask development server)이므로 실제 운영 배포에는 별도의 WSGI 서버를 사용하세요.
