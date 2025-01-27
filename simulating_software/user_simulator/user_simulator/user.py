import json
import requests as r
import utilities as u


def set_up():
    first_name = u.get_random_first_name()
    last_name = u.get_random_last_name()

    res = r.post("http://127.0.0.1:4510/register", json=json.dumps({"first_name": first_name, "last_name": last_name}))

    employee_record = res.json()[0]
    team_record = res.json()[1]

    employee_num = employee_record['Employee_Num']
    department = employee_record['Department']
    team = employee_record['Team']

    position_lead = team_record['Lead'] == employee_num
    start_hour = team_record['Start_Time']
    work_days = team_record['Days']

    res = r.post("http://127.0.0.1:4530/register",
                 json=json.dumps({"first_name": first_name, "last_name": last_name, 'employee_num': employee_num}))

    account_name = res.json()['account']

    if position_lead:
        res = r.post("http://127.0.0.1:4520/register", json=json.dumps({"department": department, "team": team}))
    else:
        res = r.get(f"http://127.0.0.1:4520/ssps?team={team}&department={department}")

    work_ssps = res.json()

    return {"first_name": first_name,
            "last_name": last_name,
            "employee_num": employee_num,
            "department": department,
            "team": team,
            "position_lead": position_lead,
            "start_hour": start_hour,
            "work_days": work_days,
            "account_name": account_name,
            "work_ssps": work_ssps,
            }
