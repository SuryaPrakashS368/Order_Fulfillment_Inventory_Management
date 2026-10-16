import pytest


@pytest.mark.parametrize(
    "method,path",
    [
        ("get", "/api/users"),
        ("get", "/api/inventory"),
        ("get", "/api/orders"),
        ("get", "/api/notifications"),
        ("get", "/api/audit-logs"),
        ("get", "/api/dashboard/summary"),
        ("get", "/api/dashboard/low-stock"),
    ],
)
def test_protected_endpoints_require_authentication(
    client,
    method,
    path,
):
    response = getattr(client, method)(path)

    assert response.status_code in (401, 403), (
        f"{method.upper()} {path} should reject anonymous users; "
        f"received {response.status_code}"
    )


def test_current_user_endpoint_requires_authentication(client):
    response = client.get("/api/auth/me")

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


def test_return_creation_requires_authentication(client):
    response = client.post(
        "/api/returns",
        json={
            "order_id": 1,
            "reason": "Testing return",
            "items": [
                {
                    "order_item_id": 1,
                    "quantity": 1,
                }
            ],
        },
    )

    assert response.status_code in (401, 403)