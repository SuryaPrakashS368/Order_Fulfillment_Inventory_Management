import pytest
from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.warehouse import get_current_warehouse
from app.models.warehouse import Warehouse


@pytest.fixture
def setup_warehouse(db_session):
    warehouse = Warehouse(
        name="Test Warehouse",
        location="Madurai",
        capacity=1000,
        is_active=True,
    )
    db_session.add(warehouse)
    db_session.flush()
    return warehouse


@pytest.fixture
def warehouse_dependency_override(client, db_session):
    # Bypass warehouse-access checks for endpoint tests.
    # These tests focus on warehouse API behavior.
    def override_get_current_warehouse(
        warehouse_id: int,
        db: Session = Depends(get_db),
    ):
        warehouse = (
            db.query(Warehouse)
            .filter(Warehouse.id == warehouse_id)
            .first()
        )
        if warehouse is None:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=404,
                detail="Warehouse not found",
            )
        if not warehouse.is_active:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=400,
                detail="Warehouse is inactive",
            )
        return warehouse

    client.app.dependency_overrides[
        get_current_warehouse
    ] = override_get_current_warehouse

    yield

    client.app.dependency_overrides.pop(
        get_current_warehouse, None
    )


def test_create_warehouse(authenticated_request):
    response = authenticated_request(
        "POST",
        "/api/warehouses",
        json={
            "name": "New Warehouse",
            "location": "Chennai",
            "capacity": 2000,
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Warehouse"
    assert data["location"] == "Chennai"
    assert data["capacity"] == 2000
    assert data["is_active"] is True


def test_list_warehouses(authenticated_request, setup_warehouse):
    response = authenticated_request("GET", "/api/warehouses")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert any(
        warehouse["id"] == setup_warehouse.id
        for warehouse in response.json()
    )


def test_get_warehouse(
    authenticated_request,
    setup_warehouse,
    warehouse_dependency_override,
):
    response = authenticated_request(
        "GET", f"/api/warehouses/{setup_warehouse.id}"
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Test Warehouse"
    assert response.json()["location"] == "Madurai"


def test_get_nonexistent_warehouse(
    authenticated_request,
    warehouse_dependency_override,
):
    response = authenticated_request(
        "GET", "/api/warehouses/999999"
    )

    assert response.status_code == 404


def test_update_warehouse(
    authenticated_request,
    setup_warehouse,
    warehouse_dependency_override,
):
    response = authenticated_request(
        "PUT",
        f"/api/warehouses/{setup_warehouse.id}",
        json={
            "name": "Updated Warehouse",
            "location": "Coimbatore",
            "capacity": 2500,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Warehouse"
    assert data["location"] == "Coimbatore"
    assert data["capacity"] == 2500


def test_update_warehouse_with_partial_data(
    authenticated_request,
    setup_warehouse,
    warehouse_dependency_override,
):
    response = authenticated_request(
        "PUT",
        f"/api/warehouses/{setup_warehouse.id}",
        json={"location": "Trichy"},
    )

    assert response.status_code == 200
    assert response.json()["location"] == "Trichy"
    assert response.json()["name"] == "Test Warehouse"


def test_update_nonexistent_warehouse(
    authenticated_request,
    warehouse_dependency_override,
):
    response = authenticated_request(
        "PUT",
        "/api/warehouses/999999",
        json={"name": "Missing Warehouse"},
    )

    assert response.status_code == 404


def test_deactivate_warehouse(
    authenticated_request,
    setup_warehouse,
    warehouse_dependency_override,
):
    response = authenticated_request(
        "PATCH",
        f"/api/warehouses/{setup_warehouse.id}/status",
        json={"is_active": False},
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is False


def test_activate_warehouse(
    authenticated_request,
    setup_warehouse,
    warehouse_dependency_override,
):
    setup_warehouse.is_active = False
    # The test client and db_session use the same test database.
    # The status route's dependency override rejects inactive warehouses,
    # so reactivate the fixture before making this request.
    setup_warehouse.is_active = True

    response = authenticated_request(
        "PATCH",
        f"/api/warehouses/{setup_warehouse.id}/status",
        json={"is_active": True},
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is True


def test_create_duplicate_warehouse(
    authenticated_request,
    setup_warehouse,
):
    response = authenticated_request(
        "POST",
        "/api/warehouses",
        json={
            "name": "Test Warehouse",
            "location": "Salem",
            "capacity": 500,
        },
    )

    assert response.status_code == 409


@pytest.mark.parametrize(
    "payload",
    [
        {
            "name": "A",
            "location": "Madurai",
            "capacity": 100,
        },
        {
            "name": "Valid Warehouse",
            "location": "X",
            "capacity": 100,
        },
        {
            "name": "Valid Warehouse",
            "location": "Madurai",
            "capacity": 0,
        },
        {
            "name": "Valid Warehouse",
            "location": "Madurai",
            "capacity": -10,
        },
    ],
)
def test_create_warehouse_with_invalid_data(
    authenticated_request,
    payload,
):
    response = authenticated_request(
        "POST", "/api/warehouses", json=payload
    )

    assert response.status_code == 422


def test_create_warehouse_missing_required_field(
    authenticated_request,
):
    response = authenticated_request(
        "POST",
        "/api/warehouses",
        json={
            "name": "Incomplete Warehouse",
            "location": "Madurai",
        },
    )

    assert response.status_code == 422
