import psycopg2
from datetime import datetime
import pandas as pd

DB_CONFIG = {
    "dbname": "mydb",
    "user": "user",
    "password": "pass",
    "host": "localhost",
    "port": "5432",
}


def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)


# TO DO Update to only have departments with employees
def get_departments():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""SELECT DISTINCT d.id, d.name FROM departments d
                       JOIN divisions div on d.id = div.department_id
                       JOIN sections sec on div.id = sec.division_id
                       JOIN employees e on sec.id = e.section_id
                       WHERE e.id IS NOT NULL;""")
    departments = cursor.fetchall()
    cursor.close()
    conn.close()
    return sorted(departments, key=lambda x: x[0])


# TO DO Update to only have divisions with employees
def get_divisions(dept_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""SELECT DISTINCT div.id, div.name FROM divisions div
                       JOIN sections sec on div.id = sec.division_id
                       JOIN employees e on sec.id = e.section_id
                       WHERE e.id IS NOT NULL 
                       AND div.department_id = %s;""", (dept_id,))
    divisions = cursor.fetchall()
    cursor.close()
    conn.close()
    return sorted(divisions, key=lambda x: x[0])


# TO DO Update to only have sections with employees
def get_sections(div_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""SELECT DISTINCT sec.id, sec.name FROM sections sec
                       JOIN employees e on sec.id = e.section_id
                       WHERE e.id IS NOT NULL 
                       AND sec.division_id = %s;""", (div_id,))
    sections = cursor.fetchall()
    cursor.close()
    conn.close()
    return sorted(sections, key=lambda x: x[0])


def get_section(section_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sections where id =  %s", (section_id,))
    section = cursor.fetchone()
    cursor.close()
    conn.close()
    section_dict = dict()
    keys = ["id", "name", "division_id", "lead_id",
            "start_hour", "monday", "tuesday", "wednesday",
            "thursday", "friday", "saturday", "sunday"]
    for key, val in zip(keys, section):
        section_dict[key] = val
    return section_dict


def get_employee(emp_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employees where id =  %s", (emp_id,))
    employee = cursor.fetchone()
    cursor.close()
    conn.close()
    employee_dict = dict()
    keys = ["id", "first_name", "last_name", "section_id"]
    for key, val in zip(keys, employee):
        employee_dict[key] = val
    return employee_dict


def get_workdays_str(section_dict):
    work_days = []
    for key in section_dict.keys():
        if str(key).find("day") != -1:
            if section_dict[key]:
                work_days.append(key)

    work_days = [w.capitalize() for w in work_days]
    if len(work_days) > 2:
        rtn_str = ""
        rtn_str += ", ".join(work_days[0:-1])
        rtn_str += ", and " + work_days[-1]
        return rtn_str

    elif len(work_days) == 2:
        return " and ".join(work_days)

    elif len(work_days) == 1:
        return work_days[0]

    else:
        return ""


def get_employees(sect_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employees where section_id =  %s", (sect_id,))
    employees = cursor.fetchall()
    cursor.close()
    conn.close()
    employee_dicts = []

    keys = ["id", "first_name", "last_name", "section_id"]
    for employee in employees:
        temp = dict()
        for key, val in zip(keys, employee):
            temp[key] = val
        employee_dicts.append(temp)
    return employee_dicts


def get_logs_by_employee(section_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""SELECT logs.*, employees.*, ssps.name
        FROM logs
        JOIN employees ON logs.emp_id = employees.id
        JOIN ssps ON logs.ssp_id = ssps.id
        WHERE employees.section_id = %s""", (section_id,))
    logs = cursor.fetchall()
    cursor.close()
    conn.close()

    log_dicts = []
    keys = ["id", "scaled_timestamp", "ssp_id", "emp_id", "authorized", "id", "first_name", "last_name", "section_id",
            "ssp_name"]
    for log in logs:
        temp_dict = dict()
        for key, val in zip(keys, log):
            if key == "scaled_timestamp":
                temp_dict[key] = datetime.fromtimestamp(val)
            else:
                temp_dict[key] = val
        temp_dict['emp_id'] = f"{temp_dict['first_name']} {temp_dict['last_name']} ({temp_dict['emp_id']})"
        temp_dict['ssp_id'] = f"{temp_dict['ssp_name']} ({temp_dict['ssp_id']})"
        log_dicts.append(temp_dict)
    return log_dicts


def hunt_insiders(threshold):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"""WITH section_avg AS (
        SELECT 
            e.section_id, 
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY unique_ssp_count) AS median_logins,
            STDDEV(unique_ssp_count) AS stddev_logins
        FROM 
            employees e
        JOIN (
            SELECT 
                emp_id, 
                COUNT(*) AS log_count,
                COUNT(DISTINCT ssp_id) AS unique_ssp_count
            FROM 
                logs
            GROUP BY 
                emp_id
        ) log_counts 
        ON e.id = log_counts.emp_id
        GROUP BY 
            e.section_id
    ),
    employee_logins AS (
        SELECT 
            e.id, 
            e.first_name,
            e.last_name,
            e.section_id, 
            COUNT(l.id) AS log_count,
            COUNT(DISTINCT l.ssp_id) AS unique_ssp_count
        FROM 
            employees e
        LEFT JOIN logs l 
            ON e.id = l.emp_id
        GROUP BY 
            e.id, e.section_id
    )

    SELECT 
        el.id, 
        el.first_name,
        el.last_name,
        sec.name,
        div.name,
        dept.name,
        el.unique_ssp_count,
        sa.median_logins,
        el.unique_ssp_count - (sa.median_logins +  {threshold}* sa.stddev_logins)
    FROM 
        employee_logins el
    JOIN 
        section_avg sa
        ON el.section_id = sa.section_id
    JOIN 
        sections sec
        ON sa.section_id = sec.id
    JOIN 
        divisions div
        ON sec.division_id = div.id
    JOIN
        departments dept
        ON div.department_id = dept.id
    WHERE 
        el.unique_ssp_count > sa.median_logins +  {threshold}* sa.stddev_logins;""")
    hits = cursor.fetchall()
    cursor.close()
    conn.close()

    columns = ['ID', 'first_name', 'last_name', 'Section', 'Division', 'Department', 'Resources', 'Median', 'Score']
    mapped = []
    for hit in hits:
        temp = dict()
        for key, value in zip(columns, hit):
            temp[key] = value
        mapped.append(temp
                      )
    return pd.DataFrame.from_dict(mapped).sort_values(['Score'], ascending=False).drop(['Resources', 'Median'], axis=1)
