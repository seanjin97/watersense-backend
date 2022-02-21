import pika
import time 
import random
import json 
from dotenv import load_dotenv
import os
load_dotenv()
RABBITMQ_URI=os.environ["RABBITMQ_URI"]

# Create connection
connection = pika.BlockingConnection(
    pika.URLParameters(RABBITMQ_URI)
)

channel = connection.channel()
channel.exchange_declare(exchange='watersense.data',
                 exchange_type='direct', durable=True)

# Send 10 sample data points
for i in range(10):
    random_start_timestamp = random.randint(1645173689, 1665173689)
    randomised_data = json.dumps({
        "start_timestamp": random_start_timestamp,
        "end_timestamp": random_start_timestamp + 1000,
        "sensor_id": "hadkshf23e"
    })
    print(f"producer: sending data - {randomised_data}")
    channel.basic_publish(
        exchange='watersense.data', 
        routing_key='sensor.data', 
        body=randomised_data
    )
    time.sleep(3)

connection.close()