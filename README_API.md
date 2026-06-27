# StockMate — API & Routes Reference

This document lists every URL route available in the StockMate application, explains what each one does, which role can access it, and what to expect as a response.

> **Base URL (Local Dev)**: `http://127.0.0.1:8000`  
> **Legend**: 🔵 Owner Only &nbsp;&nbsp; 🟢 Both Roles &nbsp;&nbsp; 🌐 Public (No Login Required)

---

## 🌐 Public Routes

### `GET /`
**Redirect to Login**
> Redirects any visitor to the login page. No authentication required.

---

### `GET /auth/login`
**Login Page**
> Displays the StockMate login form. Enter your registered email and password.
> - On success → redirected to your role dashboard.
> - On failure → login page reloads with an error banner.

---

### `POST /auth/login`
**Process Login Credentials**
> Handles the form submission from the login page. Verifies the email and password, creates a secure session cookie, and redirects accordingly.

---

### `GET /auth/logout`
🟢 **Logout**
> Clears your active session cookie and redirects back to the login page. Logs a `LOGOUT` audit event.

---

## 🏠 Dashboards

### `GET /owner/dashboard`
🔵 **Owner Dashboard**
> The Owner's main home screen. Displays:
> - 6 KPI cards: Total Revenue, Today's Revenue, Total Profit, Today's Profit, Total Bills, Today's Bills.
> - 2 alert badges: Low Stock count and Expiring Soon count.
> - 4 interactive Chart.js graphs: Daily Sales Bar, Monthly Revenue Line, Top Products Doughnut, Category Revenue Doughnut.
>
> _Attempting to access this as an Employee returns a 403 Forbidden page._

---

### `GET /employee/dashboard`
🟢 **Employee Dashboard**
> The Employee's home screen. Displays:
> - 3 KPI cards: Personal Today's Sales, Total Customers, Available Product Types.
> - Quick Action buttons for Products, Customers, and New Sale.
> - A table of the most recent 10 invoices processed by this employee.

---

## 📦 Products

### `GET /products`
🟢 **Products List Page**
> Displays all products in the inventory with their status badge (In Stock / Low Stock / Expiring Soon / Expired).
> Supports filtering by name keyword, category, and status.
> Owners see Add / Edit / Delete controls; Employees have read-only view.

---

### `POST /products`
🔵 **Create New Product**
> Accepts a form submission from the Add Product modal. Creates a new product record with the submitted name, category, cost price, selling price, stock quantity, minimum stock, manufacturing date, and expiry date. Logs a `PRODUCT_CREATE` audit event.

---

### `POST /products/{product_id}/update`
🔵 **Update Existing Product**
> Accepts the Edit Product form and updates the product record. Logs a `PRODUCT_UPDATE` audit event.

---

### `POST /products/{product_id}/delete`
🔵 **Delete a Product**
> Permanently removes the product from the inventory catalog. Logs a `PRODUCT_DELETE` audit event.

---

## 🏷️ Categories

### `GET /categories`
🟢 **Categories List Page**
> Lists all product categories, showing the category name, number of products linked to it, and the creation date.
> Owners see Add / Edit / Delete controls.

---

### `POST /categories`
🔵 **Create New Category**
> Accepts the Add Category form and inserts a new category. Logs a `CATEGORY_CREATE` audit event.

---

### `POST /categories/{category_id}/update`
🔵 **Update Category Name**
> Updates the name of an existing category.

---

### `POST /categories/{category_id}/delete`
🔵 **Delete Category**
> Deletes a category. Returns an error if any products are still linked to it. Logs a `CATEGORY_DELETE` audit event.

---

## 👥 Customers

### `GET /customers`
🟢 **Customers List Page**
> Lists all registered customers with their contact details and total number of purchases.
> Supports search by name or phone. Both roles can add and edit; only Owners can delete.

---

### `POST /customers`
🟢 **Register New Customer**
> Accepts the registration form and creates a new customer record. Logs a `CUSTOMER_CREATE` audit event.

---

### `POST /customers/{customer_id}/update`
🟢 **Update Customer Details**
> Updates a customer's name, phone, email, or address. Logs a `CUSTOMER_UPDATE` audit event.

---

### `POST /customers/{customer_id}/delete`
🔵 **Delete Customer**
> Deletes a customer record. Blocked if the customer has any existing invoices linked. Logs a `CUSTOMER_DELETE` audit event.

---

## 🛒 Sales & Invoices

### `GET /sales`
🟢 **Sales History Page**
> Lists all completed invoices in the system. Owners see all invoices from all employees; Employees see only their own.
> Supports search by invoice number, customer name, or date range.

