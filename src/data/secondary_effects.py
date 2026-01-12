"""Secondary effects system for Pokemon moves, matching Pokemon Showdown."""
import random
from typing import Optional, Dict, Any
from .models import Pokemon, Move


class SecondaryEffects:
    """Handle secondary effects from moves (status, stat changes, recoil, etc.)."""
    
    @staticmethod
    def apply_secondary_effects(
        move: Move,
        attacker: Pokemon,
        defender: Pokemon,
        damage_dealt: int
    ) -> Dict[str, Any]:
        """
        Apply secondary effects after a move hits.
        
        Returns dict with applied effects for logging/display.
        """
        effects_applied = {}
        
        if not move.secondary:
            return effects_applied
        
        secondary = move.secondary
        
        # Handle recoil damage
        if "recoil" in secondary:
            recoil_num, recoil_denom = secondary["recoil"]
            recoil_damage = max(1, int(damage_dealt * recoil_num / recoil_denom))
            attacker.hp = max(0, attacker.hp - recoil_damage)
            effects_applied["recoil"] = recoil_damage
        
        # Check if secondary effect triggers (based on chance)
        chance = secondary.get("chance", 100)
        if random.randint(1, 100) > chance:
            return effects_applied
        
        # Apply status condition to target
        if "status" in secondary and not defender.status:
            status = secondary["status"]
            # Check immunities
            if SecondaryEffects._can_apply_status(defender, status):
                defender.status = status
                effects_applied["status"] = status
        
        # Apply stat boosts/drops to target
        if "boosts" in secondary and "self" not in secondary:
            boosts = secondary["boosts"]
            for stat, change in boosts.items():
                current_boost = defender.boosts.get(stat, 0)
                new_boost = max(-6, min(6, current_boost + change))
                defender.boosts[stat] = new_boost
                effects_applied[f"boost_{stat}"] = change
        
        # Apply stat boosts to self
        if "self" in secondary and "boosts" in secondary.get("self", {}):
            boosts = secondary["self"]["boosts"]
            for stat, change in boosts.items():
                current_boost = attacker.boosts.get(stat, 0)
                new_boost = max(-6, min(6, current_boost + change))
                attacker.boosts[stat] = new_boost
                effects_applied[f"self_boost_{stat}"] = change
        
        # Volatile status (flinch, confusion, etc.)
        if "volatileStatus" in secondary:
            # Note: Flinch only works if the user moves first
            volatile = secondary["volatileStatus"]
            effects_applied["volatile"] = volatile
        
        return effects_applied
    
    @staticmethod
    def apply_self_effects(move: Move, attacker: Pokemon) -> Dict[str, Any]:
        """
        Apply effects that happen on move use (stat drops from Close Combat, boosts from Dragon Dance).
        
        Used for status moves and moves with guaranteed self-effects.
        """
        effects_applied = {}
        
        # Handle boost/stat-change moves (Dragon Dance, Swords Dance, etc.)
        if move.category == "Status" and move.secondary:
            if "boosts" in move.secondary:
                boosts = move.secondary["boosts"]
                for stat, change in boosts.items():
                    current_boost = attacker.boosts.get(stat, 0)
                    new_boost = max(-6, min(6, current_boost + change))
                    attacker.boosts[stat] = new_boost
                    effects_applied[f"boost_{stat}"] = change
        
        # Handle self-targeting effects from damaging moves (Close Combat)
        if move.secondary and "self" in move.secondary:
            self_effects = move.secondary["self"]
            if "boosts" in self_effects:
                boosts = self_effects["boosts"]
                for stat, change in boosts.items():
                    current_boost = attacker.boosts.get(stat, 0)
                    new_boost = max(-6, min(6, current_boost + change))
                    attacker.boosts[stat] = new_boost
                    effects_applied[f"self_boost_{stat}"] = change
        
        return effects_applied
    
    @staticmethod
    def _can_apply_status(pokemon: Pokemon, status: str) -> bool:
        """Check if a status can be applied to a Pokemon."""
        # Already has a status
        if pokemon.status:
            return False
        
        # Type immunities
        if status == "par":  # Paralysis
            if "Electric" in pokemon.types or "Ground" in pokemon.types:
                return False
        elif status == "brn":  # Burn
            if "Fire" in pokemon.types:
                return False
        elif status == "psn" or status == "tox":  # Poison
            if "Poison" in pokemon.types or "Steel" in pokemon.types:
                return False
        elif status == "frz":  # Freeze
            if "Ice" in pokemon.types:
                return False
        
        return True
    
    @staticmethod
    def apply_status_damage(pokemon: Pokemon) -> int:
        """
        Apply end-of-turn status damage (burn, poison, toxic).
        
        Returns damage dealt.
        """
        if not pokemon.status or pokemon.hp == 0:
            return 0
        
        damage = 0
        
        if pokemon.status == "brn":
            # Burn: 1/16 HP per turn
            damage = max(1, pokemon.max_hp // 16)
        elif pokemon.status == "psn":
            # Regular poison: 1/8 HP per turn
            damage = max(1, pokemon.max_hp // 8)
        elif pokemon.status == "tox":
            # Badly poisoned: N/16 HP per turn (N = turns poisoned)
            # For simplicity, we'll track this with a turn counter later
            damage = max(1, pokemon.max_hp // 8)
        
        if damage > 0:
            pokemon.hp = max(0, pokemon.hp - damage)
        
        return damage
    
    @staticmethod
    def check_status_prevention(pokemon: Pokemon) -> Optional[str]:
        """
        Check if status prevents Pokemon from moving.
        
        Returns reason if prevented, None otherwise.
        """
        if pokemon.status == "slp":
            # Simplified: 1-3 turns of sleep
            # In real implementation, track sleep turns
            if random.random() < 0.33:  # Wake up
                pokemon.status = ""
                return "woke_up"
            return "asleep"
        
        elif pokemon.status == "frz":
            # Freeze: 20% chance to thaw each turn
            if random.random() < 0.20:
                pokemon.status = ""
                return "thawed"
            return "frozen"
        
        elif pokemon.status == "par":
            # Paralysis: 25% chance to be fully paralyzed
            if random.random() < 0.25:
                return "paralyzed"
        
        return None
    
    @staticmethod
    def get_status_message(status: str) -> str:
        """Get display message for status condition."""
        messages = {
            "par": "is paralyzed! It may not be able to move!",
            "brn": "was burned!",
            "psn": "was poisoned!",
            "tox": "was badly poisoned!",
            "slp": "fell asleep!",
            "frz": "was frozen solid!",
        }
        return messages.get(status, f"was affected by {status}!")
    
    @staticmethod
    def get_boost_message(stat: str, change: int, is_self: bool = False) -> str:
        """Get display message for stat changes."""
        stat_names = {
            "atk": "Attack",
            "def": "Defense",
            "spa": "Sp. Atk",
            "spd": "Sp. Def",
            "spe": "Speed",
            "accuracy": "accuracy",
            "evasion": "evasiveness"
        }
        
        stat_name = stat_names.get(stat, stat)
        target = "Its" if is_self else "The target's"
        
        if abs(change) == 1:
            modifier = "rose" if change > 0 else "fell"
        elif abs(change) == 2:
            modifier = "sharply rose" if change > 0 else "harshly fell"
        else:
            modifier = "rose drastically" if change > 0 else "fell severely"
        
        return f"{target} {stat_name} {modifier}!"
