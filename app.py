from flask import Flask, render_template, request, jsonify, redirect, url_for, Response
import json, os
from datetime import date, timedelta

app = Flask(__name__)
app.json.sort_keys = False

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

# 데모 배포용 기본 인증 — 환경변수 DEMO_USER/DEMO_PASSWORD가 설정된 경우에만 활성화된다.
DEMO_USER = os.environ.get('DEMO_USER')
DEMO_PASSWORD = os.environ.get('DEMO_PASSWORD')


@app.before_request
def require_demo_auth():
    if not DEMO_USER or not DEMO_PASSWORD:
        return None
    auth = request.authorization
    if not auth or auth.username != DEMO_USER or auth.password != DEMO_PASSWORD:
        return Response(
            '인증이 필요합니다.', 401,
            {'WWW-Authenticate': 'Basic realm="Contract Management Demo"'}
        )
    return None


class ReadOnlyDemoError(Exception):
    pass


@app.errorhandler(ReadOnlyDemoError)
def handle_read_only_demo_error(_e):
    return jsonify({'error': '데모 환경에서는 저장 기능이 지원되지 않습니다.'}), 503

# Q&A AI Agent 링크 — 별도 서비스 주소가 정해지면 여기만 채우면 된다.
AGENT_URL = ''

# 계약서 원문 첨부파일 링크 — 파일을 직접 내려받지 않고 별도 문서관리 시스템으로 연결한다.
# 계약 ID를 뒤에 붙여 접근하는 형태로 가정. 시스템 주소가 정해지면 여기만 채우면 된다.
DOCUMENT_SYSTEM_URL = ''

# 좌측 사이드바에 노출되는 페이지 목록 — 새 페이지 추가 시 여기에 항목을 더한다
NAV_PAGES = [
    {'key': 'hub_v2', 'label': '계약서 Hub', 'icon': 'bi-grid-3x3-gap', 'url': '/hub-v2'},
    {'key': 'obligations', 'label': '의무조항 관리', 'icon': 'bi-clipboard-check', 'url': '/obligations'},
    {'key': 'dashboard', 'label': 'Dashboard', 'icon': 'bi-speedometer2', 'url': '/dashboard'},
    {'key': 'agent', 'label': 'Q&A AI Agent', 'icon': 'bi-robot', 'url': AGENT_URL, 'external': True},
    {'key': 'access', 'label': '권한 관리', 'icon': 'bi-shield-lock', 'url': '/access'},
]

QUANT_CATEGORIES = ["지급", "추가 비용", "검수", "정보 제공", "안전관리", "비용 부담", "인력관리"]
QUAL_CATEGORIES = ["기밀정보유지", "준법", "면책", "지적재산권", "양도제한", "해지", "통지", "손해배상"]
STATUS_OPTIONS = ["대기", "진행중", "완료", "지연"]

OBLIGATIONS_PATH = os.path.join(os.path.dirname(__file__), 'data', 'obligations.json')


@app.context_processor
def inject_nav():
    return {'nav_pages': NAV_PAGES, 'document_system_url': DOCUMENT_SYSTEM_URL}


def load_json(name):
    with open(os.path.join(DATA_DIR, name), 'r', encoding='utf-8') as f:
        return json.load(f)


def load_contracts():
    return load_json('contracts.json')['contracts']


def load_org():
    return load_json('org.json')['departments']


def load_obligations():
    return load_json('obligations.json')['obligations']


def load_permissions():
    path = os.path.join(DATA_DIR, 'permissions.json')
    if not os.path.exists(path):
        return {'roles': [], 'user_roles': []}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_permissions(perms):
    path = os.path.join(DATA_DIR, 'permissions.json')
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(perms, f, ensure_ascii=False, indent=2)
    except OSError:
        raise ReadOnlyDemoError()


def save_obligations(obligations):
    try:
        with open(OBLIGATIONS_PATH, 'w', encoding='utf-8') as f:
            json.dump({'obligations': obligations}, f, ensure_ascii=False, indent=2)
    except OSError:
        raise ReadOnlyDemoError()


