import datetime
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.category import Category
from app.models.product import Product
from app.models.customer import Customer
from app.models.supplier import Supplier
from app.models.purchase_order import PurchaseOrder
from app.models.purchase_order_item import PurchaseOrderItem
from app.models.sale import Sale
from app.models.sale_item import SaleItem

def seed_demo_data(db: Session):
    """
    Seeds realistic demo data if the database is currently empty of categories.
    """
    # 1. Check if seeding is needed
    if db.query(Category).count() > 0:
        return

    print("Seeding realistic demo business data...")

    # Fetch users for referencing
    owner = db.query(User).filter(User.role == "Owner").first()
    employee = db.query(User).filter(User.role == "Employee").first()
    
    owner_id = owner.id if owner else 1
    employee_id = employee.id if employee else 2

    # 2. Seed Categories
    electronics = Category(name="Electronics")
    groceries = Category(name="Groceries")
    apparel = Category(name="Apparel")
    stationery = Category(name="Stationery")
    
    db.add_all([electronics, groceries, apparel, stationery])
    db.flush()  # populate IDs

    # 3. Seed Products
    laptop = Product(
        product_name="Dell Laptop 15",
        category_id=electronics.id,
        description="Core i5, 8GB RAM, 512GB SSD",
        cost_price=42000.0,
        gst_rate=18.0,
        stock_quantity=12,
        minimum_stock=3
    )
    phone = Product(
        product_name="Samsung Galaxy M14",
        category_id=electronics.id,
        description="5G Mobile Phone, Dark Blue",
        cost_price=11000.0,
        gst_rate=12.0,
        stock_quantity=25,
        minimum_stock=5
    )
    rice = Product(
        product_name="Basmati Rice 5kg",
        category_id=groceries.id,
        description="Premium long grain rice",
        cost_price=420.0,
        gst_rate=0.0,
        stock_quantity=45,
        minimum_stock=10
    )
    cable = Product(
        product_name="USB-C Cable 1m",
        category_id=electronics.id,
        description="Braided fast charging cable",
        cost_price=120.0,
        gst_rate=18.0,
        stock_quantity=2,  # Low stock trigger
        minimum_stock=5
    )
    tshirt = Product(
        product_name="Cotton Polo T-Shirt",
        category_id=apparel.id,
        description="Black classic polo shirt",
        cost_price=300.0,
        gst_rate=5.0,
        stock_quantity=35,
        minimum_stock=8
    )
    notebook = Product(
        product_name="A5 Spiral Notebook",
        category_id=stationery.id,
        description="160 pages ruled journal",
        cost_price=45.0,
        gst_rate=12.0,
        stock_quantity=80,
        minimum_stock=15
    )

    db.add_all([laptop, phone, rice, cable, tshirt, notebook])
    db.flush()

    # 4. Seed Customers
    raj = Customer(
        customer_name="Raj Sharma",
        phone="9876543210",
        email="raj@example.com",
        address="102 MG Road, Mumbai"
    )
    priya = Customer(
        customer_name="Priya Patel",
        phone="9123456780",
        email="priya@example.com",
        address="45 SG Highway, Ahmedabad"
    )
    vikram = Customer(
        customer_name="Vikram Singh",
        phone="9911223344",
        email="vikram@example.com",
        address="12 Nehru Place, Delhi"
    )
    db.add_all([raj, priya, vikram])
    db.flush()

    # 5. Seed Suppliers
    tech_world = Supplier(
        supplier_name="Tech World Distributors",
        contact_name="Amit Kumar",
        email="orders@techworld.com",
        phone="9988776655",
        address="77 Nehru Place, Delhi"
    )
    farms = Supplier(
        supplier_name="Organic Farms & Co.",
        contact_name="Sanjay Shah",
        email="sanjay@organicfarms.com",
        phone="9876123456",
        address="Gram GIDC, Anand, Gujarat"
    )
    db.add_all([tech_world, farms])
    db.flush()

    # 6. Seed Purchase Orders
    # Completed PO
    po1 = PurchaseOrder(
        supplier_id=tech_world.id,
        total_amount=220000.0,
        status="Completed",
        created_at=datetime.datetime.utcnow() - datetime.timedelta(days=10)
    )
    db.add(po1)
    db.flush()
    po1_item = PurchaseOrderItem(
        purchase_order_id=po1.id,
        product_id=laptop.id,
        quantity=5,
        cost_price=44000.0,
        line_total=220000.0
    )
    db.add(po1_item)

    # Pending PO
    po2 = PurchaseOrder(
        supplier_id=farms.id,
        total_amount=4200.0,
        status="Pending",
        created_at=datetime.datetime.utcnow() - datetime.timedelta(days=1)
    )
    db.add(po2)
    db.flush()
    po2_item = PurchaseOrderItem(
        purchase_order_id=po2.id,
        product_id=rice.id,
        quantity=10,
        cost_price=420.0,
        line_total=4200.0
    )
    db.add(po2_item)

    # 7. Seed Sales (staggered historical dates for daily & monthly reports/charts)
    today = datetime.date.today()
    
    # Helper function to insert sale
    def insert_historical_sale(invoice_num, customer_id, emp_id, days_ago, items_list, payment_method="Cash"):
        sale_time = datetime.datetime.combine(today - datetime.timedelta(days=days_ago), datetime.time(14, 30))
        
        # Calculate totals
        total_amount = 0.0
        total_profit = 0.0
        total_gst = 0.0
        
        sale = Sale(
            invoice_number=invoice_num,
            customer_id=customer_id,
            employee_id=emp_id,
            total_amount=0.0,
            total_profit=0.0,
            total_gst=0.0,
            payment_method=payment_method,
            sale_date=sale_time
        )
        db.add(sale)
        db.flush()

        sale_items = []
        for prod, qty, sell_price in items_list:
            line_total = sell_price * qty
            gst = round(line_total * (prod.gst_rate / 100), 2)
            profit = (sell_price - prod.cost_price) * qty
            
            total_amount += line_total
            total_gst += gst
            total_profit += profit

            item = SaleItem(
                sale_id=sale.id,
                product_id=prod.id,
                quantity=qty,
                cost_price=prod.cost_price,
                selling_price=sell_price,
                line_total=line_total,
                gst_amount=gst,
                line_profit=profit
            )
            db.add(item)
            
        sale.total_amount = round(total_amount, 2)
        sale.total_gst = round(total_gst, 2)
        sale.total_profit = round(total_profit, 2)

    # Sale 1: 4 days ago (Electronics)
    insert_historical_sale(
        "INV-000001",
        raj.id,
        employee_id,
        days_ago=4,
        items_list=[(laptop, 1, 55000.0), (phone, 1, 14000.0)],
        payment_method="Card"
    )

    # Sale 2: 3 days ago (Groceries)
    insert_historical_sale(
        "INV-000002",
        priya.id,
        owner_id,
        days_ago=3,
        items_list=[(rice, 3, 520.0), (cable, 1, 250.0)],
        payment_method="UPI"
    )

    # Sale 3: 2 days ago (Mix)
    insert_historical_sale(
        "INV-000003",
        vikram.id,
        employee_id,
        days_ago=2,
        items_list=[(tshirt, 2, 599.0), (notebook, 5, 80.0)],
        payment_method="Cash"
    )

    # Sale 4: Yesterday
    insert_historical_sale(
        "INV-000004",
        raj.id,
        employee_id,
        days_ago=1,
        items_list=[(phone, 2, 13500.0), (cable, 1, 240.0)],
        payment_method="UPI"
    )

    # Sale 5: Today
    insert_historical_sale(
        "INV-000005",
        priya.id,
        owner_id,
        days_ago=0,
        items_list=[(rice, 2, 540.0), (tshirt, 1, 550.0), (notebook, 3, 75.0)],
        payment_method="Cash"
    )

    # Commit all seeded data
    db.commit()
    print("Demo data seeded successfully!")
