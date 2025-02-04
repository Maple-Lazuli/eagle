from flask import Flask, request, Response
import json
import psycopg2
import os
import utilities as u  # Assuming utilities.py has get_ssps()

app = Flask(__name__)

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

# Create Tables if They Don't Exist
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS departments (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS teams (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            department_id INT NOT NULL,
            UNIQUE(name, department_id),
            FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS ssps (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS team_ssps (
            team_id INT NOT NULL,
            ssp_id INT NOT NULL,
            PRIMARY KEY (team_id, ssp_id),
            FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE,
            FOREIGN KEY (ssp_id) REFERENCES ssps(id) ON DELETE CASCADE
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()

# Initialize Database
init_db()


@app.route('/departments', methods=['GET'])
def get_departments():
    """Fetch all departments."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name FROM departments")
    departments = {row[0]: row[1] for row in cursor.fetchall()}

    cursor.close()
    conn.close()

    return Response(json.dumps(departments), status=200, mimetype='application/json')


@app.route('/teams', methods=['GET'])
def get_teams():
    """Fetch all teams, optionally filtered by department."""
    department_name = request.args.get('department')

    conn = get_db_connection()
    cursor = conn.cursor()

    if department_name:
        cursor.execute("""
            SELECT teams.id, teams.name 
            FROM teams 
            JOIN departments ON teams.department_id = departments.id 
            WHERE departments.name = %s
        """, (department_name,))
    else:
        cursor.execute("SELECT id, name FROM teams")

    teams = {row[0]: row[1] for row in cursor.fetchall()}

    cursor.close()
    conn.close()

    return Response(json.dumps(teams), status=200, mimetype='application/json')


@app.route('/ssps', methods=['GET'])
def get_ssps():
    """Fetch all SSPs associated with a specific team or department."""
    team_name = request.args.get('team')
    department_name = request.args.get('department')

    conn = get_db_connection()
    cursor = conn.cursor()

    if team_name:
        cursor.execute("""
            SELECT ssps.name 
            FROM ssps 
            JOIN team_ssps ON ssps.id = team_ssps.ssp_id
            JOIN teams ON team_ssps.team_id = teams.id
            WHERE teams.name = %s
        """, (team_name,))
    elif department_name:
        cursor.execute("""
            SELECT DISTINCT ssps.name 
            FROM ssps 
            JOIN team_ssps ON ssps.id = team_ssps.ssp_id
            JOIN teams ON team_ssps.team_id = teams.id
            JOIN departments ON teams.department_id = departments.id
            WHERE departments.name = %s
        """, (department_name,))
    else:
        cursor.execute("SELECT name FROM ssps")

    ssps = [row[0] for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    return Response(json.dumps(ssps), status=200, mimetype='application/json')


@app.route('/register', methods=['POST'])
def register_team_ssps():
    """Register a new department-team and assign SSPs to it."""
    if not request.is_json:
        return Response("Invalid Request", status=400, mimetype='application/json')

    data = request.get_json()
    department_name = data['department']
    team_name = data['team']
    random_ssps = u.get_ssps()  # List of SSP names

    conn = get_db_connection()
    cursor = conn.cursor()

    # Ensure the department exists
    cursor.execute("INSERT INTO departments (name) VALUES (%s) ON CONFLICT (name) DO NOTHING RETURNING id", (department_name,))
    department_id = cursor.fetchone()
    if department_id is None:
        cursor.execute("SELECT id FROM departments WHERE name = %s", (department_name,))
        department_id = cursor.fetchone()[0]
    else:
        department_id = department_id[0]

    # Ensure the team exists
    cursor.execute("INSERT INTO teams (name, department_id) VALUES (%s, %s) ON CONFLICT (name, department_id) DO NOTHING RETURNING id",
                   (team_name, department_id))
    team_id = cursor.fetchone()
    if team_id is None:
        cursor.execute("SELECT id FROM teams WHERE name = %s AND department_id = %s", (team_name, department_id))
        team_id = cursor.fetchone()[0]
    else:
        team_id = team_id[0]

    # Insert SSPs
    for ssp_name in random_ssps:
        cursor.execute("INSERT INTO ssps (name) VALUES (%s) ON CONFLICT (name) DO NOTHING RETURNING id", (ssp_name,))
        ssp_id = cursor.fetchone()
        if ssp_id is None:
            cursor.execute("SELECT id FROM ssps WHERE name = %s", (ssp_name,))
            ssp_id = cursor.fetchone()[0]
        else:
            ssp_id = ssp_id[0]

        # Link SSPs to the team
        cursor.execute("INSERT INTO team_ssps (team_id, ssp_id) VALUES (%s, %s) ON CONFLICT DO NOTHING", (team_id, ssp_id))

    conn.commit()
    cursor.close()
    conn.close()

    return Response(json.dumps(random_ssps), status=200, mimetype='application/json')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=4520)
