from flask import Flask, request, Response
import json

app = Flask(__name__)


@app.route('/pubic_key', methods=['GET'])
def get_public_exponent():
    response = {
        "exponent": 12345
    }
    return Response(json.dumps(response), status=200, mimetype='application/json')


@app.route('/log_delivery', methods=['POST'])
def accept_log():
    if request.is_json:
        data = request.get_json()
        response = {
            "message": "Data received successfully",
            "received_data": data
        }

        return Response(json.dumps(response), status=200, mimetype='application/json')
    else:
        return Response("Invalid Delivery", status=400, mimetype='application/json')


if __name__ == '__main__':
    app.run(port=4500)
