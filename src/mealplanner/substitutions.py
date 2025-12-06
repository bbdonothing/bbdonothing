from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Dict, Iterable, List, Optional, Set, Tuple

from .models import IngredientProfile, PantryInventory, Recipe, RecipeIngredient, _normalize_name


@dataclass(frozen=True)
class SubstitutionSuggestion:
    substitute_name: str
    score: float
    reason: str
    available_quantity: float


@dataclass(frozen=True)
class AppliedSubstitution:
    original_name: str
    substitute_name: str
    quantity: float
    unit: str
    score: float


_DEFAULT_INGREDIENTS: Iterable[IngredientProfile] = [
    IngredientProfile("milk", "dairy", {"creamy", "sweet"}),
    IngredientProfile("yogurt", "dairy", {"tangy", "creamy"}),
    IngredientProfile("cream", "dairy", {"creamy", "rich"}),
    IngredientProfile("almond milk", "plant milk", {"nutty", "sweet"}),
    IngredientProfile("oat milk", "plant milk", {"sweet", "creamy"}),
    IngredientProfile("butter", "fat", {"creamy", "rich"}),
    IngredientProfile("olive oil", "fat", {"fruity", "peppery", "rich"}),
    IngredientProfile("canola oil", "fat", {"neutral"}),
    IngredientProfile("vegetable oil", "fat", {"neutral"}),
    IngredientProfile("coconut oil", "fat", {"sweet", "tropical"}),
    IngredientProfile("chicken breast", "protein", {"savory", "lean"}),
    IngredientProfile("tofu", "protein", {"neutral", "soft"}),
    IngredientProfile("tempeh", "protein", {"nutty", "savory"}),
    IngredientProfile("chickpeas", "protein", {"earthy", "nutty"}),
    IngredientProfile("beef", "protein", {"rich", "savory"}),
    IngredientProfile("pork", "protein", {"savory", "rich"}),
    IngredientProfile("lemon", "acid", {"citrus", "bright"}),
    IngredientProfile("lime", "acid", {"citrus", "bright"}),
    IngredientProfile("rice vinegar", "acid", {"bright", "mild"}),
    IngredientProfile("apple cider vinegar", "acid", {"fruity", "bright"}),
    IngredientProfile("white sugar", "sweetener", {"sweet"}),
    IngredientProfile("brown sugar", "sweetener", {"sweet", "molasses"}),
    IngredientProfile("honey", "sweetener", {"sweet", "floral"}),
    IngredientProfile("maple syrup", "sweetener", {"sweet", "caramel"}),
    IngredientProfile("soy sauce", "umami", {"salty", "savory"}),
    IngredientProfile("tamari", "umami", {"salty", "savory"}),
    IngredientProfile("coconut aminos", "umami", {"salty", "sweet"}),
    IngredientProfile("basil", "herb", {"sweet", "fresh"}),
    IngredientProfile("oregano", "herb", {"earthy", "bitter"}),
    IngredientProfile("thyme", "herb", {"earthy", "fresh"}),
    IngredientProfile("cilantro", "herb", {"fresh", "citrus"}),
    IngredientProfile("parsley", "herb", {"fresh", "bitter"}),
    IngredientProfile("garlic", "aromatic", {"pungent", "sweet"}),
    IngredientProfile("onion", "aromatic", {"sweet", "savory"}),
    IngredientProfile("shallot", "aromatic", {"sweet", "delicate"}),
    IngredientProfile("scallion", "aromatic", {"fresh", "sweet"}),
    IngredientProfile("parmesan cheese", "cheese", {"nutty", "salty"}),
    IngredientProfile("cheddar", "cheese", {"sharp", "salty"}),
    IngredientProfile("mozzarella", "cheese", {"mild", "creamy"}),
    IngredientProfile("ricotta", "cheese", {"creamy", "sweet"}),
    IngredientProfile("tomato", "vegetable", {"acidic", "sweet"}),
    IngredientProfile("bell pepper", "vegetable", {"sweet", "fresh"}),
    IngredientProfile("carrot", "vegetable", {"sweet", "earthy"}),
    IngredientProfile("celery", "vegetable", {"bitter", "fresh"}),
]

_DEFAULT_LIBRARY: Dict[str, IngredientProfile] = {
    profile.normalized_name: profile for profile in _DEFAULT_INGREDIENTS
}


