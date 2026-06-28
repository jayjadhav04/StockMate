# 📦 StockMate - Inventory & Sales Management System

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)](https://www.mysql.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71105?style=for-the-badge&logo=SQLAlchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com)
[![Railway](https://img.shields.io/badge/Railway-131415?style=for-the-badge&logo=railway&logoColor=white)](https://railway.app)

**Manage Stock. Track Sales. Grow Business.**

StockMate is a modern, high-performance, transaction-safe Inventory and Sales Management System built to streamline daily business operations. Developed primarily to demonstrate core backend engineering proficiency in Python, RESTful API design, database normalization, and robust concurrency handling.

Whether you run a single retail storefront or coordinate a multi-channel operation, StockMate provides business owners and counter employees with a secure, responsive, and visually stunning tool to control stock levels, log sales, track procurement, and analyze financial performance.

### Ideal For:
* **Retail Stores & Shop Owners** – Fast invoice generation and real-time stock deductions.
* **Wholesalers & Distributors** – Track bulk purchasing lists and vendor relations.
* **Warehouses & Small Businesses** – Automated alerts for low stock levels and expiring products.

---

## 📋 Table of Contents
1. [🌐 Live Demo](#-live-demo)
2. [📸 Screenshots](#-screenshots)
3. [🚀 Features](#-features)
4. [🛠️ Technology Stack](#%EF%B8%8F-technology-stack)
5. [📂 Project Structure](#-project-structure)
6. [🗄️ Database Schema](#%EF%B8%8F-database-schema)
7. [🔄 Application Workflow](#-application-workflow)
8. [💻 Installation Guide](#-installation-guide)
9. [🔑 Environment Variables](#-environment-variables)
10. [📖 API Documentation](#-api-documentation)
11. [☁️ Deployment](#%EF%B8%8F-deployment)
12. [🔮 Future Improvements](#-future-improvements)
13. [🎯 Why This Project](#-why-this-project)
14. [✍️ Author](#%EF%B8%8F-author)

---

## 🌐 Live Demo

Explore the live application and interactive API documentation:

| Service | Endpoint / Link | Description |
| :--- | :--- | :--- |
| **Frontend / Web App** | https://stock-mate.up.railway.app/ | Access the dashboards and UI screens. |
| **API Documentation** | https://stock-mate.up.railway.app//docs | Interactive Swagger UI for REST endpoint testing. |

---

## 📸 Screenshots

### 🔑 Login Page
![Login Page](screenshots/login.png)
*Provides secure, session-managed entry points for Owners and Employees.*

### 📊 Owner Dashboard
![Owner Dashboard](screenshots/owner_dashboard.png)
*Provides Owner-only financial analytics including daily sales, monthly revenue trend charts, and alert summaries.*

### 👤 Employee Dashboard
![Employee Dashboard](screenshots/employee_dashboard.png)
*A clean workspace for sales agents to record sales and check products.*

### 📦 Product Management
![Product Management](screenshots/products_page.png)
*Real-time product grid with automated visual warnings for Expired, Low Stock, and Expiring Soon items.*

### 👥 Customer Management
![Customer Management](screenshots/customers.png)
*Maintains a registry of customer contact details and transaction history.*

### 🏭 Supplier Management
![Supplier Management](screenshots/suppliers.png)
*Tracks contact information and purchase history for replenishment vendors.*

### 🛍️ Purchase Module (Replenishments)
![Purchase Module](screenshots/purchases.png)
*Enables employees to draft restocking orders, awaiting owner approval before updating inventory.*

### 🛒 Sales Module (Point of Sale)
![Sales Module](screenshots/sales_create.png)
*Interactive multi-item checkout builder that dynamically computes prices, sub-totals, and GST.*

### 📄 Dynamic Invoice PDF
![Invoice PDF](screenshots/invoice_pdf.png)
*Sample dynamic invoice generated programmatically with full business branding and GST calculations.*

### 📈 Reports & Analytics
![Reports Page](screenshots/reports.png)
*Provides customized date filters for profit analysis and data exporting.*

### 📉 Analytical Charts
![Charts View](screenshots/charts.png)
*Chart.js graphics representing revenue flow, category distributions, and top product metrics.*

### 🔔 System Notifications
![Notifications Screen](screenshots/notifications.png)
*Displays warning notifications for low stock thresholds and approaching expiry dates.*

### ⚙️ Audit Logs
![Settings Page](screenshots/audit_logs.png)
*Security Audit Logs*

---

## 🚀 Features

### 🔐 Authentication & Security
* **Secure Login / Logout**: Uses HTTP-Only secure cookies to manage state and session tokens.
* **Role-Based Access Control (RBAC)**: Restricts administrative modules (Audit Logs, Reports, Employee registers) strictly to `Owner` accounts, while permitting counter checkout processes to `Employee` credentials.
* **Password Hashing**: Implements secure one-way hashing algorithms (bcrypt) to safely store credentials.
* **Route Protection**: Validates JWT payloads on every requests to prevent session hijacking.

### 📦 Inventory Control
* **Product Catalog**: Full CRUD capabilities for recording product cost prices, selling prices, stock levels, and expiry alerts.
* **Nested Categories**: Standardizes hierarchical categorization with cascading validations.
* **Low Stock Warnings**: Computes dynamic warnings whenever product levels drop below their minimum threshold.
* **Expiry Tracking**: Flags items automatically as "Expired" or "Expiring Soon" (within 30 days) to prevent waste.
* **Search & Filters**: Multi-parameter search by keyword, category, and alert status.

### 🛒 Sales & Billing
* **Customer Ledger**: Integrates customer contact numbers and emails with their historical purchases.
* **Multi-Product Checkout**: Point-of-sale interface to build, adjust, and submit sales with live price updates.
* **Atomic Deductions**: Utilizes database-level locking (`.with_for_update()`) to prevent race conditions during concurrent checkouts, rolling back transactions completely if any item check fails.
* **Profit Calculations**: Calculates revenue margins per line item and stores aggregates for financial reporting.

### 🏭 Purchases & Restocking
* **Supplier Directory**: Manages vendor contacts and logs previous procurement transactions.
* **Purchase Orders**: Standardizes replenishment drafts. Stock levels and average unit cost prices are only updated upon Owner approval.

### 📊 Business Intelligence & Exports
* **Live Dashboards**: High-impact dashboards rendering charts for Daily Sales, Monthly Trends, Category distribution, and Top-Selling inventory.
* **Financial Reports**: Custom interval queries (Today, Yesterday, Last 7 Days, Month, Year, Custom Range) compiling net revenues and margins.
* **Data Streams**: Streams large datasets directly into CSV files for Excel importing.
* **PDF Billing**: Instantly generates clean PDF invoice sheets formatted with client and server information using ReportLab.

---

## 🛠️ Technology Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Backend** | **Python** | Core application runtime. |
| | **FastAPI** | High-performance, asynchronous REST framework. |
| **Frontend** | **HTML5 & CSS3** | Dynamic page structures. |
| | **Bootstrap 5** | Responsive layout styling and dark custom glassmorphic overrides. |
| | **Vanilla JavaScript** | Asynchronous fetches, dynamic form rows, and modal interactions. |
| **Database** | **MySQL / SQLite** | Relational transactional databases. |
| | **SQLAlchemy** | Database Object Relational Mapper (ORM) with transaction manager. |
| **Validation** | **Pydantic** | Strict runtime schema parsing and request verification. |
| **Visualizations** | **Chart.js** | Renders HTML5 Canvas dashboards. |
| **Reporting** | **ReportLab** | Generates dynamic PDF invoice streams. |
| **Deployment** | **Railway** | Cloud hosting with automated continuous deployment. |
| **VCS** | **Git & GitHub** | Source code management. |

---

## 📂 Project Structure

```text
StockMate/
│
├── app/
│   ├── auth/              # Security dependencies, role tokens, and bcrypt hashing
│   ├── models/            # SQLAlchemy Database structures (User, Sale, Product, etc.)
│   ├── routers/           # REST Endpoints and HTML controllers
│   ├── schemas/           # Pydantic schemas for payload validation
│   ├── static/            # Frontend assets (CSS styles, JS modules, logo images)
│   ├── templates/         # Jinja2 templates (dashboard layouts, invoices, modals)
│   ├── utils/             # Business helpers (PDF builder, CSV exporter, logger)
│   ├── config.py          # Settings parser with environment variables
│   ├── database.py        # Database engine setup and local session getters
│   └── main.py            # Main ASGI app init, middleware, and startup triggers
│
├── tests/                 # Unit and integration test suites (Pytest)
├── screenshots/           # UI image walkthrough files
├── Procfile               # Railway process commands
├── runtime.txt            # Python compiler instructions
├── requirements.txt       # Python dependency package manifests
└── stockmate.db           # SQLite database for local development
```

---

## 🗄️ Database Schema

StockMate uses a normalized, relational database schema configured with foreign key constraints, indexes for rapid querying, and cascade rules.

```
                   ┌────────────┐
                   │ Categories │
                   └──────┬─────┘
                          │ 1
                          │
                          │ *
┌───────────┐      ┌──────┴───┐      ┌────────────┐
│ Suppliers ├──────┤ Products ├──────┤ Sale_Items │
└─────┬─────┘ 1    └──────────┘ *    └─────┬──────┘
      │                                    │ *
      │ 1                                  │
┌─────┴─────┐                              │ 1
│ Purchases │                              │
└─────┬─────┘ 1                            │
      │                                    │
      │ *                                  │
┌─────┴────────────────┐             ┌─────┴───┐
│ Purchase_Order_Items │             │  Sales  │
└──────────────────────┘             └────┬────┘
                                          │ *
                                          │
                                          │ 1
                                     ┌────┴──────┐
                                     │ Customers │
                                     └───────────┘
```

### Table Definitions & Relationships:

1. **`users`**
   * Stores credential hashes and system designations (`Owner` or `Employee`).
   * *Relationships*: Has a one-to-many relationship with `sales` (employee who processed the sale) and `audit_logs` (user who triggered the event).
2. **`categories`**
   * Manages classifications for products (e.g., Electronics, Groceries).
   * *Relationships*: One-to-many relationship with `products`. Removing a category cascades validation to prevent orphaned products.
3. **`products`**
   * Stores core inventory specifications, pricing structures, stock counts, and expiry thresholds.
   * *Relationships*: Belongs to a single `category`. Linked to `sale_items` and `purchase_order_items`.
4. **`suppliers`**
   * Stores procurement vendor profiles.
   * *Relationships*: Has a one-to-many relationship with `purchases` orders.
5. **`purchases`**
   * Tracks restocking requests. Statuses include `Pending` and `Completed`.
   * *Relationships*: Belongs to a `supplier`. Has many `purchase_order_items`.
6. **`purchase_order_items`**
   * Stores the breakdown details of a purchase order (product quantities, unit costs).
   * *Relationships*: Connects `purchases` to the specific `products` being restocked.
7. **`customers`**
   * Records retail and corporate clients.
   * *Relationships*: One-to-many relationship with `sales` invoices.
8. **`sales`**
   * Represents transactions. Compiles revenue totals, profit aggregates, and GST.
   * *Relationships*: Linked to a `customer` and the processing `employee` (from `users`). Has many `sale_items`.
9. **`sale_items`**
   * Individual invoice lines storing historical transaction pricing and counts.
   * *Relationships*: Pairs each `sales` record to `products`.
10. **`company_profile` / `business_settings`**
    * Stores meta details like Business Name, Address, GST Registration Number, and Tax rates used in PDF headers.
11. **`notifications`**
    * Caches warnings for products with low stock levels or expiring dates.
12. **`audit_logs`**
    * Records security-sensitive operations. Tracks timestamps, actions, target descriptions, and IP addresses.

---

## 🔄 Application Workflow

```
[Login Screen] ──> [Verify Credentials] ──> [Check Role: Owner or Employee?]
                                                     │
       ┌─────────────────────────────────────────────┴─────────────────────────────────────────────┐
       ▼                                                                                           ▼
[Owner Dashboard]                                                                         [Employee Dashboard]
* Visual Analytics & Charts                                                               * Personal Sales Counter
* View Full Audit Logs & Reports                                                           * Quick POS Access
* Manage Employee Accounts & CRUD Controls                                                * Search Inventory Details
       │                                                                                           │
       └──────────────────────────────────────┬────────────────────────────────────────────────────┘
                                              ▼
                                      [Billing/POS Screen]
                                              │
                                              ▼
                                 [Select Customer & Products]
                                              │
                                              ▼
                               [Atomic Stock & Inventory Checks]
                                              │
                    ┌─────────────────────────┴─────────────────────────┐
                    ▼ (Success)                                         ▼ (Insufficent Stock)
        [Update Stock Quantities]                                [Rollback Transaction]
                    │                                                   │
                    ▼                                                   ▼
       [Commit Sale & Log Actions]                               [Display Error Banner]
                    │
                    ▼
     [Generate Dynamic PDF Invoice]
```

---

## 💻 Installation Guide

### Prerequisites
* Python 3.9 or higher.
* MySQL Server (optional, defaults to SQLite local developer database).

### Step 1: Clone Repository
Clone this repository to your local directory:
```bash
git clone https://github.com/YOUR_GITHUB_REPOSITORY/StockMate.git
cd StockMate
```

### Step 2: Create Virtual Environment
Initialize a local python virtual environment to isolate package dependencies:
```bash
python -m venv .venv
```

### Step 3: Activate Virtual Environment
Activate the environment:
* **Windows (Command Prompt / PowerShell)**:
  ```powershell
  .venv\Scripts\activate
  ```
* **macOS / Linux**:
  ```bash
  source .venv/bin/activate
  ```

### Step 4: Install Requirements
Install all dependencies using pip:
```bash
pip install -r requirements.txt
```

### Step 5: Configure Environment Variables
Copy the environment variables template and configure your parameters:
```bash
cp .env.example .env
```
*(On Windows cmd: `copy .env.example .env`)*

Update the values inside `.env` (such as changing the Database URL to point to SQLite or your MySQL Server instance).

### Step 6: Start Server
Run the FastAPI development server:
```bash
uvicorn app.main:app --port 8000 --reload
```
On startup, StockMate automatically sets up all database tables and seeds default user roles.

### Step 7: Open Browser
Navigate to: [http://127.0.0.1:8000](http://127.0.0.1:8000)
Log in with the default credentials:
* **Owner Dashboard**: `owner@stockmate.com` (password: `owner123`)
* **Employee Dashboard**: `employee@stockmate.com` (password: `employee123`)

---

## 🔑 Environment Variables

Create a `.env` file in the project root directory:

```env
# Application Settings
APP_ENV=development # Options: development, production
SECRET_KEY=yoursecretkey123!@# # Used for signing cookie sessions

# Database Configuration
# For SQLite (default development):
DATABASE_URL=sqlite:///./stockmate.db

# For MySQL (production):
# DATABASE_URL=mysql+pymysql://username:password@localhost:3306/stockmate_db
```

---

## 📖 API Documentation

StockMate exposes standard OpenAPI documentation, allowing developers to explore and interact with backend REST APIs:

* **Interactive Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **Alternative ReDoc UI**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## ☁️ Deployment

### Deploying to Railway

StockMate is pre-configured for instant deployment on [Railway](https://railway.app):

1. **Procfile**: Tells Railway to launch Uvicorn and bind to the correct host and port:
   ```text
   web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
2. **Environment Configuration**: Add these variables in the Railway console:
   * `APP_ENV` = `production`
   * `SECRET_KEY` = `[YourRandomCryptographicKeyString]`
   * `DATABASE_URL` = `[YourProductionMySQLConnectionString]`
3. **Database Migrations**: Database tables are initialized automatically on application startup.

---

## 🔮 Future Improvements

Here is the development roadmap for future releases of StockMate:
* 🔍 **Barcode Scanner Integration** – Scan item barcodes directly via browser camera.
* 📱 **QR Codes on Invoices** – Render payment QR codes on dynamic invoices.
* ✉️ **Email Invoices** – E-mail PDF invoices to customers automatically.
* 💬 **WhatsApp Invoices** – Send digital invoice receipts directly to WhatsApp.
* 🏢 **Multi-Store Management** – Manage inventory across multiple stores.
* 🚚 **Warehouse Transfers** – Coordinate stock movements between warehouse units.
* 📱 **Native Mobile App** – Develop a companion app for inventory checks on the go.
* 🤖 **AI Demand Forecasting** – Predict restocking requirements based on sales trends.

---

## 🎯 Why This Project

This project was built to demonstrate proficiency in core web backend concepts:
* **REST APIs**: Designed using clean HTTP methods and structured JSON payloads.
* **Authentication & Authorization**: Handled via HTTP-only cookie sessions and JWT parsing.
* **Database Design**: Structured relational schema with database-level indexes and atomic operations.
* **Business Logic**: Real-world operations like cost accounting, tax collection, and product life-cycle alerts.
* **Data Validations**: Strict client/server validation using Pydantic.
* **Reporting**: Programmatic file generation (PDF & CSV streams) built dynamically.

It showcases the ability to design, build, and deploy production-ready systems using the Python ecosystem.

---

## ✍️ Author

**Jay Jadhav** 
* **LinkedIn**: https://linkedin.com/in/jayjadhav04
* **Email**: jaydjadhav1111@gmail.com
* **Portfolio**: https://jay-jadhav-portfolio.vercel.app/

---
