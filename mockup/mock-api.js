// 계약서 관리 목업 - 클라이언트 사이드 모의 API
// 원본 Flask app.py의 서버 로직을 브라우저에서 동일하게 재현합니다.
// 서버·네트워크 없이 window.APP_DATA(data.js)만으로 동작합니다.
(function () {
  'use strict';

  if (!window.APP_DATA) {
    console.error('APP_DATA가 없습니다. data.js가 먼저 로드되어야 합니다.');
    return;
  }

  var contracts = window.APP_DATA.contracts;
  var obligations = window.APP_DATA.obligations;
  var departments = window.APP_DATA.departments;

  // ---- 의무조항 상태 변경 저장 (localStorage) ---------------------------
  // 목업이지만 상태/후속조치 변경이 새로고침 후에도 유지되도록 브라우저에 저장.
  var LS_KEY = 'mockup_obligation_overrides';

  function loadOverrides() {
    try { return JSON.parse(localStorage.getItem(LS_KEY) || '{}'); }
    catch (e) { return {}; }
  }
  function saveOverrides(o) {
    try { localStorage.setItem(LS_KEY, JSON.stringify(o)); } catch (e) {}
  }

  // 저장된 변경분을 데이터에 반영
  var overrides = loadOverrides();
  obligations.forEach(function (o) {
    var ov = overrides[o.id];
    if (ov) {
      o.status = ov.status;
      o.note = ov.note;
      o.updated_at = ov.updated_at;
    }
  });

  // ---- 날짜 헬퍼 (원본은 서버의 date.today() 사용) ----------------------
  function pad(n) { return String(n).padStart(2, '0'); }
  function toISO(d) { return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate()); }
  function today() { return toISO(new Date()); }
  function todayPlus(days) { var d = new Date(); d.setDate(d.getDate() + days); return toISO(d); }

  var STATUS_OPTIONS = ['대기', '진행중', '완료', '지연'];

  function lc(s) { return (s || '').toLowerCase(); }

  // ==================== 조직도 ====================
  function org() { return departments; }

  // ==================== 계약서 검색 ====================
  function searchContracts(p) {
    p = p || {};
    var dept = lc((p.dept || '').trim());
    var drafter = lc((p.drafter || '').trim());
    var name = lc((p.name || '').trim());
    var partner = lc((p.partner || '').trim());
    var start = (p.start || '').trim();
    var end = (p.end || '').trim();
    var status = (p.status || '').trim();

    var results = contracts.filter(function (c) {
      if (dept && lc(c.dept_name).indexOf(dept) < 0 && lc(c.division_name).indexOf(dept) < 0) return false;
      if (drafter && lc(c.drafter_name).indexOf(drafter) < 0) return false;
      if (name && lc(c.contract_name).indexOf(name) < 0 && lc(c.contract_name_ko || '').indexOf(name) < 0) return false;
      if (partner && lc(c.partner).indexOf(partner) < 0) return false;
      if (start && c.end_date < start) return false;
      if (end && c.start_date > end) return false;
      if (status && c.status !== status) return false;
      return true;
    });

    results.sort(function (a, b) { return a.start_date < b.start_date ? 1 : (a.start_date > b.start_date ? -1 : 0); });
    return { count: results.length, results: results };
  }

  function getContract(id) {
    return contracts.find(function (c) { return c.id === id; }) || null;
  }

  // ==================== 의무조항 검색 ====================
  function searchObligations(p) {
    p = p || {};
    var kind = (p.kind || 'quant').trim();
    var dept = lc((p.dept || '').trim());
    var drafter = lc((p.drafter || '').trim());
    var name = lc((p.name || '').trim());
    var partner = lc((p.partner || '').trim());
    var category = (p.category || '').trim();
    var status = (p.status || '').trim();

    var results = obligations.filter(function (o) {
      if (o.kind !== kind) return false;
      if (dept && lc(o.dept_name).indexOf(dept) < 0 && lc(o.division_name).indexOf(dept) < 0) return false;
      if (drafter && lc(o.drafter_name).indexOf(drafter) < 0) return false;
      if (name && lc(o.contract_name).indexOf(name) < 0) return false;
      if (partner && lc(o.partner).indexOf(partner) < 0) return false;
      if (category && o.category !== category) return false;
      if (status && o.status !== status) return false;
      return true;
    });

    results.sort(function (a, b) {
      var ax = a.due_date == null, bx = b.due_date == null;
      if (ax !== bx) return ax ? 1 : -1;
      var av = a.due_date || '', bv = b.due_date || '';
      return av < bv ? -1 : (av > bv ? 1 : 0);
    });
    return { count: results.length, results: results };
  }

  function getObligation(id) {
    return obligations.find(function (o) { return o.id === id; }) || null;
  }

  function updateObligation(id, body) {
    body = body || {};
    var status = body.status;
    var note = body.note || '';
    if (STATUS_OPTIONS.indexOf(status) < 0) {
      return { error: 'invalid status: ' + status };
    }
    var o = getObligation(id);
    if (!o) return { error: 'not found' };
    o.status = status;
    o.note = note;
    o.updated_at = today();
    // 저장
    var ovs = loadOverrides();
    ovs[id] = { status: o.status, note: o.note, updated_at: o.updated_at };
    saveOverrides(ovs);
    return o;
  }

  // ==================== 대시보드 ====================
  function validContracts(dept) {
    return contracts.filter(function (c) {
      return c.status === '계약중' && (!dept || c.dept_name === dept);
    });
  }
  function expiringContracts(dept, days) {
    var t = today(), h = todayPlus(days);
    return validContracts(dept).filter(function (c) { return t <= c.end_date && c.end_date <= h; });
  }
  function overdueObligations(dept) {
    var t = today();
    return obligations.filter(function (o) {
      return o.kind === 'quant' && o.due_date && o.due_date < t &&
        o.status !== '완료' && (!dept || o.dept_name === dept);
    });
  }
  function urgentObligations(dept, days) {
    var h = todayPlus(days);
    return obligations.filter(function (o) {
      return o.kind === 'quant' && o.due_date && o.due_date <= h &&
        o.status !== '완료' && (!dept || o.dept_name === dept);
    });
  }

  function dashboardSummary(dept) {
    return {
      valid_contracts: validContracts(dept).length,
      expiring_contracts: expiringContracts(dept, 30).length,
      overdue_obligations: overdueObligations(dept).length
    };
  }
  function dashboardValidContracts(dept) {
    var r = validContracts(dept).slice().sort(byEndDate);
    return { count: r.length, results: r };
  }
  function dashboardExpiringContracts(dept, days) {
    var r = expiringContracts(dept, days).slice().sort(byEndDate);
    return { count: r.length, results: r };
  }
  function dashboardOverdueObligations(dept) {
    var r = overdueObligations(dept).slice().sort(byDueDate);
    return { count: r.length, results: r };
  }
  function dashboardUrgentObligations(dept, days) {
    var r = urgentObligations(dept, days).slice().sort(byDueDate);
    return { count: r.length, results: r };
  }

  function byEndDate(a, b) { return a.end_date < b.end_date ? -1 : (a.end_date > b.end_date ? 1 : 0); }
  function byDueDate(a, b) { return a.due_date < b.due_date ? -1 : (a.due_date > b.due_date ? 1 : 0); }

  window.MockAPI = {
    org: org,
    searchContracts: searchContracts,
    getContract: getContract,
    searchObligations: searchObligations,
    getObligation: getObligation,
    updateObligation: updateObligation,
    dashboardSummary: dashboardSummary,
    dashboardValidContracts: dashboardValidContracts,
    dashboardExpiringContracts: dashboardExpiringContracts,
    dashboardOverdueObligations: dashboardOverdueObligations,
    dashboardUrgentObligations: dashboardUrgentObligations,
    STATUS_OPTIONS: STATUS_OPTIONS,
    QUANT_CATEGORIES: ['지급', '추가 비용', '검수', '정보 제공', '안전관리', '비용 부담', '인력관리'],
    QUAL_CATEGORIES: ['기밀정보유지', '준법', '면책', '지적재산권', '양도제한', '해지', '통지', '손해배상']
  };
})();
