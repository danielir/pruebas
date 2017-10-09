import pprint

#returns the recipe but scaled to other quantity of servings
def get_scaled_recipe(recipe, servings):
    if recipe["servings"] != servings:
        for ingredient in recipe["ingredients"]:
            scaledQuantity = servings * ingredient["quantity"] / recipe["servings"]
            ingredient["quantity"] = scaledQuantity;
    return recipe;



# calculates total ingredients for a list of recipes
def get_total_ingredients(recipes):

    total_ingredients = {}
    variety_units = {}

    # iterate recipes adding ingredients
    for recipe in recipes:
        for ingredient in recipe["ingredients"]:
            #print(ingredient)
            item = ingredient.get("item")
            quantity = ingredient.get("quantity")
            unit = ingredient.get("unit")

            # ingredients with unit themselves do not have item key, use unit instead
            if unit == None:
                unit = item

            # if it is first time this ingredient appears then add it
            if total_ingredients.get(item) == None:
                # add new ingredient dictionary
                total_ingredients[item] = {}
                total_ingredients[item]["quantity"] = quantity
                total_ingredients[item]["unit"] = unit
            else:
                # ingredient already exists, we have to add a quantity
                current_unit = total_ingredients[item]["unit"]
                current_quantity = total_ingredients[item]["quantity"]

                if current_unit == unit:
                    # if the units are equals then just add up quantities
                    total_ingredients[item]["quantity"] = current_quantity + quantity
                else:
                    #print("Different units " + unit + " and " + current_unit + " for ingredient", item)
                    # tactical solution
                    if total_ingredients[item]["unit"] != "variety":
                        total_ingredients[item]["unit"] = "variety"
                        variety_units[item] = {}
                        variety_units[item][unit] = quantity;
                        variety_units[item][current_unit] = current_quantity;
                        total_ingredients[item]["quantity"] = ""
                    else:
                        variety_item = variety_units.get(item)
                        if variety_item.get(unit) == None:
                            variety_item[unit] = quantity
                        else:
                            variety_item[unit] = quantity + variety_item[unit]

                    #total_ingredients[item]["quantity"] = str(quantity) + ' ' + unit + ', ' + str(current_quantity) + ' ' + current_unit

    result = []

    for key in total_ingredients.keys():
        total_ingredients[key]['item'] = key;
        if total_ingredients[key]['unit']=='variety':
            txt = ''
            for unit in variety_units[key]:
                if (txt!=''):
                    txt += ', '
                txt += str(variety_units[key][unit]) + ' ' + unit
            total_ingredients[key]['quantity'] = txt;

        result.append(total_ingredients[key])

    return result








