const recipes = [
  {
    id: 'med-salad',
    name: 'Mediterranean Power Salad',
    cuisine: 'Mediterranean',
    diet: 'Pescatarian',
    fitnessGoal: 'Lean muscle',
    ingredients: [
      { name: 'Quinoa', quantity: 1, unit: 'cup', substitutions: ['Farro', 'Brown rice'] },
      { name: 'Cherry tomatoes', quantity: 1, unit: 'cup', substitutions: ['Roma tomatoes'] },
      { name: 'Feta cheese', quantity: 0.5, unit: 'cup', substitutions: ['Goat cheese'] },
      { name: 'Olive oil', quantity: 2, unit: 'tbsp', substitutions: ['Avocado oil'] },
      { name: 'Chickpeas', quantity: 1, unit: 'can', substitutions: ['White beans'] }
    ]
  },
  {
    id: 'sheet-pan',
    name: 'Sheet Pan Chicken & Veg',
    cuisine: 'American',
    diet: 'High protein',
    fitnessGoal: 'Fat loss',
    ingredients: [
      { name: 'Chicken breast', quantity: 1, unit: 'lb', substitutions: ['Chicken thighs', 'Tofu'] },
      { name: 'Broccoli', quantity: 2, unit: 'cups', substitutions: ['Cauliflower'] },
      { name: 'Sweet potato', quantity: 2, unit: 'medium', substitutions: ['Butternut squash'] },
      { name: 'Olive oil', quantity: 2, unit: 'tbsp', substitutions: ['Avocado oil'] },
      { name: 'Smoked paprika', quantity: 1, unit: 'tsp', substitutions: ['Chili powder'] }
    ]
  },
  {
    id: 'tofu-stirfry',
    name: 'Ginger Tofu Stir-Fry',
    cuisine: 'Asian',
    diet: 'Vegan',
    fitnessGoal: 'Endurance',
    ingredients: [
      { name: 'Extra-firm tofu', quantity: 14, unit: 'oz', substitutions: ['Tempeh'] },
      { name: 'Snow peas', quantity: 2, unit: 'cups', substitutions: ['Green beans'] },
      { name: 'Bell pepper', quantity: 1, unit: 'large', substitutions: ['Zucchini'] },
      { name: 'Brown rice', quantity: 1, unit: 'cup', substitutions: ['Quinoa'] },
      { name: 'Soy sauce', quantity: 3, unit: 'tbsp', substitutions: ['Tamari', 'Coconut aminos'] }
    ]
  },
  {
    id: 'salmon-bowl',
    name: 'Miso Salmon Bowl',
    cuisine: 'Asian',
    diet: 'Pescatarian',
    fitnessGoal: 'Lean muscle',
    ingredients: [
      { name: 'Salmon fillet', quantity: 1, unit: 'lb', substitutions: ['Trout'] },
      { name: 'Brown rice', quantity: 1, unit: 'cup', substitutions: ['Quinoa'] },
      { name: 'Edamame', quantity: 1, unit: 'cup', substitutions: ['Green peas'] },
      { name: 'Cucumber', quantity: 1, unit: 'medium', substitutions: ['Zucchini'] },
      { name: 'Miso paste', quantity: 2, unit: 'tbsp', substitutions: ['Soy sauce'] }
    ]
  },
  {
    id: 'oats-bake',
    name: 'Berry Protein Oats Bake',
    cuisine: 'American',
    diet: 'Vegetarian',
    fitnessGoal: 'Recovery',
    ingredients: [
      { name: 'Rolled oats', quantity: 2, unit: 'cups', substitutions: ['Quinoa flakes'] },
      { name: 'Greek yogurt', quantity: 1, unit: 'cup', substitutions: ['Skyr'] },
      { name: 'Mixed berries', quantity: 1, unit: 'cup', substitutions: ['Frozen berries'] },
      { name: 'Almond milk', quantity: 1, unit: 'cup', substitutions: ['Oat milk'] },
      { name: 'Chia seeds', quantity: 2, unit: 'tbsp', substitutions: ['Ground flaxseed'] }
    ]
  }
];

