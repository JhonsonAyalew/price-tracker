from flask import Flask, render_template, send_file, jsonify
import sqlite3
import pandas as pd
import io
from config import DB_PATH

app = Flask(__name__)

# -------------------------
# Helpers
# -------------------------
def get_connection():
    return sqlite3.connect(DB_PATH)

def get_price_history(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT price, recorded_at FROM price_history "
        "WHERE product_id=? ORDER BY recorded_at ASC",
        (product_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    dates = [row[1] for row in rows]
    prices = [row[0] for row in rows]
    return dates, prices

def get_dashboard_stats():
    """Return total count, min, max, avg price across all products."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*), MIN(price), MAX(price), AVG(price) FROM products")
    total, lowest, highest, avg = cursor.fetchone()
    conn.close()
    return total or 0, lowest or 0, highest or 0, avg or 0

def get_price_change(product_id):
    """
    Calculate price change = latest price - first recorded price.
    Returns 0 if not enough data.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT price FROM price_history WHERE product_id=? ORDER BY recorded_at ASC LIMIT 1",
        (product_id,)
    )
    first = cursor.fetchone()
    cursor.execute(
        "SELECT price FROM price_history WHERE product_id=? ORDER BY recorded_at DESC LIMIT 1",
        (product_id,)
    )
    last = cursor.fetchone()
    conn.close()
    if not first or not last:
        return 0
    return round(last[0] - first[0], 2)

def get_similar_products(product_id, limit=4):
    """Return up to `limit` products from the same source with closest price."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT source, price FROM products WHERE id=?", (product_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return []
    source, price = row
    cursor.execute(
        """
        SELECT id, name, price
        FROM products
        WHERE source=? AND id!=?
        ORDER BY ABS(price - ?) ASC
        LIMIT ?
        """,
        (source, product_id, price, limit)
    )
    products = []
    for r in cursor.fetchall():
        pid, name, p_price = r
        change = get_price_change(pid)
        products.append({
            "id": pid,
            "name": name,
            "price": p_price,
            "change": change
        })
    conn.close()
    return products

# -------------------------
# Routes
# -------------------------
@app.route("/")
def dashboard():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price FROM products ORDER BY name ASC")
    products = []
    for pid, name, price in cursor.fetchall():
        change = get_price_change(pid)
        products.append({
            "id": pid,
            "name": name,
            "price": price,
            "change": change
        })
    conn.close()

    total_count, lowest_price, highest_price, avg_price = get_dashboard_stats()

    return render_template(
        "dashboard.html",
        products=products,
        total_count=total_count,
        lowest_price=lowest_price,
        highest_price=highest_price,
        avg_price=round(avg_price, 2)
    )

@app.route("/product/<int:product_id>")
def product_detail(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price, url, source FROM products WHERE id=?",
                   (product_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return "Product not found", 404

    change = get_price_change(product_id)
    product = {
        "id": row[0],
        "name": row[1],
        "price": row[2],
        "url": row[3],
        "source": row[4],
        "change": change
    }

    dates, prices = get_price_history(product_id)
    similar_products = get_similar_products(product_id)

    return render_template(
        "product.html",
        product=product,
        dates=dates,
        prices=prices,
        similar_products=similar_products
    )

# -------------------------
# Export Routes
# -------------------------
@app.route("/export/<format>")
def export_data(format):
    conn = get_connection()
    query = """
    SELECT p.id AS product_id, p.name, p.url, p.source,
           ph.price, ph.recorded_at
    FROM price_history ph
    JOIN products p ON ph.product_id = p.id
    ORDER BY ph.recorded_at DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    if format == "csv":
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode()),
            mimetype="text/csv",
            as_attachment=True,
            download_name="price_data.csv",
        )

    elif format == "json":
        return jsonify(df.to_dict(orient="records"))

    elif format == "excel":
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="PriceData")
        output.seek(0)
        return send_file(
            output,
            mimetype=("application/vnd.openxmlformats-"
                      "officedocument.spreadsheetml.sheet"),
            as_attachment=True,
            download_name="price_data.xlsx",
        )

    return "Unsupported format", 400


# ✅ Start Flask server
if __name__ == "__main__":
    app.run(debug=True)
