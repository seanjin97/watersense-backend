import sys
import pika
import time 
import random
import json 
from dotenv import load_dotenv
import os
import datetime
import uuid
from pymongo import MongoClient
import pytz
import sys

tz_info = pytz.timezone('Asia/Singapore')

# Load config variables
load_dotenv()

RABBITMQ_URI=os.environ["RABBITMQ_URI"]
MONGO_URI=os.environ["MONGO_URI"]

# Initialise DB
client = MongoClient(MONGO_URI)
db = client.watersense

# Create connection
connection = pika.BlockingConnection(
    pika.URLParameters(RABBITMQ_URI)
)
channel = connection.channel()

# Create random user and random sensor IDs
sensor1_id = str(uuid.uuid4())
sensor2_id = str(uuid.uuid4())
sensor3_id = str(uuid.uuid4())
sensor4_id = str(uuid.uuid4())
sensor5_id = str(uuid.uuid4())

if (sys.argv[1] == "test1"):
    sensor6_id = "be6aa32f-71dd-4c82-b84d-8ed6ea3d9f7d"
else:
    sensor6_id = str(uuid.uuid4())

example_user = {
    'username': sys.argv[1],
    'sensors': [sensor1_id, sensor2_id, sensor3_id, sensor4_id, sensor5_id, sensor6_id],
    "goals": {
        "daily": 130000,
        "monthly": 390000
    }
}
SENSORS = [
{"device": "Kitchen_1", "device_id": sensor1_id}, 
{"device": "Shower_1", "device_id": sensor2_id}, 
{"device": "Shower_2", "device_id": sensor3_id}, 
{"device": "Toilet_1", "device_id": sensor4_id}, 
{"device": "Toilet_2", "device_id": sensor5_id},
{"device": "Sink_1", "device_id": sensor6_id},
]

db.user.insert_one(example_user)

# Continuously send mock sensor data
while True:
    
    # Randomise data
    day = random.randint(1, 28)
    month = random.randint(1, 12)
    hour = random.randint(0, 11)
    minute = random.randint(0, 59)

    random_duration = random.uniform(1, 10)
    interval =  datetime.timedelta(seconds=random_duration)
    time_start = datetime.datetime.now(tz_info).replace(day=day, month=month, hour=hour, minute=minute)
    time_end = time_start + interval

    random_sensor = random.choice(SENSORS)
    random_session_usage = random.randint(1, 2000)

    randomised_data = json.dumps(
        {   
            "device": random_sensor["device"],
            "device_id": random_sensor["device_id"],
            'startTime': int(time_start.timestamp()),
            'sessionDuration': round(random_duration),
            'sessionUsage': random_session_usage
        }
    )

    print(f"producer: sending data - {randomised_data}")
    channel.basic_publish(
        exchange='amq.topic', 
        routing_key='watersense', 
        body=str(randomised_data)
    )
# time.sleep(random_duration)

connection.close()