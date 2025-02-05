from flask import Flask, request, Response
import json
import utilities as u

app = Flask(__name__)

u.init_db()


@app.route('/get_organization', methods=['GET'])
def get_org():
    org = u.get_org_structure()
    return Response(json.dumps(org), status=200, mimetype='application/json')


@app.route('/get_employees', methods=['GET'])
def get_employees():
    org = u.get_employees()
    return Response(json.dumps(org), status=200, mimetype='application/json')


@app.route('/register', methods=['POST'])
def register_employee():
    """Register a new employee and assign them to a team."""
    if not request.is_json:
        return Response("Invalid Request", status=400, mimetype='application/json')

    data = json.loads(request.json)

    first_name = data['first_name']
    last_name = data['last_name']

    employee_dict = u.add_employee(first_name, last_name)

    return Response(json.dumps(employee_dict),
                    status=200, mimetype='application/json')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=4510)
