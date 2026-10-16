from fastapi import (
    HTTPException,
    status
)

from sqlalchemy.orm import Session

from app.models.product import Product

from app.repositories.category_repository import (
    get_category_by_id
)

from app.repositories.product_repository import (
    get_product_by_id,
    get_product_by_sku,
    get_products,
    create_product,
    update_product
)


def create_product_service(
    db: Session,
    sku: str,
    name: str,
    description: str | None,
    category_id: int,
    price,
    cost_price
):

    existing_product = get_product_by_sku(
        db,
        sku
    )

    if existing_product:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="SKU already exists"
        )

    category = get_category_by_id(
        db,
        category_id
    )

    if not category:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    product = Product(
        sku=sku,
        name=name,
        description=description,
        category_id=category_id,
        price=price,
        cost_price=cost_price,
        is_active=True
    )

    return create_product(
        db,
        product
    )


def list_products_service(
    db: Session,
    category_id: int | None,
    search: str | None,
    is_active: bool | None,
    page: int,
    page_size: int
):

    skip = (
        page - 1
    ) * page_size

    return get_products(
        db,
        category_id=category_id,
        search=search,
        is_active=is_active,
        skip=skip,
        limit=page_size
    )


def get_product_service(
    db: Session,
    product_id: int
):

    product = get_product_by_id(
        db,
        product_id
    )

    if not product:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    return product


def update_product_service(
    db: Session,
    product_id: int,
    sku: str | None,
    name: str | None,
    description: str | None,
    category_id: int | None,
    price,
    cost_price
):

    product = get_product_service(
        db,
        product_id
    )

    if sku and sku != product.sku:

        existing_product = get_product_by_sku(
            db,
            sku
        )

        if existing_product:

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="SKU already exists"
            )

        product.sku = sku

    if name is not None:

        product.name = name

    if description is not None:

        product.description = description

    if category_id is not None:

        category = get_category_by_id(
            db,
            category_id
        )

        if not category:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )

        product.category_id = category_id

    if price is not None:

        product.price = price

    if cost_price is not None:

        product.cost_price = cost_price

    return update_product(
        db,
        product
    )


def update_product_status(
    db: Session,
    product_id: int,
    is_active: bool
):

    product = get_product_service(
        db,
        product_id
    )

    product.is_active = is_active

    return update_product(
        db,
        product
    )