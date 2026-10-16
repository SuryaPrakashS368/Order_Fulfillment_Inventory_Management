import pytest

from app.models.category import Category
from app.models.product import Product


@pytest.fixture
def setup_category(db_session):
    category = Category(
        name="Product Test Category",
        description="Category for product tests",
    )

    db_session.add(category)
    db_session.flush()

    return category


@pytest.fixture
def setup_product(db_session, setup_category):
    product = Product(
        sku="TEST-SKU-001",
        name="Test Product",
        description="Product for testing",
        category_id=setup_category.id,
        price=100,
        cost_price=60,
        is_active=True,
    )

    db_session.add(product)
    db_session.flush()

    return product


def test_create_product(authenticated_request, setup_category):
    response = authenticated_request(
        "POST",
        "/api/products",
        json={
            "sku": "TEST-SKU-002",
            "name": "New Product",
            "description": "New product description",
            "category_id": setup_category.id,
            "price": 150,
            "cost_price": 90,
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["sku"] == "TEST-SKU-002"
    assert data["name"] == "New Product"
    assert data["category_id"] == setup_category.id
    assert data["is_active"] is True


def test_list_products(authenticated_request, setup_product):
    response = authenticated_request(
        "GET",
        "/api/products",
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert any(
        product["sku"] == "TEST-SKU-001"
        for product in response.json()
    )


def test_filter_products_by_category(
    authenticated_request,
    setup_category,
    setup_product,
):
    response = authenticated_request(
        "GET",
        f"/api/products?category_id={setup_category.id}",
    )

    assert response.status_code == 200
    assert all(
        product["category_id"] == setup_category.id
        for product in response.json()
    )


def test_search_products(authenticated_request, setup_product):
    response = authenticated_request(
        "GET",
        "/api/products?search=Test Product",
    )

    assert response.status_code == 200
    assert any(
        product["sku"] == "TEST-SKU-001"
        for product in response.json()
    )


def test_get_product(authenticated_request, setup_product):
    response = authenticated_request(
        "GET",
        f"/api/products/{setup_product.id}",
    )

    assert response.status_code == 200
    assert response.json()["sku"] == "TEST-SKU-001"


def test_get_nonexistent_product(authenticated_request):
    response = authenticated_request(
        "GET",
        "/api/products/999999",
    )

    assert response.status_code == 404


def test_update_product(authenticated_request, setup_product):
    response = authenticated_request(
        "PUT",
        f"/api/products/{setup_product.id}",
        json={
            "name": "Updated Product",
            "price": 200,
        },
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Product"
    assert float(response.json()["price"]) == 200


def test_update_product_sku(authenticated_request, setup_product):
    response = authenticated_request(
        "PUT",
        f"/api/products/{setup_product.id}",
        json={"sku": "UPDATED-SKU-001"},
    )

    assert response.status_code == 200
    assert response.json()["sku"] == "UPDATED-SKU-001"


def test_create_product_with_duplicate_sku(
    authenticated_request,
    setup_category,
    setup_product,
):
    response = authenticated_request(
        "POST",
        "/api/products",
        json={
            "sku": "TEST-SKU-001",
            "name": "Duplicate SKU Product",
            "category_id": setup_category.id,
            "price": 100,
            "cost_price": 50,
        },
    )

    assert response.status_code == 409


def test_create_product_with_invalid_category(
    authenticated_request,
):
    response = authenticated_request(
        "POST",
        "/api/products",
        json={
            "sku": "TEST-SKU-003",
            "name": "Invalid Category Product",
            "category_id": 999999,
            "price": 100,
            "cost_price": 50,
        },
    )

    assert response.status_code == 404


def test_create_product_with_negative_price(
    authenticated_request,
    setup_category,
):
    response = authenticated_request(
        "POST",
        "/api/products",
        json={
            "sku": "TEST-SKU-004",
            "name": "Negative Price Product",
            "category_id": setup_category.id,
            "price": -10,
            "cost_price": 5,
        },
    )

    assert response.status_code == 422


def test_update_nonexistent_product(authenticated_request):
    response = authenticated_request(
        "PUT",
        "/api/products/999999",
        json={"name": "Updated Product"},
    )

    assert response.status_code == 404


def test_deactivate_product(authenticated_request, setup_product):
    response = authenticated_request(
        "PATCH",
        f"/api/products/{setup_product.id}/status",
        json={"is_active": False},
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is False


def test_delete_product(authenticated_request, setup_product):
    response = authenticated_request(
        "DELETE",
        f"/api/products/{setup_product.id}",
    )

    assert response.status_code == 200
    assert response.json()["message"] == (
        "Product deactivated successfully"
    )

    # Delete is a soft delete, so the product record remains.
    get_response = authenticated_request(
        "GET",
        f"/api/products/{setup_product.id}",
    )

    assert get_response.status_code == 200
    assert get_response.json()["is_active"] is False


def test_list_products_with_pagination(
    authenticated_request,
    setup_product,
):
    response = authenticated_request(
        "GET",
        "/api/products?page=1&page_size=10",
    )

    assert response.status_code == 200
    assert len(response.json()) <= 10
