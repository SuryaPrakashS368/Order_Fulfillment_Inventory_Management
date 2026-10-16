import pytest

from app.models.category import Category
from app.models.product import Product
from app.models.warehouse import Warehouse
from app.models.inventory import Inventory


@pytest.fixture
def inventory_test_dependencies(monkeypatch):
    """Keep these tests focused on inventory API behavior."""
    import app.routes.inventory as inventory_routes

    monkeypatch.setattr(
        inventory_routes,
        "get_assignment",
        lambda db, warehouse_id, user_id: object(),
    )

    # Avoid requiring a persisted authenticated user just to test inventory.
    monkeypatch.setattr(
        inventory_routes,
        "create_audit_log_service",
        lambda **kwargs: None,
    )


@pytest.fixture
def setup_category(db_session):
    category = Category(
        name="Inventory Test Category",
        description="Category for inventory tests",
    )
    db_session.add(category)
    db_session.flush()
    return category


@pytest.fixture
def setup_product(db_session, setup_category):
    product = Product(
        sku="INV-TEST-SKU-001",
        name="Inventory Test Product",
        description="Product for inventory tests",
        category_id=setup_category.id,
        price=100,
        cost_price=60,
        is_active=True,
    )
    db_session.add(product)
    db_session.flush()
    return product


@pytest.fixture
def setup_warehouse(db_session):
    warehouse = Warehouse(
        name="Inventory Test Warehouse",
        location="Madurai",
        capacity=1000,
        is_active=True,
    )
    db_session.add(warehouse)
    db_session.flush()
    return warehouse


@pytest.fixture
def setup_inventory(db_session, setup_product, setup_warehouse):
    inventory = Inventory(
        product_id=setup_product.id,
        warehouse_id=setup_warehouse.id,
        available_quantity=50,
        reserved_quantity=0,
        damaged_quantity=0,
        reorder_level=10,
    )
    db_session.add(inventory)
    db_session.flush()
    return inventory


