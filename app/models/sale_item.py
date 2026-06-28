from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class SaleItem(Base):
    __tablename__ = "sale_items"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    cost_price = Column(Float, nullable=False)  # Cost price at time of sale
    selling_price = Column(Float, nullable=False)  # Selling price set in invoice
    line_total = Column(Float, nullable=False)  # quantity * selling_price (pre-GST)
    gst_amount = Column(Float, nullable=False, default=0.0)  # line_total * gst_rate / 100
    line_profit = Column(Float, nullable=False)  # quantity * (selling_price - cost_price)

    # Relationships
    sale = relationship("Sale", back_populates="items")
    product = relationship("Product")
