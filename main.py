from flask import Flask, jsonify, request, blueprints
from flask_cors import CORS, cross_origin
import json
import os
from app.db import DB
from app.blueprints import testing
from waitress import serve

app = Flask(__name__)
app.config['SECRET_KEY'] = 'fckYOU!'

# Register Blueprints
app.register_blueprint(testing.testing)
# ===========================
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'



def processData(_data):
    data = _data.decode()
    parsed = json.loads(data)
    return parsed['body']


if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 5000))
    # Run this for development
    app.run(host='0.0.0.0', port=PORT, debug=True)
    # Run this for production
    # serve(app, host='0.0.0.0', port=PORT)