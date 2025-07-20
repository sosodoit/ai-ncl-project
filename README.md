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
- 위 프로젝트 구조(파일)가 동일하고
- 루트 경로가 동일한지 확인

### 2. 환경 변수 설정
```
.env 파일에서 PostgreSQL 접속 정보 등을 필요에 맞게 수정

# PostgreSQL 설정
POSTGRE_HOST=localhost
POSTGRE_PORT=5432
POSTGRE_DB=mydb
POSTGRE_USER=postgres
POSTGRE_PASSWORD=your_password
```
- 도커로 실행할시,
- POSTGRE_HOST 는 docker-compose.yml의 db 서비스명과 동일해야함 (서비스명: db)
- POSTGRE_PORT 는 기본 디폴트 포트 사용
- POSTGRE_DB 는 생성할 DB 명 입력 (본인은 corpdata 입력함)
- USER는 기본 디폴트 계정 postgres 사용
- PASSWORD는 자신의 PostgreSQL 셋팅시 설정했던 내용

### 3. Docker로 실행 (FastAPI + PostgreSQL)
```
docker-compose up --build
```
- 위 명령어 실행시, Dockefile에 작성해둔 py39 기반으로 requirements 라이브러리 설치되고 fastapi 사용할 수 있는 환경이 셋팅된 이미지 빌드 시작
- 이어서 postgres와 네트워크 연결된 컨테이너 생성되면서,
- 정상 실행중이면 fastapi 서버 확인 가능, 작업 시작

## ⚙️ 도커 기본 명령어
- 작업시 자주 사용하는거
```
# 컨테이너 실행 및 종료
docker-compose up         # docker-compose.yml 기반으로 서비스 실행 (매일 코드만 바뀌는 경우)
docker-compose up --build # 이미지 재빌드 + 실행 (패키지/환경이 바뀐 경우)
docker-compose down       # 실행 중인 모든 컨테이너 종료 및 네트워크 제거 (오늘 작업 끝났을 경우 종료!)
docker-compose down -v    # 완전히 깨끗이 정리하고 싶을 때 (DB 포함 초기화)

# 이미지 & 컨테이너 관리
docker images             # 로컬에 저장된 이미지 목록 보기
docker ps                 # 현재 실행 중인 컨테이너 확인
docker ps -a              # 종료된 것 포함 전체 컨테이너 확인
docker rm <컨테이너명>     # 컨테이너 삭제
docker rmi <이미지명>      # 이미지 삭제

# 컨테이너 내부 접속 (도커 데스크톱 사용시 내부 디렉토리 gui 확인 가능)
docker exec -it <컨테이너명> bash        # 리눅스 컨테이너 bash 쉘 접속
docker exec -it <컨테이너명> sh          # 일부 Alpine 컨테이너는 sh 사용
docker exec -it <컨테이너명> python      # 파이썬 실행 (스크립트 실행 테스트)
```

- 필요한 이미지 가져오기
```
# FastAPI Dockerfile 이미지 빌드 및 실행 (예시)
docker build -t myfastapi .                              # 현재 디렉토리에서 이미지 빌드
docker run -d --name fastapiserver -p 80:80 myfastapi    # 빌드된 이미지 실행

# PostgreSQL 도커 이미지 가져오기 (예시)
docker pull postgres
docker run -p 5432:5432 --name postgresdb -e POSTGRES_PASSWORD=# -d -v pgdata:/var/lib/postgresql/data postgres
```

## ⚙️ DB 관련 작업
company_info 테이블 기준 설명

#### 1) DB 생성
```
초기 환경변수에서 입력한 DB명으로 생성됨: corpdata
POSTGRES_DB는 초기 생성될 기본 DB 이름일 뿐이며, 이후에 SQL로 얼마든지 다른 DB를 추가 생성 가능하다고 함
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

