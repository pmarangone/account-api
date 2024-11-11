import pika
import psycopg2

# PostgreSQL database connection settings
DB_HOST = "localhost"
DB_NAME = "database"
DB_USER = "user"
DB_PASSWORD = "password"

# RabbitMQ connection settings
RABBITMQ_HOST = "localhost"
RABBITMQ_QUEUE = "transactions"

# Assuming these match your docker-compose.yml config
RABBITMQ_HOST = "localhost"  # Since you're mapping ports directly
RABBITMQ_USER = "myuser"
RABBITMQ_PASSWORD = "mypassword"


def connect_db():
    """Establish PostgreSQL database connection"""
    return psycopg2.connect(
        host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD
    )


# Connect to RabbitMQ
def connect_rabbitmq():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
    return pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials)
    )
