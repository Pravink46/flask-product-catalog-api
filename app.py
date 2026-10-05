from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
DB_NAME = "catalog.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()

@app.route("/api/products", methods=["GET"])
def get_products():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, category, price, stock FROM products")
    rows = cursor.fetchall()
    conn.close()
    
    products = [
        {"id": r[0], "name": r[1], "category": r[2], "price": r[3], "stock": r[4]}
        for r in rows
    ]
    return jsonify({"status": "success", "count": len(products), "data": products}), 200

@app.route("/api/products", methods=["POST"])
def add_product():
    payload = request.get_json()
    if not payload or not all(k in payload for k in ("name", "category", "price", "stock")):
        return jsonify({"status": "error", "message": "Missing required fields"}), 400
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO products (name, category, price, stock) VALUES (?, ?, ?, ?)",
        (payload["name"], payload["category"], float(payload["price"]), int(payload["stock"]))
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    
    return jsonify({"status": "success", "message": "Product created", "id": new_id}), 201

@app.route("/api/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    deleted = cursor.rowcount
    conn.close()
    
    if deleted == 0:
        return jsonify({"status": "error", "message": "Product not found"}), 404
    return jsonify({"status": "success", "message": "Product deleted successfully"}), 200

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)