"""Gymnasium environment for Pokemon Showdown battles."""
import gymnasium as gym
import numpy as np
from gymnasium import spaces
from typing import Optional, Dict, Any, Tuple, List
import logging
import random

from ..battle.state import BattleState
from ..battle.simulator import BattleSimulator, BattlePokemon, Move
from ..data.models import Pokemon
from ..data.type_effectiveness import get_type_effectiveness

logger = logging.getLogger(__name__)


class PokemonBattleEnv(gym.Env):
    """
    Gymnasium environment for Pokemon Showdown battles.
    
    Observation Space:
        - Our active Pokemon state (HP, stats, boosts, status)
        - Opponent active Pokemon state
        - Field conditions
        - Our team summary
        - Opponent team summary
        
    Action Space:
        - Discrete(9): 4 moves + 5 switches (max)
    """
    
    metadata = {"render_modes": ["human", "ansi"], "render_fps": 1}
    
    def __init__(self, render_mode: Optional[str] = None, max_turns: int = 100, opponent_agent=None):
        """
        Initialize the Pokemon battle environment.
        
        Args:
            render_mode: Rendering mode ("human" or "ansi")
            max_turns: Maximum turns before battle ends in draw
            opponent_agent: Opponent agent to play against (if None, uses random)
        """
        super().__init__()
        
        self.render_mode = render_mode
        self.max_turns = max_turns
        self.opponent_agent = opponent_agent
        
        # Battle state
        self.state: Optional[BattleState] = None
        self.turn_count = 0
        
        # Battle simulator (accurate Pokemon Showdown mechanics)
        self.simulator = BattleSimulator(gen=9)
        
        # Battle Pokemon (for accurate simulation)
        self.our_team: List[BattlePokemon] = []
        self.opp_team: List[BattlePokemon] = []
        self.our_active_idx: int = 0
        self.opp_active_idx: int = 0
        
        # Define action space: 4 moves + 5 switches = 9 actions max
        self.action_space = spaces.Discrete(9)
        
        # Define observation space
        # Simplified feature vector representation
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(200,),  # Feature vector size
            dtype=np.float32
        )
        
    def reset(self, seed: Optional[int] = None, options: Optional[Dict[str, Any]] = None) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Reset the environment to initial state.
        
        Args:
            seed: Random seed
            options: Additional options
            
        Returns:
            observation: Initial observation
            info: Additional information
        """
        super().reset(seed=seed)
        
        # Create a new battle state
        self.state = BattleState(our_player_id="p1")
        self.turn_count = 0
        
        # Initialize mock teams for training
        self._initialize_mock_teams()
        
        observation = self._get_observation()
        info = self._get_info()
        
        return observation, info
    
    def _initialize_mock_teams(self):
        """Initialize mock Pokemon teams for training with accurate battle mechanics."""
        if not self.state:
            return
        
        # Expanded Pokemon data with 24 species covering all types and strategic roles
        # Format: species, types, base stats (hp, atk, def, spa, spd, spe), ability
        pokemon_data = [
            # Starter trio - Balanced all-rounders
            {"species": "Charizard", "types": ["Fire", "Flying"], "ability": "Blaze",
             "stats": {"hp": 78, "atk": 84, "def": 78, "spa": 109, "spd": 85, "spe": 100}},
            {"species": "Blastoise", "types": ["Water"], "ability": "Torrent",
             "stats": {"hp": 79, "atk": 83, "def": 100, "spa": 85, "spd": 105, "spe": 78}},
            {"species": "Venusaur", "types": ["Grass", "Poison"], "ability": "Overgrow",
             "stats": {"hp": 80, "atk": 82, "def": 83, "spa": 100, "spd": 100, "spe": 80}},
            
            # Fast special attackers
            {"species": "Gengar", "types": ["Ghost", "Poison"], "ability": "Levitate",
             "stats": {"hp": 60, "atk": 65, "def": 60, "spa": 130, "spd": 75, "spe": 110}},
            {"species": "Alakazam", "types": ["Psychic"], "ability": "Synchronize",
             "stats": {"hp": 55, "atk": 50, "def": 45, "spa": 135, "spd": 95, "spe": 120}},
            {"species": "Jolteon", "types": ["Electric"], "ability": "Volt Absorb",
             "stats": {"hp": 65, "atk": 65, "def": 60, "spa": 110, "spd": 95, "spe": 130}},
            
            # Bulky physical attackers
            {"species": "Dragonite", "types": ["Dragon", "Flying"], "ability": "Multiscale",
             "stats": {"hp": 91, "atk": 134, "def": 95, "spa": 100, "spd": 100, "spe": 80}},
            {"species": "Tyranitar", "types": ["Rock", "Dark"], "ability": "Sand Stream",
             "stats": {"hp": 100, "atk": 134, "def": 110, "spa": 95, "spd": 100, "spe": 61}},
            {"species": "Machamp", "types": ["Fighting"], "ability": "Guts",
             "stats": {"hp": 90, "atk": 130, "def": 80, "spa": 65, "spd": 85, "spe": 55}},
            
            # Defensive walls
            {"species": "Blissey", "types": ["Normal"], "ability": "Natural Cure",
             "stats": {"hp": 255, "atk": 10, "def": 10, "spa": 75, "spd": 135, "spe": 55}},
            {"species": "Skarmory", "types": ["Steel", "Flying"], "ability": "Sturdy",
             "stats": {"hp": 65, "atk": 80, "def": 140, "spa": 40, "spd": 70, "spe": 70}},
            {"species": "Snorlax", "types": ["Normal"], "ability": "Thick Fat",
             "stats": {"hp": 160, "atk": 110, "def": 65, "spa": 65, "spd": 110, "spe": 30}},
            
            # Type specialists
            {"species": "Gyarados", "types": ["Water", "Flying"], "ability": "Intimidate",
             "stats": {"hp": 95, "atk": 125, "def": 79, "spa": 60, "spd": 100, "spe": 81}},
            {"species": "Arcanine", "types": ["Fire"], "ability": "Intimidate",
             "stats": {"hp": 90, "atk": 110, "def": 80, "spa": 100, "spd": 80, "spe": 95}},
            {"species": "Exeggutor", "types": ["Grass", "Psychic"], "ability": "Chlorophyll",
             "stats": {"hp": 95, "atk": 95, "def": 85, "spa": 125, "spd": 75, "spe": 55}},
            {"species": "Starmie", "types": ["Water", "Psychic"], "ability": "Natural Cure",
             "stats": {"hp": 60, "atk": 75, "def": 85, "spa": 100, "spd": 85, "spe": 115}},
            {"species": "Lapras", "types": ["Water", "Ice"], "ability": "Water Absorb",
             "stats": {"hp": 130, "atk": 85, "def": 80, "spa": 85, "spd": 95, "spe": 60}},
            
            # Unique niches
            {"species": "Pikachu", "types": ["Electric"], "ability": "Static",
             "stats": {"hp": 35, "atk": 55, "def": 40, "spa": 50, "spd": 50, "spe": 90}},
            {"species": "Mewtwo", "types": ["Psychic"], "ability": "Pressure",
             "stats": {"hp": 106, "atk": 110, "def": 90, "spa": 154, "spd": 90, "spe": 130}},
            {"species": "Mew", "types": ["Psychic"], "ability": "Synchronize",
             "stats": {"hp": 100, "atk": 100, "def": 100, "spa": 100, "spd": 100, "spe": 100}},
            
            # Additional coverage
            {"species": "Golem", "types": ["Rock", "Ground"], "ability": "Sturdy",
             "stats": {"hp": 80, "atk": 120, "def": 130, "spa": 55, "spd": 65, "spe": 45}},
            {"species": "Cloyster", "types": ["Water", "Ice"], "ability": "Shell Armor",
             "stats": {"hp": 50, "atk": 95, "def": 180, "spa": 85, "spd": 45, "spe": 70}},
            {"species": "Nidoking", "types": ["Poison", "Ground"], "ability": "Poison Point",
             "stats": {"hp": 81, "atk": 102, "def": 77, "spa": 85, "spd": 75, "spe": 85}},
            {"species": "Aerodactyl", "types": ["Rock", "Flying"], "ability": "Pressure",
             "stats": {"hp": 80, "atk": 105, "def": 65, "spa": 60, "spd": 75, "spe": 130}},
        ]
        
        # Comprehensive moves database covering all 18 types
        # Format: type -> {name, type, category, power, accuracy}
        moves_db = {
            "Fire": {"name": "Flamethrower", "type": "Fire", "category": "Special", "power": 90, "accuracy": 100},
            "Water": {"name": "Hydro Pump", "type": "Water", "category": "Special", "power": 110, "accuracy": 80},
            "Grass": {"name": "Energy Ball", "type": "Grass", "category": "Special", "power": 90, "accuracy": 100},
            "Electric": {"name": "Thunderbolt", "type": "Electric", "category": "Special", "power": 90, "accuracy": 100},
            "Ice": {"name": "Ice Beam", "type": "Ice", "category": "Special", "power": 90, "accuracy": 100},
            "Fighting": {"name": "Close Combat", "type": "Fighting", "category": "Physical", "power": 120, "accuracy": 100},
            "Poison": {"name": "Sludge Bomb", "type": "Poison", "category": "Special", "power": 90, "accuracy": 100},
            "Ground": {"name": "Earthquake", "type": "Ground", "category": "Physical", "power": 100, "accuracy": 100},
            "Flying": {"name": "Air Slash", "type": "Flying", "category": "Special", "power": 75, "accuracy": 95},
            "Psychic": {"name": "Psychic", "type": "Psychic", "category": "Special", "power": 90, "accuracy": 100},
            "Bug": {"name": "Bug Buzz", "type": "Bug", "category": "Special", "power": 90, "accuracy": 100},
            "Rock": {"name": "Stone Edge", "type": "Rock", "category": "Physical", "power": 100, "accuracy": 80},
            "Ghost": {"name": "Shadow Ball", "type": "Ghost", "category": "Special", "power": 80, "accuracy": 100},
            "Dragon": {"name": "Dragon Claw", "type": "Dragon", "category": "Physical", "power": 80, "accuracy": 100},
            "Dark": {"name": "Dark Pulse", "type": "Dark", "category": "Special", "power": 80, "accuracy": 100},
            "Steel": {"name": "Flash Cannon", "type": "Steel", "category": "Special", "power": 80, "accuracy": 100},
            "Fairy": {"name": "Moonblast", "type": "Fairy", "category": "Special", "power": 95, "accuracy": 100},
            "Normal": {"name": "Body Slam", "type": "Normal", "category": "Physical", "power": 85, "accuracy": 100},
        }
        
        # Additional coverage moves
        coverage_moves = {
            "Surf": {"name": "Surf", "type": "Water", "category": "Special", "power": 90, "accuracy": 100},
            "Thunderbolt": {"name": "Thunderbolt", "type": "Electric", "category": "Special", "power": 90, "accuracy": 100},
            "Ice Beam": {"name": "Ice Beam", "type": "Ice", "category": "Special", "power": 90, "accuracy": 100},
            "Fire Blast": {"name": "Fire Blast", "type": "Fire", "category": "Special", "power": 110, "accuracy": 85},
            "Thunder": {"name": "Thunder", "type": "Electric", "category": "Special", "power": 110, "accuracy": 70},
            "Blizzard": {"name": "Blizzard", "type": "Ice", "category": "Special", "power": 110, "accuracy": 70},
            "Solar Beam": {"name": "Solar Beam", "type": "Grass", "category": "Special", "power": 120, "accuracy": 100},
            "Giga Drain": {"name": "Giga Drain", "type": "Grass", "category": "Special", "power": 75, "accuracy": 100},
            "Brick Break": {"name": "Brick Break", "type": "Fighting", "category": "Physical", "power": 75, "accuracy": 100},
            "Rock Slide": {"name": "Rock Slide", "type": "Rock", "category": "Physical", "power": 75, "accuracy": 90},
        }
        
        # Stat-changing moves (Status moves for competitive battling)
        stat_moves = {
            "Swords Dance": {"name": "Swords Dance", "type": "Normal", "category": "Status", "power": 0, "accuracy": -1, 
                           "boosts": {"atk": 2}},
            "Dragon Dance": {"name": "Dragon Dance", "type": "Dragon", "category": "Status", "power": 0, "accuracy": -1,
                           "boosts": {"atk": 1, "spe": 1}},
            "Nasty Plot": {"name": "Nasty Plot", "type": "Dark", "category": "Status", "power": 0, "accuracy": -1,
                         "boosts": {"spa": 2}},
            "Calm Mind": {"name": "Calm Mind", "type": "Psychic", "category": "Status", "power": 0, "accuracy": -1,
                        "boosts": {"spa": 1, "spd": 1}},
            "Iron Defense": {"name": "Iron Defense", "type": "Steel", "category": "Status", "power": 0, "accuracy": -1,
                           "boosts": {"def": 2}},
            "Amnesia": {"name": "Amnesia", "type": "Psychic", "category": "Status", "power": 0, "accuracy": -1,
                      "boosts": {"spd": 2}},
            "Agility": {"name": "Agility", "type": "Psychic", "category": "Status", "power": 0, "accuracy": -1,
                      "boosts": {"spe": 2}},
            "Bulk Up": {"name": "Bulk Up", "type": "Fighting", "category": "Status", "power": 0, "accuracy": -1,
                      "boosts": {"atk": 1, "def": 1}},
        }
        
        # Randomly select 6 Pokemon for each team (with replacement for variety)
        import random
        selected_indices = random.sample(range(len(pokemon_data)), 6)
        opponent_indices = random.sample(range(len(pokemon_data)), 6)
        
        # Create teams using accurate battle simulator
        self.our_team = []
        self.opp_team = []
        
        # Helper function to get moveset for a Pokemon
        def get_moveset(types):
            """Get 4 moves based on Pokemon's types."""
            moveset = []
            # Add STAB moves for each type
            for ptype in types[:2]:  # Up to 2 types
                if ptype in moves_db:
                    moveset.append(moves_db[ptype]["name"])
            
            # Add coverage moves to fill out moveset
            coverage_list = list(coverage_moves.values())
            while len(moveset) < 4 and coverage_list:
                move = random.choice(coverage_list)
                if move["name"] not in moveset:
                    moveset.append(move["name"])
                coverage_list.remove(move)
            
            # Fill remaining slots with Body Slam if needed
            while len(moveset) < 4:
                moveset.append("Body Slam")
            
            return moveset[:4]
        
        for i, idx in enumerate(selected_indices):
            data = pokemon_data[idx]
            
            # Create BattlePokemon for our team
            our_bp = BattlePokemon(
                species=data["species"],
                level=50,
                types=data["types"],
                base_hp=data["stats"]["hp"],
                base_atk=data["stats"]["atk"],
                base_def=data["stats"]["def"],
                base_spa=data["stats"]["spa"],
                base_spd=data["stats"]["spd"],
                base_spe=data["stats"]["spe"],
                ability=data.get("ability", "No Ability")
            )
            self.our_team.append(our_bp)
            
            # Get moveset for this Pokemon
            moveset = get_moveset(data["types"])
            
            # Also create Pokemon for state tracking (for observation encoding)
            our_pkmn = Pokemon(
                species=data["species"],
                level=50,
                hp=our_bp.max_hp,
                max_hp=our_bp.max_hp,
                status="",
                active=(i == 0),
                stats={"atk": our_bp.atk, "def": our_bp.defense, "spa": our_bp.spa, 
                       "spd": our_bp.spd, "spe": our_bp.spe},
                moves=moveset
            )
            self.state.our_side.team.append(our_pkmn)
        
        for i, idx in enumerate(opponent_indices):
            data = pokemon_data[idx]
            
            # Create BattlePokemon for opponent team
            opp_bp = BattlePokemon(
                species=data["species"],
                level=50,
                types=data["types"],
                base_hp=data["stats"]["hp"],
                base_atk=data["stats"]["atk"],
                base_def=data["stats"]["def"],
                base_spa=data["stats"]["spa"],
                base_spd=data["stats"]["spd"],
                base_spe=data["stats"]["spe"],
                ability=data.get("ability", "No Ability")
            )
            self.opp_team.append(opp_bp)
            
            # Get moveset for this Pokemon
            moveset = get_moveset(data["types"])
            
            opp_pkmn = Pokemon(
                species=data["species"],
                level=50,
                hp=opp_bp.max_hp,
                max_hp=opp_bp.max_hp,
                status="",
                active=(i == 0),
                stats={"atk": opp_bp.atk, "def": opp_bp.defense, "spa": opp_bp.spa, 
                       "spd": opp_bp.spd, "spe": opp_bp.spe},
                moves=moveset
            )
            self.state.opponent_side.team.append(opp_pkmn)
        
        # Set active Pokemon (first in team)
        self.state.our_side.active_pokemon = [0]
        self.state.opponent_side.active_pokemon = [0]
        self.our_active_idx = 0
        self.opp_active_idx = 0
        
        # Create move database with all moves
        self.move_database: Dict[str, Move] = {}
        
        # Add all type-based moves
        for move_type, move_data in moves_db.items():
            self.move_database[move_data["name"]] = Move(
                name=move_data["name"],
                type=move_data["type"],
                category=move_data["category"],
                base_power=move_data["power"],
                accuracy=move_data["accuracy"],
                pp=15,
                max_pp=15
            )
        
        # Add coverage moves
        for move_name, move_data in coverage_moves.items():
            if move_data["name"] not in self.move_database:
                self.move_database[move_data["name"]] = Move(
                    name=move_data["name"],
                    type=move_data["type"],
                    category=move_data["category"],
                    base_power=move_data["power"],
                    accuracy=move_data["accuracy"],
                    pp=15,
                    max_pp=15
                )
        
        # Add stat-changing moves
        for move_name, move_data in stat_moves.items():
            if move_data["name"] not in self.move_database:
                self.move_database[move_data["name"]] = Move(
                    name=move_data["name"],
                    type=move_data["type"],
                    category=move_data["category"],
                    base_power=move_data["power"],
                    accuracy=move_data["accuracy"],
                    pp=20,  # Status moves typically have more PP
                    max_pp=20,
                    boosts=move_data.get("boosts")  # Get stat boosts if present
                )
    
    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        """
        Execute one step in the environment.
        
        Args:
            action: Action to take (0-8)
            
        Returns:
            observation: New observation
            reward: Reward for this step
            terminated: Whether episode ended (win/loss)
            truncated: Whether episode was truncated (max turns)
            info: Additional information
        """
        if self.state is None:
            raise RuntimeError("Call reset() before step()")
        
        # Execute action in battle state
        reward = self._execute_action(action)
        
        # Check if battle is over
        terminated = self._is_terminated()
        truncated = self.turn_count >= self.max_turns
        
        # Add win/loss reward
        if terminated:
            our_alive = self.state.our_side.count_alive()
            opp_alive = self.state.opponent_side.count_alive()
            
            if our_alive > opp_alive:
                reward += 5.0  # Win bonus
            elif opp_alive > our_alive:
                reward -= 5.0  # Loss penalty
        
        # Get new observation
        observation = self._get_observation()
        info = self._get_info()
        
        self.turn_count += 1
        
        return observation, reward, terminated, truncated, info
    
    def _execute_action(self, action: int) -> float:
        """
        Execute an action using accurate Pokemon Showdown battle mechanics.
        
        Args:
            action: Action index (0-3 for moves, 4-8 for switches)
            
        Returns:
            Immediate reward for this action
        """
        if not self.state:
            return 0.0
        
        reward = 0.0
        
        # Get current battle Pokemon
        our_bp = self.our_team[self.our_active_idx]
        opp_bp = self.opp_team[self.opp_active_idx]
        
        # Get state Pokemon for tracking
        our_pokemon = self.state.get_our_active_pokemon()
        opp_pokemon = self.state.get_opponent_active_pokemon()
        
        if not our_bp or not opp_bp or not our_pokemon or not opp_pokemon:
            return 0.0
        
        # Store HP before action
        our_hp_before = our_bp.current_hp
        opp_hp_before = opp_bp.current_hp
        
        # Get moves for active Pokemon
        our_moves = self._get_pokemon_moves(our_bp, our_pokemon)
        opp_moves = self._get_pokemon_moves(opp_bp, opp_pokemon)
        
        if action < 4:  # Move action
            if action >= len(our_moves):
                # Invalid move, use first move
                action = 0
            
            our_move = our_moves[action]
            
            # Opponent chooses random move
            opp_move = random.choice(opp_moves) if opp_moves else our_moves[0]
            
            # Simulate turn using accurate battle mechanics
            logs = self.simulator.simulate_turn(
                our_bp, our_move,
                opp_bp, opp_move
            )
            
            # Calculate rewards based on battle results
            our_hp_after = our_bp.current_hp
            opp_hp_after = opp_bp.current_hp
            
            # Reward for damage dealt
            damage_dealt = opp_hp_before - opp_hp_after
            if damage_dealt > 0:
                reward += damage_dealt / 100.0
            
            # Penalty for damage taken
            damage_taken = our_hp_before - our_hp_after
            if damage_taken > 0:
                reward -= damage_taken / 100.0
            
            # Big reward for KO
            if opp_bp.fainted:
                reward += 2.0
                
                # Switch opponent to next Pokemon
                self.opp_active_idx = self._get_next_alive_idx(self.opp_team, self.opp_active_idx)
                if self.opp_active_idx >= 0:
                    # Update state tracking
                    for i, p in enumerate(self.state.opponent_side.team):
                        p.active = (i == self.opp_active_idx)
                    self.state.opponent_side.active_pokemon = [self.opp_active_idx]
                    opp_pokemon = self.state.opponent_side.team[self.opp_active_idx]
                    opp_bp = self.opp_team[self.opp_active_idx]
            
            # Big penalty if we faint
            if our_bp.fainted:
                reward -= 2.0
                
                # Force switch to next Pokemon
                self.our_active_idx = self._get_next_alive_idx(self.our_team, self.our_active_idx)
                if self.our_active_idx >= 0:
                    # Update state tracking
                    for i, p in enumerate(self.state.our_side.team):
                        p.active = (i == self.our_active_idx)
                    self.state.our_side.active_pokemon = [self.our_active_idx]
                    our_pokemon = self.state.our_side.team[self.our_active_idx]
                    our_bp = self.our_team[self.our_active_idx]
            
            # Sync HP between battle sim and state tracking
            our_pokemon.hp = our_bp.current_hp
            our_pokemon.max_hp = our_bp.max_hp
            our_pokemon.fainted = our_bp.fainted
            opp_pokemon.hp = opp_bp.current_hp
            opp_pokemon.max_hp = opp_bp.max_hp
            opp_pokemon.fainted = opp_bp.fainted
        
        else:  # Switch action
            switch_idx = action - 3  # Convert action 4-8 to indices 1-5
            if switch_idx < len(self.our_team):
                target_bp = self.our_team[switch_idx]
                target_pokemon = self.state.our_side.team[switch_idx]
                
                if not target_bp.fainted and switch_idx != self.our_active_idx:
                    # Perform switch
                    self.our_active_idx = switch_idx
                    
                    # Update state tracking
                    for i, p in enumerate(self.state.our_side.team):
                        p.active = (i == switch_idx)
                    self.state.our_side.active_pokemon = [switch_idx]
                    
                    # Small penalty for switching
                    reward -= 0.1
                    
                    # Opponent gets free hit with random move
                    opp_moves = self._get_pokemon_moves(opp_bp, opp_pokemon)
                    opp_move = random.choice(opp_moves) if opp_moves else self.move_database.get("Tackle")
                    
                    # Just apply opponent's move
                    log = self.simulator.use_move(opp_bp, target_bp, opp_move)
                    
                    damage_taken = log.get('damage', 0)
                    if damage_taken > 0:
                        reward -= damage_taken / 100.0
                    
                    # Sync HP
                    target_pokemon.hp = target_bp.current_hp
                    target_pokemon.fainted = target_bp.fainted
                    
                    if target_bp.fainted:
                        reward -= 2.0
                else:
                    # Invalid switch, small penalty
                    reward -= 0.5
        
        # Small penalty per turn to encourage finishing quickly
        reward -= 0.01
        
        return reward
    
    def _get_pokemon_moves(self, battle_pokemon: BattlePokemon, state_pokemon: Pokemon) -> List[Move]:
        """Get Move objects for a Pokemon based on its types."""
        moves = []
        
        # Get moves from state pokemon
        for move_name in state_pokemon.moves[:4]:  # Max 4 moves
            if move_name in self.move_database:
                moves.append(self.move_database[move_name])
        
        # If no moves found, add Tackle as default
        if not moves and "Tackle" in self.move_database:
            moves.append(self.move_database["Tackle"])
        
        return moves
    
    def _get_next_alive_idx(self, team: List[BattlePokemon], current_idx: int) -> int:
        """Get index of next alive Pokemon in team."""
        for i in range(len(team)):
            if i != current_idx and not team[i].fainted:
                return i
        return -1  # No alive Pokemon
    
    def _get_observation(self) -> np.ndarray:
        """
        Get current observation as feature vector.
        
        Returns:
            Feature vector representing current state
        """
        if not self.state:
            return np.zeros(200, dtype=np.float32)
        
        features = []
        
        # Our active Pokemon features (50 features)
        our_pokemon = self.state.get_our_active_pokemon()
        if our_pokemon:
            features.extend(self._encode_pokemon(our_pokemon))
        else:
            features.extend([0.0] * 50)
        
        # Opponent active Pokemon features (50 features)
        opp_pokemon = self.state.get_opponent_active_pokemon()
        if opp_pokemon:
            features.extend(self._encode_pokemon(opp_pokemon))
        else:
            features.extend([0.0] * 50)
        
        # Field conditions (20 features)
        features.extend(self._encode_field())
        
        # Our team summary (40 features)
        features.extend(self._encode_team(self.state.our_side))
        
        # Opponent team summary (40 features)
        features.extend(self._encode_team(self.state.opponent_side))
        
        return np.array(features, dtype=np.float32)
    
    def _encode_pokemon(self, pokemon: Pokemon) -> list:
        """
        Encode a Pokemon as feature vector.
        
        Returns:
            List of 50 features representing the Pokemon
        """
        features = [
            pokemon.hp / pokemon.max_hp if pokemon.max_hp > 0 else 0.0,  # HP ratio
            float(pokemon.level) / 100.0,  # Normalized level
            float(pokemon.active),  # Is active
            float(pokemon.fainted),  # Is fainted
        ]
        
        # Status (one-hot encoding for common statuses)
        status_encoding = [0.0] * 6
        status_map = {"brn": 0, "par": 1, "psn": 2, "tox": 3, "slp": 4, "frz": 5}
        if pokemon.status in status_map:
            status_encoding[status_map[pokemon.status]] = 1.0
        features.extend(status_encoding)
        
        # Stats (normalized by typical max)
        for stat in ["atk", "def", "spa", "spd", "spe"]:
            features.append(pokemon.stats.get(stat, 100) / 300.0)
        
        # Boosts
        for stat in ["atk", "def", "spa", "spd", "spe", "accuracy", "evasion"]:
            features.append((pokemon.boosts.get(stat, 0) + 6) / 12.0)  # Normalize -6 to +6
        
        # Number of moves known (normalized)
        features.append(len(pokemon.moves) / 4.0)
        
        # Pad to 50 features
        while len(features) < 50:
            features.append(0.0)
        
        return features[:50]
    
    def _encode_field(self) -> list:
        """
        Encode field conditions.
        
        Returns:
            List of 20 features
        """
        if not self.state:
            return [0.0] * 20
        
        features = [
            float(self.state.field.trick_room),
            float(self.state.field.gravity),
            float(self.state.field.magic_room),
            float(self.state.field.wonder_room),
        ]
        
        # Weather (one-hot)
        weather_map = {"": 0, "sunnyday": 1, "raindance": 2, "sandstorm": 3, "hail": 4}
        weather_encoding = [0.0] * 5
        weather_idx = weather_map.get(self.state.field.weather, 0)
        weather_encoding[weather_idx] = 1.0
        features.extend(weather_encoding)
        
        # Terrain (one-hot)
        terrain_map = {"": 0, "electricterrain": 1, "grassyterrain": 2, "mistyterrain": 3, "psychicterrain": 4}
        terrain_encoding = [0.0] * 5
        terrain_idx = terrain_map.get(self.state.field.terrain, 0)
        terrain_encoding[terrain_idx] = 1.0
        features.extend(terrain_encoding)
        
        # Pad to 20
        while len(features) < 20:
            features.append(0.0)
        
        return features[:20]
    
    def _encode_team(self, side) -> list:
        """
        Encode team summary.
        
        Returns:
            List of 40 features
        """
        features = [
            float(side.count_alive()) / 6.0,  # Fraction of team alive
            float(len(side.team)) / 6.0,  # Team size
        ]
        
        # Side conditions
        features.extend([
            float(side.spikes) / 3.0,
            float(side.toxic_spikes) / 2.0,
            float(side.stealth_rock),
            float(side.sticky_web),
            float(side.light_screen) / 8.0,
            float(side.reflect) / 8.0,
            float(side.aurora_veil) / 8.0,
            float(side.tailwind) / 8.0,
        ])
        
        # Average team HP
        alive_pokemon = side.get_alive_pokemon()
        if alive_pokemon:
            avg_hp = sum(p.hp_percent for p in alive_pokemon) / len(alive_pokemon)
            features.append(avg_hp / 100.0)
        else:
            features.append(0.0)
        
        # Pad to 40
        while len(features) < 40:
            features.append(0.0)
        
        return features[:40]
    
    def _is_terminated(self) -> bool:
        """Check if battle is over."""
        if not self.state:
            return False
        
        # Battle ends when one side has no Pokemon left
        our_alive = self.state.our_side.count_alive()
        opp_alive = self.state.opponent_side.count_alive()
        
        # Only terminate if at least one team is initialized and has 0 alive
        teams_initialized = len(self.state.our_side.team) > 0 and len(self.state.opponent_side.team) > 0
        
        if not teams_initialized:
            return False
        
        return our_alive == 0 or opp_alive == 0
    
    def _get_info(self) -> Dict[str, Any]:
        """Get additional information."""
        info = {
            "turn": self.turn_count,
        }
        
        if self.state:
            info["our_alive"] = self.state.our_side.count_alive()
            info["opp_alive"] = self.state.opponent_side.count_alive()
            
            our_pokemon = self.state.get_our_active_pokemon()
            if our_pokemon:
                info["our_hp"] = our_pokemon.hp_percent
            
            opp_pokemon = self.state.get_opponent_active_pokemon()
            if opp_pokemon:
                info["opp_hp"] = opp_pokemon.hp_percent
        
        return info
    
    def render(self):
        """Render the environment."""
        if self.render_mode == "ansi":
            return self._render_ansi()
        elif self.render_mode == "human":
            print(self._render_ansi())
    
    def _render_ansi(self) -> str:
        """Render as ANSI string."""
        if not self.state:
            return "Battle not started"
        
        lines = []
        lines.append(f"=== Turn {self.turn_count} ===")
        
        our_pokemon = self.state.get_our_active_pokemon()
        opp_pokemon = self.state.get_opponent_active_pokemon()
        
        if our_pokemon:
            lines.append(f"Our Pokemon: {our_pokemon.species} (HP: {our_pokemon.hp}/{our_pokemon.max_hp})")
        
        if opp_pokemon:
            lines.append(f"Opponent Pokemon: {opp_pokemon.species} (HP: {opp_pokemon.hp}/{opp_pokemon.max_hp})")
        
        lines.append(f"Our team alive: {self.state.our_side.count_alive()}/6")
        lines.append(f"Opponent team alive: {self.state.opponent_side.count_alive()}/6")
        
        return "\n".join(lines)
    
    def close(self):
        """Clean up resources."""
        pass
