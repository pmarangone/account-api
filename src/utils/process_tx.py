import json
import logging
import psycopg2

from ..database.setup_db import connect_db

from ..database.account_repository import account_repository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process_transaction(ch=None, method=None, properties=None, body=None):
    db = connect_db()
    cur = db.cursor()

    transaction = body

    try:
        transaction_str = transaction.decode("utf-8")
        dict_data = json.loads(transaction_str)

        type, destination, amount, origin = (
            dict_data["type"],
            dict_data["destination"],
            dict_data["amount"],
            dict_data["origin"],
        )

        # Lock the user's account row in the database
        logger.info(f"data {dict_data}")

        match type:
            case "deposit":
                account_repository.update_balance(destination, amount)
            case "withdraw":
                account_repository.update_balance(origin, amount)
            case "transfer":
                transfer_to_destination = amount
                decrement_from_origin = -amount
                account_repository.update_balance(origin, decrement_from_origin)
                account_repository.update_balance(destination, transfer_to_destination)
    except (Exception, psycopg2.DatabaseError) as error:
        print("e", error)  # TODO
        db.rollback()
    finally:
        if cur:
            cur.close()
        # if db:
        #     db.close()

        # Acknowledge the message to remove it from the queue
        ch.basic_ack(delivery_tag=method.delivery_tag)
