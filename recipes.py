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
    recipes = list(db.recipes.find({}, {'_id':1, 'name':1}))
    return recipes

def get_recipe_by_name(name):
    recipe = db.recipes.find({'name':name})
    return recipe

def get_recipe_by_id(id):
    recipe = db.recipes.find({'_id':ObjectId(id)}, {"_id":0})
    return recipe

def search_recipes_by_name(recipe_name):
    recipes = db.recipes.find({'name': {'$regex': '.*' + recipe_name + '.*'}})
    return recipes

# search recipes containing term in ingredients and name
def search_recipes_containing(term):
    recipes = db.recipes.find({'$or' : [{'name':{'$regex': '.*' + term +'.*'}},{'ingredients': {'$elemMatch': {'item': {'$regex': '.*' + term + '.*'}}}}]})
    return recipes

def store_week_recipes(week_name, user, week_recipes):
    result = db.plannings.update({'$and' : [{"weekName":week_name},{"user":user}]},{'$set': {"weekPlanning" : week_recipes} })
    return result

def get_plannings_by_user(user):
    recipe = db.plannings.find({'user': user})
    return recipe

app = Flask(__name__)
CORS(app)
client = MongoClient('127.0.0.1', 27017)
db = client.test



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
    recipes_data = request.data
    week_recipes = json.loads(recipes_data)
    recipes = []
    for day_index in week_recipes.keys():
        day_recipes = week_recipes.get(day_index)
        for recipe in day_recipes:
            db_recipe = get_recipe_by_id(recipe["id"])[0]
            if db_recipe["servings"]!=recipe["servings"]:
                db_recipe = calculator.get_scaled_recipe(db_recipe, int(recipe["servings"]))
            recipes.append(db_recipe)

    total_ingredients = calculator.get_total_ingredients(recipes)
    total_ingredients_json = json.dumps(total_ingredients, cls=JSONEncoder)
    resp = Response(total_ingredients_json, mimetype='application/json')
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

@app.route("/plannings/", methods = ['POST'])
def store_week():
    data = json.loads(request.data)
    week_name = data["weekName"]
    week_recipes = data["weekRecipes"]
    result = store_week_recipes(week_name,"dani",week_recipes)
    if result["updatedExisting"]:
        return Response(json.dumps(result), status=200, mimetype='application/json')
    else:
        return Response(json.dumps(result), status=404, mimetype='application/json')

@app.route("/plannings/", methods = ['GET'])
def get_plannings():
    dbplannings = get_plannings_by_user("dani")
    plannings = []
    for dbresult in dbplannings:
        plannings.append({'id': str(dbresult["_id"]), 'weekName': dbresult["weekName"]})
    result_json = json.dumps(plannings, cls=JSONEncoder)
    return Response(result_json, status=200, mimetype='application/json')



class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

app.run(host="localhost")
#app.run(host="192.168.1.129")







