import pika
import psycopg2

# PostgreSQL database connection settings
DB_HOST = "localhost"
DB_NAME = "database"
DB_USER = "user"
DB_PASSWORD = "password"
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

# RabbitMQ connection settings
RABBITMQ_HOST = "localhost"
RABBITMQ_USER = "myuser"
RABBITMQ_PASSWORD = "mypassword"
RABBITMQ_QUEUE = "transactions"


from src.utils.logger import get_logger

logger = get_logger(__name__)


def connect_db():
    """Establish PostgreSQL database connection"""
    logger.info("Creating database connection")
    return psycopg2.connect(
        host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD
    )


# Connect to RabbitMQ
def connect_rabbitmq():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
    return pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials)
    )
