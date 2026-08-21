# 🌸 DX-Fragrance

DX-Fragrance is a modern and elegant perfume e-commerce website designed to provide customers with a smooth fragrance shopping experience.

The website includes a customer-facing shopping interface and a separate admin panel for managing products, orders, customers, and other website data.

---

## ✨ Features

### 👤 Customer Panel
- Browse available perfumes
- View perfume details
- View fragrance notes and descriptions
- Add products to cart
- Place orders
- Customer registration and login
- Customer account management

### 🔐 Admin Panel
- Secure admin login
- Admin dashboard
- Add new perfumes
- Edit product details
- Delete products
- Manage product stock
- View customer information
- Manage orders
- View sales/revenue information

### 🗄️ Database
- SQLite database
- User authentication
- Product management
- Order management
- Customer data management

---

## 🛠️ Technologies Used

- **Frontend:** HTML5, CSS3, JavaScript
- **Backend:** Python, Flask
- **Database:** SQLite
- **Templating:** Jinja2
- **Authentication:** Flask-based authentication
- **Deployment:** Render
- **Version Control:** Git & GitHub

---

## 📁 Project Structure

```text
DX-Fragrance/
│
├── app/
│   ├── __init__.py
│   ├── routes/
│   ├── models/
│   ├── services/
│   ├── templates/
│   │   ├── admin/
│   │   └── ...
│   └── static/
│       ├── css/
│       ├── js/
│       └── images/
│
├── tests/
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_orders.py
│   └── test_products.py
│
├── setup_db.py
├── requirements.txt
├── run.py
├── .gitignore
└── README.md