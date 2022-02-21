from dotenv import load_dotenv
import os
load_dotenv()

MONGO_URI = os.environ["MONGO_URI"]
ENV = os.environ["ENV"]