import json
import random
import os


def register_employee(first_name, last_name, number, organization):
    departments = [_ for _ in organization.keys()]
    department = departments[random.randint(0, len(departments) - 1)]

    teams = [_ for _ in organization[department].keys()]
    team = teams[random.randint(0, len(teams) - 1)]

    employee = {
        "First_Name": first_name,
        "Last_Name": last_name,
        "Employee_Num": number,
        "department": department,
        "team": team
    }

    organization[department][team]["Members"].append(number)

    if organization[department][team]["Lead"] == -1:
        organization[department][team]["Lead"] = number
        organization[department][team]["Start_Time"] = random.randint(0, 23)
        organization[department][team]["Days"] = list(set([random.randint(0, 6) for _ in range(6)]))

    return employee, organization


def initialize_organization():
    with open("organization.json", "r") as file_in:
        return json.load(file_in)


def save_organization(path, organization):
    with open(os.path.join(path, "organization.json"), "w") as file_out:
        json.dump(file_out, organization)


def save_employees(path, employees):
    with open(os.path.join(path, "employees.json"), "w") as file_out:
        json.dump(file_out, employees)
