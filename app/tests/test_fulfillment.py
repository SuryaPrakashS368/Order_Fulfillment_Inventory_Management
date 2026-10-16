import pytest

from app.core.constants import Roles
from app.models.role import Role
from app.models.user import User
from app.models.warehouse import Warehouse
from app.models.warehouse_user import WarehouseUser
from app.models.order import Order, OrderStatus, PaymentStatus
from app.models.order_assignment import OrderAssignment


@pytest.fixture
def fulfillment_test_data(db_session):
    # Find or create the admin role.
    admin_role = (
        db_session.query(Role)
        .filter(Role.name == Roles.ADMIN)
        .first()
    )
    if admin_role is None:
        admin_role = Role(name=Roles.ADMIN)
        db_session.add(admin_role)
        db_session.flush()

    # The authenticated_request fixture represents user ID 1.
    admin_user = (
        db_session.query(User)
        .filter(User.id == 1)
        .first()
    )
    if admin_user is None:
        admin_user = User(
            id=1,
            name="Test Admin",
            email="fulfillment.admin@example.com",
            password_hash="test-password-hash",
            role_id=admin_role.id,
            is_active=True,
        )
        db_session.add(admin_user)
        db_session.flush()

    agent_role = (
        db_session.query(Role)
        .filter(Role.name == "Fulfillment Agent")
        .first()
    )
    if agent_role is None:
        agent_role = Role(name="Fulfillment Agent")
        db_session.add(agent_role)
        db_session.flush()

    customer_role = (
        db_session.query(Role)
        .filter(Role.name == "Customer")
        .first()
    )
    if customer_role is None:
        customer_role = Role(name="Customer")
        db_session.add(customer_role)
        db_session.flush()

    agent = User(
        name="Test Fulfillment Agent",
        email="fulfillment.agent@example.com",
        password_hash="test-password-hash",
        role_id=agent_role.id,
        is_active=True,
    )
    wrong_role_user = User(
        name="Test Customer",
        email="fulfillment.customer@example.com",
        password_hash="test-password-hash",
        role_id=customer_role.id,
        is_active=True,
    )
    warehouse = Warehouse(
        name="Fulfillment Test Warehouse",
        location="Madurai",
        capacity=1000,
        is_active=True,
    )

    db_session.add_all([agent, wrong_role_user, warehouse])
    db_session.flush()

    db_session.add_all([
        WarehouseUser(
            warehouse_id=warehouse.id,
            user_id=agent.id,
        ),
        WarehouseUser(
            warehouse_id=warehouse.id,
            user_id=admin_user.id,
        ),
    ])
    db_session.flush()

    order = Order(
        order_number="FULFILLMENT-TEST-001",
        customer_id=admin_user.id,
        warehouse_id=warehouse.id,
        total_amount=200,
        status=OrderStatus.CONFIRMED,
        payment_status=PaymentStatus.PENDING,
    )
    db_session.add(order)
    db_session.flush()

    return {
        "admin": admin_user,
        "agent": agent,
        "wrong_role_user": wrong_role_user,
        "warehouse": warehouse,
        "order": order,
    }


@pytest.fixture
def fulfillment_route_setup(monkeypatch):
    import app.routes.fulfillment as routes

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


def test_assign_fulfillment_agent(
    authenticated_request,
    fulfillment_test_data,
    fulfillment_route_setup,
):
    data = fulfillment_test_data

    response = authenticated_request(
    "POST",
    f"/api/fulfillment/orders/{data['order'].id}/assign",
    json={"agent_id": data["agent"].id},
    _current_user=data["admin"],
)

    assert response.status_code == 201
    result = response.json()
    assert result["order_id"] == data["order"].id
    assert result["agent_id"] == data["agent"].id
    assert result["assigned_by"] == data["admin"].id
    assert "id" in result


def test_assign_agent_to_nonexistent_order(
    authenticated_request,
    fulfillment_test_data,
    fulfillment_route_setup,
):
    data = fulfillment_test_data

    response = authenticated_request(
        "POST",
        "/api/fulfillment/orders/999999/assign",
        json={"agent_id": data["agent"].id},
    )

    assert response.status_code == 404


