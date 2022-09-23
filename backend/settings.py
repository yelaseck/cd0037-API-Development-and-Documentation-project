from dotenv import load_dotenv
import os

load_dotenv()

DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_NAME_TEST = os.environ.get("DB_NAME_TEST")
DB_URL = os.environ.get("DB_URL")
DB_TYPE = os.environ.get("DB_TYPE")

DB_PATH = '{}://{}:{}@{}/{}'.format(DB_TYPE, DB_USER, DB_PASSWORD, DB_URL, DB_NAME)
DB_PATH_TEST = '{}://{}:{}@{}/{}'.format(DB_TYPE, DB_USER, DB_PASSWORD, DB_URL, DB_NAME_TEST)