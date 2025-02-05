import json
import random
import os
import psycopg2

# Database Configuration
DB_CONFIG = {
    "dbname": "mydb",
    "user": "user",
    "password": "pass",
    "host": "localhost",  # Change for remote DB
    "port": "5432",
}


# Establish DB Connection
def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ssps (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS section_ssps (
            sect_id INT NOT NULL,
            ssp_id INT NOT NULL,
            PRIMARY KEY (sect_id, ssp_id),
            FOREIGN KEY (sect_id) REFERENCES sections(id) ON DELETE CASCADE,
            FOREIGN KEY (ssp_id) REFERENCES ssps(id) ON DELETE CASCADE
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()
    add_ssps()


def add_ssps():
    conn = get_db_connection()
    cursor = conn.cursor()
    with open("./ssp_simulator/ssp_names.json", 'r') as file_in:
        ssps = list(set(json.load(file_in)))

    for ssp in ssps:
        cursor.execute("INSERT INTO ssps (name) VALUEs (%s)", (ssp,))
    conn.commit()
    cursor.close()
    conn.close()


def get_ssp_list():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM ssps
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def assign_ssps(sect_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    ssp_list = get_ssp_list()

    chosen_ssps = random.sample(ssp_list, random.randint(10, 30))

    for chosen_ssp in chosen_ssps:
        cursor.execute("INSERT INTO section_ssps (sect_id, ssp_id) VALUEs  (%s,%s)", (sect_id, chosen_ssp[0]))

    conn.commit()
    cursor.close()
    conn.close()


def get_section_ssps(sect_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM section_ssps where sect_id = (%s)", (sect_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows
