import json
import psycopg2

from src.utils import response
from src.models.errors import NonExist
from src.utils.routes_responses import (
    BalanceResponse,
    DepositResponse,
    TransferResponse,
    WithdrawResponse,
)

from src.repositories.account import AccountRepository

import pika
import json
from fastapi.encoders import jsonable_encoder

from src.database.setup_db import connect_rabbitmq, RABBITMQ_QUEUE

from src.utils.logger import get_logger

logger = get_logger(__name__)


class EventService:
    def __init__(self, repository: AccountRepository):
        self.account_repository = repository

    def get_account_balance(self, account_id):
        try:
            account = self.account_repository.get_account(account_id)
            if not account:
                error_msg = f"Account does not exist. Account: {account_id}"
                logger.info(error_msg)
                raise NonExist(error_msg)

            return BalanceResponse(id=account.account_id, balance=account.balance)
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(f"Error: {error}")
            return response.bad_request({"error": str(error)})

    def deposit(self, account_id: str, amount: int):
        logger.warn(f"{account_id} {amount}")
        account = self.account_repository.get_account_with_lock(account_id)

        if not account:
            account = self.account_repository.create_account(account_id, amount)
        else:
            account = self.account_repository.update_account_balance(account, amount)

        return account

    def withdraw(self, account_id: str, amount: int):
        account = self.account_repository.get_account_with_lock(account_id)

        if not account:
            error_msg = f"Account does not exist. Account: {account_id}"
            logger.info(error_msg)
            raise NonExist(error_msg)
        elif account.balance < amount:
            error_msg = f"Account does not have enough balance. Account: {account_id}, amount: {amount}"
            logger.info(error_msg)
            raise Exception(error_msg)

        to_withdraw = -amount  # decrement from current balance
        account = self.account_repository.update_account_balance(account, to_withdraw)

        return account

    def process_transaction(self, body):
        """NOTE
        Commits occur at the service level, avoiding updating the database before
        all transactions went through.

        Example: If the withdrawal succeeds but the deposit fails, any changes
        to the origin account must also be reverted manually to maintain
        consistency.

        Fix:
        """
        try:
            event_type, destination, amount, origin = (
                body.type,
                body.destination,
                body.amount,
                body.origin,
            )

            logger.info(f"data {body}")

            match event_type:
                case "deposit":
                    account = self.deposit(destination, amount)

                    EventService.publish_event(body)

                    # Defer committing until all operations went through
                    self.account_repository.commit()

                    return DepositResponse(
                        destination=BalanceResponse(
                            id=account.account_id, balance=account.balance
                        )
                    )
                case "withdraw":
                    account = self.withdraw(origin, amount)

                    # Defer committing until all operations went through
                    self.account_repository.commit()

                    return WithdrawResponse(
                        origin=BalanceResponse(
                            id=account.account_id, balance=account.balance
                        )
                    )
                case "transfer":
                    origin_account = self.withdraw(origin, amount)
                    destination_account = self.deposit(destination, amount)

                    EventService.publish_event(body)

                    # Defer committing until all operations went through
                    self.account_repository.commit()

                    return TransferResponse(
                        origin=BalanceResponse(
                            id=origin_account.account_id,
                            balance=origin_account.balance,
                        ),
                        destination=BalanceResponse(
                            id=destination_account.account_id,
                            balance=destination_account.balance,
                        ),
                    )

        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(f"Error: {error}")
            self.account_repository.rollback()
            return response.bad_request({"error": str(error)})

        finally:
            self.account_repository.close()

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
