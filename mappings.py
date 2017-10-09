import json
import json
import pprint
import pymongo
from bson.objectid import ObjectId
import smtp
from flask import Flask,Request,jsonify,Response,request,abort
from flask_cors import CORS
from pymongo import MongoClient

def get_mapping(mapping_name):
    mapped_ingredients = db.mappings.find({'name': mapping_name })
    return mapped_ingredients

def search_mapping(mapping_name, ingredient):
    mappings = db.mappings.find({"name":mapping_name}, {ingredient : 1})
    return mappings

def update_mapping(mapping_name, object):
    mappings = db.mappings.update({"name":mapping_name}, {"$set" : object})
    return mappings


app = Flask(__name__)
CORS(app)
client = MongoClient('127.0.0.1', 27017)
db = client.test


@app.route("/mappings/", methods = ['GET'])
def mappings():
    if 'ingredient' in request.args:
        if 'mapping' in request.args:
            mapping = request.args["mapping"]
        else:
            mapping = "mercadona by dani"
        dbresult = search_mapping(mapping, request.args['ingredient'])
        l = list(dbresult)
        m = l[0][request.args['ingredient']]
    elif 'name' in request.args:
        dbresult = get_mapping(request.args['name'])
        m = list(dbresult)

    recipes_json = json.dumps(m, cls=JSONEncoder)
    resp = Response(recipes_json, mimetype='application/json')
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

@app.route("/mappings/", methods = ['PUT'])
def update_mappings():
    mapping = json.loads(request.data)
    db_resp = update_mapping("mercadona by dani", mapping)
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







