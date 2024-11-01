let selectedIngredients = [];

// Toggle selection for ingredient buttons
document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".ingredient-button").forEach(button => {
        button.addEventListener("click", () => {
            const ingredient = button.getAttribute("data-ingredient");
            button.classList.toggle("selected");
            if (selectedIngredients.includes(ingredient)) {
                selectedIngredients = selectedIngredients.filter(i => i !== ingredient);
            } else {
                selectedIngredients.push(ingredient);
            }
        });
    });
});

async function findRecipes() {
    if (selectedIngredients.length === 0) {
        alert("Please select at least one ingredient.");
        return;
    }

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

// Function to clear selected ingredients
function clearSelection() {
    selectedIngredients = [];
    document.querySelectorAll(".ingredient-button").forEach(button => {
        button.classList.remove("selected");
    });
    document.getElementById('results').innerHTML = ''; // Clear results as well
}