def obligation_summary(o):
    return {
        'id': o['id'],
        'contract_id': o['contract_id'],
        'partner': o['partner'],
        'contract_name': o['contract_name'],
        'division_name': o['division_name'],
        'dept_name': o['dept_name'],
        'drafter_name': o['drafter_name'],
        'assignee': o['assignee'],
        'category': o['category'],
        'duty_party': o['duty_party'],
        'clause_title': o['clause_title'],
        'content': o['content'],
        'kind': o['kind'],
        'due_date': o['due_date'],
        'status': o['status'],
    }


def contract_summary(c):
    ai = c['ai']
    return {
        'id': c['id'],
        'contract_type': c['contract_type'],
        'contract_name': c['contract_name'],
        'contract_name_ko': c.get('contract_name_ko'),
        'language': c.get('language', 'ko'),
        'division_name': c['division_name'],
        'dept_name': c['dept_name'],
        'drafter_name': c['drafter_name'],
        'partner': c['partner'],
        'start_date': c['start_date'],
        'end_date': c['end_date'],
        'amount': c['amount'],
        'currency': c['currency'],
        'status': c['status'],
        'clause_count': ai['clause_count'],
        'important_clause_count': ai['important_clause_count'],
        'obligation_clause_count': ai['obligation_clause_count'],
        'risk_clause_count': ai['risk_clause_count'],
        'overall_risk': ai['overall_risk'],
    }


@app.route('/')
def index():
    return redirect(url_for('hub_v2'))


@app.route('/hub-v2')
def hub_v2():
    return render_template('hub_v2.html', active_page='hub_v2')


@app.route('/contract/<contract_id>')
def detail(contract_id):
    return render_template('detail.html', contract_id=contract_id)


@app.route('/obligations')
def obligations_page():
    return render_template(
        'obligations.html', active_page='obligations',
        quant_categories=QUANT_CATEGORIES, qual_categories=QUAL_CATEGORIES,
        status_options=STATUS_OPTIONS)


@app.route('/dashboard')
def dashboard_page():
    return render_template('dashboard.html', active_page='dashboard', status_options=STATUS_OPTIONS)


@app.route('/access')
def access_page():
    # 권한 관리 페이지
    return render_template('access.html', active_page='access')


@app.route('/api/org', methods=['GET'])
def api_org():
    return jsonify(load_org())


@app.route('/api/permissions', methods=['GET'])
def api_permissions():
    perms = load_permissions()
    # enrich user_roles with user name if available
    users = {e['id']: e for d in load_org() for t in d.get('children', []) for e in t.get('employees', [])}
    enriched = []
    for ur in perms.get('user_roles', []):
        u = users.get(ur.get('user_id')) or {}
        enriched.append({'user_id': ur.get('user_id'), 'roles': ur.get('roles', []), 'name': u.get('name')})
    return jsonify({'roles': perms.get('roles', []), 'user_roles': enriched})


@app.route('/api/permissions/roles', methods=['POST'])
def api_permissions_add_role():
    body = request.json or {}
    rid = body.get('id')
    label = body.get('label') or rid
    pages = body.get('pages', [])
    if not rid:
        return jsonify({'error': 'id required'}), 400
    perms = load_permissions()
    if any(r['id'] == rid for r in perms.get('roles', [])):
        return jsonify({'error': 'exists'}), 400
    perms.setdefault('roles', []).append({'id': rid, 'label': label, 'pages': pages})
    save_permissions(perms)
    return jsonify({'ok': True})


@app.route('/api/permissions/roles/<role_id>', methods=['PUT', 'DELETE'])
def api_permissions_update_role(role_id):
    perms = load_permissions()
    if request.method == 'DELETE':
        perms['roles'] = [r for r in perms.get('roles', []) if r['id'] != role_id]
        # remove role from users
        for ur in perms.get('user_roles', []):
            ur['roles'] = [x for x in ur.get('roles', []) if x != role_id]
        save_permissions(perms)
        return jsonify({'ok': True})
    body = request.json or {}
    pages = body.get('pages')
    updated = False
    for r in perms.get('roles', []):
        if r['id'] == role_id:
            if pages is not None:
                r['pages'] = pages
            updated = True
    if not updated:
        return jsonify({'error': 'not found'}), 404
    save_permissions(perms)
    return jsonify({'ok': True})


