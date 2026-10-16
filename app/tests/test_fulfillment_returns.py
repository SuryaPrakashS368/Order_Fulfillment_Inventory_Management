def test_fulfillment_assignment_requires_authentication(client):
    response = client.post(
        "/api/fulfillment/orders/1/assign",
        json={"agent_id": 2},
    )

    assert response.status_code in (401, 403)


def test_order_assignments_require_authentication(client):
    response = client.get(
        "/api/fulfillment/orders/1/assignments"
    )

    assert response.status_code in (401, 403)


def test_my_fulfillment_assignments_require_authentication(client):
    response = client.get(
        "/api/fulfillment/my-assignments"
    )

    assert response.status_code in (401, 403)


def test_my_returns_requires_authentication(client):
    response = client.get("/api/returns/my-returns")

    assert response.status_code in (401, 403)


def test_return_approval_requires_authentication(client):
    response = client.post(
        "/api/returns/1/approve",
        json={"reason": "Test approval"},
    )

    assert response.status_code in (401, 403)


def test_return_receiving_requires_authentication(client):
    response = client.post(
        "/api/returns/1/receive"
    )

    assert response.status_code in (401, 403)


def test_return_refund_requires_authentication(client):
    response = client.post(
        "/api/returns/1/refund"
    )

    assert response.status_code in (401, 403)