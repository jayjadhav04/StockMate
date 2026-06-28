from app.models.category import Category
from app.models.product import Product
from app.models.customer import Customer
from app.models.sale import Sale

def test_sales_and_inventory_transactional_safety(client, db_session):
    """
    Tests customer creation, sales billing, stock deductions, profit calculation,
    and database rollback triggers on out-of-stock validation failures.
    """
    # 1. Login as Employee
    client.post("/auth/login", data={"email": "testemployee@stockmate.com", "password": "employee123"})
    
    # 2. Seed Customer
    customer = Customer(
        customer_name="Acme Corporation",
        phone="555-1234",
        email="info@acme.com",
        address="123 Road"
    )
    db_session.add(customer)
    
    # 3. Seed Category & Product
    cat = Category(name="Tools")
    db_session.add(cat)
    db_session.commit()
    
    product = Product(
        product_name="Hammer",
        category_id=cat.id,
        cost_price=5.0,  # cost is $5
        stock_quantity=10,  # initial stock is 10
        minimum_stock=2
    )
    db_session.add(product)
    db_session.commit()
    
    # 4. Process Successful Invoice (Buy 2 Hammers at $10 each)
    invoice_payload = {
        "customer_id": customer.id,
        "items": [
            {
                "product_id": product.id,
                "quantity": 2,
                "selling_price": 10.0  # selling price is $10
            }
        ]
    }
    
    response = client.post("/sales/create", json=invoice_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["invoice_number"] == "INV-000001"
    
    # Refresh DB session variables and check state
    db_session.refresh(product)
    assert product.stock_quantity == 8  # stock reduced from 10 to 8
    
    # Verify invoice records in database
    sale = db_session.query(Sale).filter(Sale.invoice_number == "INV-000001").first()
    assert sale is not None
    assert sale.total_amount == 20.0  # 2 * 10 = $20
    assert sale.total_profit == 10.0  # 2 * (10 - 5) = $10 profit
    assert len(sale.items) == 1
    assert sale.items[0].line_total == 20.0
    assert sale.items[0].line_profit == 10.0
    
    # 5. Process Failed Invoice (Request 9 Hammers which exceeds stock 8)
    failed_payload = {
        "customer_id": customer.id,
        "items": [
            {
                "product_id": product.id,
                "quantity": 9,  # requested 9, available 8
                "selling_price": 10.0
            }
        ]
    }
    
    response2 = client.post("/sales/create", json=failed_payload)
    assert response2.status_code == 400
    assert "Insufficient stock" in response2.json()["detail"]
    
    # Verify rollback: stock remains 8 and no new invoice is created
    db_session.refresh(product)
    assert product.stock_quantity == 8  # remains unchanged
    
    failed_sale = db_session.query(Sale).filter(Sale.invoice_number == "INV-000002").first()
    assert failed_sale is None
