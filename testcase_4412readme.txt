================================================================================
  STOCKMATE — MANUAL TEST CASES  |  File: testcase_4412readme.txt
  Version: 1.0  |  Date: 2026-06-28
  Base URL: http://127.0.0.1:8000
================================================================================

HOW TO USE THIS FILE
--------------------
- Run each test case in order (they build on each other).
- Each test has: STEP, WHAT TO DO, WHAT TO ENTER, EXPECTED RESULT.
- Mark each as [PASS] or [FAIL] as you test.
- Start the server first: run `uvicorn app.main:app --port 8000 --reload`

DEFAULT CREDENTIALS (auto-seeded on first run)
-----------------------------------------------
  Owner    Email: owner@stockmate.com     Password: owner123
  Employee Email: employee@stockmate.com  Password: employee123

================================================================================
SECTION 1 — AUTHENTICATION & LOGIN
================================================================================

TEST-001: Login Page Loads
--------------------------
Step 1 : Open browser → go to http://127.0.0.1:8000/auth/login
Step 2 : Confirm the page shows email and password fields.
Expected: Login form visible, no errors.
Result  : [    ]

---

TEST-002: Login with Wrong Password
------------------------------------
Step 1 : On login page, enter:
            Email    → owner@stockmate.com
            Password → wrongpassword
Step 2 : Click Login.
Expected: Error message shown — "Invalid credentials".
          User stays on the login page.
Result  : [    ]

---

TEST-003: Owner Login
----------------------
Step 1 : Enter:
            Email    → owner@stockmate.com
            Password → owner123
Step 2 : Click Login.
Expected: Redirected to Owner Dashboard.
          Left sidebar shows: Dashboard, Products, Categories,
          Customers, Suppliers, Purchases, Sales, Reports,
          Employees, Audit Logs.
Result  : [    ]

---

TEST-004: Employee Login
-------------------------
Step 1 : Log out from Owner (click Logout in top right).
Step 2 : Enter:
            Email    → employee@stockmate.com
            Password → employee123
Step 3 : Click Login.
Expected: Redirected to Employee Dashboard.
          Sidebar does NOT show: Reports, Employees, Audit Logs.
Result  : [    ]

---

TEST-005: Unauthenticated Redirect
------------------------------------
Step 1 : Log out.
Step 2 : Type http://127.0.0.1:8000/products in browser directly.
Expected: Redirected to /auth/login page (not shown products).
Result  : [    ]


================================================================================
SECTION 2 — CATEGORIES  (Login as Owner)
================================================================================

TEST-006: Add Category — Missing Name
--------------------------------------
Step 1 : Login as Owner → click "Categories" in sidebar.
Step 2 : In the "Add New Category" form, leave Name empty.
Step 3 : Click Save.
Expected: Validation error shown.
Result  : [    ]

---

TEST-007: Add Category — Electronics
--------------------------------------
Step 1 : In Categories page → Add form:
            Category Name → Electronics
            Description   → Electronic items and gadgets
Step 2 : Click Save.
Expected: "Electronics" appears in the category table.
Result  : [    ]

---

TEST-008: Add Category — Grocery
----------------------------------
Step 1 : Add form:
            Category Name → Grocery
            Description   → Daily food and grocery items
Step 2 : Click Save.
Expected: "Grocery" appears in the category table.
Result  : [    ]

---

TEST-009: Edit Category
------------------------
Step 1 : On the "Electronics" row, click Edit.
Step 2 : Change Description to → "Consumer Electronics".
Step 3 : Click Save.
Expected: Description updated in the table.
Result  : [    ]

---

TEST-010: Employee Cannot Access Categories (Create)
------------------------------------------------------
Step 1 : Login as Employee.
Step 2 : Navigate to http://127.0.0.1:8000/categories
Expected: Employee can VIEW categories list.
          But there is NO "Add New Category" form visible.
Result  : [    ]


