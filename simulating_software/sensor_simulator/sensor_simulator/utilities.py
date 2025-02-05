import hashlib
import datetime
import random
import json
import psycopg2
import os

# Database Configuration
DB_CONFIG = {
    "dbname": "mydb",
    "user": "user",
    "password": "pass",
    "host": "localhost",
    "port": "5432",
}


# Establish DB Connection
def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)


# Initialize Database Tables
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS insiders (
            id SERIAL PRIMARY KEY,
            account VARCHAR(255) UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS logs (
            id SERIAL PRIMARY KEY,
            scaled_timestamp DOUBLE PRECISION NOT NULL,
            ssp_id INT NOT NULL,
            emp_id INT NOT NULL,
            authorized BOOLEAN NOT NULL,
            FOREIGN KEY (emp_id) REFERENCES employees(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
            FOREIGN KEY (ssp_id) REFERENCES ssps(id) ON DELETE CASCADE
        );
    """)

    conn.commit()
    cursor.close()
    conn.close()


def register_insider(account):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO insiders (account) VALUES (%s) ON CONFLICT (account) DO NOTHING", (account,))
    conn.commit()
    cursor.close()
    conn.close()


def get_insiders():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT account FROM insiders")
    insiders = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return insiders


def get_logs():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT scaled_timestamp, ssp_id, emp_id, authorized FROM logs")
    logs = cursor.fetchall()
    cursor.close()
    conn.close()
    return logs


def insert_log(current_time, emp_id, ssp_id):
    authorized = False
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT section_id FROM employees where id = (%s)", (emp_id,))
    sect_id = cursor.fetchone()
    if sect_id is not None:
        sect_id = sect_id[0]

        cursor.execute("SELECT division_id FROM sections where id = (%s)", (sect_id,))
        div_id = cursor.fetchone()
        if div_id is not None:
            div_id = div_id[0]

            cursor.execute("SELECT id FROM sections where division_id = (%s)", (div_id,))
            common_sections = cursor.fetchall()
            if len(common_sections) > 0:
                section_ids = [i[0] for i in common_sections]

                cursor.execute("SELECT * FROM section_ssps where ssp_id = (%s) and sect_id IN %s",
                               (ssp_id, tuple(section_ids)))
                hits = cursor.fetchall()
                authorized = len(hits) > 0

    cursor.execute(
        "INSERT INTO logs (scaled_timestamp, ssp_id, emp_id, authorized) VALUES (%s, %s, %s, %s)",
        (current_time, ssp_id, emp_id, authorized))

    conn.commit()
    cursor.close()
    conn.close()
