"""
파일명: app/crawler/dart_loader.py
설명: OpenDartReader 라이브러리를 사용하여 기업의 개황 정보를 수집하는 DART 크롤러 모듈입니다.
관련 모듈: -
주의사항: OpenDart API 키를 포함한 환경변수(.env)가 필요합니다.
"""

import OpenDartReader
import os
import re
from datetime import datetime, date
import time
from typing import List, Dict
import pandas as pd
from io import StringIO
from bs4 import BeautifulSoup
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("DART_API_KEY")
dart = OpenDartReader(api_key)
base_dir = Path(__file__).resolve().parent

##########################################################
#------------------- get_company_info -------------------#
def get_company_info(corp_name: str) -> dict:
    try:
        corp_code = dart.find_corp_code(corp_name)
        info = dart.company(corp_code)
        return {
            "corp_code": corp_code,
            "corp_name": info.get("corp_name"),
            "ceo_name": info.get("ceo_nm"),
            "corp_cls": info.get("corp_cls"),
            "adres": info.get("adres"),
            "hm_url": info.get("hm_url"),
            "ir_url": info.get("ir_url"),
            "modify_date": date.today()
        }
    except Exception as e:
        print(f"[ERROR] 기업 정보 조회 실패: {e}")
        return {}
#--------------------------------------------------------#

##########################################################
#-------------------- get_report_info -------------------#
def parse_report_nm(report_nm: str):
    """
    보고서명에서 유형, 연도, 월을 추출
    예: '사업보고서 (2023.12)' → ('사업보고서', 2023, 12)
    """
    match = re.search(r'(.+?)\s*\((\d{4})\.(\d{2})\)', report_nm)
    if match:
        return match.group(1).strip(), int(match.group(2)), int(match.group(3))
    return None, None, None

def get_report_info(company_info: dict) -> List[Dict]:
    """
    dart_report_info 적재를 위한 공시 목록 수집 및 정제
    이미 수집된 company_info(dict)를 기반으로 공시 목록 반환
    """

    try:
        df = dart.list(corp=company_info["corp_code"], start="2022", kind="A")
        if df.empty:
            return []

        result = []
        for _, row in df.iterrows():
            report_type, year, month = parse_report_nm(row['report_nm'])
            if report_type is None:
                continue

            result.append({
                "corp_code": company_info["corp_code"],
                "corp_name": company_info["corp_name"],
                "stock_code": row["stock_code"],
                "corp_cls": company_info["corp_cls"],
                "report_type": report_type,
                "report_year": year,
                "report_month": month,
                "report_nm": row["report_nm"],
                "rcept_no": row["rcept_no"],
                "flr_nm": row["flr_nm"],
                "rcept_dt": datetime.strptime(str(row["rcept_dt"]), "%Y%m%d").date()
            })
        return result
    except Exception as e:
        print(f"[ERROR] 공시 목록 수집 실패: {company_info['corp_name']} → {e}")
        return []
#--------------------------------------------------------#

##########################################################
#-------------------- get_report_text -------------------#
def normalize_rd_table(table: list[dict]) -> list[dict]:

    if not table or not isinstance(table, list):
        return []

    # 컬럼 헤더 추출
    header = table[0]
    if not isinstance(header, dict):
        return []

    column_map = {
        "연구과제": "project_name",
        "연구결과 및 기대효과": "expected_result",
        "연구마감년도": "end_year"
    }

    header_map = {
        idx: column_map.get(header[idx].strip(), f"col_{idx}")
        for idx in header if isinstance(header[idx], str)
    }

    normalized = []
    for row in table[1:]:
        normalized.append({
            header_map.get(k, f"col_{k}"): v for k, v in row.items()
        })

    return normalized

