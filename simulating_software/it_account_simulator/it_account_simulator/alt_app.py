from flask import Flask, request, Response
import json
import psycopg2
import os
import utilities as u  # Assuming you still use `create_user_account`

app = Flask(__name__)

# Database Configuration
DB_CONFIG = {
    "dbname": "mydb",
    "user": "user",
    "password": "pass",
    "host": "localhost",  # Change if using a remote server
    "port": "5432",
}


# Establish DB Connection
def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)


# Create Table if it Doesn't Exist
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            account_name VARCHAR(100) UNIQUE NOT NULL,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            employee_number VARCHAR(50) NOT NULL
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()


# Initialize Database
init_db()


@app.route('/accounts', methods=['GET'])
def get_accounts():
    """Fetch all accounts from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT account_name, employee_number FROM users")
    accounts = {row[0]: row[1] for row in cursor.fetchall()}

    cursor.close()
    conn.close()

    return Response(json.dumps(accounts), status=200, mimetype='application/json')


@app.route('/register', methods=['POST'])
def register_account():
    """Register a new account and store it in the database."""
    if not request.is_json:
        return Response("Invalid Request", status=400, mimetype='application/json')

    data = request.get_json()

    first_name = data['first_name']
    last_name = data['last_name']
    employee_number = data['employee_num']

    # Fetch existing account names
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT account_name FROM users")
    existing_accounts = [row[0] for row in cursor.fetchall()]

    # Generate a unique account name
    account_name = u.create_user_account(first_name, last_name, existing_accounts)

    # Insert new user into DB
    cursor.execute(
        "INSERT INTO users (account_name, first_name, last_name, employee_number) VALUES (%s, %s, %s, %s)",
        (account_name, first_name, last_name, employee_number)
    )
    conn.commit()

    cursor.close()
    conn.close()

    return Response(json.dumps({'account': account_name}), status=200, mimetype='application/json')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=4530)
