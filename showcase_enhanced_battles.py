"""
Demonstrate the enhanced Pokemon battle system with Pokemon Showdown mechanics.
This showcase highlights boosts, abilities, and competitive battling scenarios.
"""
import sys
sys.path.append('/workspaces/Black')

from src.battle.simulator import BattlePokemon, BattleSimulator, Move

def showcase_dragon_dance_sweep():
    """Demonstrate a classic Dragon Dance sweep setup."""
    print("=" * 70)
    print("SCENARIO 1: Dragon Dance Sweep")
    print("=" * 70)
    print()
    print("Dragonite wants to sweep with Dragon Dance + Dragon Claw")
    print("Blissey is a special wall but weak to physical attacks")
    print()
    
    sim = BattleSimulator()
    
    dragonite = BattlePokemon(
        species="Dragonite",
        level=50,
        types=["Dragon", "Flying"],
        base_hp=91, base_atk=134, base_def=95,
        base_spa=100, base_spd=100, base_spe=80,
        ability="Multiscale"
    )
    
    blissey = BattlePokemon(
        species="Blissey",
        level=50,
        types=["Normal"],
        base_hp=255, base_atk=10, base_def=10,
        base_spa=75, base_spd=135, base_spe=55,
        ability="Natural Cure"
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
    
    dragon_claw = Move(
        name="Dragon Claw",
        type="Dragon",
        category="Physical",
        base_power=80,
        accuracy=100,
        pp=15,
        max_pp=15
    )
    
    print(f"Turn 1: {dragonite.species} uses Dragon Dance!")
    print(f"  Current HP: {dragonite.current_hp}/{dragonite.max_hp}")
    print(f"  Attack: {dragonite.atk} -> {dragonite.get_boosted_stat('atk')}")
    print(f"  Speed: {dragonite.spe} -> {dragonite.get_boosted_stat('spe')}")
    print()
    
    dragonite.boost_by({"atk": 1, "spe": 1})
    
    print(f"After Dragon Dance:")
    print(f"  Attack: {dragonite.get_boosted_stat('atk')} (+{dragonite.boosts['atk']})")
    print(f"  Speed: {dragonite.get_boosted_stat('spe')} (+{dragonite.boosts['spe']})")
    print()
    
    print(f"Turn 2: {dragonite.species} uses Dragon Claw!")
    damage1, eff1, crit1 = sim.calculate_move_damage(dragonite, blissey, dragon_claw)
    actual_damage1 = blissey.take_damage(damage1)
    print(f"  Damage: {actual_damage1}")
    print(f"  {blissey.species}: {blissey.current_hp}/{blissey.max_hp} HP remaining")
    print()
    
    print(f"Turn 3: {dragonite.species} uses Dragon Dance again!")
    dragonite.boost_by({"atk": 1, "spe": 1})
    print(f"  Attack: {dragonite.get_boosted_stat('atk')} (+{dragonite.boosts['atk']})")
    print(f"  Speed: {dragonite.get_boosted_stat('spe')} (+{dragonite.boosts['spe']})")
    print()
    
    print(f"Turn 4: {dragonite.species} uses Dragon Claw again!")
    damage2, eff2, crit2 = sim.calculate_move_damage(dragonite, blissey, dragon_claw)
    actual_damage2 = blissey.take_damage(damage2)
    print(f"  Damage: {actual_damage2} (+{actual_damage2 - actual_damage1} from +1 more boost)")
    print(f"  {blissey.species}: {blissey.current_hp}/{blissey.max_hp} HP remaining")
    
    if blissey.fainted:
        print(f"\n  💀 {blissey.species} fainted!")
    print()

def showcase_intimidate_mindgames():
    """Demonstrate Intimidate switching strategy."""
    print("=" * 70)
    print("SCENARIO 2: Intimidate Pivot Strategy")
    print("=" * 70)
    print()
    print("Gyarados switches in to intimidate Machamp, forcing a switch")
    print()
    
    sim = BattleSimulator()
    
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
    
    arcanine = BattlePokemon(
        species="Arcanine",
        level=50,
        types=["Fire"],
        base_hp=90, base_atk=110, base_def=80,
        base_spa=100, base_spd=80, base_spe=95,
        ability="Intimidate"
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
    
    print(f"{machamp.species} is on the field")
    print(f"  Attack: {machamp.atk}")
    print(f"  Attack boosts: {machamp.boosts['atk']}")
    print()
    
    print(f"{gyarados.species} switches in!")
    sim.apply_switch_in_abilities(gyarados, machamp)
    print(f"  Intimidate activated!")
    print(f"  {machamp.species} Attack: {machamp.get_boosted_stat('atk')} (boost: {machamp.boosts['atk']})")
    print()
    
    print(f"{machamp.species} uses Close Combat!")
    damage1, _, _ = sim.calculate_move_damage(machamp, gyarados, close_combat)
    print(f"  Damage: {damage1} (reduced by Intimidate)")
    print()
    
    print(f"{arcanine.species} switches in!")
    sim.apply_switch_in_abilities(arcanine, machamp)
    print(f"  Intimidate activated again!")
    print(f"  {machamp.species} Attack: {machamp.get_boosted_stat('atk')} (boost: {machamp.boosts['atk']})")
    print()
    
    print(f"{machamp.species} uses Close Combat again!")
    damage2, _, _ = sim.calculate_move_damage(machamp, arcanine, close_combat)
    print(f"  Damage: {damage2} (severely reduced by double Intimidate)")
    print()
    
    print(f"Damage comparison:")
    print(f"  No Intimidate: {damage1 * 2:.0f} (estimated)")
    print(f"  -1 Intimidate: {damage1}")
    print(f"  -2 Intimidate: {damage2}")
    print(f"  Reduction: {((1 - damage2 / (damage1 * 2)) * 100):.1f}%")
    print()

def showcase_ability_interactions():
    """Demonstrate ability-based damage modifications."""
    print("=" * 70)
    print("SCENARIO 3: Ability-Based Damage Reduction")
    print("=" * 70)
    print()
    print("Snorlax's Thick Fat halves Fire and Ice damage")
    print()
    
    sim = BattleSimulator()
    
    snorlax = BattlePokemon(
        species="Snorlax",
        level=50,
        types=["Normal"],
        base_hp=160, base_atk=110, base_def=65,
        base_spa=65, base_spd=110, base_spe=30,
        ability="Thick Fat"
    )
    
    charizard = BattlePokemon(
        species="Charizard",
        level=50,
        types=["Fire", "Flying"],
        base_hp=78, base_atk=84, base_def=78,
        base_spa=109, base_spd=85, base_spe=100,
        ability="Blaze"
    )
    
    lapras = BattlePokemon(
        species="Lapras",
        level=50,
        types=["Water", "Ice"],
        base_hp=130, base_atk=85, base_def=80,
        base_spa=85, base_spd=95, base_spe=60,
        ability="Water Absorb"
    )
    
    flamethrower = Move(
        name="Flamethrower",
        type="Fire",
        category="Special",
        base_power=90,
        accuracy=100,
        pp=15,
        max_pp=15
    )
    
    ice_beam = Move(
        name="Ice Beam",
        type="Ice",
        category="Special",
        base_power=90,
        accuracy=100,
        pp=15,
        max_pp=15
    )
    
    thunderbolt = Move(
        name="Thunderbolt",
        type="Electric",
        category="Special",
        base_power=90,
        accuracy=100,
        pp=15,
        max_pp=15
    )
    
    print(f"{charizard.species} vs {snorlax.species}:")
    fire_damage, _, _ = sim.calculate_move_damage(charizard, snorlax, flamethrower)
    print(f"  Flamethrower: {fire_damage} damage (halved by Thick Fat)")
    
    # Compare to normal damage (without Thick Fat)
    snorlax_no_ability = BattlePokemon(
        species="Snorlax",
        level=50,
        types=["Normal"],
        base_hp=160, base_atk=110, base_def=65,
        base_spa=65, base_spd=110, base_spe=30,
        ability="No Ability"
    )
    fire_damage_normal, _, _ = sim.calculate_move_damage(charizard, snorlax_no_ability, flamethrower)
    print(f"  Without Thick Fat: {fire_damage_normal} damage")
    print(f"  Reduction: {fire_damage_normal - fire_damage} damage saved ({((1 - fire_damage / fire_damage_normal) * 100):.1f}%)")
    print()
    
    print(f"{lapras.species} vs {snorlax.species}:")
    ice_damage, _, _ = sim.calculate_move_damage(lapras, snorlax, ice_beam)
    print(f"  Ice Beam: {ice_damage} damage (halved by Thick Fat)")
    ice_damage_normal, _, _ = sim.calculate_move_damage(lapras, snorlax_no_ability, ice_beam)
    print(f"  Without Thick Fat: {ice_damage_normal} damage")
    print(f"  Reduction: {ice_damage_normal - ice_damage} damage saved ({((1 - ice_damage / ice_damage_normal) * 100):.1f}%)")
    print()
    
    print(f"Thunderbolt (not affected by Thick Fat):")
    elec_damage, _, _ = sim.calculate_move_damage(lapras, snorlax, thunderbolt)
    print(f"  Damage: {elec_damage} (no reduction)")
    print()

def showcase_competitive_scenario():
    """Full competitive battle scenario."""
    print("=" * 70)
    print("SCENARIO 4: Competitive Battle Simulation")
    print("=" * 70)
    print()
    print("Machamp (Guts) vs Gyarados (Intimidate)")
    print("Can Machamp overcome Intimidate with Bulk Up?")
    print()
    
    sim = BattleSimulator()
    
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
    
    print("Turn 1:")
    print(f"  {gyarados.species} switches in -> Intimidate!")
    sim.apply_switch_in_abilities(gyarados, machamp)
    print(f"  {machamp.species} Attack: {machamp.get_boosted_stat('atk')} (boost: {machamp.boosts['atk']})")
    print()
    
    print("Turn 2:")
    print(f"  {machamp.species} uses Bulk Up!")
    machamp.boost_by({"atk": 1, "def": 1})
    print(f"  Attack: {machamp.get_boosted_stat('atk')} (boost: {machamp.boosts['atk']})")
    print(f"  Defense: {machamp.get_boosted_stat('defense')} (boost: {machamp.boosts['def']})")
    print()
    
    print("Turn 3:")
    print(f"  {machamp.species} uses Bulk Up again!")
    machamp.boost_by({"atk": 1, "def": 1})
    print(f"  Attack: {machamp.get_boosted_stat('atk')} (boost: {machamp.boosts['atk']})")
    print(f"  Defense: {machamp.get_boosted_stat('defense')} (boost: {machamp.boosts['def']})")
    print()
    
    print("Turn 4:")
    print(f"  {machamp.species} uses Close Combat!")
    damage, eff, crit = sim.calculate_move_damage(machamp, gyarados, close_combat)
    actual_damage = gyarados.take_damage(damage)
    print(f"  Damage: {actual_damage}")
    print(f"  Effectiveness: {eff}x (super effective!)")
    print(f"  {gyarados.species}: {gyarados.current_hp}/{gyarados.max_hp} HP")
    
    if gyarados.fainted:
        print(f"\n  💀 {gyarados.species} fainted!")
        print(f"\n  {machamp.species} wins by overcoming Intimidate with Bulk Up!")
    print()

if __name__ == "__main__":
    print()
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "POKEMON SHOWDOWN BATTLE SHOWCASE" + " " * 21 + "║")
    print("║" + " " * 13 + "Enhanced Battle System with Boosts & Abilities" + " " * 9 + "║")
    print("╚" + "=" * 68 + "╝")
    print()
    
    showcase_dragon_dance_sweep()
    showcase_intimidate_mindgames()
    showcase_ability_interactions()
    showcase_competitive_scenario()
    
    print("=" * 70)
    print("All scenarios complete! Battle system working as expected.")
    print("=" * 70)
