from flask import Flask, request, Response
import json
import os
import utilities as u

app = Flask(__name__)

if os.path.exists(".data"):
    accounts = u.load_dictionary(".data", "accounts.json")
else:
    os.mkdir(".data")
    accounts = dict()


@app.route('/accounts', methods=['GET'])
def get_accounts():
    return Response(json.dumps(accounts), status=200, mimetype='application/json')


@app.route('/register', methods=['POST'])
def register_account():
    global accounts
    if not request.is_json:
        return Response("Invalid Request", status=400, mimetype='application/json')

    data = json.loads(request.json)

    first_name = data['first_name']
    last_name = data['last_name']
    employee_number = data['employee_num']

    account_name = u.create_user_account(first_name, last_name, [k for k in accounts.keys()])

    accounts[account_name] = employee_number

    u.save_dictionary(".data", "accounts.json", accounts)

    return Response(json.dumps({'account': account_name}), status=200, mimetype='application/json')


if __name__ == '__main__':
    app.run(port=4530)
