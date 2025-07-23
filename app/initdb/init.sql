-- 파일명: app/initdb/init.sql
-- 관련 모듈: app/database.py, scripts/load_companies.py
-- 주의사항: 해당 스키마는 PostgreSQL 기준이며, 초기 DB 설정 시 실행됩니다.

-- 설명: 기업의 기본 정보를 저장하는 company_info 테이블을 생성합니다.
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

-- 설명: 기업의 공시 목록을 저장하는 dart_report_info 테이블을 생성합니다.
CREATE TABLE dart_report_info (
    corp_code TEXT NOT NULL,
    corp_name TEXT,
    stock_code TEXT,
    corp_cls TEXT,
    report_type TEXT,       
    report_year INTEGER,
    report_month INTEGER,
    report_nm TEXT,
    rcept_no TEXT NOT NULL,
    flr_nm TEXT,
    rcept_dt DATE,
    PRIMARY KEY (corp_code, rcept_no)
);

-- 설명: 기업의 공시 원문을 저장하는 dart_report_text 테이블을 생성합니다.
CREATE TABLE dart_report_text (
    corp_code TEXT NOT NULL,
    rcept_no TEXT NOT NULL,
    parsed_url TEXT,            -- 연구개발 섹션 URL
    parsed_table JSONB,         -- 연구개발 실적 테이블
    PRIMARY KEY (corp_code, rcept_no)
);

-- 설명: 기업의 재무제표를 저장하는 dart_report_fs 테이블을 생성합니다.
CREATE TABLE dart_report_fs (
    rcept_no TEXT,
    reprt_code TEXT,
    bsns_year TEXT,
    corp_code TEXT,
    stock_code TEXT,
    fs_div TEXT,
    fs_nm TEXT,
    sj_div TEXT,
    sj_nm TEXT,
    account_nm TEXT,
    thstrm_nm TEXT,
    thstrm_dt DATE,
    thstrm_amount BIGINT,
    frmtrm_nm TEXT,
    frmtrm_dt DATE,
    frmtrm_amount BIGINT,
    bfefrmtrm_nm TEXT,
    bfefrmtrm_dt DATE,
    bfefrmtrm_amount BIGINT,
    ord TEXT,
    currency TEXT,
    PRIMARY KEY (corp_code, rcept_no)
);
