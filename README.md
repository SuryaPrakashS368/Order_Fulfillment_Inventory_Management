# Order Fulfillment & Inventory Management Platform

A backend API for managing products, warehouses, inventory, customer orders, order fulfillment, payments, returns, notifications, and audit logs.

The system is built using **Python, FastAPI, PostgreSQL, SQLAlchemy, Alembic, JWT Authentication, and Role-Based Access Control (RBAC)**.

---

## 📌 Project Overview

The system provides:

- User Registration & Login
- JWT Authentication
- Access & Refresh Tokens
- User Management
- Role-Based Authorization
- Product Management
- Category Management
- Warehouse Management
- Warehouse User Assignment
- Inventory Management
- Stock Availability Tracking
- Inventory Reservations
- Order Management
- Order Items Management
- Order Status Management
- Order Status History
- Order Fulfillment
- Payment Management
- Returns & Refunds
- Notifications
- Audit Logs
- Dashboard Summary
- Search & Filtering
- Sorting & Pagination
- Database Transactions
- Automated Testing
- Swagger API Documentation

The application supports four main roles:

- **Admin**
- **Warehouse Manager**
- **Fulfillment Agent**
- **Customer**

---

## 🚀 Features

- User Registration & Login
- JWT Authentication
- Access Token & Refresh Token Management
- Password Hashing
- Role-Based Access Control
- Permission-Based Authorization
- User Activation & Deactivation
- Product and Category Management
- Warehouse Management
- Warehouse User Assignment
- Inventory Tracking
- Inventory Reservation
- Stock Availability Validation
- Order Creation & Management
- Order Item Management
- Order Status Transitions
- Order Status History
- Fulfillment Processing
- Payment Processing Records
- Return & Refund Management
- Notifications
- Audit Logging
- Dashboard Summary
- Database Transaction Management
- Data Validation
- Error Handling
- Search & Filtering
- Sorting
- Pagination
- Alembic Database Migrations
- Pytest Automated Testing
- Swagger API Documentation

---

## 🛠️ Technologies

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Pydantic
- JWT Authentication
- Uvicorn
- Psycopg
- Python-JOSE
- Passlib
- Bcrypt
- Pytest
- HTTPX


## 📂 Project Structure

```text
Order_Fulfillment_Inventory_Management/
│
├── app/
│   │
│   ├── main.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── security.py
│   │   ├── permissions.py
│   │   └── exceptions.py
│   │
│   ├── dependencies/
│   │   ├── auth.py
│   │   └── authorization.py
│   │
│   ├── models/
│   │   ├── user.py
│   │   ├── role.py
│   │   ├── permission.py
│   │   ├── role_permission.py
│   │   ├── refresh_token.py
│   │   ├── product.py
│   │   ├── category.py
│   │   ├── warehouse.py
│   │   ├── warehouse_user.py
│   │   ├── inventory.py
│   │   ├── inventory_transaction.py
│   │   ├── order.py
│   │   ├── order_item.py
│   │   ├── order_status_history.py
│   │   ├── fulfillment.py
│   │   ├── payment.py
│   │   ├── return.py
│   │   ├── notification.py
│   │   └── audit_log.py
│   │
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── category.py
│   │   ├── warehouse.py
│   │   ├── inventory.py
│   │   ├── order.py
│   │   ├── order_item.py
│   │   ├── fulfillment.py
│   │   ├── payment.py
│   │   ├── return.py
│   │   ├── notification.py
│   │   └── audit_log.py
│   │
│   ├── Crud/
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── category.py
│   │   ├── warehouse.py
│   │   ├── inventory.py
│   │   ├── order.py
│   │   ├── fulfillment.py
│   │   ├── payment.py
│   │   ├── notification.py
│   │   └── audit_log.py
│   │
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── inventory_service.py
│   │   ├── order_service.py
│   │   ├── fulfillment_service.py
│   │   ├── payment_service.py
│   │   ├── notification_service.py
│   │   └── audit_log_service.py
│   │
│   └── routes/
│       ├── auth.py
│       ├── users.py
│       ├── products.py
│       ├── categories.py
│       ├── warehouses.py
│       ├── inventory.py
│       ├── orders.py
│       ├── fulfillment.py
│       ├── payments.py
│       ├── returns.py
│       ├── notifications.py
│       ├── audit_logs.py
│       └── dashboard.py
│
├── alembic/
│   ├── env.py
│   └── versions/
│
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_users.py
│   ├── test_authorization.py
│   ├── test_products.py
│   ├── test_warehouses.py
│   ├── test_inventory.py
│   ├── test_orders.py
│   ├── test_fulfillment.py
│   ├── test_payments.py
│   ├── test_notifications.py
│   ├── test_audit_logs.py
│   └── test_dashboard.py
│
├── .env
├── .env.example
├── .gitignore
├── alembic.ini
├── requirements.txt
└── README.md
```

