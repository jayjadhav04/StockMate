from typing import List
from pydantic import BaseModel, Field

class PurchaseOrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0, description="Quantity must be greater than 0")
    cost_price: float = Field(..., gt=0, description="Cost price must be greater than 0")

class PurchaseOrderCreate(BaseModel):
    supplier_id: int
    items: List[PurchaseOrderItemCreate] = Field(..., min_length=1, description="A purchase order must have at least one product")
