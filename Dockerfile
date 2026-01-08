# 베이스 이미지 (파이썬 버전 고정)
FROM python:3.11-slim

# 시스템 패키지 업데이트 및 tzdata 설치
RUN apt-get update && apt-get install -y \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사 및 패키지 설치 (setup.py 실행)
COPY . .
RUN pip install .

# 실행 설정 (Cloud Run 기본 포트 8080)
ENV PORT=8080
EXPOSE 8080

# Streamlit 실행 (주소와 포트 고정)
# --server.enableCORS=false와 --server.enableXsrfProtection=false를 추가합니다.
CMD ["streamlit", "run", "main.py", \
    "--server.port=8080", \
    "--server.address=0.0.0.0", \
    "--server.enableCORS=false", \
    "--server.enableXsrfProtection=false"]
