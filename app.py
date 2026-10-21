
import os
import sqlite3
from flask import Flask, request, redirect, render_template_string

app = Flask(__name__)

DATABASE = "/app/data/inventory.db"

os.makedirs("/app/data", exist_ok=True)


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                quantity INTEGER NOT NULL
            )
        """)


@app.route("/")
def index():
    with get_db() as conn:
        products = conn.execute(
            "SELECT * FROM products ORDER BY id DESC"
        ).fetchall()

    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Inventory Management</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 900px;
                margin: 40px auto;
                padding: 0 15px;
            }
            input, button {
                padding: 10px;
                margin: 5px 2px;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }
            th, td {
                padding: 12px;
                border: 1px solid #ddd;
                text-align: left;
            }
            th { background: #eee; }
        </style>
    </head>
    <body>
        <h1>Inventory Management</h1>

        <h2>Add Product</h2>
        <form action="/add" method="post">
            <input name="name" placeholder="Product name" required>
            <input name="price" type="number" min="0"
                   step="0.01" placeholder="Price" required>
            <input name="quantity" type="number" min="0"
                   placeholder="Quantity" required>
            <button type="submit">Add Product</button>
        </form>

        <h2>Product List</h2>
        <table>
            <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Price</th>
                <th>Quantity</th>
                <th>Action</th>
            </tr>

            {% for p in products %}
            <tr>
                <td>{{ p.id }}</td>
                <td>{{ p.name }}</td>
                <td>{{ "%.2f"|format(p.price) }}</td>
                <td>{{ p.quantity }}</td>
                <td>
                    <form action="/delete/{{ p.id }}" method="post">
                        <button type="submit">Delete</button>
                    </form>
                </td>
            </tr>
            {% endfor %}
        </table>
    </body>
    </html>
    """, products=products)


@app.route("/add", methods=["POST"])
def add_product():
    name = request.form.get("name", "").strip()

    try:
        price = float(request.form["price"])
        quantity = int(request.form["quantity"])

        if not name or price < 0 or quantity < 0:
            raise ValueError

    except (ValueError, KeyError):
        return "Invalid product details", 400

    with get_db() as conn:
        conn.execute(
            """INSERT INTO products (name, price, quantity)
               VALUES (?, ?, ?)""",
            (name, price, quantity)
        )

    return redirect("/")


@app.route("/delete/<int:product_id>", methods=["POST"])
def delete_product(product_id):
    with get_db() as conn:
        conn.execute(
            "DELETE FROM products WHERE id = ?",
            (product_id,)
        )

    return redirect("/")


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
