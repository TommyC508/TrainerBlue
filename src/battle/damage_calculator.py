"""
Pokemon damage calculator based on Pokemon Showdown's battle engine.
Reference: https://github.com/smogon/pokemon-showdown
"""
import random
import math
from typing import Dict, List, Optional, Tuple
from ..data.type_effectiveness import get_type_effectiveness


class DamageCalculator:
    """Accurate Pokemon damage calculation following PS mechanics."""
    
    def __init__(self, gen: int = 9):
        """
        Initialize damage calculator.
        
        Args:
            gen: Pokemon generation (affects damage calculation details)
        """
        self.gen = gen
    
    @staticmethod
    def trunc(value: float, bits: int = 32) -> int:
        """
        Truncate to integer, simulating Pokemon Showdown's truncation.
        
        Args:
            value: Float value to truncate
            bits: Bit width for truncation (16 or 32)
        """
        if bits == 16:
            # 16-bit truncation (0-65535)
            return int(value) & 0xFFFF
        return int(value)
    
    @staticmethod
    def clamp_int_range(value: int, min_val: int = 1, max_val: Optional[int] = None) -> int:
        """Clamp value to integer range."""
        if max_val is None:
            max_val = 2**31 - 1
        return max(min_val, min(max_val, value))
    
    def get_base_damage(
        self,
        level: int,
        base_power: int,
        attack: int,
        defense: int
    ) -> int:
        """
        Calculate base damage using Pokemon Showdown's formula.
        
        Formula: floor(floor(floor(floor(2 * L / 5 + 2) * P * A) / D) / 50)
        
        Args:
            level: Attacker's level
            base_power: Move's base power
            attack: Attacker's attack/sp.attack stat
            defense: Defender's defense/sp.defense stat
        
        Returns:
            Base damage before modifiers
        """
        tr = self.trunc
        
        # int(int(int(2 * L / 5 + 2) * A * P / D) / 50)
        base_damage = tr(tr(tr(tr(2 * level / 5 + 2) * base_power * attack) / defense) / 50)
        
        return base_damage
    
    def apply_modifiers(
        self,
        base_damage: int,
        attacker_types: List[str],
        defender_types: List[str],
        move_type: str,
        is_critical: bool = False,
        weather: Optional[str] = None,
        attacker_status: Optional[str] = None,
        move_category: str = "Physical"
    ) -> int:
        """
        Apply damage modifiers in the correct order (Gen 5+).
        
        Order:
        1. Spread modifier (doubles/triples) - not applicable in singles
        2. Weather modifier
        3. Critical hit
        4. Random factor (85-100%)
        5. STAB (1.5x if attacker has move's type)
        6. Type effectiveness (0x, 0.25x, 0.5x, 2x, 4x)
        7. Burn modifier (0.5x for physical moves if burned)
        8. Final modifier (items like Life Orb)
        
        Args:
            base_damage: Base damage before modifiers
            attacker_types: Attacker's types
            defender_types: Defender's types
            move_type: Move's type
            is_critical: Whether this is a critical hit
            weather: Active weather condition
            attacker_status: Attacker's status (brn, par, etc.)
            move_category: Physical or Special
        
        Returns:
            Final damage
        """
        tr = self.trunc
        damage = base_damage
        
        # Add base +2 before most modifiers
        damage += 2
        
        # 1. Spread modifier - skip (singles only)
        
        # 2. Weather modifier
        if weather:
            if weather == "sun" and move_type == "Fire":
                damage = tr(damage * 1.5)
            elif weather == "sun" and move_type == "Water":
                damage = tr(damage * 0.5)
            elif weather == "rain" and move_type == "Water":
                damage = tr(damage * 1.5)
            elif weather == "rain" and move_type == "Fire":
                damage = tr(damage * 0.5)
        
        # 3. Critical hit (1.5x in Gen 6+, 2x before)
        if is_critical:
            crit_modifier = 1.5 if self.gen >= 6 else 2.0
            damage = tr(damage * crit_modifier)
        
        # 4. Random factor (85-100%, i.e. multiply by random(85, 100) / 100)
        random_factor = random.randint(85, 100) / 100
        damage = tr(damage * random_factor)
        
        # 5. STAB (Same Type Attack Bonus)
        if move_type in attacker_types and move_type != "???":
            damage = tr(damage * 1.5)
        
        # 6. Type effectiveness
        total_effectiveness = 1.0
        for def_type in defender_types:
            effectiveness = get_type_effectiveness(move_type, def_type)
            total_effectiveness *= effectiveness
        
        # Apply type effectiveness as multipliers
        if total_effectiveness >= 2:
            # Super effective
            multiplier_count = int(math.log2(total_effectiveness))
            for _ in range(multiplier_count):
                damage *= 2
        elif total_effectiveness <= 0.5:
            # Not very effective
            if total_effectiveness == 0:
                return 0  # Immune
            multiplier_count = int(-math.log2(total_effectiveness))
            for _ in range(multiplier_count):
                damage = tr(damage / 2)
        
        # 7. Burn modifier (halves physical damage if burned)
        if attacker_status == "brn" and move_category == "Physical":
            damage = tr(damage * 0.5)
        
        # 8. Final modifier (items, abilities) - not implemented yet
        
        # Minimum 1 damage (unless immune)
        if self.gen != 5 and damage == 0:
            damage = 1
        
        # 16-bit truncation
        damage = self.trunc(damage, 16)
        
        return max(1, damage)
    
    def calculate_damage(
        self,
        attacker_level: int,
        attacker_types: List[str],
        attacker_attack: int,
        attacker_status: Optional[str],
        defender_types: List[str],
        defender_defense: int,
        move_base_power: int,
        move_type: str,
        move_category: str = "Physical",
        is_critical: bool = False,
        weather: Optional[str] = None
    ) -> Tuple[int, float]:
        """
        Calculate total damage for a move.
        
        Args:
            attacker_level: Attacker's level
            attacker_types: Attacker's types
            attacker_attack: Attacker's attack or sp.attack stat
            attacker_status: Attacker's status condition
            defender_types: Defender's types
            defender_defense: Defender's defense or sp.defense stat
            move_base_power: Move's base power
            move_type: Move's type
            move_category: Physical or Special
            is_critical: Whether this is a critical hit
            weather: Active weather condition
        
        Returns:
            Tuple of (damage, type_effectiveness)
        """
        # Calculate type effectiveness
        total_effectiveness = 1.0
        for def_type in defender_types:
            effectiveness = get_type_effectiveness(move_type, def_type)
            total_effectiveness *= effectiveness
        
        # Immune check
        if total_effectiveness == 0:
            return 0, 0.0
        
        # Calculate base damage
        base_damage = self.get_base_damage(
            attacker_level,
            move_base_power,
            attacker_attack,
            defender_defense
        )
        
        # Apply all modifiers
        final_damage = self.apply_modifiers(
            base_damage,
            attacker_types,
            defender_types,
            move_type,
            is_critical,
            weather,
            attacker_status,
            move_category
        )
        
        return final_damage, total_effectiveness


def calculate_stat(base_stat: int, level: int, iv: int = 31, ev: int = 0, nature_modifier: float = 1.0) -> int:
    """
    Calculate actual stat value from base stat.
    
    Formula for HP:
        floor(((2 * base + IV + floor(EV / 4)) * level) / 100) + level + 10
    
    Formula for other stats:
        floor((floor(((2 * base + IV + floor(EV / 4)) * level) / 100) + 5) * nature)
    
    Args:
        base_stat: Base stat value
        level: Pokemon level
        iv: Individual Value (0-31)
        ev: Effort Value (0-252)
        nature_modifier: Nature modifier (0.9, 1.0, or 1.1)
    
    Returns:
        Actual stat value
    """
    stat = math.floor(((2 * base_stat + iv + math.floor(ev / 4)) * level) / 100) + 5
    stat = math.floor(stat * nature_modifier)
    return max(1, stat)


def calculate_hp(base_hp: int, level: int, iv: int = 31, ev: int = 0) -> int:
    """Calculate HP stat."""
    hp = math.floor(((2 * base_hp + iv + math.floor(ev / 4)) * level) / 100) + level + 10
    return max(1, hp)
