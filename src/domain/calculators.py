# Importamos o tipo apenas para referência de tipo (type hinting)
from src.storage.models import BeerRecipe

class BrewMath:
    @staticmethod
    def estimate_abv(og: float, fg: float) -> float:
        return round((og - fg) * 131.25, 2)

    @staticmethod
    def is_plausible(recipe: BeerRecipe) -> bool:
        # Valida se o ABV informado bate com o cálculo das densidades
        calc = BrewMath.estimate_abv(recipe.target_og, recipe.target_fg)
        return abs(calc - recipe.abv) < 0.5