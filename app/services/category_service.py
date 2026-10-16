from fastapi import (
    HTTPException,
    status
)

from sqlalchemy.orm import Session

from app.models.category import Category

from app.repositories.category_repository import (
    get_category_by_id,
    get_category_by_name,
    get_categories,
    create_category,
    update_category,
    delete_category
)


def create_category_service(
    db: Session,
    name: str,
    description: str | None
):

    existing_category = get_category_by_name(
        db,
        name
    )

    if existing_category:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category already exists"
        )

    category = Category(
        name=name,
        description=description
    )

    return create_category(
        db,
        category
    )


def list_categories(
    db: Session
):

    return get_categories(db)


def get_category(
    db: Session,
    category_id: int
):

    category = get_category_by_id(
        db,
        category_id
    )

    if not category:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    return category


def update_category_service(
    db: Session,
    category_id: int,
    name: str | None,
    description: str | None
):

    category = get_category(
        db,
        category_id
    )

    if name and name != category.name:

        existing_category = get_category_by_name(
            db,
            name
        )

        if existing_category:

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Category already exists"
            )

        category.name = name

    if description is not None:

        category.description = description

    return update_category(
        db,
        category
    )


def delete_category_service(
    db: Session,
    category_id: int
):

    category = get_category(
        db,
        category_id
    )

    if category.products:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Cannot delete category "
                "because products exist"
            )
        )

    delete_category(
        db,
        category
    )

    return {
        "message": "Category deleted successfully"
    }