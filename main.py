from flask import Flask, jsonify, request, blueprints
from flask_cors import CORS, cross_origin
import json
import os
from app.blueprints import testing
from waitress import serve
import time

# ALL ABOUT FIREBASE
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Use the application default credentials
# GCLOUD
cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred, {
  'projectId': 'underbehind-c43ab',
})

# LOCAL
# Use a service account
# cred = credentials.Certificate('./serviceAccount.json')
# firebase_admin.initialize_app(cred)

db = firestore.client()

# ===================================================

app = Flask(__name__)
app.config['SECRET_KEY'] = 'fckYOU!'

# Register Blueprints
app.register_blueprint(testing.testing)
# ===========================
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/queryNearbyTracks', methods=['POST'])
@cross_origin()
def queryNearbyTracks():
    start_time = time.time()
    data = processData(request.data)
    
    # THE RANGE OF DISTANCE
    radius = 0.0003
    maxLat = data['latitude'] + radius
    maxLong = data['longitude'] + radius
    minLat = data['latitude'] - radius
    minLong = data['longitude'] - radius

    # GET ALL TRACKS BY LATITUDE
    tracks = db.collection(u'tracks')
    users = db.collection(u'users')
    docs = tracks.where(u'tags', u'array_contains', u'beta').stream()

    # GET THE LIST OF PLAYED TRACKS OF USER
    listPlayedTracks = users.document(data['userId']).get()
    listPlayedTracks = listPlayedTracks.to_dict()

    # APPEND TO AN ARRAY
    listTracks = []
    for doc in docs:
      parsed = doc.to_dict()
      parsed['trackId'] = doc.id

      # CHECK IF THE TRACK HAS ALREADY BEEN HEARD BY THE USER
      if 'playedTrackIds' in listPlayedTracks.keys():
        if parsed['trackId'] not in listPlayedTracks['playedTrackIds']:
          queryUser = users.document(parsed['userID']).get()
          result = queryUser.to_dict()

          if result is not None:
            parsed['username'] = f"@{result['firstName']}{result['lastName']}"

          listTracks.append(parsed)
      else:
        queryUser = users.document(parsed['userID']).get()
        result = queryUser.to_dict()

        if result is not None:
          parsed['username'] = f"@{result['firstName']}{result['lastName']}"

        listTracks.append(parsed)

    # FILTER ARRAY BY LONGITUDE
    filteredListTracks = [ track for track in listTracks if track['startingLocation']['longitude'] <= maxLong and track['startingLocation']['longitude'] >= minLong and track['startingLocation']['latitude'] <= maxLat and track['startingLocation']['latitude'] >= minLat ]

    print("--- %s seconds ---" % (time.time() - start_time))
    return jsonify({ 'status': filteredListTracks })


@app.route('/getNearbyBroadcasts', methods=['POST'])
@cross_origin()
def getNearbyBroadcasts():
    # SET VARIABLE OF OUTPUT 
    output = []

    # GET THE ARGUMENTS
    data = processData(request.data)
      
    # THE RANGE OF DISTANCE
    radius = 0.001
    maxLat = data['latitude'] + radius
    maxLong = data['longitude'] + radius
    minLat = data['latitude'] - radius
    minLong = data['longitude'] - radius

    # GET ALL BUSINESSES
    business = db.collection(u'business')
    docs = business.stream()

    listBusiness = []

    for doc in docs:
        listBusiness.append(doc.to_dict())

    # GET ONLY THE NEARBY BUSINESSES
    filteredBusiness = [ business for business in listBusiness if business['coordinates']['long'] <= maxLong and business['coordinates']['long'] >= minLong and business['coordinates']['lat'] <= maxLat and business['coordinates']['lat'] >= minLat ]

    
    # GET THE RESPECTIVE BROADCAST OF EACH BUSINESS
    for business in filteredBusiness:
        tracks = getTracks(business['_id'])

        for track in tracks:
            output.append({ 'business': business, 'track': track })

    return jsonify({ 'status': output })


def processData(_data):
    data = _data.decode()
    parsed = json.loads(data)
    return parsed

def getTracks(businessId):
    output = []

    docs = db.collection(u'tracks').where('businessId', '==', businessId).stream()

    for doc in docs:
        parsed = doc.to_dict()
        parsed['trackId'] = doc.id
        output.append(parsed)
    
    return output


if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 5000))
    # Run this for development
    # app.run(host='0.0.0.0', port=PORT, debug=True)
    # Run this for production
    serve(app, host='0.0.0.0', port=PORT)