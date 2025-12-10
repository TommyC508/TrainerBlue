"""
Accurate Pokemon battle simulator based on Pokemon Showdown mechanics.
Reference: https://github.com/smogon/pokemon-showdown
"""
import random
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field

from .damage_calculator import DamageCalculator, calculate_stat, calculate_hp


@dataclass
class EffectState:
    """State tracking for volatile effects, status conditions, etc."""
    id: str
    duration: Optional[int] = None
    source: Optional['BattlePokemon'] = None
    custom_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BattlePokemon:
    """Pokemon in a battle with combat stats."""
    species: str
    level: int
    types: List[str]
    
    # Base stats
    base_hp: int
    base_atk: int
    base_def: int
    base_spa: int
    base_spd: int
    base_spe: int
    
    # Calculated stats (set after initialization)
    max_hp: int = 0
    current_hp: int = 0
    atk: int = 0
    defense: int = 0
    spa: int = 0
    spd: int = 0
    spe: int = 0
    
    # Battle state
    status: Optional[str] = None  # brn, par, slp, frz, psn, tox
    status_state: Optional[EffectState] = None
    fainted: bool = False
    
    # Pokemon features
    ability: str = "No Ability"
    item: Optional[str] = None
    
    # Stat boosts (-6 to +6)
    boosts: Dict[str, int] = field(default_factory=lambda: {
        'atk': 0, 'def': 0, 'spa': 0, 'spd': 0, 'spe': 0, 'accuracy': 0, 'evasion': 0
    })
    
    # Volatile effects (temporary battle conditions)
    volatiles: Dict[str, EffectState] = field(default_factory=dict)
    
    def __post_init__(self):
        """Calculate actual stats from base stats."""
        if self.max_hp == 0:
            self.max_hp = calculate_hp(self.base_hp, self.level)
            self.current_hp = self.max_hp
        if self.atk == 0:
            self.atk = calculate_stat(self.base_atk, self.level)
        if self.defense == 0:
            self.defense = calculate_stat(self.base_def, self.level)
        if self.spa == 0:
            self.spa = calculate_stat(self.base_spa, self.level)
        if self.spd == 0:
            self.spd = calculate_stat(self.base_spd, self.level)
        if self.spe == 0:
            self.spe = calculate_stat(self.base_spe, self.level)
    
    def get_boosted_stat(self, stat_name: str, ignore_negative: bool = False) -> int:
        """
        Get stat value with boost multiplier applied.
        
        Args:
            stat_name: Name of the stat (atk, def, spa, spd, spe)
            ignore_negative: If True, ignore negative boosts (for crits)
        
        Returns:
            Stat value with boost applied
        """
        base_value = getattr(self, stat_name)
        boost = self.boosts.get(stat_name, 0)
        
        # Critical hits ignore negative offensive boosts and positive defensive boosts
        if ignore_negative:
            if stat_name in ['atk', 'spa'] and boost < 0:
                boost = 0
            elif stat_name in ['defense', 'spd'] and boost > 0:
                boost = 0
        
        # Boost multipliers from Pokemon Showdown
        # Positive: [1, 1.5, 2, 2.5, 3, 3.5, 4] for +0 to +6
        # Negative: divide by same values
        if boost == 0:
            return base_value
        elif boost > 0:
            multipliers = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]
            return int(base_value * multipliers[boost])
        else:  # boost < 0
            multipliers = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]
            return int(base_value / multipliers[-boost])
    
    def boost_by(self, boosts: Dict[str, int]) -> Dict[str, int]:
        """
        Apply stat boosts with -6 to +6 clamping.
        
        Args:
            boosts: Dictionary of stat names to boost amounts
        
        Returns:
            Dictionary of actual boosts applied (after clamping)
        """
        applied = {}
        for stat, amount in boosts.items():
            if stat not in self.boosts:
                continue
            
            old_boost = self.boosts[stat]
            new_boost = max(-6, min(6, old_boost + amount))
            actual_change = new_boost - old_boost
            
            self.boosts[stat] = new_boost
            applied[stat] = actual_change
        
        return applied
    
    def clear_boosts(self):
        """Reset all stat boosts to 0."""
        for stat in self.boosts:
            self.boosts[stat] = 0
    
    def add_volatile(self, volatile_id: str, duration: Optional[int] = None, 
                    source: Optional['BattlePokemon'] = None) -> bool:
        """
        Add a volatile effect (temporary battle condition).
        
        Args:
            volatile_id: ID of the volatile effect
            duration: Number of turns the effect lasts (None = indefinite)
            source: Pokemon that caused this effect
        
        Returns:
            True if added, False if already present
        """
        if volatile_id in self.volatiles:
            return False
        
        self.volatiles[volatile_id] = EffectState(
            id=volatile_id,
            duration=duration,
            source=source
        )
        return True
    
    def remove_volatile(self, volatile_id: str) -> bool:
        """
        Remove a volatile effect.
        
        Args:
            volatile_id: ID of the volatile to remove
        
        Returns:
            True if removed, False if not present
        """
        if volatile_id in self.volatiles:
            del self.volatiles[volatile_id]
            return True
        return False
    
    def clear_volatiles(self):
        """Clear all volatile effects (called on switch-out)."""
        self.volatiles.clear()
    
    def take_damage(self, damage: int) -> int:
        """
        Apply damage to this Pokemon.
        
        Args:
            damage: Amount of damage to take
        
        Returns:
            Actual damage dealt (capped by current HP)
        """
        actual_damage = min(damage, self.current_hp)
        self.current_hp -= actual_damage
        
        if self.current_hp <= 0:
            self.current_hp = 0
            self.fainted = True
        
        return actual_damage
    
    def heal(self, amount: int) -> int:
        """
        Heal this Pokemon.
        
        Args:
            amount: Amount of HP to heal
        
        Returns:
            Actual HP healed
        """
        if self.fainted:
            return 0
        
        old_hp = self.current_hp
        self.current_hp = min(self.current_hp + amount, self.max_hp)
        return self.current_hp - old_hp
    
    @property
    def hp_percentage(self) -> float:
        """Get HP as percentage."""
        if self.max_hp == 0:
            return 0.0
        return (self.current_hp / self.max_hp) * 100


