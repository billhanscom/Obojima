from flask import Flask, request, jsonify, render_template
import sqlite3
from itertools import combinations

app = Flask(__name__)

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

        # Determine the potion type and value based on highest score
        if total_combat > total_utility and total_combat > total_whimsy:
            potion_type = "Combat"
            potion_value = total_combat
        elif total_utility > total_combat and total_utility > total_whimsy:
            potion_type = "Utility"
            potion_value = total_utility
        else:
            potion_type = "Whimsy"
            potion_value = total_whimsy

        # Format each recipe result with details
        recipe = {
            "potion_type": f"{potion_type} {potion_value}",
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