def _all_employees():
    deps = load_org()
    for d in deps:
        for t in d.get('children', []):
            for e in t.get('employees', []):
                yield {'id': e.get('id'), 'name': e.get('name'), 'position': e.get('position'), 'dept': t.get('name'), 'division': d.get('name')}


@app.route('/api/users/search', methods=['GET'])
def api_users_search():
    q = (request.args.get('q') or '').strip().lower()
    results = []
    if q:
        for e in _all_employees():
            if q in e['id'].lower() or q in e['name'].lower():
                results.append(e)
    return jsonify({'count': len(results), 'results': results})


@app.route('/api/users/<user_id>/roles', methods=['POST'])
def api_assign_role(user_id):
    body = request.json or {}
    role = body.get('role')
    if not role:
        return jsonify({'error': 'role required'}), 400
    perms = load_permissions()
    # ensure role exists
    if not any(r['id'] == role for r in perms.get('roles', [])):
        return jsonify({'error': 'role not found'}), 404
    ur = next((u for u in perms.get('user_roles', []) if u['user_id'] == user_id), None)
    if ur is None:
        perms.setdefault('user_roles', []).append({'user_id': user_id, 'roles': [role]})
    else:
        if role not in ur.get('roles', []):
            ur['roles'].append(role)
    save_permissions(perms)
    return jsonify({'ok': True})


@app.route('/api/users/<user_id>/roles/<role_id>', methods=['DELETE'])
def api_remove_user_role(user_id, role_id):
    perms = load_permissions()
    for ur in perms.get('user_roles', []):
        if ur.get('user_id') == user_id:
            ur['roles'] = [r for r in ur.get('roles', []) if r != role_id]
    save_permissions(perms)
    return jsonify({'ok': True})


@app.route('/api/contracts/search', methods=['GET'])
def api_search():
    dept = request.args.get('dept', '').strip().lower()
    drafter = request.args.get('drafter', '').strip().lower()
    name = request.args.get('name', '').strip().lower()
    partner = request.args.get('partner', '').strip().lower()
    start = request.args.get('start', '').strip()
    end = request.args.get('end', '').strip()
    status = request.args.get('status', '').strip()

    results = []
    for c in load_contracts():
        if dept and dept not in c['dept_name'].lower() and dept not in c['division_name'].lower():
            continue
        if drafter and drafter not in c['drafter_name'].lower():
            continue
        if name and name not in c['contract_name'].lower() and name not in (c.get('contract_name_ko') or '').lower():
            continue
        if partner and partner not in c['partner'].lower():
            continue
        if start and c['end_date'] < start:
            continue
        if end and c['start_date'] > end:
            continue
        if status and c['status'] != status:
            continue
        results.append(contract_summary(c))

    results.sort(key=lambda r: r['start_date'], reverse=True)
    return jsonify({'count': len(results), 'results': results})


@app.route('/api/contracts/<contract_id>', methods=['GET'])
def api_detail(contract_id):
    for c in load_contracts():
        if c['id'] == contract_id:
            return jsonify(c)
    return jsonify({'error': 'not found'}), 404


@app.route('/api/obligations/search', methods=['GET'])
def api_obligations_search():
    kind = request.args.get('kind', 'quant').strip()
    dept = request.args.get('dept', '').strip().lower()
    drafter = request.args.get('drafter', '').strip().lower()
    name = request.args.get('name', '').strip().lower()
    partner = request.args.get('partner', '').strip().lower()
    category = request.args.get('category', '').strip()
    status = request.args.get('status', '').strip()

    results = []
    for o in load_obligations():
        if o['kind'] != kind:
            continue
        if dept and dept not in o['dept_name'].lower() and dept not in o['division_name'].lower():
            continue
        if drafter and drafter not in o['drafter_name'].lower():
            continue
        if name and name not in o['contract_name'].lower():
            continue
        if partner and partner not in o['partner'].lower():
            continue
        if category and o['category'] != category:
            continue
        if status and o['status'] != status:
            continue
        results.append(obligation_summary(o))

    def sort_key(r):
        return (r['due_date'] is None, r['due_date'] or '')
    results.sort(key=sort_key)
    return jsonify({'count': len(results), 'results': results})


