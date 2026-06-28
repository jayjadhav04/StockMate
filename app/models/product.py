import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String(100), index=True, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    description = Column(String(255), nullable=True)
    cost_price = Column(Float, nullable=False)
    gst_rate = Column(Float, nullable=False, default=18.0)  # Indian GST slab: 0, 5, 12, 18, 28
    stock_quantity = Column(Integer, nullable=False, default=0)
    minimum_stock = Column(Integer, nullable=False, default=0)
    manufacturing_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Many-to-one relationship with Category
    category = relationship("Category", back_populates="products")

    @property
    def is_low_stock(self) -> bool:
        """
        Returns True if current stock quantity is strictly less than the minimum stock level.
        """
        return self.stock_quantity < self.minimum_stock

    @property
    def expiry_status(self) -> str:
        """
        Returns "Expired", "Expiring Soon" (<=30 days), or "Normal" based on current date.
        """
        if not self.expiry_date:
            return "Normal"
        
        # Keep consistent types for date comparisons
        today = datetime.date.today()
        expiry = self.expiry_date
        
        if expiry < today:
            return "Expired"
        elif (expiry - today).days <= 30:
            return "Expiring Soon"
        
        return "Normal"
