from fastapi import (
    APIRouter,
    Depends,
    status
)

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.core.permissions_dependency import require_permission

from app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse
)

from app.services.audit_log_service import create_audit_log_service
from app.services.category_service import (
    create_category_service,
    list_categories,
    get_category,
    update_category_service,
    delete_category_service
)


router = APIRouter(
    prefix="/api/categories",
    tags=["Categories"]
)


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED
)
def create_category(
    request: CategoryCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("product:create")
    )
):

    category = create_category_service(
        db,
        request.name,
        request.description
    )

    create_audit_log_service(
        db=db,
        user_id=current_user.id,
        action="CATEGORY_CREATED",
        entity="Category",
        entity_id=category.id,
        details={
            "name": category.name
        }
    )

    return category


@router.get(
    "",
    response_model=list[CategoryResponse]
)
def get_categories(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("product:read")
    )
):

    return list_categories(db)


@router.get(
    "/{category_id}",
    response_model=CategoryResponse
)
def get_single_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("product:read")
    )
):

    return get_category(
        db,
        category_id
    )


@router.put(
    "/{category_id}",
    response_model=CategoryResponse
)
def update_category(
    category_id: int,
    request: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("product:update")
    )
):

    return update_category_service(
        db,
        category_id,
        request.name,
        request.description
    )


@router.delete(
    "/{category_id}"
)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("product:delete")
    )
):

    return delete_category_service(
        db,
        category_id
    )