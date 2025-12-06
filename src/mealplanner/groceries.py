"""Grocery list aggregation for weekly meal planning.

This module provides simple in-memory data structures paired with a
file-backed service that can be used to aggregate ingredients across a
user's selected recipes. It merges quantities for identical ingredients
and recalculates the aggregate list any time the selected recipe set is
updated.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, MutableMapping, Optional
import json


@dataclass
class Ingredient:
    """A single recipe ingredient with a quantity and optional unit."""

    name: str
    quantity: float
    unit: Optional[str] = None

    def key(self) -> tuple[str, Optional[str]]:
        """Return a normalized key for merging ingredients.

        The merge key uses a lowercase ingredient name and unit to avoid
        duplicating items that only differ by casing.
        """

        normalized_name = self.name.strip().lower()
        normalized_unit = self.unit.strip().lower() if self.unit else None
        return (normalized_name, normalized_unit)

    def to_summary(self) -> str:
        """Return a human-friendly string representation of the ingredient."""

        unit_part = f" {self.unit}" if self.unit else ""
        return f"{self.quantity:g}{unit_part} {self.name}".strip()


@dataclass
class GroceryList:
    """Aggregated grocery list for a single user/session."""

    items: List[Ingredient]

    def as_strings(self) -> List[str]:
        """Return the grocery list as display-ready strings."""

        return [item.to_summary() for item in self.items]


class GroceryListService:
    """Service layer for persisting and aggregating grocery lists.

    The service stores data in a JSON file so it can be reused by multiple
    API calls or executions. Each user (or session) has an isolated set of
    selected recipes, and the grocery list is recalculated each time the
    set is modified.
    """

    def __init__(self, storage_path: Optional[Path] = None) -> None:
        self.storage_path = storage_path or Path("data/grocery_lists.json")
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage_path.exists():
            self.storage_path.write_text(json.dumps({}), encoding="utf-8")

    def add_recipe(
        self, user_id: str, recipe_id: str, ingredients: Iterable[Ingredient]
    ) -> GroceryList:
        """Persist a recipe selection and return the updated grocery list."""

        data = self._load()
        user_data = data.setdefault(user_id, {"recipes": {}})
        user_data["recipes"][recipe_id] = [asdict(ing) for ing in ingredients]
        user_data["grocery_list"] = self._calculate_grocery_list(user_data)
        data[user_id] = user_data
        self._save(data)
        return GroceryList(items=self._inflate(user_data["grocery_list"]))

    def remove_recipe(self, user_id: str, recipe_id: str) -> GroceryList:
        """Remove a recipe selection and return the updated grocery list."""

        data = self._load()
        user_data = data.get(user_id, {"recipes": {}})
        user_data["recipes"].pop(recipe_id, None)
        user_data["grocery_list"] = self._calculate_grocery_list(user_data)
        data[user_id] = user_data
        self._save(data)
        return GroceryList(items=self._inflate(user_data["grocery_list"]))

    def clear_user(self, user_id: str) -> None:
        """Remove all saved data for the provided user/session."""

        data = self._load()
        data.pop(user_id, None)
        self._save(data)

    def get_grocery_list(self, user_id: str) -> GroceryList:
        """Return the current grocery list for a user, recalculating if needed."""

        data = self._load()
        user_data = data.get(user_id)
        if not user_data:
            return GroceryList(items=[])

        user_data["grocery_list"] = self._calculate_grocery_list(user_data)
        data[user_id] = user_data
        self._save(data)
        return GroceryList(items=self._inflate(user_data["grocery_list"]))

    def _calculate_grocery_list(
        self, user_data: Mapping[str, MutableMapping[str, list]]
    ) -> List[Mapping[str, object]]:
        """Aggregate ingredients from stored recipes.

        The algorithm merges quantities for identical (name, unit) pairs.
        """

        aggregated: Dict[tuple[str, Optional[str]], Ingredient] = {}
        for ing_dict in self._iterate_ingredients(user_data.get("recipes", {})):
            ingredient = Ingredient(**ing_dict)
            key = ingredient.key()
            if key in aggregated:
                aggregated[key].quantity += ingredient.quantity
            else:
                aggregated[key] = Ingredient(
                    name=ingredient.name,
                    quantity=ingredient.quantity,
                    unit=ingredient.unit,
                )

        sorted_items = sorted(
            aggregated.values(), key=lambda ing: (ing.name.lower(), ing.unit or "")
        )
        return [asdict(item) for item in sorted_items]

    @staticmethod
    def _iterate_ingredients(recipes: Mapping[str, list]) -> Iterable[dict]:
        for ingredients in recipes.values():
            yield from ingredients

    def _load(self) -> Dict[str, dict]:
        content = self.storage_path.read_text(encoding="utf-8")
        return json.loads(content) if content else {}

    def _save(self, data: Mapping[str, object]) -> None:
        serialized = json.dumps(data, indent=2, ensure_ascii=False)
        self.storage_path.write_text(serialized, encoding="utf-8")

    @staticmethod
    def _inflate(payload: Iterable[Mapping[str, object]]) -> List[Ingredient]:
        """Convert stored dictionaries back into Ingredient objects."""

        return [Ingredient(**item) for item in payload]
