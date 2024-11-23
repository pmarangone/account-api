import json
import logging
import psycopg2

from src.utils.routes_responses import (
    BalanceResponse,
    DepositResponse,
    TransferResponse,
    WithdrawResponse,
)

from ..database.account_repository import account_repository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
