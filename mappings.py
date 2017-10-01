import json
import json
import pprint
import pymongo
from bson.objectid import ObjectId
import smtp
from flask import Flask,Request,jsonify,Response,request,abort
from flask_cors import CORS
from pymongo import MongoClient

def search_mappings_by_name(word):
    client = MongoClient('127.0.0.1', 27017)
    db = client.test
    mappings = db.mappings.find({'name': {'$regex': '.*' + word + '.*'}})
    return mappings

def search_mapping(word):
    client = MongoClient('127.0.0.1', 27017)
    db = client.test
    mappings = db.mappings.find({}, {word : 1})
    return mappings

def update_mapping(object):
    client = MongoClient('127.0.0.1', 27017)
    db = client.test
    mappings = db.mappings.update({"name":"mercadona by dani"}, {"$set" : object})
    return mappings


app = Flask(__name__)
CORS(app)

@app.route("/mappings/", methods = ['GET'])
def mappings():
    if 'search' in request.args:
        dbresult = search_mappings_by_name(request.args['search'])
        m = list(dbresult)
    elif 'ingredient' in request.args:
        dbresult = search_mapping(request.args['ingredient'])
        l = list(dbresult)
        m = l[0][request.args['ingredient']]

    recipes_json = json.dumps(m, cls=JSONEncoder)
    resp = Response(recipes_json, mimetype='application/json')
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

@app.route("/mappings/", methods = ['PUT'])
def update_mappings():
    mapping = json.loads(request.data)
    print("mapping",mapping)
    db_resp = update_mapping(mapping)
    mappings_response = json.dumps(db_resp, cls=JSONEncoder)
    resp = Response(mappings_response, mimetype='application/json')
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

app.run(host="localhost", port=5002)







