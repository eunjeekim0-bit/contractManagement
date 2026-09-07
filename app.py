from flask import Flask, render_template, request, jsonify, redirect, url_for, Response
from upstash_redis import Redis as _UpstashRedis
import ipaddress
import json, os
from datetime import date, timedelta

app = Flask(__name__)
app.json.sort_keys = False

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

_kv_client = None
_kv_checked = False


def _kv():
    # Vercel Marketplace(Upstash) KV 연동 시 자동 주입되는 환경변수.
    # 없으면(로컬 개발 등) None을 반환해 파일 기반 저장으로 폴백한다.
    global _kv_client, _kv_checked
    if not _kv_checked:
        _kv_checked = True
        url = os.environ.get('KV_REST_API_URL') or os.environ.get('UPSTASH_REDIS_REST_URL')
        token = os.environ.get('KV_REST_API_TOKEN') or os.environ.get('UPSTASH_REDIS_REST_TOKEN')
        if url and token:
            _kv_client = _UpstashRedis(url=url, token=token)
    return _kv_client

# 사내 공인 IP 접근 제한 — 환경변수 ALLOWED_IPS로 콤마 구분 IP/CIDR 목록을 지정한다.
# 지정하지 않으면 아래 기본값(사내 Zscaler 리전 대역)이 적용된다.
# 로컬 개발 편의를 위해 localhost는 항상 허용한다.
DEFAULT_ALLOWED_IPS = '165.225.228.0/23,147.161.192.0/23,165.225.102.0/24,49.50.46.225/32'
_LOCALHOST_NETS = [ipaddress.ip_network('127.0.0.1/32'), ipaddress.ip_network('::1/128')]


def _parse_ip_networks(raw):
    networks = []
    for part in raw.split(','):
        part = part.strip()
        if not part:
            continue
        try:
            networks.append(ipaddress.ip_network(part, strict=False))
        except ValueError:
            pass
    return networks


ALLOWED_IP_NETWORKS = _parse_ip_networks(os.environ.get('ALLOWED_IPS', DEFAULT_ALLOWED_IPS)) + _LOCALHOST_NETS


def _client_ip():
    xff = request.headers.get('X-Forwarded-For', '')
    if xff:
        return xff.split(',')[0].strip()
    return request.remote_addr or ''


@app.before_request
def require_ip_allowlist():
    if not ALLOWED_IP_NETWORKS:
        return None
    try:
        ip = ipaddress.ip_address(_client_ip())
    except ValueError:
        return render_template('forbidden.html'), 403
    if any(ip in net for net in ALLOWED_IP_NETWORKS):
        return None
    return render_template('forbidden.html'), 403


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
    {'key': 'dashboard', 'label': 'Dashboard', 'icon': 'bi-speedometer2', 'url': '/dashboard'},
    {'key': 'contract_master', 'label': '계약서마스터', 'icon': 'bi-table', 'url': '/contract-master'},
    {'key': 'hub_v2', 'label': '계약서 Hub', 'icon': 'bi-grid-3x3-gap', 'url': '/hub-v2'},
    {'key': 'obligations', 'label': '의무조항 관리', 'icon': 'bi-clipboard-check', 'url': '/obligations'},
    {'key': 'agent', 'label': 'Q&A AI Agent', 'icon': 'bi-robot', 'url': AGENT_URL, 'external': True},
    {'key': 'access', 'label': '권한 관리', 'icon': 'bi-shield-lock', 'url': '/access'},
]

QUANT_CATEGORIES = ["지급", "추가 비용", "검수", "정보 제공", "안전관리", "비용 부담", "인력관리"]
QUAL_CATEGORIES = ["기밀정보유지", "준법", "면책", "지적재산권", "양도제한", "해지", "통지", "손해배상"]
STATUS_OPTIONS = ["대기", "완료", "지연"]

RELATION_TYPES = ["원계약", "수정계약", "관련계약"]
INVERSE_RELATION_TYPE = {"원계약": "수정계약", "수정계약": "원계약", "관련계약": "관련계약"}

# 연구과제 코드 목록 — 통상 e-legal I/F 수신 시 함께 들어오나, 누락 시 이 목록에서 수동 지정한다.
RESEARCH_PROJECTS = [
    "GBP410", "GBP412", "GBP413", "GBP470", "GBP480", "GBP490",
    "GBP511", "GBP540", "GBP560", "GBP570", "GBP610", "GBP620", "NBP626",
]

