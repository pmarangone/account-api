import json
import psycopg2

from src.utils.routes_responses import (
    BalanceResponse,
    DepositResponse,
    TransferResponse,
    WithdrawResponse,
)

from src.database.account_repository import account_repository

import pika
import json
from fastapi.encoders import jsonable_encoder

from src.database.setup_db import connect_rabbitmq, RABBITMQ_QUEUE

from src.utils.logger import get_logger

logger = get_logger(__name__)


class EventService:
    @staticmethod
    def process_transaction(body):
        try:
            type, destination, amount, origin = (
                body.type,
                body.destination,
                body.amount,
                body.origin,
            )

            logger.info(f"data {body}")

            match type:
                case "deposit":
                    updated_data = account_repository.update_balance(
                        destination, amount
                    )

                    EventService.publish_event(body)

                    return DepositResponse(
                        destination=BalanceResponse(
                            id=updated_data["id"], balance=updated_data["balance"]
                        )
                    )
                case "withdraw":
                    to_withdraw = -amount  # decrement from current balance
                    updated_data = account_repository.update_balance(
                        origin, to_withdraw
                    )
                    return WithdrawResponse(
                        origin=BalanceResponse(
                            id=updated_data["id"], balance=updated_data["balance"]
                        )
                    )
                case "transfer":
                    decrement_from_origin = -amount
                    transfer_to_destination = amount

                    origin_data = account_repository.update_balance(
                        origin, decrement_from_origin
                    )
                    destination_data = account_repository.update_balance(
                        destination, transfer_to_destination
                    )

                    EventService.publish_event(body)

                    return TransferResponse(
                        origin=BalanceResponse(
                            id=origin_data["id"], balance=origin_data["balance"]
                        ),
                        destination=BalanceResponse(
                            id=destination_data["id"],
                            balance=destination_data["balance"],
                        ),
                    )

        except (Exception, psycopg2.DatabaseError) as error:
            print("e", error)  # TODO

            raise error

    @staticmethod
    def publish_event(transaction):
        try:
            connection = connect_rabbitmq()
            channel = connection.channel()

            channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)

            transaction_json = jsonable_encoder(transaction)
            transaction_json = json.dumps(transaction_json)

            channel.basic_publish(
                exchange="",
                routing_key=RABBITMQ_QUEUE,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                ),
                body=transaction_json,
            )

            logger.info(f"Transaction sent to RabbitMQ: {transaction}")

            connection.close()

        except Exception as e:
            logger.error(f"Unexpected error while sending transaction: {e}")
