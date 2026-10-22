from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="MaltaShop Inventory Service",
    description="Manages product inventory for MaltaShop",
    version="1.0.0"
)

inventory = {
    "product-001": {"name": "T-Shirt", "stock": 50},
    "product-002": {"name": "Hoodie", "stock": 30},
}


class ReservationRequest(BaseModel):
    quantity: int



@app.get("/")
def home():
    return {"message": "MaltaShop Inventory Service is running"}


@app.get("/health")
def health():
    return {"status": "healthy", "service": "inventory-service"}


@app.get("/inventory")
def get_inventory():
    return inventory


@app.get("/inventory/{product_id}")
def get_product(product_id: str):
    if product_id not in inventory:
        return {"error": "Product not found"}

    return inventory[product_id]
@app.post("/inventory/{product_id}/reserve")
def reserve_inventory(product_id: str, request: ReservationRequest):
    if product_id not in inventory:
        raise HTTPException(status_code=404, detail="Product not found")

    if request.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than zero")

    if inventory[product_id]["stock"] < request.quantity:
        raise HTTPException(status_code=400, detail="Not enough stock")

    inventory[product_id]["stock"] -= request.quantity

    return {
        "message": "Stock reserved successfully",
        "product_id": product_id,
        "remaining_stock": inventory[product_id]["stock"]
    }