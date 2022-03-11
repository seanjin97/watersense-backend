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
total_usage = 0

# Continuously send mock sensor data
while True:
    
    # Randomly send data at random intervals of < 10s (float value)
    random_duration = random.uniform(1, 10)
    interval =  datetime.timedelta(seconds=random_duration)
    time_start = datetime.datetime.now()
    time_end = time_start + interval

    random_sensor = random.choice(SENSORS)
    random_session_usage = random.randint(1, 2000)
    total_usage += random_session_usage

    randomised_data = json.dumps(
        {
            'startTime': int(time_start.timestamp()),
            'endTime': int(time_end.timestamp()),
            'sessionDuration': round(random_duration),
            'device': random_sensor,
            'sessionUsage': random_session_usage,
            'totalUsage': total_usage,
            'device_id': 'be6aa32f-71dd-4c82-b84d-8ed6ea3d9f7d'
        }
    )

    print(f"producer: sending data - {randomised_data}")
    channel.basic_publish(
        exchange='amq.topic', 
        routing_key='watersense', 
        body=str(randomised_data)
    )
    time.sleep(random_duration)

connection.close()