================================================================================
SECTION 3 — PRODUCTS  (Login as Owner)
================================================================================

TEST-011: Add Product — Missing Required Fields
------------------------------------------------
Step 1 : Login as Owner → click "Products" → click "Add Product".
Step 2 : Leave all fields empty, click Save.
Expected: Form validation errors shown (product name, cost price required).
Result  : [    ]

---

TEST-012: Add Product — Laptop
-------------------------------
Step 1 : Products → Add Product. Enter:
            Product Name  → Dell Laptop
            Category      → Electronics
            Description   → 15 inch laptop
            Cost Price    → 45000
            GST Rate      → 18% — General Goods / Services
            Initial Stock → 10
            Min Stock     → 3
            Expiry Date   → (leave blank)
Step 2 : Click Save.
Expected: "Dell Laptop" appears in product list.
          Cost Price column shows ₹45000.00
          GST column (if visible to Owner) shows 18%.
Result  : [    ]

---

TEST-013: Add Product — Rice Bag (0% GST)
------------------------------------------
Step 1 : Add Product:
            Product Name  → Basmati Rice 5kg
            Category      → Grocery
            Description   → Premium Basmati Rice
            Cost Price    → 450
            GST Rate      → 0% — Exempt (Food, Medicine)
            Initial Stock → 50
            Min Stock     → 10
Step 2 : Click Save.
Expected: "Basmati Rice 5kg" in product list with cost ₹450.00, GST 0%.
Result  : [    ]

---

TEST-014: Add Product — Mobile Phone (12% GST)
-----------------------------------------------
Step 1 : Add Product:
            Product Name  → Samsung Galaxy M14
            Category      → Electronics
            Cost Price    → 12000
            GST Rate      → 12% — Standard Goods
            Initial Stock → 20
            Min Stock     → 5
Step 2 : Click Save.
Expected: Product added with 12% GST.
Result  : [    ]

---

TEST-015: Low Stock Alert
--------------------------
Step 1 : Add Product:
            Product Name  → USB Cable
            Category      → Electronics
            Cost Price    → 120
            GST Rate      → 18%
            Initial Stock → 2    ← LESS THAN MIN STOCK
            Min Stock     → 5
Step 2 : Click Save.
Step 3 : Go to Products list.
Expected: "USB Cable" row shows LOW STOCK warning/badge.
          Owner Dashboard also shows this product in the low-stock section.
Result  : [    ]

---

TEST-016: Edit Product
-----------------------
Step 1 : Click Edit on "Dell Laptop".
Step 2 : Change Cost Price → 47000.
Step 3 : Click Save.
Expected: Cost Price updated to ₹47000.00 in list.
Result  : [    ]

---

TEST-017: Employee Cannot See Cost Price
-----------------------------------------
Step 1 : Login as Employee → go to Products.
Expected: Product list visible.
          Cost Price column is HIDDEN (only visible to Owner).
Result  : [    ]


================================================================================
SECTION 4 — CUSTOMERS  (Owner or Employee)
================================================================================

TEST-018: Add Customer
-----------------------
Step 1 : Login as Owner → Customers → Add Customer.
            Name    → Raj Sharma
            Phone   → 9876543210
            Email   → raj@example.com
            Address → 12 MG Road, Mumbai
Step 2 : Click Save.
Expected: "Raj Sharma" appears in customer table.
Result  : [    ]

---

TEST-019: Add Second Customer
------------------------------
Step 1 : Add Customer:
            Name    → Priya Patel
            Phone   → 9123456780
            Email   → priya@example.com
            Address → 45 SG Highway, Ahmedabad
Step 2 : Click Save.
Expected: "Priya Patel" in customer table.
Result  : [    ]

---

TEST-020: Search Customer
--------------------------
Step 1 : In the search bar on Customers page, type "Raj".
Expected: Only "Raj Sharma" shows in results.
Result  : [    ]


================================================================================
SECTION 5 — SUPPLIERS  (Login as Owner)
================================================================================

