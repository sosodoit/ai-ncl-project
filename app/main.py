"""
파일명: app/main.py
설명: FastAPI 애플리케이션의 진입점으로, 라우터 등록 및 서버 실행 설정을 담당합니다.
관련 모듈: app/crawler, app/database.py, app/templates
주의사항:
- 실행 전 .env 파일 설정이 완료되어 있어야 합니다.
- uvicorn 또는 docker-compose를 통해 실행할 수 있습니다.
"""

from typing import Union
from pydantic import BaseModel
from fastapi import FastAPI, Request, Query, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.database import PostgreDB

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static", html=True), name="static")

#############################################################
#------------------------ 랜딩 페이지 ------------------------#
@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    corp_names = []
    try:
        db = PostgreDB()
        db._connection()
        db.cursor.execute("SELECT corp_name FROM company_info ORDER BY corp_name LIMIT 10;")  # 필요 시 LIMIT 조절
        corp_names = [row[0] for row in db.cursor.fetchall()]
        db._close()
    except Exception as e:
        print(f"기업 리스트 조회 에러: {e}")

    return templates.TemplateResponse("home.html", {
        "request": request,
        "corp_names": corp_names
    })
#-----------------------------------------------------------#

#############################################################
#------------------- 기업 검색 결과 페이지 --------------------#
@app.get("/search-company", response_class=HTMLResponse)
def search_company(request: Request, corp_name: str = None):
    
    result = None

    if corp_name:
        try:
            db = PostgreDB()
            db._connection()
            result = db._select(
                table_name="company_info",
                column="corp_name",
                value=corp_name,
                time_key="ORDER BY modify_date"
            )
            db._close()
        except Exception as e:
            return HTMLResponse(content=f"<h1>에러 발생: {e}</h1>", status_code=500)

    return templates.TemplateResponse("search_company.html", {
        "request": request,
        "corp_name": corp_name,
        "result": result
    })
#-----------------------------------------------------------#

#############################################################
#------------------- (확인용) 테이블 페이지 -------------------#
ALLOWED_TABLES = ["company_info","dart_report_info","dart_report_text","dart_report_fs"] # 허용된 생성된 테이블 목록만 지정
@app.get("/select-table", response_class=HTMLResponse)
def select_and_view_table(request: Request, table_name: str = Query(None)):
    
    rows = []
    colnames = []

    if table_name:
        if table_name not in ALLOWED_TABLES:
            return HTMLResponse(content=f"<h1>허용되지 않은 테이블입니다: {table_name}</h1>", status_code=400)

        try:
            db = PostgreDB()
            db._connection()

            sql = f"SELECT * FROM {table_name} ORDER BY 1 DESC LIMIT 10;"
            db.cursor.execute(sql)
            rows = db.cursor.fetchall()
            colnames = [desc[0] for desc in db.cursor.description]

            db._close()

        except Exception as e:
            return HTMLResponse(content=f"<h1>에러 발생: {e}</h1>", status_code=500)

    return templates.TemplateResponse("select_table.html", {
        "request": request,
        "tables": ALLOWED_TABLES,
        "table_name": table_name,
        "columns": colnames,
        "rows": rows
    })
#-----------------------------------------------------------#