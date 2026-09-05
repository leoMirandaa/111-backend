from flask import Flask, jsonify, request
import sqlite3
# from responses-advanced import created_response, success_response, not_found

app = Flask(__name__)

DB_NAME = "online-store.db"

def init_db():
    conn = sqlite3.connect(DB_NAME) # Opens a connection to the database file named 'budget_manager.db'
    cursor = conn.cursor() # Creates a Cursor/Tool that lets us send commands(SELECT, INSERT...) to the database.

    # Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT UNIQUE NOT NULL,
      price REAL NOT NULL,
      category TEXT NOT NULL,
      image TEXT NOT NULL              
    )
    """)

    # Expenses Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS coupons (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      code TEXT NOT NULL,
      discount INTEGER NOT NULL
    )
    """)

    conn.commit() # Save changes to the dabase
    conn.close() # Close the connection to the database.


@app.get("/api/health")
def health_check():
   return jsonify({"status": "OK"}), 200


# --------- PRODUCTS ---------
@app.post("/api/products")
def create_product():
    data = request.get_json()
    name = data.get("name")
    price = data.get("price")
    category = data.get("category")
    image = data.get("image")

    conn = sqlite3.connect(DB_NAME) # Opens a connection to the database file named 'budget_manager.db'
    cursor = conn.cursor() # Creates a Cursor/Tool that lets us send commands(SELECT, INSERT...) to the database.

    # allowed_categories = {"Food", "Education", "Entertainment"}
    # if category not in allowed_categories:
    #     return jsonify({"error": "Invalid category"}), 400

    # Insert a new user into DB
    cursor.execute("INSERT INTO products (name, price, category, image) VALUES (?, ?, ?, ?)", (name, price, category, image)) # Executes an SQL statement
    conn.commit() # Save changes to the database
    conn.close() # Closes the connection to the database.

    return jsonify({
        "success": True,
        "message": "Product created successfully"
    }), 201
    

# GET http://127.0.0.1:5000/api/users
@app.get("/api/products")
def get_products():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row # Allows column values to be retrieved by name, row["username"]
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products_db = cursor.fetchall() # fetchall, retrieves all rows from the result of the query, returns a list of tuples
    #  [(1, "gamer pc", 999.99), (2, "iphone 19", 799.99)]
    #   row[0]-> id.  row[1]-> name, row[2]-> price
    conn.close()

    products = []
    for row in products_db:
        print(dict(row))
        products.append(dict(row))

        # for row in rows:
    #     products.append({
    #         "id": row[0],
    #         "name": row[1],
    #         "price": row[2]
    #     })
        
    return jsonify({
        "success": True,
        "message": "Products retrieved successfully",
        "data": products
    }), 200


# GET http://127.0.0.1:5000/api/users/2
@app.get("/api/products/<int:product_id>")
def get_product_by_id(product_id):
    connection = sqlite3.connect(DB_NAME) 
    connection.row_factory = sqlite3.Row # Allow colums values to be retrieved by name, row["id"]
    cursor = connection.cursor()
    cursor.execute("SELECT id, name, price, category, image FROM products WHERE id = ?", (product_id,))
    product_db = cursor.fetchone()

    if not product_db:
        return jsonify({
            "success": False,
            "message": "Product not found"
        }), 404

    print(f"product_db = {product_db}")
    product_information = dict(product_db)
    connection.close()

    return jsonify({
        "success": True,
        "message": "Product retrieved successfully",
        "data": product_information
    }), 200


# --- Session #2 ---

# PUT http://127.0.0.1:5000/api/products/<#>
@app.put('/api/products/<int:product_id>')
def update_product_by_id(product_id):
    updated_product = request.get_json()
    
    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    
    # Validation
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product_db = cursor.fetchone()
    print(f"****** product_db: {product_db}")

    if not product_db:
        connection.close()
        return jsonify({
            "success": True,
            "message": "Product not found"
        }), 404
    
    name = updated_product["name"]
    price = updated_product["price"]
    category = updated_product.get("category", product_db["category"])
    image = updated_product.get("image", product_db["image"])


    allowed_categories = {"Food", "Education", "Entertainment"}
    if category not in allowed_categories:
        return jsonify({"error": "Invalid category"}), 400

    cursor.execute("UPDATE products SET name=?, price=?, category=?, image=? WHERE id=?", (name, price, category, image, product_id))
    connection.commit()
    connection.close()

    return jsonify({
        "success": True,
        "message": "Product updated successfully"
    }), 200 


