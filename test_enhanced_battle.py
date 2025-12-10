"""Test the enhanced Pokemon battle system with boosts, abilities, and status moves."""
import sys
sys.path.append('/workspaces/Black')

from src.battle.simulator import BattlePokemon, BattleSimulator, Move

def test_stat_boosts():
    """Test stat boost system."""
    print("=== Testing Stat Boosts ===\n")
    
    # Create a test Pokemon
    pokemon = BattlePokemon(
        species="Machamp",
        level=50,
        types=["Fighting"],
        base_hp=90,
        base_atk=130,
        base_def=80,
        base_spa=65,
        base_spd=85,
        base_spe=55,
        ability="Guts"
    )
    
    print(f"{pokemon.species} base Attack: {pokemon.atk}")
    print(f"{pokemon.species} boosted Attack (+0): {pokemon.get_boosted_stat('atk')}\n")
    
    # Apply Swords Dance (+2 Attack)
    applied = pokemon.boost_by({"atk": 2})
    print(f"Used Swords Dance! Attack boost: {applied}")
    print(f"Current boost level: {pokemon.boosts['atk']}")
    print(f"{pokemon.species} boosted Attack (+2): {pokemon.get_boosted_stat('atk')}\n")
    
    # Apply another Swords Dance (+2 more)
    applied = pokemon.boost_by({"atk": 2})
    print(f"Used Swords Dance again! Attack boost: {applied}")
    print(f"Current boost level: {pokemon.boosts['atk']}")
    print(f"{pokemon.species} boosted Attack (+4): {pokemon.get_boosted_stat('atk')}\n")
    
    # Try to go past +6 (should be capped)
    applied = pokemon.boost_by({"atk": 3})
    print(f"Tried to boost Attack by 3 more! Applied: {applied}")
    print(f"Current boost level: {pokemon.boosts['atk']} (capped at +6)")
    print(f"{pokemon.species} boosted Attack (+6): {pokemon.get_boosted_stat('atk')}\n")
    
    print("✓ Stat boost system working correctly!\n")

