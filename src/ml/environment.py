"""Reinforcement Learning environment for Pokemon Showdown using Gymnasium."""
import gymnasium as gym
from gymnasium import spaces
import numpy as np
from typing import Optional, Tuple, Dict, Any
import logging
import random

from ..battle.state import BattleState
from ..data.models import Pokemon, Move
from ..data.type_effectiveness import get_type_effectiveness
from ..data.damage_calculator import DamageCalculator
from ..data.secondary_effects import SecondaryEffects

logger = logging.getLogger(__name__)


class PokemonBattleEnv(gym.Env):
    """
    Custom Gymnasium environment for Pokemon Showdown battles.
    
    This environment allows RL agents to learn to play Pokemon battles.
    Compatible with StableBaselines3.
    """
    
    metadata = {"render_modes": ["human", "ansi"], "render_fps": 1}
    
    def __init__(
        self,
        opponent_agent=None,
        max_turns: int = 100,
        render_mode: Optional[str] = None
    ):
        """
        Initialize the environment.
        
        Args:
            opponent_agent: Agent to play against (if None, uses random)
            max_turns: Maximum turns before battle ends in draw
            render_mode: Render mode for visualization
        """
        super().__init__()
        
        self.opponent_agent = opponent_agent
        self.max_turns = max_turns
        self.render_mode = render_mode
        
        # State space dimensions
        # Each Pokemon: [hp%, 6 stats, 2 types, status, 6 boosts] = 16 features
        # 6 Pokemon per side = 96 features per side
        # Field conditions: 10 features
        # Total: 96 + 96 + 10 = 202 features
        self.observation_space = spaces.Box(
            low=-1.0,
            high=1.0,
            shape=(202,),
            dtype=np.float32
        )
        
        # Action space: 4 moves + 5 switches = 9 possible actions
        self.action_space = spaces.Discrete(9)
        
        # Battle state
        self.state: Optional[BattleState] = None
        self.current_turn = 0
        self.damage_calc = DamageCalculator()
        
    def reset(
        self,
        seed: Optional[int] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Reset the environment to initial state.
        
        Returns:
            observation: Initial observation
            info: Additional information
        """
        super().reset(seed=seed)
        
        # Initialize battle state with random teams
        self.state = self._create_random_battle()
        self.current_turn = 0
        
        observation = self._get_observation()
        info = self._get_info()
        
        return observation, info
    
    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        """
        Execute one step in the environment.
        
        Args:
            action: Action to take (0-3: moves, 4-8: switches)
            
        Returns:
            observation: New observation
            reward: Reward for the action
            terminated: Whether episode is done
            truncated: Whether episode was truncated
            info: Additional information
        """
        if self.state is None:
            raise RuntimeError("Must call reset() before step()")
        
        # Convert action to game action
        game_action = self._action_to_game_action(action)
        
        # Execute action and get opponent action
        reward = self._execute_turn(game_action)
        
        self.current_turn += 1
        
        # Check if battle is over
        terminated = self._is_battle_over()
        truncated = self.current_turn >= self.max_turns
        
        observation = self._get_observation()
        info = self._get_info()
        
        return observation, reward, terminated, truncated, info
    
    def render(self):
        """Render the environment."""
        if self.render_mode == "ansi":
            return self._render_ansi()
        elif self.render_mode == "human":
            print(self._render_ansi())
    
    def _create_random_battle(self) -> BattleState:
        """Create a battle state with random teams."""
        state = BattleState(our_player_id="p1")
        
        # Common types for random battles
        common_types = ["Normal", "Fire", "Water", "Electric", "Grass", "Fighting", "Psychic"]
        
        # Create random teams (simplified)
        for side in [state.our_side, state.opponent_side]:
            side.team = []
            for i in range(6):
                pokemon_types = [random.choice(common_types)]
                if random.random() > 0.5:  # 50% chance of dual type
                    second_type = random.choice(common_types)
                    if second_type != pokemon_types[0]:
                        pokemon_types.append(second_type)
                
                pokemon = Pokemon(
                    species=f"Pokemon{i+1}",
                    level=100,
                    hp=300,  # More realistic HP
                    max_hp=300,
                    types=pokemon_types,
                    stats={
                        "atk": np.random.randint(80, 150),
                        "def": np.random.randint(80, 150),
                        "spa": np.random.randint(80, 150),
                        "spd": np.random.randint(80, 150),
                        "spe": np.random.randint(80, 150),
                    },
                    moves=["Move1", "Move2", "Move3", "Move4"]
                )
                side.team.append(pokemon)
            
            # Set first Pokemon as active
            side.team[0].active = True
            side.active_pokemon = [0]
        
        state.started = True
        return state
    
    def _get_observation(self) -> np.ndarray:
        """
        Convert battle state to observation vector.
        
        Returns normalized feature vector of shape (202,)
        """
        if self.state is None:
            return np.zeros(202, dtype=np.float32)
        
        features = []
        
        # Our team features (96 features)
        features.extend(self._encode_team(self.state.our_side))
        
        # Opponent team features (96 features)
        features.extend(self._encode_team(self.state.opponent_side))
        
        # Field conditions (10 features)
        features.extend(self._encode_field())
        
        return np.array(features, dtype=np.float32)
    
    def _encode_team(self, side) -> list:
        """Encode a team to features (96 features for 6 Pokemon)."""
        features = []
        
        for i in range(6):
            if i < len(side.team):
                pokemon = side.team[i]
                
                # HP percentage (1 feature)
                features.append(pokemon.hp_percent / 100.0)
                
                # Stats normalized (6 features)
                for stat in ["atk", "def", "spa", "spd", "spe"]:
                    features.append(pokemon.stats.get(stat, 100) / 150.0)
                features.append(0.0)  # Padding for 6 stats
                
                # Type encoding (2 features) - encode type matchup effectiveness
                # This helps the agent learn about type advantages
                if hasattr(self, 'state') and self.state:
                    opp_active = self.state.get_opponent_active_pokemon()
                    if opp_active and pokemon.types:
                        # Calculate type effectiveness of our Pokemon's type against opponent
                        effectiveness = get_type_effectiveness(
                            pokemon.types[0], opp_active.types
                        ) if pokemon.types else 1.0
                        features.append((effectiveness - 1.0))  # Normalize around 0
                        
                        # If dual type, average effectiveness
                        if len(pokemon.types) > 1:
                            effectiveness2 = get_type_effectiveness(
                                pokemon.types[1], opp_active.types
                            )
                            features.append((effectiveness2 - 1.0))
                        else:
                            features.append(0.0)
                    else:
                        features.extend([0.0, 0.0])
                else:
                    features.extend([0.0, 0.0])
                
                # Status (1 feature)
                status_map = {"": 0.0, "par": 0.25, "brn": 0.5, "psn": 0.75, "slp": 1.0, "frz": 1.0}
                features.append(status_map.get(pokemon.status, 0.0))
                
                # Boosts (6 features)
                for stat in ["atk", "def", "spa", "spd", "spe", "accuracy"]:
                    boost = pokemon.boosts.get(stat, 0)
                    features.append(boost / 6.0)  # Normalize -6 to +6
                
            else:
                # Padding for missing Pokemon
                features.extend([0.0] * 16)
        
        return features
    
    def _encode_field(self) -> list:
        """Encode field conditions (10 features)."""
        features = []
        
        # Weather (1 feature)
        weather_map = {"": 0.0, "sunnyday": 0.33, "raindance": 0.67, "sandstorm": 1.0}
        features.append(weather_map.get(self.state.field.weather, 0.0))
        
        # Terrain (1 feature)
        terrain_map = {"": 0.0, "electricterrain": 0.33, "grassyterrain": 0.67, "mistyterrain": 1.0}
        features.append(terrain_map.get(self.state.field.terrain, 0.0))
        
        # Trick room (1 feature)
        features.append(1.0 if self.state.field.trick_room else 0.0)
        
        # Turn number normalized (1 feature)
        features.append(self.current_turn / self.max_turns)
        
        # Padding (6 features)
        features.extend([0.0] * 6)
        
        return features
    
    def _action_to_game_action(self, action: int):
        """Convert discrete action to game action."""
        from ..connection.protocol import Action
        
        if action < 4:
            # Move action
            return Action(type="move", value=str(action + 1))
        else:
            # Switch action
            return Action(type="switch", value=str(action - 3))
    
    def get_action_mask(self) -> np.ndarray:
        """
        Get mask of valid actions.
        
        Returns:
            Boolean array where True = valid action, False = invalid
        """
        if not self.state:
            return np.ones(9, dtype=bool)
        
        mask = np.zeros(9, dtype=bool)
        our_active = self.state.get_our_active_pokemon()
        
        if not our_active:
            return np.ones(9, dtype=bool)  # All valid if no active Pokemon
        
        # Moves (0-3): Always available if Pokemon is alive
        mask[0:4] = True
        
        # Switches (4-8): Valid if target Pokemon is alive and not active
        for i, pokemon in enumerate(self.state.our_side.team[:5]):
            if i < len(self.state.our_side.team) - 1:  # Max 5 switches (6 total - 1 active)
                target_idx = i + 1 if i >= 0 else i
                if target_idx < len(self.state.our_side.team):
                    target_pokemon = self.state.our_side.team[target_idx]
                    # Can switch if Pokemon is alive and not currently active
                    if target_pokemon.hp > 0 and not target_pokemon.active:
                        mask[4 + i] = True
        
        # Ensure at least one action is valid
        if not mask.any():
            mask[0] = True  # Default to first move
        
        return mask
    
    def _create_move_for_calculation(self, move_name: str, attacker_types: list) -> Move:
        """
        Create a Move object for damage calculation.
        
        Args:
            move_name: Name of the move
            attacker_types: Types of the attacking Pokemon
            
        Returns:
            Move object with appropriate properties
        """
        # Randomly assign move type based on attacker's type (for STAB)
        move_type = random.choice(attacker_types) if attacker_types else "Normal"
        
        # Randomly choose physical or special
        category = random.choice(["Physical", "Special"])
        
        # Random power between 60-100 (realistic range)
        power = random.randint(60, 100)
        
        return Move(
            name=move_name,
            type=move_type,
            category=category,
            power=power,
            accuracy=100,
            pp=10,
            priority=0
        )
    
    def _execute_turn(self, our_action) -> float:
        """
        Execute a turn and return reward.
        
        Enhanced with real damage calculation and improved reward function.
        """
        if not self.state:
            return 0.0
        
        # Get opponent action
        if self.opponent_agent:
            opp_action = self.opponent_agent.choose_move(self.state)
        else:
            # Random opponent
            legal_actions = self.state.get_legal_actions()
            if legal_actions:
                opp_action = random.choice(legal_actions)
            else:
                from ..connection.protocol import Action
                opp_action = Action(type="default")
        
        # Track HP before turn for reward calculation
        our_active = self.state.get_our_active_pokemon()
        opp_active = self.state.get_opponent_active_pokemon()
        
        if not our_active or not opp_active:
            return 0.0
        
        our_hp_before = our_active.hp
        opp_hp_before = opp_active.hp
        
        # Determine turn order based on speed
        our_goes_first = self.damage_calc.calculate_speed_order(
            our_active, opp_active, self.state.field.trick_room
        )
        
        # Execute actions in speed order
        if our_goes_first:
            self._execute_action(our_action, our_active, opp_active, is_our_turn=True)
            if opp_active.hp > 0:  # Only if opponent is still alive
                self._execute_action(opp_action, opp_active, our_active, is_our_turn=False)
        else:
            self._execute_action(opp_action, opp_active, our_active, is_our_turn=False)
            if our_active.hp > 0:  # Only if we're still alive
                self._execute_action(our_action, our_active, opp_active, is_our_turn=True)
        
        # Apply end-of-turn status damage (burn, poison)
        if our_active.hp > 0:
            SecondaryEffects.apply_status_damage(our_active)
        if opp_active.hp > 0:
            SecondaryEffects.apply_status_damage(opp_active)
        
        # Calculate reward
        reward = self._calculate_reward(
            our_active, opp_active,
            our_hp_before, opp_hp_before
        )
        
        return reward
    
    def _execute_action(self, action, attacker: Pokemon, defender: Pokemon, is_our_turn: bool):
        """
        Execute a single action (move or switch).
        
        Args:
            action: Action to execute
            attacker: Pokemon performing the action
            defender: Pokemon receiving the action
            is_our_turn: Whether this is our turn (for tracking)
        """
        if action.type == "move":
            # Check status prevention (sleep, freeze, paralysis)
            if SecondaryEffects.check_status_prevention(attacker):
                return
            
            # Create move object for damage calculation
            move = self._create_move_for_calculation(
                f"Move{action.value}",
                attacker.types
            )
            
            # Calculate damage using real damage calculator
            damage_range = self.damage_calc.calculate_damage(
                attacker=attacker,
                defender=defender,
                move=move,
                weather=self.state.field.weather,
                terrain=self.state.field.terrain,
                is_critical=random.random() < 0.0625,  # ~6.25% crit chance
                user_types=attacker.types,
                target_types=defender.types
            )
            
            # Apply damage (use average of range)
            damage = int(damage_range.average)
            defender.hp = max(0, defender.hp - damage)
            
            if defender.hp == 0:
                defender.fainted = True
            
            # Apply secondary effects (status, stat changes, recoil) if target is alive
            if damage > 0 and defender.hp > 0:
                SecondaryEffects.apply_secondary_effects(move, attacker, defender, damage)
        
        elif action.type == "switch":
            # Handle switch (simplified - just mark as switched)
            pass
    
    def _calculate_reward(self, our_active: Pokemon, opp_active: Pokemon,
                         our_hp_before: int, opp_hp_before: int) -> float:
        """
        Calculate reward for the turn using improved win-focused reward function.
        
        Reward components:
        - Win/Loss: +100/-100
        - HP advantage: +0.5 per % difference
        - KO bonus: +5/-5
        - Turn efficiency: -0.1 per turn
        """
        reward = 0.0
        
        # Check if battle is over
        our_alive = sum(1 for p in self.state.our_side.team if p.hp > 0)
        opp_alive = sum(1 for p in self.state.opponent_side.team if p.hp > 0)
        
        if our_alive == 0 or opp_alive == 0:
            # Battle over - big win/loss reward
            if our_alive > opp_alive:
                reward += 100.0  # Win
            else:
                reward -= 100.0  # Loss
        
        # HP advantage reward
        our_hp_pct = (our_active.hp / our_active.max_hp) * 100 if our_active.max_hp > 0 else 0
        opp_hp_pct = (opp_active.hp / opp_active.max_hp) * 100 if opp_active.max_hp > 0 else 0
        hp_diff = our_hp_pct - opp_hp_pct
        reward += hp_diff * 0.5
        
        # KO bonuses
        if opp_active.hp == 0 and opp_hp_before > 0:
            reward += 5.0  # Knocked out opponent
        
        if our_active.hp == 0 and our_hp_before > 0:
            reward -= 5.0  # Got knocked out
        
        # Damage dealt/received rewards
        damage_dealt = opp_hp_before - opp_active.hp
        damage_taken = our_hp_before - our_active.hp
        
        reward += damage_dealt / 100.0
        reward -= damage_taken / 100.0
        
        # Turn efficiency penalty (encourage faster wins)
        reward -= 0.1
        
        return reward
    
    def _is_battle_over(self) -> bool:
        """Check if battle is finished."""
        if not self.state:
            return True
        
        our_alive = sum(1 for p in self.state.our_side.team if p.hp > 0)
        opp_alive = sum(1 for p in self.state.opponent_side.team if p.hp > 0)
        
        return our_alive == 0 or opp_alive == 0
    
    def _get_info(self) -> Dict[str, Any]:
        """Get additional information."""
        if not self.state:
            return {}
        
        our_alive = sum(1 for p in self.state.our_side.team if p.hp > 0)
        opp_alive = sum(1 for p in self.state.opponent_side.team if p.hp > 0)
        
        info = {
            "turn": self.current_turn,
            "our_pokemon_alive": our_alive,
            "opponent_pokemon_alive": opp_alive,
            "action_mask": self.get_action_mask(),  # Add action mask for potential use
        }
        
        return info
    
    def _render_ansi(self) -> str:
        """Render as ASCII text."""
        if not self.state:
            return "Battle not started"
        
        lines = []
        lines.append(f"=== Turn {self.current_turn} ===")
        lines.append("")
        
        our_active = self.state.get_our_active_pokemon()
        opp_active = self.state.get_opponent_active_pokemon()
        
        if our_active:
            lines.append(f"Our: {our_active.species} - HP: {our_active.hp}/{our_active.max_hp}")
        
        if opp_active:
            lines.append(f"Opp: {opp_active.species} - HP: {opp_active.hp}/{opp_active.max_hp}")
        
        lines.append("")
        
        return "\n".join(lines)
