from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.encoders import jsonable_encoder
from decimal import Decimal
from app.database import get_conn, PostgreDB
from psycopg2.extras import RealDictCursor

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

#############################################################
#------------------------ 랜딩 페이지 ------------------------#
@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    corp_names = []
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT corp_name 
                      FROM dart_company_info 
                     ORDER BY corp_name
                     LIMIT 10
                """)
                corp_names = [row[0] for row in cur.fetchall()]

    except Exception as e:
        print(f"기업 리스트 조회 에러: {e}")

    return templates.TemplateResponse("home.html", {
        "request": request,
        "corp_names": corp_names
    })
#-----------------------------------------------------------#
#############################################################
#-------------------- 기업 검색 JSON API --------------------#
def to_float(val):
    return float(val) if isinstance(val, Decimal) else val

@app.get("/api/search-company")
def search_company_api(company: str = Query(...)):
    try:
        print("들어옴")

        with get_conn() as conn: 
            with conn.cursor(cursor_factory=RealDictCursor) as cur:  
                # 기업정보
                cur.execute("""
                    SELECT * FROM dart_company_info
                    WHERE corp_name = %s
                    LIMIT 1
                """, (company,))
                company_info = cur.fetchone()

                # 재무정보(기업코드로 조회)
                corp_code = company_info["corp_code"] if company_info else None

                # 재무제표(dart_report_ofs)
                finance_ofs = None
                if corp_code:
                    cur.execute("""
                        SELECT year, revenue, operating_profit AS op_profit, net_profit
                        FROM dart_report_ofs
                        WHERE corp_code = %s
                        ORDER BY year DESC
                    """, (corp_code,))
                    finance_ofs = cur.fetchall()

                # 연결재무제표(dart_report_cfs)
                finance_cfs = None
                if corp_code:
                    cur.execute("""
                        SELECT year, revenue, operating_profit AS op_profit, net_profit
                        FROM dart_report_cfs
                        WHERE corp_code = %s
                        ORDER BY year DESC
                    """, (corp_code,))
                    finance_cfs = cur.fetchall()

                # 엔터프라이즈정보
                # cur.execute("""
                #     SELECT welfare, company_basic_info, rating, company_info
                #     FROM enterprise_info
                #     WHERE company = %s
                #     LIMIT 1
                # """, (company,))
                # enterprise = cur.fetchone()

        enterprise = None
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
                    "star2": star2,
                    "finance_ofs": finance_ofs,
                    "finance_cfs": finance_cfs,
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
#############################################################
#------------------- 기업 검색 결과 페이지 --------------------#
@app.get("/search-company", response_class=HTMLResponse)
def search_company(request: Request):
    return templates.TemplateResponse("search_company.html", {"request": request})

#-----------------------------------------------------------#
#############################################################
#------------------- (확인용) 테이블 페이지 -------------------#
ALLOWED_TABLES = ["dart_company_info","dart_report_info","dart_report_text","dart_report_ofs","dart_report_cfs"]
@app.get("/select-table", response_class=HTMLResponse)
def select_and_view_table(request: Request, table_name: str = Query(None)):
    rows = []
    colnames = []
    
    if table_name:
        if table_name not in ALLOWED_TABLES:
            return HTMLResponse(
                content=f"<h1>허용되지 않은 테이블입니다: {table_name}</h1>", 
                status_code=400
            )
        
        try:
            with get_conn() as conn:
                with conn.cursor() as cur:
                    sql = f"SELECT * FROM {table_name} ORDER BY 1 DESC LIMIT 20;"
                    cur.execute(sql)
                    rows = cur.fetchall()
                    colnames = [desc[0] for desc in cur.description]
            
        except Exception as e:
            return HTMLResponse(content=f"<h1>에러 발생: {e}</h1>", status_code=500)
    
    return templates.TemplateResponse("select_table.html", {
        "request": request,
        "tables": ALLOWED_TABLES,
        "table_name": table_name,
        "columns": colnames,
        "rows": rows
    })