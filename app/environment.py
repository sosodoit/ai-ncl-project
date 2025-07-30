from dotenv import load_dotenv
import os
from pathlib import Path

env_path = Path(__file__).parent / "config" / "db_config.env"
load_dotenv(dotenv_path=env_path)

env = {
    "POSTGRE_HOST": os.getenv("POSTGRE_HOST"),
    "POSTGRE_PORT": os.getenv("POSTGRE_PORT"),
    "POSTGRE_DB": os.getenv("POSTGRE_DB"),
    "POSTGRE_USER": os.getenv("POSTGRE_USER"),
    "POSTGRE_PASSWORD": os.getenv("POSTGRE_PASSWORD"),
    "CATCH_ID" :os.getenv("CATCH_ID"),
    "CATCH_PW" : os.getenv("CATCH_PW")

}