@dataclass
class Move:
    """A Pokemon move."""
    name: str
    type: str
    category: str  # Physical, Special, or Status
    base_power: int
    accuracy: int  # 0-100, or -1 for moves that never miss
    pp: int
    max_pp: int
    
    # Move properties
    priority: int = 0
    target: str = "normal"  # normal, self, allAdjacent, etc.
    
    # Stat changes (for Status moves)
    boosts: Optional[Dict[str, int]] = None  # e.g. {"atk": 2} for Swords Dance
    
    # Secondary effects
    secondary_chance: int = 0  # 0-100
    secondary_effect: Optional[str] = None


class BattleSimulator:
    """Simulates Pokemon battles using accurate Showdown mechanics."""
    
    def __init__(self, gen: int = 9):
        """
        Initialize battle simulator.
        
        Args:
            gen: Pokemon generation
        """
        self.gen = gen
        self.damage_calc = DamageCalculator(gen)
        self.turn_count = 0
        self.weather: Optional[str] = None
        self.weather_duration = 0
    
    def calculate_move_damage(
        self,
        attacker: BattlePokemon,
        defender: BattlePokemon,
        move: Move
    ) -> Tuple[int, float, bool]:
        """
        Calculate damage for a move.
        
        Args:
            attacker: Attacking Pokemon
            defender: Defending Pokemon
            move: Move being used
        
        Returns:
            Tuple of (damage, type_effectiveness, is_critical)
        """
        if move.category == "Status":
            return 0, 1.0, False
        
        # Critical hit check (1/24 chance in modern gens)
        is_critical = random.randint(1, 24) == 1
        
        # Determine which stats to use
        # Critical hits ignore negative offensive boosts and positive defensive boosts
        if move.category == "Physical":
            attack_stat = attacker.get_boosted_stat('atk', ignore_negative=is_critical)
            defense_stat = defender.get_boosted_stat('defense', ignore_negative=is_critical)
        else:  # Special
            attack_stat = attacker.get_boosted_stat('spa', ignore_negative=is_critical)
            defense_stat = defender.get_boosted_stat('spd', ignore_negative=is_critical)
        
        # Apply ability modifications
        attack_stat = self._apply_ability_attack_mod(attacker, defender, move, attack_stat)
        defense_stat = self._apply_ability_defense_mod(attacker, defender, move, defense_stat)
        
        # Calculate damage
        damage, effectiveness = self.damage_calc.calculate_damage(
            attacker_level=attacker.level,
            attacker_types=attacker.types,
            attacker_attack=attack_stat,
            attacker_status=attacker.status,
            defender_types=defender.types,
            defender_defense=defense_stat,
            move_base_power=move.base_power,
            move_type=move.type,
            move_category=move.category,
            is_critical=is_critical,
            weather=self.weather
        )
        
        return damage, effectiveness, is_critical
    
    def use_move(
        self,
        attacker: BattlePokemon,
        defender: BattlePokemon,
        move: Move
    ) -> Dict:
        """
        Execute a move and return battle log.
        
        Args:
            attacker: Attacking Pokemon
            defender: Defending Pokemon
            move: Move being used
        
        Returns:
            Dictionary with battle log information
        """
        log = {
            'attacker': attacker.species,
            'defender': defender.species,
            'move': move.name,
            'success': False,
            'damage': 0,
            'effectiveness': 1.0,
            'critical': False,
            'message': []
        }
        
        # Check if move hits (accuracy check)
        if move.accuracy > 0:
            # Calculate accuracy (including boosts)
            accuracy_boost = attacker.boosts.get('accuracy', 0) - defender.boosts.get('evasion', 0)
            if accuracy_boost >= 0:
                accuracy_multiplier = (3 + accuracy_boost) / 3
            else:
                accuracy_multiplier = 3 / (3 - accuracy_boost)
            
            effective_accuracy = move.accuracy * accuracy_multiplier
            
            if random.randint(1, 100) > effective_accuracy:
                log['message'].append(f"{attacker.species}'s attack missed!")
                return log
        
        log['message'].append(f"{attacker.species} used {move.name}!")
        
        if move.category == "Status":
            # Status moves - handle stat changes
            log['success'] = True
            
            if move.boosts:
                # Apply stat boosts to the user (most stat moves target self)
                applied_boosts = attacker.boost_by(move.boosts)
                
                for stat, change in applied_boosts.items():
                    if change > 0:
                        stage_text = "sharply " if abs(change) >= 2 else ""
                        log['message'].append(f"{attacker.species}'s {stat.upper()} {stage_text}rose!")
                    elif change < 0:
                        stage_text = "harshly " if abs(change) >= 2 else ""
                        log['message'].append(f"{attacker.species}'s {stat.upper()} {stage_text}fell!")
                    else:
                        # Hit +6 or -6 cap
                        if attacker.boosts[stat] >= 6:
                            log['message'].append(f"{attacker.species}'s {stat.upper()} won't go any higher!")
                        elif attacker.boosts[stat] <= -6:
                            log['message'].append(f"{attacker.species}'s {stat.upper()} won't go any lower!")
            else:
                # Other status effects
                log['message'].append(f"{move.name} status effect applied!")
            
            return log
        
        # Calculate damage
        damage, effectiveness, is_critical = self.calculate_move_damage(attacker, defender, move)
        
        # Apply damage
        actual_damage = defender.take_damage(damage)
        
        log['success'] = True
        log['damage'] = actual_damage
        log['effectiveness'] = effectiveness
        log['critical'] = is_critical
        
        # Add effectiveness message
        if effectiveness == 0:
            log['message'].append(f"It doesn't affect {defender.species}...")
        elif effectiveness < 0.5:
            log['message'].append(f"It's not very effective...")
        elif effectiveness > 1:
            log['message'].append(f"It's super effective!")
        
        # Add critical hit message
        if is_critical:
            log['message'].append("A critical hit!")
        
        # Add damage message
        log['message'].append(
            f"{defender.species} took {actual_damage} damage! "
            f"({defender.current_hp}/{defender.max_hp} HP remaining)"
        )
        
        # Check if defender fainted
        if defender.fainted:
            log['message'].append(f"{defender.species} fainted!")
        
        return log
    
    def get_faster_pokemon(
        self,
        pokemon1: BattlePokemon,
        move1: Move,
        pokemon2: BattlePokemon,
        move2: Move
    ) -> Tuple[BattlePokemon, Move, BattlePokemon, Move]:
        """
        Determine move order based on priority and speed.
        
        Returns:
            Tuple of (first_pokemon, first_move, second_pokemon, second_move)
        """
        # Check priority
        if move1.priority != move2.priority:
            if move1.priority > move2.priority:
                return pokemon1, move1, pokemon2, move2
            else:
                return pokemon2, move2, pokemon1, move1
        
        # Same priority, check speed
        speed1 = pokemon1.get_boosted_stat('spe')
        speed2 = pokemon2.get_boosted_stat('spe')
        
        if speed1 != speed2:
            if speed1 > speed2:
                return pokemon1, move1, pokemon2, move2
            else:
                return pokemon2, move2, pokemon1, move1
        
        # Speed tie - random
        if random.random() < 0.5:
            return pokemon1, move1, pokemon2, move2
        else:
            return pokemon2, move2, pokemon1, move1
    
    def simulate_turn(
        self,
        pokemon1: BattlePokemon,
        move1: Move,
        pokemon2: BattlePokemon,
        move2: Move
    ) -> List[Dict]:
        """
        Simulate one turn of battle.
        
        Args:
            pokemon1: First Pokemon
            move1: Move for first Pokemon
            pokemon2: Second Pokemon
            move2: Move for second Pokemon
        
        Returns:
            List of action logs
        """
        self.turn_count += 1
        logs = []
        
        # Determine move order
        first, first_move, second, second_move = self.get_faster_pokemon(
            pokemon1, move1, pokemon2, move2
        )
        
        # First Pokemon moves
        if not first.fainted:
            log = self.use_move(first, second, first_move)
            logs.append(log)
        
        # Second Pokemon moves (if still alive and first didn't KO it)
        if not second.fainted and not first.fainted:
            log = self.use_move(second, first, second_move)
            logs.append(log)
        
        # Update weather duration
        if self.weather and self.weather_duration > 0:
            self.weather_duration -= 1
            if self.weather_duration == 0:
                self.weather = None
        
        return logs
    
    def _apply_ability_attack_mod(self, attacker: BattlePokemon, defender: BattlePokemon, 
                                  move: Move, attack_stat: int) -> int:
        """Apply ability modifiers to attack stat."""
        ability = attacker.ability.lower().replace(" ", "")
        
        # Intimidate (opponent's ability reduces attacker's attack)
        # This is handled in boost_by during switch-in
        
        # Pure Power / Huge Power
        if ability in ["purepower", "hugepower"]:
            if move.category == "Physical":
                attack_stat = int(attack_stat * 2)
        
        # Guts (1.5x Attack when statused)
        elif ability == "guts":
            if attacker.status and move.category == "Physical":
                attack_stat = int(attack_stat * 1.5)
        
        # Overgrow/Blaze/Torrent/Swarm (1.5x when below 1/3 HP)
        elif ability == "overgrow" and move.type == "Grass":
            if attacker.current_hp <= attacker.max_hp / 3:
                attack_stat = int(attack_stat * 1.5)
        elif ability == "blaze" and move.type == "Fire":
            if attacker.current_hp <= attacker.max_hp / 3:
                attack_stat = int(attack_stat * 1.5)
        elif ability == "torrent" and move.type == "Water":
            if attacker.current_hp <= attacker.max_hp / 3:
                attack_stat = int(attack_stat * 1.5)
        elif ability == "swarm" and move.type == "Bug":
            if attacker.current_hp <= attacker.max_hp / 3:
                attack_stat = int(attack_stat * 1.5)
        
        return attack_stat
    
    def _apply_ability_defense_mod(self, attacker: BattlePokemon, defender: BattlePokemon,
                                   move: Move, defense_stat: int) -> int:
        """Apply ability modifiers to defense stat."""
        ability = defender.ability.lower().replace(" ", "")
        
        # Thick Fat (halves Fire/Ice damage by reducing effective attack)
        if ability == "thickfat":
            if move.type in ["Fire", "Ice"]:
                # We modify defense instead to achieve same effect
                defense_stat = int(defense_stat * 2)
        
        # Marvel Scale (1.5x Def when statused)
        elif ability == "marvelscale":
            if defender.status and move.category == "Physical":
                defense_stat = int(defense_stat * 1.5)
        
        return defense_stat
    
    def apply_switch_in_abilities(self, pokemon: BattlePokemon, opponent: BattlePokemon):
        """Apply abilities that trigger on switch-in."""
        ability = pokemon.ability.lower().replace(" ", "")
        
        # Intimidate: Lower opponent's Attack by 1 stage
        if ability == "intimidate":
            opponent.boost_by({"atk": -1})
        
        # Download: Raise Atk or SpA by 1 based on opponent's lower defense
        elif ability == "download":
            if opponent.defense < opponent.spd:
                pokemon.boost_by({"atk": 1})
            else:
                pokemon.boost_by({"spa": 1})
