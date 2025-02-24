import os

from flask import Flask, request, Response
import json
import crypto_layer as cl
import utilities as u
import os
import secrets

app = Flask(__name__)

# Initialize Database
u.init_db()
crypto = cl.CryptoLayer()
if not os.path.exists(".data"):
    os.mkdir(".data")


@app.route('/key_id', methods=['GET'])
def get_key_id():
    return Response(json.dumps({'key_id': crypto.key_id}), status=200, mimetype='application/json')


@app.route('/accounts', methods=['GET'])
def get_accounts():
    """Fetch all accounts from the database."""
    sender_key = request.args.get('sender_key')

    conn = u.get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT account_name, employee_number FROM users")
    accounts = {row[0]: row[1] for row in cursor.fetchall()}

    cursor.close()
    conn.close()

    return Response(crypto.create_payload(accounts, sender_key), status=200, mimetype='application/json')


@app.route('/it_error_logs', methods=["POST"])
def record_errorss():
    if not request.is_json:
        return Response("Invalid Request", status=400, mimetype='application/json')

    with open(f".data/{secrets.token_hex(32)}.json", 'w') as file_out:
        json.dump(json.loads(request.json), file_out)

    return Response("Error Logged", status=200, mimetype='application/json')


@app.route('/it_error_logs', methods=['GET'])
def get_errors():
    records = []
    for root, dirs, files in os.walk(".data"):
        for file in files:
            if str(file).find(".json"):
                with open(os.path.join(root, file), "r") as file_in:
                    records.append(json.load(file_in))

    return Response(json.dumps(records), status=200, mimetype='application/json')


@app.route('/register', methods=['POST'])
def register_account():
    """Register a new account and store it in the database."""
    if not request.is_json:
        return Response("Invalid Request", status=400, mimetype='application/json')

    data = json.loads(request.json)
    sender_key = data["sender_key"]
    data = crypto.decrypt_message(data)

    first_name = data['first_name']
    last_name = data['last_name']
    employee_number = data['employee_num']
    key_id = data['key_id']
    account_name = u.add_user_account(first_name, last_name, employee_number, key_id)

    return Response(crypto.create_payload({'account': account_name}, sender_key), status=200,
                    mimetype='application/json')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=4530)
