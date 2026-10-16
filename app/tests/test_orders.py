import pytest

from app.models.role import Role
from app.models.user import User
from app.models.category import Category
from app.models.product import Product
from app.models.warehouse import Warehouse
from app.models.inventory import Inventory
from app.models.order import Order, OrderStatus, PaymentStatus
from app.models.order_item import OrderItem
from app.models.order_status_history import OrderStatusHistory



@pytest.fixture
def order_test_data(db_session):
    # Use the same Admin role and user as authenticated_request.
    role = (
        db_session.query(Role)
        .filter(Role.name == "Admin")
        .first()
    )

    if role is None:
        role = Role(name="Admin")
        db_session.add(role)
        db_session.flush()

    user = (
        db_session.query(User)
        .filter(User.email == "admin_test@example.com")
        .first()
    )

    if user is None:
        user = User(
            name="Test Admin",
            email="admin_test@example.com",
            password_hash="test-password-hash",
            role_id=role.id,
            is_active=True,
        )
        db_session.add(user)
        db_session.flush()
    else:
        # Keep the existing test user's role consistent.
        user.role_id = role.id
        db_session.flush()

    category = Category(
        name="Order Test Category",
        description="Category for order tests",
    )

    warehouse = Warehouse(
        name="Order Test Warehouse",
        location="Madurai",
        capacity=1000,
        is_active=True,
    )

    db_session.add_all([category, warehouse])
    db_session.flush()

    product = Product(
        sku="ORDER-TEST-SKU-001",
        name="Order Test Product",
        category_id=category.id,
        price=100,
        cost_price=60,
        is_active=True,
    )

    db_session.add(product)
    db_session.flush()

    inventory = Inventory(
        product_id=product.id,
        warehouse_id=warehouse.id,
        available_quantity=100,
        reserved_quantity=0,
        damaged_quantity=0,
        reorder_level=10,
    )

    db_session.add(inventory)
    db_session.flush()

    return {
        "user": user,
        "product": product,
        "warehouse": warehouse,
        "inventory": inventory,
    }


@pytest.fixture
def setup_order(db_session, order_test_data):
    data = order_test_data

    order = Order(
        order_number="ORD-TEST-0001",
        customer_id=data["user"].id,
        warehouse_id=data["warehouse"].id,
        total_amount=200,
        status=OrderStatus.PENDING,
        payment_status=PaymentStatus.PENDING,
    )
    db_session.add(order)
    db_session.flush()

    item = OrderItem(
        order_id=order.id,
        product_id=data["product"].id,
        quantity=2,
        unit_price=100,
        discount=0,
        tax=0,
        total=200,
    )
    db_session.add(item)

    history = OrderStatusHistory(
        order_id=order.id,
        from_status=None,
        to_status=OrderStatus.PENDING,
        changed_by=data["user"].id,
        reason="Order created",
    )
    db_session.add(history)
    db_session.flush()

    return order


def test_create_order_requires_idempotency_key(
    authenticated_request,
    order_test_data,
):
    data = order_test_data

    response = authenticated_request(
        "POST",
        "/api/orders",
        json={
            "warehouse_id": data["warehouse"].id,
            "items": [
                {
                    "product_id": data["product"].id,
                    "quantity": 2,
                }
            ],
        },
    )

    assert response.status_code == 400

    body = response.json()
    error_message = (
        body.get("detail")
        or body.get("error", {}).get("message", "")
    )

    assert "Idempotency-Key" in error_message


def test_create_order(
    authenticated_request,
    order_test_data,
    monkeypatch,
):
    import app.routes.orders as routes

    monkeypatch.setattr(
        routes,
        "create_audit_log_service",
        lambda **kwargs: None,
    )
    monkeypatch.setattr(
        routes,
        "create_notification_service",
        lambda **kwargs: None,
    )

    data = order_test_data

    response = authenticated_request(
        "POST",
        "/api/orders",
        headers={"Idempotency-Key": "order-test-key-001"},
        json={
            "warehouse_id": data["warehouse"].id,
            "items": [
                {
                    "product_id": data["product"].id,
                    "quantity": 2,
                }
            ],
        },
    )

    assert response.status_code == 201
    result = response.json()
    assert result["customer_id"] == data["user"].id
    assert result["warehouse_id"] == data["warehouse"].id
    assert float(result["total_amount"]) == 200
    assert result["status"] == "PENDING"
    assert len(result["items"]) == 1
    assert result["items"][0]["quantity"] == 2


