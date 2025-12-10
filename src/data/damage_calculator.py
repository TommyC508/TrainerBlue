"""Damage calculator for Pokemon battles."""
import random
from typing import Tuple, List, Optional
from .models import Pokemon, Move
from .type_effectiveness import get_type_effectiveness, get_stab_multiplier


class DamageRange:
    """Represents a range of possible damage values."""
    
    def __init__(self, min_damage: int, max_damage: int):
        self.min = min_damage
        self.max = max_damage
    
    @property
    def average(self) -> float:
        """Get average damage."""
        return (self.min + self.max) / 2
    
    def rolls_to_ko(self, hp: int) -> Tuple[int, int]:
        """
        Calculate number of hits to KO.
        
        Returns:
            (min_hits, max_hits) where min_hits uses max damage, max_hits uses min damage
        """
        if self.max == 0:
            return (999, 999)
        
        min_hits = (hp + self.max - 1) // self.max  # Ceiling division
        max_hits = (hp + self.min - 1) // self.min if self.min > 0 else 999
        
        return (min_hits, max_hits)
    
    def guarantees_ko(self, hp: int) -> bool:
        """Check if minimum damage guarantees KO."""
        return self.min >= hp
    
    def __repr__(self) -> str:
        return f"DamageRange({self.min}-{self.max}, avg={self.average:.1f})"


class DamageCalculator:
    """Calculate damage for Pokemon moves."""
    
    @staticmethod
    def calculate_damage(
        attacker: Pokemon,
        defender: Pokemon,
        move: Move,
        weather: str = "",
        terrain: str = "",
        is_critical: bool = False,
        user_types: Optional[List[str]] = None,
        target_types: Optional[List[str]] = None,
    ) -> DamageRange:
        """
        Calculate damage range for a move.
        
        Implements the Gen 9 damage formula:
        Damage = ((2 * Level / 5 + 2) * Power * A / D / 50 + 2) * Modifiers
        
        Args:
            attacker: Attacking Pokemon
            defender: Defending Pokemon
            move: Move being used
            weather: Current weather
            terrain: Current terrain
            is_critical: Whether it's a critical hit
            user_types: Attacker's types (for STAB)
            target_types: Defender's types (for effectiveness)
            
        Returns:
            DamageRange with min and max damage
        """
        # Status moves deal no damage
        if move.category == "Status" or move.power is None or move.power == 0:
            return DamageRange(0, 0)
        
        level = attacker.level
        power = move.power
        
        # Get attack and defense stats
        if move.category == "Physical":
            attack_stat = attacker.stats.get("atk", 100)
            defense_stat = defender.stats.get("def", 100)
            attack_boost = attacker.boosts.get("atk", 0)
            defense_boost = defender.boosts.get("def", 0)
        else:  # Special
            attack_stat = attacker.stats.get("spa", 100)
            defense_stat = defender.stats.get("spd", 100)
            attack_boost = attacker.boosts.get("spa", 0)
            defense_boost = defender.boosts.get("spd", 0)
        
        # Apply stat boosts
        attack_multiplier = DamageCalculator._get_boost_multiplier(attack_boost)
        defense_multiplier = DamageCalculator._get_boost_multiplier(defense_boost)
        
        # Critical hits ignore positive defense boosts and negative attack boosts
        if is_critical:
            if attack_boost < 0:
                attack_multiplier = 1.0
            if defense_boost > 0:
                defense_multiplier = 1.0
        
        attack = attack_stat * attack_multiplier
        defense = defense_stat * defense_multiplier
        
        # Base damage calculation
        base_damage = ((2 * level / 5 + 2) * power * attack / defense / 50 + 2)
        
        # Modifiers
        modifier = 1.0
        
        # STAB (Same-Type Attack Bonus)
        if user_types:
            modifier *= get_stab_multiplier(move.type, user_types)
        
        # Type effectiveness
        if target_types:
            modifier *= get_type_effectiveness(move.type, target_types)
        
        # Critical hit
        if is_critical:
            modifier *= 1.5
        
        # Weather effects (simplified)
        if weather == "sunnyday" and move.type == "Fire":
            modifier *= 1.5
        elif weather == "sunnyday" and move.type == "Water":
            modifier *= 0.5
        elif weather == "raindance" and move.type == "Water":
            modifier *= 1.5
        elif weather == "raindance" and move.type == "Fire":
            modifier *= 0.5
        
        # Burn reduces physical damage
        if attacker.status == "brn" and move.category == "Physical":
            modifier *= 0.5
        
        # Random factor: 0.85 to 1.0
        min_damage = int(base_damage * modifier * 0.85)
        max_damage = int(base_damage * modifier * 1.0)
        
        # Ensure at least 1 damage if move hits
        if min_damage == 0 and modifier > 0:
            min_damage = 1
        if max_damage == 0 and modifier > 0:
            max_damage = 1
        
        return DamageRange(min_damage, max_damage)
    
    @staticmethod
    def _get_boost_multiplier(boost: int) -> float:
        """
        Convert stat boost stage to multiplier.
        
        Boost ranges from -6 to +6.
        Formula: (2 + max(0, boost)) / (2 + max(0, -boost))
        """
        if boost >= 0:
            return (2 + boost) / 2
        else:
            return 2 / (2 - boost)
    
    @staticmethod
    def calculate_speed_order(
        pokemon_a: Pokemon,
        pokemon_b: Pokemon,
        trick_room: bool = False
    ) -> bool:
        """
        Determine if pokemon_a moves before pokemon_b.
        
        Args:
            pokemon_a: First Pokemon
            pokemon_b: Second Pokemon
            trick_room: Whether Trick Room is active
            
        Returns:
            True if pokemon_a moves first, False otherwise
        """
        # Get speed stats
        speed_a = pokemon_a.stats.get("spe", 100)
        speed_b = pokemon_b.stats.get("spe", 100)
        
        # Apply boosts
        boost_a = pokemon_a.boosts.get("spe", 0)
        boost_b = pokemon_b.boosts.get("spe", 0)
        
        speed_a *= DamageCalculator._get_boost_multiplier(boost_a)
        speed_b *= DamageCalculator._get_boost_multiplier(boost_b)
        
        # Paralysis halves speed (simplified)
        if pokemon_a.status == "par":
            speed_a *= 0.5
        if pokemon_b.status == "par":
            speed_b *= 0.5
        
        # Trick Room reverses speed order
        if trick_room:
            return speed_a < speed_b
        else:
            return speed_a > speed_b
