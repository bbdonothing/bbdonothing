from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Set


def _normalize_name(name: str) -> str:
    return name.strip().lower()


@dataclass(frozen=True)
class IngredientProfile:
    name: str
    category: str
    flavors: Set[str] = field(default_factory=set)

    @property
    def normalized_name(self) -> str:
        return _normalize_name(self.name)


@dataclass
class PantryItem:
    name: str
    quantity: float
    unit: str
    category: Optional[str] = None
    flavors: Set[str] = field(default_factory=set)

    def normalized_name(self) -> str:
        return _normalize_name(self.name)


@dataclass
class RecipeIngredient:
    name: str
    quantity: float
    unit: str
    note: Optional[str] = None

    def normalized_name(self) -> str:
        return _normalize_name(self.name)


@dataclass
class Recipe:
    name: str
    ingredients: List[RecipeIngredient]

    def clone_with_ingredients(self, new_ingredients: Iterable[RecipeIngredient]) -> "Recipe":
        return Recipe(name=self.name, ingredients=list(new_ingredients))


class PantryInventory:
    def __init__(self, items: Optional[Iterable[PantryItem]] = None) -> None:
        self._items: Dict[str, PantryItem] = {}
        if items:
            for item in items:
                self.add_item(item.name, item.quantity, item.unit, item.category, item.flavors)

    def add_item(
        self,
        name: str,
        quantity: float,
        unit: str,
        category: Optional[str] = None,
        flavors: Optional[Set[str]] = None,
    ) -> None:
        normalized_name = _normalize_name(name)
        existing = self._items.get(normalized_name)
        if existing:
            if existing.unit != unit:
                raise ValueError(f"Unit mismatch for {name!r}: {existing.unit} vs {unit}")
            existing.quantity += quantity
        else:
            self._items[normalized_name] = PantryItem(
                name=name,
                quantity=quantity,
                unit=unit,
                category=category,
                flavors=flavors or set(),
            )

    def available_quantity(self, name: str) -> float:
        normalized_name = _normalize_name(name)
        item = self._items.get(normalized_name)
        return item.quantity if item else 0.0

    def has_enough(self, name: str, quantity: float) -> bool:
        return self.available_quantity(name) >= quantity

    def consume(self, name: str, quantity: float) -> None:
        normalized_name = _normalize_name(name)
        item = self._items.get(normalized_name)
        if not item:
            raise ValueError(f"Ingredient {name} not found in pantry")
        if item.quantity < quantity:
            raise ValueError(
                f"Not enough {name} available (needed {quantity} {item.unit}, have {item.quantity})"
            )
        item.quantity -= quantity

    def items(self) -> List[PantryItem]:
        return list(self._items.values())

    def normalized_items(self) -> Dict[str, PantryItem]:
        return dict(self._items)
