from dotenv import load_dotenv
import traceback
from sqlalchemy import create_engine
import os
load_dotenv()
USER = os.getenv("MYSQL_USER")
PW   = os.getenv("MYSQL_PW")
DB   = os.getenv("MYSQL_DB")
HOST = os.getenv("MYSQL_HOST")
PORT = os.getenv("MYSQL_PORT")# Setup Instructions

def get_engine():
    try:
        full_url = f"mysql+pymysql://{USER}:{PW}@{HOST}:{PORT}/{DB}"
        return create_engine(
            full_url,
            pool_recycle=3600,
            pool_pre_ping=True
        )
    except Exception as e:
        traceback.print_exc()
        print(f"Error in creating_connection: {e}")
        return None