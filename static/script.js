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

    // Display each possible recipe from the response
    const recipes = await response.json();
    const resultsDiv = document.getElementById('results');
    if (recipes.length > 0) {
        resultsDiv.innerHTML = recipes.map(recipe => {
            const ingredientsList = recipe.ingredients.map(ing => `
                <li>${ing.name} (${ing.rarity}): [Combat: ${ing.combat}, Utility: ${ing.utility}, Whimsy: ${ing.whimsy}]</li>
            `).join('');
            return `<h3>${recipe.potion_type}</h3><ul>${ingredientsList}</ul>`;
        }).join('');
    } else {
        resultsDiv.innerHTML = '<p>No matching recipes found</p>';
    }
}
