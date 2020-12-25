from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL") 
CREATE_ALL_EACH_RUN = os.getenv("CREATE_ALL_EACH_RUN", "True")
DROP_ALL_EACH_RUN = os.getenv("DROP_ALL_EACH_RUN", "False")