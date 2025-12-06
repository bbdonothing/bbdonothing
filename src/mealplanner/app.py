from typing import List, Optional

from fastapi import FastAPI
from pydantic import BaseModel

from .services import filter_recipes, generate_weekly_meal_plan


class RecipeOut(BaseModel):
    id: str
    name: str
    cuisine: str
    dietary_tags: List[str]
    fitness_goals: List[str]
    calories_per_serving: int
    protein_grams: int
    carbs_grams: int
    fat_grams: int
    ingredients: List[str]


class MealPlanDayOut(BaseModel):
    day: str
    meals: List[RecipeOut]


class PlanRequest(BaseModel):
    dietary_tags: Optional[List[str]] = None
    cuisine: Optional[str] = None
    fitness_goals: Optional[List[str]] = None
    meals_per_day: int = 3


class RecipesResponse(BaseModel):
    total: int
    recipes: List[RecipeOut]


def create_app() -> FastAPI:
    app = FastAPI(title="Meal Planner")

    @app.get("/recipes", response_model=RecipesResponse)
    def list_recipes(
        dietary_tags: Optional[List[str]] = None,
        cuisine: Optional[str] = None,
        fitness_goals: Optional[List[str]] = None,
    ) -> RecipesResponse:
        recipes = filter_recipes(
            dietary_tags=dietary_tags, cuisine=cuisine, fitness_goals=fitness_goals
        )
        return RecipesResponse(total=len(recipes), recipes=recipes)

    @app.post("/meal-plans/weekly", response_model=List[MealPlanDayOut])
    def create_weekly_plan(request: PlanRequest) -> List[MealPlanDayOut]:
        return generate_weekly_meal_plan(
            dietary_tags=request.dietary_tags,
            cuisine=request.cuisine,
            fitness_goals=request.fitness_goals,
            meals_per_day=request.meals_per_day,
        )

    return app


app = create_app()
