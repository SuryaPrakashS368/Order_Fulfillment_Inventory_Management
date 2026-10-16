from decimal import Decimal
import secrets
import string

from fastapi import (
    HTTPException,
    status
)

from sqlalchemy.orm import Session

from app.models.order import (
    Order,
    OrderStatus,
    PaymentStatus
)

from app.models.order_item import (
    OrderItem
)

from app.models.order_status_history import (
    OrderStatusHistory
)

from app.repositories.idempotency_repository import create_idempotency_key, get_idempotency_key
from app.repositories.order_repository import (
    create_order,
    get_order_by_id,
    get_customer_orders
)

from app.repositories.order_item_repository import (
    create_order_item
)

from app.repositories.order_status_history_repository import (
    create_status_history
)

from app.repositories.product_repository import (
    get_product_by_id
)

from app.repositories.warehouse_repository import (
    get_warehouse_by_id
)

from app.repositories.inventory_repository import (
    get_inventory_by_product_and_warehouse
)

from app.services.inventory_transaction_service import (
    reserve_inventory_service
)


def generate_order_number():

    random_part = "".join(
        secrets.choice(
            string.ascii_uppercase
            + string.digits
        )
        for _ in range(8)
    )

    return f"ORD-{random_part}"


def create_order_service(
    db: Session,
    customer_id: int,
    warehouse_id: int,
    items,
    idempotency_key: str,
    request_hash: str,
):

    existing_key = get_idempotency_key(
        db=db,
        user_id=customer_id,
        key=idempotency_key,
    )

    if existing_key is not None:

        if existing_key.request_hash != request_hash:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Idempotency key was already used "
                    "with a different request"
                ),
            )

        if existing_key.resource_id is not None:
            existing_order = get_order_by_id(
                db,
                existing_key.resource_id,
            )

            if existing_order is not None:
                return existing_order

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "This idempotency key is already being "
                "processed or its previous order is unavailable"
            ),
        )

    warehouse = get_warehouse_by_id(
        db,
        warehouse_id
    )

    if not warehouse:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Warehouse not found"
        )

    if not warehouse.is_active:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Warehouse is inactive"
        )

    if not items:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order must contain at least one item"
        )

    order_items_data = []

    total_amount = Decimal("0.00")

    for item in items:

        product = get_product_by_id(
            db,
            item.product_id
        )

        if not product:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Product {item.product_id} not found"
                )
            )

        if not product.is_active:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Product {item.product_id} is inactive"
                )
            )

        inventory = (
            get_inventory_by_product_and_warehouse(
                db,
                item.product_id,
                warehouse_id
            )
        )

        if not inventory:

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"No inventory found for "
                    f"product {item.product_id} "
                    f"in selected warehouse"
                )
            )

        if (
            inventory.available_quantity
            < item.quantity
        ):

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Insufficient inventory for "
                    f"product {item.product_id}"
                )
            )

        unit_price = Decimal(
            str(product.price)
        )

        item_total = (
            unit_price
            * item.quantity
        )

        order_items_data.append({
            "product": product,
            "quantity": item.quantity,
            "unit_price": unit_price,
            "total": item_total
        })

        total_amount += item_total

    order = Order(
        order_number=generate_order_number(),
        customer_id=customer_id,
        warehouse_id=warehouse_id,
        total_amount=total_amount,
        status=OrderStatus.PENDING,
        payment_status=PaymentStatus.PENDING
    )

    try:

        create_order(
            db,
            order
        )

        for item_data in order_items_data:

            order_item = OrderItem(
                order_id=order.id,
                product_id=(
                    item_data["product"].id
                ),
                quantity=item_data["quantity"],
                unit_price=item_data["unit_price"],
                discount=Decimal("0.00"),
                tax=Decimal("0.00"),
                total=item_data["total"]
            )

            create_order_item(
                db,
                order_item
            )

        for item_data in order_items_data:

            reserve_inventory_service(
                db=db,
                product_id=(
                    item_data["product"].id
                ),
                warehouse_id=warehouse_id,
                quantity=item_data["quantity"],
                order_id=order.id,
                user_id=customer_id
            )

        history = OrderStatusHistory(
            order_id=order.id,
            from_status=None,
            to_status=OrderStatus.PENDING,
            changed_by=customer_id,
            reason="Order created"
        )

        create_status_history(
            db,
            history
        )

        create_idempotency_key(
            db=db,
            user_id=customer_id,
            key=idempotency_key,
            resource_type="Order",
            resource_id=order.id,
            request_hash=request_hash,
        )

        db.commit()

        db.refresh(order)

        return order

    except Exception:

        db.rollback()

        raise


def get_order_service(
    db: Session,
    order_id: int
):

    order = get_order_by_id(
        db,
        order_id
    )

    if not order:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    return order



def get_customer_orders_service(
    db: Session,
    customer_id: int,
    skip: int = 0,
    limit: int = 20,
    order_status: str | None = None,
    order_number: str | None = None,
):
    status_filter = None

    if order_status is not None:
        try:
            status_filter = OrderStatus(
                order_status.upper()
            )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    f"Invalid order status: {order_status}. "
                    f"Allowed values: "
                    f"{', '.join(item.value for item in OrderStatus)}"
                ),
            )

    return get_customer_orders(
        db=db,
        customer_id=customer_id,
        skip=skip,
        limit=limit,
        status=status_filter,
        order_number=order_number,
    )
