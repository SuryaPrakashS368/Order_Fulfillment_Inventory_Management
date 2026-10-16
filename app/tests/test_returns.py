import pytest
from types import SimpleNamespace
from datetime import datetime
from decimal import Decimal

from app.core.security import hash_password
from app.models.role import Role
from app.models.user import User
from app.models.category import Category
from app.models.product import Product
from app.models.warehouse import Warehouse
from app.models.order import Order, OrderStatus, PaymentStatus
from app.models.order_item import OrderItem
from app.models.return_model import Return, ReturnStatus
from app.models.return_item import ReturnItem


@pytest.fixture
def return_test_data(db_session):
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
        .filter(
            User.email == "admin_test@example.com"
        )
        .first()
    )

    if user is None:
        user = User(
        name="Test Admin",
        email="admin_test@example.com",
        password_hash=hash_password("test_password"),
        role_id=role.id,
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()

    category = Category(
        name="Return Test Category",
        description="Test category",
    )
    warehouse = Warehouse(
        name="Return Test Warehouse",
        location="Madurai",
        capacity=1000,
        is_active=True,
    )

    db_session.add_all([category, warehouse])
    db_session.flush()

    product = Product(
        sku="RETURN-TEST-SKU-001",
        name="Return Test Product",
        category_id=category.id,
        price=100,
        cost_price=60,
        is_active=True,
    )
    db_session.add(product)
    db_session.flush()

    order = Order(
        order_number="RETURN-TEST-ORDER-001",
        customer_id=user.id,
        warehouse_id=warehouse.id,
        total_amount=200,
        status=OrderStatus.DELIVERED,
        payment_status=PaymentStatus.PAID,
    )
    db_session.add(order)
    db_session.flush()

    order_item = OrderItem(
        order_id=order.id,
        product_id=product.id,
        quantity=2,
        unit_price=100,
        discount=0,
        tax=0,
        total=200,
    )
    db_session.add(order_item)
    db_session.flush()

    return {
        "user": user,
        "warehouse": warehouse,
        "product": product,
        "order": order,
        "order_item": order_item,
    }


@pytest.fixture
def setup_return(db_session, return_test_data):
    data = return_test_data

    return_record = Return(
        order_id=data["order"].id,
        customer_id=data["user"].id,
        status=ReturnStatus.REQUESTED,
        reason="Product was damaged",
        refund_amount=Decimal("100.00"),
    )
    db_session.add(return_record)
    db_session.flush()

    return_item = ReturnItem(
        return_id=return_record.id,
        order_item_id=data["order_item"].id,
        quantity=1,
        restocked=False,
    )
    db_session.add(return_item)
    db_session.flush()

    return return_record


@pytest.fixture
def return_route_mocks(monkeypatch):
    import app.routes.returns as routes

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

    return routes


def test_create_return(
    authenticated_request,
    return_test_data,
    return_route_mocks,
):
    data = return_test_data

    response = authenticated_request(
        "POST",
        "/api/returns",
        json={
            "order_id": data["order"].id,
            "reason": "Product was damaged",
            "items": [
                {
                    "order_item_id": data["order_item"].id,
                    "quantity": 1,
                }
            ],
        },
    )

    assert response.status_code == 201

    result = response.json()
    assert result["order_id"] == data["order"].id
    assert result["customer_id"] == data["user"].id
    assert result["status"] == "REQUESTED"
    assert result["reason"] == "Product was damaged"
    assert len(result["items"]) == 1
    assert result["items"][0]["quantity"] == 1


def test_create_return_invalid_order_id(
    authenticated_request,
    return_test_data,
):
    response = authenticated_request(
        "POST",
        "/api/returns",
        json={
            "order_id": 0,
            "reason": "Product was damaged",
            "items": [
                {"order_item_id": 1, "quantity": 1}
            ],
        },
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "payload",
    [
        {
            "order_id": 1,
            "reason": "x",
            "items": [{"order_item_id": 1, "quantity": 1}],
        },
        {
            "order_id": 1,
            "reason": "Product was damaged",
            "items": [],
        },
        {
            "order_id": 1,
            "reason": "Product was damaged",
            "items": [{"order_item_id": 1, "quantity": 0}],
        },
        {
            "order_id": 1,
            "reason": "Product was damaged",
            "items": [{"order_item_id": 0, "quantity": 1}],
        },
        {
            "order_id": 1,
            "reason": "Product was damaged",
        },
    ],
)
def test_create_return_invalid_payload(
    authenticated_request,
    payload,
):
    response = authenticated_request(
        "POST",
        "/api/returns",
        json=payload,
    )

    assert response.status_code == 422


def test_create_return_for_missing_order(
    authenticated_request,
    return_test_data,
):
    data = return_test_data

    response = authenticated_request(
        "POST",
        "/api/returns",
        json={
            "order_id": 999999,
            "reason": "Product was damaged",
            "items": [
                {
                    "order_item_id": data["order_item"].id,
                    "quantity": 1,
                }
            ],
        },
    )

    assert response.status_code == 404


def test_create_return_exceeding_order_quantity(
    authenticated_request,
    return_test_data,
):
    data = return_test_data

    response = authenticated_request(
        "POST",
        "/api/returns",
        json={
            "order_id": data["order"].id,
            "reason": "Product was damaged",
            "items": [
                {
                    "order_item_id": data["order_item"].id,
                    "quantity": 3,
                }
            ],
        },
    )

    assert response.status_code == 409


def test_list_returns(
    authenticated_request,
    setup_return,
    return_route_mocks,
):
    response = authenticated_request(
        "GET",
        "/api/returns",
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert any(
        item["id"] == setup_return.id
        for item in response.json()
    )


def test_get_return(
    authenticated_request,
    setup_return,
):
    response = authenticated_request(
        "GET",
        f"/api/returns/{setup_return.id}",
    )

    assert response.status_code == 200
    assert response.json()["id"] == setup_return.id
    assert response.json()["status"] == "REQUESTED"


def test_get_missing_return(
    authenticated_request,
):
    response = authenticated_request(
        "GET",
        "/api/returns/999999",
    )

    assert response.status_code == 404


def test_approve_return(
    authenticated_request,
    setup_return,
    return_route_mocks,
):
    response = authenticated_request(
        "POST",
        f"/api/returns/{setup_return.id}/approve",
        json={"reason": "Return approved"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "APPROVED"


def test_approve_missing_return(
    authenticated_request,
):
    response = authenticated_request(
        "POST",
        "/api/returns/999999/approve",
        json={"reason": "Return approved"},
    )

    assert response.status_code == 404


def test_reject_return(
    authenticated_request,
    setup_return,
    return_route_mocks,
):
    response = authenticated_request(
        "POST",
        f"/api/returns/{setup_return.id}/reject",
        json={"reason": "Return does not meet policy"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "REJECTED"


def test_receive_return_before_approval(
    authenticated_request,
    setup_return,
):
    response = authenticated_request(
        "POST",
        f"/api/returns/{setup_return.id}/receive",
    )

    assert response.status_code == 409


def test_receive_missing_return(
    authenticated_request,
):
    response = authenticated_request(
        "POST",
        "/api/returns/999999/receive",
    )

    assert response.status_code == 404


def test_refund_return_before_receiving(
    authenticated_request,
    setup_return,
):
    response = authenticated_request(
        "POST",
        f"/api/returns/{setup_return.id}/refund",
    )

    assert response.status_code == 409


def test_refund_missing_return(
    authenticated_request,
):
    response = authenticated_request(
        "POST",
        "/api/returns/999999/refund",
    )

    assert response.status_code == 404