---

### `GET /sales/create`
🟢 **New Invoice Builder Page**
> Displays the interactive invoice builder. Select a customer, add products with quantities, and see the running grand total update live.

---

### `POST /sales/create`
🟢 **Process & Finalize Invoice**
> Submits the completed invoice. Checks stock availability for every line item atomically. Deducts inventory, assigns a unique invoice number (e.g. `INV-000042`), and saves the sale. Logs a `SALE_CREATE` audit event.
> Returns a JSON response with invoice details on success.

---

### `GET /sales/{sale_id}/download`
🟢 **Download Invoice PDF**
> Streams a formatted PDF invoice for the given sale ID. Uses ReportLab to render the company header, customer details, itemized table, and totals. Can be printed or emailed directly.

---

### `POST /sales/{sale_id}/delete`
🔵 **Delete Invoice Record**
> Permanently removes a sale record. Logs a `SALE_DELETE` audit event. Does NOT restore stock (administrative deletion only).

---

## 🏭 Suppliers

### `GET /suppliers`
🟢 **Suppliers List Page**
> Lists all registered suppliers with their contact details.
> Employees can view; Owners can add, edit, and delete.

---

### `POST /suppliers`
🔵 **Register New Supplier**
> Creates a new supplier record. Logs a `SUPPLIER_CREATE` audit event.

---

### `POST /suppliers/{supplier_id}/update`
🔵 **Update Supplier Details**
> Updates supplier contact information. Logs a `SUPPLIER_UPDATE` audit event.

---

### `POST /suppliers/{supplier_id}/delete`
🔵 **Delete Supplier**
> Removes a supplier from the directory. Logs a `SUPPLIER_DELETE` audit event.

---

## 📋 Purchase Orders

### `GET /purchases`
🟢 **Purchase Orders List Page**
> Lists all purchase orders (Pending and Completed) with supplier, total cost, status, and the employee who created it.
> Owners see Approve and Delete buttons on Pending orders.

---

### `GET /purchases/create`
🟢 **New Purchase Order Builder Page**
> Interactive form for creating a restocking draft. Select supplier, add product line items with quantities and unit costs, and view the running total before submitting.

---

### `POST /purchases/create`
🟢 **Submit Purchase Order Draft**
> Saves the order as a `Pending` draft. No stock changes occur at this point. Redirects to the Purchase Orders list.

---

### `POST /purchases/{purchase_id}/complete`
🔵 **Approve & Complete Purchase Order**
> Owner-only action. Marks the order as `Completed`, increments product stock quantities by the purchased amounts, and updates each product's `cost_price` to the latest procurement cost. Logs a `PURCHASE_COMPLETE` audit event.

---

### `POST /purchases/{purchase_id}/delete`
🔵 **Delete Purchase Order**
> Removes a Pending purchase order draft. Cannot delete an already Completed order.

---

## 📊 Reports & Exports

### `GET /reports`
🔵 **Reports & Analytics Page**
> Full analytical dashboard. Filterable by date preset (Today, Yesterday, Last 7 Days, This Month, This Year, or Custom Range).
> Shows Revenue, Profit, Bill Count, Average Bill, Top Products, and Category breakdowns.

---

### `GET /reports/export/products`
🔵 **Export Products as CSV**
> Streams a `.csv` file containing the full inventory — all product names, categories, prices, stock levels, and dates.

---

### `GET /reports/export/customers`
🔵 **Export Customers as CSV**
> Streams a `.csv` file containing all customer records — name, phone, email, address, registration date.

---

### `GET /reports/export/sales`
🔵 **Export Sales as CSV**
> Streams a `.csv` file containing all invoice records with line-item detail — invoice number, customer, employee, date, total, profit.

---

## 👨‍💼 Employee Management

### `GET /employees`
🔵 **Employees List Page**
> Lists all user accounts (Owners and Employees) registered in the system, with their name, email, role badge, and creation date.

---

### `POST /employees`
🔵 **Add New Employee**
> Creates a new user account with a hashed password and an assigned role (Owner or Employee). Logs an `EMPLOYEE_CREATE` audit event.

---

### `POST /employees/{employee_id}/update`
🔵 **Update Employee Record**
> Updates name, email, or role of an existing user. Logs an `EMPLOYEE_UPDATE` audit event.

---

### `POST /employees/{employee_id}/delete`
🔵 **Delete Employee Account**
> Removes a user account from the system. An Owner cannot delete their own account (self-deletion lock). Logs an `EMPLOYEE_DELETE` audit event.

