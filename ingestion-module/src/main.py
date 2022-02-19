import config.amqp as amqp
import json
import config.config as config
import dao.sensor as sensor_db

# Message consumer thread
def receive_messages():
    amqp.channel.basic_consume(queue=config.RABBITMQ_INGESTION_QUEUE, on_message_callback=callback, auto_ack=True)
    try:
        amqp.channel.start_consuming()
    except KeyboardInterrupt:
        amqp.channel.stop_consuming()
    amqp.connection.close()

# Callback function that processes incoming messages
def callback(channel, method, properties, body):
    print("Message received:", json.loads(body))
    sensor_db.insert(json.loads(body))
    print() 

if __name__ == "__main__":
    print("Server started.")
    receive_messages()