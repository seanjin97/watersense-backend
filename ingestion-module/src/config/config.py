from dotenv import load_dotenv
import os
load_dotenv()

RABBITMQ_HOST=os.environ["RABBITMQ_HOST"]
RABBITMQ_PORT=os.environ["RABBITMQ_PORT"]
RABBITMQ_USER=os.environ["RABBITMQ_USER"]
RABBITMQ_PW=os.environ["RABBITMQ_PW"]
RABBITMQ_INGESTION_EXCHANGE=os.environ["RABBITMQ_INGESTION_EXCHANGE"]
RABBITMQ_INGESTION_QUEUE=os.environ["RABBITMQ_INGESTION_QUEUE"]
RABBITMQ_INGESTION_KEY=os.environ["RABBITMQ_INGESTION_KEY"]

MONGO_URI = os.environ["MONGO_URI"]