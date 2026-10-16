import pytest

from app.models.category import Category


@pytest.fixture
def setup_category(db_session):
    category = Category(
        name="Test Electronics",
        description="Electronic products for testing",
    )

    db_session.add(category)
    db_session.flush()

    return category


def test_create_category(authenticated_request):
    response = authenticated_request(
        "POST",
        "/api/categories",
        json={
            "name": "Test Books",
            "description": "Books for testing",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["name"] == "Test Books"
    assert data["description"] == "Books for testing"
    assert "id" in data


def test_list_categories(authenticated_request, setup_category):
    response = authenticated_request(
        "GET",
        "/api/categories",
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)

    assert any(
        category["name"] == "Test Electronics"
        for category in response.json()
    )


def test_get_category(authenticated_request, setup_category):
    response = authenticated_request(
        "GET",
        f"/api/categories/{setup_category.id}",
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Test Electronics"


def test_get_nonexistent_category(authenticated_request):
    response = authenticated_request(
        "GET",
        "/api/categories/999999",
    )

    assert response.status_code == 404


def test_update_category(authenticated_request, setup_category):
    response = authenticated_request(
        "PUT",
        f"/api/categories/{setup_category.id}",
        json={
            "name": "Updated Electronics",
            "description": "Updated category description",
        },
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Electronics"
    assert response.json()["description"] == (
        "Updated category description"
    )


def test_update_category_description_only(
    authenticated_request,
    setup_category,
):
    response = authenticated_request(
        "PUT",
        f"/api/categories/{setup_category.id}",
        json={
            "description": "New description only",
        },
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Test Electronics"
    assert response.json()["description"] == "New description only"


def test_create_duplicate_category(
    authenticated_request,
    setup_category,
):
    response = authenticated_request(
        "POST",
        "/api/categories",
        json={
            "name": "Test Electronics",
            "description": "Duplicate category",
        },
    )

    assert response.status_code == 409


def test_delete_category(authenticated_request, setup_category):
    response = authenticated_request(
        "DELETE",
        f"/api/categories/{setup_category.id}",
    )

    assert response.status_code == 200

    get_response = authenticated_request(
        "GET",
        f"/api/categories/{setup_category.id}",
    )

    assert get_response.status_code == 404


def test_delete_nonexistent_category(authenticated_request):
    response = authenticated_request(
        "DELETE",
        "/api/categories/999999",
    )

    assert response.status_code == 404


def test_create_category_with_short_name(authenticated_request):
    response = authenticated_request(
        "POST",
        "/api/categories",
        json={
            "name": "A",
            "description": "Invalid short name",
        },
    )

    assert response.status_code == 422


def test_create_category_without_name(authenticated_request):
    response = authenticated_request(
        "POST",
        "/api/categories",
        json={
            "description": "Name is missing",
        },
    )

    assert response.status_code == 422
