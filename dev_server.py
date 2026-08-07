#!/usr/bin/env python3
"""로컬 편집용 라이브 프리뷰 개발 서버 (추가 설치 불필요, 표준 라이브러리만 사용).

기능:
  - mockup/ 폴더를 http://localhost:5500 로 서빙
  - 파일을 저장하면 브라우저가 자동으로 새로고침 (라이브 리로드)
  - data/*.json 을 수정하면 mockup/data.js 를 자동 재생성

사용법:
    python dev_server.py
    (Windows 는 serve.bat, macOS/Linux 는 ./serve.sh 를 실행해도 됩니다)
"""
import http.server
import json
import os
import socketserver
import subprocess
import sys
import threading
import time
import webbrowser
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.abspath(__file__))
MOCKUP_DIR = os.path.join(ROOT, 'mockup')
DATA_DIR = os.path.join(ROOT, 'data')
BUILD_SCRIPT = os.path.join(ROOT, 'tools', 'build_data.py')
PORT = int(os.environ.get('PORT', '5500'))

# 파일이 바뀔 때마다 증가하는 버전. 브라우저가 이 값을 폴링해 변하면 새로고침한다.
VERSION = 0

# 서빙되는 HTML 에 삽입되는 라이브 리로드 스크립트
LIVERELOAD_SNIPPET = """
<script>
/* dev_server.py 라이브 리로드 - 파일 저장 시 자동 새로고침 */
(function () {
  var known = null;
  function poll() {
    fetch('/__livereload', { cache: 'no-store' })
      .then(function (r) { return r.json(); })
      .then(function (d) {
        if (known === null) { known = d.v; }
        else if (d.v !== known) { location.reload(); return; }
        setTimeout(poll, 800);
      })
      .catch(function () { setTimeout(poll, 1500); });
  }
  poll();
})();
</script>
""".encode('utf-8')


def file_signature(paths):
    """주어진 파일들의 (경로, mtime, size) 시그니처 튜플을 만든다."""
    sig = []
    for p in paths:
        try:
            st = os.stat(p)
            sig.append((p, st.st_mtime, st.st_size))
        except OSError:
            pass
    return tuple(sig)


def list_files(base):
    out = []
    for root, _dirs, files in os.walk(base):
        for name in files:
            out.append(os.path.join(root, name))
    return out


def data_json_files():
    if not os.path.isdir(DATA_DIR):
        return []
    return [os.path.join(DATA_DIR, n) for n in os.listdir(DATA_DIR) if n.endswith('.json')]


def rebuild_data():
    """data/*.json → mockup/data.js 재생성."""
    if not os.path.exists(BUILD_SCRIPT):
        return
    try:
        subprocess.run([sys.executable, BUILD_SCRIPT], check=True,
                       capture_output=True, text=True)
        print('  ↻ data/*.json 변경 감지 → mockup/data.js 재생성 완료')
    except subprocess.CalledProcessError as e:
        print('  ✗ data.js 재생성 실패:\n', e.stderr)


def watcher():
    """백그라운드로 파일 변경을 감시하며 VERSION 을 증가시킨다."""
    global VERSION
    last_data = file_signature(data_json_files())
    last_mockup = file_signature(list_files(MOCKUP_DIR))
    while True:
        time.sleep(0.7)
        # 1) 원본 데이터가 바뀌면 data.js 재생성
        cur_data = file_signature(data_json_files())
        if cur_data != last_data:
            last_data = cur_data
            rebuild_data()
        # 2) mockup 폴더 내 변화가 있으면 버전 증가 → 브라우저 새로고침
        cur_mockup = file_signature(list_files(MOCKUP_DIR))
        if cur_mockup != last_mockup:
            last_mockup = cur_mockup
            VERSION += 1
            print('  → 변경 감지, 브라우저 새로고침 (v%d)' % VERSION)


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=MOCKUP_DIR, **kwargs)

    def log_message(self, fmt, *args):
        pass  # 요청 로그는 생략(조용하게)

    def _send_bytes(self, body, content_type):
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        route = urlparse(self.path).path

        # 라이브 리로드 폴링 엔드포인트
        if route == '/__livereload':
            self._send_bytes(json.dumps({'v': VERSION}).encode('utf-8'),
                             'application/json')
            return

        # 디렉터리 요청이면 index.html 로
        target = route
        if target.endswith('/'):
            target = target + 'index.html'

        # HTML 은 라이브 리로드 스크립트를 삽입해서 서빙
        if target.endswith('.html'):
            fs_path = self.translate_path(target)
            if os.path.isfile(fs_path):
                with open(fs_path, 'rb') as f:
                    body = f.read()
                if b'</body>' in body:
                    body = body.replace(b'</body>', LIVERELOAD_SNIPPET + b'</body>', 1)
                else:
                    body = body + LIVERELOAD_SNIPPET
                self._send_bytes(body, 'text/html; charset=utf-8')
                return

        # 그 외(css/js/폰트 등)는 기본 정적 서빙
        super().do_GET()


class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True


def main():
    if not os.path.isdir(MOCKUP_DIR):
        print('오류: mockup 폴더를 찾을 수 없습니다:', MOCKUP_DIR)
        sys.exit(1)

    threading.Thread(target=watcher, daemon=True).start()

    url = 'http://localhost:%d/' % PORT
    print('=' * 56)
    print(' 계약서 관리 목업 - 라이브 프리뷰 개발 서버')
    print('=' * 56)
    print(' 주소:   %s' % url)
    print(' 편집:   mockup/ 안의 .html/.css/.js 를 수정 후 저장하면')
    print('         브라우저가 자동으로 새로고침됩니다.')
    print(' 데이터: data/*.json 수정 시 data.js 자동 재생성')
    print(' 종료:   Ctrl + C')
    print('=' * 56)

    if os.environ.get('NO_BROWSER') != '1':
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()

    try:
        with ThreadingHTTPServer(('0.0.0.0', PORT), Handler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print('\n서버를 종료합니다.')


if __name__ == '__main__':
    main()
