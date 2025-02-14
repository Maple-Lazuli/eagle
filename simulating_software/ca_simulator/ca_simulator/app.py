from flask import Flask, request, Response
import json
import base64

import utilities as u

app = Flask(__name__)

# Initialize Database
u.init_db()


@app.route('/key', methods=['GET'])
def get_key():
    key_id = request.args.get('key_id')
    key = u.get_key(key_id)
    encoded_key = base64.b64encode(key)
    return Response(json.dumps({"public_key":encoded_key}), status=200, mimetype='application/json')


@app.route('/key', methods=['POST'])
def add_key():
    """Register a new account and store it in the database."""
    if not request.is_json:
        return Response("Invalid Request", status=400, mimetype='application/json')

    data = json.loads(request.json)
    encoded_key = data['public_key']
    key = base64.b64decode(encoded_key)
    key_id = u.register_key(key)
    return Response(json.dumps({'key_id': key_id}), status=200, mimetype='application/json')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=4530)