def test_create_order_with_invalid_quantity(
    authenticated_request,
    order_test_data,
):
    data = order_test_data

    response = authenticated_request(
        "POST",
        "/api/orders",
        headers={"Idempotency-Key": "order-invalid-quantity"},
        json={
            "warehouse_id": data["warehouse"].id,
            "items": [
                {
                    "product_id": data["product"].id,
                    "quantity": 0,
                }
            ],
        },
    )

    assert response.status_code == 422


def test_create_order_with_missing_items(
    authenticated_request,
    order_test_data,
):
    data = order_test_data

    response = authenticated_request(
        "POST",
        "/api/orders",
        headers={"Idempotency-Key": "order-missing-items"},
        json={
            "warehouse_id": data["warehouse"].id,
            "items": [],
        },
    )

    assert response.status_code == 422


def test_create_order_with_nonexistent_product(
    authenticated_request,
    order_test_data,
):
    data = order_test_data

    response = authenticated_request(
        "POST",
        "/api/orders",
        headers={"Idempotency-Key": "order-missing-product"},
        json={
            "warehouse_id": data["warehouse"].id,
            "items": [
                {"product_id": 999999, "quantity": 1}
            ],
        },
    )

    assert response.status_code == 404


def test_create_order_with_nonexistent_warehouse(
    authenticated_request,
    order_test_data,
):
    data = order_test_data

    response = authenticated_request(
        "POST",
        "/api/orders",
        headers={"Idempotency-Key": "order-missing-warehouse"},
        json={
            "warehouse_id": 999999,
            "items": [
                {
                    "product_id": data["product"].id,
                    "quantity": 1,
                }
            ],
        },
    )

    assert response.status_code == 404


def test_create_order_with_insufficient_inventory(
    authenticated_request,
    order_test_data,
):
    data = order_test_data

    response = authenticated_request(
        "POST",
        "/api/orders",
        headers={"Idempotency-Key": "order-insufficient-stock"},
        json={
            "warehouse_id": data["warehouse"].id,
            "items": [
                {
                    "product_id": data["product"].id,
                    "quantity": 1000,
                }
            ],
        },
    )

    assert response.status_code == 409


def test_list_orders(
    authenticated_request,
    order_test_data,
    setup_order,
):
    response = authenticated_request("GET", "/api/orders")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert any(
        item["id"] == setup_order.id
        for item in response.json()
    )


def test_filter_orders_by_status(
    authenticated_request,
    order_test_data,
    setup_order,
):
    response = authenticated_request(
        "GET",
        "/api/orders?status=PENDING",
    )

    assert response.status_code == 200
    assert all(
        item["status"] == "PENDING"
        for item in response.json()
    )


def test_filter_orders_by_invalid_status(
    authenticated_request,
    order_test_data,
):
    response = authenticated_request(
        "GET",
        "/api/orders?status=INVALID_STATUS",
    )

    assert response.status_code == 422


def test_list_orders_invalid_pagination(
    authenticated_request,
    order_test_data,
):
    response = authenticated_request(
        "GET",
        "/api/orders?skip=-1",
    )

    assert response.status_code == 422


def test_get_order(
    authenticated_request,
    order_test_data,
    setup_order,
):
    response = authenticated_request(
        "GET",
        f"/api/orders/{setup_order.id}",
    )

    assert response.status_code == 200
    assert response.json()["id"] == setup_order.id
    assert response.json()["order_number"] == "ORD-TEST-0001"


def test_get_nonexistent_order(
    authenticated_request,
    order_test_data,
):
    response = authenticated_request(
        "GET",
        "/api/orders/999999",
    )

    assert response.status_code == 404


def test_get_order_status_history(
    authenticated_request,
    order_test_data,
    setup_order,
):
    response = authenticated_request(
        "GET",
        f"/api/orders/{setup_order.id}/history",
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert any(
        item["order_id"] == setup_order.id
        for item in response.json()
    )


def test_cancel_order_requires_reason(
    authenticated_request,
    order_test_data,
    setup_order,
):
    response = authenticated_request(
        "POST",
        f"/api/orders/{setup_order.id}/cancel",
        json={"reason": "x"},
    )

    assert response.status_code == 422
