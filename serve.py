import os
from waitress import serve
from app import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    print(f'계약서 관리 앱(운영) 실행 중: http://0.0.0.0:{port}')
    serve(app, host='0.0.0.0', port=port)
