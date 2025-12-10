"""Type effectiveness chart and calculations."""
from typing import Dict, List

# Type effectiveness chart (based on official Pokemon type chart)
# 2.0 = super effective, 1.0 = normal, 0.5 = not very effective, 0.0 = immune
TYPE_CHART: Dict[str, Dict[str, float]] = {
    "Normal": {
        "Rock": 0.5, "Ghost": 0.0, "Steel": 0.5
    },
    "Fire": {
        "Fire": 0.5, "Water": 0.5, "Grass": 2.0, "Ice": 2.0, "Bug": 2.0, "Rock": 0.5, "Dragon": 0.5, "Steel": 2.0
    },
    "Water": {
        "Fire": 2.0, "Water": 0.5, "Grass": 0.5, "Ground": 2.0, "Rock": 2.0, "Dragon": 0.5
    },
    "Grass": {
        "Fire": 0.5, "Water": 2.0, "Grass": 0.5, "Poison": 0.5, "Ground": 2.0, "Flying": 0.5, "Bug": 0.5, "Rock": 2.0, "Dragon": 0.5, "Steel": 0.5
    },
    "Electric": {
        "Water": 2.0, "Electric": 0.5, "Grass": 0.5, "Ground": 0.0, "Flying": 2.0, "Dragon": 0.5
    },
    "Ice": {
        "Fire": 0.5, "Water": 0.5, "Grass": 2.0, "Ice": 0.5, "Ground": 2.0, "Flying": 2.0, "Dragon": 2.0, "Steel": 0.5
    },
    "Fighting": {
        "Normal": 2.0, "Ice": 2.0, "Poison": 0.5, "Flying": 0.5, "Psychic": 0.5, "Bug": 0.5, "Rock": 2.0, "Ghost": 0.0, "Dark": 2.0, "Steel": 2.0, "Fairy": 0.5
    },
    "Poison": {
        "Grass": 2.0, "Poison": 0.5, "Ground": 0.5, "Rock": 0.5, "Ghost": 0.5, "Steel": 0.0, "Fairy": 2.0
    },
    "Ground": {
        "Fire": 2.0, "Electric": 2.0, "Grass": 0.5, "Poison": 2.0, "Flying": 0.0, "Bug": 0.5, "Rock": 2.0, "Steel": 2.0
    },
    "Flying": {
        "Electric": 0.5, "Grass": 2.0, "Fighting": 2.0, "Bug": 2.0, "Rock": 0.5, "Steel": 0.5
    },
    "Psychic": {
        "Fighting": 2.0, "Poison": 2.0, "Psychic": 0.5, "Dark": 0.0, "Steel": 0.5
    },
    "Bug": {
        "Fire": 0.5, "Grass": 2.0, "Fighting": 0.5, "Poison": 0.5, "Flying": 0.5, "Psychic": 2.0, "Ghost": 0.5, "Rock": 0.5, "Dark": 2.0, "Steel": 0.5, "Fairy": 0.5
    },
    "Rock": {
        "Fire": 2.0, "Ice": 2.0, "Fighting": 0.5, "Ground": 0.5, "Flying": 2.0, "Bug": 2.0, "Steel": 0.5
    },
    "Ghost": {
        "Normal": 0.0, "Psychic": 2.0, "Ghost": 2.0, "Dark": 0.5
    },
    "Dragon": {
        "Dragon": 2.0, "Steel": 0.5, "Fairy": 0.0
    },
    "Dark": {
        "Fighting": 0.5, "Psychic": 2.0, "Ghost": 2.0, "Dark": 0.5, "Fairy": 0.5
    },
    "Steel": {
        "Fire": 0.5, "Water": 0.5, "Electric": 0.5, "Ice": 2.0, "Rock": 2.0, "Steel": 0.5, "Fairy": 2.0
    },
    "Fairy": {
        "Fire": 0.5, "Fighting": 2.0, "Poison": 0.5, "Dragon": 2.0, "Dark": 2.0, "Steel": 0.5
    },
}


def get_type_effectiveness(move_type: str, target_types: List[str]) -> float:
    """
    Calculate type effectiveness multiplier.
    
    Args:
        move_type: Type of the attacking move
        target_types: List of target's types (1 or 2)
        
    Returns:
        Effectiveness multiplier (e.g., 4.0 for double super effective, 0.25 for double resisted)
    """
    multiplier = 1.0
    
    if move_type not in TYPE_CHART:
        return multiplier
    
    effectiveness_chart = TYPE_CHART[move_type]
    
    for target_type in target_types:
        if target_type in effectiveness_chart:
            multiplier *= effectiveness_chart[target_type]
    
    return multiplier


def is_super_effective(move_type: str, target_types: List[str]) -> bool:
    """Check if move is super effective."""
    return get_type_effectiveness(move_type, target_types) > 1.0


def is_not_very_effective(move_type: str, target_types: List[str]) -> bool:
    """Check if move is not very effective."""
    effectiveness = get_type_effectiveness(move_type, target_types)
    return 0.0 < effectiveness < 1.0


def is_immune(move_type: str, target_types: List[str]) -> bool:
    """Check if target is immune to move."""
    return get_type_effectiveness(move_type, target_types) == 0.0


def get_stab_multiplier(move_type: str, user_types: List[str]) -> float:
    """
    Get Same-Type Attack Bonus (STAB) multiplier.
    
    Args:
        move_type: Type of the move
        user_types: List of user's types
        
    Returns:
        1.5 if STAB applies, 1.0 otherwise
    """
    if move_type in user_types:
        return 1.5
    return 1.0