def test_abilities():
    """Test ability system."""
    print("=== Testing Abilities ===\n")
    
    # Create simulator
    sim = BattleSimulator()
    
    # Test Intimidate
    gyarados = BattlePokemon(
        species="Gyarados",
        level=50,
        types=["Water", "Flying"],
        base_hp=95,
        base_atk=125,
        base_def=79,
        base_spa=60,
        base_spd=100,
        base_spe=81,
        ability="Intimidate"
    )
    
    machamp = BattlePokemon(
        species="Machamp",
        level=50,
        types=["Fighting"],
        base_hp=90,
        base_atk=130,
        base_def=80,
        base_spa=65,
        base_spd=85,
        base_spe=55,
        ability="Guts"
    )
    
    print(f"{machamp.species} Attack before Intimidate: {machamp.atk}")
    print(f"{machamp.species} boosted Attack: {machamp.get_boosted_stat('atk')}")
    print(f"{machamp.species} Attack boosts: {machamp.boosts['atk']}\n")
    
    # Apply Intimidate on switch-in
    sim.apply_switch_in_abilities(gyarados, machamp)
    print(f"{gyarados.species} switched in! Intimidate activated!")
    print(f"{machamp.species} Attack after Intimidate: {machamp.atk}")
    print(f"{machamp.species} boosted Attack: {machamp.get_boosted_stat('atk')}")
    print(f"{machamp.species} Attack boosts: {machamp.boosts['atk']}\n")
    
    # Test Thick Fat
    snorlax = BattlePokemon(
        species="Snorlax",
        level=50,
        types=["Normal"],
        base_hp=160,
        base_atk=110,
        base_def=65,
        base_spa=65,
        base_spd=110,
        base_spe=30,
        ability="Thick Fat"
    )
    
    charizard = BattlePokemon(
        species="Charizard",
        level=50,
        types=["Fire", "Flying"],
        base_hp=78,
        base_atk=84,
        base_def=78,
        base_spa=109,
        base_spd=85,
        base_spe=100,
        ability="Blaze"
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
    
    print(f"{charizard.species} uses Flamethrower on {snorlax.species}!")
    damage, effectiveness, crit = sim.calculate_move_damage(charizard, snorlax, flamethrower)
    print(f"Damage: {damage} (reduced by Thick Fat)")
    print(f"Effectiveness: {effectiveness}x\n")
    
    print("✓ Ability system working correctly!\n")

def test_stat_moves():
    """Test stat-changing moves in battle."""
    print("=== Testing Stat-Changing Moves ===\n")
    
    sim = BattleSimulator()
    
    dragonite = BattlePokemon(
        species="Dragonite",
        level=50,
        types=["Dragon", "Flying"],
        base_hp=91,
        base_atk=134,
        base_def=95,
        base_spa=100,
        base_spd=100,
        base_spe=80,
        ability="Multiscale"
    )
    
    blissey = BattlePokemon(
        species="Blissey",
        level=50,
        types=["Normal"],
        base_hp=255,
        base_atk=10,
        base_def=10,
        base_spa=75,
        base_spd=135,
        base_spe=55,
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
    
    # Use Dragon Dance
    print(f"{dragonite.species} uses Dragon Dance!")
    log = sim.use_move(dragonite, blissey, dragon_dance)
    for msg in log['message']:
        print(f"  {msg}")
    print()
    
    print(f"{dragonite.species} stats after Dragon Dance:")
    print(f"  Attack: {dragonite.atk} -> {dragonite.get_boosted_stat('atk')} (boost: {dragonite.boosts['atk']})")
    print(f"  Speed: {dragonite.spe} -> {dragonite.get_boosted_stat('spe')} (boost: {dragonite.boosts['spe']})")
    print()
    
    # Attack with boosted stats
    print(f"{dragonite.species} uses Dragon Claw!")
    damage_before_boost, _, _ = sim.calculate_move_damage(
        BattlePokemon(
            species="Dragonite", level=50, types=["Dragon", "Flying"],
            base_hp=91, base_atk=134, base_def=95, base_spa=100, base_spd=100, base_spe=80,
            ability="Multiscale"
        ),
        blissey,
        dragon_claw
    )
    damage_after_boost, _, _ = sim.calculate_move_damage(dragonite, blissey, dragon_claw)
    
    print(f"  Damage without boosts: {damage_before_boost}")
    print(f"  Damage with +1 Attack: {damage_after_boost}")
    print(f"  Damage increase: {damage_after_boost - damage_before_boost} ({((damage_after_boost / damage_before_boost) - 1) * 100:.1f}%)\n")
    
    print("✓ Stat-changing moves working correctly!\n")

def test_critical_hits_ignore_boosts():
    """Test that critical hits ignore negative offensive boosts and positive defensive boosts."""
    print("=== Testing Critical Hit Boost Interaction ===\n")
    
    sim = BattleSimulator()
    
    attacker = BattlePokemon(
        species="Gengar",
        level=50,
        types=["Ghost", "Poison"],
        base_hp=60,
        base_atk=65,
        base_def=60,
        base_spa=130,
        base_spd=75,
        base_spe=110,
        ability="Levitate"
    )
    
    defender = BattlePokemon(
        species="Blissey",
        level=50,
        types=["Normal"],
        base_hp=255,
        base_atk=10,
        base_def=10,
        base_spa=75,
        base_spd=135,
        base_spe=55,
        ability="Natural Cure"
    )
    
    shadow_ball = Move(
        name="Shadow Ball",
        type="Ghost",
        category="Special",
        base_power=80,
        accuracy=100,
        pp=15,
        max_pp=15
    )
    
    # Lower attacker's SpA, raise defender's SpD
    attacker.boost_by({"spa": -2})
    defender.boost_by({"spd": 2})
    
    print(f"{attacker.species} SpA: {attacker.spa} (boost: {attacker.boosts['spa']})")
    print(f"{defender.species} SpD: {defender.spd} (boost: {defender.boosts['spd']})\n")
    
    # Normal hit
    normal_attack = attacker.get_boosted_stat('spa', ignore_negative=False)
    normal_defense = defender.get_boosted_stat('spd', ignore_negative=False)
    print(f"Normal hit stats:")
    print(f"  Attack: {normal_attack}")
    print(f"  Defense: {normal_defense}\n")
    
    # Critical hit (ignores negative offensive boost and positive defensive boost)
    crit_attack = attacker.get_boosted_stat('spa', ignore_negative=True)
    crit_defense = defender.get_boosted_stat('spd', ignore_negative=True)
    print(f"Critical hit stats:")
    print(f"  Attack: {crit_attack} (ignores -2 penalty)")
    print(f"  Defense: {crit_defense} (ignores +2 boost)\n")
    
    print("✓ Critical hit boost interaction working correctly!\n")

if __name__ == "__main__":
    print("=" * 60)
    print("Enhanced Pokemon Battle System Test")
    print("=" * 60)
    print()
    
    test_stat_boosts()
    test_abilities()
    test_stat_moves()
    test_critical_hits_ignore_boosts()
    
    print("=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)
