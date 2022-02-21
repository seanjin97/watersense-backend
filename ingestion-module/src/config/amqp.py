import pika
import config.config as config

connection = pika.BlockingConnection(
    pika.URLParameters(config.RABBITMQ_URI)
)

channel = connection.channel()
channel.basic_qos(prefetch_count=1)

queue_declare = channel.queue_declare(queue=config.RABBITMQ_INGESTION_QUEUE)

channel.queue_bind(exchange=config.RABBITMQ_INGESTION_EXCHANGE, queue=queue_declare.method.queue, routing_key=config.RABBITMQ_INGESTION_KEY)