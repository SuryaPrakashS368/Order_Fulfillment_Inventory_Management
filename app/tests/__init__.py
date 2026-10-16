def test_openapi_schema_available(client):
    response = client.get("/openapi.json")

    assert response.status_code == 200

    data = response.json()

    assert "openapi" in data
    assert "paths" in data


def test_swagger_documentation_available(client):
    response = client.get("/docs")

    assert response.status_code == 200


def test_redoc_documentation_available(client):
    response = client.get("/redoc")

    assert response.status_code == 200


def test_required_api_routes_are_registered(client):
    response = client.get("/openapi.json")

    assert response.status_code == 200

    paths = response.json()["paths"]

    required_paths = [
        "/api/orders",
        "/api/inventory",
        "/api/notifications",
        "/api/audit-logs",
        "/api/dashboard/summary",
        "/api/dashboard/low-stock",
    ]

    for path in required_paths:
        assert path in paths, (
            f"Expected API route {path} is missing from OpenAPI"
        )