
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uuid import uuid4
import requests

app = FastAPI(
    title="MaltaShop Order Service",
    description="Manages customer orders for MaltaShop",
    version="1.0.0"
)

orders = {}


class OrderRequest(BaseModel):
    product_id: str
    quantity: int


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
            detail=response.json().get("detail", "Inventory reservation failed")
        )

    order_id = str(uuid4())

    new_order = {
        "order_id": order_id,
        "product_id": order.product_id,
        "quantity": order.quantity,
        "status": "confirmed"
    }

    orders[order_id] = new_order

    return new_order



