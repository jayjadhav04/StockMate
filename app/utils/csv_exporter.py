import csv
from sqlalchemy.orm import Session
from app.models.product import Product
from app.models.customer import Customer
from app.models.sale import Sale

def export_products_csv(db: Session, stream):
    """
    Exports product records into a CSV writer stream.
    """
    writer = csv.writer(stream)
    writer.writerow([
        "Product ID", "Product Name", "Category", 
        "Stock Quantity", "Min Stock Alert", "Cost Price (₹)", 
        "Mfg Date", "Expiry Date", "Expiry Status"
    ])
    
    products = db.query(Product).order_by(Product.id.asc()).all()
    for p in products:
        writer.writerow([
            p.id,
            p.product_name,
            p.category.name,
            p.stock_quantity,
            p.minimum_stock,
            f"{p.cost_price:.2f}",
            p.manufacturing_date.strftime("%Y-%m-%d") if p.manufacturing_date else "-",
            p.expiry_date.strftime("%Y-%m-%d") if p.expiry_date else "-",
            p.expiry_status
        ])

def export_customers_csv(db: Session, stream):
    """
    Exports customer records into a CSV writer stream.
    """
    writer = csv.writer(stream)
    writer.writerow(["Customer ID", "Customer Name", "Phone", "Email", "Address", "Registered Date"])
    
    customers = db.query(Customer).order_by(Customer.id.asc()).all()
    for c in customers:
        writer.writerow([
            c.id,
            c.customer_name,
            c.phone,
            c.email,
            c.address,
            c.created_at.strftime("%Y-%m-%d")
        ])

def export_sales_csv(sales_list: list, stream, show_profit: bool = False):
    """
    Exports a list of sales/invoices into a CSV writer stream.
    If show_profit is True, appends the profit column.
    """
    writer = csv.writer(stream)
    
    headers = ["Invoice #", "Customer Name", "Billed By", "Date & Time", "Total Bill (₹)"]
    if show_profit:
        headers.append("Total Profit (₹)")
        
    writer.writerow(headers)
    
    for s in sales_list:
        row = [
            s.invoice_number,
            s.customer.customer_name,
            s.employee.full_name,
            s.sale_date.strftime("%Y-%m-%d %H:%M"),
            f"{s.total_amount:.2f}"
        ]
        if show_profit:
            row.append(f"{s.total_profit:.2f}")
        writer.writerow(row)
