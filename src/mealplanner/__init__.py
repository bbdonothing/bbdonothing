"""Meal planner backend module.

Provides recipe filtering and weekly plan generation utilities.
"""

from .app import create_app
from .services import filter_recipes, generate_weekly_meal_plan

__all__ = [
    "create_app",
    "filter_recipes",
    "generate_weekly_meal_plan",
]
