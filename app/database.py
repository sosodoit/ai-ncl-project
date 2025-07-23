"""
파일명: app/database.py
설명: PostgreSQL 데이터베이스와의 연결, 종료, 조회 및 적재 기능을 담당하는 클래스 기반 유틸리티 모듈입니다.
관련 모듈: scripts/load_companies.py, app/crawler/*
주의사항:
- .env 파일에 정의된 환경변수(DB 접속 정보)가 필요합니다.
- 데이터베이스 연결 객체는 재사용 가능한 방식으로 구성되어 있어야 합니다.
"""

import psycopg2
from typing import List
import os
from dotenv import load_dotenv
load_dotenv()

user = os.getenv("POSTGRE_USER")
pw = os.getenv("POSTGRE_PASSWORD")
db_host = os.getenv("POSTGRE_HOST")
db_port = os.getenv("POSTGRE_PORT")
db = os.getenv("POSTGRE_DB")

POSTGRE_URL=f"postgresql://{user}:{pw}@{db_host}:{db_port}/{db}"

class PostgreDB:

    def __init__(self):
        self.db_url = POSTGRE_URL
        self.connection = None
        self.cursor = None

    # db 연결
    def _connection(self):
        try:
            self.connection = psycopg2.connect(self.db_url)
            self.cursor = self.connection.cursor()
            print("db연결 성공")
        except Exception as error:
            print("db연결 중 에러 발생 :", error)
            self.connection = None

    # db 연결 종료
    def _close(self):
        self.connection.close()
        self.cursor.close()
        print("db 연결종료")

    # db select
    def _select(self, table_name,column,value,time_key) :
        sql = f"SELECT * FROM {table_name} WHERE {column} = %s {time_key} DESC LIMIT 1"

        try:
            self.cursor.execute(sql, (value ,))
            return self.cursor.fetchone()

        except Exception as error:
            print("db select 중 에러 : ", error)
            self.connection.rollback()
            self._close()

    # db insert
    def _insert(self, table_name: str, columns: List[str], values: List, conflict_key: str = None) -> None:
        
        columns_str = ', '.join(columns)  # 컬럼 이름을 문자열로 연결
        placeholders = ', '.join(['%s'] * len(values))  # 값의 개수에 맞게 플레이스홀더 생성
        
        sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"

        if conflict_key:
            sql += f" ON CONFLICT ({conflict_key}) DO NOTHING"

        try:
            self.cursor.execute(sql,values)
            self.connection.commit()
            print("db insert 성공")

        except Exception as error:
            print("db insert 중 에러 : ", error)
            self.connection.rollback()
            self._close()
