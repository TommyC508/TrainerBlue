"""
Demo of accurate Pokemon Showdown battle mechanics.
This demonstrates the battle system using real Pokemon data and damage calculations.
"""
import sys
import os
from typing import List, Dict
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.battle.simulator import BattleSimulator, BattlePokemon, Move
from src.battle.damage_calculator import calculate_stat, calculate_hp


def create_pokemon(species: str, level: int, types: List[str], base_stats: Dict[str, int]) -> BattlePokemon:
    """Helper to create a Pokemon with calculated stats."""
    return BattlePokemon(
        species=species,
        level=level,
        types=types,
        base_hp=base_stats['hp'],
        base_atk=base_stats['atk'],
        base_def=base_stats['def'],
        base_spa=base_stats['spa'],
        base_spd=base_stats['spd'],
        base_spe=base_stats['spe']
    )


def print_pokemon_summary(pokemon: BattlePokemon):
    """Print Pokemon stats."""
    print(f"\n{'=' * 60}")
    print(f"{pokemon.species} (Lv. {pokemon.level}) - {'/'.join(pokemon.types)}")
    print(f"{'=' * 60}")
    print(f"HP:  {pokemon.current_hp}/{pokemon.max_hp} ({pokemon.hp_percentage:.1f}%)")
    print(f"Atk: {pokemon.atk} | Def: {pokemon.defense} | Spe: {pokemon.spe}")
    print(f"SpA: {pokemon.spa} | SpD: {pokemon.spd}")
    if pokemon.status:
        print(f"Status: {pokemon.status.upper()}")
    print(f"{'=' * 60}")


def main():
    """Run battle simulation demo."""
    print("\n" + "=" * 70)
    print(" POKEMON SHOWDOWN ACCURATE BATTLE SIMULATOR")
    print("=" * 70)
    print("\nUsing official Pokemon Showdown damage formula:")
    print("  baseDamage = floor(floor(floor(floor(2*L/5+2) * P * A) / D) / 50)")
    print("\nWith modifiers: Weather, Critical, Random(85-100%), STAB, Type, etc.")
    print("=" * 70)
    
    # Create battle simulator
    simulator = BattleSimulator(gen=9)
    
    # Create two Pokemon with real stats
    # Charizard: Fire/Flying, good special attacker
    charizard = create_pokemon(
        species="Charizard",
        level=50,
        types=["Fire", "Flying"],
        base_stats={'hp': 78, 'atk': 84, 'def': 78, 'spa': 109, 'spd': 85, 'spe': 100}
    )
    
    # Venusaur: Grass/Poison, good special defense
    venusaur = create_pokemon(
        species="Venusaur",
        level=50,
        types=["Grass", "Poison"],
        base_stats={'hp': 80, 'atk': 82, 'def': 83, 'spa': 100, 'spd': 100, 'spe': 80}
    )
    
    print_pokemon_summary(charizard)
    print_pokemon_summary(venusaur)
    
    # Create moves
    flamethrower = Move(
        name="Flamethrower",
        type="Fire",
        category="Special",
        base_power=90,
        accuracy=100,
        pp=15,
        max_pp=15
    )
    
    energy_ball = Move(
        name="Energy Ball",
        type="Grass",
        category="Special",
        base_power=90,
        accuracy=100,
        pp=10,
        max_pp=10
    )
    
    # Simulate turns
    print("\n" + "=" * 70)
    print(" BATTLE START!")
    print("=" * 70)
    
    turn = 0
    while not charizard.fainted and not venusaur.fainted and turn < 10:
        turn += 1
        print(f"\n{'─' * 70}")
        print(f"TURN {turn}")
        print(f"{'─' * 70}")
        
        # Charizard uses Flamethrower (super effective!)
        # Venusaur uses Energy Ball (not very effective)
        logs = simulator.simulate_turn(
            charizard, flamethrower,
            venusaur, energy_ball
        )
        
        # Print action logs
        for log in logs:
            print(f"\n► {' '.join(log['message'])}")
            
            if log['damage'] > 0:
                print(f"   💥 Damage: {log['damage']} HP")
                if log['critical']:
                    print(f"   ⚡ Critical Hit!")
                if log['effectiveness'] != 1.0:
                    print(f"   🎯 Effectiveness: {log['effectiveness']}x")
        
        # Show HP bars
        print(f"\n┌{'─' * 68}┐")
        print(f"│ {charizard.species:20} HP: [{_hp_bar(charizard)}] {charizard.current_hp:>3}/{charizard.max_hp:<3} │")
        print(f"│ {venusaur.species:20} HP: [{_hp_bar(venusaur)}] {venusaur.current_hp:>3}/{venusaur.max_hp:<3} │")
        print(f"└{'─' * 68}┘")
    
    # Battle result
    print("\n" + "=" * 70)
    if charizard.fainted:
        print(f" BATTLE RESULT: {venusaur.species} wins!")
    elif venusaur.fainted:
        print(f" BATTLE RESULT: {charizard.species} wins!")
    else:
        print(" BATTLE RESULT: Draw (turn limit reached)")
    print("=" * 70)
    
    # Final stats
    print("\n📊 Final Statistics:")
    print(f"   • {charizard.species}: {charizard.current_hp}/{charizard.max_hp} HP ({charizard.hp_percentage:.1f}%)")
    print(f"   • {venusaur.species}: {venusaur.current_hp}/{venusaur.max_hp} HP ({venusaur.hp_percentage:.1f}%)")
    print(f"   • Total turns: {turn}")
    print(f"   • Average damage per turn: {(charizard.max_hp - charizard.current_hp + venusaur.max_hp - venusaur.current_hp) / turn:.1f}")
    
    print("\n✅ Battle simulation complete using Pokemon Showdown mechanics!")
    print("=" * 70)


def _hp_bar(pokemon: BattlePokemon, width: int = 20) -> str:
    """Generate a visual HP bar."""
    percentage = pokemon.hp_percentage / 100
    filled = int(width * percentage)
    empty = width - filled
    
    # Color based on HP
    if percentage > 0.5:
        bar = '█' * filled + '░' * empty
    elif percentage > 0.2:
        bar = '▓' * filled + '░' * empty
    else:
        bar = '▒' * filled + '░' * empty
    
    return bar


if __name__ == "__main__":
    main()
