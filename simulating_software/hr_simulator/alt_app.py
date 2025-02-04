from flask import Flask, request, Response
import json
import psycopg2
import os

app = Flask(__name__)

# Database Configuration
DB_CONFIG = {
    "dbname": "mydb",
    "user": "user",
    "password": "pass",
    "host": "localhost",  # Change if using a remote DB
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
            lead_id INT DEFAULT NULL,
            UNIQUE(name, department_id),
            FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE,
            FOREIGN KEY (lead_id) REFERENCES employees(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS employees (
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            team_id INT NOT NULL,
            UNIQUE(first_name, last_name),
            FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()

# Initialize Database
init_db()


@app.route('/users', methods=['GET'])
def get_users():
    """Fetch all employees."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT employees.id, employees.first_name, employees.last_name, teams.name AS team_name
        FROM employees
        JOIN teams ON employees.team_id = teams.id
    """)
    employees = [
        {"id": row[0], "first_name": row[1], "last_name": row[2], "team": row[3]}
        for row in cursor.fetchall()
    ]

    cursor.close()
    conn.close()

    return Response(json.dumps(employees), status=200, mimetype='application/json')


@app.route('/organization', methods=['GET'])
def get_organization():
    """Fetch organization structure."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT departments.name AS department, teams.name AS team, employees.first_name, employees.last_name 
        FROM teams
        JOIN departments ON teams.department_id = departments.id
        LEFT JOIN employees ON teams.lead_id = employees.id
    """)

    organization = {}
    for row in cursor.fetchall():
        dept_name, team_name, lead_first, lead_last = row
        lead = f"{lead_first} {lead_last}" if lead_first else "No Lead Assigned"
        if dept_name not in organization:
            organization[dept_name] = {}
        organization[dept_name][team_name] = {"lead": lead}

    cursor.close()
    conn.close()

    return Response(json.dumps(organization), status=200, mimetype='application/json')


@app.route('/register', methods=['POST'])
def register_employee():
    """Register a new employee and assign them to a team."""
    if not request.is_json:
        return Response("Invalid Request", status=400, mimetype='application/json')

    data = request.get_json()
    first_name = data['first_name']
    last_name = data['last_name']
    department_name = data['department']
    team_name = data['team']

    conn = get_db_connection()
    cursor = conn.cursor()

    # Ensure department exists
    cursor.execute("INSERT INTO departments (name) VALUES (%s) ON CONFLICT (name) DO NOTHING RETURNING id", (department_name,))
    dept_id = cursor.fetchone()
    if dept_id is None:
        cursor.execute("SELECT id FROM departments WHERE name = %s", (department_name,))
        dept_id = cursor.fetchone()[0]
    else:
        dept_id = dept_id[0]

    # Ensure team exists
    cursor.execute("INSERT INTO teams (name, department_id) VALUES (%s, %s) ON CONFLICT (name, department_id) DO NOTHING RETURNING id",
                   (team_name, dept_id))
    team_id = cursor.fetchone()
    if team_id is None:
        cursor.execute("SELECT id FROM teams WHERE name = %s AND department_id = %s", (team_name, dept_id))
        team_id = cursor.fetchone()[0]
    else:
        team_id = team_id[0]

    # Register employee
    cursor.execute("INSERT INTO employees (first_name, last_name, team_id) VALUES (%s, %s, %s) RETURNING id",
                   (first_name, last_name, team_id))
    emp_id = cursor.fetchone()[0]

    # Check if team already has a lead
    cursor.execute("SELECT lead_id FROM teams WHERE id = %s", (team_id,))
    lead_id = cursor.fetchone()[0]

    # Assign first employee as team lead
    if lead_id is None:
        cursor.execute("UPDATE teams SET lead_id = %s WHERE id = %s", (emp_id, team_id))

    conn.commit()
    cursor.close()
    conn.close()

    return Response(json.dumps({"id": emp_id, "first_name": first_name, "last_name": last_name, "team": team_name}),
                    status=200, mimetype='application/json')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=4510)
