#!/usr/bin/env python3
"""data/*.json 을 읽어 목업용 mockup/data.js 를 생성한다.

정적 목업은 서버가 없어 fetch()로 JSON을 불러올 수 없으므로(브라우저의 file://
보안 제약), 원본 JSON 데이터를 하나의 JS 파일(window.APP_DATA)로 임베드한다.

사용법:
    python tools/build_data.py
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, 'data')
OUT = os.path.join(ROOT, 'mockup', 'data.js')


def load(name, key):
    with open(os.path.join(DATA_DIR, name), 'r', encoding='utf-8') as f:
        return json.load(f)[key]


def main():
    contracts = load('contracts.json', 'contracts')
    obligations = load('obligations.json', 'obligations')
    departments = load('org.json', 'departments')

    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('// 계약서 관리 목업 - 임베드 데이터\n')
        f.write('// 서버 없이 브라우저에서 직접 열 수 있도록 원본 JSON을 이 파일에 담았습니다.\n')
        f.write('// 원본: data/contracts.json, data/obligations.json, data/org.json\n')
        f.write('// 이 파일은 tools/build_data.py 로 생성됩니다. 직접 수정하지 마세요.\n')
        f.write('window.APP_DATA = {\n')
        f.write('  contracts: ' + json.dumps(contracts, ensure_ascii=False) + ',\n')
        f.write('  obligations: ' + json.dumps(obligations, ensure_ascii=False) + ',\n')
        f.write('  departments: ' + json.dumps(departments, ensure_ascii=False) + '\n')
        f.write('};\n')

    print(f'생성 완료: {OUT}')
    print(f'  계약 {len(contracts)}건 · 의무조항 {len(obligations)}건 · 본부 {len(departments)}개')


if __name__ == '__main__':
    main()
