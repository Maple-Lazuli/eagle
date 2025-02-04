from flask import Flask, request, Response
import json
import psycopg2
import datetime
import requests as r

app = Flask(__name__)

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
        CREATE TABLE IF NOT EXISTS settings (
            id SERIAL PRIMARY KEY,
            kill_switch_active BOOLEAN DEFAULT FALSE
        );

        INSERT INTO settings (kill_switch_active) 
        SELECT FALSE 
        WHERE NOT EXISTS (SELECT 1 FROM settings);

        CREATE TABLE IF NOT EXISTS insiders (
            id SERIAL PRIMARY KEY,
            account VARCHAR(255) UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS logs (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            target VARCHAR(255) NOT NULL,
            department VARCHAR(255) NOT NULL,
            authorized BOOLEAN NOT NULL
        );
    """)

    conn.commit()
    cursor.close()
    conn.close()

init_db()

@app.route('/insider', methods=['POST'])
def register_insider():
    """Registers an insider threat."""
    data = request.get_json()
    account = data.get('account')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO insiders (account) VALUES (%s) ON CONFLICT (account) DO NOTHING", (account,))
    conn.commit()

    cursor.close()
    conn.close()

    return Response("Okay", status=200, mimetype='application/json')


@app.route('/insider', methods=['GET'])
def get_insiders():
    """Retrieves a list of registered insider threats."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT account FROM insiders")
    insiders = [row[0] for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    return Response(json.dumps(insiders), status=200, mimetype='application/json')


@app.route('/kill_switch', methods=['GET'])
def get_kill_status():
    """Returns the current kill switch status."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT kill_switch_active FROM settings LIMIT 1")
    kill_switch_status = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return Response(json.dumps({'kill_active': kill_switch_status}), status=200, mimetype='application/json')


@app.route('/kill_switch_toggle', methods=['GET'])
def set_kill_switch():
    """Toggles the kill switch."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE settings SET kill_switch_active = NOT kill_switch_active RETURNING kill_switch_active")
    new_status = cursor.fetchone()[0]

    conn.commit()
    cursor.close()
    conn.close()

    return Response(json.dumps({'kill_active': new_status}), status=200, mimetype='application/json')


@app.route('/time', methods=['GET'])
def get_time():
    """Returns a scaled timestamp."""
    time_scale = 1.0000001
    current = datetime.datetime.now()
    scaled_timestamp = current.timestamp() * time_scale

    return Response(json.dumps({'timestamp': scaled_timestamp}), status=200, mimetype='application/json')


@app.route('/logs', methods=['GET'])
def get_logs():
    """Retrieves logged events."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT timestamp, target, department, authorized FROM logs")
    logs = [
        {"timestamp": str(row[0]), "target": row[1], "department": row[2], "authorized": row[3]}
        for row in cursor.fetchall()
    ]

    cursor.close()
    conn.close()

    return Response(json.dumps(logs), status=200, mimetype='application/json')


@app.route('/event', methods=['POST'])
def archive_event():
    """Logs an event and determines if access is authorized."""
    data = request.get_json()
    target = data.get('target')
    department = data.get('department')

    # Check if SSP is authorized
    ssp_maintainer_res = r.get(f"http://127.0.0.1:4520/department_ssps?department={department}")
    authorized_ssps = ssp_maintainer_res.json()

    authorized = target in authorized_ssps

    # Log the event
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO logs (target, department, authorized) VALUES (%s, %s, %s)",
        (target, department, authorized)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return Response(json.dumps({'authorized': authorized}), status=200, mimetype='application/json')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=4590)
