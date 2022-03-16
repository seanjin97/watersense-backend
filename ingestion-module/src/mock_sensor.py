import pika
import time 
import random
import json 
from dotenv import load_dotenv
import os
import datetime

load_dotenv()
RABBITMQ_URI=os.environ["RABBITMQ_URI"]

# Create connection
connection = pika.BlockingConnection(
    pika.URLParameters(RABBITMQ_URI)
)
channel = connection.channel()

# Initialise random data
SENSORS = ["Kitchen", "Shower1", "Shower2", "Toilet1", "Toilet2"]

# Continuously send mock sensor data
while True:
    
    # Randomise data
    day = random.randint(1, 28)
    month = random.randint(1, 12)
    hour = random.randint(0, 11)
    minute = random.randint(0, 59)

    random_duration = random.uniform(1, 10)
    interval =  datetime.timedelta(seconds=random_duration)
    time_start = datetime.datetime.now().replace(month=month, day=day, hour=hour, minute=minute, second=0, microsecond=0)
    time_end = time_start + interval

    random_sensor = random.choice(SENSORS)
    random_session_usage = random.randint(1, 2000)

    randomised_data = json.dumps(
        {
            'startTime': int(time_start.timestamp()),
            'sessionDuration': round(random_duration),
            'device': random_sensor,
            'sessionUsage': random_session_usage,
            # 'device_id': 'be6aa32f-71dd-4c82-b84d-8ed6ea3d9f7d'
            'device_id': '6760e42f-c187-40a1-9196-d35b2621ee46'
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