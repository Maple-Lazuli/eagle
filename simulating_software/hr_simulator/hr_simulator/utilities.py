import psycopg2
import random
import json

DB_CONFIG = {
    "dbname": "mydb",
    "user": "user",
    "password": "pass",
    "host": "localhost",  # Change if using a remote DB
    "port": "5432",
}


def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS departments (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100)NOT NULL
        );

        CREATE TABLE IF NOT EXISTS divisions (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) UNIQUE NOT NULL,
            department_id INT NOT NULL,
            FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS sections (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            division_id INT NOT NULL,
            lead_id INT DEFAULT NULL,
            start_hour INT NOT NULL,
            monday BOOLEAN DEFAULT FALSE,
            tuesday BOOLEAN DEFAULT FALSE,
            wednesday BOOLEAN DEFAULT FALSE,
            thursday BOOLEAN DEFAULT FALSE,
            friday BOOLEAN DEFAULT FALSE,
            saturday BOOLEAN DEFAULT FALSE,
            sunday BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (division_id) REFERENCES divisions(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS employees (
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            section_id INT NOT NULL,
            FOREIGN KEY (section_id) REFERENCES sections(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED
        );


    """)
    conn.commit()
    cursor.close()
    conn.close()
    add_org_structure()


def add_org_structure():
    with open("./hr_simulator/new_org_structure.json", "r") as file_in:
        org = json.load(file_in)

    conn = get_db_connection()
    cursor = conn.cursor()

    for dept in org.keys():
        cursor.execute("INSERT INTO departments (name) VALUEs (%s) RETURNING id", (dept,))
        department_id = cursor.fetchone()[0]
        for division in org[dept].keys():
            cursor.execute("INSERT INTO divisions (name, department_id) VALUEs (%s, %s) RETURNING id",
                           (division, department_id))
            division_id = cursor.fetchone()[0]
            for section in org[dept][division]:
                start_time = random.randint(0, 23)
                work_days = list(set([random.randint(0, 6) for _ in range(5)]))
                cursor.execute("""INSERT INTO sections (name, division_id, 
    start_hour, monday, tuesday, wednesday, thursday, friday, 
    saturday, sunday) VALUEs (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id""", (section,
                                                                                        division_id,
                                                                                        start_time,
                                                                                        1 in work_days,
                                                                                        2 in work_days,
                                                                                        3 in work_days,
                                                                                        4 in work_days,
                                                                                        5 in work_days,
                                                                                        6 in work_days,
                                                                                        0 in work_days))
    conn.commit()
    cursor.close()
    conn.close()


def get_org_structure():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT 
        d.id AS department_id,
        d.name AS department_name,
        dv.id AS division_id,
        dv.name AS division_name,
        s.id AS section_id,
        s.name AS section_name,
        s.lead_id,
        s.start_hour,
        s.monday,
        s.tuesday,
        s.wednesday,
        s.thursday,
        s.friday,
        s.saturday,
        s.sunday
    FROM departments d
    LEFT JOIN divisions dv ON d.id = dv.department_id
    LEFT JOIN sections s ON dv.id = s.division_id;
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def add_employee(first_name, last_name):
    conn = get_db_connection()
    cursor = conn.cursor()

    rows = get_org_structure()
    row = rows[random.randint(0, len(rows) - 1)]
    dept_id, dept_name, div_id, div_name, sect_id, sect_name, lead_id, start_hour, mon, tues, wed, thurs, fri, sat, sun = row

    cursor.execute("INSERT INTO employees (first_name, last_name, section_id) VALUEs (%s,%s,%s) RETURNING id",
                   (first_name, last_name, sect_id))
    emp_id = cursor.fetchone()[0]
    if lead_id is None:
        cursor.execute("UPDATE sections SET lead_id = %s WHERE id = %s", (emp_id, sect_id))
        lead_id = emp_id

    conn.commit()
    cursor.close()
    conn.close()

    work_days = []
    work_days.append(1) if mon else None
    work_days.append(2) if tues else None
    work_days.append(3) if wed else None
    work_days.append(4) if thurs else None
    work_days.append(5) if fri else None
    work_days.append(6) if sat else None
    work_days.append(0) if sun else None

    return {'Department_id': dept_id,
            'Section_id': sect_id,
            'Division_id': div_id,
            'Employee_id': emp_id,
            'Lead_id': lead_id,
            'Start_Time': start_hour,
            'Days': work_days}
