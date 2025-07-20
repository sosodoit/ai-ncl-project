# ai-ncl-project (가칭)

FastAPI와 PostgreSQL 기반으로 동작하는 기업 정보 제공 API 백엔드입니다.  
OpenDART에서 기업 개황 정보를 수집하고, 데이터베이스에 저장한 뒤 API를 통해 제공합니다.

---

## 🗂️ 프로젝트 디렉토리 구조
```
├── app/
│   ├── crawler/             # DART 크롤링 모듈
│   ├── initdb/              # DB 초기화 SQL
│   ├── templates/           # Jinja2 템플릿
├── scripts/                 # 보조 스크립트 (데이터 적재 등)
├── main.py                  # FastAPI 진입점
├── database.py              # DB 연결 유틸리티
├── Dockerfile               # 백엔드 Docker 이미지 정의
├── docker-compose.yml       # 전체 서비스 구성 (FastAPI + PostgreSQL)
├── .env                     # 환경변수 정의
├── requirements.txt         # 의존성 라이브러리
```

## ⌛ 실행 방법

### 1. 이 저장소 클론하기 (혹은 다운로드)
```
git clone https://github.com/your-username/ai-ncl-project.git
cd ai-ncl-project
```

### 2. 환경 변수 설정
.env 파일에서 PostgreSQL 접속 정보 등을 필요에 맞게 수정

### 3. Docker로 실행 (FastAPI + PostgreSQL)
```
docker-compose up --build
```

## ⚙️ DB 관련 작업
company_info 테이블 기준 설명

#### 1) DB 생성
```
corpdata
```

#### 2) 테이블 생성
```
initdb/init.sql : company_info 테이블 생성 스크립트
생성할 테이블 스크립트가 작성된 sql 파일이 해당 경로에 있으면 초기 도커 실행시 자동 생성
```

#### 3) 데이터 적재
```
docker exec -it 컨테이너이름 python scripts/load_companies.py
```

