from flask import Blueprint, jsonify, request
from flask_cors import CORS, cross_origin
import json
from db import DB

authenticate = Blueprint('authenticate', __name__)

db = DB()

@authenticate.route('/register', methods=['POST'])
@cross_origin()
def register():
    return db.registerUser(request.data)


@authenticate.route('/login', methods=['POST'])
@cross_origin()
def login():
    data = processData(request.data)
    response = db.authenticateUser(data['uid'], data['password'])

    if response is not None:
        response['_id'] = str(response['_id'])
        return jsonify(response)
    else:
        return jsonify({'status': False})


def processData(_data):
    data = _data.decode()
    parsed = json.loads(data)
    return parsed['body']