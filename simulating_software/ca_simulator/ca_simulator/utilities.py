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
        CREATE TABLE IF NOT EXISTS keys (
            id SERIAL PRIMARY KEY,
            public_key BYTEA
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()


def register_key(public_key):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO keys (public_key) VALUES (%s) RETURNING id",
        (psycopg2.Binary(public_key),))
    key_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return key_id


def get_key(key_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT public_key FROM keys where id = (%s)",
        (key_id,))
    public_key = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return public_key
