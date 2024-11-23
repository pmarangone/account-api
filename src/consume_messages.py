import asyncio
import json
from .database.setup_db import connect_rabbitmq, RABBITMQ_QUEUE
from typing import Optional
from .utils.logger import get_logger

logger = get_logger(__name__)


def process_event(ch=None, method=None, properties=None, body=None):
    """
    Parameters:
    ch (pika.Channel, optional)
    method (pika.Basic.Deliver, optional)
    properties (pika.Basic.Properties, optional)
    body (bytes, optional)
    """

    if body is None:
        logger.warning("Received an empty transaction body.")
        return

    try:
        transaction_str = body.decode("utf-8")
        dict_data = json.loads(transaction_str)

        type, destination, amount, origin = (
            dict_data["type"],
            dict_data["destination"],
            dict_data["amount"],
            dict_data["origin"],
        )

        match type:
            case "transfer":
                logger.info(
                    f"Transfer received: {amount} has been transferred to your account from {origin}. Destination: {destination}."
                )
            case "deposit":
                logger.info(
                    f"Deposit received: {amount} has been deposited into your account. Destination: {destination}."
                )

    except Exception as error:
        logger.error(f"Error processing transaction: {error}")
    finally:
        # Acknowledge the message to remove it from the queue
        ch.basic_ack(delivery_tag=method.delivery_tag)


async def consume_messages(stop_event: Optional[asyncio.Future] = None):
    try:
        connection = connect_rabbitmq()
        channel = connection.channel()
        channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)

        channel.basic_consume(
            queue=RABBITMQ_QUEUE,
            on_message_callback=process_event,
            auto_ack=False,
        )
        logger.info("Starting consumer.")

        while True:
            # Check if we need to stop
            if stop_event and stop_event.done():
                logger.error("Stopping consumer...")
                break

            # Async-friendly way to handle I/O bound operations
            # If connection.process_data_events is blocking, consider:
            # await asyncio.to_thread(connection.process_data_events, time_limit=None)
            if hasattr(
                connection, "process_data_events_async"
            ):  # Check if async method exists
                await connection.process_data_events_async(time_limit=None)
            else:
                await asyncio.to_thread(connection.process_data_events, time_limit=None)

            await asyncio.sleep(0.01)

    except ConnectionRefusedError as e:
        logger.error(f"RabbitMQ Connection Refused: {e}")
    except Exception as e:
        logger.critical(f"Unexpected Error in Consumer: {e}")
    finally:
        if "connection" in locals() and connection.is_open:
            connection.close()
        logger.info("Consumer stopped.")