@app.context_processor
def inject_nav():
    return {'nav_pages': NAV_PAGES, 'document_system_url': DOCUMENT_SYSTEM_URL}


def load_json(name):
    key = name.rsplit('.', 1)[0]
    client = _kv()
    if client is not None:
        raw = client.get(key)
        if raw is not None:
            return json.loads(raw)
    # KV에 아직 없거나(최초 배포 직후) 로컬 개발 모드 — 번들된 파일에서 읽는다.
    with open(os.path.join(DATA_DIR, name), 'r', encoding='utf-8') as f:
        data = json.load(f)
    if client is not None:
        client.set(key, json.dumps(data, ensure_ascii=False))
    return data


def save_json(name, data):
    key = name.rsplit('.', 1)[0]
    client = _kv()
    if client is not None:
        client.set(key, json.dumps(data, ensure_ascii=False))
        return
    path = os.path.join(DATA_DIR, name)
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except OSError:
        raise ReadOnlyDemoError()


def load_contracts():
    return load_json('contracts.json')['contracts']


def load_org():
    return load_json('org.json')['departments']


def load_obligations():
    return load_json('obligations.json')['obligations']


def load_permissions():
    client = _kv()
    if client is not None:
        raw = client.get('permissions')
        if raw is not None:
            return json.loads(raw)
    path = os.path.join(DATA_DIR, 'permissions.json')
    if not os.path.exists(path):
        return {'roles': [], 'user_roles': []}
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if client is not None:
        client.set('permissions', json.dumps(data, ensure_ascii=False))
    return data


def save_permissions(perms):
    save_json('permissions.json', perms)


def save_obligations(obligations):
    save_json('obligations.json', {'obligations': obligations})


def save_contracts(contracts):
    save_json('contracts.json', {'contracts': contracts})


