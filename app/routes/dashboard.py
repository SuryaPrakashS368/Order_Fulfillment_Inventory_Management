from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.permissions_dependency import require_permission
from app.schemas.dashboard import LowStockInventoryResponse
from app.services.dashboard_service import (
    get_dashboard_summary_service,
    get_low_stock_service,
)

router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"],
)


@router.get("/summary")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("dashboard:read")
    ),
):
    return get_dashboard_summary_service(
        db=db,
        current_user=current_user,
    )


@router.get(
    "/low-stock",
    response_model=list[LowStockInventoryResponse],
)
def get_low_stock(
    skip: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
    current_user=Depends(
        require_permission("dashboard:read")
    ),
):
    return get_low_stock_service(
        db=db,
        current_user=current_user,
        skip=skip,
        limit=limit,
    )