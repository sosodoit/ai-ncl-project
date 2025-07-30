"""
파일명: app/database.py
설명: PostgreSQL 데이터베이스와의 연결, 종료, 조회 및 적재 기능을 담당하는 클래스 기반 유틸리티 모듈입니다.
관련 모듈: scripts/load_companies.py, app/crawler/*
주의사항:
- .env 파일에 정의된 환경변수(DB 접속 정보)가 필요합니다.
- 데이터베이스 연결 객체는 재사용 가능한 방식으로 구성되어 있어야 합니다.
"""

import os
from typing import List, Generator, Any
from contextlib import contextmanager
from environment import env

import psycopg2
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import RealDictCursor

user = env.get("POSTGRE_USER")
pw = env.get("POSTGRE_PASSWORD")
db_host = env.get("POSTGRE_HOST")
db_port = env.get("POSTGRE_PORT")
db = env.get("POSTGRE_DB")

POSTGRE_URL=f"postgresql://{user}:{pw}@{db_host}:{db_port}/{db}"

# 1. 전역 커넥션 풀 (프로세스당 1개)
POOL = ThreadedConnectionPool(
    # 서비스에 따라서 min,max 변경가능
    minconn=5, # 커넥션 최소 5개 유지
    maxconn=30, # 동시에 30개까지 점유 허용
    dsn=POSTGRE_URL
)

# ───────────── 2. 컨텍스트 매니저 ─────────────
@contextmanager
def get_conn(cursor_dict: bool = False) -> Generator[psycopg2.extensions.connection, None, None]:
    """
    with get_conn() as conn:
        ...
    cursor_dict=True ➜ RealDictCursor 반환
    """
    conn = POOL.getconn()
    try:
        if cursor_dict:
            # 기본 커서 대신 딕트형 커서가 필요할 때
            conn.cursor_factory = RealDictCursor
        yield conn
    finally:
        POOL.putconn(conn)

# 3. 클래스 유틸 
class PostgreDB:
    """
    커넥션 풀 구조로 변경 (select 요청별로 connection,close시 
    max_connections 초과나 복잡도 문제로 변경)
    """
    # SELECT
    @staticmethod
    def _select(
        table_name: str,
        column: str,
        value: Any,
        order_by: str = "",
        dict_row: bool = False
    ):
        order_clause = f"ORDER BY {order_by} DESC" if order_by else ""
        sql = f"""
            SELECT * FROM {table_name}
             WHERE {column} = %s
             {order_clause}
             LIMIT 1
        """
        with get_conn(cursor_dict=dict_row) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (value,))
                return cur.fetchone()

    # db insert
    def _insert(self, table_name: str, columns: List[str], values: List) -> None:
        
        columns_str = ', '.join(columns)  # 컬럼 이름을 문자열로 연결
        placeholders = ', '.join(['%s'] * len(values))  # 값의 개수에 맞게 플레이스홀더 생성
        
        sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"

        try:
            self.cursor.execute(sql,values)
            self.connection.commit()
            print("db insert 성공")

        except Exception as error:
            print("db insert 중 에러 : ", error)
            self.connection.rollback()
            self._close()
