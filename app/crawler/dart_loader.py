"""
파일명: app/crawler/dart_loader.py
설명: OpenDartReader 라이브러리를 사용하여 기업의 개황 정보를 수집하는 DART 크롤러 모듈입니다.
관련 모듈: -
주의사항: OpenDart API 키를 포함한 환경변수(.env)가 필요합니다.
"""

import OpenDartReader
import os
from datetime import date
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("DART_API_KEY")
dart = OpenDartReader(api_key)

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
        print(f"기업 정보 조회 실패: {e}")
        return {}