def obligation_summary(o, contracts_by_id=None):
    research_project = None
    if contracts_by_id:
        c = contracts_by_id.get(o['contract_id'])
        if c:
            research_project = c.get('research_project')
    return {
        'id': o['id'],
        'contract_id': o['contract_id'],
        'research_project': research_project,
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
        'research_project': c.get('research_project'),
        'sealed': bool(c.get('sealed', False)),
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


@app.route('/contract-master')
def contract_master():
    return render_template('contract_master.html', active_page='contract_master')


@app.route('/contract/<contract_id>')
def detail(contract_id):
    return render_template('detail.html', contract_id=contract_id)


@app.route('/obligations')
def obligations_page():
    return render_template(
        'obligations.html', active_page='obligations',
        quant_categories=QUANT_CATEGORIES, qual_categories=QUAL_CATEGORIES,
        status_options=STATUS_OPTIONS, research_projects=RESEARCH_PROJECTS)


@app.route('/dashboard')
def dashboard_page():
    return render_template(
        'dashboard.html', active_page='dashboard',
        status_options=STATUS_OPTIONS, research_projects=RESEARCH_PROJECTS)


@app.route('/access')
def access_page():
    # 권한 관리 페이지
    return render_template('access.html', active_page='access')


@app.route('/api/org', methods=['GET'])
def api_org():
    return jsonify(load_org())


@app.route('/api/research-projects', methods=['GET'])
def api_research_projects():
    return jsonify(RESEARCH_PROJECTS)


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
    contract_type = request.args.get('type', '').strip()
    research_project = request.args.get('research_project', '').strip()

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
        if contract_type and c['contract_type'] != contract_type:
            continue
        if research_project and c.get('research_project') != research_project:
            continue
        results.append(contract_summary(c))

    results.sort(key=lambda r: r['start_date'], reverse=True)
    return jsonify({'count': len(results), 'results': results})


def _related_contracts(links, contracts_by_id):
    results = []
    for i, link in enumerate(links or []):
        rc = contracts_by_id.get(link['id'])
        if not rc:
            continue
        results.append({
            'id': rc['id'],
            'contract_name': rc['contract_name'],
            'contract_type': rc['contract_type'],
            'partner': rc['partner'],
            'status': rc['status'],
            'source': link.get('source', 'manual'),
            'relation_type': link.get('relation_type', '관련계약'),
            'order': i + 1,
        })
    return results


@app.route('/api/contracts/<contract_id>', methods=['GET'])
def api_detail(contract_id):
    contracts = load_contracts()
    contracts_by_id = {c['id']: c for c in contracts}
    c = contracts_by_id.get(contract_id)
    if not c:
        return jsonify({'error': 'not found'}), 404
    data = dict(c)
    data['related_contracts'] = _related_contracts(c.get('related_contract_ids'), contracts_by_id)
    return jsonify(data)


@app.route('/api/contracts/<contract_id>/research-project', methods=['PUT'])
def api_contract_set_research_project(contract_id):
    body = request.json or {}
    research_project = (body.get('research_project') or '').strip()

    contracts = load_contracts()
    contracts_by_id = {c['id']: c for c in contracts}
    c = contracts_by_id.get(contract_id)
    if not c:
        return jsonify({'error': 'not found'}), 404

    c['research_project'] = research_project or None
    save_contracts(contracts)
    return jsonify({'research_project': c['research_project']})


@app.route('/api/contracts/<contract_id>/sealed', methods=['PUT'])
def api_contract_set_sealed(contract_id):
    body = request.json or {}
    sealed = bool(body.get('sealed'))

    contracts = load_contracts()
    contracts_by_id = {c['id']: c for c in contracts}
    c = contracts_by_id.get(contract_id)
    if not c:
        return jsonify({'error': 'not found'}), 404

    c['sealed'] = sealed
    save_contracts(contracts)
    return jsonify({'sealed': c['sealed']})


@app.route('/api/contracts/<contract_id>/related', methods=['POST'])
def api_contract_add_related(contract_id):
    body = request.json or {}
    related_id = (body.get('related_id') or '').strip()
    relation_type = body.get('relation_type') or '관련계약'
    if not related_id:
        return jsonify({'error': 'related_id is required'}), 400
    if related_id == contract_id:
        return jsonify({'error': '자기 자신은 연관 계약으로 지정할 수 없습니다.'}), 400
    if relation_type not in RELATION_TYPES:
        return jsonify({'error': f'invalid relation_type: {relation_type}'}), 400

    contracts = load_contracts()
    contracts_by_id = {c['id']: c for c in contracts}
    c = contracts_by_id.get(contract_id)
    rc = contracts_by_id.get(related_id)
    if not c or not rc:
        return jsonify({'error': 'not found'}), 404

    c.setdefault('related_contract_ids', [])
    rc.setdefault('related_contract_ids', [])
    if not any(l['id'] == related_id for l in c['related_contract_ids']):
        links = c['related_contract_ids']
        order = body.get('order')
        index = len(links)
        if isinstance(order, int):
            index = max(0, min(order - 1, len(links)))
        links.insert(index, {'id': related_id, 'source': 'manual', 'relation_type': relation_type})
    if not any(l['id'] == contract_id for l in rc['related_contract_ids']):
        rc['related_contract_ids'].append({'id': contract_id, 'source': 'manual', 'relation_type': INVERSE_RELATION_TYPE[relation_type]})

    save_contracts(contracts)
    return jsonify({'related_contracts': _related_contracts(c['related_contract_ids'], contracts_by_id)})


@app.route('/api/contracts/<contract_id>/related/<related_id>', methods=['PUT'])
def api_contract_update_related(contract_id, related_id):
    body = request.json or {}
    order = body.get('order')
    relation_type = body.get('relation_type')
    if order is None and relation_type is None:
        return jsonify({'error': 'order or relation_type is required'}), 400
    if order is not None and not isinstance(order, int):
        return jsonify({'error': 'order must be an integer'}), 400
    if relation_type is not None and relation_type not in RELATION_TYPES:
        return jsonify({'error': f'invalid relation_type: {relation_type}'}), 400

    contracts = load_contracts()
    contracts_by_id = {c['id']: c for c in contracts}
    c = contracts_by_id.get(contract_id)
    if not c:
        return jsonify({'error': 'not found'}), 404

    links = c.get('related_contract_ids', [])
    idx = next((i for i, l in enumerate(links) if l['id'] == related_id), None)
    if idx is None:
        return jsonify({'error': 'not found'}), 404

    if relation_type is not None:
        links[idx]['relation_type'] = relation_type
        rc = contracts_by_id.get(related_id)
        if rc:
            for l in rc.get('related_contract_ids', []):
                if l['id'] == contract_id:
                    l['relation_type'] = INVERSE_RELATION_TYPE[relation_type]

    if order is not None:
        link = links.pop(idx)
        new_index = max(0, min(order - 1, len(links)))
        links.insert(new_index, link)
    c['related_contract_ids'] = links

    save_contracts(contracts)
    return jsonify({'related_contracts': _related_contracts(c['related_contract_ids'], contracts_by_id)})


@app.route('/api/contracts/<contract_id>/related/<related_id>', methods=['DELETE'])
def api_contract_remove_related(contract_id, related_id):
    contracts = load_contracts()
    contracts_by_id = {c['id']: c for c in contracts}
    c = contracts_by_id.get(contract_id)
    if not c:
        return jsonify({'error': 'not found'}), 404

    links = c.get('related_contract_ids', [])
    link = next((l for l in links if l['id'] == related_id), None)
    if link is None:
        return jsonify({'error': 'not found'}), 404
    if link.get('source') == 'if':
        return jsonify({'error': 'e-legal I/F로 수신된 연관 계약서는 삭제할 수 없습니다.'}), 400

    c['related_contract_ids'] = [l for l in links if l['id'] != related_id]

    rc = contracts_by_id.get(related_id)
    if rc:
        rc['related_contract_ids'] = [
            l for l in rc.get('related_contract_ids', [])
            if not (l['id'] == contract_id and l.get('source') != 'if')
        ]

    save_contracts(contracts)
    return jsonify({'related_contracts': _related_contracts(c['related_contract_ids'], contracts_by_id)})


@app.route('/api/obligations/search', methods=['GET'])
def api_obligations_search():
    kind = request.args.get('kind', 'quant').strip()
    dept = request.args.get('dept', '').strip().lower()
    drafter = request.args.get('drafter', '').strip().lower()
    name = request.args.get('name', '').strip().lower()
    partner = request.args.get('partner', '').strip().lower()
    category = request.args.get('category', '').strip()
    status = request.args.get('status', '').strip()
    research_project = request.args.get('research_project', '').strip()

    contracts_by_id = {c['id']: c for c in load_contracts()}

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
        if research_project and contracts_by_id.get(o['contract_id'], {}).get('research_project') != research_project:
            continue
        results.append(obligation_summary(o, contracts_by_id))

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
            if 'due_date' in body:
                due_date = (body.get('due_date') or '').strip()
                if due_date:
                    try:
                        date.fromisoformat(due_date)
                    except ValueError:
                        return jsonify({'error': f'invalid due_date: {due_date}'}), 400
                    o['due_date'] = due_date
                else:
                    o['due_date'] = None
            if 'memo' in body:
                o['memo'] = body.get('memo', '')
            if 'dept_name' in body:
                dept_name = (body.get('dept_name') or '').strip()
                if not dept_name:
                    return jsonify({'error': 'dept_name is required'}), 400
                o['dept_name'] = dept_name
            if 'assignee' in body:
                assignee = (body.get('assignee') or '').strip()
                if not assignee:
                    return jsonify({'error': 'assignee is required'}), 400
                o['assignee'] = assignee
            o['updated_at'] = date.today().isoformat()
            save_obligations(obligations)
            return jsonify(o)
    return jsonify({'error': 'not found'}), 404


def _valid_contracts(dept, research_project=None):
    return [c for c in load_contracts()
            if c['status'] == '계약중' and (not dept or c['dept_name'] == dept)
            and (not research_project or c.get('research_project') == research_project)]


def _expiring_contracts(dept, days, research_project=None):
    today = date.today().isoformat()
    horizon = (date.today() + timedelta(days=days)).isoformat()
    return [c for c in _valid_contracts(dept, research_project) if today <= c['end_date'] <= horizon]


def _obligation_matches_research_project(o, contracts_by_id, research_project):
    if not research_project:
        return True
    c = contracts_by_id.get(o['contract_id'])
    return bool(c) and c.get('research_project') == research_project


def _overdue_obligations(dept, research_project=None):
    today = date.today().isoformat()
    contracts_by_id = {c['id']: c for c in load_contracts()}
    return [o for o in load_obligations()
            if o['kind'] == 'quant' and o['due_date'] and o['due_date'] < today
            and o['status'] != '완료' and (not dept or o['dept_name'] == dept)
            and _obligation_matches_research_project(o, contracts_by_id, research_project)]


def _urgent_obligations(dept, days, research_project=None):
    horizon = (date.today() + timedelta(days=days)).isoformat()
    contracts_by_id = {c['id']: c for c in load_contracts()}
    return [o for o in load_obligations()
            if o['kind'] == 'quant' and o['due_date'] and o['due_date'] <= horizon
            and o['status'] != '완료' and (not dept or o['dept_name'] == dept)
            and _obligation_matches_research_project(o, contracts_by_id, research_project)]


@app.route('/api/dashboard/summary', methods=['GET'])
def api_dashboard_summary():
    dept = request.args.get('dept', '').strip()
    research_project = request.args.get('research_project', '').strip()
    overdue = _overdue_obligations(dept, research_project)
    overdue_by_duty = {'갑': 0, '을': 0, '양당사자': 0}
    for o in overdue:
        overdue_by_duty[o['duty_party']] = overdue_by_duty.get(o['duty_party'], 0) + 1
    return jsonify({
        'valid_contracts': len(_valid_contracts(dept, research_project)),
        'expiring_contracts': len(_expiring_contracts(dept, 30, research_project)),
        'overdue_obligations': len(overdue),
        'overdue_obligations_by_duty': overdue_by_duty,
    })


@app.route('/api/dashboard/valid-contracts', methods=['GET'])
def api_dashboard_valid_contracts():
    dept = request.args.get('dept', '').strip()
    research_project = request.args.get('research_project', '').strip()
    results = sorted((contract_summary(c) for c in _valid_contracts(dept, research_project)), key=lambda r: r['end_date'])
    return jsonify({'count': len(results), 'results': results})


@app.route('/api/dashboard/expiring-contracts', methods=['GET'])
def api_dashboard_expiring_contracts():
    dept = request.args.get('dept', '').strip()
    research_project = request.args.get('research_project', '').strip()
    days = int(request.args.get('days', 30))
    results = sorted((contract_summary(c) for c in _expiring_contracts(dept, days, research_project)), key=lambda r: r['end_date'])
    return jsonify({'count': len(results), 'results': results})


@app.route('/api/dashboard/overdue-obligations', methods=['GET'])
def api_dashboard_overdue_obligations():
    dept = request.args.get('dept', '').strip()
    research_project = request.args.get('research_project', '').strip()
    contracts_by_id = {c['id']: c for c in load_contracts()}
    results = sorted((obligation_summary(o, contracts_by_id) for o in _overdue_obligations(dept, research_project)), key=lambda r: r['due_date'])
    return jsonify({'count': len(results), 'results': results})


@app.route('/api/dashboard/urgent-obligations', methods=['GET'])
def api_dashboard_urgent_obligations():
    dept = request.args.get('dept', '').strip()
    research_project = request.args.get('research_project', '').strip()
    days = int(request.args.get('days', 7))
    contracts_by_id = {c['id']: c for c in load_contracts()}
    results = sorted((obligation_summary(o, contracts_by_id) for o in _urgent_obligations(dept, days, research_project)), key=lambda r: r['due_date'])
    return jsonify({'count': len(results), 'results': results})


@app.route('/api/dashboard/obligations-by-category', methods=['GET'])
def api_dashboard_obligations_by_category():
    dept = request.args.get('dept', '').strip()
    research_project = request.args.get('research_project', '').strip()
    contracts_by_id = {c['id']: c for c in load_contracts()}
    obligations = [o for o in load_obligations()
                   if (not dept or o['dept_name'] == dept)
                   and _obligation_matches_research_project(o, contracts_by_id, research_project)]

    counts = {}
    for o in obligations:
        cat = o['category']
        key = cat.replace(' ', '')
        if key not in counts:
            counts[key] = {'label': cat, 'count': 0, 'duty': {'갑': 0, '을': 0, '양당사자': 0}}
        counts[key]['count'] += 1
        counts[key]['duty'][o['duty_party']] = counts[key]['duty'].get(o['duty_party'], 0) + 1

    total = len(obligations)
    categories = [
        {
            'category': v['label'],
            'count': v['count'],
            'pct': (v['count'] / total * 100) if total else 0,
            'duty': v['duty'],
        }
        for v in counts.values()
    ]
    categories.sort(key=lambda x: -x['count'])
    return jsonify({'total': total, 'categories': categories})


if __name__ == '__main__':
    print('계약서 관리 앱 실행 중: http://localhost:5002')
    app.run(debug=True, port=5002)
