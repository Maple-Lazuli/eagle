from flask import Flask, request, Response
import json
import utilities as u
import os

app = Flask(__name__)

if os.path.exists(".data"):
    organization = u.load_dictionary(".data/organization.json")
    employees = u.load_dictionary(".data/employees.json")
else:
    os.mkdir(".data")
    organization = u.load_dictionary("organization.json")
    employees = dict()


@app.route('/users', methods=['GET'])
def get_users():
    return Response(json.dumps(employees), status=200, mimetype='application/json')


@app.route('/register', methods=['POST'])
def accept_log():
    global organization
    global employees
    if not request.is_json:
        return Response("Invalid Request", status=400, mimetype='application/json')

    data = request.get_json()
    first_name = data['first_name']
    last_name = data['last_name']
    num = len([_ for _ in employees.keys()]) + 1

    employee, organization = u.register_employee(first_name, last_name,num, organization)

    employees[num] = employee

    team = organization[employee['Department']][employee['Team']]
    return Response(json.dumps([employee, team]), status=200, mimetype='application/json')


if __name__ == '__main__':
    app.run(port=4510)
