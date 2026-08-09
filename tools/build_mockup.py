#!/usr/bin/env python3
"""계약서 관리 시스템 - 단일 HTML 목업 생성기.

Flask 서버/API 없이 브라우저에서 바로 열어볼 수 있는 정적 목업(mockup.html)을 만든다.
실제 data/*.json 을 그대로 임베드하고, app.py 의 API 로직을 클라이언트 JS 로 재현한다.
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, 'data')
OUT = os.path.join(ROOT, 'mockup.html')


def load(name):
    with open(os.path.join(DATA_DIR, name), 'r', encoding='utf-8') as f:
        return json.load(f)


MOCK = {
    'contracts': load('contracts.json')['contracts'],
    'obligations': load('obligations.json')['obligations'],
    'org': load('org.json')['departments'],
    'permissions': load('permissions.json'),
    'quant_categories': ["지급", "추가 비용", "검수", "정보 제공", "안전관리", "비용 부담", "인력관리"],
    'qual_categories': ["기밀정보유지", "준법", "면책", "지적재산권", "양도제한", "해지", "통지", "손해배상"],
    'status_options': ["대기", "진행중", "완료", "지연"],
    'nav_pages': [
        {'key': 'hub', 'label': '계약서 Hub', 'icon': 'bi-grid-3x3-gap'},
        {'key': 'obligations', 'label': '의무조항 관리', 'icon': 'bi-clipboard-check'},
        {'key': 'dashboard', 'label': 'Dashboard', 'icon': 'bi-speedometer2'},
        {'key': 'agent', 'label': 'Q&A AI Agent', 'icon': 'bi-robot', 'external': True},
        {'key': 'access', 'label': '권한 관리', 'icon': 'bi-shield-lock'},
    ],
}

DATA_JSON = json.dumps(MOCK, ensure_ascii=False)

HTML = r"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>계약서 관리 · 목업</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
<style>
:root { --primary: #4361ee; --risk-high:#ef476f; --risk-mid:#ffd166; --risk-low:#06d6a0; }
body { background: #f0f2f5; font-family: 'Segoe UI', sans-serif; }

.mock-banner {
  background: #fff3cd; color: #7a5b00; border-bottom: 1px solid #ffe08a;
  font-size: .82rem; padding: 6px 16px; text-align: center; font-weight: 600;
}

.app-shell { display: flex; min-height: 100vh; }
.sidebar {
  width: 232px; flex-shrink: 0; background: #1e1e2e; color: #fff;
  position: sticky; top: 0; height: 100vh; overflow-y: auto; overflow-x: hidden;
  display: flex; flex-direction: column; transition: width .18s ease;
}
.sidebar-brand { padding: 14px 14px; border-bottom: 1px solid rgba(255,255,255,.08); display: flex; align-items: center; gap: 10px; }
.sidebar-toggle { background: none; border: none; color: #c9cbe0; cursor: pointer; font-size: 1.1rem; padding: 6px 9px; border-radius: 8px; flex-shrink: 0; line-height: 1; }
.sidebar-toggle:hover { background: rgba(255,255,255,.08); color: #fff; }
.sidebar-brand-text { font-weight: 700; font-size: 1.05rem; white-space: nowrap; overflow: hidden; }
.sidebar-nav { padding: 12px 10px; flex: 1; }
.sidebar-section-label { padding: 10px 12px 4px; font-size: .72rem; font-weight: 700; color: #7d80a0; text-transform: uppercase; letter-spacing: .04em; white-space: nowrap; }
.sidebar-link { display: flex; align-items: center; padding: 10px 12px; border-radius: 10px; color: #c9cbe0; text-decoration: none; font-weight: 600; font-size: .9rem; margin-bottom: 4px; white-space: nowrap; overflow: hidden; cursor: pointer; }
.sidebar-link:hover { background: rgba(255,255,255,.08); color: #fff; }
.sidebar-link.active { background: var(--primary); color: #fff; }
.sidebar-link i { width: 20px; text-align: center; flex-shrink: 0; }
.sidebar-link-label { margin-left: 10px; display:flex; align-items:center; gap:6px; }
.sidebar-link.disabled { color: #6c6f8a; cursor: not-allowed; }
.sidebar-link-external-icon { font-size: .7rem; opacity: .6; }

.main-content { flex: 1; min-width: 0; }
.content-header { background: #fff; border-bottom: 1px solid #e5e7f0; padding: 16px 24px; display: flex; align-items: center; justify-content: space-between; }
.content-header h5 { margin: 0; font-weight: 700; }
.content-body { padding: 16px 20px; }

html.sidebar-collapsed .sidebar { width: 68px; }
html.sidebar-collapsed .sidebar-brand { justify-content: center; }
html.sidebar-collapsed .sidebar-brand-text,
html.sidebar-collapsed .sidebar-section-label,
html.sidebar-collapsed .sidebar-link-label { display: none; }
html.sidebar-collapsed .sidebar-link { justify-content: center; padding: 10px; }
html.sidebar-collapsed .sidebar-toggle i { transform: rotate(180deg); }

/* 공통 카드 */
.search-card, .result-card, .dept-card, .info-card { border-radius: 16px; border: none; box-shadow: 0 2px 8px rgba(0,0,0,.08); }
.form-label { font-weight: 600; font-size: .85rem; color: #444; }

/* 테이블 */
table.contract-table, table.ob-table, table.ct-table { font-size: .85rem; }
table.contract-table thead th { vertical-align: middle; text-align: center; white-space: nowrap; }
table.ob-table thead th, table.ct-table thead th { vertical-align: middle; text-align: center; white-space: nowrap; background:#e8eaff; color:#2b2d6e; }
.thead-basic { background: #e8eaff; color: #2b2d6e; }
.thead-ai { background: #fff0f3; color: #7a1230; }
.thead-link { background: #1e1e2e; color: #fff; }
.amount-cell { text-align: right; font-variant-numeric: tabular-nums; }
.center-cell { text-align: center; }
.ob-content { max-width: 340px; color:#555; }

/* badge */
.badge-risk-낮음 { background: #d8f8ee; color: #06a075; }
.badge-risk-중간 { background: #fff3cd; color: #9c7a00; }
.badge-risk-높음 { background: #fde0e8; color: #c0394a; }
.status-badge { font-size: .72rem; }
.status-계약중 { background:#d8f8ee; color:#06a075; }
.status-만료 { background:#f0f0f0; color:#888; }
.status-예정 { background:#e8eaff; color:#3b4bd0; }
.status-대기 { background:#f0f0f0; color:#666; }
.status-진행중 { background:#d4eef8; color:#118ab2; }
.status-완료 { background:#d8f8ee; color:#06a075; }
.status-지연 { background:#fde0e8; color:#c0394a; }
.category-badge { font-size: .72rem; background:#f0f0f0; color:#555; }
.duty-badge { font-size: .72rem; }
.duty-갑 { background:#e8eaff; color:#3b4bd0; }
.duty-을 { background:#fff3cd; color:#9c7a00; }
.duty-양당사자 { background:#f0f0f0; color:#666; }
.due-overdue { color:#c0394a; font-weight:700; }
.due-soon { color:#9c7a00; font-weight:700; }
.empty-state { text-align:center; padding: 50px 0; color:#999; }

/* dashboard stat */
.stat-card { border-radius: 16px; border: none; box-shadow: 0 2px 8px rgba(0,0,0,.08); cursor: pointer; transition: transform .12s ease, box-shadow .12s ease; }
.stat-card:hover { transform: translateY(-2px); box-shadow: 0 6px 16px rgba(0,0,0,.12); }
.stat-card .icon { width: 52px; height: 52px; border-radius: 14px; display:flex; align-items:center; justify-content:center; font-size:1.5rem; }
.icon-valid { background: #d8f8ee; color: #06a075; }
.icon-expiring { background: #fff3cd; color: #9c7a00; }
.icon-overdue { background: #fde0e8; color: #c0394a; }
.stat-value { font-size: 2rem; font-weight: 800; line-height: 1; }
.stat-label { color: #666; font-weight: 600; font-size: .92rem; }
.stat-hint { color: #999; font-size: .78rem; }

/* org tree */
.org-tree .division-header { font-weight: 700; background: #f0f2ff; padding: 6px 10px; border-radius: 8px; }
.org-tree .team-block { margin: 4px 0 8px 14px; }
.org-tree .team-name { font-weight: 600; color: var(--primary); padding: 4px 6px; cursor: pointer; border-radius: 6px; }
.org-tree .team-name:hover { background: #eef0ff; }
.org-tree .emp-row { padding: 3px 10px 3px 20px; cursor: pointer; border-radius: 6px; font-size: .88rem; }
.org-tree .emp-row:hover { background: #f5f6ff; }
.emp-pos { color: #999; font-size: .78rem; }

.nav-tabs .nav-link { color: #666; font-weight: 500; cursor: pointer; }
.nav-tabs .nav-link.active { color: var(--primary); font-weight: 700; border-color: transparent transparent var(--primary); border-bottom: 3px solid; }
.kind-hint { font-size: .82rem; color:#888; }

/* detail */
.info-row { display:flex; padding: 8px 0; border-bottom: 1px solid #f0f0f0; }
.info-row:last-child { border-bottom: none; }
.info-label { width: 130px; color: #888; font-weight: 600; font-size: .88rem; flex-shrink:0; }
.info-value { font-weight: 600; }
.stat-card .icon-total { background: #e8eaff; color: #4361ee; }
.stat-card .icon-important { background: #fff3cd; color: #9c7a00; }
.stat-card .icon-obligation { background: #d4eef8; color: #118ab2; }
.stat-card .icon-risk { background: #fde0e8; color: #ef476f; }
.clause-type-badge { font-size: .72rem; }
.type-일반 { background:#f0f0f0; color:#666; }
.type-중요 { background:#fff3cd; color:#9c7a00; }
.type-의무 { background:#d4eef8; color:#118ab2; }
.type-리스크 { background:#fde0e8; color:#c0394a; }
.clause-row td { vertical-align: top; }
.clause-content { color:#555; font-size:.85rem; }
.filter-chip { cursor:pointer; }
.filter-chip.active { background: var(--primary); color:#fff; }

@media (max-width: 767px) {
  .app-shell { flex-direction: column; }
  .sidebar, html.sidebar-collapsed .sidebar { width: 100%; height: auto; position: relative; flex-direction: row; overflow-x: auto; }
  .sidebar-brand { border-bottom: none; border-right: 1px solid rgba(255,255,255,.08); white-space: nowrap; }
  .sidebar-toggle { display: none; }
  .sidebar-nav { display: flex; padding: 8px; }
  .sidebar-link { margin-bottom: 0; margin-right: 4px; white-space: nowrap; }
}
</style>
</head>
<body>

<div class="mock-banner"><i class="bi bi-info-circle me-1"></i>정적 목업(Mockup) — 서버 없이 동작하며 데이터 변경은 저장되지 않습니다. 실제 데이터를 기반으로 모든 화면을 재현했습니다.</div>

<div class="app-shell">
  <aside class="sidebar">
    <div class="sidebar-brand">
      <button class="sidebar-toggle" id="sidebarToggleBtn" title="메뉴 접기/펼치기" type="button"><i class="bi bi-chevron-double-left"></i></button>
      <span class="sidebar-brand-text"><i class="bi bi-file-earmark-text me-2"></i>계약서 관리</span>
    </div>
    <nav class="sidebar-nav" id="sidebarNav"></nav>
  </aside>

  <main class="main-content">
    <div class="content-header">
      <h5 id="pageTitle"></h5>
      <div id="headerExtra"></div>
    </div>
    <div class="content-body" id="pageContent"></div>
  </main>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
<script>
const MOCK = __MOCK_DATA__;
</script>
<script>
/* =========================================================================
   목업 데이터 계층 — app.py 의 API 로직을 브라우저에서 그대로 재현한다.
   ========================================================================= */
const TODAY = new Date().toISOString().slice(0, 10);
function addDays(days) { const d = new Date(); d.setDate(d.getDate() + days); return d.toISOString().slice(0, 10); }
function daysUntil(dateStr) { return Math.round((new Date(dateStr) - new Date(TODAY)) / 86400000); }

function fmt(n) { if (n == null || isNaN(n)) return '0'; return Math.round(n).toLocaleString('ko-KR'); }
function formatAmount(amount, currency) {
  const n = fmt(amount);
  if (currency === 'USD') return '$' + n;
  if (currency === 'EUR') return '€' + n;
  return n + '원';
}
function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }

function contractSummary(c) {
  const ai = c.ai;
  return {
    id: c.id, contract_type: c.contract_type, contract_name: c.contract_name,
    contract_name_ko: c.contract_name_ko, language: c.language || 'ko',
    division_name: c.division_name, dept_name: c.dept_name, drafter_name: c.drafter_name,
    partner: c.partner, start_date: c.start_date, end_date: c.end_date,
    amount: c.amount, currency: c.currency, status: c.status,
    clause_count: ai.clause_count, important_clause_count: ai.important_clause_count,
    obligation_clause_count: ai.obligation_clause_count, risk_clause_count: ai.risk_clause_count,
    overall_risk: ai.overall_risk,
  };
}
function obligationSummary(o) {
  return {
    id: o.id, contract_id: o.contract_id, partner: o.partner, contract_name: o.contract_name,
    division_name: o.division_name, dept_name: o.dept_name, drafter_name: o.drafter_name,
    assignee: o.assignee, category: o.category, duty_party: o.duty_party,
    clause_title: o.clause_title, content: o.content, kind: o.kind,
    due_date: o.due_date, status: o.status,
  };
}

const api = {
  org() { return MOCK.org; },

  searchContracts(p) {
    const dept = (p.dept || '').trim().toLowerCase();
    const drafter = (p.drafter || '').trim().toLowerCase();
    const name = (p.name || '').trim().toLowerCase();
    const partner = (p.partner || '').trim().toLowerCase();
    const start = (p.start || '').trim();
    const end = (p.end || '').trim();
    const status = (p.status || '').trim();
    let res = MOCK.contracts.filter(c => {
      if (dept && !c.dept_name.toLowerCase().includes(dept) && !c.division_name.toLowerCase().includes(dept)) return false;
      if (drafter && !c.drafter_name.toLowerCase().includes(drafter)) return false;
      if (name && !c.contract_name.toLowerCase().includes(name) && !((c.contract_name_ko || '').toLowerCase().includes(name))) return false;
      if (partner && !c.partner.toLowerCase().includes(partner)) return false;
      if (start && c.end_date < start) return false;
      if (end && c.start_date > end) return false;
      if (status && c.status !== status) return false;
      return true;
    }).map(contractSummary);
    res.sort((a, b) => b.start_date.localeCompare(a.start_date));
    return res;
  },

  getContract(id) { return MOCK.contracts.find(c => c.id === id) || null; },

  searchObligations(p) {
    const kind = (p.kind || 'quant').trim();
    const dept = (p.dept || '').trim().toLowerCase();
    const drafter = (p.drafter || '').trim().toLowerCase();
    const name = (p.name || '').trim().toLowerCase();
    const partner = (p.partner || '').trim().toLowerCase();
    const category = (p.category || '').trim();
    const status = (p.status || '').trim();
    let res = MOCK.obligations.filter(o => {
      if (o.kind !== kind) return false;
      if (dept && !o.dept_name.toLowerCase().includes(dept) && !o.division_name.toLowerCase().includes(dept)) return false;
      if (drafter && !o.drafter_name.toLowerCase().includes(drafter)) return false;
      if (name && !o.contract_name.toLowerCase().includes(name)) return false;
      if (partner && !o.partner.toLowerCase().includes(partner)) return false;
      if (category && o.category !== category) return false;
      if (status && o.status !== status) return false;
      return true;
    }).map(obligationSummary);
    res.sort((a, b) => {
      const ak = a.due_date == null, bk = b.due_date == null;
      if (ak !== bk) return ak ? 1 : -1;
      return (a.due_date || '').localeCompare(b.due_date || '');
    });
    return res;
  },

  getObligation(id) { return MOCK.obligations.find(o => o.id === id) || null; },
  updateObligation(id, status, note) {
    const o = MOCK.obligations.find(x => x.id === id);
    if (!o) return null;
    o.status = status; o.note = note; o.updated_at = TODAY;
    return o;
  },

  validContracts(dept) { return MOCK.contracts.filter(c => c.status === '계약중' && (!dept || c.dept_name === dept)); },
  expiringContracts(dept, days) {
    const horizon = addDays(days);
    return this.validContracts(dept).filter(c => TODAY <= c.end_date && c.end_date <= horizon);
  },
  overdueObligations(dept) {
    return MOCK.obligations.filter(o => o.kind === 'quant' && o.due_date && o.due_date < TODAY && o.status !== '완료' && (!dept || o.dept_name === dept));
  },
  urgentObligations(dept, days) {
    const horizon = addDays(days);
    return MOCK.obligations.filter(o => o.kind === 'quant' && o.due_date && o.due_date <= horizon && o.status !== '완료' && (!dept || o.dept_name === dept));
  },

  permissions() {
    const users = {};
    MOCK.org.forEach(d => (d.children || []).forEach(t => (t.employees || []).forEach(e => { users[e.id] = e; })));
    const enriched = (MOCK.permissions.user_roles || []).map(ur => ({
      user_id: ur.user_id, roles: ur.roles || [], name: (users[ur.user_id] || {}).name,
    }));
    return { roles: MOCK.permissions.roles || [], user_roles: enriched };
  },
  allEmployees() {
    const out = [];
    MOCK.org.forEach(d => (d.children || []).forEach(t => (t.employees || []).forEach(e =>
      out.push({ id: e.id, name: e.name, position: e.position, dept: t.name, division: d.name }))));
    return out;
  },
  searchUsers(q) {
    q = (q || '').trim().toLowerCase();
    if (!q) return [];
    return this.allEmployees().filter(e => e.id.toLowerCase().includes(q) || e.name.toLowerCase().includes(q));
  },
  addRole(id, label, pages) {
    if ((MOCK.permissions.roles || []).some(r => r.id === id)) return false;
    (MOCK.permissions.roles = MOCK.permissions.roles || []).push({ id, label: label || id, pages: pages || [] });
    return true;
  },
  updateRolePages(id, pages) {
    const r = (MOCK.permissions.roles || []).find(r => r.id === id);
    if (r) r.pages = pages;
    return !!r;
  },
  deleteRole(id) {
    MOCK.permissions.roles = (MOCK.permissions.roles || []).filter(r => r.id !== id);
    (MOCK.permissions.user_roles || []).forEach(ur => { ur.roles = (ur.roles || []).filter(x => x !== id); });
  },
  assignRole(userId, role) {
    if (!(MOCK.permissions.roles || []).some(r => r.id === role)) return false;
    let ur = (MOCK.permissions.user_roles || []).find(u => u.user_id === userId);
    if (!ur) (MOCK.permissions.user_roles = MOCK.permissions.user_roles || []).push({ user_id: userId, roles: [role] });
    else if (!ur.roles.includes(role)) ur.roles.push(role);
    return true;
  },
  removeUserRole(userId, roleId) {
    (MOCK.permissions.user_roles || []).forEach(ur => { if (ur.user_id === userId) ur.roles = (ur.roles || []).filter(r => r !== roleId); });
  },
};

/* 공통 badge 헬퍼 */
function riskBadge(l) { return `<span class="badge badge-risk-${l}">${l}</span>`; }
function statusBadge(s) { return `<span class="badge status-badge status-${s}">${s}</span>`; }
function categoryBadge(c) { return `<span class="badge category-badge">${esc(c)}</span>`; }

/* =========================================================================
   조직도 검색 모달 (Hub / 의무조항 공용)
   ========================================================================= */
let _orgModal = null, _orgSelectDept = null, _orgSelectDrafter = null;
function ensureOrgModal() {
  if (document.getElementById('orgModal')) return;
  const wrap = document.createElement('div');
  wrap.innerHTML = `
  <div class="modal fade" id="orgModal" tabindex="-1">
    <div class="modal-dialog modal-dialog-scrollable">
      <div class="modal-content">
        <div class="modal-header py-2">
          <h6 class="modal-title fw-bold" id="orgModalTitle"><i class="bi bi-diagram-3 me-2"></i>조직도 검색</h6>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <input type="text" class="form-control mb-3" id="orgSearchInput" placeholder="부서명 또는 이름 검색...">
          <div class="org-tree" id="orgTree"></div>
        </div>
      </div>
    </div>
  </div>`;
  document.body.appendChild(wrap.firstElementChild);
  _orgModal = new bootstrap.Modal(document.getElementById('orgModal'));
  document.getElementById('orgSearchInput').addEventListener('input', e => renderOrgTree(e.target.value.trim().toLowerCase()));
}
function openOrgModal(mode, onDept, onDrafter) {
  ensureOrgModal();
  _orgSelectDept = onDept; _orgSelectDrafter = onDrafter;
  document.getElementById('orgModalTitle').innerHTML = mode === 'dept'
    ? '<i class="bi bi-diagram-3 me-2"></i>기안부서 검색'
    : '<i class="bi bi-person-badge me-2"></i>기안자 검색';
  document.getElementById('orgSearchInput').value = '';
  renderOrgTree('');
  _orgModal.show();
}
function renderOrgTree(filter) {
  const container = document.getElementById('orgTree');
  container.innerHTML = '';
  api.org().forEach(division => {
    const teams = division.children.map(team => {
      const matchTeam = !filter || team.name.toLowerCase().includes(filter) || division.name.toLowerCase().includes(filter);
      const employees = team.employees.filter(e => !filter || matchTeam || e.name.toLowerCase().includes(filter));
      return { team, employees, show: matchTeam || employees.length > 0 };
    }).filter(t => t.show);
    if (filter && teams.length === 0) return;
    const divDiv = document.createElement('div');
    divDiv.className = 'mb-2';
    divDiv.innerHTML = `<div class="division-header"><i class="bi bi-building me-1"></i>${esc(division.name)}</div>`;
    container.appendChild(divDiv);
    teams.forEach(({ team, employees }) => {
      const teamBlock = document.createElement('div');
      teamBlock.className = 'team-block';
      const teamNameEl = document.createElement('div');
      teamNameEl.className = 'team-name';
      teamNameEl.innerHTML = `<i class="bi bi-people me-1"></i>${esc(team.name)}`;
      teamNameEl.onclick = () => { if (_orgSelectDept) _orgSelectDept(team.name); _orgModal.hide(); };
      teamBlock.appendChild(teamNameEl);
      (filter ? employees : team.employees).forEach(emp => {
        const empEl = document.createElement('div');
        empEl.className = 'emp-row';
        empEl.innerHTML = `<i class="bi bi-person me-1"></i>${esc(emp.name)} <span class="emp-pos">${esc(emp.position)}</span>`;
        empEl.onclick = () => { if (_orgSelectDrafter) _orgSelectDrafter(team.name, emp.name); _orgModal.hide(); };
        teamBlock.appendChild(empEl);
      });
      container.appendChild(teamBlock);
    });
  });
}

/* =========================================================================
   후속조치 업데이트 모달 (Dashboard / 의무조항 공용)
   ========================================================================= */
let _updateModal = null, _updateId = null, _onUpdateSaved = null;
function ensureUpdateModal() {
  if (document.getElementById('updateModal')) return;
  const opts = MOCK.status_options.map(s => `<option value="${s}">${s}</option>`).join('');
  const wrap = document.createElement('div');
  wrap.innerHTML = `
  <div class="modal fade" id="updateModal" tabindex="-1">
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header py-2">
          <h6 class="modal-title fw-bold"><i class="bi bi-pencil-square me-2 text-primary"></i>후속 조치 업데이트</h6>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <div class="mb-2"><span class="text-muted small">계약명</span><div class="fw-semibold" id="um-contract-name"></div></div>
          <div class="row mb-2">
            <div class="col-6"><span class="text-muted small">파트너사</span><div class="fw-semibold" id="um-partner"></div></div>
            <div class="col-6"><span class="text-muted small">담당자</span><div class="fw-semibold" id="um-assignee"></div></div>
          </div>
          <div class="row mb-2">
            <div class="col-6"><span class="text-muted small">조항 구분</span><div class="fw-semibold" id="um-category"></div></div>
            <div class="col-6"><span class="text-muted small">기한일</span><div class="fw-semibold" id="um-due"></div></div>
          </div>
          <div class="mb-3">
            <span class="text-muted small">조항 내용</span>
            <div class="small border rounded p-2 bg-light" id="um-content" style="max-height:100px; overflow-y:auto"></div>
          </div>
          <hr>
          <div class="mb-3">
            <label class="form-label fw-semibold">진행 상태</label>
            <select class="form-select" id="um-status">${opts}</select>
          </div>
          <div class="mb-2">
            <label class="form-label fw-semibold">후속 조치 내용</label>
            <textarea class="form-control" id="um-note" rows="4" placeholder="처리 내용을 입력하세요"></textarea>
          </div>
        </div>
        <div class="modal-footer border-0 pt-0">
          <button class="btn btn-secondary btn-sm" data-bs-dismiss="modal">취소</button>
          <button class="btn btn-primary btn-sm px-3" id="um-save"><i class="bi bi-check2 me-1"></i>저장</button>
        </div>
      </div>
    </div>
  </div>`;
  document.body.appendChild(wrap.firstElementChild);
  _updateModal = new bootstrap.Modal(document.getElementById('updateModal'));
  document.getElementById('um-save').addEventListener('click', () => {
    const status = document.getElementById('um-status').value;
    const note = document.getElementById('um-note').value.trim();
    api.updateObligation(_updateId, status, note);
    _updateModal.hide();
    if (_onUpdateSaved) _onUpdateSaved();
  });
}
function openUpdateModal(id, onSaved) {
  ensureUpdateModal();
  _updateId = id; _onUpdateSaved = onSaved;
  const o = api.getObligation(id);
  document.getElementById('um-contract-name').textContent = o.contract_name;
  document.getElementById('um-partner').textContent = o.partner;
  document.getElementById('um-assignee').textContent = o.assignee;
  document.getElementById('um-category').textContent = o.category;
  document.getElementById('um-due').textContent = o.due_date || '-';
  document.getElementById('um-content').textContent = o.content;
  document.getElementById('um-status').value = o.status || MOCK.status_options[0];
  document.getElementById('um-note').value = o.note || '';
  _updateModal.show();
}

/* =========================================================================
   페이지 정의
   ========================================================================= */
const PAGES = {};

/* ---------------- 계약서 Hub ---------------- */
PAGES.hub = {
  title: '<i class="bi bi-grid-3x3-gap me-2 text-primary"></i>계약서 Hub',
  render() {
    return `
    <div class="card search-card p-3 mb-3">
      <div class="row g-3">
        <div class="col-md-3 col-sm-6"><label class="form-label">기안부서</label>
          <div class="input-group"><input type="text" class="form-control" id="q-dept" placeholder="부서명 입력 또는 검색">
          <button class="btn btn-outline-secondary" type="button" id="q-dept-btn"><i class="bi bi-diagram-3"></i></button></div></div>
        <div class="col-md-3 col-sm-6"><label class="form-label">기안자</label>
          <div class="input-group"><input type="text" class="form-control" id="q-drafter" placeholder="이름 입력 또는 검색">
          <button class="btn btn-outline-secondary" type="button" id="q-drafter-btn"><i class="bi bi-person-badge"></i></button></div></div>
        <div class="col-md-3 col-sm-6"><label class="form-label">계약명</label><input type="text" class="form-control" id="q-name" placeholder="계약명 일부 입력"></div>
        <div class="col-md-3 col-sm-6"><label class="form-label">파트너사</label><input type="text" class="form-control" id="q-partner" placeholder="파트너사명 일부 입력"></div>
        <div class="col-md-4 col-sm-6"><label class="form-label">계약기간</label>
          <div class="d-flex align-items-center gap-2"><input type="date" class="form-control" id="q-start"><span class="text-muted">~</span><input type="date" class="form-control" id="q-end"></div></div>
        <div class="col-md-3 col-sm-6"><label class="form-label">상태</label>
          <select class="form-select" id="q-status"><option value="">전체</option><option value="예정">예정</option><option value="계약중">계약중</option><option value="만료">만료</option></select></div>
        <div class="col-12 d-flex justify-content-end gap-2 mt-2">
          <button class="btn btn-outline-secondary" id="q-reset"><i class="bi bi-arrow-counterclockwise me-1"></i>초기화</button>
          <button class="btn btn-primary px-4" id="q-run"><i class="bi bi-search me-1"></i>검색</button></div>
      </div>
    </div>
    <div class="card result-card">
      <div class="card-header bg-white fw-bold"><span><i class="bi bi-list-ul me-2 text-primary"></i>조회 결과 <span class="badge bg-secondary" id="resultCount">0</span></span></div>
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-bordered table-hover contract-table mb-0">
            <thead>
              <tr><th class="thead-basic" colspan="6">기본 사항</th><th class="thead-ai" colspan="4">AI 분석 결과</th><th class="thead-link" rowspan="2" style="width:70px">상세</th></tr>
              <tr><th class="thead-basic">계약유형</th><th class="thead-basic" style="min-width:220px">계약명</th><th class="thead-basic">기안부서</th><th class="thead-basic">기안자</th><th class="thead-basic">계약기간</th><th class="thead-basic">계약금액</th>
                  <th class="thead-ai">조항</th><th class="thead-ai">중요</th><th class="thead-ai">의무</th><th class="thead-ai">리스크</th></tr>
            </thead>
            <tbody id="resultBody"></tbody>
          </table>
        </div>
        <div class="empty-state" id="emptyState"><i class="bi bi-inbox" style="font-size:2.5rem"></i><div class="mt-2">검색 조건을 입력하고 검색 버튼을 눌러주세요</div></div>
      </div>
    </div>`;
  },
  init() {
    const run = () => {
      const results = api.searchContracts({
        dept: v('q-dept'), drafter: v('q-drafter'), name: v('q-name'), partner: v('q-partner'),
        start: v('q-start'), end: v('q-end'), status: v('q-status'),
      });
      const tbody = document.getElementById('resultBody'); tbody.innerHTML = '';
      document.getElementById('resultCount').textContent = results.length;
      document.getElementById('emptyState').style.display = results.length ? 'none' : '';
      results.forEach(r => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td class="center-cell">${esc(r.contract_type)}</td>
          <td><div class="fw-semibold">${esc(r.contract_name)} ${r.language === 'en' ? '<span class="badge bg-info-subtle text-info-emphasis border" title="해외 계약 (영문)">EN</span>' : ''}</div>
              <div class="small text-muted">${esc(r.partner)} &nbsp; ${statusBadge(r.status)}</div></td>
          <td class="center-cell">${esc(r.dept_name)}<div class="small text-muted">${esc(r.division_name)}</div></td>
          <td class="center-cell">${esc(r.drafter_name)}</td>
          <td class="center-cell small">${r.start_date}<br>~ ${r.end_date}</td>
          <td class="amount-cell">${formatAmount(r.amount, r.currency)}</td>
          <td class="center-cell">${r.clause_count}</td>
          <td class="center-cell">${r.important_clause_count}</td>
          <td class="center-cell">${r.obligation_clause_count}</td>
          <td class="center-cell">${r.risk_clause_count} ${riskBadge(r.overall_risk)}</td>
          <td class="center-cell"><a href="#contract/${r.id}" class="btn btn-sm btn-outline-primary"><i class="bi bi-box-arrow-up-right"></i></a></td>`;
        tbody.appendChild(tr);
      });
    };
    document.getElementById('q-run').onclick = run;
    document.getElementById('q-reset').onclick = () => { ['q-dept','q-drafter','q-name','q-partner','q-start','q-end','q-status'].forEach(id => document.getElementById(id).value = ''); run(); };
    document.getElementById('q-dept-btn').onclick = () => openOrgModal('dept', team => document.getElementById('q-dept').value = team);
    document.getElementById('q-drafter-btn').onclick = () => openOrgModal('drafter', null, (team, name) => { document.getElementById('q-drafter').value = name; document.getElementById('q-dept').value = team; });
    run();
  },
};

/* ---------------- 의무조항 관리 ---------------- */
PAGES.obligations = {
  title: '<i class="bi bi-clipboard-check me-2 text-primary"></i>의무조항 관리',
  render() {
    const quantCats = MOCK.quant_categories.map(c => `<option value="${esc(c)}">${esc(c)}</option>`).join('');
    const qualCats = MOCK.qual_categories.map(c => `<option value="${esc(c)}">${esc(c)}</option>`).join('');
    const statusOpts = MOCK.status_options.map(s => `<option value="${s}">${s}</option>`).join('');
    return `
    <ul class="nav nav-tabs mb-3" id="obTab">
      <li class="nav-item"><a class="nav-link active" data-tab="quant"><i class="bi bi-calendar-check me-1"></i>정량적 의무사항</a></li>
      <li class="nav-item"><a class="nav-link" data-tab="qual"><i class="bi bi-list-check me-1"></i>정성적 의무사항</a></li>
    </ul>
    <div id="pane-quant">
      <div class="kind-hint mb-2"><i class="bi bi-info-circle me-1"></i>기한에 맞춰 후속 조치가 필요한 의무 조항입니다.</div>
      <div class="card search-card p-3 mb-3"><div class="row g-3">
        <div class="col-md-3 col-sm-6"><label class="form-label">기안부서</label><div class="input-group"><input type="text" class="form-control" id="qt-dept" placeholder="부서명 입력 또는 검색"><button class="btn btn-outline-secondary" type="button" id="qt-dept-btn"><i class="bi bi-diagram-3"></i></button></div></div>
        <div class="col-md-3 col-sm-6"><label class="form-label">기안자</label><div class="input-group"><input type="text" class="form-control" id="qt-drafter" placeholder="이름 입력 또는 검색"><button class="btn btn-outline-secondary" type="button" id="qt-drafter-btn"><i class="bi bi-person-badge"></i></button></div></div>
        <div class="col-md-3 col-sm-6"><label class="form-label">계약명</label><input type="text" class="form-control" id="qt-name" placeholder="계약명 일부 입력"></div>
        <div class="col-md-3 col-sm-6"><label class="form-label">파트너사</label><input type="text" class="form-control" id="qt-partner" placeholder="파트너사명 일부 입력"></div>
        <div class="col-md-3 col-sm-6"><label class="form-label">조항 구분</label><select class="form-select" id="qt-category"><option value="">전체</option>${quantCats}</select></div>
        <div class="col-md-3 col-sm-6"><label class="form-label">진행 상태</label><select class="form-select" id="qt-status"><option value="">전체</option>${statusOpts}</select></div>
        <div class="col-12 d-flex justify-content-end gap-2 mt-2"><button class="btn btn-outline-secondary" id="qt-reset"><i class="bi bi-arrow-counterclockwise me-1"></i>초기화</button><button class="btn btn-primary px-4" id="qt-run"><i class="bi bi-search me-1"></i>검색</button></div>
      </div></div>
      <div class="card result-card"><div class="card-header bg-white fw-bold"><span><i class="bi bi-list-ul me-2 text-primary"></i>조회 결과 <span class="badge bg-secondary" id="qtResultCount">0</span></span></div>
        <div class="card-body p-0"><div class="table-responsive"><table class="table table-bordered table-hover ob-table mb-0"><thead><tr>
          <th>파트너사</th><th style="min-width:200px">계약명</th><th>조항 구분</th><th style="min-width:280px">내용</th><th>기한일</th><th>부서</th><th>담당자</th><th>후속 조치 상태</th><th style="width:70px">관리</th>
        </tr></thead><tbody id="qtBody"></tbody></table></div>
        <div class="empty-state" id="qtEmpty"><i class="bi bi-inbox" style="font-size:2.5rem"></i><div class="mt-2">검색 조건을 입력하고 검색 버튼을 눌러주세요</div></div></div></div>
    </div>
    <div id="pane-qual" style="display:none">
      <div class="kind-hint mb-2"><i class="bi bi-info-circle me-1"></i>별도의 기한이나 후속 조치가 필요하지 않은 의무 조항입니다.</div>
      <div class="card search-card p-3 mb-3"><div class="row g-3">
        <div class="col-md-3 col-sm-6"><label class="form-label">기안부서</label><div class="input-group"><input type="text" class="form-control" id="ql-dept" placeholder="부서명 입력 또는 검색"><button class="btn btn-outline-secondary" type="button" id="ql-dept-btn"><i class="bi bi-diagram-3"></i></button></div></div>
        <div class="col-md-3 col-sm-6"><label class="form-label">기안자</label><div class="input-group"><input type="text" class="form-control" id="ql-drafter" placeholder="이름 입력 또는 검색"><button class="btn btn-outline-secondary" type="button" id="ql-drafter-btn"><i class="bi bi-person-badge"></i></button></div></div>
        <div class="col-md-3 col-sm-6"><label class="form-label">계약명</label><input type="text" class="form-control" id="ql-name" placeholder="계약명 일부 입력"></div>
        <div class="col-md-3 col-sm-6"><label class="form-label">파트너사</label><input type="text" class="form-control" id="ql-partner" placeholder="파트너사명 일부 입력"></div>
        <div class="col-md-3 col-sm-6"><label class="form-label">조항 구분</label><select class="form-select" id="ql-category"><option value="">전체</option>${qualCats}</select></div>
        <div class="col-12 d-flex justify-content-end gap-2 mt-2"><button class="btn btn-outline-secondary" id="ql-reset"><i class="bi bi-arrow-counterclockwise me-1"></i>초기화</button><button class="btn btn-primary px-4" id="ql-run"><i class="bi bi-search me-1"></i>검색</button></div>
      </div></div>
      <div class="card result-card"><div class="card-header bg-white fw-bold"><span><i class="bi bi-list-ul me-2 text-primary"></i>조회 결과 <span class="badge bg-secondary" id="qlResultCount">0</span></span></div>
        <div class="card-body p-0"><div class="table-responsive"><table class="table table-bordered table-hover ob-table mb-0"><thead><tr>
          <th>파트너사</th><th style="min-width:200px">계약명</th><th>조항 구분</th><th style="min-width:320px">내용</th><th>부서</th><th>담당자</th>
        </tr></thead><tbody id="qlBody"></tbody></table></div>
        <div class="empty-state" id="qlEmpty"><i class="bi bi-inbox" style="font-size:2.5rem"></i><div class="mt-2">검색 조건을 입력하고 검색 버튼을 눌러주세요</div></div></div></div>
    </div>`;
  },
  init() {
    let qtResults = [];
    const runQuant = () => {
      qtResults = api.searchObligations({ kind: 'quant', dept: v('qt-dept'), drafter: v('qt-drafter'), name: v('qt-name'), partner: v('qt-partner'), category: v('qt-category'), status: v('qt-status') });
      const tbody = document.getElementById('qtBody'); tbody.innerHTML = '';
      document.getElementById('qtResultCount').textContent = qtResults.length;
      document.getElementById('qtEmpty').style.display = qtResults.length ? 'none' : '';
      qtResults.forEach(o => {
        const overdue = o.due_date && o.due_date < TODAY && o.status !== '완료';
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td class="center-cell">${esc(o.partner)}</td><td>${esc(o.contract_name)}</td>
          <td class="center-cell">${categoryBadge(o.category)}</td><td class="ob-content small">${esc(o.content)}</td>
          <td class="center-cell ${overdue ? 'due-overdue' : ''}">${o.due_date || '-'}</td>
          <td class="center-cell">${esc(o.dept_name)}</td><td class="center-cell">${esc(o.assignee)}</td>
          <td class="center-cell">${statusBadge(o.status)}</td>
          <td class="center-cell"><button class="btn btn-sm btn-outline-primary" data-ob="${o.id}"><i class="bi bi-pencil-square"></i></button></td>`;
        tbody.appendChild(tr);
      });
      tbody.querySelectorAll('[data-ob]').forEach(btn => btn.onclick = () => openUpdateModal(btn.dataset.ob, runQuant));
    };
    const runQual = () => {
      const results = api.searchObligations({ kind: 'qual', dept: v('ql-dept'), drafter: v('ql-drafter'), name: v('ql-name'), partner: v('ql-partner'), category: v('ql-category') });
      const tbody = document.getElementById('qlBody'); tbody.innerHTML = '';
      document.getElementById('qlResultCount').textContent = results.length;
      document.getElementById('qlEmpty').style.display = results.length ? 'none' : '';
      results.forEach(o => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td class="center-cell">${esc(o.partner)}</td><td>${esc(o.contract_name)}</td><td class="center-cell">${categoryBadge(o.category)}</td><td class="ob-content small">${esc(o.content)}</td><td class="center-cell">${esc(o.dept_name)}</td><td class="center-cell">${esc(o.assignee)}</td>`;
        tbody.appendChild(tr);
      });
    };
    document.querySelectorAll('[data-tab]').forEach(link => link.addEventListener('click', e => {
      e.preventDefault();
      document.querySelectorAll('[data-tab]').forEach(l => l.classList.remove('active'));
      link.classList.add('active');
      const tab = link.dataset.tab;
      document.getElementById('pane-quant').style.display = tab === 'quant' ? '' : 'none';
      document.getElementById('pane-qual').style.display = tab === 'qual' ? '' : 'none';
      if (tab === 'qual') runQual();
    }));
    document.getElementById('qt-run').onclick = runQuant;
    document.getElementById('qt-reset').onclick = () => { ['qt-dept','qt-drafter','qt-name','qt-partner','qt-category','qt-status'].forEach(id => document.getElementById(id).value = ''); runQuant(); };
    document.getElementById('ql-run').onclick = runQual;
    document.getElementById('ql-reset').onclick = () => { ['ql-dept','ql-drafter','ql-name','ql-partner','ql-category'].forEach(id => document.getElementById(id).value = ''); runQual(); };
    document.getElementById('qt-dept-btn').onclick = () => openOrgModal('dept', team => document.getElementById('qt-dept').value = team);
    document.getElementById('qt-drafter-btn').onclick = () => openOrgModal('drafter', null, (team, name) => { document.getElementById('qt-drafter').value = name; document.getElementById('qt-dept').value = team; });
    document.getElementById('ql-dept-btn').onclick = () => openOrgModal('dept', team => document.getElementById('ql-dept').value = team);
    document.getElementById('ql-drafter-btn').onclick = () => openOrgModal('drafter', null, (team, name) => { document.getElementById('ql-drafter').value = name; document.getElementById('ql-dept').value = team; });
    runQuant();
  },
};

/* ---------------- Dashboard ---------------- */
PAGES.dashboard = {
  title: '<i class="bi bi-speedometer2 me-2 text-primary"></i>Dashboard',
  render() {
    return `
    <div class="card dept-card p-3 mb-3"><div class="row g-3 align-items-end">
      <div class="col-md-4 col-sm-6"><label class="form-label fw-semibold small text-muted">부서 선택</label>
        <select class="form-select" id="deptFilter"><option value="">전체</option></select></div>
    </div></div>
    <div class="row g-3 mb-4">
      <div class="col-md-4"><div class="card stat-card p-3 h-100" id="card-valid"><div class="d-flex align-items-center gap-3">
        <div class="icon icon-valid"><i class="bi bi-file-earmark-check"></i></div>
        <div><div class="stat-label">현재 유효한 계약수</div><div class="stat-value" id="stat-valid">-</div><div class="stat-hint">클릭하여 목록 보기</div></div></div></div></div>
      <div class="col-md-4"><div class="card stat-card p-3 h-100" id="card-expiring"><div class="d-flex align-items-center gap-3">
        <div class="icon icon-expiring"><i class="bi bi-hourglass-split"></i></div>
        <div><div class="stat-label">30일 이내 만료되는 계약수</div><div class="stat-value" id="stat-expiring">-</div><div class="stat-hint">클릭하여 목록 보기</div></div></div></div></div>
      <div class="col-md-4"><div class="card stat-card p-3 h-100" id="card-overdue"><div class="d-flex align-items-center gap-3">
        <div class="icon icon-overdue"><i class="bi bi-exclamation-triangle"></i></div>
        <div><div class="stat-label">의무사항 조치 기한 만료 건수</div><div class="stat-value" id="stat-overdue">-</div><div class="stat-hint">클릭하여 목록 보기</div></div></div></div></div>
    </div>
    <div class="card result-card">
      <div class="card-header bg-white fw-bold d-flex justify-content-between align-items-center">
        <span><i class="bi bi-alarm me-2 text-danger"></i>임박·만료 의무사항 <span class="badge bg-secondary" id="urgentCount">0</span></span>
        <span class="small text-muted">기한 만료 또는 7일 이내 도래 항목</span></div>
      <div class="card-body p-0"><div class="table-responsive"><table class="table table-bordered table-hover ob-table mb-0"><thead><tr>
        <th>파트너사</th><th style="min-width:200px">계약명</th><th>조항 구분</th><th style="min-width:260px">내용</th><th>기한일</th><th>부서</th><th>담당자</th><th>상태</th><th style="width:70px">관리</th>
      </tr></thead><tbody id="urgentBody"></tbody></table></div>
      <div class="empty-state" id="urgentEmpty" style="display:none"><i class="bi bi-emoji-smile" style="font-size:2rem"></i><div class="mt-2">임박하거나 만료된 의무사항이 없습니다</div></div></div>
    </div>`;
  },
  init() {
    const select = document.getElementById('deptFilter');
    api.org().forEach(division => {
      const group = document.createElement('optgroup'); group.label = division.name;
      division.children.forEach(team => { const opt = document.createElement('option'); opt.value = team.name; opt.textContent = team.name; group.appendChild(opt); });
      select.appendChild(group);
    });
    const dept = () => select.value;
    const renderRows = (results, bodyId, emptyId, reload) => {
      const tbody = document.getElementById(bodyId); tbody.innerHTML = '';
      document.getElementById(emptyId).style.display = results.length ? 'none' : '';
      results.forEach(o => {
        const overdue = o.due_date < TODAY; const dueClass = overdue ? 'due-overdue' : 'due-soon';
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td class="center-cell">${esc(o.partner)}</td><td>${esc(o.contract_name)}</td>
          <td class="center-cell">${categoryBadge(o.category)}</td><td class="ob-content small">${esc(o.content)}</td>
          <td class="center-cell ${dueClass}">${o.due_date}${overdue ? ' (만료)' : ''}</td>
          <td class="center-cell">${esc(o.dept_name)}</td><td class="center-cell">${esc(o.assignee)}</td>
          <td class="center-cell">${statusBadge(o.status)}</td>
          <td class="center-cell"><button class="btn btn-sm btn-outline-primary" data-ob="${o.id}"><i class="bi bi-pencil-square"></i></button></td>`;
        tbody.appendChild(tr);
      });
      tbody.querySelectorAll('[data-ob]').forEach(btn => btn.onclick = () => openUpdateModal(btn.dataset.ob, reload));
    };
    const loadUrgent = () => {
      const results = api.urgentObligations(dept(), 7).map(obligationSummary).sort((a,b)=>(a.due_date||'').localeCompare(b.due_date||''));
      document.getElementById('urgentCount').textContent = results.length;
      renderRows(results, 'urgentBody', 'urgentEmpty', load);
    };
    function load() {
      document.getElementById('stat-valid').textContent = api.validContracts(dept()).length;
      document.getElementById('stat-expiring').textContent = api.expiringContracts(dept(), 30).length;
      document.getElementById('stat-overdue').textContent = api.overdueObligations(dept()).length;
      loadUrgent();
    }
    select.onchange = load;

    document.getElementById('card-valid').onclick = () => openContractModal('valid', dept());
    document.getElementById('card-expiring').onclick = () => openContractModal('expiring', dept());
    document.getElementById('card-overdue').onclick = () => {
      ensureDashboardModals();
      const results = api.overdueObligations(dept()).map(obligationSummary).sort((a,b)=>(a.due_date||'').localeCompare(b.due_date||''));
      renderRows(results, 'obligationModalBody', 'obligationModalEmpty', () => { load(); document.getElementById('card-overdue').click(); });
      _obligationModal.show();
    };
    load();
  },
};

let _contractModal = null, _obligationModal = null;
function ensureDashboardModals() {
  if (!document.getElementById('contractModal')) {
    const w = document.createElement('div');
    w.innerHTML = `
    <div class="modal fade" id="contractModal" tabindex="-1"><div class="modal-dialog modal-xl modal-dialog-scrollable"><div class="modal-content">
      <div class="modal-header py-2"><h6 class="modal-title fw-bold" id="contractModalTitle"></h6><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
      <div class="modal-body p-0"><div class="table-responsive"><table class="table table-bordered ct-table mb-0"><thead><tr>
        <th>계약유형</th><th style="min-width:200px">계약명</th><th>기안부서</th><th>기안자</th><th>계약기간</th><th>계약금액</th><th id="ctExtraHeader" style="display:none">D-day</th><th style="width:60px">상세</th>
      </tr></thead><tbody id="contractModalBody"></tbody></table></div>
      <div class="empty-state" id="contractModalEmpty" style="display:none"><div class="mt-2">해당하는 계약이 없습니다</div></div></div>
    </div></div></div>`;
    document.body.appendChild(w.firstElementChild);
    _contractModal = new bootstrap.Modal(document.getElementById('contractModal'));
  }
  if (!document.getElementById('obligationModal')) {
    const w = document.createElement('div');
    w.innerHTML = `
    <div class="modal fade" id="obligationModal" tabindex="-1"><div class="modal-dialog modal-xl modal-dialog-scrollable"><div class="modal-content">
      <div class="modal-header py-2"><h6 class="modal-title fw-bold"><i class="bi bi-exclamation-triangle me-2 text-danger"></i>기한 만료 의무사항</h6><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
      <div class="modal-body p-0"><div class="table-responsive"><table class="table table-bordered ob-table mb-0"><thead><tr>
        <th>파트너사</th><th style="min-width:200px">계약명</th><th>조항 구분</th><th style="min-width:260px">내용</th><th>기한일</th><th>부서</th><th>담당자</th><th>상태</th><th style="width:70px">관리</th>
      </tr></thead><tbody id="obligationModalBody"></tbody></table></div>
      <div class="empty-state" id="obligationModalEmpty" style="display:none"><div class="mt-2">기한이 만료된 의무사항이 없습니다</div></div></div>
    </div></div></div>`;
    document.body.appendChild(w.firstElementChild);
    _obligationModal = new bootstrap.Modal(document.getElementById('obligationModal'));
  }
}
function openContractModal(mode, dept) {
  ensureDashboardModals();
  const isExpiring = mode === 'expiring';
  const list = isExpiring ? api.expiringContracts(dept, 30) : api.validContracts(dept);
  const results = list.map(contractSummary).sort((a, b) => a.end_date.localeCompare(b.end_date));
  document.getElementById('contractModalTitle').innerHTML = isExpiring
    ? '<i class="bi bi-hourglass-split me-2 text-warning"></i>30일 이내 만료되는 계약'
    : '<i class="bi bi-file-earmark-check me-2 text-success"></i>현재 유효한 계약';
  document.getElementById('ctExtraHeader').style.display = isExpiring ? '' : 'none';
  const tbody = document.getElementById('contractModalBody'); tbody.innerHTML = '';
  document.getElementById('contractModalEmpty').style.display = results.length ? 'none' : '';
  results.forEach(c => {
    const dday = daysUntil(c.end_date);
    const ddayCell = isExpiring ? `<td class="center-cell ${dday <= 7 ? 'due-overdue' : 'due-soon'}">D-${dday}</td>` : '';
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td class="center-cell">${esc(c.contract_type)}</td><td>${esc(c.contract_name)}</td>
      <td class="center-cell">${esc(c.dept_name)}</td><td class="center-cell">${esc(c.drafter_name)}</td>
      <td class="center-cell small">${c.start_date}<br>~ ${c.end_date}</td><td class="amount-cell">${formatAmount(c.amount, c.currency)}</td>
      ${ddayCell}<td class="center-cell"><a href="#contract/${c.id}" class="btn btn-sm btn-outline-primary"><i class="bi bi-box-arrow-up-right"></i></a></td>`;
    tbody.appendChild(tr);
  });
  _contractModal.show();
}

/* ---------------- 권한 관리 ---------------- */
PAGES.access = {
  title: '권한 관리',
  render() {
    return `
    <div class="row">
      <div class="col-md-5">
        <div class="card mb-3"><div class="card-body">
          <h6 class="card-title">역할 목록</h6>
          <ul id="roleList" class="list-group"></ul>
          <div class="mt-3 d-flex">
            <input id="newRoleInput" class="form-control me-2" placeholder="새 역할 id (예: manager)">
            <input id="newRoleLabel" class="form-control me-2" placeholder="표시명">
            <button id="addRoleBtn" class="btn btn-primary">추가</button>
          </div></div></div>
        <div class="card"><div class="card-body">
          <h6 class="card-title">사용자 검색 / 권한 부여</h6>
          <div class="input-group mb-2"><input id="userSearch" class="form-control" placeholder="사용자 이름 또는 ID 검색"><button id="searchUserBtn" class="btn btn-outline-secondary">검색</button></div>
          <ul id="userSearchResults" class="list-group"></ul></div></div>
      </div>
      <div class="col-md-7">
        <div class="card"><div class="card-body">
          <h6 class="card-title">선택된 역할의 페이지 접근 설정</h6>
          <div id="pagesCheckboxes" class="mb-3"></div>
          <button id="saveRolePages" class="btn btn-success">저장</button></div></div>
        <div class="card mt-3"><div class="card-body">
          <h6 class="card-title">선택된 역할의 사용자</h6>
          <ul id="roleUsers" class="list-group"></ul></div></div>
      </div>
    </div>`;
  },
  init() {
    const navPages = MOCK.nav_pages;
    let selectedRoleId = null;
    function load() {
      const data = api.permissions();
      const ul = document.getElementById('roleList'); ul.innerHTML = '';
      data.roles.forEach(r => {
        const li = document.createElement('li'); li.className = 'list-group-item d-flex justify-content-between align-items-center'; li.style.cursor = 'pointer';
        li.innerHTML = `<div><strong>${esc(r.label)}</strong> <small class="text-muted">(${esc(r.id)})</small></div>`;
        li.addEventListener('click', () => { selectedRoleId = r.id; load(); });
        const del = document.createElement('button'); del.className = 'btn btn-sm btn-outline-danger'; del.textContent = '삭제';
        del.addEventListener('click', e => { e.stopPropagation(); if (confirm('삭제하시겠습니까?')) { api.deleteRole(r.id); selectedRoleId = null; load(); } });
        li.appendChild(del); ul.appendChild(li);
      });
      if (!selectedRoleId && data.roles.length) selectedRoleId = data.roles[0].id;
      const role = data.roles.find(r => r.id === selectedRoleId);
      const pagesDiv = document.getElementById('pagesCheckboxes'); pagesDiv.innerHTML = '';
      if (!role) { pagesDiv.innerHTML = '<div class="text-muted">역할 선택하세요</div>'; document.getElementById('roleUsers').innerHTML = ''; return; }
      navPages.forEach(p => {
        const cb = document.createElement('div'); cb.className = 'form-check';
        cb.innerHTML = `<input class="form-check-input" type="checkbox" id="chk_${p.key}" ${role.pages.includes(p.key) ? 'checked' : ''}>
          <label class="form-check-label" for="chk_${p.key}">${esc(p.label)} (${esc(p.key)})</label>`;
        pagesDiv.appendChild(cb);
      });
      const urs = data.user_roles.filter(u => u.roles && u.roles.includes(role.id));
      const rul = document.getElementById('roleUsers'); rul.innerHTML = '';
      urs.forEach(u => {
        const li = document.createElement('li'); li.className = 'list-group-item d-flex justify-content-between align-items-center';
        li.textContent = `${u.user_id} (${u.name || ''})`;
        const btn = document.createElement('button'); btn.className = 'btn btn-sm btn-outline-danger'; btn.textContent = '권한 제거';
        btn.addEventListener('click', () => { if (confirm('권한을 제거하시겠습니까?')) { api.removeUserRole(u.user_id, role.id); load(); } });
        li.appendChild(btn); rul.appendChild(li);
      });
    }
    document.getElementById('addRoleBtn').onclick = () => {
      const id = document.getElementById('newRoleInput').value.trim();
      const label = document.getElementById('newRoleLabel').value.trim() || id;
      if (!id) return alert('id 입력');
      if (api.addRole(id, label, [])) { document.getElementById('newRoleInput').value = ''; document.getElementById('newRoleLabel').value = ''; load(); }
      else alert('이미 존재하는 역할입니다');
    };
    document.getElementById('saveRolePages').onclick = () => {
      if (!selectedRoleId) return alert('역할 선택');
      const pages = Array.from(document.querySelectorAll('#pagesCheckboxes input[type=checkbox]')).filter(c => c.checked).map(c => c.id.replace('chk_', ''));
      api.updateRolePages(selectedRoleId, pages); load(); alert('저장되었습니다');
    };
    document.getElementById('searchUserBtn').onclick = () => {
      const q = document.getElementById('userSearch').value.trim();
      const ul = document.getElementById('userSearchResults'); ul.innerHTML = '';
      api.searchUsers(q).forEach(u => {
        const li = document.createElement('li'); li.className = 'list-group-item d-flex justify-content-between align-items-center';
        li.textContent = `${u.id} - ${u.name}`;
        const addBtn = document.createElement('button'); addBtn.className = 'btn btn-sm btn-primary'; addBtn.textContent = '부여';
        addBtn.addEventListener('click', () => { if (!selectedRoleId) return alert('역할 선택'); if (api.assignRole(u.id, selectedRoleId)) load(); });
        li.appendChild(addBtn); ul.appendChild(li);
      });
    };
    load();
  },
};

/* ---------------- 계약서 상세 ---------------- */
function renderDetail(id) {
  const c = api.getContract(id);
  setActiveNav('hub');
  document.getElementById('headerExtra').innerHTML = '';
  if (!c) {
    document.getElementById('pageTitle').innerHTML = '<i class="bi bi-file-earmark-text me-2 text-primary"></i>계약서 상세';
    document.getElementById('pageContent').innerHTML = '<div class="text-muted text-center py-5">계약서를 찾을 수 없습니다.</div>';
    return;
  }
  const ai = c.ai;
  document.getElementById('pageTitle').innerHTML = '<i class="bi bi-file-earmark-text me-2 text-primary"></i>계약서 상세';
  document.getElementById('headerExtra').innerHTML = '<a href="#hub" class="btn btn-sm btn-outline-secondary"><i class="bi bi-arrow-left me-1"></i>목록으로</a>';
  document.getElementById('pageContent').innerHTML = `
    <div class="row g-3 mb-3">
      <div class="col-lg-6"><div class="card info-card p-3 h-100">
        <div class="d-flex justify-content-between align-items-start mb-2">
          <div><div class="text-muted small mb-1">${esc(c.contract_type)}</div><h5 class="fw-bold mb-0">${esc(c.contract_name)}</h5></div>
          <span class="badge status-badge status-${c.status}">${c.status}</span></div>
        <hr>
        <div class="info-row"><div class="info-label">기안부서</div><div class="info-value">${esc(c.dept_name)} (${esc(c.division_name)})</div></div>
        <div class="info-row"><div class="info-label">기안자</div><div class="info-value">${esc(c.drafter_name)}</div></div>
        <div class="info-row"><div class="info-label">파트너사</div><div class="info-value">${esc(c.partner)}</div></div>
        <div class="info-row"><div class="info-label">계약기간</div><div class="info-value">${c.start_date} ~ ${c.end_date}</div></div>
        <div class="info-row"><div class="info-label">계약금액</div><div class="info-value">${formatAmount(c.amount, c.currency)}</div></div>
        <div class="info-row"><div class="info-label">첨부파일</div><div class="info-value text-muted"><i class="bi bi-paperclip me-1"></i>${esc(c.file_name)}</div></div>
      </div></div>
      <div class="col-lg-6"><div class="row g-3 h-100">
        <div class="col-6"><div class="card stat-card p-3 h-100"><div class="d-flex align-items-center gap-3"><div class="icon icon-total"><i class="bi bi-list-ol"></i></div><div><div class="text-muted small">조항수</div><div class="fw-bold fs-4">${ai.clause_count}</div></div></div></div></div>
        <div class="col-6"><div class="card stat-card p-3 h-100"><div class="d-flex align-items-center gap-3"><div class="icon icon-important"><i class="bi bi-star-fill"></i></div><div><div class="text-muted small">중요조항수</div><div class="fw-bold fs-4">${ai.important_clause_count}</div></div></div></div></div>
        <div class="col-6"><div class="card stat-card p-3 h-100"><div class="d-flex align-items-center gap-3"><div class="icon icon-obligation"><i class="bi bi-clipboard-check"></i></div><div><div class="text-muted small">의무조항수</div><div class="fw-bold fs-4">${ai.obligation_clause_count}</div></div></div></div></div>
        <div class="col-6"><div class="card stat-card p-3 h-100"><div class="d-flex align-items-center gap-3"><div class="icon icon-risk"><i class="bi bi-exclamation-triangle-fill"></i></div><div><div class="text-muted small">리스크조항수</div><div class="fw-bold fs-4">${ai.risk_clause_count}</div></div></div></div></div>
        <div class="col-12"><div class="card stat-card p-3" style="cursor:default">
          <div class="d-flex justify-content-between align-items-center mb-1"><span class="fw-bold small"><i class="bi bi-robot me-1 text-primary"></i>AI 종합 소견</span><span class="badge badge-risk-${ai.overall_risk}">종합 리스크: ${ai.overall_risk}</span></div>
          <div class="small text-muted">${esc(ai.summary)}</div></div></div>
      </div></div>
    </div>
    <div class="card info-card">
      <div class="card-header bg-white fw-bold d-flex justify-content-between align-items-center flex-wrap gap-2">
        <span><i class="bi bi-journal-text me-2 text-primary"></i>조항 상세 <span class="badge bg-secondary" id="clauseCount">0</span></span>
        <div class="d-flex gap-1" id="typeFilters">
          <span class="badge border filter-chip active" data-type="all">전체</span>
          <span class="badge border filter-chip" data-type="중요">중요</span>
          <span class="badge border filter-chip" data-type="의무">의무</span>
          <span class="badge border filter-chip" data-type="리스크">리스크</span>
          <span class="badge border filter-chip" data-type="일반">일반</span></div>
      </div>
      <div class="card-body p-0"><table class="table table-hover mb-0"><thead class="table-light"><tr>
        <th style="width:50px">#</th><th style="width:90px">유형</th><th style="width:110px">구분</th><th style="width:90px">의무 주체</th><th style="width:200px">조항명</th><th>내용</th>
      </tr></thead><tbody id="clauseBody"></tbody></table></div>
    </div>`;
  let activeFilter = 'all';
  const renderClauses = () => {
    const clauses = activeFilter === 'all' ? ai.clauses : ai.clauses.filter(cl => cl.type === activeFilter);
    document.getElementById('clauseCount').textContent = clauses.length;
    const tbody = document.getElementById('clauseBody'); tbody.innerHTML = '';
    clauses.forEach(cl => {
      const riskTag = cl.risk_level ? `<span class="badge bg-light text-dark border ms-1">${cl.risk_level}</span>` : '';
      const tr = document.createElement('tr'); tr.className = 'clause-row';
      tr.innerHTML = `
        <td class="text-muted">${cl.no}</td>
        <td><span class="badge clause-type-badge type-${cl.type}">${cl.type}</span>${riskTag}</td>
        <td><span class="badge category-badge">${esc(cl.category)}</span></td>
        <td><span class="badge duty-badge duty-${cl.duty_party}">${cl.duty_party}</span></td>
        <td class="fw-semibold">${esc(cl.title)}</td>
        <td class="clause-content">${esc(cl.content)}</td>`;
      tbody.appendChild(tr);
    });
  };
  document.querySelectorAll('.filter-chip').forEach(chip => chip.addEventListener('click', () => {
    document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
    chip.classList.add('active'); activeFilter = chip.dataset.type; renderClauses();
  }));
  renderClauses();
}

/* =========================================================================
   사이드바 + 라우터
   ========================================================================= */
function v(id) { const el = document.getElementById(id); return el ? el.value : ''; }

function renderSidebar() {
  const nav = document.getElementById('sidebarNav');
  let html = '<div class="sidebar-section-label">페이지</div>';
  MOCK.nav_pages.forEach(p => {
    if (p.external) {
      html += `<a class="sidebar-link disabled" data-key="${p.key}" title="${esc(p.label)} (링크 미설정)"><i class="bi ${p.icon}"></i><span class="sidebar-link-label">${esc(p.label)}</span></a>`;
    } else {
      html += `<a class="sidebar-link" data-key="${p.key}" href="#${p.key}"><i class="bi ${p.icon}"></i><span class="sidebar-link-label">${esc(p.label)}</span></a>`;
    }
  });
  nav.innerHTML = html;
}
function setActiveNav(key) {
  document.querySelectorAll('.sidebar-link').forEach(l => l.classList.toggle('active', l.dataset.key === key));
}

function route() {
  const hash = (location.hash || '#hub').slice(1);
  if (hash.startsWith('contract/')) { renderDetail(hash.slice('contract/'.length)); window.scrollTo(0, 0); return; }
  const key = PAGES[hash] ? hash : 'hub';
  const page = PAGES[key];
  setActiveNav(key);
  document.getElementById('pageTitle').innerHTML = page.title;
  document.getElementById('headerExtra').innerHTML = '';
  document.getElementById('pageContent').innerHTML = page.render();
  page.init();
  window.scrollTo(0, 0);
}

document.getElementById('sidebarToggleBtn').addEventListener('click', () => {
  document.documentElement.classList.toggle('sidebar-collapsed');
});
window.addEventListener('hashchange', route);
renderSidebar();
route();
</script>
</body>
</html>
"""

html = HTML.replace('__MOCK_DATA__', DATA_JSON)
with open(OUT, 'w', encoding='utf-8') as f:
    f.write(html)
print('wrote', OUT, '(%.1f KB)' % (len(html) / 1024))