# http://127.0.0.1:5000/api/products/2
@app.delete("/api/products/<int:product_id>")
def delete_product(product_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Validate if user exists
    cursor.execute("SELECT * FROM products WHERE id=?", (product_id,)) # execute(), executes an SQL statement(SELECT,INSERT...)
    if not cursor.fetchone(): #fetchone(), retrieves a single row from the result, useful when expecting only one record
        conn.close()
        return jsonify({'message': "Product not found"}), 404


    cursor.execute("DELETE FROM products WHERE id=?", (product_id,))
    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Product deleted successfully"
    }), 200


# --------- COUPONS ---------
@app.post("/api/coupons")
def create_coupon():
    new_coupon = request.get_json()
    print(new_coupon)

    code = new_coupon.get("code", "")
    discount = new_coupon.get("discount", "")

    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO coupons (code, discount) VALUES (?, ?)""", (code, discount))
    connection.commit()
    connection.close()

    return jsonify({
        "success": True,
        "message": "Coupon created successfully"
    }), 201


# MINI-CHALLENGE: get all the coupons
@app.get('/api/coupons')
def get_coupons():
    # http://127.0.0.1:5000/api/expenses?user_id=3
    # user_id = request.args.get("user_id")

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # if user_id:
    #     cursor.execute("SELECT * FROM expenses where user_id=?", (user_id))
    # else:
    #     cursor.execute("SELECT * from expenses")

    cursor.execute("SELECT * from coupons")

    coupons_db = cursor.fetchall()
    conn.close()

    coupons_list = []
    for coupon in coupons_db:
        coupons_list.append(dict(coupon))

    return jsonify({
            "success": True,
            "message": "Coupons retrieved successfully",
            "data": coupons_list
        }), 200


# GET http://127.0.0.1:5000/api/coupons/2
@app.get("/api/coupons/<int:coupon_id>")
def get_coupon_by_id(coupon_id):
    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM coupons WHERE id = ?", (coupon_id,))
    coupon_db = cursor.fetchone()

    if not coupon_db:
        return jsonify({
            "success": False,
            "message": "Coupon not found"
        }), 404

    print(f"coupon {dict(coupon_db)}")
    coupon_information = dict(coupon_db)
    connection.close()

    return jsonify({
        "success": True,
        "message": "Expense retrieved successfully",
        "data": coupon_information
    }), 200



# DELETE http://127.0.0.1:5000/api/coupons/2
@app.delete("/api/coupons/<int:coupon_id>")
def delete_coupon_by_id(coupon_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM coupons WHERE id = ?", (coupon_id,))
    coupon_db = cursor.fetchone()

    if not coupon_db:
        return jsonify({
            "success": False,
            "message": "Coupon not found"
        }), 404

    cursor.execute("DELETE FROM coupons WHERE id = ?",(coupon_id,))
    connection.commit()
    connection.close()

    return jsonify({
        "success": True,
        "message": "Coupon deleted successfully"
    }), 200


@app.put("/api/coupons/<int:coupon_id>")
def update_coupon(coupon_id):
    data = request.get_json()
    code = data.get("code", "")
    discount = data.get("discount", 0)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM coupons WHERE id=?", (coupon_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({"message": "Coupon not found"}), 404

    cursor.execute("""
        UPDATE coupons
        SET code=?, discount=?
        WHERE id=?
    """, (code, discount, coupon_id))

    conn.commit()
    conn.close()

    return jsonify({"message": "Coupon updated successfully"})


if __name__ == "__main__":
  init_db()
  app.run(debug=True)