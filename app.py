from flask import Flask, request, jsonify, render_template
import sqlite3
from itertools import combinations
import json

app = Flask(__name__)

# Load potion names from JSON file
with open('potion_names.json') as f:
    potion_names_data = json.load(f)

combat_names = potion_names_data["combat_names"]
utility_names = potion_names_data["utility_names"]
whimsy_names = potion_names_data["whimsy_names"]

# Database connection helper function
def get_db_connection():
    conn = sqlite3.connect('recipes.db')
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn

# Route to the main page to display the ingredient selection form
@app.route('/')
def index():
    conn = get_db_connection()
    ingredients = conn.execute("SELECT name, rarity, combat, utility, whimsy FROM ingredients").fetchall()
    conn.close()
    # Separate ingredients by rarity for display in columns
    common_ingredients = [ing for ing in ingredients if ing['rarity'] == 'C']
    uncommon_ingredients = [ing for ing in ingredients if ing['rarity'] == 'U']
    rare_ingredients = [ing for ing in ingredients if ing['rarity'] == 'R']
    return render_template('index.html', common_ingredients=common_ingredients,
                           uncommon_ingredients=uncommon_ingredients, rare_ingredients=rare_ingredients)

# Calculate all possible recipes based on selected ingredients
@app.route('/get-recipes', methods=['POST'])
def get_recipes():
    user_ingredients = request.json['ingredients']  # Get selected ingredients
    conn = get_db_connection()

    # Retrieve ingredient details for each selected ingredient
    placeholders = ','.join('?' * len(user_ingredients))
    query = f"SELECT name, rarity, combat, utility, whimsy FROM ingredients WHERE name IN ({placeholders})"
    ingredient_data = conn.execute(query, user_ingredients).fetchall()
    conn.close()

    # Calculate all possible recipes from every combination of three ingredients
    possible_recipes = {'Combat': [], 'Utility': [], 'Whimsy': []}
    for combo in combinations(ingredient_data, 3):
        total_combat = sum([ing['combat'] for ing in combo])
        total_utility = sum([ing['utility'] for ing in combo])
        total_whimsy = sum([ing['whimsy'] for ing in combo])

        # Determine the potion type and handle ties by creating multiple recipes if needed
        recipe_types = []
        if total_combat > total_utility and total_combat > total_whimsy:
            recipe_types.append(("Combat", total_combat))
        if total_utility > total_combat and total_utility > total_whimsy:
            recipe_types.append(("Utility", total_utility))
        if total_whimsy > total_combat and total_whimsy > total_utility:
            recipe_types.append(("Whimsy", total_whimsy))
        
        # If there's a tie between any of the attributes, add both tied recipes
        if len(recipe_types) == 0:  # All three are tied
            recipe_types = [("Combat", total_combat), ("Utility", total_utility), ("Whimsy", total_whimsy)]
        elif len(recipe_types) == 2:  # Two are tied
            recipe_types = recipe_types

        # Add recipes to the result for each type in recipe_types
        for potion_type, potion_value in recipe_types:
            # Fetch the appropriate potion name from the dictionary (converting the number to a string for lookup)
            potion_name = ""
            if potion_type == "Combat":
                potion_name = f"{potion_value}. {combat_names.get(str(potion_value), 'Unknown')}"
            elif potion_type == "Utility":
                potion_name = f"{potion_value}. {utility_names.get(str(potion_value), 'Unknown')}"
            elif potion_type == "Whimsy":
                potion_name = f"{potion_value}. {whimsy_names.get(str(potion_value), 'Unknown')}"

            recipe = {
                "potion_type": potion_name,
                "attribute_totals": f"[{total_combat}/{total_utility}/{total_whimsy}]",
                "ingredients": [
                    {
                        "name": ing["name"],
                        "rarity": ing["rarity"],
                        "combat": ing["combat"],
                        "utility": ing["utility"],
                        "whimsy": ing["whimsy"]
                    } for ing in combo
                ]
            }
            possible_recipes[potion_type].append(recipe)

    # Sort each potion type's recipes alphabetically by potion type
    for potions in possible_recipes.values():
        potions.sort(key=lambda x: x['potion_type'])

    # Return list of possible recipes as JSON
    return jsonify(possible_recipes)

if __name__ == '__main__':
    app.run(debug=True)
