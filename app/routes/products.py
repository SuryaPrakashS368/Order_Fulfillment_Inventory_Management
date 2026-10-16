from fastapi import (
    APIRouter,
    Depends,
    Query,
    status
)

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.core.permissions_dependency import require_permission
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductStatusUpdate,
    ProductResponse
)

from app.services.audit_log_service import create_audit_log_service
from app.services.product_service import (
    create_product_service,
    list_products_service,
    get_product_service,
    update_product_service,
    update_product_status
)


router = APIRouter(
    prefix="/api/products",
    tags=["Products"]
)


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED
)
def create_product(
    request: ProductCreate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("product:create")
    )
):

    product = create_product_service(
        db,
        request.sku,
        request.name,
        request.description,
        request.category_id,
        request.price,
        request.cost_price
    )

    create_audit_log_service(
        db=db,
        user_id=current_user.id,
        action="PRODUCT_CREATED",
        entity="Product",
        entity_id=product.id,
        details={
            "sku": product.sku,
            "name": product.name,
            "category_id": product.category_id
        }
    )

    return product


@router.get(
    "",
    response_model=list[ProductResponse]
)
def get_products(
    category_id: int | None = Query(
        default=None,
        gt=0
    ),
    search: str | None = None,
    is_active: bool | None = None,
    page: int = Query(
        default=1,
        ge=1
    ),
    page_size: int = Query(
        default=20,
        ge=1,
        le=100
    ),
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("product:read")
    )
):

    return list_products_service(
        db,
        category_id,
        search,
        is_active,
        page,
        page_size
    )


@router.get(
    "/{product_id}",
    response_model=ProductResponse
)
def get_single_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("product:read")
    )
):

    return get_product_service(
        db,
        product_id
    )


@router.put(
    "/{product_id}",
    response_model=ProductResponse
)
def update_product(
    product_id: int,
    request: ProductUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("product:update")
    )
):

    return update_product_service(
        db,
        product_id,
        request.sku,
        request.name,
        request.description,
        request.category_id,
        request.price,
        request.cost_price
    )


@router.patch(
    "/{product_id}/status",
    response_model=ProductResponse
)
def update_product_status_route(
    product_id: int,
    request: ProductStatusUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("product:update")
    )
):

    return update_product_status(
        db,
        product_id,
        request.is_active
    )


@router.delete(
    "/{product_id}"
)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("product:delete")
    )
):

    product = get_product_service(
        db,
        product_id
    )

    product.is_active = False

    db.commit()

    return {
        "message": "Product deactivated successfully"
    }