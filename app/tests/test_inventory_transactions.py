import pytest

from app.models.category import Category
from app.models.product import Product
from app.models.warehouse import Warehouse
from app.models.inventory import Inventory
from app.models.inventory_transaction import (
    InventoryTransaction,
    InventoryTransactionType,
)


@pytest.fixture
def transaction_dependencies(monkeypatch):
    import app.routes.inventory_transactions as routes

    # Focus on transaction business logic, not permission assignment.
    monkeypatch.setattr(
        routes,
        "check_warehouse_access",
        lambda db, warehouse_id, current_user: None,
    )

    # Avoid requiring audit-log setup in these tests.
    monkeypatch.setattr(
        routes,
        "create_audit_log_service",
        lambda **kwargs: None,
    )


@pytest.fixture
def transaction_inventory(db_session):
    category = Category(
        name="Transaction Test Category",
        description="Test category",
    )
    db_session.add(category)
    db_session.flush()

    product = Product(
        sku="TRANS-TEST-001",
        name="Transaction Test Product",
        category_id=category.id,
        price=100,
        cost_price=60,
        is_active=True,
    )
    warehouse = Warehouse(
        name="Transaction Test Warehouse",
        location="Madurai",
        capacity=1000,
        is_active=True,
    )
    db_session.add_all([product, warehouse])
    db_session.flush()

    inventory = Inventory(
        product_id=product.id,
        warehouse_id=warehouse.id,
        available_quantity=50,
        reserved_quantity=0,
        damaged_quantity=0,
        reorder_level=10,
    )
    db_session.add(inventory)
    db_session.flush()

    return {
        "product": product,
        "warehouse": warehouse,
        "inventory": inventory,
    }