TEST-021: Add Supplier
-----------------------
Step 1 : Login as Owner → Suppliers → Add Supplier.
            Supplier Name → Tech World Distributors
            Contact Name  → Amit Kumar
            Email         → amit@techworld.com
            Phone         → 9988776655
            Address       → 77 Nehru Place, Delhi
Step 2 : Click Save.
Expected: Supplier appears in supplier list.
Result  : [    ]


================================================================================
SECTION 6 — PURCHASE ORDERS  (Login as Owner)
================================================================================

TEST-022: Create Purchase Order
--------------------------------
Step 1 : Login as Owner → Purchases → New Purchase Order.
Step 2 : Select Supplier → Tech World Distributors.
Step 3 : Add Item:
            Product  → Dell Laptop
            Quantity → 5
            Cost     → 44000
Step 4 : Add another Item:
            Product  → Samsung Galaxy M14
            Quantity → 10
            Cost     → 11500
Step 5 : Note the Grand Total shown.
Step 6 : Click "Submit Purchase Order".
Expected: Purchase order created with status "Pending".
          Grand Total = (5 × 44000) + (10 × 11500) = ₹3,35,000.
Result  : [    ]

---

TEST-023: Approve Purchase Order (Stock Should Increase)
---------------------------------------------------------
Step 1 : In Purchase Orders list → click "Approve" on the pending order.
Expected: Status changes from "Pending" to "Approved".
Step 2 : Go to Products → check "Dell Laptop" stock.
Expected: Stock increased from 10 to 15 (10 existing + 5 from PO).
Step 3 : Check "Samsung Galaxy M14" stock.
Expected: Stock increased from 20 to 30.
Result  : [    ]


================================================================================
SECTION 7 — SALES / INVOICE  (Login as Employee)
================================================================================

TEST-024: Create Invoice — with GST + Cash Payment
----------------------------------------------------
Step 1 : Login as Employee → Sales → New Invoice.
Step 2 : Select Customer → Raj Sharma.
Step 3 : Add Item:
            Product       → Dell Laptop (shows GST: 18%)
            Quantity      → 1
            Selling Price → 55000
Step 4 : Observe invoice items table:
            Subtotal (ex-GST) = ₹55,000.00
            GST (18%)         = ₹9,900.00
            Grand Total       = ₹64,900.00
Step 5 : Payment Method → select 💵 Cash.
Step 6 : Click "Process & Save Invoice".
Expected: Redirected to Sales list.
          Invoice INV-000001 visible.
          Payment badge shows: Cash (green).
Result  : [    ]

---

TEST-025: Create Invoice — UPI Payment + 0% GST Product
---------------------------------------------------------
Step 1 : Sales → New Invoice.
Step 2 : Select Customer → Priya Patel.
Step 3 : Add Item:
            Product       → Basmati Rice 5kg (shows GST: 0%)
            Quantity      → 5
            Selling Price → 550
Step 4 : Observe:
            Subtotal = ₹2,750.00
            GST      = ₹0.00
            Grand Total = ₹2,750.00
Step 5 : Payment Method → select 📱 UPI.
Step 6 : Process Invoice.
Expected: Invoice created. Payment badge shows: UPI (blue).
Result  : [    ]

---

TEST-026: Stock Deduction After Sale
-------------------------------------
Step 1 : After TEST-024, go to Products → Dell Laptop.
Expected: Stock reduced from 15 to 14 (one laptop was sold).
Step 2 : After TEST-025 → Basmati Rice 5kg stock.
Expected: Stock reduced from 50 to 45.
Result  : [    ]

---

TEST-027: Cannot Sell More Than Available Stock
------------------------------------------------
Step 1 : Sales → New Invoice.
Step 2 : Select Customer → Raj Sharma.
Step 3 : Add Item:
            Product       → USB Cable
            Quantity      → 10   ← only 2 in stock
            Selling Price → 150
