import json
import random
import os
import psycopg2

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
            employee_number int NOT NULL,
            key_id int NOT NULL,
            FOREIGN KEY (employee_number) REFERENCES employees(id) ON DELETE CASCADE,
            FOREIGN KEY (key_id) REFERENCES keys(id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()


def generate_user_name(first_name, last_name, accounts_names):
    base_account_name = f'{first_name[0]}{last_name}'

    if base_account_name not in accounts_names:
        return base_account_name
    else:
        index = 1
        base_account_name_numeric = base_account_name + str(index)
        while base_account_name_numeric in accounts_names:
            index += 1
            base_account_name_numeric = base_account_name + str(index)
        return base_account_name_numeric


def add_user_account(first_name, last_name, employee_number, key_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT account_name FROM users")
    existing_accounts = [row[0] for row in cursor.fetchall()]

    account_name = generate_user_name(first_name, last_name, existing_accounts)

    cursor.execute(
        "INSERT INTO users (account_name, employee_number, key_id) VALUES (%s, %s, %s)",
        (account_name, employee_number, key_id))

    conn.commit()
    cursor.close()
    conn.close()
    return account_name
