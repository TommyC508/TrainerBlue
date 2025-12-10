"""
Interactive Pokemon battle demo showing both Pokemon clearly.
"""
import sys
sys.path.append('/workspaces/Black')

from src.battle.simulator import BattlePokemon, BattleSimulator, Move

def print_battle_status(pokemon1, pokemon2, turn_number):
    """Display both Pokemon's status side by side."""
    print("\n" + "=" * 80)
    print(f"TURN {turn_number}".center(80))
    print("=" * 80)
    
    # Header
    print(f"\n{'PLAYER 1':<40}{'PLAYER 2':>40}")
    print(f"{pokemon1.species:<40}{pokemon2.species:>40}")
    print("-" * 80)
    
    # HP bars
    hp1_percent = pokemon1.current_hp / pokemon1.max_hp
    hp2_percent = pokemon2.current_hp / pokemon2.max_hp
    
    hp1_bar = "█" * int(hp1_percent * 20) + "░" * (20 - int(hp1_percent * 20))
    hp2_bar = "█" * int(hp2_percent * 20) + "░" * (20 - int(hp2_percent * 20))
    
    print(f"HP: {hp1_bar} {pokemon1.current_hp}/{pokemon1.max_hp:<20}HP: {hp2_bar} {pokemon2.current_hp}/{pokemon2.max_hp:>10}")
    
    # Stats with boosts
    print(f"\nStats (with boosts):{' ' * 21}Stats (with boosts):")
    
    stats = ['atk', 'defense', 'spa', 'spd', 'spe']
    stat_names = {'atk': 'Attack', 'defense': 'Defense', 'spa': 'Sp.Atk', 'spd': 'Sp.Def', 'spe': 'Speed'}
    
    for stat in stats:
        boost1 = pokemon1.boosts.get(stat, 0)
        boost2 = pokemon2.boosts.get(stat, 0)
        
        val1 = pokemon1.get_boosted_stat(stat)
        val2 = pokemon2.get_boosted_stat(stat)
        
        boost1_str = f"(+{boost1})" if boost1 > 0 else f"({boost1})" if boost1 < 0 else ""
        boost2_str = f"(+{boost2})" if boost2 > 0 else f"({boost2})" if boost2 < 0 else ""
        
        line1 = f"  {stat_names[stat]}: {val1} {boost1_str}"
        line2 = f"{stat_names[stat]}: {val2} {boost2_str}"
        print(f"{line1:<40}{line2:>40}")
    
    # Abilities
    print(f"\nAbility: {pokemon1.ability:<31}Ability: {pokemon2.ability:>40}")
    
    # Status
    status1 = pokemon1.status_state.id if pokemon1.status_state else "None"
    status2 = pokemon2.status_state.id if pokemon2.status_state else "None"
    print(f"Status: {status1:<32}Status: {status2:>40}")
    
    print("=" * 80)

