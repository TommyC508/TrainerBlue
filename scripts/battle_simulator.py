#!/usr/bin/env python3
"""
Interactive battle simulator with detailed logging.
Plays out a full Pokemon battle with two AI agents battling each other.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.data.models import Pokemon
from src.agents.heuristic_agent import HeuristicAgent
from src.agents.random_agent import RandomAgent
from src.battle.state import BattleState
from src.data.type_effectiveness import get_type_effectiveness
import random
import time


def create_battle_team(team_name: str) -> list[Pokemon]:
    """Create competitive Pokemon teams."""
    teams = {
        "player": [
            Pokemon(
                species="Charizard",
                level=50,
                hp=153,
                max_hp=153,
                moves=["flamethrower", "airslash", "dragonpulse", "roost"],
                ability="Blaze",
                active=True,
                stats={"atk": 104, "def": 98, "spa": 129, "spd": 105, "spe": 120}
            ),
            Pokemon(
                species="Blastoise",
                level=50,
                hp=158,
                max_hp=158,
                moves=["surf", "icebeam", "darkpulse", "rapidspin"],
                ability="Torrent",
                stats={"atk": 103, "def": 120, "spa": 105, "spd": 125, "spe": 98}
            ),
            Pokemon(
                species="Venusaur",
                level=50,
                hp=155,
                max_hp=155,
                moves=["gigadrain", "sludgebomb", "earthpower", "synthesis"],
                ability="Overgrow",
                stats={"atk": 102, "def": 103, "spa": 120, "spd": 120, "spe": 100}
            ),
        ],
        "opponent": [
            Pokemon(
                species="Tyranitar",
                level=50,
                hp=175,
                max_hp=175,
                moves=["stoneedge", "crunch", "earthquake", "dragondance"],
                ability="Sand Stream",
                active=True,
                stats={"atk": 154, "def": 130, "spa": 115, "spd": 120, "spe": 81}
            ),
            Pokemon(
                species="Alakazam",
                level=50,
                hp=130,
                max_hp=130,
                moves=["psychic", "shadowball", "focusblast", "calmmind"],
                ability="Magic Guard",
                stats={"atk": 70, "def": 65, "spa": 155, "spd": 105, "spe": 140}
            ),
            Pokemon(
                species="Machamp",
                level=50,
                hp=165,
                max_hp=165,
                moves=["closecombat", "stoneedge", "knockoff", "bulletpunch"],
                ability="Guts",
                stats={"atk": 150, "def": 100, "spa": 85, "spd": 105, "spe": 75}
            ),
        ],
    }
    return teams[team_name]


def get_pokemon_types(species: str) -> list[str]:
    """Get types for a Pokemon species."""
    type_chart = {
        "Charizard": ["Fire", "Flying"],
        "Blastoise": ["Water"],
        "Venusaur": ["Grass", "Poison"],
        "Tyranitar": ["Rock", "Dark"],
        "Alakazam": ["Psychic"],
        "Machamp": ["Fighting"],
    }
    return type_chart.get(species, ["Normal"])


def get_move_data(move_id: str) -> dict:
    """Get move data for damage calculation."""
    moves_db = {
        "flamethrower": {"name": "Flamethrower", "type": "Fire", "category": "Special", "power": 90, "accuracy": 100},
        "airslash": {"name": "Air Slash", "type": "Flying", "category": "Special", "power": 75, "accuracy": 95},
        "dragonpulse": {"name": "Dragon Pulse", "type": "Dragon", "category": "Special", "power": 85, "accuracy": 100},
        "roost": {"name": "Roost", "type": "Flying", "category": "Status", "power": 0, "accuracy": 100},
        "surf": {"name": "Surf", "type": "Water", "category": "Special", "power": 90, "accuracy": 100},
        "icebeam": {"name": "Ice Beam", "type": "Ice", "category": "Special", "power": 90, "accuracy": 100},
        "darkpulse": {"name": "Dark Pulse", "type": "Dark", "category": "Special", "power": 80, "accuracy": 100},
        "rapidspin": {"name": "Rapid Spin", "type": "Normal", "category": "Physical", "power": 50, "accuracy": 100},
        "gigadrain": {"name": "Giga Drain", "type": "Grass", "category": "Special", "power": 75, "accuracy": 100},
        "sludgebomb": {"name": "Sludge Bomb", "type": "Poison", "category": "Special", "power": 90, "accuracy": 100},
        "earthpower": {"name": "Earth Power", "type": "Ground", "category": "Special", "power": 90, "accuracy": 100},
        "synthesis": {"name": "Synthesis", "type": "Grass", "category": "Status", "power": 0, "accuracy": 100},
        "stoneedge": {"name": "Stone Edge", "type": "Rock", "category": "Physical", "power": 100, "accuracy": 80},
        "crunch": {"name": "Crunch", "type": "Dark", "category": "Physical", "power": 80, "accuracy": 100},
        "earthquake": {"name": "Earthquake", "type": "Ground", "category": "Physical", "power": 100, "accuracy": 100},
        "dragondance": {"name": "Dragon Dance", "type": "Dragon", "category": "Status", "power": 0, "accuracy": 100},
        "psychic": {"name": "Psychic", "type": "Psychic", "category": "Special", "power": 90, "accuracy": 100},
        "shadowball": {"name": "Shadow Ball", "type": "Ghost", "category": "Special", "power": 80, "accuracy": 100},
        "focusblast": {"name": "Focus Blast", "type": "Fighting", "category": "Special", "power": 120, "accuracy": 70},
        "calmmind": {"name": "Calm Mind", "type": "Psychic", "category": "Status", "power": 0, "accuracy": 100},
        "closecombat": {"name": "Close Combat", "type": "Fighting", "category": "Physical", "power": 120, "accuracy": 100},
        "knockoff": {"name": "Knock Off", "type": "Dark", "category": "Physical", "power": 65, "accuracy": 100},
        "bulletpunch": {"name": "Bullet Punch", "type": "Steel", "category": "Physical", "power": 40, "accuracy": 100},
    }
    return moves_db.get(move_id, {"name": move_id, "type": "Normal", "category": "Physical", "power": 50, "accuracy": 100})


def print_separator(char="=", length=80):
    """Print a separator line."""
    print(char * length)


def print_hp_bar(pokemon: Pokemon, width=30):
    """Print a colored HP bar."""
    hp_percent = (pokemon.hp / pokemon.max_hp) * 100
    filled = int((hp_percent / 100) * width)
    empty = width - filled
    
    # Color coding
    if hp_percent > 50:
        color = "\033[92m"  # Green
    elif hp_percent > 20:
        color = "\033[93m"  # Yellow
    else:
        color = "\033[91m"  # Red
    reset = "\033[0m"
    
    bar = color + "█" * filled + reset + "░" * empty
    return f"{bar} {pokemon.hp}/{pokemon.max_hp} HP ({hp_percent:.1f}%)"


def print_battle_state(state: BattleState, turn: int):
    """Print the current battle state."""
    print("\n")
    print_separator("=")
    print(f"⚔️  TURN {turn}")
    print_separator("=")
    
    # Get active Pokemon
    p1_active = None
    p2_active = None
    
    for mon in state.our_side.team:
        if mon.active and not mon.fainted:
            p1_active = mon
            break
    
    for mon in state.opponent_side.team:
        if mon.active and not mon.fainted:
            p2_active = mon
            break
    
    if p1_active and p2_active:
        p1_types = get_pokemon_types(p1_active.species)
        p2_types = get_pokemon_types(p2_active.species)
        
        print(f"\n🔵 Player 1: {p1_active.species} [{'/'.join(p1_types)}]")
        print(f"   {print_hp_bar(p1_active)}")
        
        print(f"\n🔴 Player 2: {p2_active.species} [{'/'.join(p2_types)}]")
        print(f"   {print_hp_bar(p2_active)}")
    
    # Show full teams
    print(f"\n🔵 PLAYER 1 TEAM:")
    for i, mon in enumerate(state.our_side.team, 1):
        status = "⚔️  ACTIVE" if mon.active else "💀 FAINTED" if mon.fainted else "   Benched"
        print(f"   {status} │ {mon.species:12} │ HP: {mon.hp:3}/{mon.max_hp:3}")
    
    print(f"\n🔴 PLAYER 2 TEAM:")
    for i, mon in enumerate(state.opponent_side.team, 1):
        status = "⚔️  ACTIVE" if mon.active else "💀 FAINTED" if mon.fainted else "   Benched"
        print(f"   {status} │ {mon.species:12} │ HP: {mon.hp:3}/{mon.max_hp:3}")


def execute_move(attacker: Pokemon, defender: Pokemon, move_id: str, attacker_name: str, defender_name: str) -> int:
    """Execute a move and return damage dealt."""
    move_data = get_move_data(move_id)
    
    print(f"\n   💬 {attacker_name} used {move_data['name']}!")
    
    # Status moves
    if move_data['power'] == 0:
        if 'roost' in move_id or 'synthesis' in move_id:
            heal = min(attacker.max_hp // 2, attacker.max_hp - attacker.hp)
            attacker.hp += heal
            print(f"   💚 {attacker_name} restored {heal} HP!")
        else:
            print(f"   ✨ {attacker_name}'s stats changed!")
        return 0
    
    # Check accuracy
    if random.randint(1, 100) > move_data['accuracy']:
        print(f"   ❌ The attack missed!")
        return 0
    
    # Calculate type effectiveness (pass all types at once)
    defender_types = get_pokemon_types(defender.species)
    effectiveness = get_type_effectiveness(move_data['type'], defender_types)
    
    # Calculate damage
    if move_data['category'] == "Physical":
        attack = attacker.stats['atk']
        defense = defender.stats['def']
    else:
        attack = attacker.stats['spa']
        defense = defender.stats['spd']
    
    # Simplified damage formula
    level = attacker.level
    power = move_data['power']
    damage = ((2 * level / 5 + 2) * power * (attack / defense) / 50 + 2)
    damage = int(damage * effectiveness * random.uniform(0.85, 1.0))
    damage = min(damage, defender.hp)
    
    # Apply damage
    defender.hp -= damage
    
    # Print effectiveness message
    if effectiveness > 1.5:
        print(f"   💥 It's super effective!")
    elif effectiveness > 1.0:
        print(f"   ⚡ It's super effective!")
    elif effectiveness < 0.5:
        print(f"   🛡️  It's not very effective...")
    elif effectiveness < 1.0:
        print(f"   🛡️  It's not very effective...")
    elif effectiveness == 0:
        print(f"   🚫 It doesn't affect {defender_name}...")
        return 0
    
    print(f"   💢 Dealt {damage} damage! ({effectiveness}x type effectiveness)")
    print(f"   {defender_name}: {print_hp_bar(defender)}")
    
    if defender.hp <= 0:
        defender.fainted = True
        defender.active = False
        print(f"   💀 {defender_name}'s {defender.species} fainted!")
    
    return damage


def ai_choose_switch(team: list[Pokemon], agent_name: str) -> int:
    """Choose which Pokemon to switch to."""
    alive = [(i, mon) for i, mon in enumerate(team) if not mon.fainted and not mon.active]
    if not alive:
        return -1
    
    # Pick the first alive Pokemon
    idx, mon = alive[0]
    print(f"   🔄 {agent_name} sent out {mon.species}!")
    return idx


def simulate_battle():
    """Simulate a full battle between two AI agents."""
    print("\n" + "="*80)
    print("🎮 POKEMON BATTLE SIMULATOR")
    print("="*80)
    print("\n🤖 Player 1: HeuristicAgent (Smart tactical AI)")
    print("🤖 Player 2: HeuristicAgent (Smart tactical AI)")
    print("\n   🧠 BATTLE OF THE MINDS - Two strategic AIs face off!")
    print("\n" + "="*80)
    
    input("\n⏸️  Press Enter to start the battle...")
    
    # Create battle state
    state = BattleState(our_player_id="p1")
    state.our_side.team = create_battle_team("player")
    state.opponent_side.team = create_battle_team("opponent")
    state.started = True
    
    # Create agents
    agent1 = HeuristicAgent()
    agent2 = HeuristicAgent()
    
    turn = 1
    max_turns = 50
    
    while turn <= max_turns:
        print_battle_state(state, turn)
        
        # Check for battle end
        p1_alive = sum(1 for mon in state.our_side.team if not mon.fainted)
        p2_alive = sum(1 for mon in state.opponent_side.team if not mon.fainted)
        
        if p1_alive == 0:
            print("\n" + "="*80)
            print("🏆 PLAYER 2 WINS!")
            print("="*80)
            break
        
        if p2_alive == 0:
            print("\n" + "="*80)
            print("🏆 PLAYER 1 WINS!")
            print("="*80)
            break
        
        # Get active Pokemon
        p1_active = next((mon for mon in state.our_side.team if mon.active and not mon.fainted), None)
        p2_active = next((mon for mon in state.opponent_side.team if mon.active and not mon.fainted), None)
        
        # Handle forced switches
        if not p1_active:
            print("\n🔵 Player 1 must switch!")
            idx = ai_choose_switch(state.our_side.team, "Player 1")
            if idx >= 0:
                state.our_side.team[idx].active = True
                p1_active = state.our_side.team[idx]
        
        if not p2_active:
            print("\n🔴 Player 2 must switch!")
            idx = ai_choose_switch(state.opponent_side.team, "Player 2")
            if idx >= 0:
                state.opponent_side.team[idx].active = True
                p2_active = state.opponent_side.team[idx]
        
        if not p1_active or not p2_active:
            break
        
        print("\n" + "-"*80)
        print("⚡ BATTLE PHASE")
        print("-"*80)
        
        # Determine turn order (based on speed)
        if p1_active.stats['spe'] >= p2_active.stats['spe']:
            first, second = (p1_active, "Player 1", agent1, state, p2_active, "Player 2"), \
                           (p2_active, "Player 2", agent2, state, p1_active, "Player 1")
        else:
            first, second = (p2_active, "Player 2", agent2, state, p1_active, "Player 1"), \
                           (p1_active, "Player 1", agent1, state, p2_active, "Player 2")
        
        # First Pokemon moves
        attacker, attacker_name, agent, battle_state, defender, defender_name = first
        print(f"\n🎯 {attacker_name} moves first! (Speed: {attacker.stats['spe']})")
        
        if attacker.active and not attacker.fainted:
            # Choose random move for simplicity
            if attacker.moves:
                move_id = random.choice(attacker.moves)
                execute_move(attacker, defender, move_id, attacker_name, defender_name)
        
        # Check if defender fainted
        if defender.fainted:
            print(f"\n   ⚠️  {defender_name}'s {defender.species} was knocked out!")
            # Auto-switch
            team = state.our_side.team if defender_name == "Player 1" else state.opponent_side.team
            idx = ai_choose_switch(team, defender_name)
            if idx >= 0:
                team[idx].active = True
            else:
                # No more Pokemon
                turn += 1
                continue
        
        # Second Pokemon moves (if still alive)
        attacker, attacker_name, agent, battle_state, defender, defender_name = second
        
        if attacker.active and not attacker.fainted:
            print(f"\n🎯 {attacker_name}'s turn! (Speed: {attacker.stats['spe']})")
            if attacker.moves:
                move_id = random.choice(attacker.moves)
                execute_move(attacker, defender, move_id, attacker_name, defender_name)
        
        # Check if defender fainted
        if defender.fainted:
            print(f"\n   ⚠️  {defender_name}'s {defender.species} was knocked out!")
            team = state.our_side.team if defender_name == "Player 1" else state.opponent_side.team
            idx = ai_choose_switch(team, defender_name)
            if idx >= 0:
                team[idx].active = True
        
        turn += 1
        state.turn = turn
        
        # Pause between turns
        if turn <= max_turns:
            input("\n⏸️  Press Enter for next turn...")
    
    # Battle summary
    print("\n" + "="*80)
    print("📊 BATTLE SUMMARY")
    print("="*80)
    print(f"\nTotal turns: {turn - 1}")
    print(f"\n🔵 Player 1 remaining: {sum(1 for mon in state.our_side.team if not mon.fainted)}/3")
    print(f"🔴 Player 2 remaining: {sum(1 for mon in state.opponent_side.team if not mon.fainted)}/3")
    print("\n" + "="*80)


if __name__ == "__main__":
    simulate_battle()