---

## 📜 Audit Logs

### `GET /audit-logs`
🔵 **Audit Logs Page**
> A chronological, paginated list of every significant system event. Each row shows the timestamp, the user who triggered it, the action code, a human-readable description, and the originating IP address.
> Filter by username or action type using the dropdowns.

---

## 🔧 Health & API

### `GET /health`
🌐 **Health Check**
> Returns a simple JSON response confirming the app is running:
> ```json
> { "status": "healthy", "app": "StockMate" }
> ```
> Useful for Railway deployment health monitoring.

---

### `GET /api/charts/data`
🔵 **Chart Data API (JSON)**
> Internal JSON endpoint consumed by the Owner Dashboard's Chart.js graphs.
> Returns structured data for Daily Sales, Monthly Revenue, Top Products, and Category Revenue charts.
> Example response structure:
> ```json
> {
>   "daily_sales": [...],
>   "monthly_revenue": [...],
>   "top_products": [...],
>   "category_revenue": [...]
> }
> ```

---

### `GET /docs`
🌐 **Swagger UI — Interactive API Explorer**
> FastAPI's built-in interactive API documentation page. Every route is listed and can be tested live directly from the browser. Useful for developers integrating with the StockMate backend.
> URL: `http://127.0.0.1:8000/docs`

---

### `GET /redoc`
🌐 **ReDoc — API Reference Docs**
> A clean, readable alternative to Swagger for browsing the full OpenAPI specification.
> URL: `http://127.0.0.1:8000/redoc`

---

## 📌 Quick Reference Table

| Route | Method | Role | Purpose |
|-------|--------|------|---------|
| `/` | GET | Public | Redirect to login |
| `/auth/login` | GET / POST | Public | Login form & authentication |
| `/auth/logout` | GET | Both | Clear session & logout |
| `/owner/dashboard` | GET | 🔵 Owner | Business KPIs & charts |
| `/employee/dashboard` | GET | 🟢 Both | Personal stats & quick actions |
| `/products` | GET / POST | 🟢 Both | View inventory / Add product |
| `/products/{id}/update` | POST | 🔵 Owner | Edit a product |
| `/products/{id}/delete` | POST | 🔵 Owner | Remove a product |
| `/categories` | GET / POST | 🟢 Both | View / Add categories |
| `/categories/{id}/update` | POST | 🔵 Owner | Edit a category |
| `/categories/{id}/delete` | POST | 🔵 Owner | Remove a category |
| `/customers` | GET / POST | 🟢 Both | View / Add customers |
| `/customers/{id}/update` | POST | 🟢 Both | Edit a customer |
| `/customers/{id}/delete` | POST | 🔵 Owner | Remove a customer |
| `/sales` | GET | 🟢 Both | View invoice history |
| `/sales/create` | GET / POST | 🟢 Both | Build & submit new invoice |
| `/sales/{id}/download` | GET | 🟢 Both | Download invoice PDF |
| `/sales/{id}/delete` | POST | 🔵 Owner | Delete an invoice record |
| `/suppliers` | GET / POST | 🟢 / 🔵 | View suppliers / Add supplier |
| `/suppliers/{id}/update` | POST | 🔵 Owner | Edit supplier details |
| `/suppliers/{id}/delete` | POST | 🔵 Owner | Remove a supplier |
| `/purchases` | GET | 🟢 Both | View purchase orders |
| `/purchases/create` | GET / POST | 🟢 Both | Build & submit PO draft |
| `/purchases/{id}/complete` | POST | 🔵 Owner | Approve PO & restock inventory |
| `/purchases/{id}/delete` | POST | 🔵 Owner | Remove a PO draft |
| `/reports` | GET | 🔵 Owner | Analytics & reporting |
| `/reports/export/products` | GET | 🔵 Owner | Download products CSV |
| `/reports/export/customers` | GET | 🔵 Owner | Download customers CSV |
| `/reports/export/sales` | GET | 🔵 Owner | Download sales CSV |
| `/employees` | GET / POST | 🔵 Owner | View / Add employees |
| `/employees/{id}/update` | POST | 🔵 Owner | Edit employee |
| `/employees/{id}/delete` | POST | 🔵 Owner | Remove employee |
| `/audit-logs` | GET | 🔵 Owner | View audit event log |
| `/health` | GET | Public | App health check |
| `/api/charts/data` | GET | 🔵 Owner | JSON chart data |
| `/docs` | GET | Public | Swagger UI |
| `/redoc` | GET | Public | ReDoc API reference |
