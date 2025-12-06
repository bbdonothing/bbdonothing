import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from mealplanner import PantryInventory, Recipe, RecipeIngredient, SubstitutionEngine  # noqa: E402


def test_suggest_substitutions_prefers_category_and_flavor():
    pantry = PantryInventory()
    pantry.add_item("Almond Milk", 2, "cup", category="plant milk", flavors={"nutty", "sweet"})
    pantry.add_item("Olive Oil", 1, "tbsp", category="fat", flavors={"fruity", "rich"})
    pantry.add_item("Yogurt", 1, "cup", category="dairy", flavors={"creamy", "tangy"})

    engine = SubstitutionEngine(pantry)
    suggestions = engine.suggest_substitutions("milk", max_results=3, min_score=1.0)

    assert len(suggestions) >= 2
    assert suggestions[0].score >= suggestions[1].score
    assert suggestions[0].substitute_name.lower() in {"almond milk", "yogurt"}
    assert any("category" in suggestion.reason for suggestion in suggestions)


def test_apply_to_recipe_consumes_inventory_and_updates_grocery_list():
    pantry = PantryInventory()
    pantry.add_item("Olive Oil", 5, "tbsp", category="fat", flavors={"rich", "fruity"})
    pantry.add_item("Tofu", 3, "piece", category="protein", flavors={"neutral", "soft"})

    recipe = Recipe(
        name="Herby Chicken",
        ingredients=[
            RecipeIngredient("Butter", 2, "tbsp"),
            RecipeIngredient("Chicken Breast", 2, "piece"),
            RecipeIngredient("Basil", 1, "bunch"),
        ],
    )

    engine = SubstitutionEngine(pantry)
    updated_recipe, grocery_list, applied = engine.apply_to_recipe(recipe, min_score=1.0)

    updated_names = {ingredient.name.lower() for ingredient in updated_recipe.ingredients}

    assert "olive oil" in updated_names
    assert "tofu" in updated_names
    assert any(entry.original_name.lower() == "butter" for entry in applied)
    assert any(entry.original_name.lower() == "chicken breast" for entry in applied)
    assert any(item.name.lower() == "basil" for item in grocery_list)

    pantry_items_after = pantry.normalized_items()
    assert pytest.approx(pantry_items_after["olive oil"].quantity) == 3
    assert pytest.approx(pantry_items_after["tofu"].quantity) == 1
