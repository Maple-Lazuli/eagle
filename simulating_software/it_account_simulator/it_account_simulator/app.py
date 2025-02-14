from flask import Flask, request, Response
import json

import utilities as u

app = Flask(__name__)

# Initialize Database
u.init_db()


@app.route('/accounts', methods=['GET'])
def get_accounts():
    """Fetch all accounts from the database."""
    conn = u.get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT account_name, employee_number FROM users")
    accounts = {row[0]: row[1] for row in cursor.fetchall()}

    cursor.close()
    conn.close()

    return Response(json.dumps(accounts), status=200, mimetype='application/json')


@app.route('/register', methods=['POST'])
def register_account():
    """Register a new account and store it in the database."""
    if not request.is_json:
        return Response("Invalid Request", status=400, mimetype='application/json')

    data = json.loads(request.json)

    first_name = data['first_name']
    last_name = data['last_name']
    employee_number = data['employee_num']
    key_id = data['key_id']
    account_name = u.add_user_account(first_name, last_name, employee_number, key_id)

    return Response(json.dumps({'account': account_name}), status=200, mimetype='application/json')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=4530)
