from app.models.category import Category
from app.models.product import Product
from app.models.supplier import Supplier
from app.models.purchase_order import PurchaseOrder
from app.models.audit_log import AuditLog

def test_purchase_order_lifecycle(client, db_session):
    """
    Tests supplier creation, employee drafting PO, employee blocked from completing PO,
    and owner successfully completing PO (verifying stock increments, cost updates, and audit logging).
    """
    # 1. Login as Owner to seed supplier and product
    client.post("/auth/login", data={"email": "testowner@stockmate.com", "password": "owner123"})
    
    supplier = Supplier(
        supplier_name="Global Foods Ltd",
        contact_name="Bob Miller",
        phone="555-9876",
        email="bob@global.com",
        address="789 Warehouse St"
    )
    db_session.add(supplier)
    
    cat = Category(name="Beverages")
    db_session.add(cat)
    db_session.commit()
    
    product = Product(
        product_name="Orange Juice",
        category_id=cat.id,
        cost_price=1.50,  # initial cost is $1.50
        stock_quantity=10,  # initial stock is 10
        minimum_stock=5
    )
    db_session.add(product)
    db_session.commit()
    
    # 2. Login as Employee
    client.post("/auth/login", data={"email": "testemployee@stockmate.com", "password": "employee123"})
    
    # 3. Create Purchase Order Draft (Buy 20 Orange Juices at $1.80 each)
    po_payload = {
        "supplier_id": supplier.id,
        "items": [
            {
                "product_id": product.id,
                "quantity": 20,
                "cost_price": 1.80
            }
        ]
    }
    response = client.post("/purchases/create", json=po_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    
    # Check draft created in database
    po = db_session.query(PurchaseOrder).filter(PurchaseOrder.supplier_id == supplier.id).first()
    assert po is not None
    assert po.status == "Pending"
    assert po.total_amount == 36.00  # 20 * 1.80 = $36.00
    assert len(po.items) == 1
    
    # 4. Employee attempts to complete the Purchase Order (should be blocked with 403 Forbidden)
    response_complete_fail = client.post(f"/purchases/{po.id}/complete", follow_redirects=False)
    assert response_complete_fail.status_code == 403  # owner check fails
    
    # Verify stock has not changed yet
    db_session.refresh(product)
    assert product.stock_quantity == 10
    assert product.cost_price == 1.50
    
    # 5. Login as Owner
    client.post("/auth/login", data={"email": "testowner@stockmate.com", "password": "owner123"})
    
    # 6. Owner completes the Purchase Order
    response_complete_success = client.post(f"/purchases/{po.id}/complete", follow_redirects=False)
    assert response_complete_success.status_code == 303
    assert response_complete_success.headers["location"].startswith("/purchases?success")
    
    # Verify stock replenished & cost updated
    db_session.refresh(po)
    db_session.refresh(product)
    assert po.status == "Completed"
    assert product.stock_quantity == 30  # 10 + 20 = 30
    assert product.cost_price == 1.80   # Updated to $1.80 (latest cost price)
    
    # Verify audit log recorded
    audit = db_session.query(AuditLog).filter(AuditLog.action == "PURCHASE_COMPLETE").first()
    assert audit is not None
    assert f"Purchase Order ID {po.id}" in audit.details