const preferences = {
  diet: ['Any', ...new Set(recipes.map((r) => r.diet))],
  cuisine: ['Any', ...new Set(recipes.map((r) => r.cuisine))],
  fitnessGoal: ['Any', ...new Set(recipes.map((r) => r.fitnessGoal))]
};

const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

const state = {
  selections: Object.fromEntries(days.map((day) => [day, null])),
  pantry: new Set(['Olive oil', 'Almond milk']),
  filters: { diet: 'Any', cuisine: 'Any', fitnessGoal: 'Any' },
  substitutions: {}
};

const dietSelect = document.getElementById('diet-select');
const cuisineSelect = document.getElementById('cuisine-select');
const fitnessSelect = document.getElementById('fitness-select');
const weeklyPlan = document.getElementById('weekly-plan');
const groceryList = document.getElementById('grocery-list');
const pantryInput = document.getElementById('pantry-input');
const addPantryBtn = document.getElementById('add-pantry');
const pantryTags = document.getElementById('pantry-tags');
const substitutionSuggestions = document.getElementById('substitution-suggestions');

function populateSelect(select, options) {
  select.innerHTML = '';
  options.forEach((option) => {
    const opt = document.createElement('option');
    opt.value = option;
    opt.textContent = option;
    select.appendChild(opt);
  });
}

function initControls() {
  populateSelect(dietSelect, preferences.diet);
  populateSelect(cuisineSelect, preferences.cuisine);
  populateSelect(fitnessSelect, preferences.fitnessGoal);

  dietSelect.addEventListener('change', () => updateFilters('diet', dietSelect.value));
  cuisineSelect.addEventListener('change', () => updateFilters('cuisine', cuisineSelect.value));
  fitnessSelect.addEventListener('change', () => updateFilters('fitnessGoal', fitnessSelect.value));

  addPantryBtn.addEventListener('click', () => {
    const item = pantryInput.value.trim();
    if (!item) return;
    state.pantry.add(capitalize(item));
    pantryInput.value = '';
    renderPantry();
    refresh();
  });

  pantryInput.addEventListener('keyup', (e) => {
    if (e.key === 'Enter') {
      addPantryBtn.click();
    }
  });
}

function capitalize(text) {
  return text
    .split(' ')
    .filter(Boolean)
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ');
}

function updateFilters(type, value) {
  state.filters[type] = value;
  renderWeeklyPlan();
  refresh();
}

function filterRecipes() {
  return recipes.filter((recipe) => {
    const { diet, cuisine, fitnessGoal } = state.filters;
    const matchesDiet = diet === 'Any' || recipe.diet === diet;
    const matchesCuisine = cuisine === 'Any' || recipe.cuisine === cuisine;
    const matchesFitness = fitnessGoal === 'Any' || recipe.fitnessGoal === fitnessGoal;
    return matchesDiet && matchesCuisine && matchesFitness;
  });
}

function renderWeeklyPlan() {
  weeklyPlan.innerHTML = '';
  const available = filterRecipes();

  days.forEach((day) => {
    const wrapper = document.createElement('div');
    wrapper.className = 'day-card';

    const heading = document.createElement('h3');
    heading.textContent = day;
    wrapper.appendChild(heading);

    const select = document.createElement('select');
    const emptyOpt = document.createElement('option');
    emptyOpt.value = '';
    emptyOpt.textContent = 'No recipe';
    select.appendChild(emptyOpt);

    available.forEach((recipe) => {
      const opt = document.createElement('option');
      opt.value = recipe.id;
      opt.textContent = recipe.name;
      if (state.selections[day] === recipe.id) opt.selected = true;
      select.appendChild(opt);
    });

    select.addEventListener('change', () => {
      state.selections[day] = select.value || null;
      refresh();
    });

    wrapper.appendChild(select);
    weeklyPlan.appendChild(wrapper);
  });
}

