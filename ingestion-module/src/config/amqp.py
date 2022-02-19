import pika
import config.config as config

hostname = config.RABBITMQ_HOST
port = int(config.RABBITMQ_PORT)

credentials = pika.PlainCredentials(config.RABBITMQ_USER, config.RABBITMQ_PW)

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=hostname, port=port,
        heartbeat=3600, blocked_connection_timeout=3600,
        credentials=credentials
    )
)

channel = connection.channel()
channel.basic_qos(prefetch_count=1)

queue_declare = channel.queue_declare(queue=config.RABBITMQ_INGESTION_QUEUE)

channel.queue_bind(exchange=config.RABBITMQ_INGESTION_EXCHANGE, queue=queue_declare.method.queue, routing_key=config.RABBITMQ_INGESTION_KEY)