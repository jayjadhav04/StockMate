import datetime
from app.models.category import Category
from app.models.product import Product

def test_product_alerts_logic(db_session):
    """
    Tests the Product model's dynamic property alerts for stock level and expiry dates.
    """
    today = datetime.date.today()
    
    # Create category first
    cat = Category(name="Grocery")
    db_session.add(cat)
    db_session.commit()
    
    # 1. Test Low Stock alert
    p1 = Product(
        product_name="Product A",
        category_id=cat.id,
        cost_price=10.0,
        stock_quantity=5,
        minimum_stock=10  # Stock (5) < Min (10) -> Low Stock
    )
    assert p1.is_low_stock is True
    
    # 2. Test Expired status
    p2 = Product(
        product_name="Product B",
        category_id=cat.id,
        cost_price=10.0,
        stock_quantity=50,
        minimum_stock=5,
        expiry_date=today - datetime.timedelta(days=1)  # expired yesterday
    )
    assert p2.expiry_status == "Expired"
    
    # 3. Test Expiring Soon status (within 30 days)
    p3 = Product(
        product_name="Product C",
        category_id=cat.id,
        cost_price=10.0,
        stock_quantity=50,
        minimum_stock=5,
        expiry_date=today + datetime.timedelta(days=10)  # expiring in 10 days
    )
    assert p3.expiry_status == "Expiring Soon"
    
    # 4. Test Normal status (more than 30 days)
    p4 = Product(
        product_name="Product D",
        category_id=cat.id,
        cost_price=10.0,
        stock_quantity=50,
        minimum_stock=5,
        expiry_date=today + datetime.timedelta(days=45)  # expiring in 45 days
    )
    assert p4.expiry_status == "Normal"

def test_product_add_validation_fail(client, db_session):
    """
    Verifies that invalid product inputs (e.g. wrong expiry bounds) are rejected.
    """
    client.post("/auth/login", data={"email": "testowner@stockmate.com", "password": "owner123"})
    
    cat = Category(name="Household")
    db_session.add(cat)
    db_session.commit()
    
    # Submit invalid product form (Expiry date before Manufacturing date)
    invalid_data = {
        "product_name": "Invalid Date Product",
        "category_id": cat.id,
        "cost_price": 10.0,
        "stock_quantity": 100,
        "minimum_stock": 10,
        "manufacturing_date": "2026-06-25",
        "expiry_date": "2026-06-20"  # expiry before mfg
    }
    response = client.post("/products/add", data=invalid_data)
    
    assert response.status_code == 200
    assert "Expiry date cannot be before manufacturing date." in response.text
