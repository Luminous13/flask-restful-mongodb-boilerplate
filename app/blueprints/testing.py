from flask import Blueprint, jsonify
from flask_cors import CORS, cross_origin

testing = Blueprint('testing', __name__)

@testing.route('/test')
@cross_origin()
def test():
    return jsonify({ 'status': 200 })