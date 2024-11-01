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

    // Display the recipe result from the backend
    const recipe = await response.json();
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = recipe
        ? `<p>Recipe Type: ${recipe.recipe_type}</p><p>Score: ${recipe.recipe_score}</p>`
        : '<p>No matching recipe found</p>';
}
