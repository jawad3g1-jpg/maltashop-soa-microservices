
import json
import logging
import os
import time

import pika

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger("notification-service")


def process_event(channel, method, properties, body):
    try:
        event = json.loads(body)
        correlation_id = event.get(
            "correlation_id",
            properties.correlation_id
        )

        logger.info(
            "Consumed %s order_id=%s correlation_id=%s",
            event.get("event_type"),
            event.get("order_id"),
            correlation_id
        )

        channel.basic_ack(delivery_tag=method.delivery_tag)
    except Exception:
        logger.exception("Failed to process event")
        channel.basic_nack(
            delivery_tag=method.delivery_tag,
            requeue=False
        )


def main():
    host = os.getenv("RABBITMQ_HOST", "rabbitmq")

    while True:
        connection = None
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=host)
            )
            channel = connection.channel()
            channel.queue_declare(
                queue="order_events",
                durable=True
            )
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(
                queue="order_events",
                on_message_callback=process_event
            )

            logger.info(
                "Notification Service waiting for OrderPlaced events"
            )
            channel.start_consuming()

        except Exception:
            logger.exception(
                "RabbitMQ connection lost; retrying in 5 seconds"
            )
            time.sleep(5)
        finally:
            if connection and connection.is_open:
                connection.close()


if __name__ == "__main__":
    main()