@app.route('/api/obligations/<obligation_id>', methods=['GET'])
def api_obligation_detail(obligation_id):
    for o in load_obligations():
        if o['id'] == obligation_id:
            return jsonify(o)
    return jsonify({'error': 'not found'}), 404


@app.route('/api/obligations/<obligation_id>', methods=['PUT'])
def api_obligation_update(obligation_id):
    body = request.json or {}

    obligations = load_obligations()
    for o in obligations:
        if o['id'] == obligation_id:
            if 'status' in body:
                status = body.get('status')
                if status not in STATUS_OPTIONS:
                    return jsonify({'error': f'invalid status: {status}'}), 400
                o['status'] = status
                o['note'] = body.get('note', '')
            if 'assignee' in body:
                assignee = (body.get('assignee') or '').strip()
                if not assignee:
                    return jsonify({'error': 'assignee is required'}), 400
                o['assignee'] = assignee
            o['updated_at'] = date.today().isoformat()
            save_obligations(obligations)
            return jsonify(o)
    return jsonify({'error': 'not found'}), 404


def _valid_contracts(dept):
    return [c for c in load_contracts()
            if c['status'] == '계약중' and (not dept or c['dept_name'] == dept)]


def _expiring_contracts(dept, days):
    today = date.today().isoformat()
    horizon = (date.today() + timedelta(days=days)).isoformat()
    return [c for c in _valid_contracts(dept) if today <= c['end_date'] <= horizon]


def _overdue_obligations(dept):
    today = date.today().isoformat()
    return [o for o in load_obligations()
            if o['kind'] == 'quant' and o['due_date'] and o['due_date'] < today
            and o['status'] != '완료' and (not dept or o['dept_name'] == dept)]


def _urgent_obligations(dept, days):
    horizon = (date.today() + timedelta(days=days)).isoformat()
    return [o for o in load_obligations()
            if o['kind'] == 'quant' and o['due_date'] and o['due_date'] <= horizon
            and o['status'] != '완료' and (not dept or o['dept_name'] == dept)]


@app.route('/api/dashboard/summary', methods=['GET'])
def api_dashboard_summary():
    dept = request.args.get('dept', '').strip()
    return jsonify({
        'valid_contracts': len(_valid_contracts(dept)),
        'expiring_contracts': len(_expiring_contracts(dept, 30)),
        'overdue_obligations': len(_overdue_obligations(dept)),
    })


@app.route('/api/dashboard/valid-contracts', methods=['GET'])
def api_dashboard_valid_contracts():
    dept = request.args.get('dept', '').strip()
    results = sorted((contract_summary(c) for c in _valid_contracts(dept)), key=lambda r: r['end_date'])
    return jsonify({'count': len(results), 'results': results})


@app.route('/api/dashboard/expiring-contracts', methods=['GET'])
def api_dashboard_expiring_contracts():
    dept = request.args.get('dept', '').strip()
    days = int(request.args.get('days', 30))
    results = sorted((contract_summary(c) for c in _expiring_contracts(dept, days)), key=lambda r: r['end_date'])
    return jsonify({'count': len(results), 'results': results})


@app.route('/api/dashboard/overdue-obligations', methods=['GET'])
def api_dashboard_overdue_obligations():
    dept = request.args.get('dept', '').strip()
    results = sorted((obligation_summary(o) for o in _overdue_obligations(dept)), key=lambda r: r['due_date'])
    return jsonify({'count': len(results), 'results': results})


@app.route('/api/dashboard/urgent-obligations', methods=['GET'])
def api_dashboard_urgent_obligations():
    dept = request.args.get('dept', '').strip()
    days = int(request.args.get('days', 7))
    results = sorted((obligation_summary(o) for o in _urgent_obligations(dept, days)), key=lambda r: r['due_date'])
    return jsonify({'count': len(results), 'results': results})


if __name__ == '__main__':
    print('계약서 관리 앱 실행 중: http://localhost:5002')
    app.run(debug=True, port=5002)
