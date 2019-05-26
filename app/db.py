import pymongo
import config
import json
from bson.objectid import ObjectId
from models import User
from flask import jsonify


class DB():
    # Instantiate PyMongo
    myclient = pymongo.MongoClient(config.DBHOST)
    mydb = myclient[config.DBNAME]

    # Collections
    userCol = mydb["users"]

    def authenticateUser(self, _uid, _password):
        query = {'uid': _uid, 'password': _password}
        return self.userCol.find_one(query)

    def registerUser(self, _user):
        user = self.processData(_user)
        query = self.find('username', user['username']).count()

        if query == 0:
            if self.userCol.insert_one(user):
                return _user
        else:
            return jsonify({'status': False})

    def changePassword(self, _data):
        data = self.processData(_data)
        query = {'username': data['username']}
        newValue = {'$set': {'password': data['newPassword']}}
        try:
            self.userCol.update_one(query, newValue)
            return True
        except:
            return False


    def getUsers(self):
        return self.convertToList(self.userCol.find())

    def find(self, attribute, param):
        query = {attribute: param}
        return self.userCol.find(query)

    def processData(self, _data):
        data = _data.decode()
        parsed = json.loads(data)
        return parsed['body']

    def convertToList(self, data):
        data = list(data)
        for x in data:
            x['_id'] = str(x['_id'])
        return json.dumps(data)
