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
from typing import Dict, List, Tuple
import pandas as pd
import numpy as np
import json
from io import StringIO
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("DART_API_KEY")
dart = OpenDartReader(api_key)
base_dir = Path(__file__).resolve().parent

#--------------------------------------------------------#
##########################################################
def get_corp_code_mapping(corp_names):

    corp_name_list = []
    for corp_name in corp_names:
        try:
            corp_code = dart.find_corp_code(corp_name)
            info = dart.company(corp_code)

            if info is None:
                print(f"[WARN] 기업 정보 없음: {corp_name}")
                continue

            stock_name = info.get("stock_name")
            corp_name_official = info.get("corp_name")

            corp_name_list.append({
                "corp_code": corp_code,
                "corp_name": corp_name_official,
                "stock_name": stock_name
            })

        except Exception as e:
            print(f"[ERROR] 기업 조회 실패: {corp_name} → {e}")

    df_corp_mapping = pd.DataFrame(corp_name_list)
    return df_corp_mapping
#--------------------------------------------------------#
##########################################################
def parse_report_nm(report_nm: str):

    match = re.search(r'(.+?)\s*\((\d{4})\.(\d{2})\)', report_nm)
    if match:
        return match.group(1).strip(), int(match.group(2)), int(match.group(3))
    return None, None, None
#--------------------------------------------------------#
##########################################################
def get_report_text(html_path: str):

    with open(html_path, encoding="utf-8") as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, "html.parser")

    for tag in soup(['script', 'style']):
        tag.decompose()

    markdown_text = md(str(soup))
    clean_table = markdown_text
    clean_table = re.sub(r'\[.*?\]\(javascript:void\(0\);?\)', '', clean_table) 
    clean_table = re.sub(r'\|\s*\|\s*\n\|\s*---+\s*\|\s*\n?', '', clean_table)   
    clean_table = re.sub(r'\n{3,}', '\n\n', clean_table)                        
    clean_table = re.sub(r'^\|\s*\|\s*$', '', clean_table, flags=re.MULTILINE)
    md_table = clean_table.strip()
    jsonb_markdown = json.dumps({"markdown": md_table}, ensure_ascii=False)
    
    return jsonb_markdown
#--------------------------------------------------------#
##########################################################
def get_company_info(corp_code: str, start_year: str = "2022"):

    try:       
        #--------------------------------------------------------#
        # 1) 기업 코드 및 정보 조회
        # - 관련 테이블명: company_info     
        #--------------------------------------------------------#
        info = dart.company(corp_code)        
        company_info = {
            "corp_code": corp_code,
            "corp_name": info.get("stock_name"),
            "ceo_name": info.get("ceo_nm"),
            "corp_cls": info.get("corp_cls"),
            "adres": info.get("adres"),
            "hm_url": info.get("hm_url"),
            "ir_url": info.get("ir_url")
        }

        #--------------------------------------------------------#
        # 2) 공시 목록 조회
        # - 관련 테이블명: dart_report_info     
        #--------------------------------------------------------#
        df = dart.list(corp=corp_code, start=start_year, kind="A")
        if df.empty:
            return company_info, [], []
        
        df = df.sort_values(by="rcept_dt", ascending=False).reset_index(drop=True)

        report_list = []
        for _, row in df.iterrows():
            report_type, year, month = parse_report_nm(row['report_nm'])
            if report_type is None:
                continue

            report_list.append({
                "corp_code": corp_code,
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
        
        #--------------------------------------------------------#
        # 3) 가장 최근 공시의 rcept_no로 연구개발문서 다운로드
        # - 관련 테이블명: dart_report_text 
        #--------------------------------------------------------#
        latest_rcept_no = report_list[0]["rcept_no"]
        rd_text_list = []
        sub_df = dart.sub_docs(latest_rcept_no, match="연구개발").reset_index(drop=True)
        if not sub_df.empty:
            rd_url = sub_df['url'][0]
            print(f"[INFO] 연구개발문서 URL: {rd_url}")
            
            base_dir = Path(__file__).resolve().parent
            html_path = base_dir / 'data' / f"{corp_code}_{latest_rcept_no}.html"

            if not html_path.exists():
                dart.download(url=rd_url, fn=str(html_path))
                # print(f"[INFO] 다운로드 완료: {html_path}")
            
            # HTML → Markdown → JSON 변환
            jsonb_markdown = get_report_text(html_path)
            rd_text_list.append({
                "corp_code": corp_code,
                "rcept_no": latest_rcept_no,
                "parsed_url": rd_url,
                "parsed_table": jsonb_markdown
            })

        return company_info, report_list, rd_text_list
    
    except Exception as e:
        print(f"[ERROR] 기업({corp_code}) 수집 실패 → {e}")
        return {}, [], []
#--------------------------------------------------------#
##########################################################
def get_dart_report_fs(corp_code, year, fs_name, indicators):

    try:
        fs = dart.finstate(corp=corp_code, bsns_year=year, reprt_code="11011")
        
        if fs is None or fs.empty:
            print(f"[WARN] 재무제표 없음: {corp_code}({year})")
            return pd.DataFrame([
                [corp_code, year] + [0]*len(indicators),
                [corp_code, year-1] + [0]*len(indicators),
                [corp_code, year-2] + [0]*len(indicators),
            ], columns=['corp_code', 'year'] + indicators)
            
        fs = fs[fs['account_nm'].isin(indicators)]
        fs = fs[fs['fs_nm'] == fs_name]
        
        if fs.empty:
            print(f"[WARN] {fs_name} 없음: {corp_code}({year})")
            return pd.DataFrame([
                [corp_code, year] + [0]*len(indicators),
                [corp_code, year-1] + [0]*len(indicators),
                [corp_code, year-2] + [0]*len(indicators),
            ], columns=['corp_code', 'year'] + indicators)

        for col in ['thstrm_amount','frmtrm_amount','bfefrmtrm_amount']:
            fs[col] = (
                fs[col]
                .astype(str)          
                .str.replace(',', '')
                .replace('nan', np.nan)
            )
            fs[col] = pd.to_numeric(fs[col], errors='coerce').fillna(0)
        
        fs_data = []
        year_cols = [(year, 'thstrm_amount'), (year-1, 'frmtrm_amount'), (year-2, 'bfefrmtrm_amount')]
        
        for y, col in year_cols:
            row = [corp_code, y]
            for i in indicators:
                row_data = fs.loc[fs['account_nm'] == i, col]
                if not row_data.empty:
                    value = row_data.iloc[0]
                else:
                    value = 0
                row.append(value)
            fs_data.append(row)
            
        return pd.DataFrame(fs_data, columns = ['corp_code','year'] + indicators)
    
    except Exception as e:
        print(f"[ERROR] 재무정보없음: {corp_code}({year}) → {e}")
        return pd.DataFrame(columns=['corp_code', 'year'] + indicators)
#--------------------------------------------------------#
##########################################################