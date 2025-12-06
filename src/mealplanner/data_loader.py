import json
from functools import lru_cache
from pathlib import Path
from typing import List

from .models import Recipe


def _data_path() -> Path:
    return Path(__file__).resolve().parent / "data" / "recipes.json"


@lru_cache(maxsize=1)
def load_recipes() -> List[Recipe]:
    path = _data_path()
    with path.open("r", encoding="utf-8") as fh:
        raw_recipes = json.load(fh)

    recipes = [
        Recipe(
            id=item["id"],
            name=item["name"],
            cuisine=item["cuisine"],
            dietary_tags=item.get("dietary_tags", []),
            fitness_goals=item.get("fitness_goals", []),
            calories_per_serving=item.get("calories_per_serving", 0),
            protein_grams=item.get("protein_grams", 0),
            carbs_grams=item.get("carbs_grams", 0),
            fat_grams=item.get("fat_grams", 0),
            ingredients=item.get("ingredients", []),
        )
        for item in raw_recipes
    ]
    return recipes
