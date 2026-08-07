# 계약서 관리 시스템

계약서 조회(Hub), 의무조항 관리, Dashboard 를 제공하는 웹 애플리케이션입니다.

이 저장소는 두 가지 형태를 제공합니다.

| 구분 | 위치 | 서버 필요 | 용도 |
|------|------|:---:|------|
| **정적 목업 (Mockup)** | `mockup/` | ❌ | 다운로드 후 브라우저로 바로 열어 화면 확인 |
| 원본 Flask 앱 | 루트 (`app.py`) | ✅ | 실제 서버 구동 버전 |

---

## ✅ 목업 확인하기 (서버·설치 불필요)

**가장 간단합니다. 파일을 열기만 하면 됩니다.**

1. `mockup/` 폴더를 통째로 다운로드(또는 압축 해제)합니다.
2. 폴더 안의 **`index.html`** 파일을 **더블클릭**해서 브라우저로 엽니다.

끝입니다. 웹서버도, 파이썬도, 인터넷 연결도 필요하지 않습니다.
(Bootstrap 등 필요한 자원을 `mockup/vendor/` 안에 모두 포함했기 때문에 완전 오프라인으로 동작합니다.)

### 화면 이동

- 좌측 사이드바에서 **계약서 Hub / 의무조항 관리 / Dashboard** 페이지를 오갈 수 있습니다.
- 계약서 목록의 **상세** 버튼을 누르면 계약 상세 화면(`detail.html`)이 새 탭으로 열립니다.

### 목업에서 동작하는 기능

- 계약서 검색(부서/기안자/계약명/파트너사/기간/상태), 조직도 트리 검색
- 계약 상세: AI 분석 지표, 조항 목록 필터, 영문 계약 번역보기 토글
- 의무조항 정량/정성 탭 조회, 후속 조치(진행 상태·메모) 업데이트
- Dashboard 지표 집계 및 임박·만료 의무사항 목록

> **참고**: 원본 서버 버전은 상태 변경을 `data/obligations.json` 파일에 저장하지만,
> 목업은 서버가 없으므로 변경 내용을 **브라우저 localStorage**에 저장합니다.
> 같은 브라우저에서는 새로고침해도 유지되며, 초기 상태로 되돌리려면 브라우저 저장소를 비우면 됩니다.

### 목업 폴더 구조

```
mockup/
├── index.html          # 계약서 Hub (시작 화면)
├── detail.html         # 계약 상세 (index.html?id=... 로 진입)
├── obligations.html    # 의무조항 관리
├── dashboard.html      # Dashboard
├── data.js             # 계약/의무/조직 데이터 (원본 JSON을 임베드)
├── mock-api.js         # 서버 로직을 재현한 클라이언트 모의 API
├── app.css             # 공통 레이아웃(사이드바 등) 스타일
├── shell.js            # 사이드바 접기/펼치기
└── vendor/             # Bootstrap 5.3.2 · Bootstrap Icons 1.11.3 (오프라인용 로컬 사본)
```

목업 데이터를 갱신하려면 루트의 `data/*.json` 을 수정한 뒤 아래 명령으로 `data.js` 를 다시 생성하세요.

```bash
python tools/build_data.py
```

---

## 🖥️ 원본 Flask 앱 실행하기 (선택)

실제 서버로 구동하려면 Python 3.9 이상이 필요합니다.

**Windows**: `run.bat` 실행 · **macOS / Linux**: `./run.sh` 실행
→ 가상환경 생성·패키지 설치·서버 실행이 자동으로 진행됩니다.

수동 실행:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate   |   macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

접속: **http://localhost:5002**

| 메뉴 | 경로 | 설명 |
|------|------|------|
| 계약서 Hub | `/` | 계약서 검색 및 목록 조회 |
| 의무조항 관리 | `/obligations` | 정량/정성 의무조항 조회 및 상태 관리 |
| Dashboard | `/dashboard` | 유효 계약, 만료 예정, 기한 초과 의무 현황 |
| Q&A AI Agent | (외부) | `app.py` 의 `AGENT_URL` 에 주소 설정 시 활성화 |

- 개발용 서버(Flask development server)이므로 실제 운영 배포에는 별도의 WSGI 서버를 사용하세요.
