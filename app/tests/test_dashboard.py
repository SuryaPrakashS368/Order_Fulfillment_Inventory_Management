def test_dashboard_requires_authentication(client):
    response = client.get("/api/dashboard/summary")

    assert response.status_code in (401, 403)


def test_low_stock_rejects_invalid_pagination(
    authenticated_request,
):
    response = authenticated_request(
        "GET",
        "/api/dashboard/low-stock?skip=-1",
    )

    assert response.status_code == 422


def test_low_stock_rejects_limit_above_maximum(
    authenticated_request,
):
    response = authenticated_request(
        "GET",
        "/api/dashboard/low-stock?limit=101",
    )

    assert response.status_code == 422
