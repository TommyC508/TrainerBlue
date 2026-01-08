"""
Web-based Battle Visualizer using Flask
Display Pokemon battles in a web browser with real-time updates
"""
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import sys
import json
from pathlib import Path
sys.path.append('/workspaces/Black')

from src.battle.simulator import BattlePokemon, BattleSimulator, Move
from typing import Optional, Dict, List

app = Flask(__name__, 
            template_folder='/workspaces/Black/src/graphics/templates',
            static_folder='/workspaces/Black/src/graphics/static')
CORS(app)

class BattleState:
    """Stores current battle state for web display"""
    def __init__(self):
        self.player_pokemon: Optional[BattlePokemon] = None
        self.opponent_pokemon: Optional[BattlePokemon] = None
        self.messages: List[str] = []
        self.turn: int = 0
        self.battle_over: bool = False
        self.winner: Optional[str] = None
        self.simulator = BattleSimulator()
    
    def reset(self):
        """Reset battle state"""
        self.messages = []
        self.turn = 0
        self.battle_over = False
        self.winner = None
    
    def add_message(self, message: str):
        """Add a message to the battle log"""
        self.messages.append(message)
        # Keep only last 10 messages
        if len(self.messages) > 10:
            self.messages = self.messages[-10:]
    
    def to_dict(self) -> Dict:
        """Convert battle state to dictionary for JSON"""
        return {
            'turn': self.turn,
            'battle_over': self.battle_over,
            'winner': self.winner,
            'messages': self.messages,
            'player': self._pokemon_to_dict(self.player_pokemon) if self.player_pokemon else None,
            'opponent': self._pokemon_to_dict(self.opponent_pokemon) if self.opponent_pokemon else None,
        }
    
    def _pokemon_to_dict(self, pokemon: BattlePokemon) -> Dict:
        """Convert Pokemon to dictionary"""
        return {
            'species': pokemon.species,
            'level': pokemon.level,
            'hp': pokemon.current_hp,
            'max_hp': pokemon.max_hp,
            'hp_percent': int((pokemon.current_hp / pokemon.max_hp) * 100) if pokemon.max_hp > 0 else 0,
            'types': pokemon.types,
            'ability': pokemon.ability,
            'status': pokemon.status_state.id if pokemon.status_state else None,
            'fainted': pokemon.fainted,
            'boosts': {
                'atk': pokemon.boosts.get('atk', 0),
                'defense': pokemon.boosts.get('defense', 0),
                'spa': pokemon.boosts.get('spa', 0),
                'spd': pokemon.boosts.get('spd', 0),
                'spe': pokemon.boosts.get('spe', 0),
            }
        }

# Global battle state
battle_state = BattleState()

@app.route('/')
def index():
    """Main battle display page"""
    return render_template('battle.html')

@app.route('/api/battle/state')
def get_battle_state():
    """Get current battle state as JSON"""
    return jsonify(battle_state.to_dict())

@app.route('/api/battle/start', methods=['POST'])
def start_battle():
    """Start a new battle"""
    battle_state.reset()
    
    # Create demo Pokemon
    battle_state.player_pokemon = BattlePokemon(
        species="Machamp",
        level=50,
        types=["Fighting"],
        base_hp=90, base_atk=130, base_def=80,
        base_spa=65, base_spd=85, base_spe=55,
        ability="Guts"
    )
    
    battle_state.opponent_pokemon = BattlePokemon(
        species="Gyarados",
        level=50,
        types=["Water", "Flying"],
        base_hp=95, base_atk=125, base_def=79,
        base_spa=60, base_spd=100, base_spe=81,
        ability="Intimidate"
    )
    
    battle_state.add_message("Battle started!")
    battle_state.add_message(f"Go! {battle_state.player_pokemon.species}!")
    battle_state.add_message(f"Enemy {battle_state.opponent_pokemon.species} appeared!")
    
    return jsonify({'success': True, 'state': battle_state.to_dict()})

