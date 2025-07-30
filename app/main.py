from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from decimal import Decimal
from fastapi.encoders import jsonable_encoder
from psycopg2.extras import RealDictCursor

from database import get_conn

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# ------------------- 랜딩 ------------------- 
@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


def to_float(val):
    return float(val) if isinstance(val, Decimal) else val

@app.get("/api/search-company")
def search_company_api(company: str = Query(...)):
    try:
        print("들어옴")

        with get_conn() as conn: 
            with conn.cursor(cursor_factory=RealDictCursor) as cur:  
                cur.execute("""
                    SELECT * FROM company_info
                    WHERE corp_name = %s
                    ORDER BY modify_date DESC
                    LIMIT 1
                """, (company,))
                company_info = cur.fetchone()

                cur.execute("""
                    SELECT welfare, company_basic_info, rating, company_info
                    FROM enterprise_info
                    WHERE company = %s
                    LIMIT 1
                """, (company,))
                enterprise = cur.fetchone()

        star1 = star2 = 0.0
        if enterprise and enterprise["rating"]:
            r = [to_float(x) for x in enterprise["rating"]]
            if len(r) >= 2:
                star1, star2 = r[:2]
        print("company_info",company_info,"enterprise",enterprise)
        return JSONResponse(
            jsonable_encoder({
                "success": True,
                "data": {
                    "corp_name": company,
                    "company_info": company_info,
                    "enterprise_info": enterprise,
                    "star1": star1,
                    "star2": star2
                }
            })
        )

    except Exception as e:
        import traceback, sys
        traceback.print_exc(file=sys.stderr)
        return JSONResponse(
            {"success": False, "error": str(e)},
            status_code=500
        )

# ------------------- HTML 페이지 ------------------- 
@app.get("/search-company", response_class=HTMLResponse)
def search_company_page(request: Request):
    """기업 검색 페이지 (JavaScript로 동적 구성)"""
    return templates.TemplateResponse("search_company.html", {"request": request})

# ------------------- 테이블 조회용 ------------------- 
ALLOWED_TABLES = ["company_info"]

@app.get("/select-table", response_class=HTMLResponse)
def select_and_view_table(request: Request, table_name: str = Query(None)):
    rows = []
    colnames = []
    
    if table_name:
        if table_name not in ALLOWED_TABLES:
            return HTMLResponse(content=f"<h1>허용되지 않은 테이블입니다: {table_name}</h1>", status_code=400)
        
        try:
            from database import PostgreDB
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