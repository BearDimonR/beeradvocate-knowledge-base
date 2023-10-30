import json

from dotenv import load_dotenv
import os

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
COOKIES = json.loads(os.getenv("COOKIES"))

DIR_PATH = os.path.dirname(__file__)
FOLDER = os.path.join(DIR_PATH, "scrapped_data")