function renderPantry() {
  pantryTags.innerHTML = '';
  state.pantry.forEach((item) => {
    const tag = document.createElement('span');
    tag.className = 'tag';
    tag.textContent = item;

    const remove = document.createElement('button');
    remove.ariaLabel = `Remove ${item}`;
    remove.textContent = '×';
    remove.addEventListener('click', () => {
      state.pantry.delete(item);
      if (state.substitutions[item]) delete state.substitutions[item];
      renderPantry();
      refresh();
    });
    tag.appendChild(remove);
    pantryTags.appendChild(tag);
  });
}

function collectSelectedRecipes() {
  return Object.values(state.selections)
    .filter(Boolean)
    .map((id) => recipes.find((r) => r.id === id));
}

function buildSubstitutionSuggestions(selectedRecipes) {
  const suggestions = [];
  selectedRecipes.forEach((recipe) => {
    recipe.ingredients.forEach((ingredient) => {
      const hasPantry = state.pantry.has(ingredient.name);
      const existing = state.substitutions[ingredient.name];
      if (hasPantry || existing) return;
      const viableSub = ingredient.substitutions?.find((sub) => state.pantry.has(sub));
      if (viableSub) {
        suggestions.push({
          ingredient: ingredient.name,
          substitute: viableSub,
          recipe: recipe.name
        });
      }
    });
  });
  return suggestions;
}

function renderSubstitutionSuggestions(selectedRecipes) {
  substitutionSuggestions.innerHTML = '';
  const suggestions = buildSubstitutionSuggestions(selectedRecipes);

  if (!suggestions.length) {
    substitutionSuggestions.innerHTML = '<p class="subtle">No substitutions to review. Pantry items already cover your picks.</p>';
    return;
  }

  suggestions.forEach((suggestion) => {
    const card = document.createElement('div');
    card.className = 'suggestion';
    card.innerHTML = `
      <div><strong>${suggestion.substitute}</strong> can replace <strong>${suggestion.ingredient}</strong></div>
      <p class="subtle">Available in pantry for ${suggestion.recipe}.</p>
    `;

    const acceptBtn = document.createElement('button');
    acceptBtn.className = 'btn';
    acceptBtn.textContent = 'Use substitution';
    acceptBtn.addEventListener('click', () => {
      state.substitutions[suggestion.ingredient] = suggestion.substitute;
      refresh();
    });

    card.appendChild(acceptBtn);
    substitutionSuggestions.appendChild(card);
  });
}

function calculateGroceryList(selectedRecipes) {
  const totals = {};

  selectedRecipes.forEach((recipe) => {
    recipe.ingredients.forEach((ingredient) => {
      const substituted = state.substitutions[ingredient.name];
      const nameToUse = substituted || ingredient.name;
      if (state.pantry.has(nameToUse)) return;

      if (!totals[nameToUse]) {
        totals[nameToUse] = { quantity: 0, unit: ingredient.unit };
      }
      totals[nameToUse].quantity += ingredient.quantity;
    });
  });

  return Object.entries(totals).map(([name, detail]) => ({ name, ...detail }));
}

function renderGroceryList(selectedRecipes) {
  groceryList.innerHTML = '';
  const items = calculateGroceryList(selectedRecipes);

  if (!items.length) {
    groceryList.innerHTML = '<p class="subtle">Your pantry covers everything. Add recipes to see what you need.</p>';
    return;
  }

  items.forEach((item) => {
    const row = document.createElement('div');
    row.className = 'list__item';
    row.innerHTML = `
      <span>${item.name}</span>
      <strong>${item.quantity} ${item.unit}</strong>
    `;
    groceryList.appendChild(row);
  });
}

function refresh() {
  const selectedRecipes = collectSelectedRecipes();
  renderSubstitutionSuggestions(selectedRecipes);
  renderGroceryList(selectedRecipes);
}

function bootstrap() {
  initControls();
  renderPantry();
  renderWeeklyPlan();
  refresh();
}

bootstrap();