*Note: The structure above is a documentation template. Keep only the filenames and directories that exist in your actual project.*

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone <repository-url>

cd Order_Fulfillment_Inventory_Management
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

**Windows PowerShell**

```powershell
.\venv\Scripts\Activate.ps1
```

If script execution is blocked, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

.\venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
python -m pip install --upgrade pip

pip install -r requirements.txt
```

### 5. Configure PostgreSQL

Create the project database in PostgreSQL.

```sql
CREATE DATABASE order_fulfillment_db;
```

Update your `.env` file with the database connection and security settings.

Example:

```env
APP_NAME=Order Fulfillment & Inventory Management Platform
APP_VERSION=1.0.0
DEBUG=True

DATABASE_URL=postgresql://postgres:password@localhost:5432/order_fulfillment_db

JWT_SECRET_KEY=your-long-random-secret-key
JWT_ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

Use the exact environment variable names expected by your application's configuration module.

**Security:** Replace the example password and JWT secret with your own values. Never commit real credentials or the `.env` file to GitHub.

### 6. Run database migrations

```bash
alembic upgrade head
```

Check the current migration:

```bash
alembic current
```

View migration history:

```bash
alembic history
```

### 7. Start the application

```bash
uvicorn app.main:app --reload
```

The API should be available at:

```text
http://127.0.0.1:8000
```

---

## 🧪 Running Tests

Run the complete test suite:

```bash
pytest -v
```

Run authentication tests:

```bash
pytest tests/test_auth.py -v
```

Run authorization tests:

```bash
pytest tests/test_authorization.py -v
```

Run inventory tests:

```bash
pytest tests/test_inventory.py -v
```

Run order tests:

```bash
pytest tests/test_orders.py -v
```

Run fulfillment tests:

```bash
pytest tests/test_fulfillment.py -v
```

Run payment tests:

```bash
pytest tests/test_payments.py -v
```

Run a specific test function:

```bash
pytest tests/test_orders.py::test_order_creation -v
```

Use the actual test filenames and test function names in your project. Configure a separate test database where required, and ensure the test suite does not modify production data.

---

## 📖 API Documentation

### Swagger UI

```text
http://127.0.0.1:8000/docs
```

### ReDoc

```text
http://127.0.0.1:8000/redoc
```

### OpenAPI Schema

```text
http://127.0.0.1:8000/openapi.json
```

Swagger UI can be used to inspect endpoints, provide authentication credentials, submit requests, and review response schemas.

---


## 🛠️ Common Commands

Start the development server:

```bash
uvicorn app.main:app --reload
```

Apply database migrations:

```bash
alembic upgrade head
```

Check the migration revision:

```bash
alembic current
```

View migration history:

```bash
alembic history
```

Run the complete test suite:

```bash
pytest -v
```

Run tests with a short summary:

```bash
pytest -ra
```


## 👨‍💻 Author

**Surya Prakash S**
