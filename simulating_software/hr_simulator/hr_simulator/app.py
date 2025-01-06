from flask import Flask, request, Response
import json

app = Flask(__name__)

employees = dict()


@app.route('/users', methods=['GET'])
def get_users():
    return Response(json.dumps(employees), status=200, mimetype='application/json')


@app.route('/register', methods=['POST'])
def accept_log():
    if request.is_json:
        data = request.get_json()
        first_name = data['first_name']
        last_name = data['last_name']

        return Response(json.dumps(response), status=200, mimetype='application/json')
    else:
        return Response("Invalid Request", status=400, mimetype='application/json')


if __name__ == '__main__':
    app.run(port=4510)
