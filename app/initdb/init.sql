-- 파일명: app/initdb/init.sql
-- 관련 모듈: app/database.py, scripts/load_companies.py
-- 주의사항: 해당 스키마는 PostgreSQL 기준이며, 초기 DB 설정 시 실행됩니다.

-- 설명: 기업의 기본 정보를 저장하는 dart_company_info 테이블을 생성합니다.
CREATE TABLE dart_company_info (
    corp_code TEXT PRIMARY KEY,
    corp_name TEXT,
    ceo_name TEXT,
    corp_cls TEXT,
    adres TEXT,
    hm_url TEXT,
    ir_url TEXT
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
    parsed_url TEXT,        
    parsed_table JSONB,        
    PRIMARY KEY (corp_code, rcept_no)
);

-- 설명: 기업의 재무제표를 저장하는 dart_report_fs 테이블을 생성합니다.
CREATE TABLE dart_report_ofs (
    corp_code TEXT NOT NULL,
    corp_name TEXT NOT NULL,
    year INT NOT NULL,
    revenue BIGINT DEFAULT 0,           -- 매출액
    operating_profit BIGINT DEFAULT 0,  -- 영업이익
    net_profit BIGINT DEFAULT 0,        -- 당기순이익
    PRIMARY KEY (corp_code, year)
);

CREATE TABLE dart_report_cfs (
    corp_code TEXT NOT NULL,
    corp_name TEXT NOT NULL,
    year INT NOT NULL,
    revenue BIGINT DEFAULT 0,           -- 매출액
    operating_profit BIGINT DEFAULT 0,  -- 영업이익
    net_profit BIGINT DEFAULT 0,        -- 당기순이익
    PRIMARY KEY (corp_code, year)
);

CREATE TABLE dart_corp_map (
    corp_code TEXT PRIMARY KEY,
    corp_name TEXT,
    stock_name TEXT
);