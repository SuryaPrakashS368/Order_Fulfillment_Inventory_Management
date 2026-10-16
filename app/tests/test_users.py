import pytest

from app.models.role import Role
from app.models.user import User
from app.core.security import hash_password



import pytest

from app.models.role import Role
from app.models.user import User


@pytest.fixture
def setup_user(db_session):
    """Create test roles and an admin user."""

    admin_role = (
        db_session.query(Role)
        .filter(Role.name == "Admin")
        .first()
    )

    if admin_role is None:
        admin_role = Role(name="Admin")
        db_session.add(admin_role)
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
            password_hash=hash_password("test_password"),
            role_id=admin_role.id,
            is_active=True,
        )
        db_session.add(user)
        db_session.flush()

    return user


def test_create_user(authenticated_request, setup_user):
    response = authenticated_request(
        "POST",
        "/api/users",
        json={
            "name": "Test Customer",
            "email": "customer_test@example.com",
            "password": "CustomerPass123!",
            "role": "Customer",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Customer"
    assert data["email"] == "customer_test@example.com"
    assert data["role"] == "Customer"
    assert data["is_active"] is True


def test_list_users(authenticated_request, setup_user):
    response = authenticated_request(
        "GET",
        "/api/users",
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert any(
        user["email"] == "admin_test@example.com"
        for user in response.json()
    )


def test_get_user(authenticated_request, setup_user):
    response = authenticated_request(
        "GET",
        f"/api/users/{setup_user.id}",
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == setup_user.id
    assert data["email"] == "admin_test@example.com"

def test_get_nonexistent_user(authenticated_request, setup_user):
    response = authenticated_request(
        "GET",
        "/api/users/999999",
    )

    assert response.status_code == 404


def test_update_user(authenticated_request, setup_user):
    response = authenticated_request(
        "PUT",
        f"/api/users/{setup_user.id}",
        json={
            "name": "Updated Admin",
            "email": "updated_admin@example.com",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Updated Admin"
    assert data["email"] == "updated_admin@example.com"


def test_deactivate_user(authenticated_request, setup_user):
    response = authenticated_request(
        "PATCH",
        f"/api/users/{setup_user.id}/status",
        json={"is_active": False},
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is False


def test_create_user_with_duplicate_email(
    authenticated_request,
    setup_user,
):
    response = authenticated_request(
        "POST",
        "/api/users",
        json={
            "name": "Duplicate Admin",
            "email": "admin_test@example.com",
            "password": "AnotherPass123!",
            "role": "Customer",
        },
    )

    assert response.status_code == 409
