import os
from langchain_community.utilities.sql_database import SQLDatabase
from sqlalchemy import text, create_engine
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

def getDBEngine(database_url=None):
    # 데이터베이스 URL이 제공되지 않은 경우 환경 변수에서 가져옴
    if not database_url:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL이 제공되지 않았습니다. 환경 변수 또는 매개변수로 제공해주세요.")
    
    # 데이터베이스 엔진 생성
    engine = create_engine(database_url)
    
    # SQLDatabase 인스턴스 생성
    db = SQLDatabase(engine)
    return db