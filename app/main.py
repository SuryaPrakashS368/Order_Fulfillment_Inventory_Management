from fastapi import FastAPI

from app.core.config import settings
from app.routes.auth import router as auth_router
from app.routes.users import router as user_router
from app.routes.categories import router as categories_router
from app.routes.products import router as products_router
from app.routes.warehouses import router as warehouses_router
from app.routes.warehouse_users import router as warehouse_users_router
from app.routes.inventory import router as inventory_router
from app.routes.inventory_transactions import router as inventory_transactions_router
from app.routes.orders import router as orders_router
from app.routes.fulfillment import router as fulfillment_router
from app.routes.returns import router as returns_router
from app.routes.notifications import router as notifications_router
from app.routes.audit_logs import router as audit_logs_router
from app.routes.payments import router as payments_router
from app.routes.dashboard import router as dashboard_router

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import StarletteHTTPException

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(categories_router)
app.include_router(products_router)
app.include_router(warehouses_router)
app.include_router(warehouse_users_router)
app.include_router(inventory_transactions_router)
app.include_router(inventory_router)
app.include_router(orders_router)
app.include_router(fulfillment_router)
app.include_router(returns_router)
app.include_router(notifications_router)
app.include_router(audit_logs_router)
app.include_router(payments_router)
app.include_router(dashboard_router)



@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        # Use a generic message only when the requested route does not exist.
        message = (
            "Endpoint not found"
            if exc.detail == "Not Found"
            else str(exc.detail)
        )

        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": message,
                },
            },
        )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": str(exc.detail),
            },
        },
        headers=exc.headers,
    )
