# MaltaShop — SOA and Microservices

## 1. Project Overview

MaltaShop is a prototype e-commerce system developed using Service-Oriented Architecture (SOA) and microservices principles. It separates order processing and inventory management into two independent services.

## 2. Architecture

The project contains two microservices:

- **Order Service:** Accepts customer orders, generates order IDs, and coordinates inventory reservations.
- **Inventory Service:** Maintains product information and stock quantities and supports inventory reservation requests.

The Order Service communicates with the Inventory Service over HTTP.

### Architecture Diagram

```text
Customer / API Client
         |
         v
   Order Service
    Port 8000
         |
         | HTTP request
         v
  Inventory Service
    Port 8001
         |
         v
 Product Inventory
```

## 3. Technologies Used

- Python
- FastAPI
- Uvicorn
- Docker
- Docker Compose
- GitHub Actions
- REST APIs
- OpenAPI / Swagger UI

## 4. Project Structure

```text
maltashop-soa-microservices/
├── .github/
│   └── workflows/
│       └── ci.yml
├── inventory-service/
│   ├── app/
│   ├── Dockerfile
│   └── requirements.txt
├── order-service/
│   ├── app/
│   │   ├── __init__.py
│   │   └── main.py
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml
└── README.md
```

## 5. Prerequisites

Install the following before running the project:

- Docker Desktop
- Git
- A web browser

Ensure Docker Desktop is running before starting the services.

## 6. Running the Application

Open a terminal in the project root directory.

Build and start the services:

```bash
docker compose up --build
```

To run the services in the background:

```bash
docker compose up --build -d
```

To stop the services:

```bash
docker compose down
```

## 7. API Endpoints

### Order Service — Port 8000

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Service home endpoint |
| GET | `/health` | Health check |
| POST | `/orders` | Create an order |

Swagger API documentation:

http://localhost:8000/docs

### Inventory Service — Port 8001

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/inventory` | View available inventory |

Inventory endpoint:

http://localhost:8001/inventory

## 8. Testing and Verification

The following checks have been performed during development:

- Docker Compose configuration validation.
- Successful Docker image builds for both microservices.
- Successful startup of both services.
- Successful health-check responses from both services.
- Inventory endpoint verification.
- Order creation and inventory stock reduction verification.

The order test demonstrated a reduction in T-shirt stock from 50 to 48.

## 9. Continuous Integration

The project includes a GitHub Actions workflow at `.github/workflows/ci.yml`.

The workflow is configured to run on pushes and pull requests targeting the `main` branch. Its current steps include checking out the repository, validating the Docker Compose configuration, and building the microservices.

A successful local build does not, by itself, confirm that the GitHub Actions workflow has passed.

## 10. Current Scope

This project demonstrates a basic microservices implementation with HTTP-based service communication, containerisation, API documentation, and a CI build workflow.

Additional architectural features, such as persistent databases, asynchronous messaging, and automated integration tests, should only be considered implemented when they are present in the source code and have been verified.
