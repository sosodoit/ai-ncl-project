-- 파일명: app/initdb/init.sql
-- 설명: 기업의 기본 정보를 저장하는 company_info 테이블을 생성합니다.
-- 관련 모듈: app/database.py, scripts/load_companies.py
-- 주의사항: 해당 스키마는 PostgreSQL 기준이며, 초기 DB 설정 시 실행됩니다.

CREATE TABLE company_info (
    corp_code TEXT PRIMARY KEY,
    corp_name TEXT,
    ceo_name TEXT,
    corp_cls TEXT,
    adres TEXT,
    hm_url TEXT,
    ir_url TEXT,
    modify_date DATE
);
