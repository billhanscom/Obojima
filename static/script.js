async function findRecipes() {
    // Get selected ingredients
    const selectedIngredients = Array.from(document.querySelectorAll('input[name="ingredient"]:checked'))
                                      .map(checkbox => checkbox.value);

    // Send selected ingredients to the backend
    const response = await fetch('/get-recipes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ingredients: selectedIngredients })
    });

    // Display each possible recipe from the response in columns by potion type
    const recipes = await response.json();
    window.generatedRecipes = recipes;  // Store recipes globally for export
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '';

    ['Combat', 'Utility', 'Whimsy'].forEach(type => {
        const column = document.createElement('div');
        column.classList.add('recipe-column');
        column.innerHTML = `<h3>${type} Potions</h3>`;

        if (recipes[type] && recipes[type].length > 0) {
            column.innerHTML += recipes[type].map(recipe => {
                const ingredientsList = recipe.ingredients.map(ing => `
                    <li>${ing.name} [${ing.combat}/${ing.utility}/${ing.whimsy}]</li>
                `).join('');
                return `<h4>${recipe.potion_type} ${recipe.attribute_totals}</h4><ul>${ingredientsList}</ul>`;
            }).join('');
        } else {
            column.innerHTML += '<p>No recipes found</p>';
        }
        resultsDiv.appendChild(column);
    });
}

// Export PDF function
async function exportPDF() {
    const selectedIngredients = Array.from(document.querySelectorAll('input[name="ingredient"]:checked'))
                                      .map(checkbox => checkbox.value);
    const recipes = window.generatedRecipes;

    if (!recipes || !selectedIngredients.length) {
        alert("Please select ingredients and generate recipes first.");
        return;
    }

    const response = await fetch('/export-pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ingredients: selectedIngredients, recipes: recipes })
    });

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'potion_recipe_report.pdf';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Function to clear selected ingredients
function clearSelection() {
    document.querySelectorAll('input[name="ingredient"]:checked').forEach(checkbox => checkbox.checked = false);
    document.getElementById('results').innerHTML = ''; // Clear results as well
}
