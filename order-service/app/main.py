
import json
import logging
import os
import time
from uuid import uuid4

import pika
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("order-service")

app = FastAPI(
    title="MaltaShop Order Service",
    description="Manages customer orders for MaltaShop",
    version="1.0.0"
)

orders = {}


class OrderRequest(BaseModel):
    product_id: str
    quantity: int


def publish_order_event(event):
    rabbitmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
    connection = None

    for attempt in range(5):
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=rabbitmq_host,
                    heartbeat=30,
                    blocked_connection_timeout=5
                )
            )
            break
        except pika.exceptions.AMQPConnectionError:
            logger.warning(
                "RabbitMQ unavailable, retry %s/5",
                attempt + 1
            )
            time.sleep(2)

    if connection is None:
        raise RuntimeError("Unable to connect to RabbitMQ")

    try:
        channel = connection.channel()
        channel.queue_declare(queue="order_events", durable=True)

        channel.basic_publish(
            exchange="",
            routing_key="order_events",
            body=json.dumps(event),
            properties=pika.BasicProperties(
                delivery_mode=2,
                correlation_id=event["correlation_id"],
                content_type="application/json"
            )
        )

        logger.info(
            "Published OrderPlaced order_id=%s correlation_id=%s",
            event["order_id"],
            event["correlation_id"]
        )
    finally:
        connection.close()


@app.get("/")
def home():
    return {"message": "MaltaShop Order Service is running"}


@app.get("/health")
def health():
    return {"status": "healthy", "service": "order-service"}


@app.post("/orders", status_code=201)
def create_order(order: OrderRequest):
    if order.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than zero"
        )

    try:
        response = requests.post(
            f"http://inventory-service:8001/inventory/{order.product_id}/reserve",
            json={"quantity": order.quantity},
            timeout=5
        )
    except requests.RequestException:
        raise HTTPException(
            status_code=503,
            detail="Inventory service unavailable"
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.json().get(
                "detail", "Inventory reservation failed"
            )
        )

    order_id = str(uuid4())
    correlation_id = str(uuid4())

    new_order = {
        "order_id": order_id,
        "product_id": order.product_id,
        "quantity": order.quantity,
        "status": "confirmed",
        "correlation_id": correlation_id
    }

    orders[order_id] = new_order

    event = {
        "event_type": "OrderPlaced",
        "order_id": order_id,
        "product_id": order.product_id,
        "quantity": order.quantity,
        "correlation_id": correlation_id
    }

    try:
        publish_order_event(event)
    except Exception:
        logger.exception(
            "Failed to publish OrderPlaced correlation_id=%s",
            correlation_id
        )
        # Order was already confirmed and stock reserved.
        # Do not claim that event publication succeeded.
        new_order["event_status"] = "publish_failed"
    else:
        new_order["event_status"] = "published"

    return new_order