def test_assign_nonexistent_agent(
    authenticated_request,
    fulfillment_test_data,
    fulfillment_route_setup,
):
    data = fulfillment_test_data

    response = authenticated_request(
        "POST",
        f"/api/fulfillment/orders/{data['order'].id}/assign",
        json={"agent_id": 999999},
    )

    assert response.status_code == 404


def test_assign_user_who_is_not_a_fulfillment_agent(
    authenticated_request,
    fulfillment_test_data,
    fulfillment_route_setup,
):
    data = fulfillment_test_data

    response = authenticated_request(
        "POST",
        f"/api/fulfillment/orders/{data['order'].id}/assign",
        json={"agent_id": data["wrong_role_user"].id},
    )

    assert response.status_code == 400


def test_assign_inactive_fulfillment_agent(
    authenticated_request,
    db_session,
    fulfillment_test_data,
    fulfillment_route_setup,
):
    data = fulfillment_test_data
    data["agent"].is_active = False
    db_session.flush()

    response = authenticated_request(
        "POST",
        f"/api/fulfillment/orders/{data['order'].id}/assign",
        json={"agent_id": data["agent"].id},
    )

    assert response.status_code == 400


def test_assign_agent_to_pending_order(
    authenticated_request,
    db_session,
    fulfillment_test_data,
    fulfillment_route_setup,
):
    data = fulfillment_test_data
    data["order"].status = OrderStatus.PENDING
    db_session.flush()

    response = authenticated_request(
        "POST",
        f"/api/fulfillment/orders/{data['order'].id}/assign",
        json={"agent_id": data["agent"].id},
    )

    assert response.status_code == 409


def test_assign_agent_not_assigned_to_warehouse(
    authenticated_request,
    db_session,
    fulfillment_test_data,
    fulfillment_route_setup,
):
    data = fulfillment_test_data

    assignment = (
        db_session.query(WarehouseUser)
        .filter(
            WarehouseUser.warehouse_id == data["warehouse"].id,
            WarehouseUser.user_id == data["agent"].id,
        )
        .first()
    )
    db_session.delete(assignment)
    db_session.flush()

    response = authenticated_request(
        "POST",
        f"/api/fulfillment/orders/{data['order'].id}/assign",
        json={"agent_id": data["agent"].id},
    )

    assert response.status_code == 400


def test_assign_same_agent_twice(
    authenticated_request,
    db_session,
    fulfillment_test_data,
    fulfillment_route_setup,
):
    data = fulfillment_test_data

    existing = OrderAssignment(
        order_id=data["order"].id,
        agent_id=data["agent"].id,
        assigned_by=data["admin"].id,
    )
    db_session.add(existing)
    db_session.flush()

    response = authenticated_request(
        "POST",
        f"/api/fulfillment/orders/{data['order'].id}/assign",
        json={"agent_id": data["agent"].id},
    )

    assert response.status_code == 409


def test_assign_agent_with_invalid_payload(
    authenticated_request,
    fulfillment_test_data,
    fulfillment_route_setup,
):
    data = fulfillment_test_data

    response = authenticated_request(
        "POST",
        f"/api/fulfillment/orders/{data['order'].id}/assign",
        json={"agent_id": 0},
    )

    assert response.status_code == 422


def test_list_order_assignments(
    authenticated_request,
    db_session,
    fulfillment_test_data,
    fulfillment_route_setup,
):
    data = fulfillment_test_data

    assignment = OrderAssignment(
        order_id=data["order"].id,
        agent_id=data["agent"].id,
        assigned_by=data["admin"].id,
    )
    db_session.add(assignment)
    db_session.flush()

    response = authenticated_request(
        "GET",
        f"/api/fulfillment/orders/{data['order'].id}/assignments",
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert any(
        item["agent_id"] == data["agent"].id
        for item in response.json()
    )


def test_list_assignments_for_nonexistent_order(
    authenticated_request,
    fulfillment_test_data,
    fulfillment_route_setup,
):
    response = authenticated_request(
        "GET",
        "/api/fulfillment/orders/999999/assignments",
    )

    assert response.status_code == 404
