from flask import Flask, request, Response
import json
import utilities as u
import crypto_layer as cl

app = Flask(__name__)

u.init_db()
crypto = cl.CryptoLayer()


@app.route('/key_id', methods=['GET'])
def get_key_id():
    return Response(json.dumps({'key_id': crypto.key_id}), status=200, mimetype='application/json')


@app.route('/get_organization', methods=['GET'])
def get_org():
    sender_key = request.args.get('sender_key')
    org = u.get_org_structure()
    return Response(crypto.create_payload(org, sender_key), status=200, mimetype='application/json')


@app.route('/get_employees', methods=['GET'])
def get_employees():
    sender_key = request.args.get('sender_key')
    org = u.get_employees()
    return Response(crypto.create_payload(org, sender_key), status=200, mimetype='application/json')


@app.route('/register', methods=['POST'])
def register_employee():
    """Register a new employee and assign them to a team."""
    if not request.is_json:
        return Response("Invalid Request", status=400, mimetype='application/json')

    data = json.loads(request.json)
    sender_key = data["sender_key"]
    data = crypto.decrypt_message(data)

    first_name = data['first_name']
    last_name = data['last_name']

    employee_dict = u.add_employee(first_name, last_name)

    return Response(crypto.create_payload(employee_dict, sender_key), status=200, mimetype='application/json')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=4510)
