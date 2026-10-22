
# MaltaShop — Service-Oriented Architecture and Microservices

## Project Overview

MaltaShop is a working microservices prototype developed for a Service-Oriented Architecture assessment.

The project demonstrates independently containerised services, synchronous REST communication, asynchronous event messaging through RabbitMQ, and distributed tracing using correlation IDs.

## Technologies

- Python
- FastAPI
- Docker and Docker Compose
- RabbitMQ
- GitHub Actions

## Implemented Services

### 1. Order Service

Port: `8000`

- Exposes a REST API for creating orders.
- Validates order quantities.
- Requests stock reservation from the Inventory Service.
- Generates an order ID and correlation ID.
- Publishes an `OrderPlaced` event to RabbitMQ after successful order creation.

API documentation: http://localhost:8000/docs

### 2. Inventory Service

Port: `8001`

- Provides inventory information.
- Processes stock reservation requests from the Order Service.
- Updates available stock following successful reservations.

### 3. Notification Service

- Connects to RabbitMQ.
- Consumes `OrderPlaced` events from the `order_events` queue.
- Logs consumed events with their order IDs and correlation IDs.
- Demonstrates asynchronous event processing.

This prototype logs notification events rather than sending real emails or push notifications.

### 4. RabbitMQ

Management interface: http://localhost:15672

Default local credentials:

- Username: `guest`
- Password: `guest`

RabbitMQ enables asynchronous communication between the Order and Notification services.

## Architecture

```text
Client
  |
  | HTTP POST /orders
  v
Order Service
  |
  | Synchronous REST request
  v
Inventory Service
  |
  | Stock reservation response
  v
Order Service
  |
  | Publish OrderPlaced event
  v
RabbitMQ
  |
  | Consume event
  v
Notification Service
```

## Running the Project

### Prerequisites

- Docker Desktop
- Docker Compose

### Start the services

Open a terminal in the project root and run:

```bash
docker compose up --build -d
```

### Check container status

```bash
docker compose ps
```

### Test order creation

1. Open http://localhost:8000/docs
2. Expand `POST /orders`.
3. Click **Try it out**.
4. Enter:

```json
{
  "product_id": "product-001",
  "quantity": 1
}
```

5. Click **Execute**.

A successful request returns HTTP `201 Created`, including an order ID, correlation ID, and event publication status.

### Verify asynchronous event consumption

Run:

```bash
docker compose logs notification-service --tail 30
```

Look for a log entry containing `Consumed OrderPlaced`.

### Verify event publication

Run:

```bash
docker compose logs order-service --tail 50
```

Look for a log entry containing `Published OrderPlaced`.

The correlation IDs in the publishing and consuming logs can be compared to trace the same event.

## Continuous Integration

The project includes a GitHub Actions workflow at:

`.github/workflows/ci.yml`

The workflow validates the Docker Compose configuration and builds the microservice images.

A successful workflow run demonstrates automated build validation, not complete integration testing or production deployment.

## Prototype Limitations

This is an educational proof of concept rather than a production-ready e-commerce system.

The prototype does not implement:

- Real payment processing
- A complete compensating saga
- Production-grade persistent databases
- Actual email or push notification delivery
- Comprehensive automated integration and performance tests
- Production deployment

## Repository

https://github.com/jawad3g1-jpg/maltashop-soa-microservices
