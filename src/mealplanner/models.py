from dataclasses import dataclass, field
from typing import List


@dataclass
class Recipe:
    id: str
    name: str
    cuisine: str
    dietary_tags: List[str]
    fitness_goals: List[str]
    calories_per_serving: int
    protein_grams: int
    carbs_grams: int
    fat_grams: int
    ingredients: List[str] = field(default_factory=list)


@dataclass
class MealPlanDay:
    day: str
    meals: List[Recipe]
