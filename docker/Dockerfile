# 파일명: Dockerfile
# 설명: FastAPI 애플리케이션을 위한 Docker 이미지 빌드 설정 파일입니다.
# 관련 파일: requirements.txt, app/main.py
# 주의사항:
# - 로컬 개발 환경에서는 uvicorn을 통해 실행되며, 포트는 80번으로 설정되어 있습니다.

FROM python:3.10-slim

WORKDIR /app

COPY requirements/prod.txt ./requirements.txt

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY ./app ./app
COPY ./scripts ./scripts

ENV PYTHONPATH=/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]