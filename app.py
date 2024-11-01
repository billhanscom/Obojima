from flask import Flask, request, jsonify, render_template, send_file
import sqlite3
from itertools import combinations
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO

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

        # Format each recipe result with details and total attributes
        recipe = {
            "potion_type": f"{potion_type} {potion_value}",
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

# Generate PDF report of selected ingredients and recipes
@app.route('/export-pdf', methods=['POST'])
def export_pdf():
    data = request.json
    selected_ingredients = data['ingredients']
    recipes = data['recipes']

    # Create a PDF in memory
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Potion Recipe Report")

    # Selected Ingredients
    y_position = height - 80
    c.setFont("Helvetica", 12)
    c.drawString(50, y_position, "Selected Ingredients:")
    y_position -= 20

    for ingredient in selected_ingredients:
        c.drawString(60, y_position, f"{ingredient['name']} ({ingredient['rarity']}) [Combat: {ingredient['combat']}, Utility: {ingredient['utility']}, Whimsy: {ingredient['whimsy']}]")
        y_position -= 15

    # Recipes
    y_position -= 20
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y_position, "Generated Recipes:")
    y_position -= 20
    c.setFont("Helvetica", 12)

    for potion_type, recipe_list in recipes.items():
        c.drawString(50, y_position, f"{potion_type} Potions:")
        y_position -= 20
        for recipe in recipe_list:
            c.drawString(60, y_position, f"{recipe['potion_type']} {recipe['attribute_totals']}")
            y_position -= 15
            for ingredient in recipe['ingredients']:
                c.drawString(80, y_position, f"{ingredient['name']} ({ingredient['rarity']}) [Combat: {ingredient['combat']}, Utility: {ingredient['utility']}, Whimsy: {ingredient['whimsy']}]")
                y_position -= 15
            y_position -= 10

            if y_position < 50:
                c.showPage()
                y_position = height - 50

    c.save()
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="potion_recipe_report.pdf", mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)
