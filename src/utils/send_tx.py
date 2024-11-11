import pika
import json
from fastapi.encoders import jsonable_encoder

from ..database.setup_db import connect_rabbitmq, RABBITMQ_QUEUE


def send_transaction_to_rabbitmq(transaction):
    try:
        connection = connect_rabbitmq()
        channel = connection.channel()

        channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)

        transaction_json = jsonable_encoder(transaction)
        transaction_json = json.dumps(transaction_json)

        channel.basic_publish(
            exchange="",
            routing_key=RABBITMQ_QUEUE,
            body=transaction_json,
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make message persistent
            ),
        )

        print(f"Transaction sent to RabbitMQ: {transaction}")

        connection.close()

    except Exception as e:
        print("error send tx", e)  # TODO