def parser_rd_table(save_path) -> list:

    try:     
        # HTML 파싱
        with open(save_path, encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
        
        # 정규표현식 기반 키워드 탐색 패턴 (대소문자 무시, 공백 포함 대응)
        keyword_pattern = re.compile(r"연구\s*개발.*실적", re.IGNORECASE)

        # <p>, <td>, <th> 중에서 텍스트가 유사 키워드와 일치하는 태그 탐색
        target_tag = soup.find(
            lambda tag: tag.name in ['p', 'td', 'th'] and tag.get_text(strip=True) and keyword_pattern.search(tag.get_text())
        )

        if not target_tag:
            print("[WARN] '연구개발 실적' 문구를 찾지 못했습니다.")
            return []

        # 이후에 나오는 <table>을 탐색
        next_table = target_tag.find_next('table')
        if not next_table:
            print("[WARN] '연구개발 실적' 이후 테이블을 찾지 못했습니다.")
            return []

        # HTML → DataFrame → JSON 변환
        df_list = pd.read_html(StringIO(str(next_table)))
        raw_table = df_list[0].dropna(how='all').to_dict(orient="records")

        return normalize_rd_table(raw_table)

    except Exception as e:
        print(f"[ERROR] 연구개발 실적 테이블 추출 실패: {e}")
        return []

def get_report_text(report_info: List[dict]) -> List[dict]:
    """
    get_report_text 적재를 위한 공시 원문 수집 및 정제
    report_info(dict)를 기반으로 공시 목록 반환
    """
    
    results = []
    for report in report_info:
        corp_code = report.get("corp_code")
        rcept_no = report.get("rcept_no")
        try:
            sub_df = dart.sub_docs(rcept_no, match="연구개발").reset_index(drop=True)
            if sub_df.empty:
                continue

            rd_url = sub_df['url'][0]
            html_path = base_dir / "data" / f"{corp_code}_{rcept_no}.html"
            if not html_path.exists():
                dart.download(url=rd_url, fn=str(html_path))

            parsed_table = parser_rd_table(str(html_path))
            if parsed_table:
                results.append({
                    "corp_code": corp_code,
                    "rcept_no": rcept_no,
                    "parsed_url": rd_url,
                    "parsed_table": parsed_table
                })

        except Exception as e:
            print(f"[ERROR] rcept_no {rcept_no} → {e}")
            continue

    return results
#--------------------------------------------------------#

##########################################################
#--------------------- get_report_fs --------------------#
def extract_end_date(raw: str) -> str:
    if pd.isna(raw):
        return ""
    # 문자열이 "~" 포함된 경우 → 종료일만 추출
    if "~" in raw:
        raw = raw.split("~")[-1].strip()
    # " 현재" 제거 + "." → "-" 변환
    raw = raw.replace(" 현재", "").replace(".", "-").strip()
    return raw

def get_dart_report_fs(report_info: dict):
    """
    report_info(dict)를 기반으로 사업보고서에 해당하는 연간 재무제표 수집
    """
    corp_code = report_info["corp_code"]
    report_year = report_info["report_year"]

    result = []
    try:
        fs = dart.finstate(corp=corp_code, bsns_year=report_year, reprt_code="11011")
        
        if fs is None or fs.empty:
            print(f"[SKIP] {report_info['corp_name']} - {report_year} → 재무제표 없음")
        else:
            df = fs[[
                    'rcept_no', 'reprt_code', 'bsns_year', 'corp_code', 'stock_code',
                    'fs_div', 'fs_nm', 'sj_div', 'sj_nm', 'account_nm',
                    'thstrm_nm', 'thstrm_dt', 'thstrm_amount',
                    'frmtrm_nm', 'frmtrm_dt', 'frmtrm_amount',
                    'bfefrmtrm_nm', 'bfefrmtrm_dt', 'bfefrmtrm_amount',
                    'ord', 'currency'
                ]].copy()
            
            # 금액 처리
            for col in ['thstrm_amount', 'frmtrm_amount', 'bfefrmtrm_amount']:
                df[col] = (
                    df[col].astype(str)
                    .str.replace(",", "", regex=False)
                    .str.strip()
                    .replace('-', '0')
                    .fillna("0")
                    .astype("int64")
                )

            # 날짜 처리
            for col in ['thstrm_dt', 'frmtrm_dt', 'bfefrmtrm_dt']:
                df[col] = df[col].astype(str).map(extract_end_date)

            # 문자열형 지정
            for col in ['rcept_no', 'reprt_code', 'bsns_year', 'corp_code', 'stock_code',
                        'fs_div', 'fs_nm', 'sj_div', 'sj_nm', 'account_nm',
                        'thstrm_nm', 'frmtrm_nm', 'bfefrmtrm_nm', 'ord', 'currency']:
                df[col] = df[col].astype(str)
            
            result.extend(df.to_dict(orient='records'))

        time.sleep(0.2)
        return result

    except Exception as e:
        print(f"[ERROR] 재무제표 수집 실패: {report_info['corp_name']} → {e}")
#--------------------------------------------------------#