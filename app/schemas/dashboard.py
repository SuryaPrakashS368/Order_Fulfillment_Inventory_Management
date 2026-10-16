from pydantic import BaseModel, ConfigDict


class LowStockInventoryResponse(BaseModel):
    id: int
    product_id: int
    warehouse_id: int
    available_quantity: int
    reserved_quantity: int
    damaged_quantity: int
    reorder_level: int

    model_config = ConfigDict(
        from_attributes=True
    )