def test_purchase_inventory(
    authenticated_request,
    transaction_inventory,
    transaction_dependencies,
):
    product = transaction_inventory["product"]
    warehouse = transaction_inventory["warehouse"]

    response = authenticated_request(
        "POST",
        "/api/inventory/transactions/purchase",
        json={
            "product_id": product.id,
            "warehouse_id": warehouse.id,
            "quantity": 10,
            "reason": "Stock replenishment",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["transaction_type"] == "PURCHASE"
    assert data["quantity"] == 10
    assert data["product_id"] == product.id
    assert data["warehouse_id"] == warehouse.id


def test_adjust_inventory(
    authenticated_request,
    transaction_inventory,
    transaction_dependencies,
):
    product = transaction_inventory["product"]
    warehouse = transaction_inventory["warehouse"]

    response = authenticated_request(
        "POST",
        "/api/inventory/transactions/adjust",
        json={
            "product_id": product.id,
            "warehouse_id": warehouse.id,
            "quantity": 5,
            "reason": "Stock count correction",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["transaction_type"] == "ADJUSTMENT"
    assert data["quantity"] == 5


def test_adjust_inventory_negative_quantity_below_stock(
    authenticated_request,
    transaction_inventory,
    transaction_dependencies,
):
    product = transaction_inventory["product"]
    warehouse = transaction_inventory["warehouse"]

    response = authenticated_request(
        "POST",
        "/api/inventory/transactions/adjust",
        json={
            "product_id": product.id,
            "warehouse_id": warehouse.id,
            "quantity": -100,
            "reason": "Incorrect stock count",
        },
    )

    assert response.status_code == 400


def test_purchase_inventory_invalid_quantity(
    authenticated_request,
    transaction_inventory,
    transaction_dependencies,
):
    product = transaction_inventory["product"]
    warehouse = transaction_inventory["warehouse"]

    response = authenticated_request(
        "POST",
        "/api/inventory/transactions/purchase",
        json={
            "product_id": product.id,
            "warehouse_id": warehouse.id,
            "quantity": 0,
            "reason": "Invalid purchase",
        },
    )

    assert response.status_code == 422


def test_damage_inventory(
    authenticated_request,
    transaction_inventory,
    transaction_dependencies,
):
    product = transaction_inventory["product"]
    warehouse = transaction_inventory["warehouse"]

    response = authenticated_request(
        "POST",
        "/api/inventory/transactions/damage",
        json={
            "product_id": product.id,
            "warehouse_id": warehouse.id,
            "quantity": 5,
            "reason": "Damaged during handling",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["transaction_type"] == "DAMAGE"
    assert data["quantity"] == 5


def test_damage_inventory_insufficient_stock(
    authenticated_request,
    transaction_inventory,
    transaction_dependencies,
):
    product = transaction_inventory["product"]
    warehouse = transaction_inventory["warehouse"]

    response = authenticated_request(
        "POST",
        "/api/inventory/transactions/damage",
        json={
            "product_id": product.id,
            "warehouse_id": warehouse.id,
            "quantity": 100,
            "reason": "Excess damage quantity",
        },
    )

    assert response.status_code == 400


def test_damage_inventory_invalid_quantity(
    authenticated_request,
    transaction_inventory,
    transaction_dependencies,
):
    product = transaction_inventory["product"]
    warehouse = transaction_inventory["warehouse"]

    response = authenticated_request(
        "POST",
        "/api/inventory/transactions/damage",
        json={
            "product_id": product.id,
            "warehouse_id": warehouse.id,
            "quantity": 0,
            "reason": "Invalid damage quantity",
        },
    )

    assert response.status_code == 422


def test_adjust_inventory_missing_inventory(
    authenticated_request,
    transaction_inventory,
    transaction_dependencies,
):
    warehouse = transaction_inventory["warehouse"]

    response = authenticated_request(
        "POST",
        "/api/inventory/transactions/adjust",
        json={
            "product_id": 999999,
            "warehouse_id": warehouse.id,
            "quantity": 5,
            "reason": "Missing inventory record",
        },
    )

    assert response.status_code == 404


def test_list_inventory_transactions(
    authenticated_request,
    db_session,
    transaction_inventory,
    transaction_dependencies,
):
    product = transaction_inventory["product"]
    warehouse = transaction_inventory["warehouse"]

    transaction = InventoryTransaction(
        product_id=product.id,
        warehouse_id=warehouse.id,
        transaction_type=InventoryTransactionType.PURCHASE,
        quantity=10,
        reference_entity="Inventory",
        reference_id=transaction_inventory["inventory"].id,
        transaction_metadata={"reason": "Test purchase"},
    )
    db_session.add(transaction)
    db_session.flush()

    response = authenticated_request(
        "GET",
        "/api/inventory/transactions",
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert any(
        item["id"] == transaction.id
        for item in response.json()
    )


def test_filter_transactions_by_product(
    authenticated_request,
    db_session,
    transaction_inventory,
    transaction_dependencies,
):
    product = transaction_inventory["product"]
    warehouse = transaction_inventory["warehouse"]

    transaction = InventoryTransaction(
        product_id=product.id,
        warehouse_id=warehouse.id,
        transaction_type=InventoryTransactionType.PURCHASE,
        quantity=3,
    )
    db_session.add(transaction)
    db_session.flush()

    response = authenticated_request(
        "GET",
        f"/api/inventory/transactions?product_id={product.id}",
    )

    assert response.status_code == 200
    assert all(
        item["product_id"] == product.id
        for item in response.json()
    )


def test_filter_transactions_by_warehouse(
    authenticated_request,
    db_session,
    transaction_inventory,
    transaction_dependencies,
):
    product = transaction_inventory["product"]
    warehouse = transaction_inventory["warehouse"]

    transaction = InventoryTransaction(
        product_id=product.id,
        warehouse_id=warehouse.id,
        transaction_type=InventoryTransactionType.PURCHASE,
        quantity=3,
    )
    db_session.add(transaction)
    db_session.flush()

    response = authenticated_request(
        "GET",
        f"/api/inventory/transactions?warehouse_id={warehouse.id}",
    )

    assert response.status_code == 200
    assert all(
        item["warehouse_id"] == warehouse.id
        for item in response.json()
    )


def test_filter_transactions_by_type(
    authenticated_request,
    db_session,
    transaction_inventory,
    transaction_dependencies,
):
    product = transaction_inventory["product"]
    warehouse = transaction_inventory["warehouse"]

    transaction = InventoryTransaction(
        product_id=product.id,
        warehouse_id=warehouse.id,
        transaction_type=InventoryTransactionType.DAMAGE,
        quantity=2,
    )
    db_session.add(transaction)
    db_session.flush()

    response = authenticated_request(
        "GET",
        "/api/inventory/transactions?transaction_type=DAMAGE",
    )

    assert response.status_code == 200
    assert all(
        item["transaction_type"] == "DAMAGE"
        for item in response.json()
    )


@pytest.mark.parametrize(
    "query",
    [
        "?product_id=0",
        "?warehouse_id=0",
        "?skip=-1",
        "?limit=0",
        "?limit=101",
        "?transaction_type=INVALID",
    ],
)
def test_list_transactions_invalid_query_parameters(
    authenticated_request,
    query,
    transaction_dependencies,
):
    response = authenticated_request(
        "GET",
        f"/api/inventory/transactions{query}",
    )

    assert response.status_code == 422
