import json
import pprint
import pymongo
from bson.objectid import ObjectId
import smtp
from flask import Flask,Request,jsonify,Response,request,abort
from flask_cors import CORS
from pymongo import MongoClient
import calculator


def get_all_recipes():
    client = MongoClient('127.0.0.1', 27017)
    db = client.test
    recipes = list(db.recipes.find({}, {'_id':1, 'name':1}))
    return recipes

def search_recipes_by_name(word):
    client = MongoClient('127.0.0.1', 27017)
    db = client.test
    recipes = db.recipes.find({'name': {'$regex': '.*' + word + '.*'}})
    return recipes

def search_recipes_containing(word):
    client = MongoClient('127.0.0.1', 27017)
    db = client.test
    recipes = db.recipes.find({'$or' : [{'name':{'$regex': '.*' + word +'.*'}},{'ingredients': {'$elemMatch': {'item': {'$regex': '.*' + word + '.*'}}}}]})
    return recipes

def get_recipe_by_name(name):
    client = MongoClient('127.0.0.1', 27017)
    db = client.test
    recipe = db.recipes.find({'name':name})
    return recipe

def get_recipe_by_id(id):
    client = MongoClient('127.0.0.1', 27017)
    db = client.test
    recipe = db.recipes.find({'_id':ObjectId(id)}, {"_id":0})
    return recipe

app = Flask(__name__)
CORS(app)

@app.route("/recipes/", methods = ['GET'])
def recipes():
    if 'search' in request.args:
        dbrecipes = search_recipes_by_name(request.args['search'])
    elif 'contains' in request.args:
        dbrecipes = search_recipes_containing(request.args['contains'])
    else:
        dbrecipes = list(get_all_recipes())
    recipes = []
    for dbrecipe in dbrecipes:
        recipes.append({'id':str(dbrecipe["_id"]), 'name':dbrecipe["name"]})
    recipes_json = json.dumps(recipes)
    resp = Response(recipes_json, mimetype='application/json')
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

@app.route("/recipes/name/<name>")
def recipe_detail_by_name(name):
    dbrecipe = get_recipe_by_name(name)
    recipes_json = json.dumps(list(dbrecipe), cls=JSONEncoder)
    resp = Response(recipes_json, mimetype='application/json')
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route("/recipes/id/<id>")
def recipe_detail_by_id(id):
    dbrecipe = get_recipe_by_id(id)
    recipes_json = json.dumps(list(dbrecipe), cls=JSONEncoder)
    resp = Response(recipes_json, mimetype='application/json')
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

@app.route("/recipes/shopping-list/", methods = ['POST'])
def recipes_calculate_ingredients():
    '''
    mockresponse = {"0": [{"id": "59b99963a8baaaf3676c57ed", "name": "pimientos rellenos (bajoques farcides)"}],
    "1": [{"id": "59b99963a8baaaf3676c57ef", "name": "arroz con verduras"}], "2": [], "3": [],
    "4": [{"id": "59b99963a8baaaf3676c57eb", "name": "ensalada de lentejas"}]}
    '''
    recipes_data = request.data
    mockresponse = json.loads(recipes_data)
    recipes = []
    print(mockresponse)
    for day in mockresponse.keys():
        print("day ", day)
        day_recipes = mockresponse.get(day)
        for recipe in day_recipes:
            print(recipe["id"]," ", recipe["servings"])
            data = get_recipe_by_id(recipe["id"])
            for item in data:
                if item["servings"]!=recipe["servings"]:
                    print("We should adapt ",recipe["name"]," from ",item["servings"]," to ",recipe["servings"])
                    item = calculator.get_scaled_recipe(item, int(recipe["servings"]))
                recipes.append(item)

    print("recipes:",recipes)
    total_ingredients = calculator.get_total_ingredients(recipes)
    print("total ingredients", total_ingredients)
    #total_ingredients = {"id":"1", "ingredients": total_ingredients}
    total_ingredients_json = json.dumps(total_ingredients, cls=JSONEncoder)

    resp = Response(total_ingredients_json, mimetype='application/json')
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

#recipes_calculate_ingredients()
app.run(host="localhost")
#app.run(host="192.168.1.129")







