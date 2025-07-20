"""
파일명: scripts/load_companies.py
설명: 외부에서 수집한 기업 개황 정보를 PostgreSQL 데이터베이스에 적재하는 스크립트입니다. 
- DB명: corpdata
- 테이블명: company_info
관련 모듈: database.py, app/crawler/dart_loader.py, initdb/init.sql
주의사항:
- DB 연결 정보는 .env 파일을 통해 설정되어야 합니다.
- 데이터를 적재하기 전에 company_info 테이블이 초기화되어 있어야 합니다.
- 크롤링된 데이터를 직접 사용하는 경우, 데이터 구조에 주의해야 합니다.
- 도커에서 적재 실행문: docker exec -it fastapi-server python scripts/load_companies.py
"""

import sys
from app.crawler.dart_loader import get_company_info
from app.database import PostgreDB

db = PostgreDB()
db._connection()

corp_names = ['NAVER', '카카오', '당근마켓', '당근페이', '삼성에스디에스', 'LG씨엔에스']

for name in corp_names:
    info = get_company_info(name)
    if info:
        print(f"적재: {info['corp_name']}")
        db._insert(
            table_name="company_info",
            columns=list(info.keys()),
            values=list(info.values())
        )

db._close()