class SubstitutionEngine:
    def __init__(
        self,
        pantry: PantryInventory,
        knowledge_base: Optional[Dict[str, IngredientProfile]] = None,
    ) -> None:
        self.pantry = pantry
        base = knowledge_base or _DEFAULT_LIBRARY
        self.knowledge_base: Dict[str, IngredientProfile] = {
            _normalize_name(name): profile for name, profile in base.items()
        }

    def suggest_substitutions(
        self, target_name: str, max_results: int = 5, min_score: float = 0.0
    ) -> List[SubstitutionSuggestion]:
        target_profile = self._profile_for(target_name)
        suggestions: List[SubstitutionSuggestion] = []

        for item in self.pantry.items():
            candidate_profile = self._profile_for(
                item.name, category=item.category, flavors=item.flavors
            )
            score = self._similarity(target_profile, candidate_profile)
            if item.name.lower() == target_name.lower() and item.quantity > 0:
                reason = "Ingredient already available"
                suggestions.append(
                    SubstitutionSuggestion(
                        substitute_name=item.name,
                        score=score + 2.0,
                        reason=reason,
                        available_quantity=item.quantity,
                    )
                )
                continue

            if score < min_score or item.quantity <= 0:
                continue

            reason = self._reason_for(target_profile, candidate_profile)
            suggestions.append(
                SubstitutionSuggestion(
                    substitute_name=item.name,
                    score=score,
                    reason=reason,
                    available_quantity=item.quantity,
                )
            )

        suggestions.sort(key=lambda suggestion: suggestion.score, reverse=True)
        return suggestions[:max_results]

    def apply_to_recipe(
        self, recipe: Recipe, min_score: float = 1.0
    ) -> Tuple[Recipe, List[RecipeIngredient], List[AppliedSubstitution]]:
        updated_ingredients: List[RecipeIngredient] = []
        grocery_list: List[RecipeIngredient] = []
        applied: List[AppliedSubstitution] = []

        for ingredient in recipe.ingredients:
            required_quantity = ingredient.quantity
            unit = ingredient.unit

            if self.pantry.has_enough(ingredient.name, required_quantity):
                self.pantry.consume(ingredient.name, required_quantity)
                updated_ingredients.append(ingredient)
                continue

            available_quantity = self.pantry.available_quantity(ingredient.name)
            if available_quantity > 0:
                use_quantity = min(available_quantity, required_quantity)
                self.pantry.consume(ingredient.name, use_quantity)
                updated_ingredients.append(
                    RecipeIngredient(
                        name=ingredient.name,
                        quantity=use_quantity,
                        unit=unit,
                        note="used from pantry",
                    )
                )
                required_quantity -= use_quantity

            if required_quantity <= 0:
                continue

            candidates = [
                suggestion
                for suggestion in self.suggest_substitutions(
                    ingredient.name, max_results=3, min_score=min_score
                )
                if self.pantry.has_enough(suggestion.substitute_name, required_quantity)
            ]

            if candidates:
                chosen = candidates[0]
                self.pantry.consume(chosen.substitute_name, required_quantity)
                updated_ingredients.append(
                    RecipeIngredient(
                        name=chosen.substitute_name,
                        quantity=required_quantity,
                        unit=unit,
                        note=f"substitute for {ingredient.name}",
                    )
                )
                applied.append(
                    AppliedSubstitution(
                        original_name=ingredient.name,
                        substitute_name=chosen.substitute_name,
                        quantity=required_quantity,
                        unit=unit,
                        score=chosen.score,
                    )
                )
            else:
                grocery_list.append(
                    RecipeIngredient(
                        name=ingredient.name,
                        quantity=required_quantity,
                        unit=unit,
                        note="add to grocery list",
                    )
                )

        return recipe.clone_with_ingredients(updated_ingredients), grocery_list, applied

    def _profile_for(
        self, name: str, category: Optional[str] = None, flavors: Optional[Set[str]] = None
    ) -> IngredientProfile:
        normalized_name = _normalize_name(name)
        if normalized_name in self.knowledge_base:
            base = self.knowledge_base[normalized_name]
            category = category or base.category
            merged_flavors = set(base.flavors)
            if flavors:
                merged_flavors.update(flavor.lower() for flavor in flavors)
            return IngredientProfile(name=name, category=category, flavors=merged_flavors)

        return IngredientProfile(
            name=name,
            category=category or "unknown",
            flavors={flavor.lower() for flavor in (flavors or set())} or set(normalized_name.split()),
        )

    def _similarity(self, target: IngredientProfile, candidate: IngredientProfile) -> float:
        score = 0.0
        if target.category and candidate.category and target.category == candidate.category:
            score += 3.0
        shared_flavors = target.flavors.intersection(candidate.flavors)
        score += len(shared_flavors)
        score += SequenceMatcher(None, target.normalized_name, candidate.normalized_name).ratio()
        return score

    def _reason_for(self, target: IngredientProfile, candidate: IngredientProfile) -> str:
        reasons: List[str] = []
        if target.category == candidate.category and target.category:
            reasons.append(f"same category ({target.category})")
        flavor_overlap = target.flavors.intersection(candidate.flavors)
        if flavor_overlap:
            reasons.append(f"shared flavors: {', '.join(sorted(flavor_overlap))}")
        if not reasons:
            reasons.append("closest name match")
        return "; ".join(reasons)
