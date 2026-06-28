from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, model_validator
from app.schemas.category import CategoryResponse

class ProductBase(BaseModel):
    product_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    cost_price: float = Field(..., gt=0, description="Cost price must be greater than 0")
    stock_quantity: int = Field(0, ge=0, description="Stock quantity cannot be negative")
    minimum_stock: int = Field(0, ge=0, description="Minimum stock level cannot be negative")
    manufacturing_date: Optional[date] = None
    expiry_date: Optional[date] = None

class ProductCreate(ProductBase):
    category_id: int

    @model_validator(mode="after")
    def validate_dates(self) -> 'ProductCreate':
        if self.manufacturing_date and self.expiry_date:
            if self.expiry_date < self.manufacturing_date:
                raise ValueError("Expiry date cannot be before manufacturing date")
        return self

class ProductUpdate(BaseModel):
    product_name: Optional[str] = Field(None, min_length=1, max_length=100)
    category_id: Optional[int] = None
    description: Optional[str] = Field(None, max_length=255)
    cost_price: Optional[float] = Field(None, gt=0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    minimum_stock: Optional[int] = Field(None, ge=0)
    manufacturing_date: Optional[date] = None
    expiry_date: Optional[date] = None

    @model_validator(mode="after")
    def validate_dates(self) -> 'ProductUpdate':
        mfg = self.manufacturing_date
        exp = self.expiry_date
        if mfg and exp:
            if exp < mfg:
                raise ValueError("Expiry date cannot be before manufacturing date")
        return self

class ProductResponse(ProductBase):
    id: int
    category_id: int
    created_at: datetime
    updated_at: datetime
    category: CategoryResponse
    is_low_stock: bool
    expiry_status: str

    class Config:
        from_attributes = True
