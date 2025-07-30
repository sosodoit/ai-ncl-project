from app.crawler.dart_loader import get_company_info
from app.database import PostgreDB

db = PostgreDB()
db._connection()

corp_names = ['00266961', '00258801', '01547845', '01717824', '00126186', '00139834']

for name in corp_names:

    company_info, report_list, rd_text_list = get_company_info(name, start_year="2022")
    
    if company_info:
        db._insert("company_info", 
                   list(company_info.keys()), 
                   list(company_info.values()),
                   conflict_key="corp_code")
        print(f"[INFO] company_info 적재: {company_info['corp_name']}")   
    else:
        print(f"[SKIP] 기업 정보 없음: {name}")

    if report_list:
        for report in report_list:
            db._insert("dart_report_info", 
                       list(report.keys()), 
                       list(report.values()),
                       conflict_key="corp_code, rcept_no")
        print(f"[INFO] dart_report_info 적재: {company_info['corp_name']}")
    else:
        print(f"[SKIP] 공시 정보 없음: {name}")

    if rd_text_list:
        for rd_text in rd_text_list:         
            db._insert("dart_report_text",
                        list(rd_text.keys()), 
                        list(rd_text.values()),
                        conflict_key="corp_code, rcept_no") 
            print(f"[INFO] get_report_text 적재: {rd_text['rcept_no']}")
    else:
        print(f"[SKIP] 연구 정보 없음: {name}")

db._close()
