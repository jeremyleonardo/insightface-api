from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL") 
RECREATE_TABLES_EACH_RUN = os.getenv("RECREATE_TABLES_EACH_RUN")