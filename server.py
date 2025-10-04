from flask import Flask, jsonify, request
import sqlite3
from datetime import date

app = Flask(__name__)

DB_NAME = "budget_manager.db"

def init_db():
    conn = sqlite3.connect(DB_NAME) # Opens a connection to the database file named 'budget_manager.db'
    cursor = conn.cursor() # Creates a Cursor/Tool that lets us send commands(SELECT, INSERT...) to the database.

    # Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT UNIQUE NOT NULL,
      password TEXT NOT NULL              
    )
    """)

    # Expenses Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT,
      description TEXT NOT NULL,
      amount INT NOT NULL,
      date TEXT NOT NULL,
      category TEXT NOT NULL,
      user_id INTEGER,
      FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    conn.commit() # Save changes to the dabase
    conn.close() # Close the connection to the database.


# @app.route("/api/health", methods=["GET"])
# def health_check():
#     return jsonify({"status": "OK"}), HTTPStatus.OK


@app.get("/api/health")
def health_check():
   return jsonify({"status": "OK"}), 200


# ---------| USER |---------
@app.post("/api/register")
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Insert a new user into DB
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit() # Save changes to the database
    conn.close()

    return jsonify({"message": "user registered successfully"}), 201


# http://127.0.0.1:5000/api/users/3
@app.get("/api/users/<int:user_id>")
def get_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row # Allows column values to be retrieved by name, row["username"]
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    row = cursor.fetchone()
    conn.close()

    return jsonify({"id": row["id"], "username": row["username"]}), 200


# http://127.0.0.1:5000/api/users/2
@app.put("/api/users/<int:user_id>") # Flask
def update_user(user_id): # Python
    data = request.get_json() # Flask
    username = data.get("username") # Python
    password = data.get("password") # Python

    conn = sqlite3.connect(DB_NAME) # sqlite3
    cursor = conn.cursor() # sqlite3

    # Validate if user exists
    cursor.execute("SELECT * from users where id=?", (user_id,)) # execute(), executes an SQL statement(SELECT,INSERT...)
    if not cursor.fetchone(): #fetchone(), retrieves a single row from the result, useful when expecting only one record
        conn.close()
        return jsonify({'message': "User not found"}), 404

    cursor.execute("UPDATE users SET username=?, password=? WHERE id=?", (username, password, user_id)) # SQL + sqlite3
    conn.commit() # sqlite3
    conn.close() # sqlite 3

    return jsonify({"message": "User updated successfully"}), 200 # Flask


# http://127.0.0.1:5000/api/users/2
@app.delete("/api/users/<int:user_id>")
def delete_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Validate if user exists
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,)) # execute(), executes an SQL statement(SELECT,INSERT...)
    if not cursor.fetchone(): #fetchone(), retrieves a single row from the result, useful when expecting only one record
        conn.close()
        return jsonify({'message': "User not found"}), 404


    cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "User deleted successfully"}), 200


@app.get("/api/users")
def get_users():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row # Allows column values to be retrieved by name, row["username"]
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall() # fetchall, retrieves all rows from the result of the query, returns a list of tuples
    conn.close()

    users = []
    for row in rows:
        user = {"id": row["id"], "username": row["username"], "password": row["password"]}
        users.append(user)
        
    return jsonify(users), 200


# ---------| EXPENSES |---------
@app.post("/api/expenses")
def create_expense():
    data = request.get_json()
    title = data.get("title")
    description = data.get("description")
    amount = data.get("amount")
    category = data.get("category")
    user_id = data.get("user_id")
    date_str = date.today()

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
      INSERT INTO expenses (title, description, amount, date, category, user_id)
      VALUES (?, ?, ?, ?, ?, ?)
    """, (title, description, amount, date_str, category, user_id))

    conn.commit()
    conn.close()

    return jsonify({"message": "Expense added successfully"}), 201



if __name__ == "__main__":
  init_db()
  app.run(debug=True)