@app.route('/api/battle/action', methods=['POST'])
def perform_action():
    """Perform a battle action"""
    data = request.json
    action = data.get('action')
    
    if not battle_state.player_pokemon or not battle_state.opponent_pokemon:
        return jsonify({'error': 'Battle not started'}), 400
    
    if battle_state.battle_over:
        return jsonify({'error': 'Battle is over'}), 400
    
    battle_state.turn += 1
    
    if action == 'intimidate':
        # Gyarados switches in with Intimidate
        battle_state.simulator.apply_switch_in_abilities(
            battle_state.opponent_pokemon, 
            battle_state.player_pokemon
        )
        battle_state.add_message(f"{battle_state.opponent_pokemon.species}'s Intimidate!")
        battle_state.add_message(f"{battle_state.player_pokemon.species}'s Attack fell!")
    
    elif action == 'bulk_up':
        # Machamp uses Bulk Up
        battle_state.player_pokemon.boost_by({"atk": 1, "defense": 1})
        battle_state.add_message(f"{battle_state.player_pokemon.species} used Bulk Up!")
        battle_state.add_message("Attack and Defense rose!")
    
    elif action == 'dragon_dance':
        # Gyarados uses Dragon Dance
        battle_state.opponent_pokemon.boost_by({"atk": 1, "spe": 1})
        battle_state.add_message(f"{battle_state.opponent_pokemon.species} used Dragon Dance!")
        battle_state.add_message("Attack and Speed rose!")
    
    elif action == 'waterfall':
        # Gyarados uses Waterfall
        move = Move(
            name="Waterfall",
            type="Water",
            category="Physical",
            base_power=80,
            accuracy=100,
            pp=15,
            max_pp=15
        )
        damage, effectiveness, crit = battle_state.simulator.calculate_move_damage(
            battle_state.opponent_pokemon,
            battle_state.player_pokemon,
            move
        )
        battle_state.player_pokemon.take_damage(damage)
        battle_state.add_message(f"{battle_state.opponent_pokemon.species} used Waterfall!")
        battle_state.add_message(f"Dealt {damage} damage!")
        if crit:
            battle_state.add_message("Critical hit!")
    
    elif action == 'close_combat':
        # Machamp uses Close Combat
        move = Move(
            name="Close Combat",
            type="Fighting",
            category="Physical",
            base_power=120,
            accuracy=100,
            pp=5,
            max_pp=5
        )
        damage, effectiveness, crit = battle_state.simulator.calculate_move_damage(
            battle_state.player_pokemon,
            battle_state.opponent_pokemon,
            move
        )
        battle_state.opponent_pokemon.take_damage(damage)
        battle_state.add_message(f"{battle_state.player_pokemon.species} used Close Combat!")
        battle_state.add_message(f"Dealt {damage} damage!")
        if crit:
            battle_state.add_message("Critical hit!")
    
    # Check for fainted Pokemon
    if battle_state.player_pokemon.fainted:
        battle_state.add_message(f"{battle_state.player_pokemon.species} fainted!")
        battle_state.add_message(f"{battle_state.opponent_pokemon.species} wins!")
        battle_state.battle_over = True
        battle_state.winner = "opponent"
    elif battle_state.opponent_pokemon.fainted:
        battle_state.add_message(f"{battle_state.opponent_pokemon.species} fainted!")
        battle_state.add_message(f"{battle_state.player_pokemon.species} wins!")
        battle_state.battle_over = True
        battle_state.winner = "player"
    
    return jsonify({'success': True, 'state': battle_state.to_dict()})

@app.route('/api/battle/reset', methods=['POST'])
def reset_battle():
    """Reset the battle"""
    battle_state.reset()
    battle_state.player_pokemon = None
    battle_state.opponent_pokemon = None
    return jsonify({'success': True})

if __name__ == '__main__':
    # Create directories if they don't exist
    Path('/workspaces/Black/src/graphics/templates').mkdir(parents=True, exist_ok=True)
    Path('/workspaces/Black/src/graphics/static').mkdir(parents=True, exist_ok=True)
    
    print("\n" + "="*60)
    print("🎮 Pokemon Battle Web Server Starting!")
    print("="*60)
    print("\n📺 Open your browser to: http://localhost:5000")
    print("\n✨ Battle visualizer ready!\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
