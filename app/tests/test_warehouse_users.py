import pytest
from app.models.role import Role
from app.models.user import User
from app.models.warehouse import Warehouse
from app.models.warehouse_user import WarehouseUser


@pytest.fixture
def setup_warehouse(db_session):
    warehouse = Warehouse(
        name="Warehouse User Test",
        location="Madurai",
        capacity=1000,
        is_active=True,
    )
    db_session.add(warehouse)
    db_session.flush()
    return warehouse



@pytest.fixture
def setup_user(db_session):
    # Find the Admin role instead of assuming its ID is 1.
    admin_role = (
        db_session.query(Role)
        .filter(Role.name == "Admin")
        .first()
    )

    # Create the role if it does not exist.
    if admin_role is None:
        admin_role = Role(name="Admin")
        db_session.add(admin_role)
        db_session.flush()

    user = User(
        name="Warehouse Test User",
        email="warehouse.test@example.com",
        password_hash="test-password-hash",
        role_id=admin_role.id,
        is_active=True,
    )

    db_session.add(user)
    db_session.flush()

    return user



def test_assign_user_to_warehouse(
    authenticated_request,
    setup_warehouse,
    setup_user,
):
    response = authenticated_request(
        "POST",
        f"/api/warehouses/{setup_warehouse.id}/users",
        json={"user_id": setup_user.id},
    )

    assert response.status_code == 201

    data = response.json()
    assert data["message"] == "User assigned to warehouse successfully"
    assert data["warehouse_id"] == setup_warehouse.id
    assert data["user_id"] == setup_user.id
    assert "id" in data


def test_assign_user_to_nonexistent_warehouse(
    authenticated_request,
    setup_user,
):
    response = authenticated_request(
        "POST",
        "/api/warehouses/999999/users",
        json={"user_id": setup_user.id},
    )

    assert response.status_code == 404


def test_assign_nonexistent_user_to_warehouse(
    authenticated_request,
    setup_warehouse,
):
    response = authenticated_request(
        "POST",
        f"/api/warehouses/{setup_warehouse.id}/users",
        json={"user_id": 999999},
    )

    assert response.status_code == 404


def test_assign_same_user_twice(
    authenticated_request,
    db_session,
    setup_warehouse,
    setup_user,
):
    # Create the existing assignment first.
    assignment = WarehouseUser(
        warehouse_id=setup_warehouse.id,
        user_id=setup_user.id,
    )
    db_session.add(assignment)
    db_session.flush()

    response = authenticated_request(
        "POST",
        f"/api/warehouses/{setup_warehouse.id}/users",
        json={"user_id": setup_user.id},
    )

    assert response.status_code == 409


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"user_id": 0},
        {"user_id": -1},
        {"user_id": "invalid"},
    ],
)
def test_assign_user_with_invalid_payload(
    authenticated_request,
    setup_warehouse,
    payload,
):
    response = authenticated_request(
        "POST",
        f"/api/warehouses/{setup_warehouse.id}/users",
        json=payload,
    )

    assert response.status_code == 422