Step 4 : Click "Add to Invoice".
Expected: Error message shown:
          "Cannot add item. Requested quantity (10) exceeds available stock (2)..."
Result  : [    ]

---

TEST-028: Employee Sees Only Own Invoices
------------------------------------------
Step 1 : Create an invoice as Employee (employee@stockmate.com).
Step 2 : Sales list → note the invoices shown.
Expected: Only invoices created by this employee are visible.
          (Owner's sales are NOT shown to Employee)
Result  : [    ]

---

TEST-029: Download PDF Invoice
--------------------------------
Step 1 : In Sales list → find INV-000001.
Step 2 : Click "PDF" download button.
Expected: PDF file downloads (browser downloads it).
          PDF shows:
          → Invoice # INV-000001
          → Customer: Raj Sharma
          → Payment: Cash
          → Subtotal row
          → GST row (₹9,900.00)
          → Grand Total row
Result  : [    ]


================================================================================
SECTION 8 — OWNER DASHBOARD  (Login as Owner)
================================================================================

TEST-030: Dashboard KPI Cards
-------------------------------
Step 1 : Login as Owner → Dashboard.
Expected KPI cards visible:
  → Total Products (should be 4 — Laptop, Rice, Samsung, USB Cable)
  → Inventory Value (₹ amount based on cost prices × stock)
  → Total Revenue (₹ from completed sales)
  → Net Profit (Revenue minus cost of goods)
  → Recent invoices table at bottom.
Result  : [    ]

---

TEST-031: Dashboard Charts
----------------------------
Step 1 : On Owner Dashboard scroll down.
Expected: Monthly Revenue vs Profit bar chart visible.
          Daily Sales line chart visible.
          Both charts show ₹ labels (not $).
Result  : [    ]

---

TEST-032: Owner Sees All Invoices
-----------------------------------
Step 1 : Owner → Sales.
Expected: ALL invoices visible (both owner-created and employee-created).
          Each invoice row shows:
          → Invoice Number
          → Customer Name
          → Billed By
          → Subtotal
          → Profit
          → Payment badge (Cash / UPI / Card)
Result  : [    ]


================================================================================
SECTION 9 — REPORTS  (Login as Owner)
================================================================================

TEST-033: Reports — Today Filter
----------------------------------
Step 1 : Login as Owner → Reports.
Step 2 : Select "Today" preset (default).
Expected: Metrics show:
  → Total Revenue ₹ (sum of today's invoices subtotals)
  → Net Profit ₹
  → GST Collected ₹ (sum of GST from today's invoices)
  → Items Sold count
  → Customers Billed count
Result  : [    ]

---

TEST-034: Reports — Product-wise Profit Table
----------------------------------------------
Step 1 : On Reports page, scroll down below the Sales Log.
Expected: "Product-wise Profit Breakdown" table visible.
          Columns: Product Name | Units Sold | Revenue | Profit | Margin %
          "Dell Laptop" row shows:
            Units Sold = 1
            Revenue    = ₹55,000.00
            Profit     = ₹55,000 - ₹47,000 = ₹8,000.00
            Margin %   = 14.5% (badge in yellow/orange)
Result  : [    ]

---

TEST-035: Reports — Custom Date Range
--------------------------------------
Step 1 : Reports → select "Custom Date Range".
Step 2 : Enter Start Date = today's date, End Date = today's date.
Step 3 : Click Apply.
Expected: Same data as "Today" filter.
Result  : [    ]

---

TEST-036: Export CSV
---------------------
Step 1 : Reports → click "Export CSV".
Expected: CSV file downloads.
          Open CSV — headers should be:
          "Invoice #, Customer Name, Billed By, Date & Time, Total Bill (₹), Total Profit (₹)"
Result  : [    ]

---

TEST-037: Employee Cannot Access Reports
-----------------------------------------
Step 1 : Login as Employee.
Step 2 : Type http://127.0.0.1:8000/reports in browser.
Expected: Redirected to 403 Forbidden page.
          Reports link NOT visible in sidebar.
Result  : [    ]


================================================================================
SECTION 10 — EMPLOYEE MANAGEMENT  (Login as Owner)
================================================================================

TEST-038: View Employees
-------------------------
Step 1 : Login as Owner → Employees.
Expected: Table shows at least 2 employees:
          "Default Owner" (Owner role)
          "Default Employee" (Employee role)
Result  : [    ]

---

TEST-039: Add New Employee
---------------------------
Step 1 : Add Employee:
            Full Name → Sneha Verma
            Email     → sneha@stockmate.com
            Password  → sneha123
            Role      → Employee
Step 2 : Click Save.
Expected: Sneha Verma appears in the employees table.
Result  : [    ]

---

TEST-040: New Employee Login
-----------------------------
Step 1 : Logout → login with:
            Email    → sneha@stockmate.com
            Password → sneha123
Expected: Successfully logged in as Employee.
          Employee Dashboard visible.
Result  : [    ]

---

TEST-041: Employee Cannot Access Employee Management
-----------------------------------------------------
Step 1 : While logged in as Employee (Sneha).
Step 2 : Type http://127.0.0.1:8000/employees in browser.
Expected: 403 Forbidden page shown.
Result  : [    ]


================================================================================
SECTION 11 — AUDIT LOGS  (Login as Owner)
================================================================================

TEST-042: Audit Log Entries
-----------------------------
Step 1 : Login as Owner → Audit Logs.
Expected: Table shows event history including entries like:
          → INVOICE_CREATE — Billed invoice INV-000001...
          → INVOICE_CREATE — Billed invoice INV-000002...
          → PRODUCT_CREATE — Created product 'Dell Laptop'...
          → PURCHASE_APPROVE — Approved order...
          Each row shows: User | Action | Details | IP | Timestamp
Result  : [    ]

---

TEST-043: Employee Cannot Access Audit Logs
--------------------------------------------
Step 1 : Login as Employee.
Step 2 : Type http://127.0.0.1:8000/audit-logs in browser.
Expected: 403 Forbidden page shown.
Result  : [    ]


================================================================================
SECTION 12 — UI / THEME  (Any Role)
================================================================================

TEST-044: Dark / Light Mode Toggle
------------------------------------
Step 1 : Click the 🌙 / ☀️ theme toggle button in the sidebar (top).
Expected: Page switches between dark and light mode.
Step 2 : Refresh the page.
Expected: Theme preference is REMEMBERED (persists across refresh).
Step 3 : In Dark Mode — check that all text is clearly readable (white/light).
Result  : [    ]

---

TEST-045: Sidebar Collapse
----------------------------
Step 1 : Click the "Hide" / collapse button on the sidebar.
Expected: Sidebar slides/collapses. Main content area expands to full width.
Step 2 : Click again to expand.
Expected: Sidebar returns. Layout returns to normal.
Step 3 : Refresh page.
Expected: Sidebar collapse/expand state is REMEMBERED.
Result  : [    ]

---

TEST-046: Sidebar Scrolling
-----------------------------
Step 1 : If sidebar has many links (narrow screen or long list),
         try scrolling the sidebar independently.
Expected: Sidebar scrolls independently without affecting main content.
Result  : [    ]


================================================================================
SECTION 13 — SECURITY  (Login as Owner)
================================================================================

TEST-047: Docs Hidden in Production
-------------------------------------
Step 1 : In .env file set APP_ENV=production and restart server.
Step 2 : Go to http://127.0.0.1:8000/docs
Expected: 404 Not Found — Swagger UI NOT accessible.
Step 3 : Go to http://127.0.0.1:8000/redoc
Expected: 404 Not Found — ReDoc NOT accessible.
Step 4 : Change APP_ENV back to development.
Result  : [    ]

---

TEST-048: Docs Visible in Development
---------------------------------------
Step 1 : Ensure APP_ENV=development in .env, restart server.
Step 2 : Go to http://127.0.0.1:8000/docs
Expected: Swagger UI fully loads with all API routes listed.
Result  : [    ]

---

TEST-049: Health Check Endpoint
---------------------------------
Step 1 : Go to http://127.0.0.1:8000/health (no login needed).
Expected: JSON response: {"status": "healthy"}
Result  : [    ]


================================================================================
SECTION 14 — FULL END-TO-END FLOW TEST
================================================================================

This is a combined test that runs through the entire business cycle.

TEST-050: Full Business Day Simulation
---------------------------------------
Step 1  : Login as Owner.
Step 2  : Add category: "Furniture".
Step 3  : Add product:
              Name  → Wooden Chair
              GST   → 12%
              Cost  → 2500
              Stock → 30
              Min   → 5
Step 4  : Add customer:
              Name  → Vikram Singh  |  Phone → 9911223344
Step 5  : Go to Suppliers → add supplier:
              Name → Office Furniture Hub
Step 6  : Go to Purchases → create PO:
              Supplier → Office Furniture Hub
              Product  → Wooden Chair  |  Qty: 20  |  Cost: 2400
              Approve the order.
Step 7  : Check stock — Wooden Chair should now be 50 (30 + 20).
Step 8  : Login as Employee.
Step 9  : Create Invoice:
              Customer       → Vikram Singh
              Product        → Wooden Chair (GST: 12%)
              Qty            → 3
              Selling Price  → 3200
              Payment        → 💳 Card
              Process Invoice.
Step 10 : Verify:
              Subtotal = 3 × 3200 = ₹9,600
              GST 12%  = ₹1,152
              Grand Total = ₹10,752
              Wooden Chair stock = 47
Step 11 : Login as Owner → check Dashboard:
              Revenue includes ₹9,600 (subtotal).
Step 12 : Go to Reports → Product Profit Breakdown:
              Wooden Chair | Units: 3 | Revenue: ₹9,600 | Profit: ₹2,100 | Margin: 21.9% (green)
Step 13 : Download PDF of the invoice.
              Verify PDF shows: Payment: Card, Subtotal, GST ₹1,152, Grand Total ₹10,752.
Step 14 : Check Audit Logs — should show INVOICE_CREATE entry.

Expected: ALL steps above produce correct, consistent results.
Result  : [    ]


================================================================================
TEST SUMMARY SHEET
================================================================================

Section 1  — Authentication        : TEST-001 to TEST-005    [ /5 passed ]
Section 2  — Categories            : TEST-006 to TEST-010    [ /5 passed ]
Section 3  — Products              : TEST-011 to TEST-017    [ /7 passed ]
Section 4  — Customers             : TEST-018 to TEST-020    [ /3 passed ]
Section 5  — Suppliers             : TEST-021                [ /1 passed ]
Section 6  — Purchase Orders       : TEST-022 to TEST-023    [ /2 passed ]
Section 7  — Sales / Invoice       : TEST-024 to TEST-029    [ /6 passed ]
Section 8  — Owner Dashboard       : TEST-030 to TEST-032    [ /3 passed ]
Section 9  — Reports               : TEST-033 to TEST-037    [ /5 passed ]
Section 10 — Employee Management   : TEST-038 to TEST-041    [ /4 passed ]
Section 11 — Audit Logs            : TEST-042 to TEST-043    [ /2 passed ]
Section 12 — UI / Theme            : TEST-044 to TEST-046    [ /3 passed ]
Section 13 — Security              : TEST-047 to TEST-049    [ /3 passed ]
Section 14 — Full End-to-End       : TEST-050                [ /1 passed ]

TOTAL TESTS : 50
PASSED      : ___
FAILED      : ___
SKIPPED     : ___

TESTER NAME : _______________________
TEST DATE   : _______________________
APP VERSION : 1.0.0

================================================================================
END OF TEST FILE — StockMate Manual QA  |  testcase_4412readme.txt
================================================================================
