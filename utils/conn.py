import time
import pandas as pd
import streamlit as st
from sqlalchemy.exc import OperationalError
from sqlalchemy.engine import Engine
from sqlalchemy import create_engine, text
import os
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
from .logger_config import setup_logging
import logging

# .env 파일 로드
current_dir = Path(__file__).parent
env_path = current_dir / '.env'
load_dotenv(dotenv_path=env_path)

# 로깅 설정
setup_logging()
logger = logging.getLogger(__name__)

# 글로벌 engine 객체
db_engine = None

def get_base_path():
    try:
        # 스크립트 파일(.py) 실행 시
        return Path(__file__).resolve().parent
    except NameError:
        # 주피터 노트북 실행 시
        return Path.cwd()


##################################
# 현재 DB 기록 내 최대연도 구하기
##################################
def get_max_year(engine):
    query = """
    SELECT
    max(year) FROM raw_tracking.tm;
    """
    with engine.begin() as connection:
        result = connection.execute(text(query))
        최대연도 = result.cursor.fetchone()[0]
        return 최대연도

##################################
# 현재 DB 트래킹 데이터 내 연도 목록 구하기
##################################
def get_season_list(engine):
    query = """
    SELECT
    DISTINCT year FROM raw_tracking.tm;
    """
    with engine.begin() as connection:
        result = connection.execute(text(query))
        res = result.cursor.fetchall()
        연도목록 = [x[0] for x in res]
        return 연도목록

def get_conn(db_name: str = None):
    """
    1. st.secrets (로컬의 secrets.toml 혹은 서버의 환경 변수)
    2. os.getenv (시스템 환경 변수)
    순서로 값을 읽어 SQLAlchemy Engine을 생성합니다.
    """
    
    # 헬퍼 함수: secrets와 env를 통합해서 찾음
    def get_setting(key, default=None):
        try:
            # 1. st.secrets 내부의 gcp_db_setups 딕셔너리 확인
            if 'gcp_db_setups' in st.secrets:
                if key in st.secrets['gcp_db_setups']:
                    return st.secrets['gcp_db_setups'][key]

            # 2. st.secrets 상위 레벨 혹은 환경 변수 확인 (Streamlit이 자동 매핑)
            if key in st.secrets:
                return st.secrets[key]
        except (KeyError, FileNotFoundError, RuntimeError, Exception):
            # secrets.toml이 없으면 위 구문에서 에러가 날 수 있으므로 pass
            pass

        # 3. 마지막 수단으로 os.environ 확인
        # Cloud Run에 넣은 환경 변수는 여기서 잡힘
        return os.getenv(key, default)

    # 설정값 로드
    user = get_setting('DB_USER')
    pw = get_setting('DB_PW')
    host = get_setting('DB_HOST')
    port = get_setting('DB_PORT', 3306)

    # 디버깅용 (비밀번호는 제외하고 로그 출력)
    if not all([user, pw, host]):
        logger.error("DB 연결 설정이 누락되었습니다. DB_USER, DB_PW, DB_HOST를 확인하세요.")
        logger.error(f"설정 누락 -> USER: {user is not None}, PW: {pw is not None}, HOST: {host is not None}")
        raise ValueError("Database configuration missing.")

    # DB URL 빌드
    db_path = f"/{db_name}" if db_name else ""
    db_url = f"mysql+pymysql://{user}:{pw}@{host}:{port}{db_path}?charset=utf8mb4"

    try:
        engine = create_engine(
            db_url,
            pool_size=5,
            max_overflow=2,
            pool_recycle=1800,
            pool_pre_ping=True,
            echo=False
        )
        logger.info(f"DB Engine 생성 완료 (Host: {host}, DB: {db_name})")
        return engine
    except Exception as e:
        logger.error(f"DB 연결 실패: {e}")
        raise e


def get_sql_df(query,
               engine,
               max_retries = 3,
               retry_delay = 5,
               verbose=False):
    """
    쿼리를 실행, DF 리턴

    Parameters:
        query (str): SQL 쿼리
        engine (sqlalchemy.engine.Engine): sqlalchemy engine 객체
        max_retries (int): 최대 재시도 횟수
        retry_delay (int): 재시도 전 대기시간
        verbose (boolean): 내용 출력 여부

    Returns:
        DataFrame: 읽어온 데이터
    """

    for attempt in range(max_retries):
        try:
            st = time.time()
            if verbose is True:
                print(f'{attempt+1}번째 SELECT 시도')
            df = pd.read_sql(query, con=engine)
            et = time.time()
            if verbose is True:
                print(f'Duration: {et - st:.1f}sec')
            break  # 성공하면 반복문 탈출
        except OperationalError as e:
            if verbose is True:
                print(f"DB 연결 실패, {retry_delay}초 후 재시도 ({attempt+1}/{max_retries})")
            time.sleep(retry_delay)
    else:
        if verbose is True:
            print("재시도 실패: DB 연결에 문제가 있습니다.")
        return
    if verbose is True:
        print("DB 연결 성공, 리턴")
    return df


def execute_dml_query(query: str,
                      engine: Engine,
                      params=None,  # 대량 데이터(list of dict)를 받을 수 있도록 추가
                      verbose=False):
    """
    SQLAlchemy Engine을 사용하여 DML 쿼리를 실행합니다.
    Batch 처리를 위해 params 인자를 지원합니다.
    """
    try:
        with engine.begin() as connection:
            # engine.begin()은 커밋/롤백을 자동으로 처리합니다.
            # text() 함수를 사용하여 쿼리 문자열을 실행 가능한 객체로 변환합니다.
            # params가 있으면 executemany 패턴으로 자동 실행됩니다.
            result = connection.execute(text(query), params)
            if verbose:
                logger.info(f"쿼리 실행 완료. 영향받은 행: {result.rowcount}")
            return result
    except Exception as e:
        if verbose:
            logger.error(f"DML 실행 오류: {e}")
        raise

@st.cache_resource
def get_gcs_storage_options():
    """
    로컬(파일/Secrets) 및 Cloud Run(환경변수/IAM) 환경에 모두 대응하는 GCS 설정 반환
    """
    # 1. 로컬 개발용 키 파일 경로 (utils/conn.py 기준 상위 폴더의 .cred)
    key_path = current_dir.parent / ".cred" / "service_account_key.json"

    # CASE A: Streamlit Secrets에 직접 신분증 정보가 있는 경우 (주로 Streamlit Community Cloud나 특정 설정 시)
    try:
        if st.secrets and "gcp_service_account" in st.secrets:
            logger.info("Streamlit Secrets에서 GCP 서비스 계정 정보를 로드합니다.")
            return {"token": dict(st.secrets["gcp_service_account"])}
    except Exception:
        pass

    # CASE B: 로컬 파일 시스템에 키 파일이 존재하는 경우
    if key_path.exists():
        logger.info(f"로컬 키 파일({key_path})을 사용하여 인증합니다.")
        return {"token": str(key_path)}

    # CASE C: Cloud Run 및 환경 변수 기반 인증
    # GOOGLE_APPLICATION_CREDENTIALS 환경 변수가 있거나, 
    # Cloud Run처럼 서비스 계정이 연결된 환경에서는 'None' 혹은 빈 값을 넘기면 
    # 구글 클라이언트 라이브러리가 자동으로 인증(ADC)을 수행합니다.
    logger.info("시스템 기본 인증(ADC) 또는 환경 변수를 사용합니다.")
    return {"token": None}
