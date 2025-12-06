from itertools import cycle
from typing import Iterable, List, Optional

from .data_loader import load_recipes
from .models import MealPlanDay, Recipe


def _normalize(values: Optional[Iterable[str]]) -> List[str]:
    return [value.lower() for value in values] if values else []


def filter_recipes(
    *,
    dietary_tags: Optional[Iterable[str]] = None,
    cuisine: Optional[str] = None,
    fitness_goals: Optional[Iterable[str]] = None,
) -> List[Recipe]:
    recipes = load_recipes()
    normalized_tags = set(_normalize(dietary_tags))
    normalized_goals = set(_normalize(fitness_goals))
    target_cuisine = cuisine.lower() if cuisine else None

    filtered: List[Recipe] = []
    for recipe in recipes:
        if target_cuisine and recipe.cuisine.lower() != target_cuisine:
            continue

        recipe_tags = {tag.lower() for tag in recipe.dietary_tags}
        recipe_goals = {goal.lower() for goal in recipe.fitness_goals}

        if normalized_tags and not normalized_tags.issubset(recipe_tags):
            continue
        if normalized_goals and not normalized_goals.issubset(recipe_goals):
            continue

        filtered.append(recipe)

    return filtered


def generate_weekly_meal_plan(
    *,
    dietary_tags: Optional[Iterable[str]] = None,
    cuisine: Optional[str] = None,
    fitness_goals: Optional[Iterable[str]] = None,
    meals_per_day: int = 3,
) -> List[MealPlanDay]:
    filtered_recipes = filter_recipes(
        dietary_tags=dietary_tags, cuisine=cuisine, fitness_goals=fitness_goals
    )
    if not filtered_recipes:
        return []

    day_names = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    rotating_recipes = cycle(filtered_recipes)
    plan: List[MealPlanDay] = []
    for day in day_names:
        meals = [next(rotating_recipes) for _ in range(meals_per_day)]
        plan.append(MealPlanDay(day=day, meals=meals))

    return plan
