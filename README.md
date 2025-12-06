# Meal Planner Backend

This repository contains a minimal FastAPI backend for filtering recipes by dietary tags, cuisine, and fitness goals. It also provides a weekly meal-plan generator that uses the filtered recipes to build plans aligned with user preferences.

## Features
- Filter recipes by cuisine, dietary tags (e.g., vegan, gluten-free), and fitness goals (e.g., weight_loss, muscle_gain).
- Generate a 7-day meal plan using the available recipes and user preferences.
- Sample recipe data stored in `src/mealplanner/data/recipes.json`.

## Getting Started
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the FastAPI server:
   ```bash
   uvicorn mealplanner.app:app --reload
   ```

## API Overview
- `GET /recipes`
  - Query params: `dietary_tags`, `cuisine`, `fitness_goals`.
  - Returns matching recipes from the sample data.
- `POST /meal-plans/weekly`
  - Body: `{ "dietary_tags": ["vegan"], "cuisine": "Asian", "fitness_goals": ["weight_loss"], "meals_per_day": 3 }`
  - Returns a 7-day plan cycling through the filtered recipes.

Open http://127.0.0.1:8000/docs for interactive API exploration once the server is running.
