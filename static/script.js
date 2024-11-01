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
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '';

    ['Combat', 'Utility', 'Whimsy'].forEach(type => {
        const column = document.createElement('div');
        column.classList.add('recipe-column');
        column.innerHTML = `<h3>${type} Potions</h3>`;

        if (recipes[type] && recipes[type].length > 0) {
            column.innerHTML += recipes[type].map(recipe => {
                const ingredientsList = recipe.ingredients.map(ing => `
                    <li><span class="${ing.rarity.toLowerCase()}">${ing.name}</span> [${ing.combat}/${ing.utility}/${ing.whimsy}]</li>
                `).join('');
                return `<h4>${recipe.potion_type}</h4><ul>${ingredientsList}</ul>`;
            }).join('');
        } else {
            column.innerHTML += '<p>No recipes found</p>';
        }
        resultsDiv.appendChild(column);
    });
}
