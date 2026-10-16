from sqlalchemy.orm import Session

from app.models.product import Product


def get_product_by_id(
    db: Session,
    product_id: int
):
    return (
        db.query(Product)
        .filter(
            Product.id == product_id
        )
        .first()
    )


def get_product_by_sku(
    db: Session,
    sku: str
):
    return (
        db.query(Product)
        .filter(
            Product.sku == sku
        )
        .first()
    )


def get_products(
    db: Session,
    category_id: int | None = None,
    search: str | None = None,
    is_active: bool | None = None,
    skip: int = 0,
    limit: int = 20
):

    query = db.query(Product)

    if category_id is not None:

        query = query.filter(
            Product.category_id == category_id
        )

    if search:

        search_value = f"%{search}%"

        query = query.filter(
            Product.name.ilike(search_value)
            |
            Product.sku.ilike(search_value)
        )

    if is_active is not None:

        query = query.filter(
            Product.is_active == is_active
        )

    return (
        query
        .order_by(Product.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_product(
    db: Session,
    product: Product
):
    db.add(product)
    db.commit()
    db.refresh(product)

    return product


def update_product(
    db: Session,
    product: Product
):
    db.commit()
    db.refresh(product)

    return product