def battle_demo():
    """Run an interactive battle demo."""
    print("\n" + "╔" + "=" * 78 + "╗")
    print("║" + "POKEMON BATTLE SIMULATOR - ENHANCED EDITION".center(78) + "║")
    print("╚" + "=" * 78 + "╝")
    
    sim = BattleSimulator()
    
    # Create battling Pokemon
    machamp = BattlePokemon(
        species="Machamp",
        level=50,
        types=["Fighting"],
        base_hp=90, base_atk=130, base_def=80,
        base_spa=65, base_spd=85, base_spe=55,
        ability="Guts"
    )
    
    gyarados = BattlePokemon(
        species="Gyarados",
        level=50,
        types=["Water", "Flying"],
        base_hp=95, base_atk=125, base_def=79,
        base_spa=60, base_spd=100, base_spe=81,
        ability="Intimidate"
    )
    
    # Moves
    bulk_up = Move(
        name="Bulk Up",
        type="Fighting",
        category="Status",
        base_power=0,
        accuracy=-1,
        pp=20,
        max_pp=20,
        boosts={"atk": 1, "def": 1}
    )
    
    close_combat = Move(
        name="Close Combat",
        type="Fighting",
        category="Physical",
        base_power=120,
        accuracy=100,
        pp=5,
        max_pp=5
    )
    
    waterfall = Move(
        name="Waterfall",
        type="Water",
        category="Physical",
        base_power=80,
        accuracy=100,
        pp=15,
        max_pp=15
    )
    
    dragon_dance = Move(
        name="Dragon Dance",
        type="Dragon",
        category="Status",
        base_power=0,
        accuracy=-1,
        pp=20,
        max_pp=20,
        boosts={"atk": 1, "spe": 1}
    )
    
    turn = 0
    
    # Initial state
    print_battle_status(machamp, gyarados, turn)
    input("\nPress Enter to start the battle...")
    
    # Turn 1: Gyarados switches in with Intimidate
    turn += 1
    print("\n>>> GYARADOS switches in!")
    sim.apply_switch_in_abilities(gyarados, machamp)
    print(">>> Intimidate activated! Machamp's Attack fell!")
    print_battle_status(machamp, gyarados, turn)
    input("\nPress Enter for next turn...")
    
    # Turn 2: Machamp uses Bulk Up, Gyarados uses Dragon Dance
    turn += 1
    print("\n>>> MACHAMP uses Bulk Up!")
    machamp.boost_by({"atk": 1, "def": 1})
    print(">>> Machamp's Attack and Defense rose!")
    
    print("\n>>> GYARADOS uses Dragon Dance!")
    gyarados.boost_by({"atk": 1, "spe": 1})
    print(">>> Gyarados's Attack and Speed rose!")
    print_battle_status(machamp, gyarados, turn)
    input("\nPress Enter for next turn...")
    
    # Turn 3: Both attack
    turn += 1
    print("\n>>> GYARADOS uses Waterfall!")
    damage1, eff1, crit1 = sim.calculate_move_damage(gyarados, machamp, waterfall)
    actual_damage1 = machamp.take_damage(damage1)
    print(f">>> Hit for {actual_damage1} damage! {'Critical hit!' if crit1 else ''}")
    
    print("\n>>> MACHAMP uses Close Combat!")
    damage2, eff2, crit2 = sim.calculate_move_damage(machamp, gyarados, close_combat)
    actual_damage2 = gyarados.take_damage(damage2)
    print(f">>> Hit for {actual_damage2} damage! {'Critical hit!' if crit2 else ''}")
    print_battle_status(machamp, gyarados, turn)
    
    if machamp.fainted or gyarados.fainted:
        print("\n" + "=" * 80)
        if machamp.fainted:
            print(f"💀 {machamp.species} fainted! {gyarados.species} wins!")
        else:
            print(f"💀 {gyarados.species} fainted! {machamp.species} wins!")
        print("=" * 80)
    else:
        input("\nPress Enter for next turn...")
        
        # Turn 4: Set up more
        turn += 1
        print("\n>>> MACHAMP uses Bulk Up!")
        machamp.boost_by({"atk": 1, "def": 1})
        print(">>> Machamp's Attack and Defense rose!")
        
        print("\n>>> GYARADOS uses Dragon Dance!")
        gyarados.boost_by({"atk": 1, "spe": 1})
        print(">>> Gyarados's Attack and Speed rose!")
        print_battle_status(machamp, gyarados, turn)
        input("\nPress Enter for next turn...")
        
        # Turn 5: Final clash
        turn += 1
        print("\n>>> GYARADOS uses Waterfall!")
        damage3, eff3, crit3 = sim.calculate_move_damage(gyarados, machamp, waterfall)
        actual_damage3 = machamp.take_damage(damage3)
        print(f">>> Hit for {actual_damage3} damage! {'Critical hit!' if crit3 else ''}")
        
        if not machamp.fainted:
            print("\n>>> MACHAMP uses Close Combat!")
            damage4, eff4, crit4 = sim.calculate_move_damage(machamp, gyarados, close_combat)
            actual_damage4 = gyarados.take_damage(damage4)
            print(f">>> Hit for {actual_damage4} damage! {'Critical hit!' if crit4 else ''}")
        
        print_battle_status(machamp, gyarados, turn)
        
        print("\n" + "=" * 80)
        if machamp.fainted:
            print(f"💀 {machamp.species} fainted! {gyarados.species} wins!")
        elif gyarados.fainted:
            print(f"💀 {gyarados.species} fainted! {machamp.species} wins!")
        else:
            print("Battle continues... Both Pokemon still standing!")
        print("=" * 80)

if __name__ == "__main__":
    battle_demo()
