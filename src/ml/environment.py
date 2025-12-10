"""Reinforcement Learning environment for Pokemon Showdown using Gymnasium."""
import gymnasium as gym
from gymnasium import spaces
import numpy as np
from typing import Optional, Tuple, Dict, Any
import logging

from ..battle.state import BattleState
from ..data.models import Pokemon
from ..data.type_effectiveness import get_type_effectiveness
from ..data.damage_calculator import DamageCalculator

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
        
        # Create random teams (simplified)
        for side in [state.our_side, state.opponent_side]:
            side.team = []
            for i in range(6):
                pokemon = Pokemon(
                    species=f"Pokemon{i+1}",
                    level=100,
                    hp=100,
                    max_hp=100,
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
                
                # Type encoding (2 features) - simplified
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
    
    def _execute_turn(self, our_action) -> float:
        """
        Execute a turn and return reward.
        
        Simplified turn execution for training.
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
                import random
                opp_action = random.choice(legal_actions)
            else:
                from ..connection.protocol import Action
                opp_action = Action(type="default")
        
        # Simplified battle simulation
        reward = 0.0
        
        our_active = self.state.get_our_active_pokemon()
        opp_active = self.state.get_opponent_active_pokemon()
        
        if our_active and opp_active:
            # Simulate damage
            if our_action.type == "move":
                # Deal damage to opponent
                damage = np.random.randint(20, 40)
                opp_active.hp = max(0, opp_active.hp - damage)
                reward += damage / 100.0  # Reward for dealing damage
                
                if opp_active.hp == 0:
                    opp_active.fainted = True
                    reward += 2.0  # Big reward for KO
            
            if opp_action.type == "move" and opp_active.hp > 0:
                # Take damage from opponent
                damage = np.random.randint(20, 40)
                our_active.hp = max(0, our_active.hp - damage)
                reward -= damage / 100.0  # Penalty for taking damage
                
                if our_active.hp == 0:
                    our_active.fainted = True
                    reward -= 2.0  # Big penalty for being KO'd
        
        # Penalty for each turn (encourage faster wins)
        reward -= 0.01
        
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
        
        return {
            "turn": self.current_turn,
            "our_pokemon_alive": our_alive,
            "opponent_pokemon_alive": opp_alive,
        }
    
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
