import asyncio
from .database.setup_db import connect_rabbitmq, RABBITMQ_QUEUE
from typing import Optional
from src.utils.process_tx import process_transaction
from .utils.logger import get_logger

logger = get_logger(__name__)


async def consume_messages(stop_event: Optional[asyncio.Future] = None):
    try:
        connection = connect_rabbitmq()
        channel = connection.channel()
        channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)

        channel.basic_consume(
            queue=RABBITMQ_QUEUE,
            on_message_callback=process_transaction,
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
