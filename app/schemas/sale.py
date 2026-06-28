from datetime import datetime
from typing import List, Literal
from pydantic import BaseModel, Field

class SaleItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0, description="Quantity must be greater than 0")
    selling_price: float = Field(..., gt=0, description="Selling price must be greater than 0")
    gst_rate: float = Field(default=18.0, ge=0, description="GST rate in percent (0, 5, 12, 18, 28)")

class SaleCreate(BaseModel):
    customer_id: int
    payment_method: Literal["Cash", "UPI", "Card"] = "Cash"
    items: List[SaleItemCreate] = Field(..., min_length=1, description="An invoice must have at least one product")

class SaleItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    cost_price: float
    selling_price: float
    line_total: float
    gst_amount: float
    line_profit: float

    class Config:
        from_attributes = True

class SaleResponse(BaseModel):
    id: int
    invoice_number: str
    customer_id: int
    employee_id: int
    total_amount: float
    total_profit: float
    total_gst: float
    payment_method: str
    sale_date: datetime
    items: List[SaleItemResponse]

    class Config:
        from_attributes = True
