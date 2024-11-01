from flask import Flask, request, jsonify, render_template
import sqlite3

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
    ingredients = conn.execute("SELECT name FROM ingredients").fetchall()  # Get list of ingredients
    conn.close()
    return render_template('index.html', ingredients=[row['name'] for row in ingredients])

# Calculate recipes based on selected ingredients
@app.route('/get-recipes', methods=['POST'])
def get_recipes():
    user_ingredients = request.json['ingredients']  # Get selected ingredients from the request
    conn = get_db_connection()
    
    # Retrieve ingredient scores
    query = "SELECT combat, utility, whimsy FROM ingredients WHERE name IN ({})".format(','.join(['?'] * len(user_ingredients)))
    ingredient_data = conn.execute(query, user_ingredients).fetchall()
    conn.close()

    # Calculate total attribute scores
    total_combat = sum([row['combat'] for row in ingredient_data])
    total_utility = sum([row['utility'] for row in ingredient_data])
    total_whimsy = sum([row['whimsy'] for row in ingredient_data])

    # Determine the recipe type based on highest score
    if total_combat > total_utility and total_combat > total_whimsy:
        recipe_type = "Combat"
        recipe_score = total_combat
    elif total_utility > total_combat and total_utility > total_whimsy:
        recipe_type = "Utility"
        recipe_score = total_utility
    else:
        recipe_type = "Whimsy"
        recipe_score = total_whimsy

    # Send recipe type and score back to frontend
    recipe_result = {"recipe_type": recipe_type, "recipe_score": recipe_score}
    return jsonify(recipe_result)

if __name__ == '__main__':
    app.run(debug=True)
