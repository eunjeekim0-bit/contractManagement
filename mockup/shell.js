// 사이드바 접기/펼치기 (원본 base.html에서 이관)
document.addEventListener('DOMContentLoaded', function () {
  var btn = document.getElementById('sidebarToggleBtn');
  if (!btn) return;
  btn.addEventListener('click', function () {
    var collapsed = document.documentElement.classList.toggle('sidebar-collapsed');
    try { localStorage.setItem('sidebarCollapsed', collapsed ? '1' : '0'); } catch (e) {}
  });
});
