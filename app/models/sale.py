import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(50), unique=True, index=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    employee_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    total_amount = Column(Float, nullable=False, default=0.0)   # Pre-GST subtotal
    total_profit = Column(Float, nullable=False, default=0.0)
    total_gst = Column(Float, nullable=False, default=0.0)       # Total GST collected
    payment_method = Column(String(20), nullable=False, default="Cash")  # Cash | UPI | Card
    sale_date = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="sales")
    employee = relationship("User")
    items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")

    @property
    def serialized_items(self) -> list:
        return [
            {
                "product_id": item.product_id,
                "product_name": item.product.product_name if item.product else f"Product #{item.product_id}",
                "quantity": item.quantity,
                "selling_price": item.selling_price,
                "line_total": item.line_total
            }
            for item in self.items
        ]
