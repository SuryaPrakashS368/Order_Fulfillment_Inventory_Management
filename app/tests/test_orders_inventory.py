import pytest


# --------------------------------------------------
# ORDER AUTHENTICATION TESTS
# --------------------------------------------------

def test_order_list_requires_authentication(client):
    response = client.get("/api/orders")

    assert response.status_code in (401, 403)


def test_order_creation_requires_authentication(client):
    response = client.post(
        "/api/orders",
        json={
            "warehouse_id": 1,
            "items": [
                {
                    "product_id": 1,
                    "quantity": 1,
                }
            ],
        },
    )

    assert response.status_code in (401, 403)


# --------------------------------------------------
# ORDER PAGINATION VALIDATION TESTS
# --------------------------------------------------

@pytest.mark.parametrize(
    "query",
    [
        "?skip=-1",
        "?limit=0",
        "?limit=101",
    ],
)
def test_order_pagination_validation(
    authenticated_request,
    query,
):
    response = authenticated_request(
        "GET",
        "/api/orders" + query,
    )

    assert response.status_code == 422


# --------------------------------------------------
# INVENTORY AUTHENTICATION TESTS
# --------------------------------------------------

def test_inventory_list_requires_authentication(client):
    response = client.get("/api/inventory")

    assert response.status_code in (401, 403)


def test_inventory_transactions_require_authentication(client):
    response = client.get(
        "/api/inventory/transactions"
    )

    assert response.status_code in (401, 403)


# --------------------------------------------------
# DASHBOARD LOW-STOCK PAGINATION TESTS
# --------------------------------------------------

@pytest.mark.parametrize(
    "query",
    [
        "?skip=-1",
        "?limit=0",
        "?limit=101",
    ],
)
def test_low_stock_pagination_validation(
    authenticated_request,
    query,
):
    response = authenticated_request(
        "GET",
        "/api/dashboard/low-stock" + query,
    )

    assert response.status_code == 422


# --------------------------------------------------
# INVALID ORDER ID TEST
# --------------------------------------------------

def test_invalid_order_id_does_not_create_order(client):
    response = client.get(
        "/api/orders/999999999"
    )

    assert response.status_code in (401, 403, 404)