def test_create_inventory(
    authenticated_request,
    setup_product,
    setup_warehouse,
    inventory_test_dependencies,
):
    response = authenticated_request(
        "POST",
        "/api/inventory",
        json={
            "product_id": setup_product.id,
            "warehouse_id": setup_warehouse.id,
            "available_quantity": 50,
            "reorder_level": 10,
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["product_id"] == setup_product.id
    assert data["warehouse_id"] == setup_warehouse.id
    assert data["available_quantity"] == 50
    assert data["reserved_quantity"] == 0
    assert data["damaged_quantity"] == 0
    assert data["reorder_level"] == 10


def test_list_inventory(
    authenticated_request,
    setup_inventory,
    inventory_test_dependencies,
):
    response = authenticated_request("GET", "/api/inventory")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert any(
        item["id"] == setup_inventory.id
        for item in response.json()
    )


def test_filter_inventory_by_product(
    authenticated_request,
    setup_inventory,
    setup_product,
    inventory_test_dependencies,
):
    response = authenticated_request(
        "GET",
        f"/api/inventory?product_id={setup_product.id}",
    )

    assert response.status_code == 200
    assert all(
        item["product_id"] == setup_product.id
        for item in response.json()
    )


def test_filter_inventory_by_warehouse(
    authenticated_request,
    setup_inventory,
    setup_warehouse,
    inventory_test_dependencies,
):
    response = authenticated_request(
        "GET",
        f"/api/inventory?warehouse_id={setup_warehouse.id}",
    )

    assert response.status_code == 200
    assert all(
        item["warehouse_id"] == setup_warehouse.id
        for item in response.json()
    )


def test_get_single_inventory(
    authenticated_request,
    setup_inventory,
    inventory_test_dependencies,
):
    response = authenticated_request(
        "GET",
        f"/api/inventory/{setup_inventory.id}",
    )

    assert response.status_code == 200
    assert response.json()["id"] == setup_inventory.id
    assert response.json()["available_quantity"] == 50


def test_get_nonexistent_inventory(
    authenticated_request,
    inventory_test_dependencies,
):
    response = authenticated_request(
        "GET",
        "/api/inventory/999999",
    )

    assert response.status_code == 404


def test_update_inventory_reorder_level(
    authenticated_request,
    setup_inventory,
    inventory_test_dependencies,
):
    response = authenticated_request(
        "PUT",
        f"/api/inventory/{setup_inventory.id}",
        json={"reorder_level": 20},
    )

    assert response.status_code == 200
    assert response.json()["reorder_level"] == 20
    assert response.json()["available_quantity"] == 50


def test_update_inventory_with_negative_reorder_level(
    authenticated_request,
    setup_inventory,
    inventory_test_dependencies,
):
    response = authenticated_request(
        "PUT",
        f"/api/inventory/{setup_inventory.id}",
        json={"reorder_level": -1},
    )

    assert response.status_code == 422


def test_update_nonexistent_inventory(
    authenticated_request,
    inventory_test_dependencies,
):
    response = authenticated_request(
        "PUT",
        "/api/inventory/999999",
        json={"reorder_level": 5},
    )

    assert response.status_code == 404


def test_create_inventory_for_nonexistent_product(
    authenticated_request,
    setup_warehouse,
    inventory_test_dependencies,
):
    response = authenticated_request(
        "POST",
        "/api/inventory",
        json={
            "product_id": 999999,
            "warehouse_id": setup_warehouse.id,
            "available_quantity": 10,
            "reorder_level": 2,
        },
    )

    assert response.status_code == 404


def test_create_inventory_for_nonexistent_warehouse(
    authenticated_request,
    setup_product,
    inventory_test_dependencies,
):
    response = authenticated_request(
        "POST",
        "/api/inventory",
        json={
            "product_id": setup_product.id,
            "warehouse_id": 999999,
            "available_quantity": 10,
            "reorder_level": 2,
        },
    )

    assert response.status_code == 404


def test_create_duplicate_inventory(
    authenticated_request,
    setup_inventory,
    setup_product,
    setup_warehouse,
    inventory_test_dependencies,
):
    response = authenticated_request(
        "POST",
        "/api/inventory",
        json={
            "product_id": setup_product.id,
            "warehouse_id": setup_warehouse.id,
            "available_quantity": 20,
            "reorder_level": 5,
        },
    )

    assert response.status_code == 409


def test_create_inventory_for_inactive_product(
    authenticated_request,
    db_session,
    setup_product,
    setup_warehouse,
    inventory_test_dependencies,
):
    setup_product.is_active = False
    db_session.flush()

    response = authenticated_request(
        "POST",
        "/api/inventory",
        json={
            "product_id": setup_product.id,
            "warehouse_id": setup_warehouse.id,
            "available_quantity": 10,
            "reorder_level": 2,
        },
    )

    assert response.status_code == 400


def test_create_inventory_for_inactive_warehouse(
    authenticated_request,
    db_session,
    setup_product,
    setup_warehouse,
    inventory_test_dependencies,
):
    setup_warehouse.is_active = False
    db_session.flush()

    response = authenticated_request(
        "POST",
        "/api/inventory",
        json={
            "product_id": setup_product.id,
            "warehouse_id": setup_warehouse.id,
            "available_quantity": 10,
            "reorder_level": 2,
        },
    )

    assert response.status_code == 400


@pytest.mark.parametrize(
    "payload",
    [
        {
            "product_id": 0,
            "warehouse_id": 1,
            "available_quantity": 10,
            "reorder_level": 2,
        },
        {
            "product_id": 1,
            "warehouse_id": 0,
            "available_quantity": 10,
            "reorder_level": 2,
        },
        {
            "product_id": 1,
            "warehouse_id": 1,
            "available_quantity": -1,
            "reorder_level": 2,
        },
        {
            "product_id": 1,
            "warehouse_id": 1,
            "available_quantity": 10,
            "reorder_level": -1,
        },
    ],
)
def test_create_inventory_with_invalid_data(
    authenticated_request,
    payload,
    inventory_test_dependencies,
):
    response = authenticated_request(
        "POST",
        "/api/inventory",
        json=payload,
    )

    assert response.status_code == 422


def test_get_inventory_for_nonexistent_product(
    authenticated_request,
    inventory_test_dependencies,
):
    response = authenticated_request(
        "GET",
        "/api/inventory/product/999999",
    )

    assert response.status_code == 404


def test_get_inventory_for_product(
    authenticated_request,
    setup_inventory,
    setup_product,
    inventory_test_dependencies,
):
    response = authenticated_request(
        "GET",
        f"/api/inventory/product/{setup_product.id}",
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert any(
        item["id"] == setup_inventory.id
        for item in response.json()
    )
