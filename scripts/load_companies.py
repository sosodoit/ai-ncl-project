"""
파일명: scripts/load_companies.py
설명: 외부에서 수집한 기업 및 공시 정보를 PostgreSQL에 적재
- DB명: corpdata
- 테이블명: company_info, dart_report_info
관련 모듈: database.py, app/crawler/dart_loader.py, initdb/init.sql
주의사항:
- DB 연결 정보는 .env 파일을 통해 설정되어야 합니다.
- 데이터를 적재하기 전에 company_info 테이블이 초기화되어 있어야 합니다.
- 크롤링된 데이터를 직접 사용하는 경우, 데이터 구조에 주의해야 합니다.
- 도커에서 적재 실행문: docker exec -it fastapi-server python scripts/load_companies.py
"""

import sys
from app.crawler.dart_loader import get_company_info, get_report_info, get_report_text, get_dart_report_fs
from app.database import PostgreDB
import json

db = PostgreDB()
db._connection()

corp_names = ['NAVER', '카카오', '당근마켓', '당근페이', '삼성에스디에스', 'LG씨엔에스']

for name in corp_names:
    # 기업 기본 정보 수집 + 적재
    company_info = get_company_info(name)
    if not company_info:
        print(f"[SKIP] 기업 정보 없음: {name}")
    else:     
        db._insert("company_info",
                list(company_info.keys()),
                list(company_info.values()),
                conflict_key="corp_code")
        print(f"[INFO] company_info 적재: {company_info['corp_name']}")   

    # 기업 공시 목록 수집 및 적재
    report_info = get_report_info(company_info)
    if not report_info:
        print(f"[INFO] 공시 목록 없음: {company_info['corp_name']}")
    else:
        for report in report_info:
            try:
                db._insert("dart_report_info", 
                        list(report.keys()), 
                        list(report.values()),
                        conflict_key="corp_code, rcept_no")
                print(f"[INFO] dart_report_info 적재: {company_info['corp_name']}")

            except Exception as e:
                print(f"[DUPLICATE/ERROR] rcept_no {report['rcept_no']} → {e}")

    # 기업 공시 원문(연구개발 실적) 수집 및 적재
    rd_texts = get_report_text(report_info)
    if not rd_texts:
        print(f"[INFO] 연구 개발 목록 없음: {company_info['corp_name']}")
    else:
        for rd in rd_texts:
            try:           
                rd["parsed_table"] = json.dumps(rd["parsed_table"], ensure_ascii=False) 
                db._insert("dart_report_text",
                            list(rd.keys()), 
                            list(rd.values()),
                            conflict_key="corp_code, rcept_no") 
                print(f"[INFO] get_report_text 적재: {rd['rcept_no']}")

            except Exception as e:
                print(f"[DUPLICATE/ERROR] 연구개발 rcept_no {rd['rcept_no']} → {e}")
    
    # 기업 공시 (연간)재무제표 수집 및 적재
    for report in report_info:
        if report['report_type'] == '사업보고서':
            print(name, report['report_type'], report['report_year'])
            fs_table = get_dart_report_fs(report)

            if not fs_table:
                continue

            for fs in fs_table:
                db._insert("dart_report_fs",
                            list(fs.keys()),
                            list(fs.values()),
                            conflict_key="corp_code, rcept_no")
                print(f"[INFO] dart_report_fs 적재: {fs['rcept_no']}")

db._close()
