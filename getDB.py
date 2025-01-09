from langchain_community.utilities.sql_database import SQLDatabase
from sqlalchemy import text, create_engine

def getDBEngine(database_url):

    # Create the database engine
    engine = create_engine(database_url)

    db = SQLDatabase(engine)
    return db